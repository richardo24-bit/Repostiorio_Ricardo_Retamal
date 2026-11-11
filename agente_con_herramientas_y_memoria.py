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


# --- Bloque 1: Herramientas con Pydantic (args_schema) adaptadas al nuevo dominio ---

class ArgumentosPasosSiniestro(BaseModel):
    etapa_actual: str = Field(
        description="La etapa o momento actual del siniestro, por ejemplo 'denuncio', 'liquidación' o 'reparación'."
    )
    incluir_plazos: bool = Field(
        default=True,
        description="Si es True, incluye los plazos estimados de cada paso."
    )


class ArgumentosDocumentacion(BaseModel):
    tipo_siniestro: str = Field(
        description="Tipo de siniestro o reclamo, por ejemplo 'choque', 'robo' o 'daño parcial'."
    )


@tool(
    "consultar_pasos_a_seguir",
    args_schema=ArgumentosPasosSiniestro
)
def consultar_pasos_a_seguir(etapa_actual: str, incluir_plazos: bool = True) -> str:
    """Explica de forma clara y secuencial los pasos a seguir por el asegurado 
    según la etapa en la que seencuentre su siniestro."""
    
    etapa = etapa_actual.strip().lower()
    
    if "denuncio" in etapa:
        pasos = (
            "1. Presentar la constancia o denuncia policial (si aplica).\n"
            "2. Ingresar el formulario de denuncio de siniestro.\n"
            "3. Esperar la asignación del liquidador o número de expediente."
        )
        plazos = "\nPlazo sugerido para denuncio: dentro de las primeras 48 a 72 horas hábiles." if incluir_plazos else ""
        return f"Pasos para la etapa de denuncio:\n{pasos}{plazos}"
        
    elif "liquidación" in etapa or "peritaje" in etapa:
        pasos = (
            "1. Ingresar el vehículo al taller asignado para la tasación.\n"
            "2. Esperar la emisión del presupuesto de daños.\n"
            "3. Revisión y validación de cobertura y deducibles por el liquidador."
        )
        plazos = "\nPlazo estimado: 3 a 5 días hábiles." if incluir_plazos else ""
        return f"Pasos para la etapa de liquidación:\n{pasos}{plazos}"
        
    else:
        return (
            "Pasos generales del proceso:\n"
            "1. Denuncio del siniestro.\n"
            "2. Evaluación y peritaje en taller.\n"
            "3. Aprobación y ejecución de la reparación o indemnización."
        )


@tool(
    "consultar_documentacion_aprobacion",
    args_schema=ArgumentosDocumentacion
)
def consultar_documentacion_aprobacion(tipo_siniestro: str) -> str:
    """Indica la documentación legal y técnica obligatoria que el asegurado 
    debe presentar o subir al sistema para lograr la aprobación de su siniestro."""
    
    tipo = tipo_siniestro.strip().lower()
    
    if "choque" in tipo or "colisión" in tipo or "daño" in tipo:
        return (
            "Documentación necesaria para aprobación de daños materiales:\n"
            "- Licencia de conducir vigente del conductor al momento del hecho.\n"
            "- Padrón o certificado de inscripción del vehículo.\n"
            "- Relato de los hechos firmado por el asegurado.\n"
            "- Fotografías nítidas de los daños y de la patente."
        )
    elif "robo" in tipo:
        return (
            "Documentación necesaria para siniestros de robo:\n"
            "- Copia original de la constancia o denuncia ante Carabineros/Policía.\n"
            "- Padrón del vehículo y certificado de multas no pagadas.\n"
            "- Entrega de todas las llaves originales del vehículo."
        )
    else:
        return (
            "Documentación estándar solicitada:\n"
            "- Cédula de identidad del asegurado.\n"
            "- Licencia de conducir (si conducía al momento).\n"
            "- Formulario de reclamación de siniestro completado y firmado."
        )


# --- Bloque 2: Ensamblaje del agente y ejecutor ---
herramientas = [
    consultar_pasos_a_seguir,
    consultar_documentacion_aprobacion,
]

prompt_agente = ChatPromptTemplate.from_messages([
    (
        "system",
        "Eres un asistente operativo experto en orientación al cliente y gestión de siniestros. "
        "Ayuda a los asegurados guiándoles sobre los pasos a seguir, la documentación de aprobación, "
        "o atendiendo de forma empática sus consultas y quejas operativas utilizando estrictamente las herramientas cuando se requiera.",
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
    chat_history = []

    print("--- TURNO 1: Consulta sobre pasos a seguir ---")
    entrada_1 = "¿Cuáles son los pasos a seguir justo después de realizar el denuncio de mi choque?"
    res_1 = ejecutor_agente.invoke({
        "entrada": entrada_1,
        "chat_history": chat_history
    })
    print("Respuesta 1:", res_1["output"])
    
    chat_history.append(HumanMessage(content=entrada_1))
    chat_history.append(AIMessage(content=res_1["output"]))

    print("\n--- TURNO 2: Consulta sobre documentación contextual con memoria ---")
    entrada_2 = "¿Qué documentos exactos necesito presentar para que me aprueben este caso?"
    res_2 = ejecutor_agente.invoke({
        "entrada": entrada_2,
        "chat_history": chat_history
    })
    print("Respuesta 2:", res_2["output"])

    chat_history.append(HumanMessage(content=entrada_2))
    chat_history.append(AIMessage(content=res_2["output"]))

    print("\n--- TURNO 3: Atención de queja o consulta operativa ---")
    entrada_3 = "Me parece inaceptable que los plazos de peritaje estén demorando tanto tiempo, ¿pueden hacer algo?"
    res_3 = ejecutor_agente.invoke({
        "entrada": entrada_3,
        "chat_history": chat_history
    })
    print("Respuesta 3:", res_3["output"])