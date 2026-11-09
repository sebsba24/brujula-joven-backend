"""
Seed: reemplaza las preguntas de NIVEL 1 y NIVEL 2 con ítems propios
basados en las dimensiones de Holland (RIASEC).

Fundamento teórico:
  - Holland, J. L. (1997). Making Vocational Choices (3rd ed.). PAR.
  - Rounds, J., & Su, R. (2014). The nature and power of interests.
    Current Directions in Psychological Science, 23(2), 98–103.

Instrucción al responder (nivel 1):
  "¿Qué tanto te gustaría hacer esto?" (1 = Nada, 5 = Mucho)

Instrucción al responder (nivel 2):
  "En cada situación, elige la opción que más se ajuste a ti."

Uso:
  cd backend
  python seed_cuestionario.py
"""

import asyncio
from sqlalchemy import text
from database import async_session_maker as AsyncSessionLocal


# ── Nivel 1: Ítems de INTERÉS por rasgo (Likert 1–5) ────────────────────────
ITEMS_NIVEL1 = [
    # R — Realista
    ("R", "Armar o reparar aparatos electrónicos o mecánicos"),
    ("R", "Trabajar al aire libre con herramientas o maquinaria pesada"),
    ("R", "Construir muebles, estructuras u objetos con mis manos"),
    ("R", "Programar robots o automatizar procesos físicos"),
    ("R", "Practicar actividades físicas intensas o deportes de alto rendimiento"),

    # I — Investigativo
    ("I", "Investigar las causas de un fenómeno científico o social"),
    ("I", "Resolver problemas matemáticos o de lógica complejos"),
    ("I", "Leer sobre descubrimientos científicos o avances tecnológicos"),
    ("I", "Diseñar experimentos para comprobar una hipótesis"),
    ("I", "Analizar grandes conjuntos de datos para encontrar patrones"),

    # A — Artístico
    ("A", "Crear composiciones musicales o interpretar música"),
    ("A", "Escribir cuentos, poemas o guiones creativos"),
    ("A", "Diseñar piezas visuales como logos, ilustraciones o fotografías"),
    ("A", "Actuar, dirigir o producir contenido para teatro o cine"),
    ("A", "Decorar espacios o diseñar ambientes con criterio estético"),

    # S — Social
    ("S", "Enseñar o tutorear a otras personas en algo que domino"),
    ("S", "Brindar apoyo emocional a alguien en una situación difícil"),
    ("S", "Trabajar en proyectos que mejoren la vida de una comunidad"),
    ("S", "Mediar conflictos entre personas o grupos con posturas opuestas"),
    ("S", "Organizar actividades de bienestar o recreación para grupos"),

    # E — Emprendedor
    ("E", "Crear y liderar mi propio proyecto o empresa"),
    ("E", "Convencer a otros de adoptar mis ideas o propuestas"),
    ("E", "Negociar contratos o acuerdos comerciales"),
    ("E", "Identificar y aprovechar oportunidades de mercado"),
    ("E", "Coordinar y motivar equipos hacia una meta ambiciosa"),

    # C — Convencional
    ("C", "Organizar archivos, bases de datos o inventarios de forma sistemática"),
    ("C", "Llevar la contabilidad o las finanzas de una organización"),
    ("C", "Revisar documentos en busca de errores o inconsistencias"),
    ("C", "Aplicar procedimientos establecidos con precisión y orden"),
    ("C", "Planificar horarios, presupuestos o cronogramas detallados"),
]


# ── Nivel 2: Escenarios de ELECCIÓN FORZADA ────────────────────────────────
# Formato: (enunciado_texto, rasgo_A, texto_opcion_A, rasgo_B, texto_opcion_B)
# Cubre los 6 pares adyacentes del hexágono + 2 pares opuestos (I↔C, R↔E)
ESCENARIOS_NIVEL2 = [
    (
        "En una feria de ciencias, ¿qué preferiría hacer?",
        "R", "Construir y demostrar el funcionamiento de un prototipo físico",
        "I", "Presentar los resultados de una investigación experimental",
    ),
    (
        "Si pudiera diseñar un proyecto libre para la universidad, elegiría:",
        "I", "Un estudio sobre el impacto de la tecnología en el comportamiento humano",
        "A", "Una serie de fotografías o instalaciones que exploren una emoción profunda",
    ),
    (
        "El fin de semana largo ideal para mí sería:",
        "A", "Aprender una técnica nueva de diseño o producción artística",
        "S", "Ser voluntario en una organización que apoya a personas vulnerables",
    ),
    (
        "Si fuera a liderar un proyecto comunitario, mi rol preferido sería:",
        "S", "Escuchar las necesidades del grupo y brindar acompañamiento cercano",
        "E", "Diseñar la estrategia, conseguir recursos y dirigir al equipo",
    ),
    (
        "Al emprender un negocio, lo que más me motivaría sería:",
        "E", "Conquistar nuevos mercados y hacer crecer la empresa rápidamente",
        "C", "Asegurar que los procesos internos sean eficientes y libres de errores",
    ),
    (
        "Para gestionar un evento grande, preferiría encargarme de:",
        "C", "Organizar la logística, el presupuesto y la documentación del evento",
        "R", "Supervisar la instalación del equipo técnico y el montaje del espacio",
    ),
    (
        "Frente a un problema urgente en la empresa, mi primera reacción sería:",
        "R", "Buscar una solución técnica y práctica y ejecutarla yo mismo",
        "E", "Reunir al equipo, delegar responsabilidades y coordinar la respuesta",
    ),
    (
        "En mi trabajo ideal, pasaría la mayor parte del tiempo:",
        "I", "Investigando, analizando datos y generando conocimiento nuevo",
        "C", "Aplicando metodologías probadas con rigor y atención al detalle",
    ),
]

