import os
import requests
from dotenv import load_dotenv
import time
  
load_dotenv()

import os
import requests
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

def calcular_costo(datos, precio_entrada, precio_salida):
    """Extrae la metadata, calcula el costo y retorna todas las métricas juntas."""
    uso = datos["usageMetadata"]
    tokens_entrada = uso["promptTokenCount"]
    tokens_salida = uso["candidatesTokenCount"]
    tokens_total = uso["totalTokenCount"]
    
    costo = (tokens_entrada * precio_entrada) + (tokens_salida * precio_salida)
    
    
    return costo, tokens_entrada, tokens_salida, tokens_total

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
    print("\n--- MÉTRICAS DE USO Y COSTO ---")
    print(f" Tokens de entrada:" ,datos["usageMetadata"]["promptTokenCount"])
    print(f" Tokens de salida:" ,datos["usageMetadata"]["candidatesTokenCount"])
    print(f" Tokens totales usados:" ,datos["usageMetadata"]["totalTokenCount"])
    try:
        
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en el lugar esperado.")

#bloque de pruebas
def obtener_dato_de_prueba(pregunta):
    #Función principal que coordina el flujo completo del módulo.
    try:
        url, body = armar_peticion(pregunta)
        datos = enviar_peticion(url, body)
        costo = calcular_costo(datos,0.00000030,0.00000250)
        print("Respuesta de la IA:")
        print(f"Costo estimado: ${costo}")
        return extraer_texto(datos)
    except (ValueError, RuntimeError) as error:
            print("No se pudo completar la operación:", error)

def test_latencia (i) :
        latencias = []
        for i in range(4):
            url, body = armar_peticion("C ")
            inicio = time.perf_counter()
            respuesta_json = enviar_peticion(url, body)
            fin = time.perf_counter()
            latencias.append(fin - inicio)
            print(f"Intento {i + 1}: {latencias[-1]:.2f} segundos")
        latencia_promedio = sum(latencias) / len(latencias)
        print(f"Latencia promedio: {latencia_promedio:.2f} segundos")
            
 

if __name__ == "__main__":#
    print(obtener_dato_de_prueba("¿cuanto es 2 + 2? dame solo el numero"))
    test_latencia(10)
    