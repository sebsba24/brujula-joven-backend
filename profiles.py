from collections import defaultdict

VALID_RASGOS = {"R", "I", "A", "S", "E", "C", "N"}
# Solo los 6 rasgos RIASEC participan en el scoring; "N" es válido en BD pero no se puntúa
SCORING_RASGOS = ["R", "I", "A", "S", "E", "C"]

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


RASGOS_NOMBRES = {
    "R": "Realista",
    "I": "Investigativo",
    "A": "Artístico",
    "S": "Social",
    "E": "Emprendedor",
    "C": "Convencional",
}

# ── Pesos por nivel ──────────────────────────────────────────────────────────
# Nivel 1 (interés Likert) y Nivel 2 (elección forzada) miden INTERÉS
# Nivel 3 (Likert) mide AUTOEFICACIA — modelo SCCT Lent, Brown & Hackett (1994)
PESOS_INTERES = {"nivel1": 2.0, "nivel2": 1.0}
PESO_INTERES       = 0.60   # Holland (1997): interés como predictor principal
PESO_AUTOEFICACIA  = 0.40   # SCCT: autoeficacia condiciona la elección real

# Suavizado mínimo por rasgo (evita que alguno quede en 0%)
SMOOTH_FLOOR = 0.02


def _normalizar(scores: dict) -> dict:
    """Normaliza un dict de rasgos a proporciones que suman 1."""
    total = sum(scores.values()) or 1
    return {r: scores[r] / total for r in scores}


def _score_nivel(nivel: str, respuestas: dict) -> dict:
    """Devuelve scores crudos por rasgo para un nivel dado."""
    temp = defaultdict(float)
    if nivel == "nivel2":
        for key in respuestas:
            if isinstance(key, str) and key and key[0] in VALID_RASGOS:
                temp[key[0]] += 1.0
    else:
        for key, value in respuestas.items():
            if not isinstance(key, str) or not key:
                continue
            if not isinstance(value, (int, float)) or not (1 <= value <= 5):
                continue
            if key[0] in VALID_RASGOS:
                temp[key[0]] += value
    return dict(temp)


def calcular_perfil(respuestas_json: dict):
    """
    Combina interés (nivel1 + nivel2) y autoeficacia (nivel3) en proporción
    60/40, fundamentado en Holland (1997) y SCCT — Lent, Brown & Hackett (1994).
    Si nivel3 está ausente, el score final equivale sólo a interés (retrocompat.).
    """
    niveles = respuestas_json.get("respuestas", {})

    # ── Scores crudos por nivel ───────────────────────────────────────────────
    scores_por_nivel = {
        nv: _score_nivel(nv, resp)
        for nv, resp in niveles.items()
        if resp
    }

    # ── Componente INTERÉS (nivel1 + nivel2) ─────────────────────────────────
    interes_raw = defaultdict(float)
    for nv, peso in PESOS_INTERES.items():
        if nv in scores_por_nivel:
            norm = _normalizar({r: scores_por_nivel[nv].get(r, 0) for r in SCORING_RASGOS})
            for r in SCORING_RASGOS:
                interes_raw[r] += norm[r] * peso

    interes_norm = _normalizar({r: interes_raw[r] for r in SCORING_RASGOS})

    # ── Componente AUTOEFICACIA (nivel3) ─────────────────────────────────────
    if "nivel3" in scores_por_nivel:
        ae_norm = _normalizar({r: scores_por_nivel["nivel3"].get(r, 0) for r in SCORING_RASGOS})
    else:
        # Sin datos de autoeficacia → se usa interés como proxy (retrocompat.)
        ae_norm = interes_norm.copy()

    # ── Combinación 60 / 40 ───────────────────────────────────────────────────
    final_raw = {
        r: (interes_norm[r] * PESO_INTERES) + (ae_norm[r] * PESO_AUTOEFICACIA)
        for r in SCORING_RASGOS
    }

    # Suavizado mínimo
    for r in SCORING_RASGOS:
        if final_raw[r] < SMOOTH_FLOOR:
            final_raw[r] = SMOOTH_FLOOR

    total = sum(final_raw.values()) or 1
    resultado = {r: round(final_raw[r] / total * 100, 2) for r in SCORING_RASGOS}

    interes_pct      = {r: round(interes_norm[r] * 100, 2) for r in SCORING_RASGOS}
    autoeficacia_pct = {r: round(ae_norm[r] * 100, 2) for r in SCORING_RASGOS}

    top = sorted(resultado.items(), key=lambda x: x[1], reverse=True)

    return {
        "perfil":            resultado,          # combinado 60/40
        "interes":           interes_pct,         # solo interés
        "autoeficacia":      autoeficacia_pct,    # solo autoeficacia
        "dominante":         top[0][0],
        "dominante_nombre":  RASGOS_NOMBRES[top[0][0]],
        "top3":              [t[0] for t in top[:3]],
    }


