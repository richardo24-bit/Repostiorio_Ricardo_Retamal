from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from Cadena_3_pasos import construir_cadena

def test_cadena_conecta_los_tres_pasos():
    # Simula las respuestas secuenciales de los 3 pasos de la cadena
    modelo_falso = MagicMock()
    modelo_falso.side_effect = [
        AIMessage(content="punto 1: error 500 en póliza\npunto 2: urgencia de talleres"),
        AIMessage(content="Estimado cliente, revisaremos el error 500 de inmediato."),
        AIMessage(content="Asunto: Solución a incidencia de póliza\n\nEstimado cliente, revisaremos..."),
    ]
    
    cadena = construir_cadena(modelo_falso)
    resultado = cadena.invoke({"texto": "texto de prueba"})
    
    # Verificaciones de la suite
    assert modelo_falso.call_count == 3
    assert "Asunto" in resultado