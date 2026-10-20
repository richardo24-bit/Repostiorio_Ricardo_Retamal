import os
import requests
from dotenv import load_dotenv
  
load_dotenv()

import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def calcular_costo(datos, precio_entrada, precio_salida):
	uso = datos["usageMetadata"]
	tokens_entrada = uso["promptTokenCount"]
	tokens_salida = uso["candidatesTokenCount"]
	return (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)

def armar_peticion(pregunta):
    #Valida entrada, construye la URL y el body de la petición.
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("No se encontró la API key en las variables de entorno.")
        
    modelo = "gemini-3.5-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={api_key}"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    return url, body

def enviar_peticion(url, body):
    #Envía la petición y maneja errores de red o de formato JSON.
    try:
        respuesta = requests.post(url, json=body)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Intenta de nuevo en unos segundos.")
    
    # Validar si la respuesta HTTP fue exitosa antes de parsear
    if respuesta.status_code != 200:
        raise RuntimeError(f"El servicio respondió con un error (Código {respuesta.status_code}): {respuesta.text}")

    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError("La respuesta del servicio no llegó en el formato esperado.")

def extraer_texto(datos):
    #Extrae el texto generado de la estructura JSON de la respuesta
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")

def obtener_dato_de_prueba(pregunta):
    #Función principal que coordina el flujo completo del módulo.
    url, body = armar_peticion(pregunta)
    datos = enviar_peticion(url, body)
    return extraer_texto(datos)


#Bloque de pregunta 
try:
    pregunta = "En 20 palabras, ¿Cual es el animal mas grande del mundo?"
    
    # Ejecucion de flujo para obtener datos
    url, body = armar_peticion(pregunta)
    datos_respuesta = enviar_peticion(url, body)
    
    # Extraer datos con función
    resultado = extraer_texto(datos_respuesta)
    print("Respuesta de la IA:")
    print(resultado)
    
    print("\n--- MÉTRICAS DE USO Y COSTO ---")
    # Precios de referencia por modelo
    PRECIO_ENTRADA = 0.00000030
    PRECIO_SALIDA = 0.00000250 
    
    # 3. Calculo el costo con función calcular_costo
    uso = datos_respuesta["usageMetadata"]
    tokens_in = uso["promptTokenCount"]
    tokens_out = uso["candidatesTokenCount"]
    tokens_total = uso["totalTokenCount"]
    
    costo_total = calcular_costo(datos_respuesta, PRECIO_ENTRADA, PRECIO_SALIDA)
    
    print(f"Tokens de entrada: {tokens_in}")
    print(f"Tokens de salida: {tokens_out}")
    print(f"Total de tokens: {tokens_total}")
    print(f"Costo estimado: ${costo_total:.6f}")

except (ValueError, RuntimeError) as error:
    print("No se pudo completar la operación:", error)