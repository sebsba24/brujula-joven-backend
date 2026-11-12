"""
Pruebas unitarias mapeadas a los Requerimientos Funcionales (RF-01 … RF-05).
Cubren la lógica de negocio verificable sin base de datos ni red.
Ejecutar desde backend/:  pytest test_rf.py -v

Los RF que dependen de la UI (localStorage, routing) o de la BD/endpoints
(persistencia, carga de preguntas) se documentan al final del archivo y en el
reporte, ya que no son unidades puras del backend.
"""
import sys, os, time
sys.path.insert(0, os.path.dirname(__file__))

import pytest
import pyotp
from pydantic import ValidationError

from schemas import UsuarioCreate, PerfilFinancieroCreate
from security import (
    hash_password, verify_password,
    create_access_token, create_temp_token, decode_access_token,
    ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES,
)
from auth_service import AuthService
from profiles import (
    calcular_perfil, calcular_chaside, generar_recomendaciones,
    calcular_capacidad_financiera, puntuar_programas,
    BECAS_POR_CAPACIDAD, RASGOS_NOMBRES, SCORING_RASGOS,
)


# ════════════════════════════════════════════════════════════════════
# RF-01 — Autenticación y Gestión de Usuarios
# ════════════════════════════════════════════════════════════════════

class TestRF01_Autenticacion:

    # RF-01.1 — Registro con nombre, correo, tipo/número de documento y
    # contraseña (mínimo 8 caracteres).
    def test_rf0101_registro_campos_validos(self):
        u = UsuarioCreate(
            nombre="Ana Gómez", email="ana@mail.com",
            tipo_documento="CC", numero_documento="123456789",
            password="ClaveSegura1",
        )
        assert u.email == "ana@mail.com"
        assert u.tipo_documento == "CC"

    def test_rf0101_password_minimo_8_rechaza_corta(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nombre="Ana", email="ana@mail.com",
                tipo_documento="CC", numero_documento="123",
                password="1234567",  # 7 caracteres → debe fallar
            )

    def test_rf0101_password_8_exacto_valido(self):
        u = UsuarioCreate(
            nombre="Ana", email="ana@mail.com",
            tipo_documento="CC", numero_documento="123",
            password="12345678",  # 8 caracteres → válido
        )
        assert len(u.password) == 8

    def test_rf0101_email_invalido_rechazado(self):
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nombre="Ana", email="no-es-correo",
                tipo_documento="CC", numero_documento="123",
                password="ClaveSegura1",
            )

    def test_rf0101_password_se_hashea_no_plano(self):
        hashed = hash_password("ClaveSegura1")
        assert hashed != "ClaveSegura1"
        assert verify_password("ClaveSegura1", hashed)

    # RF-01.2 — Autenticación con correo/contraseña emitiendo JWT con expiración.
    def test_rf0102_jwt_emitido_y_decodificable(self):
        token = create_access_token({"sub": "42"})
        payload = decode_access_token(token)
        assert payload["sub"] == "42"

    def test_rf0102_jwt_contiene_expiracion(self):
        token = create_access_token({"sub": "1"})
        payload = decode_access_token(token)
        assert "exp" in payload

    def test_rf0102_jwt_invalido_rechazado(self):
        assert decode_access_token("token.falso.xxx") is None

    def test_rf0102_build_login_response_sin_2fa(self):
        class U: id_usuario = 7; totp_enabled = False
        resp = AuthService.build_login_response(U())
        assert resp["access_token"] and resp["token_type"] == "bearer"
        assert resp["requires_2fa"] is False

    def test_rf0102_2fa_flujo_temp_token(self):
        class U: id_usuario = 9; totp_enabled = True
        resp = AuthService.build_login_response(U())
        assert resp["requires_2fa"] is True
        payload = decode_access_token(resp["temp_token"])
        assert payload["2fa_pending"] is True

    def test_rf0102_totp_verifica_codigo_correcto(self):
        secret = AuthService.generate_totp_secret()
        assert AuthService.verify_totp(secret, pyotp.TOTP(secret).now()) is True

    # Nota: RF-01.3 (localStorage), RF-01.4 (logout limpia token) y
    # RF-01.5 (rutas protegidas redirigen) son lógica de FRONTEND
    # (AuthContext, ProtectedRoute). Se verificaron manualmente en navegador.


