from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from collections import defaultdict
from typing import List
from security import get_current_user

from database import get_db
import crud
import schemas
from routes import auth

ALLOWED_ORIGINS = ["http://localhost:5173"]

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
        content={"detail": f"Error interno: {str(exc)}"},
        headers=headers,
    )

VALID_RASGOS = {"R", "I", "A", "S", "E", "C", "N"}
# ==================== AUTH ====================
app.include_router(auth.router)

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
    

# ===================== LÓGICA DE PERFILES =====================    

MAPA_CARRERAS = {
    "R": [
        "Ingeniería Mecánica",
        "Ingeniería Civil",
        "Técnico en Electrónica",
        "Mecánica Automotriz",
        "Construcción"
    ],
    "I": [
        "Ingeniería de Sistemas",
        "Ciencia de Datos",
        "Investigación Científica",
        "Matemáticas",
        "Física"
    ],
    "A": [
        "Diseño Gráfico",
        "Arquitectura",
        "Publicidad",
        "Artes Visuales",
        "Producción Multimedia"
    ],
    "S": [
        "Psicología",
        "Trabajo Social",
        "Docencia",
        "Enfermería",
        "Coaching"
    ],
    "E": [
        "Administración de Empresas",
        "Marketing",
        "Negocios Internacionales",
        "Emprendimiento",
        "Ventas"
    ],
    "C": [
        "Contaduría",
        "Administración",
        "Logística",
        "Gestión Documental",
        "Finanzas"
    ]
}

MAPA_COMBINADO = {
    ("R", "I"): [
        "Ingeniería Mecánica",
        "Ingeniería Electrónica",
        "Ingeniería de Sistemas",
        "Robótica",
        "Mecatrónica"
    ],
    ("R", "E"): [
        "Ingeniería Industrial",
        "Administración de Proyectos",
        "Construcción",
        "Logística",
        "Gestión de Operaciones"
    ],
    ("I", "E"): [
        "Ciencia de Datos",
        "Ingeniería de Sistemas",
        "Business Intelligence",
        "Finanzas",
        "Consultoría"
    ]
}

def calcular_perfil(respuestas_json: dict):
    niveles = respuestas_json.get("respuestas", {})

    pesos_nivel = {
        "nivel1": 3,
        "nivel2": 2,
        "nivel3": 1
    }

    niveles_scores = {}

    # ====================
    # 1. CALCULAR POR NIVEL
    # ====================
    for nivel, respuestas in niveles.items():

        if nivel == "nivel2":
            valores = list(respuestas.values())
            if len(valores) > 0 and len(set(valores)) == 1:
                continue  # ignora nivel2 completamente

        temp_scores = defaultdict(float)

        for key, value in respuestas.items():

            # VALIDACIONES
            if not isinstance(key, str) or len(key) == 0:
                continue

            if not isinstance(value, (int, float)):
                continue

            if value < 1 or value > 5:
                continue

            rasgo = key[0]

            if rasgo in VALID_RASGOS:
                temp_scores[rasgo] += value

        total_nivel = sum(temp_scores.values()) or 1

        # NORMALIZAR NIVEL (0–1)
        for r in temp_scores:
            temp_scores[r] = temp_scores[r] / total_nivel

        niveles_scores[nivel] = temp_scores

    # ====================
    # 2. COMBINAR NIVELES
    # ====================
    final_scores = defaultdict(float)

    for nivel, scores in niveles_scores.items():
        peso = pesos_nivel.get(nivel, 1)

        for r in ["R", "I", "A", "S", "E", "C"]:
            final_scores[r] += scores.get(r, 0) * peso

    # ====================
    # 3. NORMALIZAR FINAL
    # ====================
    total_final = sum(final_scores.values()) or 1

    resultado = {}

    for r in ["R", "I", "A", "S", "E", "C"]:
        resultado[r] = round((final_scores[r] / total_final) * 100, 2)

    top = sorted(resultado.items(), key=lambda x: x[1], reverse=True)

    return {
        "perfil": resultado,
        "dominante": top[0][0],
        "top3": [t[0] for t in top[:3]]
    }

def generar_recomendaciones(perfil_data: dict):
    perfil = perfil_data["perfil"]
    top3 = perfil_data["top3"]

    dominante = perfil_data["dominante"]

    # 🎯 PRINCIPAL (una sola carrera fuerte)
    principal_lista = MAPA_CARRERAS.get(dominante, [])
    principal = principal_lista[0] if principal_lista else "Sin definir"

    # 🔹 SECUNDARIAS (sin porcentaje)
    secundarias = []

    for rasgo in top3[1:]:
        secundarias.extend(MAPA_CARRERAS.get(rasgo, []))

    secundarias = list(dict.fromkeys(secundarias))[:6]

    return {
        "principal": principal,
        "secundarias": secundarias
    }

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
async def get_perfil_by_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):

    data = await crud.respuesta_cuestionario_crud.get_filtered(
        db,
        {"id_usuario": id_usuario}
    )

    if not data:
        raise HTTPException(status_code=404, detail="No hay respuestas para este usuario")

    # tomar la última respuesta
    ultima = sorted(data, key=lambda x: x.id_respuesta, reverse=True)[0]

    return calcular_perfil(ultima.respuestas)

