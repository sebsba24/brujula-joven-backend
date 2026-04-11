from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.middleware.cors import CORSMiddleware
from collections import defaultdict
from typing import List
from security import get_current_user

from database import get_db
import crud
import schemas
from routes import auth

app = FastAPI(
    title="Brujula Joven API",
    version="2.0.0"
)

# ==================== CORS ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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