-- Migración: agregar tabla perfiles_financieros
-- Ejecutar en la base de datos PostgreSQL del proyecto

CREATE SEQUENCE IF NOT EXISTS public.id_perfil_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE TABLE IF NOT EXISTS public.perfiles_financieros (
    id_perfil           INTEGER DEFAULT nextval('public.id_perfil_seq') NOT NULL,

    -- Relación con usuario
    id_usuario          INTEGER NOT NULL REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE,

    -- Paso 1: Hogar
    estrato             INTEGER NOT NULL CHECK (estrato BETWEEN 1 AND 6),
    personas_hogar      INTEGER,
    personas_trabajan   INTEGER,
    ingresos_hogar      VARCHAR(10),   -- '<1', '1-2', '2-4', '4+'

    -- Paso 2: Situación personal
    trabaja_actualmente BOOLEAN DEFAULT FALSE,
    ingresos_propios    VARCHAR(10),   -- 'ninguno', '<1', '1-2', '2+'
    personas_a_cargo    BOOLEAN DEFAULT FALSE,
    tiene_deudas        BOOLEAN DEFAULT FALSE,

    -- Paso 3: Capacidad educativa
    acceso_internet     BOOLEAN DEFAULT FALSE,
    tiene_computador    BOOLEAN DEFAULT FALSE,
    disponibilidad_tiempo VARCHAR(20),  -- 'completo', 'medio', 'fines_semana'
    puede_pagar_matricula VARCHAR(15),  -- 'no', 'parcialmente', 'si'
    recibe_subsidios    BOOLEAN DEFAULT FALSE,

    -- Resultado calculado
    capacidad_economica VARCHAR(10),   -- 'alta', 'media', 'baja'
    elegible_subsidios  BOOLEAN DEFAULT FALSE,

    -- Auditoría
    estado              BOOLEAN DEFAULT TRUE,
    created_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT perfiles_financieros_pkey PRIMARY KEY (id_perfil)
);

CREATE INDEX IF NOT EXISTS idx_perfiles_financieros_usuario
    ON public.perfiles_financieros (id_usuario);

-- Trigger para updated_at automático
CREATE TRIGGER update_perfiles_financieros_updated_at
    BEFORE UPDATE ON public.perfiles_financieros
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();
