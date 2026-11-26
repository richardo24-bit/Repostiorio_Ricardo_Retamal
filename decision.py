def recomendar_estrategia(respuestas):
    puntos = {"RAG": 0, "Fine-tuning completo": 0, "PEFT": 0}

    if respuestas["informacion_cambia_seguido"]:
        puntos["RAG"] += 3
    if respuestas["problema_de_formato_o_tono"]:
        puntos["PEFT"] += 2
        puntos["Fine-tuning completo"] += 1
    if respuestas["dataset_grande_y_de_calidad"]:
        puntos["Fine-tuning completo"] += 2
        puntos["PEFT"] += 1
    if respuestas["presupuesto_limitado_o_iterar_rapido"]:
        puntos["RAG"] += 2
        puntos["PEFT"] += 1
    if respuestas["necesita_multiples_variantes"]:
        puntos["PEFT"] += 2

    maximo = max(puntos.values())
    ganadoras = [tecnica for tecnica, p in puntos.items() if p == maximo]
    return puntos, ganadoras


def generar_esqueleto_decision(problema, puntos, ganadoras):
    empate = len(ganadoras) > 1
    lineas = [
        "# Decision de personalizacion",
        "",
        "## 1. El problema",
        problema,
        "",
        "## 2. Resultado del metodo de decision",
    ]
    for tecnica, p in sorted(puntos.items(), key=lambda x: -x[1]):
        lineas.append(f"- {tecnica}: {p} puntos")
    if empate:
        lineas.append("")
        lineas.append(f"**Empate entre: {', '.join(ganadoras)}**")

    lineas.append("")
    lineas.append("## 3. Tecnica elegida y por que")
    if empate:
        lineas.append("[COMPLETAR: justifica el desempate con criterio propio]")
    else:
        lineas.append(f"[COMPLETAR: por que {ganadoras[0]} responde mejor a este caso]")

    lineas.append("")
    lineas.append("## 4. Que necesitarias para ejecutarla")
    lineas.append("[COMPLETAR: corpus faltante o cantidad exacta de ejemplos etiquetados]")
    return "\n".join(lineas)


# Evaluacion sobre el clasificador de triaje de siniestros (Bloque 29)
respuestas_mi_caso = {
    "informacion_cambia_seguido": False,        # Las 4 categorias de triaje no cambian cada mes
    "problema_de_formato_o_tono": True,         # Necesitamos JSON estricto con tipo_gestion y prioridad
    "dataset_grande_y_de_calidad": False,       # Hoy tenemos 12 ejemplos validados (bajo el umbral de 200)
    "presupuesto_limitado_o_iterar_rapido": True,  # Presupuesto acotado (max 2 intentos) y necesidad de iterar rapido
    "necesita_multiples_variantes": False,      # Un solo clasificador para todo el flujo de siniestros
}

if any(valor is None for valor in respuestas_mi_caso.values()):
    raise SystemExit("Completa las cinco respuestas con True o False antes de continuar.")

puntos, ganadoras = recomendar_estrategia(respuestas_mi_caso)
print("Puntajes:", puntos)
print("Candidatas:", ganadoras)

# Prueba rapida de sensibilidad cambiando una respuesta a la vez
print("\n--- Sensibilidad ---")
for clave in respuestas_mi_caso:
    variante = dict(respuestas_mi_caso)
    variante[clave] = not variante[clave]
    _, ganadoras_v = recomendar_estrategia(variante)
    cambio = "CAMBIA" if set(ganadoras_v) != set(ganadoras) else "igual"
    print(f"{clave} -> {variante[clave]}: {ganadoras_v} [{cambio}]")

esqueleto = generar_esqueleto_decision(
    "El clasificador de mensajes de asegurados necesita devolver siempre un JSON estricto con tipo_gestion y prioridad.",
    puntos,
    ganadoras,
)

with open("decision_personalizacion.md", "w", encoding="utf-8") as f:
    f.write(esqueleto)

print("\nEsqueleto guardado en decision_personalizacion.md")