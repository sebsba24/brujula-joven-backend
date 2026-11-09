from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy import select
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from security import get_current_user

from database import get_db
import crud
import schemas
import models
from routes import auth, chat
from profiles import (
    VALID_RASGOS, MAPA_CARRERAS, MAPA_COMBINADO, HOLLAND_ADYACENTES,
    BECAS_POR_CAPACIDAD,
    calcular_perfil, calcular_chaside, generar_recomendaciones,
    calcular_capacidad_financiera, puntuar_programas,
)
from config import get_settings


async def _cargar_programas_db(db: AsyncSession) -> dict:
    """Carga programas educativos desde BD y los devuelve en el mismo
    formato que PROGRAMAS_EDUCATIVOS (dict rasgo → list[dict])."""
    result = await db.execute(
        select(models.Carrera, models.Universidad)
        .join(models.Universidad, models.Carrera.id_universidad == models.Universidad.id_universidad)
        .where(models.Carrera.estado == True)
        .where(models.Carrera.rasgo.isnot(None))
    )
    rows = result.all()
    programas: dict = {r: [] for r in VALID_RASGOS}
    for carrera, uni in rows:
        rasgo = carrera.rasgo
        if rasgo not in programas:
            continue
        programas[rasgo].append({
            "nombre":      carrera.nombre,
            "inst":        uni.nombre,
            "tipo":        carrera.tipo or "",
            "costo":       carrera.costo or "gratuito",
            "ciudad":      carrera.ciudad or "Nacional",
            "modalidad":   carrera.modalidad or [],
            "con_beca":    carrera.con_beca or False,
            "duracion":    carrera.duracion or "",
            "requisitos":  carrera.requisitos or "",
            "descripcion": carrera.descripcion or "",
            "url":         carrera.url or "",
        })
    return programas

_settings = get_settings()
ALLOWED_ORIGINS = [o.strip() for o in _settings.allowed_origins.split(",") if o.strip()]

app = FastAPI(
    title="Brujula Joven API",
    version="2.0.0"
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== CORS EN ERRORES 500 ====================
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    headers = {}
    if origin in ALLOWED_ORIGINS:
        headers["Access-Control-Allow-Origin"]      = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
        headers=headers,
    )

# ==================== AUTH + CHAT ====================
app.include_router(auth.router)
app.include_router(chat.router, prefix="/chat", tags=["Chat"])

# ==================== HEALTH ====================
@app.get("/health")
async def health():
    return {"status": "ok"}


# ==================== GENERADOR DE ENDPOINTS ====================

def register_crud_routes(
    name: str,
    crud_instance,
    response_schema,
    create_schema,
    update_schema
):
    base_path = f"/{name}"

    # GET ALL
    @app.get(base_path, response_model=List[response_schema], tags=[name.capitalize()])
    async def get_all(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
        return await crud_instance.get_all(db, skip, limit)

    # GET BY ID
    @app.get(f"{base_path}/{{id}}", response_model=response_schema, tags=[name.capitalize()])
    async def get_by_id(id: int, db: AsyncSession = Depends(get_db)):
        obj = await crud_instance.get(db, id)
        if not obj:
            raise HTTPException(404, f"{name} not found")
        return obj

    # FILTER
    @app.post(f"{base_path}/filter", tags=[name.capitalize()])
    async def filter_data(payload: dict, db: AsyncSession = Depends(get_db)):
        filters = payload.get("filters", {})
        fields = payload.get("fields", None)
        return await crud_instance.get_filtered(db, filters, fields)

    # CREATE
    @app.post(base_path, response_model=response_schema, status_code=201, tags=[name.capitalize()])
    async def create(item: create_schema, db: AsyncSession = Depends(get_db)):
        return await crud_instance.create(db, item.model_dump())

    # UPDATE
    @app.put(f"{base_path}/{{id}}", response_model=response_schema, tags=[name.capitalize()])
    async def update(id: int, item: update_schema, db: AsyncSession = Depends(get_db)):
        result = await crud_instance.update(db, id, item.model_dump(exclude_unset=True))
        if not result:
            raise HTTPException(404, f"{name} not found")
        return result

    # SOFT DELETE
    @app.put(f"{base_path}/{{id}}/delete", status_code=204, tags=[name.capitalize()])
    async def soft_delete(id: int, db: AsyncSession = Depends(get_db)):
        deleted = await crud_instance.soft_delete(db, id)
        if not deleted:
            raise HTTPException(404, f"{name} not found")
        return None
    

# ==================== ENDPOINTS ESPECIALES ====================

# Carreras por universidad
@app.get("/universidades/{id_universidad}/carreras", tags=["Carreras"])
async def get_carreras_by_universidad(id_universidad: int, db: AsyncSession = Depends(get_db)):
    return await crud.carrera_crud.get_filtered(db, {"id_universidad": id_universidad})


# Roles por usuario
@app.get("/usuarios/{id_usuario}/roles", tags=["Usuario Roles"])
async def get_roles_by_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):
    return await crud.usuario_rol_crud.get_filtered(db, {"id_usuario": id_usuario})


