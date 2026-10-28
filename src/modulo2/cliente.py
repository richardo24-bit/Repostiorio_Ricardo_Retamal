import time
import random
from typing import Callable, Any
from cliente_api import armar_peticion, enviar_peticion, extraer_texto

def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    """Ejecuta una función y reintenta aplicando backoff exponencial y jitter si lanza un TimeoutError."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            # Cálculo de espera exponencial con un techo máximo y jitter aleatorio (10%)
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            espera_con_jitter = espera + random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} falló. Reintentando en {espera_con_jitter:.1f}s...")
            time.sleep(espera_con_jitter)

# Configuración de costos referenciales por cada 1000 tokens
COSTO_POR_1000_TOKENS = 0.002
costo_total_sesion = 0.0

def registrar_costo(respuesta: dict) -> float:
    """Calcula, acumula e imprime el costo estimado de los tokens de la operación exitosa."""
    global costo_total_sesion
    uso = respuesta.get("usageMetadata", {})
    total_tokens = uso.get("totalTokenCount", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
    
    print(f"Operación: {total_tokens} tokens, costo estimado: ${costo_estimado:.5f} (acumulado: ${costo_total_sesion:.5f})")
    return costo_estimado

def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    """Función principal: arma la petición, aplica reintento con backoff, registra costos y extrae el texto."""
    cuerpo = armar_peticion(pregunta, system_instruction)
    
    try:
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    
    registrar_costo(respuesta)
    return extraer_texto(respuesta)

if __name__ == "__main__":
    print("--- INICIANDO ENSAYO DE ESTRÉS Y CONTROL DE COSTOS ---\n")
    
    # Bucle para enviar múltiples peticiones seguidas y provocar el rate limit (429) a propósito
    for i in range(20):
        try:
            respuesta = consultar_modelo(f"Pregunta de prueba número {i}")
            print(f"Respuesta {i}: {respuesta[:40]}...\n")
        except RuntimeError as error:
            print(f"Respuesta {i} falló definitivamente: {error}\n")

    # Muestra el costo total acumulado al terminar el ensayo completo
    print(f"Costo total del ensayo: ${costo_total_sesion:.5f}")