# ════════════════════════════════════════════════════════════════════
# RF-02 — Cuestionario Vocacional (RIASEC)
# ════════════════════════════════════════════════════════════════════

class TestRF02_Vocacional:

    # RF-02.1 — Cuestionario de tres niveles (interés, elección forzada, autoeficacia).
    def test_rf0201_procesa_tres_niveles(self):
        resp = {"respuestas": {
            "nivel1": {"R_1": 5, "I_1": 3},
            "nivel2": {"R_a": 1, "I_b": 1},
            "nivel3": {"R_1": 4, "I_1": 2},
        }}
        perfil = calcular_perfil(resp)
        assert "perfil" in perfil and "interes" in perfil and "autoeficacia" in perfil

    # RF-02.3 — Fórmula: puntaje = interés × 0.60 + autoeficacia × 0.40.
    def test_rf0203_ponderacion_60_40(self):
        # Interés 100% R, autoeficacia 100% I → R debe dominar (0.60 > 0.40)
        resp = {"respuestas": {
            "nivel1": {"R_1": 5, "R_2": 5, "R_3": 5},
            "nivel3": {"I_1": 5, "I_2": 5, "I_3": 5},
        }}
        perfil = calcular_perfil(resp)["perfil"]
        assert perfil["R"] > perfil["I"]          # interés pesa más
        assert perfil["R"] > 0 and perfil["I"] > 0  # ambos contribuyen

    def test_rf0203_sin_autoeficacia_usa_interes(self):
        # Sin nivel3 → el perfil equivale al interés (retrocompatibilidad)
        resp = {"respuestas": {"nivel1": {"A_1": 5, "A_2": 5}}}
        perfil = calcular_perfil(resp)
        assert perfil["dominante"] == "A"

    # RF-02.4 — Identificar rasgo dominante y top 3.
    def test_rf0204_dominante_y_top3(self):
        resp = {"respuestas": {"nivel1": {"S_1": 5, "E_1": 4, "A_1": 3, "R_1": 1}}}
        out = calcular_perfil(resp)
        assert out["dominante"] == out["top3"][0]
        assert len(out["top3"]) == 3
        assert out["dominante"] == "S"

    def test_rf0204_top3_orden_descendente(self):
        resp = {"respuestas": {"nivel1": {"I_1": 5, "R_1": 4, "C_1": 3}}}
        perfil = calcular_perfil(resp)
        top3 = perfil["top3"]
        vals = [perfil["perfil"][r] for r in top3]
        assert vals == sorted(vals, reverse=True)

    # RF-02.5 — Mapear el perfil Holland (RIASEC) a códigos del contexto (CHASIDE).
    def test_rf0205_mapeo_chaside(self):
        perfil_riasec = {"R": 10, "I": 60, "A": 5, "S": 5, "E": 10, "C": 10}
        chaside = calcular_chaside(perfil_riasec)
        assert "scores" in chaside and "dominante" in chaside
        # Perfil Investigativo fuerte → CHASIDE Ciencias (C) o Ingeniería (I)
        assert chaside["dominante"] in ("C", "I")

    # RF-02.7 — Ver perfil completo con descripción de cada rasgo y porcentaje.
    def test_rf0207_porcentajes_suman_100(self):
        resp = {"respuestas": {"nivel1": {"R_1": 3, "I_1": 3, "A_1": 3, "S_1": 3, "E_1": 3, "C_1": 3}}}
        perfil = calcular_perfil(resp)["perfil"]
        assert abs(sum(perfil.values()) - 100) < 0.5  # tolerancia por redondeo

    def test_rf0207_nombres_de_rasgos_disponibles(self):
        # Cada rasgo RIASEC tiene nombre descriptivo para mostrar al usuario
        for r in SCORING_RASGOS:
            assert RASGOS_NOMBRES[r]

    def test_rf0207_recomendaciones_principal_y_secundarias(self):
        perfil = calcular_perfil({"respuestas": {"nivel1": {"I_1": 5, "R_1": 3}}})
        rec = generar_recomendaciones(perfil)
        assert rec["principal"] and isinstance(rec["secundarias"], list)


# ════════════════════════════════════════════════════════════════════
# RF-04 — Módulo Financiero
# ════════════════════════════════════════════════════════════════════

