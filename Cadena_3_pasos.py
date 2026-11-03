from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def construir_cadena(modelo):
    """Construye y devuelve una cadena de tres pasos conectados con LangChain."""
    
    # 1 analiza y describe puntos clave
    plantilla_analizar = PromptTemplate.from_template(
        "Extrae y resume los puntos clave del siguiente caso de soporte o siniestro:\n\n{texto}"
    )
    paso_analizar = plantilla_analizar | modelo | StrOutputParser()

    # 2 redacta respuesta de soporte
    plantilla_redactar = PromptTemplate.from_template(
        "A partir de los siguientes puntos clave, redacta una respuesta inicial y formal de soporte:\n\n{puntos_clave}"
    )
    paso_redactar = plantilla_redactar | modelo | StrOutputParser()

    # 3 formatea como correo electrónico profesional
    plantilla_formatear = PromptTemplate.from_template(
        "Convierte la siguiente respuesta en un correo electrónico estructurado, incluyendo un asunto claro y el cuerpo del mensaje:\n\n{borrador}"
    )
    paso_formatear = plantilla_formatear | modelo | StrOutputParser()

    # Encadenamiento lineal completo con el operador '|' y funciones intermedias
    cadena = (
        paso_analizar
        | (lambda puntos_clave: {"puntos_clave": puntos_clave})
        | paso_redactar
        | (lambda borrador: {"borrador": borrador})
        | paso_formatear
    )
    return cadena


if __name__ == "__main__":
    load_dotenv()
    # Instanciación del modelo de Gemini
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")
    cadena = construir_cadena(modelo)

    # Caso de entrada real (simulando un reporte operativo o de reclamo)
    texto_entrada = (
        "Hola, tengo un problema crítico con el sistema de seguimiento de siniestros. "
        "Cuando intento ingresar el número de póliza, la pantalla se queda congelada "
        "y luego sale un error 500. Necesito una solución urgente porque tengo talleres esperando."
    )

    print("--- EJECUTANDO CADENA DE TRES PASOS ---")
    resultado = cadena.invoke({"texto": texto_entrada})
    print(resultado)