import logging
from langgraph.types import Command
from servicio_rag import HUELLA_PROMPT_ACTIVO, crear_app_supervision, responder

CORREO = "ana.perez@exampejemplo.com"
PREGUNTA = "¿Cuánto plazo tengo para denunciar un siniestro? Mi correo es " + CORREO


def test_1_pipeline_sin_excepciones():
    resultado = responder(PREGUNTA)
    assert resultado["respuesta"].strip(), "el servicio devolvio una respuesta vacia"


def test_2_respuesta_cita_fuente():
    resultado = responder(PREGUNTA)
    assert resultado["fuentes"], "el servicio no devolvio ninguna fuente"
    assert any(
        f in resultado["respuesta"] for f in resultado["fuentes"]
    ), "la respuesta no menciona su fuente"


def test_3_logs_sin_contenido_crudo(caplog):
    with caplog.at_level(logging.DEBUG):
        responder(PREGUNTA)
    texto_logs = " ".join(r.getMessage() + " " + str(r.__dict__) for r in caplog.records)
    assert CORREO not in texto_logs, "un dato sensible aparece en los logs"
    assert PREGUNTA not in texto_logs, "la consulta completa aparece en los logs"


def test_4_supervision_pausa_y_reanuda():
    app = crear_app_supervision()
    config = {"configurable": {"thread_id": "test-gate2"}}
    pausado = app.invoke(
        {"huella_nueva": HUELLA_PROMPT_ACTIVO, "aprobado": False}, config=config
    )
    assert "__interrupt__" in pausado, "el grafo no se detuvo en el punto de supervision"
    final = app.invoke(Command(resume=True), config=config)
    assert "__interrupt__" not in final, "el grafo sigue pausado despues de reanudar"
    assert final["aprobado"] is True, "la decision no quedo registrada"