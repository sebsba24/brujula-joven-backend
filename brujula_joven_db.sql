--
-- PostgreSQL database dump
--

\restrict X7unU6nB29V2W07xDkbLfTkLN5wFwAMIwJB8XTF6bn2BpTEu3PgvhlVCocsrjeI

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-04-10 22:16:05

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 4 (class 2615 OID 2200)
-- Name: public; Type: SCHEMA; Schema: -; Owner: pg_database_owner
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO pg_database_owner;

--
-- TOC entry 5167 (class 0 OID 0)
-- Dependencies: 4
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: pg_database_owner
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- TOC entry 240 (class 1255 OID 16572)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 16573)
-- Name: id_carrera_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_carrera_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_carrera_seq OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 220 (class 1259 OID 16574)
-- Name: carreras; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.carreras (
    id_carrera integer DEFAULT nextval('public.id_carrera_seq'::regclass) NOT NULL,
    id_universidad integer,
    nombre character varying(200) NOT NULL,
    estado boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.carreras OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 16583)
-- Name: id_subsidio_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_subsidio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_subsidio_seq OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 16584)
-- Name: convenios_subsidios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.convenios_subsidios (
    id_subsidio integer DEFAULT nextval('public.id_subsidio_seq'::regclass) NOT NULL,
    nombre character varying(200) NOT NULL,
    entidad character varying(200),
    descripcion text,
    estado boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.convenios_subsidios OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 16595)
-- Name: preguntas; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.preguntas (
    id_pregunta integer NOT NULL,
    rasgo character varying(1) NOT NULL,
    descripcion text NOT NULL,
    tipo character varying(20) DEFAULT 'opcion_multiple'::character varying,
    nivel integer DEFAULT 1,
    estado boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.preguntas OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 16608)
-- Name: id_pregunta_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_pregunta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_pregunta_seq OWNER TO postgres;

--
-- TOC entry 5168 (class 0 OID 0)
-- Dependencies: 224
-- Name: id_pregunta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.id_pregunta_seq OWNED BY public.preguntas.id_pregunta;


--
-- TOC entry 225 (class 1259 OID 16609)
-- Name: id_respuesta_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_respuesta_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_respuesta_seq OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 16610)
-- Name: id_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_rol_seq OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 16611)
-- Name: id_universidad_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_universidad_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_universidad_seq OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 16612)
-- Name: id_usuario_carrera_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_usuario_carrera_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_usuario_carrera_seq OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 16613)
-- Name: id_usuario_rol_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_usuario_rol_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_usuario_rol_seq OWNER TO postgres;

--
-- TOC entry 230 (class 1259 OID 16614)
-- Name: id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_usuario_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_usuario_seq OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 16615)
-- Name: id_usuario_subsidio_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_usuario_subsidio_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_usuario_subsidio_seq OWNER TO postgres;

--
-- TOC entry 239 (class 1259 OID 16761)
-- Name: preguntas_multiples; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.preguntas_multiples (
    id_enunciado integer NOT NULL,
    id_pregunta integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estado boolean,
    grupo character varying(1)
);


ALTER TABLE public.preguntas_multiples OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 16616)
-- Name: respuestas_cuestionario; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.respuestas_cuestionario (
    id_respuesta integer DEFAULT nextval('public.id_respuesta_seq'::regclass) NOT NULL,
    id_usuario integer NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    respuestas jsonb,
    estado boolean DEFAULT true
);


ALTER TABLE public.respuestas_cuestionario OWNER TO postgres;

--
-- TOC entry 233 (class 1259 OID 16623)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id_rol integer DEFAULT nextval('public.id_rol_seq'::regclass) NOT NULL,
    nombre character varying(50) NOT NULL,
    estado boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 234 (class 1259 OID 16632)
-- Name: universidades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.universidades (
    id_universidad integer DEFAULT nextval('public.id_universidad_seq'::regclass) NOT NULL,
    nombre character varying(200) NOT NULL,
    ubicacion text,
    estado boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.universidades OWNER TO postgres;

--
-- TOC entry 235 (class 1259 OID 16643)
-- Name: usuario_carreras; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario_carreras (
    id_usuario_carrera integer DEFAULT nextval('public.id_usuario_carrera_seq'::regclass) NOT NULL,
    id_usuario integer,
    id_carrera integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estado boolean
);


ALTER TABLE public.usuario_carreras OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 16649)
-- Name: usuario_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario_roles (
    id_usuario_rol integer DEFAULT nextval('public.id_usuario_rol_seq'::regclass) NOT NULL,
    id_usuario integer,
    id_rol integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    estado boolean
);


ALTER TABLE public.usuario_roles OWNER TO postgres;

