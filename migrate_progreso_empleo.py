import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from config import get_settings

settings = get_settings()

async def main():
    engine = create_async_engine(settings.database_url)
    async with engine.begin() as conn:
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS progreso_empleo (
                id_progreso         SERIAL PRIMARY KEY,
                id_usuario          INTEGER NOT NULL
                                        REFERENCES usuarios(id_usuario)
                                        ON DELETE CASCADE,
                recursos_completados JSONB  DEFAULT '[]'::jsonb,
                created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(id_usuario)
            )
        """))
        print("Tabla progreso_empleo creada (o ya existia).")
    await engine.dispose()

asyncio.run(main())