# ==================== CHASIDE ====================

CHASIDE_PESOS = {
    "C": {"I": 0.6, "R": 0.4},
    "H": {"A": 0.5, "S": 0.5},
    "A": {"A": 1.0},
    "S": {"S": 0.6, "I": 0.4},
    "I": {"R": 0.5, "I": 0.5},
    "D": {"E": 0.5, "S": 0.5},
    "E": {"E": 0.5, "C": 0.5},
}

CHASIDE_NOMBRES = {
    "C": "Ciencias",
    "H": "Humanidades",
    "A": "Arte",
    "S": "Salud",
    "I": "Ingeniería",
    "D": "Derecho y Ciencias Sociales",
    "E": "Economía y Negocios",
}

CHASIDE_DESCRIPCIONES = {
    "C": "Ciencias exactas y naturales: matemáticas, física, química, biología. Orientado a la investigación y el método científico.",
    "H": "Lenguas, comunicación, filosofía, historia y ciencias humanas. Vocación por comprender y expresar la condición humana.",
    "A": "Diseño, artes visuales, música, arquitectura y producción creativa. Orientado a la expresión y la innovación estética.",
    "S": "Medicina, enfermería, psicología, nutrición y bienestar. Vocación por cuidar y mejorar la salud de las personas.",
    "I": "Ingeniería de sistemas, civil, mecánica, electrónica e industrial. Orientado a construir, optimizar y resolver problemas técnicos.",
    "D": "Derecho, trabajo social, ciencias políticas y relaciones internacionales. Vocación por la justicia y el impacto social.",
    "E": "Administración, contaduría, finanzas, mercadeo y emprendimiento. Orientado a los negocios y la gestión organizacional.",
}


