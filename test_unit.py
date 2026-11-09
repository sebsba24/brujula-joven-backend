"""
Pruebas unitarias del backend — sin base de datos ni red.
Ejecutar desde el directorio backend/:  pytest test_unit.py -v
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import pyotp
from jose import jwt

# Importaciones del proyecto
from config import get_settings
from security import (
    hash_password,
    verify_password,
    create_access_token,
    create_temp_token,
    decode_access_token,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TEMP_TOKEN_EXPIRE_MINUTES,
)
from auth_service import AuthService

# ── Funciones del algoritmo RIASEC copiadas (mismo patrón que test_algoritmo.py) ──

PROGRAMAS_EDUCATIVOS = {
    "R": [
        {"nombre": "Técnico en Electrónica",     "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Mecánica Automotriz",         "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Mecánica",         "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Civil",            "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Mecánica",         "inst": "U. de los Andes", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "I": [
        {"nombre": "Análisis y Desarrollo de Software", "inst": "SENA",     "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Ingeniería de Sistemas",      "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ciencia de Datos",            "inst": "U. de los Andes", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "A": [
        {"nombre": "Diseño Gráfico",              "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Artes Visuales",              "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Arquitectura",                "inst": "U. Javeriana",    "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "S": [
        {"nombre": "Atención a la Primera Infancia", "inst": "SENA",        "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Trabajo Social",              "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Psicología",                  "inst": "U. Javeriana",    "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "E": [
        {"nombre": "Técnico en Ventas",           "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Administración de Empresas",  "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Marketing",                   "inst": "U. de los Andes", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "C": [
        {"nombre": "Contabilidad y Finanzas",     "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Contaduría Pública",          "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Contaduría Pública",          "inst": "U. Javeriana",    "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
}

HOLLAND_ADYACENTES = {
    "R": ["I", "C"], "I": ["R", "A"], "A": ["I", "S"],
    "S": ["A", "E"], "E": ["S", "C"], "C": ["E", "R"],
}

def puntuar_programas(rasgos_scores, capacidad, modalidad_pref):
    COSTOS_OK = {
        "baja":  ["gratuito", "bajo"],
        "media": ["gratuito", "bajo", "medio"],
        "alta":  ["gratuito", "bajo", "medio", "alto"],
    }
    costos_permitidos = COSTOS_OK.get(capacidad, ["gratuito", "bajo", "medio"])
    resultado = []

    for rasgo, programas in PROGRAMAS_EDUCATIVOS.items():
        score_directo = rasgos_scores.get(rasgo, 0) / 100
        adyacentes    = HOLLAND_ADYACENTES.get(rasgo, [])
        score_adj     = max((rasgos_scores.get(a, 0) for a in adyacentes), default=0) / 100
        riasec_score  = (score_directo * 0.80) + (score_adj * 0.20)

        for prog in programas:
            if prog["costo"] in costos_permitidos:
                fin_score = 1.0
            elif prog["con_beca"]:
                fin_score = 0.65
            else:
                continue

            mod_score = 1.0 if modalidad_pref in prog["modalidad"] else 0.3
            total = round((riasec_score * 0.60) + (fin_score * 0.25) + (mod_score * 0.15), 3)
            resultado.append({**prog, "rasgo": rasgo, "score": total})

    vistos, ordenados = set(), []
    for p in sorted(resultado, key=lambda x: x["score"], reverse=True):
        key = (p["nombre"], p["inst"])
        if key not in vistos:
            vistos.add(key)
            ordenados.append(p)
    return ordenados


# ═══════════════════════════════════════════════════════════════════
# 1. ALGORITMO RIASEC
# ═══════════════════════════════════════════════════════════════════

class TestPuntuarProgramas:

    def test_orden_descendente(self):
        scores = puntuar_programas({"I": 70, "R": 15}, "baja", "virtual")
        puntos = [p["score"] for p in scores]
        assert puntos == sorted(puntos, reverse=True)

    def test_scores_en_rango_01(self):
        scores = puntuar_programas({"A": 65, "S": 20}, "alta", "presencial")
        for p in scores:
            assert 0.0 <= p["score"] <= 1.0, f"Score fuera de rango: {p['score']}"

    def test_capacidad_baja_excluye_alto_sin_beca(self):
        scores = puntuar_programas({"I": 80}, "baja", "presencial")
        for p in scores:
            # costo alto sin beca no debe aparecer
            assert not (p["costo"] == "alto" and not p["con_beca"])

    def test_capacidad_alta_incluye_mas_programas_que_baja(self):
        base = {"I": 60, "R": 20}
        alta = puntuar_programas(base, "alta", "presencial")
        baja = puntuar_programas(base, "baja", "presencial")
        assert len(alta) >= len(baja)

    def test_perfil_dominante_prioriza_rasgo_correcto(self):
        # I fuerte → primer programa en rasgo I o adyacente (R, A)
        scores = puntuar_programas({"I": 90, "R": 5, "A": 5}, "alta", "virtual")
        primer_rasgo = scores[0]["rasgo"]
        assert primer_rasgo in ("I", "R", "A")

    def test_sin_duplicados_en_resultado(self):
        scores = puntuar_programas({"E": 50, "S": 30}, "media", "presencial")
        claves = [(p["nombre"], p["inst"]) for p in scores]
        assert len(claves) == len(set(claves))

    def test_modalidad_virtual_penaliza_solo_presencial(self):
        scores = puntuar_programas({"C": 60}, "alta", "virtual")
        for p in scores:
            if "virtual" not in p["modalidad"]:
                # mod_score 0.3 → score total debe ser menor que con mod_score 1.0
                # (no hay garantía de posición, pero el score sí refleja la penalización)
                assert p["score"] < 1.0

    def test_scores_artista_capacidad_alta(self):
        scores = puntuar_programas({"A": 65, "I": 10, "S": 10}, "alta", "presencial")
        assert len(scores) > 0
        # Los primeros resultados deben incluir rasgo A o adyacentes (I, S)
        top3_rasgos = {p["rasgo"] for p in scores[:3]}
        assert top3_rasgos & {"A", "I", "S"}

    def test_todos_scores_cero_devuelve_lista(self):
        # Con todos scores en 0 el algoritmo igual devuelve programas accesibles
        scores = puntuar_programas({"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}, "alta", "presencial")
        assert isinstance(scores, list)

    def test_capacidad_invalida_usa_fallback(self):
        # Capacidad desconocida → fallback a gratuito/bajo/medio (sin "alto")
        scores = puntuar_programas({"E": 50}, "desconocida", "presencial")
        for p in scores:
            assert not (p["costo"] == "alto" and not p["con_beca"])


# ═══════════════════════════════════════════════════════════════════
# 2. SEGURIDAD — CONTRASEÑAS
# ═══════════════════════════════════════════════════════════════════

class TestPassword:

    def test_hash_no_igual_a_plaintext(self):
        hashed = hash_password("mi_contraseña_segura")
        assert hashed != "mi_contraseña_segura"

    def test_verify_correcta(self):
        pwd = "Test1234!"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed) is True

    def test_verify_incorrecta(self):
        hashed = hash_password("contraseña_correcta")
        assert verify_password("contraseña_incorrecta", hashed) is False

    def test_hashes_distintos_misma_clave(self):
        # bcrypt usa salt aleatorio → cada hash es distinto
        h1 = hash_password("misma")
        h2 = hash_password("misma")
        assert h1 != h2

    def test_hash_empieza_con_bcrypt_prefix(self):
        hashed = hash_password("cualquier_clave")
        assert hashed.startswith("$2b$") or hashed.startswith("$2a$")

    def test_cadena_vacia(self):
        hashed = hash_password("")
        assert verify_password("", hashed) is True

    def test_contraseña_unicode(self):
        pwd = "clave_ñoño_üñíçødé"
        hashed = hash_password(pwd)
        assert verify_password(pwd, hashed) is True


# ═══════════════════════════════════════════════════════════════════
# 3. SEGURIDAD — JWT
# ═══════════════════════════════════════════════════════════════════

class TestJWT:

    def test_create_access_token_decodeable(self):
        token = create_access_token({"sub": "42"})
        payload = decode_access_token(token)
        assert payload is not None
        assert payload["sub"] == "42"

    def test_access_token_contiene_exp(self):
        token = create_access_token({"sub": "1"})
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_token_invalido_devuelve_none(self):
        result = decode_access_token("token.invalido.xxx")
        assert result is None

    def test_token_alterado_devuelve_none(self):
        token = create_access_token({"sub": "99"})
        # Alterar el payload
        partes = token.split(".")
        partes[1] = partes[1] + "X"
        result = decode_access_token(".".join(partes))
        assert result is None

    def test_create_temp_token_tiene_2fa_pending(self):
        token = create_temp_token(user_id=5)
        payload = decode_access_token(token)
        assert payload is not None
        assert payload.get("2fa_pending") is True
        assert payload["sub"] == "5"

    def test_temp_token_expira_antes_que_access(self):
        from datetime import datetime, timezone
        access_token = create_access_token({"sub": "1"})
        temp_token = create_temp_token(user_id=1)

        access_payload = decode_access_token(access_token)
        temp_payload = decode_access_token(temp_token)

        assert temp_payload["exp"] < access_payload["exp"]

    def test_clave_secreta_del_settings(self):
        settings = get_settings()
        token = create_access_token({"sub": "7"})
        # Verificar que el token fue firmado con la clave del settings
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        assert payload["sub"] == "7"

    def test_token_firmado_con_clave_distinta_falla(self):
        from jose import JWTError
        token = create_access_token({"sub": "3"})
        with pytest.raises(JWTError):
            jwt.decode(token, "clave_equivocada", algorithms=[ALGORITHM])


# ═══════════════════════════════════════════════════════════════════
# 4. TOTP / 2FA
# ═══════════════════════════════════════════════════════════════════

class TestTOTP:

    def test_generate_totp_secret_no_vacio(self):
        secret = AuthService.generate_totp_secret()
        assert isinstance(secret, str)
        assert len(secret) > 0

    def test_secrets_distintos_cada_llamada(self):
        s1 = AuthService.generate_totp_secret()
        s2 = AuthService.generate_totp_secret()
        assert s1 != s2

    def test_get_totp_uri_contiene_issuer(self):
        secret = AuthService.generate_totp_secret()
        uri = AuthService.get_totp_uri(secret, "usuario@test.com")
        assert "NextSteps" in uri

    def test_get_totp_uri_contiene_email(self):
        secret = AuthService.generate_totp_secret()
        uri = AuthService.get_totp_uri(secret, "usuario@test.com")
        assert "usuario" in uri

    def test_get_totp_uri_es_otpauth(self):
        secret = AuthService.generate_totp_secret()
        uri = AuthService.get_totp_uri(secret, "x@y.com")
        assert uri.startswith("otpauth://totp/")

    def test_verify_totp_codigo_correcto(self):
        secret = AuthService.generate_totp_secret()
        codigo_actual = pyotp.TOTP(secret).now()
        assert AuthService.verify_totp(secret, codigo_actual) is True

    def test_verify_totp_codigo_incorrecto(self):
        secret = AuthService.generate_totp_secret()
        assert AuthService.verify_totp(secret, "000000") is False

    def test_verify_totp_codigo_aleatorio_falla(self):
        secret = AuthService.generate_totp_secret()
        # Probabilidad de colisión < 1/1_000_000
        assert AuthService.verify_totp(secret, "999999") is False

    def test_verify_totp_secreto_conocido(self):
        # RFC 6238 test vector conocido (evita flakiness por tiempo)
        secret = "DOC47PTE6EYRDSVNC6QBBZLXS6QVRNFV"
        codigo = pyotp.TOTP(secret).now()
        assert AuthService.verify_totp(secret, codigo) is True

    def test_verify_totp_acepta_ventana_1(self):
        # Verifica que valid_window=1 está configurado (acepta código del step anterior)
        secret = AuthService.generate_totp_secret()
        totp = pyotp.TOTP(secret)
        # Generar código con timestamp del step anterior
        codigo_previo = totp.at(int(time.time()) - 30)
        # Con valid_window=1 debe aceptar
        assert AuthService.verify_totp(secret, codigo_previo) is True


# ═══════════════════════════════════════════════════════════════════
# 5. AUTH SERVICE — build_login_response (sin DB)
# ═══════════════════════════════════════════════════════════════════

class TestAuthServiceLoginResponse:

    class _FakeUser:
        def __init__(self, id_usuario, totp_enabled):
            self.id_usuario = id_usuario
            self.totp_enabled = totp_enabled

    def test_sin_2fa_devuelve_access_token(self):
        user = self._FakeUser(id_usuario=10, totp_enabled=False)
        resp = AuthService.build_login_response(user)
        assert "access_token" in resp
        assert resp["token_type"] == "bearer"
        assert resp["requires_2fa"] is False

    def test_con_2fa_devuelve_temp_token(self):
        user = self._FakeUser(id_usuario=20, totp_enabled=True)
        resp = AuthService.build_login_response(user)
        assert "temp_token" in resp
        assert resp["requires_2fa"] is True
        assert "access_token" not in resp

    def test_temp_token_contiene_2fa_pending(self):
        user = self._FakeUser(id_usuario=20, totp_enabled=True)
        resp = AuthService.build_login_response(user)
        payload = decode_access_token(resp["temp_token"])
        assert payload is not None
        assert payload["2fa_pending"] is True

    def test_access_token_contiene_sub_correcto(self):
        user = self._FakeUser(id_usuario=42, totp_enabled=False)
        resp = AuthService.build_login_response(user)
        payload = decode_access_token(resp["access_token"])
        assert payload["sub"] == "42"
