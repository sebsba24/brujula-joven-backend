-- Índices para acelerar los filtros más frecuentes de la API.
-- El esquema se importa desde el dump (brujula_joven_db.sql), no se crea con los modelos,
-- así que estos índices deben aplicarse una sola vez a la BD existente:
--   psql -U postgres -d brujulaj_db -f migrations/add_indexes.sql

-- /programas-educativos y _cargar_programas_db filtran por rasgo y estado.
CREATE INDEX IF NOT EXISTS ix_carreras_rasgo_estado
    ON carreras (rasgo, estado);

-- get_last_respuesta_by_usuario filtra por (id_usuario, estado) y ordena por id_respuesta.
CREATE INDEX IF NOT EXISTS ix_respuestas_usuario_estado
    ON respuestas_cuestionario (id_usuario, estado);

-- get_last_perfil_financiero filtra por id_usuario.
CREATE INDEX IF NOT EXISTS ix_perfiles_financieros_id_usuario
    ON perfiles_financieros (id_usuario);
