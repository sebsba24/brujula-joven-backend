from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.exc import IntegrityError
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from fastapi import HTTPException

from database import Base
from security import hash_password
import models

T = TypeVar("T", bound=Base)


class CRUDBase(Generic[T]):
    def __init__(self, model: Type[T], id_field: str):
        self.model = model
        self.id_field = id_field

    # ==================== GET BY ID ====================
    async def get(self, db: AsyncSession, id: int) -> Optional[T]:
        result = await db.execute(
            select(self.model).where(getattr(self.model, self.id_field) == id)
        )
        return result.scalar_one_or_none()

    # ==================== GET ALL ====================
    async def get_all(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[T]:
        query = select(self.model)

        if hasattr(self.model, "estado"):
            query = query.where(getattr(self.model, "estado") == True)

        result = await db.execute(query.offset(skip).limit(limit))
        return list(result.scalars().all())

    # ==================== GET FILTERED ====================
    async def get_filtered(
        self,
        db: AsyncSession,
        filters: Dict[str, Any],
        fields: Optional[List[str]] = None
    ):
        query = select(self.model)

        if hasattr(self.model, "estado"):
            query = query.where(getattr(self.model, "estado") == True)

        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)

        result = await db.execute(query)
        data = result.scalars().all()

        if fields:
            return [
                {field: getattr(row, field) for field in fields if hasattr(row, field)}
                for row in data
            ]

        return list(data)

    # ==================== CREATE ====================
    async def create(self, db: AsyncSession, obj_in: Dict[str, Any]) -> T:
        # Manejo especial para usuarios (hash de contraseña)
        if "password" in obj_in:
            obj_in["password_hash"] = hash_password(obj_in.pop("password"))

        db_obj = self.model(**obj_in)
        db.add(db_obj)

        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    # ==================== UPDATE ====================
    async def update(
        self,
        db: AsyncSession,
        id: int,
        obj_in: Dict[str, Any]
    ) -> Optional[T]:
        db_obj = await self.get(db, id)

        if not db_obj:
            return None

        blocked_fields = {
            "id",
            self.id_field,
            "created_at",
            "updated_at"
        }

        for key, value in obj_in.items():
            if key not in blocked_fields and hasattr(db_obj, key):
                setattr(db_obj, key, value)

        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    # ==================== SOFT DELETE ====================
    async def soft_delete(self, db: AsyncSession, id: int) -> bool:
        db_obj = await self.get(db, id)

        if not db_obj:
            return False

        if hasattr(db_obj, "estado"):
            setattr(db_obj, "estado", False)
        else:
            raise HTTPException(status_code=400, detail="Modelo no soporta soft delete")

        await db.commit()
        return True


# ==================== INSTANCIAS CRUD ====================

universidad_crud = CRUDBase(models.Universidad, "id_universidad")
carrera_crud = CRUDBase(models.Carrera, "id_carrera")
rol_crud = CRUDBase(models.Rol, "id_rol")
subsidio_crud = CRUDBase(models.ConvenioSubsidio, "id_subsidio")
usuario_crud = CRUDBase(models.Usuario, "id_usuario")
usuario_rol_crud = CRUDBase(models.UsuarioRol, "id_usuario_rol")
usuario_carrera_crud = CRUDBase(models.UsuarioCarrera, "id_usuario_carrera")
usuario_subsidio_crud = CRUDBase(models.UsuarioSubsidio, "id_usuario_subsidio")
pregunta_crud = CRUDBase(models.Pregunta, "id_pregunta")
respuesta_cuestionario_crud = CRUDBase(models.RespuestaCuestionario, "id_respuesta")


# ==================== MÉTODOS ESPECIALES ====================

async def get_preguntas_multiples(db: AsyncSession):
    result = await db.execute(select(models.PreguntaMultiple))
    return list(result.scalars().all())

async def get_last_respuesta_by_usuario(db: AsyncSession, id_usuario: int):
    query = (
        select(models.RespuestaCuestionario)
        .where(models.RespuestaCuestionario.id_usuario == id_usuario)
        .where(models.RespuestaCuestionario.estado == True)
        .order_by(desc(models.RespuestaCuestionario.id_respuesta))
        .limit(1)
    )

    result = await db.execute(query)
    return result.scalar_one_or_none()