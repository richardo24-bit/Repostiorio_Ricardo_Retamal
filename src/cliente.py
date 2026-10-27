import time
from typing import Callable, Any
# Importa todas las funciones necesarias desde modulo base
from consumir_gemini import armar_peticion, enviar_peticion, extraer_texto

def con_reintento(
    funcion: Callable[[], Any],
    intentos: int = 3,
    espera_segundos: int = 2,
) -> Any:
    """Ejecuta una función y reintenta automáticamente si lanza un TimeoutError."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError:
            if intento == intentos:
                raise
            print(f"Intento {intento} de {intentos} falló por límite de uso. Reintentando...")
            time.sleep(espera_segundos)

def consultar_modelo(
    pregunta: str,
    system_instruction: str = "",
) -> str:
    """Función pública principal: arma la petición, la envía con reintentos y extrae el texto."""
  
    url, body = armar_peticion(pregunta, system_instruction)
    
    try:
        
        respuesta = con_reintento(lambda: enviar_peticion(url, body))
    except TimeoutError:
        raise RuntimeError("El servicio no respondió tras varios intentos. Intenta más tarde.")
        
    return extraer_texto(respuesta)

if __name__ == "__main__":
    try:
        print("Enviando consulta al modelo...")
        
        resultado = consultar_modelo(
            pregunta="¿Cuál es la capital de Chile?",
            system_instruction="Eres un asistente amigable y experto en geografía. Responde de forma breve."
        )
        print("\n--- RESPUESTA ---")
        print(resultado)
    except ValueError as error:
        print(f"Error de configuración (API_KEY): {error}")
    except RuntimeError as error:
        print(f"Error en la ejecución: {error}")