def calcular_chaside(perfil_riasec: dict) -> dict:
    scores = {}
    for categoria, pesos in CHASIDE_PESOS.items():
        scores[categoria] = sum(perfil_riasec.get(r, 0) * p for r, p in pesos.items())

    total = sum(scores.values()) or 1
    scores_norm = {k: round(v / total * 100, 1) for k, v in scores.items()}

    top = sorted(scores_norm.items(), key=lambda x: x[1], reverse=True)

    return {
        "scores": scores_norm,
        "dominante": top[0][0],
        "dominante_nombre": CHASIDE_NOMBRES[top[0][0]],
        "top3": [
            {"codigo": t[0], "nombre": CHASIDE_NOMBRES[t[0]], "pct": t[1]}
            for t in top[:3]
        ],
        "descripciones": CHASIDE_DESCRIPCIONES,
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
        {
            "nombre": "Técnico en Electrónica", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "18 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Aprende a instalar, mantener y reparar equipos y sistemas electrónicos industriales y domésticos. Formación práctica con salida laboral inmediata.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Mecánica Automotriz", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "18 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Programa orientado al diagnóstico, mantenimiento y reparación de vehículos automotores. Incluye práctica en talleres dotados con equipos reales.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Tecnología en Construcción", "inst": "SENA", "tipo": "Tecnológico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "2 años", "requisitos": "Bachillerato completo",
            "descripcion": "Forma tecnólogos capaces de supervisar y ejecutar obras civiles, leer planos y aplicar normas sismo-resistentes colombianas (NSR-10).",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Ingeniería Mecánica", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "10 semestres", "requisitos": "Pruebas Saber 11, examen de admisión UNAL",
            "descripcion": "Una de las ingenierías más demandadas del país. Énfasis en diseño de máquinas, termodinámica y manufactura. Alta tasa de empleabilidad en industria y energía.",
            "url": "https://ingmec.unal.edu.co/",
        },
        {
            "nombre": "Ingeniería Civil", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "10 semestres", "requisitos": "Pruebas Saber 11, examen de admisión UNAL",
            "descripcion": "Diseño y construcción de infraestructura: vías, puentes, acueductos y estructuras. Alta demanda en el sector público y privado colombiano.",
            "url": "https://civil.unal.edu.co/",
        },
        {
            "nombre": "Ingeniería Industrial", "inst": "Uniminuto", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Optimización de procesos productivos y cadenas de suministro. Uniminuto ofrece horarios flexibles y modalidad virtual, ideal para quienes trabajan.",
            "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/ingenieria-industrial",
        },
        {
            "nombre": "Ingeniería Mecánica", "inst": "U. de los Andes", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, entrevista, Saber 11",
            "descripcion": "Programa de alta calidad con laboratorios de punta y vínculos con la industria. Reconocida internacionalmente; excelente red de egresados.",
            "url": "https://mecanica.uniandes.edu.co/",
        },
    ],
    "I": [
        {
            "nombre": "Análisis y Desarrollo de Software", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "22 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Uno de los programas más solicitados del SENA. Aprende programación, bases de datos, desarrollo web y móvil con proyectos reales desde el primer semestre.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Ingeniería de Sistemas", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "10 semestres", "requisitos": "Examen de admisión UNAL, Saber 11",
            "descripcion": "Formación sólida en algoritmos, arquitectura de software, inteligencia artificial y redes. Una de las carreras con mayor proyección laboral en Colombia.",
            "url": "https://sistemas.unal.edu.co/",
        },
        {
            "nombre": "Matemáticas", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "10 semestres", "requisitos": "Examen de admisión UNAL, alto puntaje en Saber 11",
            "descripcion": "Carrera para quienes disfrutan el pensamiento abstracto. Salidas laborales en finanzas cuantitativas, ciencia de datos, docencia e investigación.",
            "url": "https://matematicas.unal.edu.co/",
        },
        {
            "nombre": "Ingeniería de Sistemas", "inst": "Uniminuto", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Programa acreditado con enfoque práctico en desarrollo de software, gestión de proyectos TI y transformación digital. Modalidad flexible.",
            "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/ingenieria-de-sistemas",
        },
        {
            "nombre": "Ciencia de Datos", "inst": "U. de los Andes", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "8 semestres", "requisitos": "Bachillerato completo, entrevista, Saber 11",
            "descripcion": "Programa pionero en Colombia. Combina estadística, machine learning y visualización de datos. Altísima demanda en el mercado laboral local e internacional.",
            "url": "https://sistemasydatos.uniandes.edu.co/",
        },
        {
            "nombre": "Física", "inst": "U. Javeriana", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, prueba de admisión Javeriana",
            "descripcion": "Formación científica rigurosa con énfasis en física teórica y computacional. Abre puertas a posgrados en el exterior y a sectores de energía y tecnología.",
            "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-ciencias/fisica",
        },
    ],
    "A": [
        {
            "nombre": "Diseño Gráfico", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "18 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Manejo de herramientas Adobe (Illustrator, Photoshop, InDesign), identidad visual y diseño para medios digitales e impresos.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Producción Multimedia", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "18 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Producción de contenidos audiovisuales, animación, edición de video y fotografía digital. Alta salida laboral en agencias y medios de comunicación.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Artes Visuales", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "10 semestres", "requisitos": "Examen de admisión UNAL, portafolio artístico",
            "descripcion": "Formación integral en artes plásticas, fotografía, instalación y arte contemporáneo. Una de las escuelas de arte más reconocidas de Colombia.",
            "url": "https://artes.unal.edu.co/",
        },
        {
            "nombre": "Diseño Gráfico", "inst": "Uniminuto", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "8 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Diseño visual con énfasis en comunicación digital, branding y UX/UI. Programa con alta demanda laboral en publicidad y medios digitales.",
            "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/diseno-grafico",
        },
        {
            "nombre": "Arquitectura", "inst": "U. Javeriana", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "10 semestres", "requisitos": "Bachillerato completo, portafolio, prueba de admisión",
            "descripcion": "Carrera acreditada de alta calidad con enfoque en diseño sostenible y patrimonio urbano. Destacada en concursos nacionales e internacionales.",
            "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-arquitectura-y-diseno/arquitectura",
        },
        {
            "nombre": "Publicidad", "inst": "U. Jorge Tadeo", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "8 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Referente nacional en publicidad creativa. Énfasis en estrategia de marca, comunicación digital y producción audiovisual publicitaria.",
            "url": "https://www.utadeo.edu.co/es/programa/pregrado/publicidad",
        },
    ],
    "S": [
        {
            "nombre": "Atención a la Primera Infancia", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "18 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Formación para trabajar en jardines infantiles, hogares comunitarios y programas del ICBF. Alta demanda en el sector público.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Trabajo Social", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Examen de admisión UNAL, Saber 11",
            "descripcion": "Intervención en problemáticas sociales, comunitarias y familiares. Salidas laborales en entidades gubernamentales, ONG e instituciones de salud.",
            "url": "https://trabajosocial.unal.edu.co/",
        },
        {
            "nombre": "Enfermería", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "8 semestres", "requisitos": "Examen de admisión UNAL, Saber 11",
            "descripcion": "Carrera de alta vocación de servicio con sólida formación clínica. Oportunidades laborales en Colombia y en el exterior bajo convenios internacionales.",
            "url": "https://enfermeria.unal.edu.co/",
        },
        {
            "nombre": "Psicología", "inst": "Uniminuto", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Formación en psicología clínica, organizacional y social con práctica desde quinto semestre. Programa flexible con opción virtual.",
            "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/psicologia",
        },
        {
            "nombre": "Licenciatura en Educación", "inst": "U. Pedagógica", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "8 semestres", "requisitos": "Examen de admisión UPN, Saber 11",
            "descripcion": "Formación de docentes para básica y media. La Universidad Pedagógica Nacional es la institución líder en formación de maestros en Colombia.",
            "url": "https://www.pedagogica.edu.co/",
        },
        {
            "nombre": "Psicología", "inst": "U. Javeriana", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, entrevista, prueba de admisión",
            "descripcion": "Programa acreditado de alta calidad con énfasis en neurociencias y psicología clínica. Excelente reputación en el mercado laboral.",
            "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-psicologia/psicologia",
        },
    ],
    "E": [
        {
            "nombre": "Técnico en Ventas", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "12 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Habilidades comerciales, atención al cliente, manejo de CRM y técnicas de negociación. Salida laboral inmediata en el sector comercial y de servicios.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Administración de Empresas", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Examen de admisión UNAL, Saber 11",
            "descripcion": "Gestión empresarial con enfoque estratégico, financiero y de innovación. Reconocida como una de las mejores del país por clasificación Sapiens.",
            "url": "https://administracion.unal.edu.co/",
        },
        {
            "nombre": "Administración de Empresas", "inst": "Uniminuto", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Formación en gestión con énfasis en responsabilidad social y emprendimiento. Amplia red de egresados en pymes y grandes empresas colombianas.",
            "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/administracion-de-empresas",
        },
        {
            "nombre": "Negocios Internacionales", "inst": "U. EAN", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "8 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Comercio exterior, logística internacional y negociación multicultural. La EAN tiene convenios con más de 80 universidades en el exterior.",
            "url": "https://www.universidadean.edu.co/programas/pregrado/negocios-internacionales",
        },
        {
            "nombre": "Marketing", "inst": "U. de los Andes", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "8 semestres", "requisitos": "Bachillerato completo, entrevista, Saber 11",
            "descripcion": "Marketing digital, estrategia de marca y comportamiento del consumidor. Programa con alta empleabilidad en multinacionales y agencias digitales.",
            "url": "https://administracion.uniandes.edu.co/programas/pregrado/marketing",
        },
        {
            "nombre": "Emprendimiento e Innovación", "inst": "U. Javeriana", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "8 semestres", "requisitos": "Bachillerato completo, prueba de admisión",
            "descripcion": "Único programa en Colombia 100% enfocado en creación de empresas. Acceso al ecosistema de startups Javeriano y fondos de inversión ángel.",
            "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-ciencias-economicas-y-administrativas/emprendimiento-e-innovacion",
        },
    ],
    "C": [
        {
            "nombre": "Contabilidad y Finanzas", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "18 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Manejo de nómina, facturación electrónica, impuestos y contabilidad básica. Programa muy demandado por pymes y contadores públicos.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Gestión Documental", "inst": "SENA", "tipo": "Técnico",
            "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "12 meses", "requisitos": "Bachillerato en curso o completo",
            "descripcion": "Organización y conservación de archivos físicos y digitales según normas ICONTEC. Alta demanda en entidades públicas y privadas.",
            "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html",
        },
        {
            "nombre": "Contaduría Pública", "inst": "UNAL", "tipo": "Universitario",
            "costo": "bajo", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Examen de admisión UNAL, Saber 11",
            "descripcion": "Una de las mejores contadurías del país. Énfasis en auditoría, tributaria y NIIF. Alta tasa de aprobación del examen de habilitación profesional.",
            "url": "https://contaduria.unal.edu.co/",
        },
        {
            "nombre": "Administración", "inst": "Uniminuto", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial", "virtual"], "con_beca": True,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Gestión organizacional con enfoque en procesos administrativos, contabilidad gerencial y liderazgo de equipos. Modalidad flexible.",
            "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/administracion-de-empresas",
        },
        {
            "nombre": "Finanzas y Comercio Exterior", "inst": "U. EAN", "tipo": "Universitario",
            "costo": "medio", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "8 semestres", "requisitos": "Bachillerato completo, Saber 11",
            "descripcion": "Finanzas corporativas, mercados internacionales y gestión de riesgo. Programa con doble titulación disponible con universidades europeas.",
            "url": "https://www.universidadean.edu.co/programas/pregrado/finanzas-y-comercio-exterior",
        },
        {
            "nombre": "Contaduría Pública", "inst": "U. Javeriana", "tipo": "Universitario",
            "costo": "alto", "ciudad": "Bogotá", "modalidad": ["presencial"], "con_beca": False,
            "duracion": "9 semestres", "requisitos": "Bachillerato completo, prueba de admisión Javeriana",
            "descripcion": "Programa acreditado de alta calidad con énfasis en revisoría fiscal, auditoría forense y estándares internacionales NIIF.",
            "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-ciencias-economicas-y-administrativas/contaduria-publica",
        },
    ],
}

