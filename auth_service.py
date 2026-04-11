from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

import models
from security import create_access_token
from security import verify_password  # si lo agregas


class AuthService:

    @staticmethod
    async def authenticate(db: AsyncSession, email: str, password: str):
        result = await db.execute(
            select(models.Usuario).where(models.Usuario.email == email)
        )
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        if not user.estado:
            raise HTTPException(403, "Usuario inactivo")

        return user

    @staticmethod
    def create_token(user):
        return create_access_token({
            "sub": str(user.id_usuario)
        })