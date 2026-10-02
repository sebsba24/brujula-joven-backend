from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List
import anthropic

from database import get_db
from security import get_current_user
from config import get_settings
import crud
from profiles import (
    calcular_perfil, calcular_capacidad_financiera,
    PROGRAMAS_EDUCATIVOS, BECAS_POR_CAPACIDAD,
)

router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class ChatResponse(BaseModel):
    reply: str


def _build_system_prompt(
    nombre: str,
    riasec_text: str,
    financiero_text: str,
    programas: list,
    becas: list,
) -> str:
    programas_str = "\n".join(
        f"- {p['nombre']} ({p['inst']}, {p['tipo']}, costo: {p['costo']})"
        for p in programas[:8]
    )
    becas_str = "\n".join(f"- {b}" for b in becas)

    return (
        "Eres Brújula, el asistente de orientación educativa de NextSteps (Brújula Joven), "
        "una plataforma colombiana para jóvenes. Eres amigable, cercano y empático. "
        "Hablas en español colombiano natural. Tus respuestas son concisas (máximo 200 palabras), "
        "prácticas y personalizadas al perfil del usuario.\n\n"
        f"PERFIL DEL USUARIO:\n"
        f"- Nombre: {nombre}\n"
        f"- {riasec_text}\n"
        f"- {financiero_text}\n\n"
        f"PROGRAMAS EDUCATIVOS RELEVANTES:\n{programas_str}\n\n"
        f"BECAS Y FINANCIAMIENTO DISPONIBLES:\n{becas_str}\n\n"
        "INSTRUCCIONES:\n"
        "- Personaliza siempre según el perfil RIASEC y financiero del usuario.\n"
        "- Si el usuario no tiene perfil aún, sugiérele completar el test y el formulario financiero.\n"
        "- Responde solo sobre educación superior colombiana, programas técnicos/tecnológicos, "
        "becas y orientación vocacional.\n"
        "- No inventes instituciones ni programas que no estén en el contexto.\n"
        "- Si te preguntan algo fuera de tu alcance, redirige amablemente."
    )


@router.post("/message", response_model=ChatResponse)
async def send_message(
    payload: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="Servicio de chat no configurado. Agrega ANTHROPIC_API_KEY al .env")

    # ── RIASEC ────────────────────────────────────────────────────────────────
    riasec_text = "Aún no ha completado el cuestionario vocacional."
    top3 = []
    ultima_resp = await crud.get_last_respuesta_by_usuario(db, current_user.id_usuario)
    if ultima_resp:
        perfil = calcular_perfil(ultima_resp.respuestas)
        top3 = perfil["top3"]
        scores = perfil["perfil"]
        scores_str = ", ".join(f"{k}={v}%" for k, v in scores.items())
        riasec_text = (
            f"Perfil RIASEC — Dominante: {perfil['dominante']}, "
            f"Top 3: {', '.join(top3)}. Puntajes: {scores_str}"
        )

    # ── Financiero ────────────────────────────────────────────────────────────
    financiero_text = "Aún no ha completado el perfil financiero."
    capacidad = "media"
    fin_data = await crud.perfil_financiero_crud.get_filtered(db, {"id_usuario": current_user.id_usuario})
    if fin_data:
        uf = sorted(fin_data, key=lambda x: x.id_perfil, reverse=True)[0]
        capacidad = uf.capacidad_economica or "media"
        calc = calcular_capacidad_financiera({
            "estrato":               uf.estrato,
            "ingresos_hogar":        uf.ingresos_hogar,
            "puede_pagar_matricula": uf.puede_pagar_matricula,
            "acceso_internet":       uf.acceso_internet,
            "tiene_computador":      uf.tiene_computador,
            "disponibilidad_tiempo": uf.disponibilidad_tiempo,
        })
        financiero_text = (
            f"Estrato {uf.estrato}, capacidad económica: {capacidad}, "
            f"elegible subsidios: {'sí' if uf.elegible_subsidios else 'no'}, "
            f"modalidad recomendada: {calc['modalidad_recomendada']}"
        )

    # ── Programas relevantes ──────────────────────────────────────────────────
    programas_relevantes = []
    if top3:
        for rasgo in top3:
            programas_relevantes.extend(PROGRAMAS_EDUCATIVOS.get(rasgo, []))
    else:
        for progs in PROGRAMAS_EDUCATIVOS.values():
            programas_relevantes.extend(progs[:1])

    becas = BECAS_POR_CAPACIDAD.get(capacidad, [])

    system_prompt = _build_system_prompt(
        current_user.nombre, riasec_text, financiero_text, programas_relevantes, becas
    )

    # ── Historial (máx 10 turnos) ─────────────────────────────────────────────
    history_slice = payload.history[-10:]
    messages = [{"role": m.role, "content": m.content} for m in history_slice]
    messages.append({"role": "user", "content": payload.message})

    # ── Llamada a Anthropic ───────────────────────────────────────────────────
    try:
        client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            system=system_prompt,
            messages=messages,
        )
        reply_text = response.content[0].text
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Error del servicio de IA: {str(e)}")

    return {"reply": reply_text}
