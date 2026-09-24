# Test standalone — no requiere FastAPI ni DB
# Copia las funciones del algoritmo para probarlas directamente

PROGRAMAS_EDUCATIVOS = {
    "R": [
        {"nombre": "Técnico en Electrónica",     "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Mecánica Automotriz",         "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Tecnología en Construcción",  "inst": "SENA",            "tipo": "Tecnológico",   "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Mecánica",         "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Civil",            "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería Industrial",       "inst": "Uniminuto",       "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Ingeniería Mecánica",         "inst": "U. de los Andes", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "I": [
        {"nombre": "Análisis y Desarrollo de Software", "inst": "SENA",     "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Ingeniería de Sistemas",      "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Matemáticas",                 "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Ingeniería de Sistemas",      "inst": "Uniminuto",       "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Ciencia de Datos",            "inst": "U. de los Andes", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
        {"nombre": "Física",                      "inst": "U. Javeriana",    "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "A": [
        {"nombre": "Diseño Gráfico",              "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Producción Multimedia",       "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Artes Visuales",              "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Diseño Gráfico",              "inst": "Uniminuto",       "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Arquitectura",                "inst": "U. Javeriana",    "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
        {"nombre": "Publicidad",                  "inst": "U. Jorge Tadeo",  "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "S": [
        {"nombre": "Atención a la Primera Infancia", "inst": "SENA",        "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Trabajo Social",              "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Enfermería",                  "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Psicología",                  "inst": "Uniminuto",       "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Docencia",                    "inst": "U. Pedagógica",   "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Psicología",                  "inst": "U. Javeriana",    "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "E": [
        {"nombre": "Técnico en Ventas",           "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Administración de Empresas",  "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Administración de Empresas",  "inst": "Uniminuto",       "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Negocios Internacionales",    "inst": "U. EAN",          "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Marketing",                   "inst": "U. de los Andes", "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
        {"nombre": "Emprendimiento e Innovación", "inst": "U. Javeriana",    "tipo": "Universitario", "costo": "alto",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
    ],
    "C": [
        {"nombre": "Contabilidad y Finanzas",     "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Gestión Documental",          "inst": "SENA",            "tipo": "Técnico",       "costo": "gratuito", "ciudad": "Nacional", "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Contaduría Pública",          "inst": "UNAL",            "tipo": "Universitario", "costo": "bajo",     "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": True},
        {"nombre": "Administración",              "inst": "Uniminuto",       "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial", "virtual"], "con_beca": True},
        {"nombre": "Finanzas y Comercio Exterior","inst": "U. EAN",          "tipo": "Universitario", "costo": "medio",    "ciudad": "Bogotá",   "modalidad": ["presencial"],            "con_beca": False},
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

# ─────────────────────────────────────────────────────────────────────────────

SEP = "─" * 72

def tabla(titulo, programas, limite=10):
    print(f"\n{'═'*72}")
    print(f"  {titulo}")
    print(f"{'═'*72}")
    print(f"{'#':<3} {'PROGRAMA':<36} {'INSTITUCIÓN':<16} {'RASGO':<6} {'SCORE':>6}")
    print(SEP)
    for i, p in enumerate(programas[:limite], 1):
        beca = " ★" if p["con_beca"] else ""
        print(f"{i:<3} {p['nombre']:<36} {p['inst']:<16} {p['rasgo']:<6} {p['score']:>6.3f}{beca}")
    print(f"\n  Total recomendados: {len(programas)}")

# CASO 1 — Investigador fuerte, capacidad baja, virtual
r1 = {"R": 15, "I": 70, "A": 10, "S": 10, "E": 5, "C": 5}
p1 = puntuar_programas(r1, "baja", "virtual")
tabla("CASO 1 — Investigador (I=70) | Capacidad BAJA | Virtual", p1)

# CASO 2 — Social + Emprendedor, capacidad media, presencial
r2 = {"R": 5, "I": 10, "A": 15, "S": 40, "E": 35, "C": 5}
p2 = puntuar_programas(r2, "media", "presencial")
tabla("CASO 2 — Social+Emprendedor (S=40, E=35) | Capacidad MEDIA | Presencial", p2)

# CASO 3 — Artístico, capacidad alta, presencial
r3 = {"R": 5, "I": 10, "A": 65, "S": 10, "E": 5, "C": 5}
p3 = puntuar_programas(r3, "alta", "presencial")
tabla("CASO 3 — Artístico (A=65) | Capacidad ALTA | Presencial", p3)

# ── VALIDACIONES ──────────────────────────────────────────────────────────────
print(f"\n{'═'*72}")
print("  VALIDACIONES")
print(f"{'═'*72}")

ok = True

# 1. Orden descendente
for nombre, prog in [("Caso1", p1), ("Caso2", p2), ("Caso3", p3)]:
    scores = [p["score"] for p in prog]
    passed = scores == sorted(scores, reverse=True)
    print(f"  {'✅' if passed else '❌'} Orden descendente ({nombre}): {'OK' if passed else 'FALLO'}")
    ok = ok and passed

# 2. Sin inaccesibles en capacidad baja
inac = [p for p in p1 if p["costo"] not in ["gratuito", "bajo"] and not p["con_beca"]]
passed = not inac
print(f"  {'✅' if passed else '❌'} Sin inaccesibles (capacidad baja): {'OK' if passed else f'FALLO — {len(inac)} programas fuera de rango'}")
ok = ok and passed

# 3. Alta tiene >= programas que baja
rb = {"R": 20, "I": 60, "A": 5, "S": 5, "E": 5, "C": 5}
alta = puntuar_programas(rb, "alta", "presencial")
baja = puntuar_programas(rb, "baja", "presencial")
passed = len(alta) >= len(baja)
print(f"  {'✅' if passed else '❌'} Alta >= programas que baja: {'OK' if passed else 'FALLO'} ({len(alta)} vs {len(baja)})")
ok = ok and passed

# 4. Score siempre entre 0 y 1
todos = p1 + p2 + p3
fuera = [p for p in todos if not (0 <= p["score"] <= 1)]
passed = not fuera
print(f"  {'✅' if passed else '❌'} Scores en rango [0, 1]: {'OK' if passed else f'FALLO — {len(fuera)} fuera de rango'}")
ok = ok and passed

# 5. Holland — rasgo I debe salir primero en perfil I fuerte
primer_rasgo = p1[0]["rasgo"] if p1 else None
passed = primer_rasgo in ["I", "R", "A"]  # I o adyacentes
print(f"  {'✅' if passed else '❌'} Primer programa en rasgo correcto (I o adyacente): {'OK' if passed else f'FALLO — rasgo={primer_rasgo}'}")
ok = ok and passed

print(f"\n  {'🎉 TODAS LAS VALIDACIONES PASARON' if ok else '⚠️  ALGUNAS VALIDACIONES FALLARON'}")
print(f"{'═'*72}\n")
