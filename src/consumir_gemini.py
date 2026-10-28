import os
import json
import re
import requests
from dotenv import load_dotenv
import time

# Cargar las variables de entorno desde el archivo .env
load_dotenv()


def calcular_costo(datos, precio_entrada, precio_salida):
    # Extrae la metadata, calcula el costo y retorna todas las métricas juntas.
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    tokens_salida = uso["candidatesTokenCount"]
    tokens_total = uso["totalTokenCount"]

    costo = (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)
    return costo, tokens_entrada, tokens_salida, tokens_total


def armar_peticion(pregunta, system_instruction, response_schema=None):
    # Valida entrada y sistema, construye la URL, el body y el esquema opcional JSON.
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")

    if not system_instruction or not system_instruction.strip():
        raise ValueError("El prompt de sistema no puede estar vacío.")

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("No se encontró la API key en las variables de entorno.")

    modelo = "gemini-3.5-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"

    body = {
        "systemInstruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"parts": [{"text": pregunta}]}],
    }

    if response_schema is not None:
        body["generationConfig"] = {
            "responseMimeType": "application/json",
            "responseSchema": response_schema,
        }

    return url, body


def enviar_peticion(url, body):
    # Envía la petición y maneja errores de red o de formato JSON.
    try:
        respuesta = requests.post(url, json=body, timeout=10)
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
        # Se corrigió añadiendo la 'f' para que interpole la variable {e} correctamente
        raise TimeoutError(f"No se pudo conectar o tiempo de espera agotado: {e}")

    if respuesta.status_code in (401, 403):
        raise ValueError("Credencial inválida o sin permiso. Revisa tu API_KEY.")

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


def con_reintento(funcion, intentos=3, espera_segundos=2):
    """Función genérica para reintentar operaciones que fallen por TimeoutError (límites o red)."""
    for intento in range(1, intentos + 1):
        try:
            return funcion()
        except TimeoutError as error:
            if intento == intentos:
                raise RuntimeError(
                    f"El servicio no respondió tras varios intentos. Último error: {error}"
                )
            print(
                f"  [Reintento] Intento {intento} de {intentos} falló. Esperando {espera_segundos}s..."
            )
            time.sleep(espera_segundos)


def extraer_texto(datos):
    # Extrae el texto generado de la estructura JSON de la respuesta.
    print("\n--- MÉTRICAS DE USO Y COSTO ---")
    print(" Tokens de entrada:", datos["usageMetadata"]["promptTokenCount"])
    print(" Tokens de salida:", datos["usageMetadata"]["candidatesTokenCount"])
    print(" Tokens totales usados:", datos["usageMetadata"]["totalTokenCount"])
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError(
            "La respuesta no trae el texto generado en el lugar esperado."
        )


def parsear_respuesta_json(texto):
    # Limpia markdown, decodifica el JSON y retorna el diccionario de Python.
    texto_limpio = texto.strip()
    texto_limpio = re.sub(r"^```(?:json)?\s*", "", texto_limpio)
    texto_limpio = re.sub(r"\s*```$", "", texto_limpio)

    try:
        datos = json.loads(texto_limpio)
    except json.JSONDecodeError:
        raise ValueError("La respuesta del modelo no es JSON válido.")

    return datos


BANCO_DE_PROMPTS = [
    {
        "nombre": "clasificar_sentimiento",
        "system_instruction": (
            "Responde únicamente un JSON con las claves 'sentimiento' "
            "('positivo', 'negativo' o 'neutro') y 'confianza' (número entre 0 y 1)."
        ),
        "ejemplo_usuario": "El servicio llegó tarde pero el producto está perfecto.",
        "claves_esperadas": ["sentimiento", "confianza"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "sentimiento": {"type": "STRING"},
                "confianza": {"type": "NUMBER"},
            },
            "required": ["sentimiento", "confianza"],
        },
    },
    {
        "nombre": "extraer_prioridad",
        "system_instruction": (
            "Analiza el mensaje del usuario y clasifícalo en un JSON estricto "
            "con las claves 'prioridad' ('alta', 'media', 'baja') y 'urgente' (booleano)."
        ),
        "ejemplo_usuario": "El sistema de pagos está caído y los usuarios no pueden comprar.",
        "claves_esperadas": ["prioridad", "urgente"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "prioridad": {"type": "STRING"},
                "urgente": {"type": "BOOLEAN"},
            },
            "required": ["prioridad", "urgente"],
        },
    },
    {
        "nombre": "resumen_corto",
        "system_instruction": (
            "Resume el texto provisto en un JSON con las claves 'resumen' (string de máximo 15 palabras) "
            "y 'palabras_clave' (array de strings)."
        ),
        "ejemplo_usuario": "La inteligencia artificial agiliza procesos repetitivos en la banca y reduce errores humanos.",
        "claves_esperadas": ["resumen", "palabras_clave"],
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "resumen": {"type": "STRING"},
                "palabras_clave": {"type": "ARRAY", "items": {"type": "STRING"}},
            },
            "required": ["resumen", "palabras_clave"],
        },
    },
]


