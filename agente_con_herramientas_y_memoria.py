from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
)
from langchain_classic.agents import (
    AgentExecutor,
    create_tool_calling_agent,
)

# 1. Carga de variables de entorno y configuración del modelo
load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


# --- Bloque 1: Herramienta personalizada con Pydantic (args_schema) ---
class ArgumentosConsultaSiniestro(BaseModel):
    numero_siniestro: str = Field(
        description="Número de identificación del siniestro, por ejemplo 'SIN88888'."
    )
    incluir_bitacora: bool = Field(
        default=False,
        description="Si es True, incluye el detalle técnico y la bitácora completa de los analistas de taller."
    )


TALLERES_DB = {
    "SIN88888": {
        "actual": "El vehículo se encuentra en fase de pintura y pulido final. Estimado de entrega: 3 días hábiles.",
        "bitacora": [
            "ingreso al taller y desarme pericial",
            "aprobación de repuestos por liquidación",
            "reparación de latonería y aplicación de fondo",
        ],
    },
    "SIN11111": {
        "actual": "El auto está ingresado en bancada para reparación estructural de chasis.",
        "bitacora": [
            "ingreso a banco de estiraje",
            "medición láser de geometría",
        ],
    },
}


@tool(
    "consultar_estado_reparacion_con_bitacora",
    args_schema=ArgumentosConsultaSiniestro
)
def consultar_estado_reparacion_detallado(
    numero_siniestro: str,
    incluir_bitacora: bool = False
) -> str:
    """Consulta el estado actual de la reparación de un vehículo en el taller, 
    con la opción de incluir su bitácora técnica completa."""
    
    siniestro = TALLERES_DB.get(numero_siniestro.strip().upper())
    if siniestro is None:
        return f"No se encontró ningún registro de taller para el siniestro {numero_siniestro}."
    
    if not incluir_bitacora:
        return siniestro["actual"]
    
    bitacora_texto = ", ".join(siniestro["bitacora"])
    return f"{siniestro['actual']} (Bitácora técnica: {bitacora_texto})"


@tool
def calcular_presupuesto_adicional(horas_mano_obra: float, costo_repuestos: float) -> str:
    """Calcula el presupuesto total estimado sumando las horas de mano de obra 
    (valorizadas a $35,000 la hora) y el costo neto de los repuestos mecánicos."""
    total = (horas_mano_obra * 35000) + costo_repuestos
    return f"El presupuesto adicional calculado es de ${total:,.2f}."


# --- Bloque 2: Ensamblaje del agente y ejecutor ---
herramientas = [
    consultar_estado_reparacion_detallado,
    calcular_presupuesto_adicional,
]

prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente operativo experto en coordinación de talleres y siniestros automotrices. "
        "Ayuda a los asegurados utilizando las herramientas disponibles estrictamente cuando las necesites.",
    ),
    MessagesPlaceholder("chat_history"),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent=agente,
    tools=herramientas,
    verbose=True,
    return_intermediate_steps=True,
)


if __name__ == "__main__":
    # Historial de conversación explícito en memoria
    chat_history = []

    print("--- TURNO 1: Consulta inicial con bitácora ---")
    entrada_1 = "¿Cuál es el estado de reparación del siniestro SIN88888, incluyendo su bitácora técnica?"
    
    res_1 = ejecutor_agente.invoke({
        "entrada": entrada_1,
        "chat_history": chat_history
    })
    
    print("Respuesta 1:", res_1["output"])

    # Actualizamos el historial de forma limpia con los objetos estándar de LangChain
    chat_history.append(HumanMessage(content=entrada_1))
    chat_history.append(AIMessage(content=res_1["output"]))

    print("\n--- TURNO 2: Pregunta contextual usando la memoria ---")
    entrada_2 = "¿Ya fue entregado ese mismo vehículo?"
    
    res_2 = ejecutor_agente.invoke({
        "entrada": entrada_2,
        "chat_history": chat_history
    })
    
    print("Respuesta 2:", res_2["output"])




    """
=============================================================================
REGISTRO DE APRENDIZAJE Y NOTA TÉCNICA (A CONSIDERAR A FUTURO):
=============================================================================
- Error anterior: 
  'ValueError: Message dict must contain 'role' and 'content' keys' 
  generado al utilizar 'RunnableWithMessageHistory' combinado con 'langchain-google-genai'.

- Causa raíz:
  Las versiones actuales de los adaptadores de Gemini inyectan metadatos internos 
  complejos en los mensajes de respuesta (campos adicionales como 'extras', 'index', etc.). 
  Al delegar la memoria en el manejador automático predeterminado, dichos metadatos 
  se serializan incorrectamente. En el siguiente turno, al intentar reinyectar el historial, 
  el formateador de mensajes de LangChain falla porque espera diccionarios limpios 
  con claves estrictas de 'role' y 'content'.

- Solución aplicada:
  Se eliminó la dependencia de 'RunnableWithMessageHistory' y se optó por un manejo 
  explícito del historial mediante una lista nativa (`chat_history = []`). 
  Se anexan manualmente objetos de clase estándar de LangChain (`HumanMessage` y `AIMessage`) 
  después de cada invocación, garantizando una compatibilidad total, control transparente 
  y evitando la corrupción de metadatos de Gemini en conversaciones multiturno.
=============================================================================
"""