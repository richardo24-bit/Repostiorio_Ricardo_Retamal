import re
import json
from collections import Counter
from cliente import consultar_modelo

def limpiar_texto(texto: str) -> str:
    """Convierte el texto a minúsculas, elimina puntuación y normaliza espacios en blanco."""
    if not isinstance(texto, str):
        return ""
    texto = texto.lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto

def tokenizar(texto_limpio: str) -> list[str]:
    """Divide el texto limpio en una lista de tokens (palabras)."""
    if not texto_limpio:
        return []
    return texto_limpio.split()

def procesar_texto(texto: str) -> list[str]:
    """Pipeline completo: limpia el texto y lo tokeniza."""
    texto_limpio = limpiar_texto(texto)
    return tokenizar(texto_limpio)

def contar_coincidencias(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> int:
    """Cuenta las coincidencias entre referencia y respuesta respetando frecuencias (Counter)."""
    conteo_referencia = Counter(tokens_referencia)
    conteo_respuesta = Counter(tokens_respuesta)
    interseccion = conteo_referencia & conteo_respuesta
    return sum(interseccion.values())

def calcular_precision_cobertura_f1(
    tokens_referencia: list[str],
    tokens_respuesta: list[str],
) -> dict[str, float]:
    """Calcula precisión, cobertura y F1 de dos listas de tokens."""
    coincidencias = contar_coincidencias(tokens_referencia, tokens_respuesta)

    if not tokens_respuesta or not tokens_referencia:
        return {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

    precision = coincidencias / len(tokens_respuesta)
    cobertura = coincidencias / len(tokens_referencia)

    if precision + cobertura == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * cobertura / (precision + cobertura)

    return {
        "precision": round(precision, 3),
        "cobertura": round(cobertura, 3),
        "f1": round(f1, 3),
    }

def calcular_metricas(texto_referencia: str, texto_respuesta: str) -> dict[str, float]:
    """Combina el pipeline de procesamiento y el cálculo de métricas en una sola llamada."""
    tokens_referencia = procesar_texto(texto_referencia)
    tokens_respuesta = procesar_texto(texto_respuesta)
    return calcular_precision_cobertura_f1(tokens_referencia, tokens_respuesta)

def resumir_metricas(resultados: list[dict]) -> dict[str, float]:
    """Resume una lista de resultados calculando los promedios de precisión, cobertura y F1."""
    if not resultados:
        return {
            "precision_promedio": 0.0,
            "cobertura_promedio": 0.0,
            "f1_promedio": 0.0,
        }

    n = len(resultados)
    return {
        "precision_promedio": round(sum(r["precision"] for r in resultados) / n, 3),
        "cobertura_promedio": round(sum(r["cobertura"] for r in resultados) / n, 3),
        "f1_promedio": round(sum(r["f1"] for r in resultados) / n, 3),
    }

if __name__ == "__main__":
    print("--- EVALUACIÓN DE SALIDAS CON PIPELINE DE TEXTO Y MÉTRICAS ---\n")
    
    casos = [
        (
            "¿Qué es Python?",
            "Python es un lenguaje de programación interpretado.",
        ),
        ("¿Cuándo se creó Python?", "Python fue creado en 1991."),
        (
            "¿Qué es una lista en Python?",
            "Una lista es una colección ordenada y modificable.",
        ),
    ]
    
    resultados = []
    for idx, (consulta, referencia) in enumerate(casos, start=1):
        print(f"Ejecutando Caso {idx}: {consulta}")
        respuesta = consultar_modelo(consulta)
        print(f"Respuesta generada: {respuesta}")
        
        # Comparación cruda vs procesada para evidencia del pipeline
        crudo_ref = referencia.split()
        crudo_resp = respuesta.split()
        comunes_crudo = set(crudo_ref) & set(crudo_resp)
        pct_crudo = len(comunes_crudo) / len(set(crudo_ref)) if crudo_ref else 0.0
        
        metricas = calcular_metricas(referencia, respuesta)
        
        print(f"[Caso {idx}] Coincidencia texto crudo: {pct_crudo:.1%}")
        print(f"[Caso {idx}] Métricas procesadas (Precisión, Cobertura, F1): {metricas}\n")
        
        resultados.append({
            "consulta": consulta,
            "referencia": referencia,
            "respuesta": respuesta,
            **metricas,
        })
        
    with open("resultados_metricas.json", "w", encoding="utf-8") as archivo:
        json.dump(resultados, archivo, indent=2, ensure_ascii=False)
        
    resumen = resumir_metricas(resultados)
    print("--- RESUMEN GENERAL DE MÉTRICAS ---")
    print(resumen)
    
    print("\n--- ORDENADOS POR PEORES CASOS (F1) ---")
    peores_casos = sorted(resultados, key=lambda r: r["f1"])
    for caso in peores_casos:
        print(f"Consulta: {caso['consulta']} | F1: {caso['f1']}")