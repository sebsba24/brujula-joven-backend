from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import (
    LoginRequest, LoginResponse,
    TwoFASetupResponse, TwoFAVerifySetupRequest,
    TwoFALoginVerifyRequest, TwoFADisableRequest,
)
from auth_service import AuthService
from security import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return AuthService.build_login_response(user)


# ==================== 2FA: verificar código en el login ====================

@router.post("/2fa/verify", response_model=LoginResponse)
async def verify_2fa_login(data: TwoFALoginVerifyRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.complete_2fa_login(db, data.temp_token, data.code)
    return {
        "access_token": AuthService.create_token(user),
        "token_type": "bearer",
        "user": user,
        "requires_2fa": False,
    }


# ==================== 2FA: configurar (usuario ya autenticado) ====================

@router.post("/2fa/setup", response_model=TwoFASetupResponse)
async def setup_2fa(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Genera un secreto TOTP y devuelve el URI para escanear con Google Authenticator."""
    if current_user.totp_enabled:
        raise HTTPException(400, "El 2FA ya está activado. Desactívalo primero.")

    secret = AuthService.generate_totp_secret()
    uri = AuthService.get_totp_uri(secret, current_user.email)

    # Guarda el secreto pendiente (sin habilitar aún)
    current_user.totp_secret = secret
    await db.commit()

    return {"secret": secret, "otpauth_uri": uri}


@router.post("/2fa/enable")
async def enable_2fa(
    data: TwoFAVerifySetupRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Verifica el primer código TOTP y activa el 2FA."""
    if current_user.totp_enabled:
        raise HTTPException(400, "El 2FA ya está activado.")
    if not current_user.totp_secret:
        raise HTTPException(400, "Primero llama a /auth/2fa/setup.")

    if not AuthService.verify_totp(current_user.totp_secret, data.code):
        raise HTTPException(401, "Código incorrecto. Verifica tu aplicación.")

    current_user.totp_enabled = True
    await db.commit()
    return {"message": "Autenticación de dos factores activada exitosamente."}


@router.post("/2fa/disable")
async def disable_2fa(
    data: TwoFADisableRequest,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Desactiva el 2FA después de verificar el código actual."""
    if not current_user.totp_enabled:
        raise HTTPException(400, "El 2FA no está activado.")

    if not AuthService.verify_totp(current_user.totp_secret, data.code):
        raise HTTPException(401, "Código incorrecto.")

    current_user.totp_enabled = False
    current_user.totp_secret = None
    await db.commit()
    return {"message": "Autenticación de dos factores desactivada."}


@router.get("/2fa/status")
async def get_2fa_status(current_user=Depends(get_current_user)):
    """Retorna si el usuario tiene 2FA activado."""
    return {"totp_enabled": current_user.totp_enabled}
