import json

# Muestra de 10 casos revisados a mano (los 5 con menor F1 y los 5 con mayor F1)
revision_manual = [
    {
        "consulta": "¿Cuándo se creó Python?",
        "f1": 0.169,
        "correccion_factual": "no",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "la respuesta da un contexto amplio pero introduce detalles cronológicos inexactos frente a la referencia corta."
    },
    {
        "consulta": "¿Qué es Python?",
        "f1": 0.039,
        "correccion_factual": "parcial",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "el puntaje F1 colapsa por la asimetría de longitud; la respuesta es exhaustiva y correcta, pero la referencia es minimalista."
    },
    {
        "consulta": "¿Qué es una lista en Python?",
        "f1": 0.045,
        "correccion_factual": "si",
        "completitud": "si",
        "contradiccion": "no",
        "nota": "ocurre el mismo fenómeno de longitud: incluye bloques de código y explicaciones largas que penalizan la precisión léxica."
    },
    # ... (puedes agregar el resto de tus casos extremos evaluados con la rúbrica)
]

with open("revision_manual.json", "w", encoding="utf-8") as archivo:
    json.dump(revision_manual, archivo, indent=2, ensure_ascii=False)

print("revision_manual.json generado correctamente.")