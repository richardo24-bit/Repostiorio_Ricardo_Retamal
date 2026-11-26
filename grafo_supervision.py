from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command


class EstadoDespliegue(TypedDict):
    huella_nueva: str
    aprobado: bool


def proponer(estado: EstadoDespliegue):
    return {}


def supervisar(estado: EstadoDespliegue):
    decision = interrupt(
        {
            "motivo": "aprobar nueva version de prompt de siniestros en produccion",
            "huella_propuesta": estado["huella_nueva"],
        }
    )
    return {"aprobado": decision}


def aplicar(estado: EstadoDespliegue):
    if estado["aprobado"]:
        print("-> Version", estado["huella_nueva"], "ACTIVADA en produccion")
    else:
        print("-> Version", estado["huella_nueva"], "RECHAZADA, se mantiene la anterior")
    return {}


grafo = StateGraph(EstadoDespliegue)
grafo.add_node("proponer", proponer)
grafo.add_node("supervisar", supervisar)
grafo.add_node("aplicar", aplicar)
grafo.add_edge(START, "proponer")
grafo.add_edge("proponer", "supervisar")
grafo.add_edge("supervisar", "aplicar")
grafo.add_edge("aplicar", END)

app_despliegue = grafo.compile(checkpointer=InMemorySaver())


if __name__ == "__main__":

    
    huella_v2 = "12c03d00eb50"

    # 1. Camino de aprobacion
    print("=== Prueba 1: Aprobacion ===")
    config_1 = {"configurable": {"thread_id": "despliegue-siniestros-1"}}
    res_pausado = app_despliegue.invoke(
        {"huella_nueva": huella_v2, "aprobado": False}, config=config_1
    )
    print("Interrumpido:", "__interrupt__" in res_pausado)
    print("Pendiente:", app_despliegue.get_state(config_1).interrupts[0].value)

    res_aprobado = app_despliegue.invoke(Command(resume=True), config=config_1)
    print("Estado final:", res_aprobado)

    # 2. Camino de rechazo (con otro thread_id para no reusar el hilo terminado)
    print("\n=== Prueba 2: Rechazo ===")
    config_2 = {"configurable": {"thread_id": "despliegue-siniestros-2"}}
    app_despliegue.invoke(
        {"huella_nueva": huella_v2, "aprobado": False}, config=config_2
    )
    res_rechazado = app_despliegue.invoke(Command(resume=False), config=config_2)
    print("Estado final:", res_rechazado)