from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableBranch,
    RunnablePassthrough,
    RunnableLambda,
)
import logging

load_dotenv()

# Configuración del sistema de logging para trazar errores sin perderlos
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def construir_paso_clasificacion(modelo):
    """Construye el paso que clasifica la entrada y la normaliza a minúsculas sin espacios."""
    plantilla_clasificacion = PromptTemplate.from_template(
        "Clasifica el siguiente mensaje de soporte en una sola "
        "palabra: pregunta, queja o sugerencia. Responde solo "
        "con esa palabra.\n\n{mensaje}"
    )
    return (
        plantilla_clasificacion
        | modelo
        | StrOutputParser()
        | (lambda texto: texto.strip().lower())
    )


# Respuesta genérica de respaldo para los fallbacks
respuesta_generica = RunnableLambda(
    lambda x: (
        "Gracias por tu mensaje. Un miembro de nuestro "
        "equipo te va a responder pronto."
    )
)


def construir_cadena_queja_segura(cadena_queja):
    """Protege la ruta de quejas envolviéndola con with_fallbacks."""
    return cadena_queja.with_fallbacks([respuesta_generica])


def procesar_mensaje_seguro(cadena, mensaje):
    """Red de seguridad general (try/except) alrededor del invoke completo de la chain."""
    try:
        return cadena.invoke({"mensaje": mensaje})
    except Exception as error:
        logger.error(f"Error procesando mensaje: {error}")
        return (
            "No pudimos procesar tu mensaje en este "
            "momento. Intenta de nuevo más tarde."
        )


def construir_cadena_con_enrutamiento(
    paso_clasificacion,
    cadena_queja=None,
    cadena_sugerencia=None,
    cadena_pregunta=None,
):
    """Encadena la clasificación con la bifurcación condicional (RunnableBranch)."""
    modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

    cadena_queja = cadena_queja or (
        PromptTemplate.from_template("Responde a esta queja con empatía:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )
    
    # Aplicamos fallback seguro a la cadena de queja
    cadena_queja_segura = construir_cadena_queja_segura(cadena_queja)

    cadena_sugerencia = cadena_sugerencia or (
        PromptTemplate.from_template("Agradece esta sugerencia:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )
    cadena_pregunta = cadena_pregunta or (
        PromptTemplate.from_template("Responde esta pregunta técnica con precisión:\n\n{mensaje}")
        | modelo
        | StrOutputParser()
    )

    bifurcacion = RunnableBranch(
        (lambda x: x["categoria"] == "queja", cadena_queja_segura),
        (lambda x: x["categoria"] == "sugerencia", cadena_sugerencia),
        cadena_pregunta,
    )

    return (
        RunnablePassthrough.assign(categoria=paso_clasificacion)
        | bifurcacion
    )