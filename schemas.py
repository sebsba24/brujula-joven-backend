from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, List


# ==================== BASE MIXINS ====================

class TimestampSchema(BaseModel):
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class EstadoSchema(BaseModel):
    estado: bool = True

# ==================== UNIVERSIDAD ====================

class UniversidadBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    ubicacion: Optional[str] = None

class UniversidadCreate(UniversidadBase):
    estado: bool = True

class UniversidadUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    ubicacion: Optional[str] = None
    estado: Optional[bool] = None

class UniversidadResponse(UniversidadBase, EstadoSchema, TimestampSchema):
    id_universidad: int

# ==================== CARRERA ====================

class CarreraBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    id_universidad: int

class CarreraCreate(CarreraBase):
    estado: bool = True

class CarreraUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    id_universidad: Optional[int] = None
    estado: Optional[bool] = None

class CarreraResponse(CarreraBase, EstadoSchema, TimestampSchema):
    id_carrera: int

# ==================== ROL ====================

class RolBase(BaseModel):
    nombre: str = Field(..., max_length=50)

class RolCreate(RolBase):
    estado: bool = True

class RolUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=50)
    estado: Optional[bool] = None

class RolResponse(RolBase, EstadoSchema, TimestampSchema):
    id_rol: int

# ==================== SUBSIDIOS ====================

class SubsidioBase(BaseModel):
    nombre: str = Field(..., max_length=200)
    entidad: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None

class SubsidioCreate(SubsidioBase):
    estado: bool = True

class SubsidioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=200)
    entidad: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    estado: Optional[bool] = None

class SubsidioResponse(SubsidioBase, EstadoSchema, TimestampSchema):
    id_subsidio: int

# ==================== USUARIO ====================

class UsuarioBase(BaseModel):
    nombre: str = Field(..., max_length=100)
    email: EmailStr
    tipo_documento: str = Field(..., max_length=10)
    numero_documento: str = Field(..., max_length=25)

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)
    estado: bool = True

class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    tipo_documento: Optional[str] = Field(None, max_length=10)
    numero_documento: Optional[str] = Field(None, max_length=25)
    estado: Optional[bool] = None
    password: Optional[str] = Field(None, min_length=6)

class UsuarioResponse(UsuarioBase, EstadoSchema, TimestampSchema):
    id_usuario: int

# ==================== AUTH ====================

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UsuarioResponse

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# ==================== RELACIONES ====================

class UsuarioRolBase(BaseModel):
    id_usuario: int
    id_rol: int

class UsuarioRolCreate(UsuarioRolBase):
    estado: bool = True

class UsuarioRolResponse(UsuarioRolBase, EstadoSchema, TimestampSchema):
    id_usuario_rol: int

class UsuarioCarreraBase(BaseModel):
    id_usuario: int
    id_carrera: int

class UsuarioCarreraCreate(UsuarioCarreraBase):
    estado: bool = True

class UsuarioCarreraResponse(UsuarioCarreraBase, EstadoSchema, TimestampSchema):
    id_usuario_carrera: int

class UsuarioSubsidioBase(BaseModel):
    id_usuario: int
    id_subsidio: int

class UsuarioSubsidioCreate(UsuarioSubsidioBase):
    estado: bool = True

class UsuarioSubsidioResponse(UsuarioSubsidioBase, EstadoSchema, TimestampSchema):
    id_usuario_subsidio: int

# ==================== PREGUNTAS ====================

class PreguntaBase(BaseModel):
    rasgo: str = Field(..., pattern="^[RIASECN]$")
    descripcion: str
    tipo: str = Field(default="opcion_multiple", max_length=20)
    nivel: int = Field(default=1, ge=1)

class PreguntaCreate(PreguntaBase):
    estado: bool = True

class PreguntaUpdate(BaseModel):
    rasgo: Optional[str] = Field(None, pattern="^[RIASECN]$")
    descripcion: Optional[str] = None
    tipo: Optional[str] = Field(None, max_length=20)
    nivel: Optional[int] = Field(None, ge=1)
    estado: Optional[bool] = None

class PreguntaResponse(PreguntaBase, EstadoSchema, TimestampSchema):
    id_pregunta: int

# ============= RESPUESTAS CUESTIONARIO =============

class RespuestaCuestionarioBase(BaseModel):
    id_usuario: int
    id_pregunta: int
    valor: int = Field(..., ge=1, le=5)

class RespuestaCuestionarioCreate(BaseModel):
    id_usuario: int
    respuestas: Dict[str, Dict[str, int]]
    estado: bool = True

class RespuestaCuestionarioUpdate(BaseModel):
    valor: Optional[int] = Field(None, ge=1, le=5)

class RespuestaCuestionarioResponse(TimestampSchema):
    id_respuesta: int
    id_usuario: int
    respuestas: Dict[str, Dict[str, int]]
    estado: bool

# ================ CALCULO DE PERFIL ================

class PerfilResponse(BaseModel):
    perfil: Dict[str, float]
    dominante: str
    dominante_nombre: str
    top3: List[str]