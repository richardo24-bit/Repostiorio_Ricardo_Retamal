import time
import random
from typing import Callable, Any

# Importamos las funciones base desde tu módulo cliente_api.py
from cliente_api import armar_peticion, enviar_peticion, extraer_texto


def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_base: float = 2,
    espera_maxima: float = 30,
) -> Any:
    """Ejecuta una función y reintenta con retroceso exponencial si lanza un TimeoutError."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            # Cálculo de espera exponencial con un poco de aleatoriedad (jitter)
            espera = min(espera_base * (2 ** (intento - 1)), espera_maxima)
            tiempo_espera = espera + random.uniform(0, espera * 0.1)
            print(f"Intento {intento} de {intentos} falló. Reintentando en {tiempo_espera:.2f}s...")
            time.sleep(tiempo_espera)


# Variables y función de control de costos de la sesión
COSTO_POR_1000_TOKENS = 0.002  # Referencial según el modelo
costo_total_sesion = 0.0


def registrar_costo(respuesta: dict) -> float:
    """Calcula y acumula el costo estimado de los tokens utilizados en la respuesta."""
    global costo_total_sesion
    uso = respuesta.get("usageMetadata", {})
    total_tokens = uso.get("totalTokenCount", 0)
    costo_estimado = (total_tokens / 1000) * COSTO_POR_1000_TOKENS
    costo_total_sesion += costo_estimado
    return costo_estimado


def consultar_modelo(pregunta: str, system_instruction: str = "") -> str:
    """Función pública principal: arma la petición, la envía con reintentos y registra costos."""
    # 1. Arma el cuerpo utilizando la función de cliente_api
    cuerpo = armar_peticion(pregunta, system_instruction)
    
    try:
        # 2. Envía la petición aplicando la lógica de reintentos
        respuesta = con_reintento(lambda: enviar_peticion(cuerpo))
    except TimeoutError:
        # Traduce el agotamiento de reintentos en un error amigable para el usuario final
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
    
    # 3. Registra el costo y extrae el texto final
    registrar_costo(respuesta)
    return extraer_texto(respuesta)


if __name__ == "__main__":
    try:
        print("Enviando consulta al modelo...")
        resultado = consultar_modelo("¿Cuál es la capital de Mexico?")
        print("\n--- RESPUESTA ---")
        print(resultado)
        print(f"\nCosto acumulado de la sesión: ${costo_total_sesion:.5f}")
    except ValueError as error:
        print(f"Error de configuración: {error}")
    except RuntimeError as error:
        print(f"Error en la ejecución: {error}")