from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas import LoginRequest, LoginResponse
from auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService.authenticate(db, data.email, data.password)

    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = AuthService.create_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }