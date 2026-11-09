"""
Migración + seed de universidades y programas educativos.
Ejecutar desde la raíz del backend:
  python migrate_programas.py
"""
import asyncio, sys, os
sys.path.insert(0, os.path.dirname(__file__))
os.chdir(os.path.dirname(__file__))

from database import engine
from sqlalchemy import text

UNIVERSIDADES = [
    {"nombre": "SENA",               "ubicacion": "Nacional"},
    {"nombre": "UNAL",               "ubicacion": "Bogotá"},
    {"nombre": "Uniminuto",          "ubicacion": "Bogotá"},
    {"nombre": "U. de los Andes",    "ubicacion": "Bogotá"},
    {"nombre": "U. Javeriana",       "ubicacion": "Bogotá"},
    {"nombre": "U. EAN",             "ubicacion": "Bogotá"},
    {"nombre": "U. Pedagógica",      "ubicacion": "Bogotá"},
    {"nombre": "U. Jorge Tadeo",     "ubicacion": "Bogotá"},
]

PROGRAMAS = [
    # ── R ──────────────────────────────────────────────────────────────────────
    {"rasgo": "R", "inst": "SENA",            "nombre": "Técnico en Electrónica",      "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial","virtual"], "con_beca": True,  "duracion": "18 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Aprende a instalar, mantener y reparar equipos y sistemas electrónicos industriales y domésticos. Formación práctica con salida laboral inmediata.",                                                                                          "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "R", "inst": "SENA",            "nombre": "Mecánica Automotriz",         "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial"],            "con_beca": True,  "duracion": "18 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Programa orientado al diagnóstico, mantenimiento y reparación de vehículos automotores. Incluye práctica en talleres dotados con equipos reales.",                                                                                                "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "R", "inst": "SENA",            "nombre": "Tecnología en Construcción",  "tipo": "Tecnológico",   "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial"],            "con_beca": True,  "duracion": "2 años",      "requisitos": "Bachillerato completo",                                   "descripcion": "Forma tecnólogos capaces de supervisar y ejecutar obras civiles, leer planos y aplicar normas sismo-resistentes colombianas (NSR-10).",                                                                                                             "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "R", "inst": "UNAL",            "nombre": "Ingeniería Mecánica",         "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "10 semestres", "requisitos": "Pruebas Saber 11, examen de admisión UNAL",               "descripcion": "Una de las ingenierías más demandadas del país. Énfasis en diseño de máquinas, termodinámica y manufactura. Alta tasa de empleabilidad en industria y energía.",                                                                                   "url": "https://ingmec.unal.edu.co/"},
    {"rasgo": "R", "inst": "UNAL",            "nombre": "Ingeniería Civil",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "10 semestres", "requisitos": "Pruebas Saber 11, examen de admisión UNAL",               "descripcion": "Diseño y construcción de infraestructura: vías, puentes, acueductos y estructuras. Alta demanda en el sector público y privado colombiano.",                                                                                                        "url": "https://civil.unal.edu.co/"},
    {"rasgo": "R", "inst": "Uniminuto",       "nombre": "Ingeniería Industrial",       "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",    "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Optimización de procesos productivos y cadenas de suministro. Uniminuto ofrece horarios flexibles y modalidad virtual, ideal para quienes trabajan.",                                                                                               "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/ingenieria-industrial"},
    {"rasgo": "R", "inst": "U. de los Andes", "nombre": "Ingeniería Mecánica",         "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "9 semestres",  "requisitos": "Bachillerato completo, entrevista, Saber 11",             "descripcion": "Programa de alta calidad con laboratorios de punta y vínculos con la industria. Reconocida internacionalmente; excelente red de egresados.",                                                                                                        "url": "https://mecanica.uniandes.edu.co/"},
    # ── I ──────────────────────────────────────────────────────────────────────
    {"rasgo": "I", "inst": "SENA",            "nombre": "Análisis y Desarrollo de Software", "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial","virtual"], "con_beca": True,  "duracion": "22 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Uno de los programas más solicitados del SENA. Aprende programación, bases de datos, desarrollo web y móvil con proyectos reales desde el primer semestre.",                                                                                        "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "I", "inst": "UNAL",            "nombre": "Ingeniería de Sistemas",      "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "10 semestres", "requisitos": "Examen de admisión UNAL, Saber 11",                       "descripcion": "Formación sólida en algoritmos, arquitectura de software, inteligencia artificial y redes. Una de las carreras con mayor proyección laboral en Colombia.",                                                                                          "url": "https://sistemas.unal.edu.co/"},
    {"rasgo": "I", "inst": "UNAL",            "nombre": "Matemáticas",                 "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "10 semestres", "requisitos": "Examen de admisión UNAL, alto puntaje en Saber 11",       "descripcion": "Carrera para quienes disfrutan el pensamiento abstracto. Salidas laborales en finanzas cuantitativas, ciencia de datos, docencia e investigación.",                                                                                                  "url": "https://matematicas.unal.edu.co/"},
    {"rasgo": "I", "inst": "Uniminuto",       "nombre": "Ingeniería de Sistemas",      "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",    "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Programa acreditado con enfoque práctico en desarrollo de software, gestión de proyectos TI y transformación digital. Modalidad flexible.",                                                                                                          "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/ingenieria-de-sistemas"},
    {"rasgo": "I", "inst": "U. de los Andes", "nombre": "Ciencia de Datos",           "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "8 semestres",  "requisitos": "Bachillerato completo, entrevista, Saber 11",             "descripcion": "Programa pionero en Colombia. Combina estadística, machine learning y visualización de datos. Altísima demanda en el mercado laboral local e internacional.",                                                                                       "url": "https://sistemasydatos.uniandes.edu.co/"},
    {"rasgo": "I", "inst": "U. Javeriana",    "nombre": "Física",                      "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "9 semestres",  "requisitos": "Bachillerato completo, prueba de admisión Javeriana",    "descripcion": "Formación científica rigurosa con énfasis en física teórica y computacional. Abre puertas a posgrados en el exterior y a sectores de energía y tecnología.",                                                                                       "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-ciencias/fisica"},
    # ── A ──────────────────────────────────────────────────────────────────────
    {"rasgo": "A", "inst": "SENA",            "nombre": "Diseño Gráfico",              "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "18 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Manejo de herramientas Adobe (Illustrator, Photoshop, InDesign), identidad visual y diseño para medios digitales e impresos.",                                                                                                                       "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "A", "inst": "SENA",            "nombre": "Producción Multimedia",       "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "18 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Producción de contenidos audiovisuales, animación, edición de video y fotografía digital. Alta salida laboral en agencias y medios de comunicación.",                                                                                                "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "A", "inst": "UNAL",            "nombre": "Artes Visuales",             "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "10 semestres", "requisitos": "Examen de admisión UNAL, portafolio artístico",            "descripcion": "Formación integral en artes plásticas, fotografía, instalación y arte contemporáneo. Una de las escuelas de arte más reconocidas de Colombia.",                                                                                                    "url": "https://artes.unal.edu.co/"},
    {"rasgo": "A", "inst": "Uniminuto",       "nombre": "Diseño Gráfico",              "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",    "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "8 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Diseño visual con énfasis en comunicación digital, branding y UX/UI. Programa con alta demanda laboral en publicidad y medios digitales.",                                                                                                           "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/diseno-grafico"},
    {"rasgo": "A", "inst": "U. Javeriana",    "nombre": "Arquitectura",               "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "10 semestres", "requisitos": "Bachillerato completo, portafolio, prueba de admisión",   "descripcion": "Carrera acreditada de alta calidad con enfoque en diseño sostenible y patrimonio urbano. Destacada en concursos nacionales e internacionales.",                                                                                                      "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-arquitectura-y-diseno/arquitectura"},
    {"rasgo": "A", "inst": "U. Jorge Tadeo",  "nombre": "Publicidad",                 "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "8 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Referente nacional en publicidad creativa. Énfasis en estrategia de marca, comunicación digital y producción audiovisual publicitaria.",                                                                                                             "url": "https://www.utadeo.edu.co/es/programa/pregrado/publicidad"},
    # ── S ──────────────────────────────────────────────────────────────────────
    {"rasgo": "S", "inst": "SENA",            "nombre": "Atención a la Primera Infancia", "tipo": "Técnico",   "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "18 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Formación para trabajar en jardines infantiles, hogares comunitarios y programas del ICBF. Alta demanda en el sector público.",                                                                                                                      "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "S", "inst": "UNAL",            "nombre": "Trabajo Social",              "tipo": "Universitario", "costo": "bajo",    "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Examen de admisión UNAL, Saber 11",                       "descripcion": "Intervención en problemáticas sociales, comunitarias y familiares. Salidas laborales en entidades gubernamentales, ONG e instituciones de salud.",                                                                                                   "url": "https://trabajosocial.unal.edu.co/"},
    {"rasgo": "S", "inst": "UNAL",            "nombre": "Enfermería",                  "tipo": "Universitario", "costo": "bajo",    "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "8 semestres",  "requisitos": "Examen de admisión UNAL, Saber 11",                       "descripcion": "Carrera de alta vocación de servicio con sólida formación clínica. Oportunidades laborales en Colombia y en el exterior bajo convenios internacionales.",                                                                                            "url": "https://enfermeria.unal.edu.co/"},
    {"rasgo": "S", "inst": "Uniminuto",       "nombre": "Psicología",                  "tipo": "Universitario", "costo": "medio",   "ciudad": "Bogotá",    "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Formación en psicología clínica, organizacional y social con práctica desde quinto semestre. Programa flexible con opción virtual.",                                                                                                                 "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/psicologia"},
    {"rasgo": "S", "inst": "U. Pedagógica",   "nombre": "Licenciatura en Educación",   "tipo": "Universitario", "costo": "bajo",    "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "8 semestres",  "requisitos": "Examen de admisión UPN, Saber 11",                        "descripcion": "Formación de docentes para básica y media. La Universidad Pedagógica Nacional es la institución líder en formación de maestros en Colombia.",                                                                                                        "url": "https://www.pedagogica.edu.co/"},
    {"rasgo": "S", "inst": "U. Javeriana",    "nombre": "Psicología",                  "tipo": "Universitario", "costo": "alto",    "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "9 semestres",  "requisitos": "Bachillerato completo, entrevista, prueba de admisión",   "descripcion": "Programa acreditado de alta calidad con énfasis en neurociencias y psicología clínica. Excelente reputación en el mercado laboral.",                                                                                                                "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-psicologia/psicologia"},
    # ── E ──────────────────────────────────────────────────────────────────────
    {"rasgo": "E", "inst": "SENA",            "nombre": "Técnico en Ventas",           "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "12 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Habilidades comerciales, atención al cliente, manejo de CRM y técnicas de negociación. Salida laboral inmediata en el sector comercial y de servicios.",                                                                                             "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "E", "inst": "UNAL",            "nombre": "Administración de Empresas",  "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Examen de admisión UNAL, Saber 11",                       "descripcion": "Gestión empresarial con enfoque estratégico, financiero y de innovación. Reconocida como una de las mejores del país por clasificación Sapiens.",                                                                                                     "url": "https://administracion.unal.edu.co/"},
    {"rasgo": "E", "inst": "Uniminuto",       "nombre": "Administración de Empresas",  "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",    "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Formación en gestión con énfasis en responsabilidad social y emprendimiento. Amplia red de egresados en pymes y grandes empresas colombianas.",                                                                                                      "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/administracion-de-empresas"},
    {"rasgo": "E", "inst": "U. EAN",          "nombre": "Negocios Internacionales",    "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "8 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Comercio exterior, logística internacional y negociación multicultural. La EAN tiene convenios con más de 80 universidades en el exterior.",                                                                                                          "url": "https://www.universidadean.edu.co/programas/pregrado/negocios-internacionales"},
    {"rasgo": "E", "inst": "U. de los Andes", "nombre": "Marketing",                   "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "8 semestres",  "requisitos": "Bachillerato completo, entrevista, Saber 11",             "descripcion": "Marketing digital, estrategia de marca y comportamiento del consumidor. Programa con alta empleabilidad en multinacionales y agencias digitales.",                                                                                                    "url": "https://administracion.uniandes.edu.co/programas/pregrado/marketing"},
    {"rasgo": "E", "inst": "U. Javeriana",    "nombre": "Emprendimiento e Innovación", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "8 semestres",  "requisitos": "Bachillerato completo, prueba de admisión",               "descripcion": "Único programa en Colombia 100% enfocado en creación de empresas. Acceso al ecosistema de startups Javeriano y fondos de inversión ángel.",                                                                                                          "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-ciencias-economicas-y-administrativas/emprendimiento-e-innovacion"},
    # ── C ──────────────────────────────────────────────────────────────────────
    {"rasgo": "C", "inst": "SENA",            "nombre": "Contabilidad y Finanzas",     "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "18 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Manejo de nómina, facturación electrónica, impuestos y contabilidad básica. Programa muy demandado por pymes y contadores públicos.",                                                                                                                "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "C", "inst": "SENA",            "nombre": "Gestión Documental",          "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional",  "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "12 meses",    "requisitos": "Bachillerato en curso o completo",                        "descripcion": "Organización y conservación de archivos físicos y digitales según normas ICONTEC. Alta demanda en entidades públicas y privadas.",                                                                                                                    "url": "https://oferta.senasofiaplus.edu.co/sofia-oferta/detalle-oferta.html"},
    {"rasgo": "C", "inst": "UNAL",            "nombre": "Contaduría Pública",          "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Examen de admisión UNAL, Saber 11",                       "descripcion": "Una de las mejores contadurías del país. Énfasis en auditoría, tributaria y NIIF. Alta tasa de aprobación del examen de habilitación profesional.",                                                                                                   "url": "https://contaduria.unal.edu.co/"},
    {"rasgo": "C", "inst": "Uniminuto",       "nombre": "Administración",              "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",    "modalidad": ["presencial","virtual"],  "con_beca": True,  "duracion": "9 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Gestión organizacional con enfoque en procesos administrativos, contabilidad gerencial y liderazgo de equipos. Modalidad flexible.",                                                                                                                  "url": "https://www.uniminuto.edu/web/bogota-presencial-y-distancia/administracion-de-empresas"},
    {"rasgo": "C", "inst": "U. EAN",          "nombre": "Finanzas y Comercio Exterior","tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "8 semestres",  "requisitos": "Bachillerato completo, Saber 11",                         "descripcion": "Finanzas corporativas, mercados internacionales y gestión de riesgo. Programa con doble titulación disponible con universidades europeas.",                                                                                                          "url": "https://www.universidadean.edu.co/programas/pregrado/finanzas-y-comercio-exterior"},
    {"rasgo": "C", "inst": "U. Javeriana",    "nombre": "Contaduría Pública",          "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",    "modalidad": ["presencial"],            "con_beca": False, "duracion": "9 semestres",  "requisitos": "Bachillerato completo, prueba de admisión Javeriana",    "descripcion": "Programa acreditado de alta calidad con énfasis en revisoría fiscal, auditoría forense y estándares internacionales NIIF.",                                                                                                                         "url": "https://www.javeriana.edu.co/programas/pregrado/facultad-de-ciencias-economicas-y-administrativas/contaduria-publica"},
]


async def main():
    async with engine.begin() as conn:
        # 1. Agregar columnas que faltan en carreras
        print("► Aplicando migración de columnas…")
        await conn.execute(text("""
            ALTER TABLE carreras
                ADD COLUMN IF NOT EXISTS rasgo       VARCHAR(1),
                ADD COLUMN IF NOT EXISTS tipo        VARCHAR(50),
                ADD COLUMN IF NOT EXISTS costo       VARCHAR(20),
                ADD COLUMN IF NOT EXISTS ciudad      VARCHAR(100),
                ADD COLUMN IF NOT EXISTS modalidad   JSONB DEFAULT '[]'::jsonb,
                ADD COLUMN IF NOT EXISTS con_beca    BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS duracion    VARCHAR(50),
                ADD COLUMN IF NOT EXISTS requisitos  TEXT,
                ADD COLUMN IF NOT EXISTS descripcion TEXT,
                ADD COLUMN IF NOT EXISTS url         TEXT
        """))

        # Constraint (ignora si ya existe)
        try:
            await conn.execute(text(
                "ALTER TABLE carreras ADD CONSTRAINT carrera_rasgo_check "
                "CHECK (rasgo IN ('R','I','A','S','E','C'))"
            ))
        except Exception:
            pass  # ya existe

        # 2. Agregar UNIQUE en nombre si no existe
        try:
            await conn.execute(text(
                "ALTER TABLE universidades ADD CONSTRAINT universidades_nombre_key UNIQUE (nombre)"
            ))
        except Exception:
            pass  # ya existe

        # 3. Insertar universidades (ON CONFLICT nombre → update ubicacion)
        print("► Insertando universidades…")
        for u in UNIVERSIDADES:
            await conn.execute(text("""
                INSERT INTO universidades (nombre, ubicacion, estado)
                VALUES (:nombre, :ubicacion, TRUE)
                ON CONFLICT (nombre) DO UPDATE SET ubicacion = EXCLUDED.ubicacion
            """), u)

        # 4. Obtener mapa nombre→id
        rows = await conn.execute(text("SELECT id_universidad, nombre FROM universidades"))
        uni_map = {r.nombre: r.id_universidad for r in rows}

        # 5. Insertar carreras (skip duplicados exactos nombre+institución)
        print("► Insertando programas educativos…")
        inserted = 0
        skipped  = 0
        for p in PROGRAMAS:
            id_uni = uni_map.get(p["inst"])
            if not id_uni:
                print(f"  ⚠  Institución no encontrada: {p['inst']}")
                continue

            exists = await conn.execute(text("""
                SELECT 1 FROM carreras WHERE nombre = :nombre AND id_universidad = :id_uni
            """), {"nombre": p["nombre"], "id_uni": id_uni})
            if exists.fetchone():
                skipped += 1
                continue

            import json
            await conn.execute(text("""
                INSERT INTO carreras
                    (id_universidad, nombre, rasgo, tipo, costo, ciudad,
                     modalidad, con_beca, duracion, requisitos, descripcion, url, estado)
                VALUES
                    (:id_uni, :nombre, :rasgo, :tipo, :costo, :ciudad,
                     :modalidad, :con_beca, :duracion, :requisitos, :descripcion, :url, TRUE)
            """), {
                "id_uni":      id_uni,
                "nombre":      p["nombre"],
                "rasgo":       p["rasgo"],
                "tipo":        p["tipo"],
                "costo":       p["costo"],
                "ciudad":      p["ciudad"],
                "modalidad":   json.dumps(p["modalidad"]),
                "con_beca":    p["con_beca"],
                "duracion":    p["duracion"],
                "requisitos":  p["requisitos"],
                "descripcion": p["descripcion"],
                "url":         p["url"],
            })
            inserted += 1

        print(f"\n✔  Migración completada:")
        print(f"   Universidades: {len(UNIVERSIDADES)}")
        print(f"   Programas insertados: {inserted}")
        print(f"   Programas omitidos (ya existían): {skipped}")


if __name__ == "__main__":
    asyncio.run(main())
