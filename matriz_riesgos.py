def puntaje_riesgo(probabilidad, impacto):
    return probabilidad * impacto


def categoria_riesgo(puntaje):
    if puntaje >= 15:
        return "CRITICO"
    if puntaje >= 9:
        return "ALTO"
    if puntaje >= 4:
        return "MEDIO"
    return "BAJO"


def esta_en_el_limite(probabilidad, impacto):
    categoria_actual = categoria_riesgo(puntaje_riesgo(probabilidad, impacto))
    vecinos = [
        (probabilidad + 1, impacto),
        (probabilidad - 1, impacto),
        (probabilidad, impacto + 1),
        (probabilidad, impacto - 1),
    ]
    for p2, i2 in vecinos:
        if not (1 <= p2 <= 5 and 1 <= i2 <= 5):
            continue
        if categoria_riesgo(puntaje_riesgo(p2, i2)) != categoria_actual:
            return True
    return False


mis_riesgos = [
    {
        "riesgo": "Inyeccion de prompt via relato de siniestro o ticket de taller indexado",
        "probabilidad": 4,
        "impacto": 4,
        "mitigacion": "Filtro de patrones sospechosos + delimitacion de contexto (Bloque 31)",
        "supervision": "Revision humana obligatoria cuando el filtro descarta un documento",
    },
    {
        "riesgo": "Filtracion de datos personales del asegurado (RUT, patente, telefono) en logs",
        "probabilidad": 3,
        "impacto": 5,
        "mitigacion": "Loguear solo largo de pregunta y trace_id en vez de texto completo (Bloque 31)",
        "supervision": "Aprobacion de acceso a logs de produccion solo para personal autorizado",
    },
    {
        "riesgo": "Dataset de triaje desbalanceado sesga la prioridad de reclamos de taller",
        "probabilidad": 3,
        "impacto": 3,
        "mitigacion": "Chequeo de balance por categoria y validacion JSON antes de entrenar (Bloque 29)",
        "supervision": "Revision manual del dataset y aprobacion antes de lanzar tuning PEFT",
    },
    {
        "riesgo": "Modelo de embeddings deprecado rompe la recuperacion semantica",
        "probabilidad": 2,
        "impacto": 4,
        "mitigacion": "Revision periodica de documentacion oficial y reindexacion completa (Bloque 25 y 28)",
        "supervision": "No aplica (MEDIO)",
    },
    {
        "riesgo": "Respuesta con plazos o deducibles viejos por manual no reindexado",
        "probabilidad": 3,
        "impacto": 2,
        "mitigacion": "Actualizacion del indice con ids explicitos y evaluacion periodica (Bloque 25 y 27)",
        "supervision": "No aplica (MEDIO)",
    },
]


if __name__ == "__main__":
    for r in mis_riesgos:
        r["puntaje"] = puntaje_riesgo(r["probabilidad"], r["impacto"])
        r["categoria"] = categoria_riesgo(r["puntaje"])
        r["al_limite"] = esta_en_el_limite(r["probabilidad"], r["impacto"])

    print("--- Matriz de riesgos ordenada ---")
    for r in sorted(mis_riesgos, key=lambda x: -x["puntaje"]):
        marca = " [AL LIMITE]" if r["al_limite"] else ""
        print(f"{r['categoria']:8} ({r['puntaje']:2}) - {r['riesgo']}{marca}")
        if r["categoria"] in ("CRITICO", "ALTO"):
            print(f"           Supervision: {r['supervision']}")

    print("\n--- Filas para revisar con otra persona ---")
    for r in mis_riesgos:
        if r["al_limite"]:
            print("-", r["riesgo"])