BECAS_POR_CAPACIDAD = {
    "baja": [
        "Política de Gratuidad (Matrícula Cero) — matrícula gratuita en IES públicas de pregrado para estudiantes de menores recursos",
        "Crédito ICETEX 100% condonable — líneas para población vulnerable y comunidades étnicas",
        "Programas gratuitos SENA — técnicos y tecnólogos sin costo (inscripción por la plataforma Betowa)",
        "Fondo de Garantías / FoSIES (ICETEX, Ley 1911 de 2018) — respalda créditos a estudiantes sin codeudor",
    ],
    "media": [
        "Política de Gratuidad (Matrícula Cero) — cobertura en IES públicas para estratos 1, 2 y 3",
        "Crédito ICETEX condonable y de largo plazo — tasas subsidiadas",
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


def puntuar_programas(
    rasgos_scores: dict,
    capacidad: str,
    modalidad_pref: str,
    programas_dict: dict | None = None,
) -> list:
    """
    Scoring ponderado:
      60% RIASEC match  (80% directo + 20% Holland adyacente)
      25% financiero
      15% modalidad

    programas_dict: dict rasgo→list[prog]. Si None usa PROGRAMAS_EDUCATIVOS.
    """
    fuente = programas_dict if programas_dict is not None else PROGRAMAS_EDUCATIVOS
    COSTOS_OK = {
        "baja":  ["gratuito", "bajo"],
        "media": ["gratuito", "bajo", "medio"],
        "alta":  ["gratuito", "bajo", "medio", "alto"],
    }
    costos_permitidos = COSTOS_OK.get(capacidad, ["gratuito", "bajo", "medio"])
    resultado = []

    for rasgo, programas in fuente.items():
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
