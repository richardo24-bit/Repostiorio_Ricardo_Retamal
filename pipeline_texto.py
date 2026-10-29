import re
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

if __name__ == "__main__":
    print("--- EVALUACIÓN DE SALIDAS CON PIPELINE DE TEXTO ---\n")
    
    # 3 Casos de prueba reales comparando respuestas del modelo contra referencias escritas
    casos = [
        {
            "consulta": "¿Qué es Python?",
            "referencia": "Python es un lenguaje de programación interpretado."
        },
        {
            "consulta": "¿Cuál es la capital de Chile?",
            "referencia": "Santiago es la capital de Chile."
        },
        {
            "consulta": "¿Qué elemento químico es el H2O?",
            "referencia": "El agua está compuesta por hidrógeno y oxígeno."
        }
    ]
    
    for idx, caso in enumerate(casos, start=1):
        print(f"Ejecutando Caso {idx}: {caso['consulta']}")
        respuesta = consultar_modelo(caso["consulta"])
        print(f"Respuesta generada: {respuesta}")
        
        # 1. Medición con texto CRUDO (.split() sin limpieza)
        crudo_ref = caso["referencia"].split()
        crudo_resp = respuesta.split()
        comunes_crudo = set(crudo_ref) & set(crudo_resp)
        pct_crudo = len(comunes_crudo) / len(set(crudo_ref)) if crudo_ref else 0.0
        
        # 2. Medición con texto PROCESADO (Pipeline completo)
        tokens_ref = procesar_texto(caso["referencia"])
        tokens_resp = procesar_texto(respuesta)
        comunes_proc = set(tokens_ref) & set(tokens_resp)
        pct_proc = len(comunes_proc) / len(set(tokens_ref)) if tokens_ref else 0.0
        
        print(f"[Caso {idx}] Coincidencia texto crudo: {pct_crudo:.1%}")
        print(f"[Caso {idx}] Coincidencia texto procesado: {pct_proc:.1%}\n")