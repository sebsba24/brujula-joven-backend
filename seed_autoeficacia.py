"""
Seed: reemplaza las preguntas de nivel 3 con ítems de AUTOEFICACIA.

Fundamento teórico:
  - Holland, J. L. (1997). Making Vocational Choices (3rd ed.). PAR.
  - Lent, R. W., Brown, S. D., & Hackett, G. (1994). Toward a unifying
    social cognitive theory of career and academic interest, choice, and
    performance. Journal of Vocational Behavior, 45(1), 79–122.

Instrucción al responder:
  "¿Qué tan capaz te sientes de hacer esto bien?" (1 = Nada capaz, 5 = Muy capaz)

Uso:
  cd backend
  python seed_autoeficacia.py
"""

import asyncio
from sqlalchemy import text
from database import async_session_maker as AsyncSessionLocal


# ── Ítems de autoeficacia por rasgo RIASEC ────────────────────────────────────
ITEMS_AUTOEFICACIA = [
    # R — Realista
    ("R", "Aprender a reparar aparatos electrónicos o mecánicos con práctica"),
    ("R", "Construir o armar objetos físicos siguiendo instrucciones técnicas"),
    ("R", "Operar maquinaria o herramientas de trabajo con el entrenamiento adecuado"),
    ("R", "Mantener un buen desempeño en trabajos físicos o manuales"),
    ("R", "Instalar o configurar equipos técnicos con supervisión inicial"),

    # I — Investigativo
    ("I", "Entender conceptos científicos o matemáticos complejos si me los explican bien"),
    ("I", "Analizar datos y llegar a conclusiones lógicas por mi cuenta"),
    ("I", "Diseñar y ejecutar un experimento o investigación desde cero"),
    ("I", "Aprender a programar o usar herramientas de análisis de datos"),
    ("I", "Leer e interpretar textos académicos o técnicos especializados"),

    # A — Artístico
    ("A", "Desarrollar un estilo propio en alguna forma de expresión creativa"),
    ("A", "Aprender técnicas de diseño gráfico, fotografía o producción audiovisual"),
    ("A", "Crear piezas artísticas o creativas que otros valoren positivamente"),
    ("A", "Mejorar mis habilidades musicales, visuales o narrativas con práctica"),
    ("A", "Defender mis decisiones creativas frente a críticas o sugerencias"),

    # S — Social
    ("S", "Explicar temas complejos de forma que otros los entiendan fácilmente"),
    ("S", "Generar confianza en personas que están pasando por dificultades"),
    ("S", "Organizar y facilitar actividades grupales de forma efectiva"),
    ("S", "Mantener la calma y ser útil en situaciones emocionalmente difíciles"),
    ("S", "Establecer relaciones de trabajo sólidas con personas muy diferentes a mí"),

    # E — Emprendedor
    ("E", "Presentar y defender una idea frente a personas que toman decisiones"),
    ("E", "Motivar y coordinar a un grupo hacia un objetivo común"),
    ("E", "Identificar oportunidades de negocio y actuar sobre ellas"),
    ("E", "Manejar la presión y la incertidumbre de liderar un proyecto"),
    ("E", "Negociar y llegar a acuerdos favorables en situaciones de conflicto"),

    # C — Convencional
    ("C", "Organizar grandes cantidades de información de forma sistemática y sin errores"),
    ("C", "Aplicar procesos administrativos o contables con precisión"),
    ("C", "Detectar errores en documentos o datos con atención al detalle"),
    ("C", "Planificar proyectos con cronogramas, presupuestos y seguimiento"),
    ("C", "Manejar herramientas de oficina, hojas de cálculo o software administrativo"),
]


async def main():
    async with AsyncSessionLocal() as db:
        # 1. Desactivar preguntas nivel 3 existentes
        await db.execute(
            text("UPDATE preguntas SET estado = FALSE WHERE nivel = 3")
        )
        print("✓ Preguntas nivel 3 anteriores desactivadas")

        # 2. Insertar nuevos ítems de autoeficacia
        inserted = 0
        for rasgo, descripcion in ITEMS_AUTOEFICACIA:
            await db.execute(
                text("""
                    INSERT INTO preguntas (rasgo, descripcion, tipo, nivel, estado)
                    VALUES (:rasgo, :descripcion, 'likert', 3, TRUE)
                """),
                {"rasgo": rasgo, "descripcion": descripcion},
            )
            inserted += 1

        await db.commit()
        print(f"✓ {inserted} ítems de autoeficacia insertados (nivel 3)")
        print("\nDistribución:")
        rasgos = {}
        for rasgo, _ in ITEMS_AUTOEFICACIA:
            rasgos[rasgo] = rasgos.get(rasgo, 0) + 1
        for r, n in sorted(rasgos.items()):
            print(f"  {r}: {n} ítems")


if __name__ == "__main__":
    asyncio.run(main())