class TestRF04_Financiero:

    # RF-04.1 — Validación del perfil financiero (estrato 1–6).
    def test_rf0401_estrato_valido(self):
        p = PerfilFinancieroCreate(estrato=3)
        assert p.estrato == 3

    def test_rf0401_estrato_fuera_de_rango_rechazado(self):
        with pytest.raises(ValidationError):
            PerfilFinancieroCreate(estrato=7)

    # RF-04.2 — Calcular capacidad económica (alta / media / baja).
    def test_rf0402_capacidad_alta_por_estrato(self):
        r = calcular_capacidad_financiera({"estrato": 5})
        assert r["capacidad_economica"] == "alta"

    def test_rf0402_capacidad_alta_por_puede_pagar(self):
        r = calcular_capacidad_financiera({"estrato": 1, "puede_pagar_matricula": "si"})
        assert r["capacidad_economica"] == "alta"

    def test_rf0402_capacidad_baja(self):
        r = calcular_capacidad_financiera({
            "estrato": 2, "ingresos_hogar": "<1", "puede_pagar_matricula": "no",
        })
        assert r["capacidad_economica"] == "baja"

    def test_rf0402_capacidad_media_por_defecto(self):
        r = calcular_capacidad_financiera({"estrato": 3})
        assert r["capacidad_economica"] == "media"

    # RF-04.3 — Determinar elegibilidad para subsidios.
    def test_rf0403_elegible_estrato_bajo(self):
        assert calcular_capacidad_financiera({"estrato": 3})["elegible_subsidios"] is True

    def test_rf0403_no_elegible_estrato_alto(self):
        assert calcular_capacidad_financiera({"estrato": 4})["elegible_subsidios"] is False

    def test_rf0402_modalidad_virtual_segun_recursos(self):
        r = calcular_capacidad_financiera({
            "estrato": 3, "acceso_internet": True, "tiene_computador": True,
            "disponibilidad_tiempo": "medio",
        })
        assert r["modalidad_recomendada"] == "virtual"


# ════════════════════════════════════════════════════════════════════
# RF-05 — Módulo Educativo
# ════════════════════════════════════════════════════════════════════

class TestRF05_Educativo:

    # RF-05.1 — Recomendaciones combinando perfil vocacional + financiero.
    def test_rf0501_combina_vocacional_y_financiero(self):
        rasgos = {"I": 70, "R": 20, "A": 10}
        progs = puntuar_programas(rasgos, "alta", "presencial")
        assert isinstance(progs, list) and len(progs) > 0
        assert all("score" in p for p in progs)

    def test_rf0501_orden_descendente_por_score(self):
        progs = puntuar_programas({"I": 70}, "alta", "presencial")
        scores = [p["score"] for p in progs]
        assert scores == sorted(scores, reverse=True)

    # RF-05.2 — Cada recomendación incluye modalidad, tipo, costo y ciudad.
    def test_rf0502_campos_requeridos_presentes(self):
        progs = puntuar_programas({"A": 60}, "media", "virtual")
        for campo in ("modalidad", "tipo", "costo", "ciudad"):
            assert campo in progs[0], f"Falta el campo {campo}"

    # RF-05.3 — Listar becas/subsidios cuando el usuario es elegible.
    def test_rf0503_becas_por_capacidad(self):
        assert len(BECAS_POR_CAPACIDAD["baja"]) > 0
        assert len(BECAS_POR_CAPACIDAD["media"]) > 0
        assert len(BECAS_POR_CAPACIDAD["alta"]) > 0

    def test_rf0503_capacidad_baja_incluye_gratuidad(self):
        becas = " ".join(BECAS_POR_CAPACIDAD["baja"]).lower()
        assert "gratuidad" in becas or "matrícula cero" in becas

    # RF-05.5 — Filtrar por costo y tipo según capacidad del usuario.
    def test_rf0505_capacidad_baja_filtra_costosos_sin_beca(self):
        progs = puntuar_programas({"I": 80}, "baja", "presencial")
        for p in progs:
            assert not (p["costo"] == "alto" and not p["con_beca"])

    def test_rf0505_capacidad_alta_incluye_mas_opciones(self):
        base = {"I": 60, "R": 20}
        alta = puntuar_programas(base, "alta", "presencial")
        baja = puntuar_programas(base, "baja", "presencial")
        assert len(alta) >= len(baja)
