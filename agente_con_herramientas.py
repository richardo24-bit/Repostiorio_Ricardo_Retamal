from dotenv import load_dotenv
from langchain_core.tools import tool
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

# 1. Carga de variables de entorno y configuración del modelo gemini-3.5-flash-lite
load_dotenv()
modelo = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


# 2. Definición de herramientas operativas de talleres y siniestros
@tool
def consultar_estado_reparacion(numero_siniestro: str) -> str:
    """Consulta el porcentaje y la fase física actual de la reparación de un vehículo 
    en el taller asignado a partir de su número de siniestro (ej. SIN88888). 
    Usar cuando el usuario pregunta en qué fase de latonería, pintura o armado se encuentra su auto."""
    
    talleres_db = {
        "SIN88888": "El vehículo se encuentra en fase de pintura y pulido final. Estimado de entrega: 3 días hábiles.",
        "SIN11111": "El auto está ingresado en bancada para reparación estructural de chasis.",
        "SIN22222": "Vehículo listo para entrega en taller."
    }
    
    try:
        return talleres_db[numero_siniestro.strip().upper()]
    except KeyError:
        return f"No se registran datos de taller para el siniestro {numero_siniestro}."


@tool
def consultar_emision_presupuesto(numero_siniestro: str) -> str:
    """Verifica si el taller mecánico ya emitió y envió el presupuesto de daños 
    para la aprobación del liquidador o analista de siniestros (ej. SIN88888). 
    Usar cuando el usuario pregunta si el taller ya cotizó los repuestos o mandó el presupuesto."""
    
    presupuestos_db = {
        "SIN88888": "Presupuesto emitido por el taller por un monto de $1,450,000 y aprobado por liquidación el 12 de octubre.",
        "SIN33333": "El taller aún no emite el presupuesto; están pendientes de desmontaje para cotizar repuestos ocultos.",
        "SIN44444": "Presupuesto enviado por el taller hoy por la mañana, pendiente de revisión técnica."
    }
    
    try:
        return presupuestos_db[numero_siniestro.strip().upper()]
    except KeyError:
        return f"No hay registros de presupuesto emitido para el siniestro {numero_siniestro}."


# 3. Ensamblaje del agente con prompt y memoria de pasos
herramientas = [consultar_estado_reparacion, consultar_emision_presupuesto]

prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente especializado en la coordinación de talleres y seguimiento de siniestros automotrices. "
        "Ayuda a los asegurados a consultar el estatus técnico de sus vehículos utilizando estrictamente las herramientas "
        "disponibles cuando el caso lo requiera.",
    ),
    ("human", "{entrada}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agente = create_tool_calling_agent(modelo, herramientas, prompt_agente)

ejecutor_agente = AgentExecutor(
    agent=agente, 
    tools=herramientas, 
    verbose=True, 
    return_intermediate_steps=True
)


if __name__ == "__main__":
    print("--- PRUEBA 1: Estado de Reparación en Taller ---")
    res_1 = ejecutor_agente.invoke({"entrada": "¿Cómo va la reparación de mi auto en el siniestro SIN88888?"})
    print("Respuesta:", res_1["output"])
    
    print("\n--- PRUEBA 2: Consulta de Presupuesto del Taller ---")
    res_2 = ejecutor_agente.invoke({"entrada": "Quisiera saber si el taller ya mandó el presupuesto de daños para el siniestro SIN33333."})
    print("Respuesta:", res_2["output"])
    
    print("\n--- PRUEBA 3: Pregunta general (sin uso de herramientas) ---")
    res_3 = ejecutor_agente.invoke({"entrada": "¿Qué documentos debo llevar al momento de retirar mi vehículo del taller?"})
    print("Respuesta:", res_3["output"])
    print("Pasos intermedios:", res_3["intermediate_steps"])