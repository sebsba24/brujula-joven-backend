"""
Migración: cifra en reposo el campo `numero_documento` de la tabla usuarios.

Qué hace:
  1. Cambia la columna a tipo TEXT (el ciphertext es más largo que varchar(25)).
  2. Cifra los valores existentes que aún estén en texto plano (omite los ya cifrados).

Uso (contra la BD que apunte DATABASE_URL, con el mismo ENCRYPTION_KEY):
    python migrate_encrypt_cedula.py

Para producción: exporta DATABASE_URL (Supabase) y ENCRYPTION_KEY antes de correrlo.
Haz un respaldo de la tabla antes de ejecutar en producción.
"""
import asyncio

from sqlalchemy import text
from cryptography.fernet import InvalidToken

from database import engine
from crypto import encrypt, decrypt


async def main():
    cifrados = 0
    total = 0
    async with engine.begin() as conn:
        # 1. Asegurar que la columna admita ciphertext (texto largo)
        await conn.execute(
            text("ALTER TABLE usuarios ALTER COLUMN numero_documento TYPE text")
        )

        # 2. Leer valores crudos (text() evita el cifrado del ORM)
        result = await conn.execute(
            text("SELECT id_usuario, numero_documento FROM usuarios")
        )
        filas = result.fetchall()
        total = len(filas)

        for id_usuario, valor in filas:
            if valor is None:
                continue
            # ¿Ya está cifrado? Si descifra bien, se omite.
            try:
                decrypt(valor)
                continue
            except (InvalidToken, ValueError):
                pass
            await conn.execute(
                text("UPDATE usuarios SET numero_documento = :v WHERE id_usuario = :id"),
                {"v": encrypt(str(valor)), "id": id_usuario},
            )
            cifrados += 1

    print(f"Migración completa. Registros cifrados: {cifrados} de {total}.")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