def probar_consistencia_banco():
    # Ejecuta el banco de prompts múltiples veces y genera el registro de resultados.
    registro = {}
    print("--- INICIANDO PRUEBAS DE CONSISTENCIA DEL BANCO DE PROMPTS ---\n")

    for prompt in BANCO_DE_PROMPTS:
        exitos = 0
        intentos_banco = 3
        print(f"Probando prompt: '{prompt['nombre']}'")

        for intento in range(intentos_banco):
            try:
                url, body = armar_peticion(
                    prompt["ejemplo_usuario"],
                    prompt["system_instruction"],
                    prompt.get("response_schema"),
                )

                # Envolvemos el envío en la función de reintento para aguantar caídas y límites 429
                respuesta = con_reintento(lambda: enviar_peticion(url, body))

                texto = extraer_texto(respuesta)
                datos = parsear_respuesta_json(texto)

                if all(clave in datos for clave in prompt["claves_esperadas"]):
                    exitos += 1
                else:
                    print(
                        f"  Intento {intento + 1} falló: Faltan claves esperadas en la estructura."
                    )

            # Se incluye TimeoutError para capturar correctamente las excepciones de reintento agotado o red
            except (ValueError, RuntimeError, TimeoutError) as error:
                print(f"  Intento {intento + 1} falló: {error}")

            time.sleep(2)

        print(
            f"-> Resultado para '{prompt['nombre']}': {exitos}/{intentos_banco} respuestas válidas\n"
        )
        registro[prompt["nombre"]] = {"exitos": exitos, "intentos": intentos_banco}

    with open("prompts/registro_resultados.json", "w", encoding="utf-8") as archivo:
        json.dump(registro, archivo, indent=2, ensure_ascii=False)

    print("¡Pruebas finalizadas! Registro guardado en 'registro_resultados.json'.")


def obtener_dato_de_prueba(pregunta, system_instruction, response_schema=None):
    # Función principal que coordina el flujo completo del módulo.
    try:
        url, body = armar_peticion(pregunta, system_instruction, response_schema)

        # Integrando reintento automático
        datos = con_reintento(lambda: enviar_peticion(url, body))

        costo, tokens_in, tokens_out, tokens_tot = calcular_costo(
            datos, 0.00000030, 0.00000250
        )

        print(f"Costo estimado: ${costo:.6f}")
        texto_generado = extraer_texto(datos)

        if response_schema is not None:
            return parsear_respuesta_json(texto_generado)
        else:
            return texto_generado

    except (ValueError, RuntimeError, TimeoutError) as error:
        print("No se pudo completar la operación:", error)
        return None


def test_latencia(pregunta, system_instruction, ciclos=4):
    # Realiza pruebas de rendimiento midiendo la latencia.
    latencias = []
    try:
        url, body = armar_peticion(pregunta, system_instruction)
        for i in range(ciclos):
            inicio = time.perf_counter()
            _ = con_reintento(lambda: enviar_peticion(url, body))
            fin = time.perf_counter()
            latencia_intento = fin - inicio
            latencias.append(latencia_intento)
            print(f"Intento {i + 1}: {latencia_intento:.2f} segundos")

        latencia_promedio = sum(latencias) / len(latencias)
        print(f"Latencia promedio: {latencia_promedio:.2f} segundos")
    except (ValueError, RuntimeError, TimeoutError) as error:
        print("Error en el test de latencia:", error)


if __name__ == "__main__":
    probar_consistencia_banco()
