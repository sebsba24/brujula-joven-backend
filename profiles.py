from collections import defaultdict

VALID_RASGOS = {"R", "I", "A", "S", "E", "C", "N"}

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

    for nivel, respuestas in niveles.items():

        if nivel == "nivel2":
            valores = list(respuestas.values())
            if len(valores) > 0 and len(set(valores)) == 1:
                continue

        temp_scores = defaultdict(float)

        for key, value in respuestas.items():

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

        for r in temp_scores:
            temp_scores[r] = temp_scores[r] / total_nivel

        niveles_scores[nivel] = temp_scores

    final_scores = defaultdict(float)

    for nivel, scores in niveles_scores.items():
        peso = pesos_nivel.get(nivel, 1)

        for r in ["R", "I", "A", "S", "E", "C"]:
            final_scores[r] += scores.get(r, 0) * peso

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
    top3 = perfil_data["top3"]
    dominante = perfil_data["dominante"]

    principal_lista = MAPA_CARRERAS.get(dominante, [])
    principal = principal_lista[0] if principal_lista else "Sin definir"

    secundarias = []
    for rasgo in top3[1:]:
        secundarias.extend(MAPA_CARRERAS.get(rasgo, []))

    secundarias = list(dict.fromkeys(secundarias))[:6]

    return {
        "principal": principal,
        "secundarias": secundarias
    }


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
    estrato        = data.get("estrato", 3)
    ingresos_hogar = data.get("ingresos_hogar", "1-2")
    puede_pagar    = data.get("puede_pagar_matricula", "parcialmente")

    if estrato >= 4 or puede_pagar == "si":
        capacidad = "alta"
    elif estrato <= 2 and ingresos_hogar == "<1" and puede_pagar == "no":
        capacidad = "baja"
    else:
        capacidad = "media"

    elegible   = estrato <= 3
    internet   = data.get("acceso_internet", False)
    computador = data.get("tiene_computador", False)
    disp       = data.get("disponibilidad_tiempo", "completo")
    modalidad  = "virtual" if (internet and computador and disp != "completo") else "presencial"

    return {"capacidad_economica": capacidad, "elegible_subsidios": elegible, "modalidad_recomendada": modalidad}


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
    Scoring ponderado:
      60% RIASEC match  (80% directo + 20% Holland adyacente)
      25% financiero
      15% modalidad
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
        adyacentes    = HOLLAND_ADYACENTES.get(rasgo, [])
        score_adj     = max((rasgos_scores.get(a, 0) for a in adyacentes), default=0) / 100
        riasec_score  = (score_directo * 0.80) + (score_adj * 0.20)

        for prog in programas:
            if prog["costo"] in costos_permitidos:
                fin_score = 1.0
            elif prog["con_beca"]:
                fin_score = 0.65
            else:
                continue

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