# ===================== LÓGICA FINANCIERA =====================

PROGRAMAS_EDUCATIVOS = {
    "R": [
        {"nombre": "Técnico en Electrónica",     "inst": "SENA",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Mecánica Automotriz",          "inst": "SENA",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Tecnología en Construcción",  "inst": "SENA",           "tipo": "Tecnológico",   "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Mecánica",          "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Civil",             "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Industrial",        "inst": "Uniminuto",      "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Ingeniería Mecánica",          "inst": "U. de los Andes","tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "I": [
        {"nombre": "Análisis y Desarrollo de Software","inst": "SENA",      "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Ingeniería de Sistemas",       "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Matemáticas",                  "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería de Sistemas",       "inst": "Uniminuto",      "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Ciencia de Datos",             "inst": "U. de los Andes","tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
        {"nombre": "Física",                       "inst": "U. Javeriana",   "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "A": [
        {"nombre": "Diseño Gráfico",               "inst": "SENA",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Producción Multimedia",        "inst": "SENA",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Artes Visuales",               "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Diseño Gráfico",               "inst": "Uniminuto",      "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Arquitectura",                 "inst": "U. Javeriana",   "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
        {"nombre": "Publicidad",                   "inst": "U. Jorge Tadeo", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "S": [
        {"nombre": "Atención a la Primera Infancia","inst": "SENA",          "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Trabajo Social",               "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Enfermería",                   "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Psicología",                   "inst": "Uniminuto",      "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Docencia",                     "inst": "U. Pedagógica",  "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Psicología",                   "inst": "U. Javeriana",   "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "E": [
        {"nombre": "Técnico en Ventas",            "inst": "SENA",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Administración de Empresas",   "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Administración de Empresas",   "inst": "Uniminuto",      "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Negocios Internacionales",     "inst": "U. EAN",         "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Marketing",                    "inst": "U. de los Andes","tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
        {"nombre": "Emprendimiento e Innovación",  "inst": "U. Javeriana",   "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "C": [
        {"nombre": "Contabilidad y Finanzas",      "inst": "SENA",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Gestión Documental",           "inst": "SENA",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Contaduría Pública",           "inst": "UNAL",           "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Administración",               "inst": "Uniminuto",      "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Finanzas y Comercio Exterior", "inst": "U. EAN",         "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
        {"nombre": "Contaduría Pública",           "inst": "U. Javeriana",   "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
}

BECAS_POR_CAPACIDAD = {
    "baja": [
        "Beca Generación E — cubre el 100% de matrícula en universidades públicas (estratos 1, 2 y 3)",
        "Crédito ICETEX condonable — para estratos 1 y 2",
        "Programas gratuitos SENA — tecnólogos y técnicos sin costo",
        "Fondo de Solidaridad y Garantías (FONSAET) — apoyo a jóvenes vulnerables",
    ],
    "media": [
        "Beca Generación E — para estratos 1, 2 y 3 en universidades públicas",
        "Crédito ICETEX largo plazo — tasas subsidiadas para estrato 3",
        "Descuentos por mérito académico en universidades privadas",
        "Programas técnicos y tecnológicos SENA gratuitos",
    ],
    "alta": [
        "Crédito ICETEX — financiación parcial disponible",
        "Becas por mérito en universidades privadas de alta calidad",
        "Programas de intercambio y doble titulación",
    ],
}

def calcular_capacidad_financiera(data: dict) -> dict:
    estrato       = data.get("estrato", 3)
    ingresos_hogar = data.get("ingresos_hogar", "1-2")
    puede_pagar   = data.get("puede_pagar_matricula", "parcialmente")

    if estrato >= 4 or puede_pagar == "si":
        capacidad = "alta"
    elif estrato <= 2 and ingresos_hogar == "<1" and puede_pagar == "no":
        capacidad = "baja"
    else:
        capacidad = "media"

    elegible  = estrato <= 3
    internet  = data.get("acceso_internet", False)
    computador = data.get("tiene_computador", False)
    disp      = data.get("disponibilidad_tiempo", "completo")
    modalidad = "virtual" if (internet and computador and disp != "completo") else "presencial"

    return {"capacidad_economica": capacidad, "elegible_subsidios": elegible, "modalidad_recomendada": modalidad}

# Modelo hexagonal de Holland: rasgos adyacentes tienen mayor afinidad
HOLLAND_ADYACENTES = {
    "R": ["I", "C"],
    "I": ["R", "A"],
    "A": ["I", "S"],
    "S": ["A", "E"],
    "E": ["S", "C"],
    "C": ["E", "R"],
}

def puntuar_programas(rasgos_scores: dict, capacidad: str, modalidad_pref: str) -> list:
    """
    Scoring ponderado por programa:
      60% RIASEC match  (score directo 80% + bonus adyacente Holland 20%)
      25% match financiero
      15% match modalidad
    """
    COSTOS_OK = {
        "baja":  ["gratuito", "bajo"],
        "media": ["gratuito", "bajo", "medio"],
        "alta":  ["gratuito", "bajo", "medio", "alto"],
    }
    costos_permitidos = COSTOS_OK.get(capacidad, ["gratuito", "bajo", "medio"])
    resultado = []

    for rasgo, programas in PROGRAMAS_EDUCATIVOS.items():
        score_directo = rasgos_scores.get(rasgo, 0) / 100

        adyacentes = HOLLAND_ADYACENTES.get(rasgo, [])
        score_adj = max((rasgos_scores.get(a, 0) for a in adyacentes), default=0) / 100

        riasec_score = (score_directo * 0.80) + (score_adj * 0.20)

        for prog in programas:
            if prog["costo"] in costos_permitidos:
                fin_score = 1.0
            elif prog["con_beca"]:
                fin_score = 0.65
            else:
                continue  # inaccesible sin beca → excluir

            mod_score = 1.0 if modalidad_pref in prog["modalidad"] else 0.3

            total = round((riasec_score * 0.60) + (fin_score * 0.25) + (mod_score * 0.15), 3)
            resultado.append({**prog, "rasgo": rasgo, "score": total})

    vistos, ordenados = set(), []
    for p in sorted(resultado, key=lambda x: x["score"], reverse=True):
        key = (p["nombre"], p["inst"])
        if key not in vistos:
            vistos.add(key)
            ordenados.append(p)

    return ordenados


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
    resp_data      = await crud.respuesta_cuestionario_crud.get_filtered(db, {"id_usuario": id_usuario})
    sin_vocacional = not bool(resp_data)
    top_rasgos     = ["R", "I", "A"]
    rasgos_scores  = {"R": 33, "I": 33, "A": 34, "S": 0, "E": 0, "C": 0}  # defaults
    if resp_data:
        ultima_resp   = sorted(resp_data, key=lambda x: x.id_respuesta, reverse=True)[0]
        perfil_riasec = calcular_perfil(ultima_resp.respuestas)
        top_rasgos    = perfil_riasec["top3"]
        rasgos_scores = perfil_riasec["perfil"]  # scores reales 0-100 por cada rasgo

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

    return {
        "capacidad_economica":   capacidad,
        "elegible_subsidios":    elegible,
        "modalidad_recomendada": modalidad,
        "top_rasgos":            top_rasgos,
        "rasgos_scores":         rasgos_scores,
        "programas":             puntuar_programas(rasgos_scores, capacidad, modalidad),
        "becas":                 BECAS_POR_CAPACIDAD.get(capacidad, []),
        "sin_perfil_financiero": sin_financiero,
        "sin_perfil_vocacional": sin_vocacional,
    }


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
        await db.delete(resp)
    await db.commit()
    return {"message": "Respuestas del cuestionario eliminadas"}


@app.get("/usuarios/{id_usuario}/recomendaciones", tags=["Usuario Perfil"])
async def get_recomendaciones_by_usuario(id_usuario: int, db: AsyncSession = Depends(get_db)):

    data = await crud.respuesta_cuestionario_crud.get_filtered(
        db,
        {"id_usuario": id_usuario}
    )

    if not data:
        raise HTTPException(status_code=404, detail="No hay respuestas para este usuario")

    ultima = sorted(data, key=lambda x: x.id_respuesta, reverse=True)[0]

    perfil = calcular_perfil(ultima.respuestas)

    recomendaciones = generar_recomendaciones(perfil)

    return {
        "perfil": perfil,
        "recomendaciones": recomendaciones
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

            resultado[rel.id_enunciado]["opciones"].append({
                "id": opcion.id_pregunta,
                "texto": opcion.descripcion,
                "rasgo": opcion.rasgo
            })

        return list(resultado.values())

    except Exception as e:
        print("ERROR CRITICO:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

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
            "respuestas": payload.model_dump(),
            "estado": True
        }

        result = await crud.respuesta_cuestionario_crud.create(db, data)

        return {
            "message": "Respuestas guardadas correctamente",
            "id_respuesta": result.id_respuesta
        }

    except Exception as e:
        print("ERROR GUARDANDO RESPUESTAS:", str(e))
        raise HTTPException(status_code=500, detail=str(e))

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