# Carreras por usuario
@app.get("/usuarios/{id_usuario}/carreras", tags=["Usuario Carreras"])
async def get_carreras_by_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):
    return await crud.usuario_carrera_crud.get_filtered(db, {"id_usuario": id_usuario})


# Subsidios por usuario
@app.get("/usuarios/{id_usuario}/subsidios", tags=["Usuario Subsidios"])
async def get_subsidios_by_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):
    return await crud.usuario_subsidio_crud.get_filtered(db, {"id_usuario": id_usuario})

# Perfil RIASEC por usuario
@app.get("/usuarios/{id_usuario}/perfil", tags=["Usuario Perfil"])
async def get_perfil_by_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")

    ultima = await crud.get_last_respuesta_by_usuario(db, id_usuario)
    if not ultima:
        raise HTTPException(status_code=404, detail="No hay respuestas para este usuario")

    resultado = calcular_perfil(ultima.respuestas)
    resultado["chaside"] = calcular_chaside(resultado["perfil"])
    return resultado

# ==================== ENDPOINTS FINANCIERO ====================

@app.post("/financiero/guardar", tags=["Financiero"])
async def guardar_perfil_financiero(
    payload: schemas.PerfilFinancieroCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    calculado = calcular_capacidad_financiera(payload.model_dump())
    data = {
        **payload.model_dump(),
        "id_usuario": current_user.id_usuario,
        "capacidad_economica": calculado["capacidad_economica"],
        "elegible_subsidios":  calculado["elegible_subsidios"],
        "estado": True,
    }
    result = await crud.perfil_financiero_crud.create(db, data)
    return {
        "message":             "Perfil financiero guardado",
        "id_perfil":           result.id_perfil,
        "capacidad_economica": result.capacidad_economica,
        "elegible_subsidios":  result.elegible_subsidios,
        "modalidad_recomendada": calculado["modalidad_recomendada"],
    }


@app.get("/usuarios/{id_usuario}/perfil-financiero", tags=["Financiero"])
async def get_perfil_financiero(id_usuario: int, db: AsyncSession = Depends(get_db)):
    data = await crud.perfil_financiero_crud.get_filtered(db, {"id_usuario": id_usuario})
    if not data:
        raise HTTPException(status_code=404, detail="Sin perfil financiero")
    ultimo = sorted(data, key=lambda x: x.id_perfil, reverse=True)[0]
    calc   = calcular_capacidad_financiera({
        "estrato":               ultimo.estrato,
        "ingresos_hogar":        ultimo.ingresos_hogar,
        "puede_pagar_matricula": ultimo.puede_pagar_matricula,
        "acceso_internet":       ultimo.acceso_internet,
        "tiene_computador":      ultimo.tiene_computador,
        "disponibilidad_tiempo": ultimo.disponibilidad_tiempo,
    })
    return {
        "id_perfil":              ultimo.id_perfil,
        "estrato":                ultimo.estrato,
        "personas_hogar":         ultimo.personas_hogar,
        "personas_trabajan":      ultimo.personas_trabajan,
        "ingresos_hogar":         ultimo.ingresos_hogar,
        "trabaja_actualmente":    ultimo.trabaja_actualmente,
        "ingresos_propios":       ultimo.ingresos_propios,
        "personas_a_cargo":       ultimo.personas_a_cargo,
        "tiene_deudas":           ultimo.tiene_deudas,
        "acceso_internet":        ultimo.acceso_internet,
        "tiene_computador":       ultimo.tiene_computador,
        "disponibilidad_tiempo":  ultimo.disponibilidad_tiempo,
        "puede_pagar_matricula":  ultimo.puede_pagar_matricula,
        "recibe_subsidios":       ultimo.recibe_subsidios,
        "capacidad_economica":    ultimo.capacidad_economica,
        "elegible_subsidios":     ultimo.elegible_subsidios,
        "modalidad_recomendada":  calc["modalidad_recomendada"],
    }


@app.get("/usuarios/{id_usuario}/recomendaciones-educacion", tags=["Financiero"])
async def get_recomendaciones_educacion(id_usuario: int, db: AsyncSession = Depends(get_db)):
    # Perfil vocacional
    ultima_resp    = await crud.get_last_respuesta_by_usuario(db, id_usuario)
    sin_vocacional = ultima_resp is None
    top_rasgos     = ["R", "I", "A"]
    rasgos_scores  = {"R": 33, "I": 33, "A": 34, "S": 0, "E": 0, "C": 0}  # defaults
    if ultima_resp:
        perfil_riasec = calcular_perfil(ultima_resp.respuestas)
        top_rasgos    = perfil_riasec["top3"]
        rasgos_scores = perfil_riasec["perfil"]

    # Perfil financiero
    fin_data       = await crud.perfil_financiero_crud.get_filtered(db, {"id_usuario": id_usuario})
    sin_financiero = not bool(fin_data)
    capacidad, elegible, modalidad = "media", True, "presencial"
    if fin_data:
        uf        = sorted(fin_data, key=lambda x: x.id_perfil, reverse=True)[0]
        capacidad = uf.capacidad_economica or "media"
        elegible  = uf.elegible_subsidios
        calc      = calcular_capacidad_financiera({
            "estrato": uf.estrato, "ingresos_hogar": uf.ingresos_hogar,
            "puede_pagar_matricula": uf.puede_pagar_matricula,
            "acceso_internet": uf.acceso_internet, "tiene_computador": uf.tiene_computador,
            "disponibilidad_tiempo": uf.disponibilidad_tiempo,
        })
        modalidad = calc["modalidad_recomendada"]

    programas_db = await _cargar_programas_db(db)

    return {
        "capacidad_economica":   capacidad,
        "elegible_subsidios":    elegible,
        "modalidad_recomendada": modalidad,
        "top_rasgos":            top_rasgos,
        "rasgos_scores":         rasgos_scores,
        "programas":             puntuar_programas(rasgos_scores, capacidad, modalidad, programas_db),
        "becas":                 BECAS_POR_CAPACIDAD.get(capacidad, []),
        "sin_perfil_financiero": sin_financiero,
        "sin_perfil_vocacional": sin_vocacional,
    }


@app.get("/programas-educativos", tags=["Educación"])
async def get_programas_educativos(
    rasgo: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Devuelve todos los programas educativos desde la BD.
    Filtrable por rasgo RIASEC: ?rasgo=I"""
    query = (
        select(models.Carrera, models.Universidad)
        .join(models.Universidad, models.Carrera.id_universidad == models.Universidad.id_universidad)
        .where(models.Carrera.estado == True)
    )
    if rasgo:
        rasgo = rasgo.upper()
        if rasgo not in VALID_RASGOS:
            raise HTTPException(status_code=400, detail=f"Rasgo inválido. Válidos: {VALID_RASGOS}")
        query = query.where(models.Carrera.rasgo == rasgo)

    result = await db.execute(query.order_by(models.Carrera.rasgo, models.Carrera.id_carrera))
    rows = result.all()
    return [
        {
            "id_carrera":  c.id_carrera,
            "rasgo":       c.rasgo,
            "nombre":      c.nombre,
            "inst":        u.nombre,
            "tipo":        c.tipo,
            "costo":       c.costo,
            "ciudad":      c.ciudad,
            "modalidad":   c.modalidad,
            "con_beca":    c.con_beca,
            "duracion":    c.duracion,
            "requisitos":  c.requisitos,
            "descripcion": c.descripcion,
            "url":         c.url,
        }
        for c, u in rows
    ]


@app.delete("/usuarios/{id_usuario}/perfil-financiero", tags=["Financiero"])
async def eliminar_perfil_financiero(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")
    data = await crud.perfil_financiero_crud.get_filtered(db, {"id_usuario": id_usuario})
    if not data:
        raise HTTPException(status_code=404, detail="Sin perfil financiero")
    for perfil in data:
        await db.delete(perfil)
    await db.commit()
    return {"message": "Perfil financiero eliminado"}


@app.delete("/usuarios/{id_usuario}/respuestas-cuestionario", tags=["Respuestas Cuestionario"])
async def eliminar_respuestas_cuestionario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")
    data = await crud.respuesta_cuestionario_crud.get_filtered(db, {"id_usuario": id_usuario})
    if not data:
        raise HTTPException(status_code=404, detail="Sin respuestas registradas")
    for resp in data:
        resp.estado = False
    await db.commit()
    return {"message": "Respuestas del cuestionario desactivadas"}


@app.get("/usuarios/{id_usuario}/recomendaciones", tags=["Usuario Perfil"])
async def get_recomendaciones_by_usuario(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")

    ultima = await crud.get_last_respuesta_by_usuario(db, id_usuario)
    if not ultima:
        raise HTTPException(status_code=404, detail="No hay respuestas para este usuario")

    perfil = calcular_perfil(ultima.respuestas)
    return {
        "perfil": perfil,
        "recomendaciones": generar_recomendaciones(perfil),
    }

# Preguntas múltiples por grupo
@app.get("/preguntas/multiples/{grupo}", tags=["Preguntas"])
async def get_preguntas_multiples_por_grupo(grupo: str, db: AsyncSession = Depends(get_db)):
    try:
        preguntas = await crud.pregunta_crud.get_all(db)
        relaciones = await crud.get_preguntas_multiples(db)

        preguntas_dict = {p.id_pregunta: p for p in preguntas}
        resultado = {}

        for rel in relaciones:

            if rel.grupo != grupo:
                continue

            enunciado = preguntas_dict.get(rel.id_enunciado)
            opcion = preguntas_dict.get(rel.id_pregunta)

            if not enunciado or not opcion:
                continue

            if rel.id_enunciado not in resultado:
                resultado[rel.id_enunciado] = {
                    "id": enunciado.id_pregunta,
                    "enunciado": enunciado.descripcion,
                    "opciones": []
                }

            # Evitar opciones duplicadas por rasgo o por texto
            rasgos_existentes = {o["rasgo"] for o in resultado[rel.id_enunciado]["opciones"]}
            textos_existentes = {o["texto"] for o in resultado[rel.id_enunciado]["opciones"]}
            if opcion.rasgo in rasgos_existentes or opcion.descripcion in textos_existentes:
                continue

            resultado[rel.id_enunciado]["opciones"].append({
                "id": opcion.id_pregunta,
                "texto": opcion.descripcion,
                "rasgo": opcion.rasgo
            })

        return list(resultado.values())

    except Exception as e:
        print("ERROR CRITICO:", str(e))
        raise HTTPException(status_code=500, detail="Error al cargar preguntas múltiples")

@app.get("/preguntas/nivel/{nivel}", response_model=List[schemas.PreguntaResponse],tags=["Preguntas"])
async def get_preguntas_by_nivel(nivel: int, db: AsyncSession = Depends(get_db)):
    return await crud.pregunta_crud.get_filtered(db, {"nivel": nivel})


@app.get("/preguntas/rasgo/{rasgo}", response_model=List[schemas.PreguntaResponse], tags=["Preguntas"])
async def get_preguntas_by_rasgo(rasgo: str, db: AsyncSession = Depends(get_db)):
    if rasgo not in VALID_RASGOS:
        raise HTTPException(status_code=400, detail="Rasgo no válido")
    return await crud.pregunta_crud.get_filtered(db, {"rasgo": rasgo})

# Guardar respuestas de cuestionario
@app.post("/respuestas-cuestionario/guardar", tags=["Respuestas Cuestionario"])
async def guardar_respuestas_cuestionario(
    payload: schemas.RespuestaCuestionarioCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        data = {
            "id_usuario": current_user.id_usuario,
            "respuestas": {"respuestas": payload.respuestas},
            "estado": True,
        }
        result = await crud.respuesta_cuestionario_crud.create(db, data)
        return {
            "message": "Respuestas guardadas correctamente",
            "id_respuesta": result.id_respuesta,
        }
    except Exception as e:
        print("ERROR GUARDANDO RESPUESTAS:", str(e))
        raise HTTPException(status_code=500, detail="Error al guardar las respuestas")

# ==================== ENDPOINTS EMPLEO ====================

@app.get("/usuarios/{id_usuario}/progreso-empleo", tags=["Empleo"])
async def get_progreso_empleo(
    id_usuario: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")
    result = await db.execute(
        select(models.ProgresoEmpleo).where(models.ProgresoEmpleo.id_usuario == id_usuario)
    )
    progreso = result.scalar_one_or_none()
    recursos = progreso.recursos_completados if progreso else []
    return {"id_usuario": id_usuario, "recursos_completados": recursos or []}


@app.post("/usuarios/{id_usuario}/progreso-empleo", tags=["Empleo"])
async def guardar_progreso_empleo(
    id_usuario: int,
    payload: schemas.ProgresoEmpleoUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.id_usuario != id_usuario:
        raise HTTPException(status_code=403, detail="No autorizado")
    result = await db.execute(
        select(models.ProgresoEmpleo).where(models.ProgresoEmpleo.id_usuario == id_usuario)
    )
    progreso = result.scalar_one_or_none()
    if progreso:
        progreso.recursos_completados = payload.recursos_completados
    else:
        progreso = models.ProgresoEmpleo(
            id_usuario=id_usuario,
            recursos_completados=payload.recursos_completados,
        )
        db.add(progreso)
    await db.commit()
    return {"message": "Progreso guardado", "recursos_completados": payload.recursos_completados}


# ==================== REGISTRO DE ENTIDADES ====================

register_crud_routes(
    "universidades",
    crud.universidad_crud,
    schemas.UniversidadResponse,
    schemas.UniversidadCreate,
    schemas.UniversidadUpdate
)

register_crud_routes(
    "carreras",
    crud.carrera_crud,
    schemas.CarreraResponse,
    schemas.CarreraCreate,
    schemas.CarreraUpdate
)

register_crud_routes(
    "roles",
    crud.rol_crud,
    schemas.RolResponse,
    schemas.RolCreate,
    schemas.RolUpdate
)

register_crud_routes(
    "subsidios",
    crud.subsidio_crud,
    schemas.SubsidioResponse,
    schemas.SubsidioCreate,
    schemas.SubsidioUpdate
)

register_crud_routes(
    "usuarios",
    crud.usuario_crud,
    schemas.UsuarioResponse,
    schemas.UsuarioCreate,
    schemas.UsuarioUpdate
)

register_crud_routes(
    "preguntas",
    crud.pregunta_crud,
    schemas.PreguntaResponse,
    schemas.PreguntaCreate,
    schemas.PreguntaUpdate
)

register_crud_routes(
    "respuestas_cuestionario",
    crud.respuesta_cuestionario_crud,
    schemas.RespuestaCuestionarioResponse,
    schemas.RespuestaCuestionarioCreate,
    schemas.RespuestaCuestionarioUpdate
)