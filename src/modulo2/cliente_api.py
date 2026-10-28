import os
import requests
from dotenv import load_dotenv

# Carga las variables definidas en el archivo .env (API_KEY)
load_dotenv()

API_KEY = os.getenv("API_KEY")
URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    f"gemini-3.5-flash-lite:generateContent?key={API_KEY}"
)
headers = {"Content-Type": "application/json"}


def armar_peticion(
    pregunta: str, system_instruction: str = "Eres un asistente útil y conciso."
) -> dict:
    """Valida los campos y construye el cuerpo (body) de la petición para la API."""
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if not system_instruction or not system_instruction.strip():
        system_instruction = "Eres un asistente útil."

    cuerpo = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": pregunta}]}],
    }
    return cuerpo


def enviar_peticion(cuerpo: dict) -> dict:
    """Envía la petición HTTP y clasifica los errores según el código de estado."""
    try:
        respuesta = requests.post(URL, json=cuerpo, headers=headers, timeout=10)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        raise TimeoutError(
            f"No se pudo contactar al proveedor. Puede ser momentáneo: {e}"
        )

    # 401 y 403: Credenciales inválidas o sin permiso (NO se reintenta)
    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu API_KEY.")

    # 429 y códigos >= 500: Límites de uso o errores del servidor (SÍ se reintenta)
    if respuesta.status_code == 429 or respuesta.status_code >= 500:
        raise TimeoutError(
            "El proveedor no pudo procesar la petición. Hay que esperar y reintentar."
        )

    if respuesta.status_code != 200:
        raise RuntimeError(
            f"El servicio respondió con un error (Código {respuesta.status_code}): {respuesta.text}"
        )

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")


def extraer_texto(datos: dict) -> str:
    """Extrae el texto generado de la estructura JSON de la respuesta."""
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        )
