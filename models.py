from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB
from database import Base


# ==================== BASE MIXIN ====================

class TimestampMixin:
    created_at = Column(DateTime, server_default=func.current_timestamp())
    updated_at = Column(DateTime, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class EstadoMixin:
    estado = Column(Boolean, default=True)


# ==================== UNIVERSIDAD ====================

class Universidad(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "universidades"

    id_universidad = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    ubicacion = Column(Text)

    carreras = relationship("Carrera", back_populates="universidad", cascade="all, delete-orphan")


# ==================== CARRERA ====================

class Carrera(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "carreras"

    id_carrera = Column(Integer, primary_key=True, index=True)
    id_universidad = Column(Integer, ForeignKey("universidades.id_universidad", ondelete="CASCADE"))
    nombre = Column(String(200), nullable=False)

    universidad = relationship("Universidad", back_populates="carreras")
    usuario_carreras = relationship("UsuarioCarrera", back_populates="carrera", cascade="all, delete-orphan")


# ==================== ROL ====================

class Rol(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)

    usuario_roles = relationship("UsuarioRol", back_populates="rol", cascade="all, delete-orphan")


# ==================== SUBSIDIOS ====================

class ConvenioSubsidio(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "convenios_subsidios"

    id_subsidio = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    entidad = Column(String(200))
    descripcion = Column(Text)

    usuario_subsidios = relationship("UsuarioSubsidio", back_populates="subsidio", cascade="all, delete-orphan")


# ==================== USUARIO ====================

class Usuario(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    tipo_documento = Column(String(10), nullable=False)
    numero_documento = Column(String(25), nullable=False)

    usuario_roles = relationship("UsuarioRol", back_populates="usuario", cascade="all, delete-orphan")
    usuario_carreras = relationship("UsuarioCarrera", back_populates="usuario", cascade="all, delete-orphan")
    usuario_subsidios = relationship("UsuarioSubsidio", back_populates="usuario", cascade="all, delete-orphan")
    respuestas_cuestionario = relationship("RespuestaCuestionario", back_populates="usuario", cascade="all, delete-orphan")
    perfiles_financieros = relationship("PerfilFinanciero", back_populates="usuario", cascade="all, delete-orphan")


# ==================== RELACIONES ====================

class UsuarioRol(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "usuario_roles"

    id_usuario_rol = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    id_rol = Column(Integer, ForeignKey("roles.id_rol", ondelete="CASCADE"))

    usuario = relationship("Usuario", back_populates="usuario_roles")
    rol = relationship("Rol", back_populates="usuario_roles")


class UsuarioCarrera(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "usuario_carreras"

    id_usuario_carrera = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    id_carrera = Column(Integer, ForeignKey("carreras.id_carrera", ondelete="CASCADE"))

    usuario = relationship("Usuario", back_populates="usuario_carreras")
    carrera = relationship("Carrera", back_populates="usuario_carreras")


class UsuarioSubsidio(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "usuario_subsidios"

    id_usuario_subsidio = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))
    id_subsidio = Column(Integer, ForeignKey("convenios_subsidios.id_subsidio", ondelete="CASCADE"))

    usuario = relationship("Usuario", back_populates="usuario_subsidios")
    subsidio = relationship("ConvenioSubsidio", back_populates="usuario_subsidios")


# ==================== PREGUNTAS ====================

class Pregunta(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "preguntas"

    id_pregunta = Column(Integer, primary_key=True, index=True)
    rasgo = Column(String(1), nullable=False)
    descripcion = Column(Text, nullable=False)
    tipo = Column(String(20), default="opcion_multiple")
    nivel = Column(Integer, default=1)

    __table_args__ = (
        CheckConstraint("rasgo IN ('R','I','A','S','E','C')", name="pregunta_rasgo_check"),
    )

class PreguntaMultiple(Base):
    __tablename__ = "preguntas_multiples"

    id_enunciado = Column(Integer, ForeignKey("preguntas.id_pregunta"), primary_key=True)
    id_pregunta = Column(Integer, ForeignKey("preguntas.id_pregunta"), primary_key=True)
    grupo = Column(String(1), nullable=False)

# ==================== RESPUESTAS CUESTIONARIO ====================

# ==================== PERFIL FINANCIERO ====================

class PerfilFinanciero(Base, TimestampMixin, EstadoMixin):
    __tablename__ = "perfiles_financieros"

    id_perfil = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"))

    # Paso 1: Hogar
    estrato = Column(Integer, nullable=False)
    personas_hogar = Column(Integer)
    personas_trabajan = Column(Integer)
    ingresos_hogar = Column(String(10))           # '<1', '1-2', '2-4', '4+'

    # Paso 2: Situación personal
    trabaja_actualmente = Column(Boolean, default=False)
    ingresos_propios = Column(String(10))          # 'ninguno', '<1', '1-2', '2+'
    personas_a_cargo = Column(Boolean, default=False)
    tiene_deudas = Column(Boolean, default=False)

    # Paso 3: Capacidad educativa
    acceso_internet = Column(Boolean, default=False)
    tiene_computador = Column(Boolean, default=False)
    disponibilidad_tiempo = Column(String(20))     # 'completo', 'medio', 'fines_semana'
    puede_pagar_matricula = Column(String(15))     # 'no', 'parcialmente', 'si'
    recibe_subsidios = Column(Boolean, default=False)

    # Resultado calculado
    capacidad_economica = Column(String(10))       # 'alta', 'media', 'baja'
    elegible_subsidios = Column(Boolean, default=False)

    usuario = relationship("Usuario", back_populates="perfiles_financieros")


# ==================== RESPUESTAS CUESTIONARIO ====================

class RespuestaCuestionario(Base, TimestampMixin):
    __tablename__ = "respuestas_cuestionario"

    id_respuesta = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario"))
    respuestas = Column(JSONB)
    estado = Column(Boolean, default=True)

    usuario = relationship("Usuario", back_populates="respuestas_cuestionario")