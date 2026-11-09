from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import pyotp

import models
from security import create_access_token, create_temp_token, decode_access_token
from security import verify_password


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
    def create_token(user) -> str:
        return create_access_token({"sub": str(user.id_usuario)})

    @staticmethod
    def build_login_response(user) -> dict:
        """Devuelve el dict de respuesta de login según si el usuario tiene 2FA activo."""
        if user.totp_enabled:
            return {
                "requires_2fa": True,
                "temp_token": create_temp_token(user.id_usuario),
            }
        return {
            "access_token": create_access_token({"sub": str(user.id_usuario)}),
            "token_type": "bearer",
            "user": user,
            "requires_2fa": False,
        }

    # ==================== TOTP ====================

    @staticmethod
    def generate_totp_secret() -> str:
        return pyotp.random_base32()

    @staticmethod
    def get_totp_uri(secret: str, email: str) -> str:
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=email,
            issuer_name="NextSteps",
        )

    @staticmethod
    def verify_totp(secret: str, code: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    @staticmethod
    async def complete_2fa_login(db: AsyncSession, temp_token: str, code: str):
        """Valida el token temporal y el código TOTP; retorna el usuario si todo es correcto."""
        payload = decode_access_token(temp_token)
        if not payload or not payload.get("2fa_pending"):
            raise HTTPException(401, "Token inválido o expirado")

        user_id = int(payload["sub"])
        result = await db.execute(
            select(models.Usuario).where(models.Usuario.id_usuario == user_id)
        )
        user = result.scalar_one_or_none()
        if not user or not user.totp_enabled or not user.totp_secret:
            raise HTTPException(401, "Usuario inválido")

        if not AuthService.verify_totp(user.totp_secret, code):
            raise HTTPException(401, "Código incorrecto")

        return user