--
-- TOC entry 237 (class 1259 OID 16655)
-- Name: usuario_subsidios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuario_subsidios (
    id_usuario_subsidio integer DEFAULT nextval('public.id_usuario_subsidio_seq'::regclass) NOT NULL,
    id_usuario integer,
    id_subsidio integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at time without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.usuario_subsidios OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 16661)
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.usuarios (
    id_usuario integer DEFAULT nextval('public.id_usuario_seq'::regclass) NOT NULL,
    nombre character varying(100) NOT NULL,
    email character varying(150) NOT NULL,
    password_hash text NOT NULL,
    tipo_documento character varying(10) NOT NULL,
    numero_documento character varying(25) NOT NULL,
    estado boolean DEFAULT true,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- TOC entry 4914 (class 2604 OID 16676)
-- Name: preguntas id_pregunta; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preguntas ALTER COLUMN id_pregunta SET DEFAULT nextval('public.id_pregunta_seq'::regclass);


--
-- TOC entry 5142 (class 0 OID 16574)
-- Dependencies: 220
-- Data for Name: carreras; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5144 (class 0 OID 16584)
-- Dependencies: 222
-- Data for Name: convenios_subsidios; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5145 (class 0 OID 16595)
-- Dependencies: 223
-- Data for Name: preguntas; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.preguntas (id_pregunta, rasgo, descripcion, tipo, nivel, estado, created_at, updated_at) VALUES
	(1, 'R', 'Cuando algo se daña, intento revisarlo o arreglarlo', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(2, 'R', 'Prefiero usar herramientas antes que solo leer o escuchar', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(3, 'I', 'Busco información hasta entender un tema completamente', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(4, 'I', 'Disfruto resolver problemas que requieren varios pasos', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(5, 'A', 'Intento dar estilo propio a mis trabajos o tareas', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(6, 'A', 'Creo contenido por iniciativa propia (dibujos, videos, textos)', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(7, 'S', 'Explico temas a compañeros cuando no entienden', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(8, 'S', 'Procuro que todos participen en trabajos grupales', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(9, 'E', 'Tomo iniciativa para organizar actividades en grupo', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(10, 'E', 'Me siento cómodo tomando decisiones importantes', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(11, 'C', 'Organizo tareas usando listas o métodos claros', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(12, 'C', 'Sigo instrucciones paso a paso sin omitir detalles', 'Likert', 1, true, '2026-03-27 22:03:40.576987', '2026-03-27 22:03:40.576987'),
	(13, 'R', 'Intento reparar objetos antes de reemplazarlos', 'Likert', 3, true, '2026-03-27 22:08:44.693212', '2026-03-27 22:08:44.693212'),
	(14, 'R', 'Me interesa cómo funcionan los objetos por dentro', 'Likert', 3, true, '2026-03-27 22:08:44.693212', '2026-03-27 22:08:44.693212'),
	(15, 'R', 'Prefiero actividades prácticas a leer teoría', 'Likert', 3, true, '2026-03-27 22:08:44.693212', '2026-03-27 22:08:44.693212'),
	(16, 'R', 'Disfruto tareas con resultados visibles', 'Likert', 3, true, '2026-03-27 22:08:44.693212', '2026-03-27 22:08:44.693212'),
	(17, 'R', 'Prefiero trabajar con objetos que ideas abstractas', 'Likert', 3, true, '2026-03-27 22:08:44.693212', '2026-03-27 22:08:44.693212'),
	(18, 'R', 'He armado o desarmado cosas por iniciativa propia', 'Likert', 3, true, '2026-03-27 22:08:44.693212', '2026-03-27 22:08:44.693212'),
	(19, 'R', 'Aprendo mejor haciendo que escuchando', 'Likert', 3, true, '2026-03-27 22:08:44.693212', '2026-03-27 22:08:44.693212'),
	(20, 'I', 'Busco causas antes de solucionar problemas', 'Likert', 3, true, '2026-03-27 22:10:17.509669', '2026-03-27 22:10:17.509669');
INSERT INTO public.preguntas (id_pregunta, rasgo, descripcion, tipo, nivel, estado, created_at, updated_at) VALUES
	(21, 'I', 'Comparo diferentes soluciones para un problema', 'Likert', 3, true, '2026-03-27 22:10:17.509669', '2026-03-27 22:10:17.509669'),
	(22, 'I', 'Disfruto analizar información o patrones', 'Likert', 3, true, '2026-03-27 22:10:17.509669', '2026-03-27 22:10:17.509669'),
	(23, 'I', 'Hago preguntas para entender mejor los temas', 'Likert', 3, true, '2026-03-27 22:10:17.509669', '2026-03-27 22:10:17.509669'),
	(24, 'I', 'Prefiero pensar antes que actuar rápidamente', 'Likert', 3, true, '2026-03-27 22:10:17.509669', '2026-03-27 22:10:17.509669'),
	(25, 'I', 'Me interesan temas complejos', 'Likert', 3, true, '2026-03-27 22:10:17.509669', '2026-03-27 22:10:17.509669'),
	(26, 'I', 'Identifico errores cuando algo falla', 'Likert', 3, true, '2026-03-27 22:10:17.509669', '2026-03-27 22:10:17.509669'),
	(27, 'A', 'Modifico trabajos para hacerlos más originales', 'Likert', 3, true, '2026-03-27 22:13:29.226125', '2026-03-27 22:13:29.226125'),
	(28, 'A', 'Prefiero tareas sin reglas estrictas', 'Likert', 3, true, '2026-03-27 22:13:29.226125', '2026-03-27 22:13:29.226125'),
	(29, 'A', 'Me gusta combinar colores o estilos', 'Likert', 3, true, '2026-03-27 22:13:29.226125', '2026-03-27 22:13:29.226125'),
	(30, 'A', 'Prefiero crear en lugar de repetir instrucciones', 'Likert', 3, true, '2026-03-27 22:13:29.226125', '2026-03-27 22:13:29.226125'),
	(31, 'A', 'Me gustan tareas sin única respuesta correcta', 'Likert', 3, true, '2026-03-27 22:13:29.226125', '2026-03-27 22:13:29.226125'),
	(32, 'A', 'Experimento nuevas formas de hacer cosas', 'Likert', 3, true, '2026-03-27 22:13:29.226125', '2026-03-27 22:13:29.226125'),
	(33, 'A', 'Busco que mi trabajo tenga estilo propio', 'Likert', 3, true, '2026-03-27 22:13:29.226125', '2026-03-27 22:13:29.226125'),
	(34, 'S', 'Intento entender emociones antes de responder', 'Likert', 3, true, '2026-03-27 22:15:17.544418', '2026-03-27 22:15:17.544418'),
	(35, 'S', 'Disfruto interactuar con otras personas', 'Likert', 3, true, '2026-03-27 22:15:17.544418', '2026-03-27 22:15:17.544418'),
	(36, 'S', 'Me siento cómodo explicando temas', 'Likert', 3, true, '2026-03-27 22:15:17.544418', '2026-03-27 22:15:17.544418'),
	(37, 'S', 'Prefiero trabajar en equipo', 'Likert', 3, true, '2026-03-27 22:15:17.544418', '2026-03-27 22:15:17.544418'),
	(38, 'S', 'Me gusta ayudar a mejorar a otros', 'Likert', 3, true, '2026-03-27 22:15:17.544418', '2026-03-27 22:15:17.544418'),
	(39, 'S', 'Ofrezco ayuda sin que me la pidan', 'Likert', 3, true, '2026-03-27 22:15:17.544418', '2026-03-27 22:15:17.544418'),
	(40, 'S', 'Me gusta que mi trabajo ayude a otros', 'Likert', 3, true, '2026-03-27 22:15:17.544418', '2026-03-27 22:15:17.544418');
INSERT INTO public.preguntas (id_pregunta, rasgo, descripcion, tipo, nivel, estado, created_at, updated_at) VALUES
	(41, 'E', 'Propongo planes cuando el grupo está desorganizado', 'Likert', 3, true, '2026-03-27 22:16:41.769443', '2026-03-27 22:16:41.769443'),
	(42, 'E', 'Intento influir en decisiones del grupo', 'Likert', 3, true, '2026-03-27 22:16:41.769443', '2026-03-27 22:16:41.769443'),
	(43, 'E', 'Hablo con seguridad frente a varias personas', 'Likert', 3, true, '2026-03-27 22:16:41.769443', '2026-03-27 22:16:41.769443'),
	(44, 'E', 'Asumo responsabilidades que otros evitan', 'Likert', 3, true, '2026-03-27 22:16:41.769443', '2026-03-27 22:16:41.769443'),
	(45, 'E', 'Tomo decisiones con información incompleta', 'Likert', 3, true, '2026-03-27 22:16:41.769443', '2026-03-27 22:16:41.769443'),
	(46, 'E', 'Intento convencer a otros de mis ideas', 'Likert', 3, true, '2026-03-27 22:16:41.769443', '2026-03-27 22:16:41.769443'),
	(47, 'E', 'Me interesa iniciar proyectos nuevos', 'Likert', 3, true, '2026-03-27 22:16:41.769443', '2026-03-27 22:16:41.769443'),
	(48, 'C', 'Mantengo la información organizada', 'Likert', 3, true, '2026-03-27 22:17:54.298969', '2026-03-27 22:17:54.298969'),
	(49, 'C', 'Prefiero tareas con instrucciones claras', 'Likert', 3, true, '2026-03-27 22:17:54.298969', '2026-03-27 22:17:54.298969'),
	(50, 'C', 'Sigo procesos paso a paso', 'Likert', 3, true, '2026-03-27 22:17:54.298969', '2026-03-27 22:17:54.298969'),
	(51, 'C', 'Reviso detalles para evitar errores', 'Likert', 3, true, '2026-03-27 22:17:54.298969', '2026-03-27 22:17:54.298969'),
	(52, 'C', 'Prefiero estructura antes que improvisación', 'Likert', 3, true, '2026-03-27 22:17:54.298969', '2026-03-27 22:17:54.298969'),
	(53, 'C', 'Uso listas o registros para trabajar', 'Likert', 3, true, '2026-03-27 22:17:54.298969', '2026-03-27 22:17:54.298969'),
	(54, 'C', 'Me siento cómodo con reglas claras', 'Likert', 3, true, '2026-03-27 22:17:54.298969', '2026-03-27 22:17:54.298969'),
	(58, 'N', '¿Con qué tipo de herramientas prefieres trabajar?', 'Enunciado', 2, true, '2026-03-31 11:29:07.131775', '2026-04-06 15:44:21.937608'),
	(55, 'N', '¿Qué actividad te resulta más atractiva?', 'Enunciado', 2, true, '2026-03-31 11:29:07.131775', '2026-04-06 15:42:47.622077'),
	(57, 'N', '¿En qué ambiente te sentirías más cómodo?', 'Enunciado', 2, true, '2026-03-31 11:29:07.131775', '2026-04-06 15:44:07.52282'),
	(56, 'N', '¿Qué tipo de reto disfrutas más?', 'Enunciado', 2, true, '2026-03-31 11:29:07.131775', '2026-04-06 15:43:44.267826'),
	(59, 'N', '¿Qué te motiva más al realizar una actividad?', 'Enunciado', 2, true, '2026-03-31 11:29:07.131775', '2026-04-06 15:44:41.727706'),
	(60, 'N', '¿Qué resultado te genera más satisfacción?', 'Enunciado', 2, true, '2026-03-31 11:29:07.131775', '2026-04-06 15:45:04.622417');
INSERT INTO public.preguntas (id_pregunta, rasgo, descripcion, tipo, nivel, estado, created_at, updated_at) VALUES
	(72, 'I', 'Laboratorio o entorno de análisis', 'Choice', 2, true, '2026-03-31 13:22:49.344514', '2026-04-06 15:54:53.498081'),
	(73, 'I', 'Software de análisis o programación', 'Choice', 2, true, '2026-03-31 13:22:49.344514', '2026-04-06 15:54:53.498081'),
	(74, 'I', 'Descubrir o entender algo nuevo', 'Choice', 2, true, '2026-03-31 13:22:49.344514', '2026-04-06 15:54:53.498081'),
	(75, 'A', 'Diseñar o crear algo visual', 'Choice', 2, true, '2026-03-31 13:23:00.321305', '2026-04-06 15:57:34.458446'),
	(76, 'A', 'Expresar ideas de forma creativa', 'Choice', 2, true, '2026-03-31 13:23:00.321305', '2026-04-06 15:57:34.458446'),
	(65, 'R', 'Reparar o construir algo con tus manos', 'Choice', 2, true, '2026-03-31 13:22:35.12298', '2026-04-06 15:51:54.543'),
	(66, 'R', 'Armar o arreglar un objeto físico', 'Choice', 2, true, '2026-03-31 13:22:35.12298', '2026-04-06 15:51:54.543'),
	(67, 'R', 'Taller, obra o espacio físico', 'Choice', 2, true, '2026-03-31 13:22:35.12298', '2026-04-06 15:51:54.543'),
	(68, 'R', 'Herramientas o maquinaria', 'Choice', 2, true, '2026-03-31 13:22:35.12298', '2026-04-06 15:51:54.543'),
	(69, 'R', 'Construir o reparar algo útil', 'Choice', 2, true, '2026-03-31 13:22:35.12298', '2026-04-06 15:51:54.543'),
	(70, 'I', 'Investigar cómo funciona algo', 'Choice', 2, true, '2026-03-31 13:22:49.344514', '2026-04-06 15:54:53.498081'),
	(71, 'I', 'Resolver un problema complejo', 'Choice', 2, true, '2026-03-31 13:22:49.344514', '2026-04-06 15:54:53.498081'),
	(77, 'A', 'Estudio creativo', 'Choice', 2, true, '2026-03-31 13:23:00.321305', '2026-04-06 15:57:34.458446'),
	(78, 'A', 'Herramientas de diseño o arte', 'Choice', 2, true, '2026-03-31 13:23:00.321305', '2026-04-06 15:57:34.458446'),
	(79, 'A', 'Crear algo original', 'Choice', 2, true, '2026-03-31 13:23:00.321305', '2026-04-06 15:57:34.458446'),
	(80, 'S', 'Ayudar a alguien con un problema', 'Choice', 2, true, '2026-03-31 13:23:16.279607', '2026-04-06 16:00:26.194165'),
	(81, 'S', 'Resolver conflictos entre personas', 'Choice', 2, true, '2026-03-31 13:23:16.279607', '2026-04-06 16:00:26.194165'),
	(82, 'S', 'Espacio de interacción con personas', 'Choice', 2, true, '2026-03-31 13:23:16.279607', '2026-04-06 16:00:26.194165'),
	(83, 'S', 'Comunicación directa con personas', 'Choice', 2, true, '2026-03-31 13:23:16.279607', '2026-04-06 16:00:26.194165'),
	(84, 'S', 'Ayudar o impactar a otros', 'Choice', 2, true, '2026-03-31 13:23:16.279607', '2026-04-06 16:00:26.194165');
INSERT INTO public.preguntas (id_pregunta, rasgo, descripcion, tipo, nivel, estado, created_at, updated_at) VALUES
	(85, 'E', 'Liderar o proponer una idea', 'Choice', 2, true, '2026-03-31 13:23:27.059698', '2026-04-06 16:01:53.790703'),
	(86, 'E', 'Iniciar un proyecto o negocio', 'Choice', 2, true, '2026-03-31 13:23:27.059698', '2026-04-06 16:01:53.790703'),
	(87, 'E', 'Oficina de negocios o emprendimiento', 'Choice', 2, true, '2026-03-31 13:23:27.059698', '2026-04-06 16:01:53.790703'),
	(88, 'E', 'Estrategias y modelos de negocio', 'Choice', 2, true, '2026-03-31 13:23:27.059698', '2026-04-06 16:01:53.790703'),
	(89, 'E', 'Lograr éxito o reconocimiento', 'Choice', 2, true, '2026-03-31 13:23:27.059698', '2026-04-06 16:01:53.790703'),
	(90, 'C', 'Organizar información o datos', 'Choice', 2, true, '2026-03-31 13:23:37.361079', '2026-04-06 16:05:11.290809'),
	(91, 'C', 'Ordenar y optimizar procesos', 'Choice', 2, true, '2026-03-31 13:23:37.361079', '2026-04-06 16:05:11.290809'),
	(92, 'C', 'Oficina administrativa', 'Choice', 2, true, '2026-03-31 13:23:37.361079', '2026-04-06 16:05:11.290809'),
	(93, 'C', 'Sistemas de gestión y organización', 'Choice', 2, true, '2026-03-31 13:23:37.361079', '2026-04-06 16:05:11.290809'),
	(94, 'C', 'Mantener orden y control', 'Choice', 2, true, '2026-03-31 13:23:37.361079', '2026-04-06 16:05:11.290809'),
	(95, 'R', 'Ver algo funcionando correctamente', 'Choice', 2, true, '2026-04-06 16:11:08.042326', '2026-04-06 16:11:08.042326'),
	(97, 'A', 'Terminar una creación propia', 'Choice', 2, true, '2026-04-06 16:11:08.042326', '2026-04-06 16:11:08.042326'),
	(98, 'S', 'Mejorar la vida de alguien', 'Choice', 2, true, '2026-04-06 16:11:08.042326', '2026-04-06 16:11:08.042326'),
	(99, 'E', 'Alcanzar metas o liderar logros', 'Choice', 2, true, '2026-04-06 16:11:08.042326', '2026-04-06 16:11:08.042326'),
	(100, 'C', 'Tener todo organizado y claro', 'Choice', 2, true, '2026-04-06 16:11:08.042326', '2026-04-06 16:11:08.042326'),
	(96, 'I', 'Encontrar la solución a un problema', 'Choice', 2, true, '2026-04-06 16:11:08.042326', '2026-04-06 16:42:17.628905');


--
-- TOC entry 5161 (class 0 OID 16761)
-- Dependencies: 239
-- Data for Name: preguntas_multiples; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.preguntas_multiples (id_enunciado, id_pregunta, created_at, updated_at, estado, grupo) VALUES
	(55, 65, '2026-04-06 16:19:52.834776', '2026-04-06 16:19:52.834776', true, 'A'),
	(55, 70, '2026-04-06 16:19:52.834776', '2026-04-06 16:19:52.834776', true, 'A'),
	(55, 75, '2026-04-06 16:19:52.834776', '2026-04-06 16:19:52.834776', true, 'A'),
	(55, 80, '2026-04-06 16:19:52.834776', '2026-04-06 16:19:52.834776', true, 'A'),
	(55, 85, '2026-04-06 16:19:52.834776', '2026-04-06 16:19:52.834776', true, 'A'),
	(55, 90, '2026-04-06 16:19:52.834776', '2026-04-06 16:19:52.834776', true, 'A'),
	(56, 66, '2026-04-06 16:23:11.285894', '2026-04-06 16:23:11.285894', true, 'A'),
	(56, 71, '2026-04-06 16:23:11.285894', '2026-04-06 16:23:11.285894', true, 'A'),
	(56, 76, '2026-04-06 16:23:11.285894', '2026-04-06 16:23:11.285894', true, 'A'),
	(56, 81, '2026-04-06 16:23:11.285894', '2026-04-06 16:23:11.285894', true, 'A'),
	(56, 86, '2026-04-06 16:23:11.285894', '2026-04-06 16:23:11.285894', true, 'A'),
	(56, 91, '2026-04-06 16:23:11.285894', '2026-04-06 16:23:11.285894', true, 'A'),
	(57, 67, '2026-04-06 16:29:49.784276', '2026-04-06 16:29:49.784276', true, 'A'),
	(57, 72, '2026-04-06 16:29:49.784276', '2026-04-06 16:29:49.784276', true, 'A'),
	(57, 77, '2026-04-06 16:29:49.784276', '2026-04-06 16:29:49.784276', true, 'A'),
	(57, 82, '2026-04-06 16:29:49.784276', '2026-04-06 16:29:49.784276', true, 'A'),
	(57, 87, '2026-04-06 16:29:49.784276', '2026-04-06 16:29:49.784276', true, 'A'),
	(57, 92, '2026-04-06 16:29:49.784276', '2026-04-06 16:29:49.784276', true, 'A'),
	(58, 68, '2026-04-06 16:32:13.578244', '2026-04-06 16:32:13.578244', true, 'A'),
	(58, 73, '2026-04-06 16:32:13.578244', '2026-04-06 16:32:13.578244', true, 'A');
INSERT INTO public.preguntas_multiples (id_enunciado, id_pregunta, created_at, updated_at, estado, grupo) VALUES
	(58, 78, '2026-04-06 16:32:13.578244', '2026-04-06 16:32:13.578244', true, 'A'),
	(58, 83, '2026-04-06 16:32:13.578244', '2026-04-06 16:32:13.578244', true, 'A'),
	(58, 88, '2026-04-06 16:32:13.578244', '2026-04-06 16:32:13.578244', true, 'A'),
	(58, 93, '2026-04-06 16:32:13.578244', '2026-04-06 16:32:13.578244', true, 'A'),
	(59, 69, '2026-04-06 16:34:13.315288', '2026-04-06 16:37:19.862157', true, 'A'),
	(59, 74, '2026-04-06 16:34:13.315288', '2026-04-06 16:37:19.862157', true, 'A'),
	(59, 79, '2026-04-06 16:34:13.315288', '2026-04-06 16:37:19.862157', true, 'A'),
	(59, 84, '2026-04-06 16:34:13.315288', '2026-04-06 16:37:19.862157', true, 'A'),
	(59, 89, '2026-04-06 16:34:13.315288', '2026-04-06 16:37:19.862157', true, 'A'),
	(59, 94, '2026-04-06 16:34:13.315288', '2026-04-06 16:37:19.862157', true, 'A'),
	(60, 95, '2026-04-06 16:42:24.123675', '2026-04-06 16:42:24.123675', true, 'A'),
	(60, 96, '2026-04-06 16:42:24.123675', '2026-04-06 16:42:24.123675', true, 'A'),
	(60, 97, '2026-04-06 16:42:24.123675', '2026-04-06 16:42:24.123675', true, 'A'),
	(60, 98, '2026-04-06 16:42:24.123675', '2026-04-06 16:42:24.123675', true, 'A'),
	(60, 99, '2026-04-06 16:42:24.123675', '2026-04-06 16:42:24.123675', true, 'A'),
	(60, 100, '2026-04-06 16:42:24.123675', '2026-04-06 16:42:24.123675', true, 'A');


--
-- TOC entry 5154 (class 0 OID 16616)
-- Dependencies: 232
-- Data for Name: respuestas_cuestionario; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.respuestas_cuestionario (id_respuesta, id_usuario, created_at, updated_at, respuestas, estado) VALUES
	(1, 2, '2026-04-10 21:14:02.57629', '2026-04-10 21:14:02.57629', '{"estado": true, "id_usuario": 2, "respuestas": {"nivel1": {"A5": 2, "A6": 3, "E9": 4, "I3": 3, "I4": 3, "R1": 4, "R2": 4, "S7": 3, "S8": 2, "C11": 2, "C12": 3, "E10": 2}, "nivel2": {"A55": 5, "C55": 5, "E55": 5, "I55": 5, "I58": 5, "I59": 5, "R55": 5, "R56": 5, "R57": 5, "R60": 5, "S55": 5}, "nivel3": {"R13": 4, "R14": 5, "R15": 4, "R16": 5, "R17": 5, "R18": 3, "R19": 4}}}', true);


--
-- TOC entry 5155 (class 0 OID 16623)
-- Dependencies: 233
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5156 (class 0 OID 16632)
-- Dependencies: 234
-- Data for Name: universidades; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5157 (class 0 OID 16643)
-- Dependencies: 235
-- Data for Name: usuario_carreras; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5158 (class 0 OID 16649)
-- Dependencies: 236
-- Data for Name: usuario_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5159 (class 0 OID 16655)
-- Dependencies: 237
-- Data for Name: usuario_subsidios; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5160 (class 0 OID 16661)
-- Dependencies: 238
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.usuarios (id_usuario, nombre, email, password_hash, tipo_documento, numero_documento, estado, created_at, updated_at) VALUES
	(2, 'Jhon Bernal', 'prueba@mail.com', '$2b$12$2fFSkgcckB.LtfhWaeyeCuB7fNrGctLTlGODRSuPmuhrUuD9dOsOO', 'CC', '123098456', true, '2026-04-01 16:30:01.642684', '2026-04-01 16:30:01.642684');


--
-- TOC entry 5169 (class 0 OID 0)
-- Dependencies: 219
-- Name: id_carrera_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_carrera_seq', 1, false);


--
-- TOC entry 5170 (class 0 OID 0)
-- Dependencies: 224
-- Name: id_pregunta_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_pregunta_seq', 100, true);


--
-- TOC entry 5171 (class 0 OID 0)
-- Dependencies: 225
-- Name: id_respuesta_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_respuesta_seq', 1, true);


--
-- TOC entry 5172 (class 0 OID 0)
-- Dependencies: 226
-- Name: id_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_rol_seq', 1, false);


--
-- TOC entry 5173 (class 0 OID 0)
-- Dependencies: 221
-- Name: id_subsidio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_subsidio_seq', 1, false);


--
-- TOC entry 5174 (class 0 OID 0)
-- Dependencies: 227
-- Name: id_universidad_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_universidad_seq', 1, false);


--
-- TOC entry 5175 (class 0 OID 0)
-- Dependencies: 228
-- Name: id_usuario_carrera_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_usuario_carrera_seq', 1, false);


--
-- TOC entry 5176 (class 0 OID 0)
-- Dependencies: 229
-- Name: id_usuario_rol_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_usuario_rol_seq', 1, false);


--
-- TOC entry 5177 (class 0 OID 0)
-- Dependencies: 230
-- Name: id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_usuario_seq', 2, true);


--
-- TOC entry 5178 (class 0 OID 0)
-- Dependencies: 231
-- Name: id_usuario_subsidio_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_usuario_subsidio_seq', 1, false);


--
-- TOC entry 4948 (class 2606 OID 16678)
-- Name: carreras carreras_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carreras
    ADD CONSTRAINT carreras_pkey PRIMARY KEY (id_carrera);


--
-- TOC entry 4950 (class 2606 OID 16680)
-- Name: convenios_subsidios convenios_subsidios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.convenios_subsidios
    ADD CONSTRAINT convenios_subsidios_pkey PRIMARY KEY (id_subsidio);


--
-- TOC entry 4952 (class 2606 OID 16682)
-- Name: preguntas preguntas_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.preguntas
    ADD CONSTRAINT preguntas_pkey PRIMARY KEY (id_pregunta);


--
-- TOC entry 4954 (class 2606 OID 16684)
-- Name: respuestas_cuestionario respuestas_cuestionario_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.respuestas_cuestionario
    ADD CONSTRAINT respuestas_cuestionario_pkey PRIMARY KEY (id_respuesta);


--
-- TOC entry 4956 (class 2606 OID 16686)
-- Name: roles roles_nombre_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);


--
-- TOC entry 4958 (class 2606 OID 16688)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id_rol);


--
-- TOC entry 4970 (class 2606 OID 16690)
-- Name: usuarios unique_documento; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT unique_documento UNIQUE (tipo_documento, numero_documento);


--
-- TOC entry 4960 (class 2606 OID 16692)
-- Name: universidades universidades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.universidades
    ADD CONSTRAINT universidades_pkey PRIMARY KEY (id_universidad);


--
-- TOC entry 4962 (class 2606 OID 16694)
-- Name: usuario_carreras usuario_carreras_id_usuario_id_carrera_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_carreras
    ADD CONSTRAINT usuario_carreras_id_usuario_id_carrera_key UNIQUE (id_usuario, id_carrera);


--
-- TOC entry 4964 (class 2606 OID 16696)
-- Name: usuario_carreras usuario_carreras_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_carreras
    ADD CONSTRAINT usuario_carreras_pkey PRIMARY KEY (id_usuario_carrera);


--
-- TOC entry 4966 (class 2606 OID 16698)
-- Name: usuario_roles usuario_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_roles
    ADD CONSTRAINT usuario_roles_pkey PRIMARY KEY (id_usuario_rol);


--
-- TOC entry 4968 (class 2606 OID 16700)
-- Name: usuario_subsidios usuario_subsidios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_subsidios
    ADD CONSTRAINT usuario_subsidios_pkey PRIMARY KEY (id_usuario_subsidio);


--
-- TOC entry 4972 (class 2606 OID 16702)
-- Name: usuarios usuarios_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_email_key UNIQUE (email);


--
-- TOC entry 4974 (class 2606 OID 16704)
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id_usuario);


--
-- TOC entry 4983 (class 2620 OID 16787)
-- Name: carreras tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.carreras FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4984 (class 2620 OID 16788)
-- Name: convenios_subsidios tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.convenios_subsidios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4985 (class 2620 OID 16789)
-- Name: preguntas tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.preguntas FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4993 (class 2620 OID 16797)
-- Name: preguntas_multiples tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.preguntas_multiples FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4986 (class 2620 OID 16790)
-- Name: respuestas_cuestionario tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.respuestas_cuestionario FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4987 (class 2620 OID 16791)
-- Name: roles tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.roles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4988 (class 2620 OID 16792)
-- Name: universidades tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.universidades FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4989 (class 2620 OID 16793)
-- Name: usuario_carreras tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.usuario_carreras FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4990 (class 2620 OID 16794)
-- Name: usuario_roles tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.usuario_roles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4991 (class 2620 OID 16795)
-- Name: usuario_subsidios tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.usuario_subsidios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4992 (class 2620 OID 16796)
-- Name: usuarios tr_update_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER tr_update_updated_at BEFORE UPDATE ON public.usuarios FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 4975 (class 2606 OID 16710)
-- Name: carreras carreras_id_universidad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.carreras
    ADD CONSTRAINT carreras_id_universidad_fkey FOREIGN KEY (id_universidad) REFERENCES public.universidades(id_universidad) ON DELETE CASCADE;


--
-- TOC entry 4976 (class 2606 OID 16720)
-- Name: respuestas_cuestionario respuestas_cuestionario_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.respuestas_cuestionario
    ADD CONSTRAINT respuestas_cuestionario_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- TOC entry 4977 (class 2606 OID 16725)
-- Name: usuario_carreras usuario_carreras_id_carrera_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_carreras
    ADD CONSTRAINT usuario_carreras_id_carrera_fkey FOREIGN KEY (id_carrera) REFERENCES public.carreras(id_carrera) ON DELETE CASCADE;


--
-- TOC entry 4978 (class 2606 OID 16730)
-- Name: usuario_carreras usuario_carreras_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_carreras
    ADD CONSTRAINT usuario_carreras_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- TOC entry 4979 (class 2606 OID 16735)
-- Name: usuario_roles usuario_roles_id_rol_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_roles
    ADD CONSTRAINT usuario_roles_id_rol_fkey FOREIGN KEY (id_rol) REFERENCES public.roles(id_rol) ON DELETE CASCADE;


--
-- TOC entry 4980 (class 2606 OID 16740)
-- Name: usuario_roles usuario_roles_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_roles
    ADD CONSTRAINT usuario_roles_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


--
-- TOC entry 4981 (class 2606 OID 16745)
-- Name: usuario_subsidios usuario_subsidios_id_subsidio_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_subsidios
    ADD CONSTRAINT usuario_subsidios_id_subsidio_fkey FOREIGN KEY (id_subsidio) REFERENCES public.convenios_subsidios(id_subsidio) ON DELETE CASCADE;


--
-- TOC entry 4982 (class 2606 OID 16750)
-- Name: usuario_subsidios usuario_subsidios_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.usuario_subsidios
    ADD CONSTRAINT usuario_subsidios_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuarios(id_usuario) ON DELETE CASCADE;


-- Completed on 2026-04-10 22:16:05

--
-- PostgreSQL database dump complete
--

\unrestrict X7unU6nB29V2W07xDkbLfTkLN5wFwAMIwJB8XTF6bn2BpTEu3PgvhlVCocsrjeI