GRUPO_NIVEL2 = "A"


async def main():
    async with AsyncSessionLocal() as db:

        # ── NIVEL 1 ──────────────────────────────────────────────────────────
        await db.execute(text("UPDATE preguntas SET estado = FALSE WHERE nivel = 1"))
        print("✓ Preguntas nivel 1 anteriores desactivadas")

        inserted_n1 = 0
        for rasgo, descripcion in ITEMS_NIVEL1:
            await db.execute(
                text("""
                    INSERT INTO preguntas (rasgo, descripcion, tipo, nivel, estado)
                    VALUES (:rasgo, :descripcion, 'likert', 1, TRUE)
                """),
                {"rasgo": rasgo, "descripcion": descripcion},
            )
            inserted_n1 += 1

        await db.commit()
        print(f"✓ {inserted_n1} ítems de interés insertados (nivel 1)")

        # ── NIVEL 2 ──────────────────────────────────────────────────────────
        # Desactivar enunciados/opciones existentes de nivel 2
        await db.execute(text("UPDATE preguntas SET estado = FALSE WHERE nivel = 2"))
        print("✓ Preguntas nivel 2 anteriores desactivadas")

        inserted_n2 = 0
        for enunciado_texto, rasgo_a, texto_a, rasgo_b, texto_b in ESCENARIOS_NIVEL2:
            # Insertar enunciado (asignamos el rasgo de la primera opción — no se puntúa)
            result = await db.execute(
                text("""
                    INSERT INTO preguntas (rasgo, descripcion, tipo, nivel, estado)
                    VALUES (:rasgo, :descripcion, 'enunciado', 2, TRUE)
                    RETURNING id_pregunta
                """),
                {"rasgo": rasgo_a, "descripcion": enunciado_texto},
            )
            id_enunciado = result.scalar_one()

            # Insertar opción A
            result_a = await db.execute(
                text("""
                    INSERT INTO preguntas (rasgo, descripcion, tipo, nivel, estado)
                    VALUES (:rasgo, :descripcion, 'opcion', 2, TRUE)
                    RETURNING id_pregunta
                """),
                {"rasgo": rasgo_a, "descripcion": texto_a},
            )
            id_opcion_a = result_a.scalar_one()

            # Insertar opción B
            result_b = await db.execute(
                text("""
                    INSERT INTO preguntas (rasgo, descripcion, tipo, nivel, estado)
                    VALUES (:rasgo, :descripcion, 'opcion', 2, TRUE)
                    RETURNING id_pregunta
                """),
                {"rasgo": rasgo_b, "descripcion": texto_b},
            )
            id_opcion_b = result_b.scalar_one()

            # Enlazar en preguntas_multiples
            await db.execute(
                text("""
                    INSERT INTO preguntas_multiples (id_enunciado, id_pregunta, grupo)
                    VALUES (:id_enunciado, :id_pregunta, :grupo)
                    ON CONFLICT DO NOTHING
                """),
                {"id_enunciado": id_enunciado, "id_pregunta": id_opcion_a, "grupo": GRUPO_NIVEL2},
            )
            await db.execute(
                text("""
                    INSERT INTO preguntas_multiples (id_enunciado, id_pregunta, grupo)
                    VALUES (:id_enunciado, :id_pregunta, :grupo)
                    ON CONFLICT DO NOTHING
                """),
                {"id_enunciado": id_enunciado, "id_pregunta": id_opcion_b, "grupo": GRUPO_NIVEL2},
            )
            inserted_n2 += 1

        await db.commit()
        print(f"✓ {inserted_n2} escenarios de elección forzada insertados (nivel 2)")

        # ── Resumen ───────────────────────────────────────────────────────────
        print("\nDistribución nivel 1:")
        rasgos = {}
        for rasgo, _ in ITEMS_NIVEL1:
            rasgos[rasgo] = rasgos.get(rasgo, 0) + 1
        for r, n in sorted(rasgos.items()):
            print(f"  {r}: {n} ítems")

        print("\nEscenarios nivel 2:")
        for i, (enunciado, ra, _, rb, _) in enumerate(ESCENARIOS_NIVEL2, 1):
            print(f"  {i}. {ra} vs {rb} — {enunciado[:60]}...")


if __name__ == "__main__":
    asyncio.run(main())
