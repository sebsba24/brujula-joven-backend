"""Migración: agrega columnas totp_secret y totp_enabled a la tabla usuarios."""
import asyncio
import asyncpg
from config import get_settings

async def main():
    settings = get_settings()
    dsn = settings.database_url.replace("postgresql+asyncpg://", "postgresql://")
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute("""
            ALTER TABLE usuarios
            ADD COLUMN IF NOT EXISTS totp_secret TEXT,
            ADD COLUMN IF NOT EXISTS totp_enabled BOOLEAN NOT NULL DEFAULT FALSE
        """)
        print("✅ Columnas totp_secret y totp_enabled agregadas (o ya existían).")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(main())
