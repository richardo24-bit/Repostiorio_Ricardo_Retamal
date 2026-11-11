from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda
from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
    construir_cadena_queja_segura,
    procesar_mensaje_seguro,
)


def test_clasificacion_normaliza_antes_de_comparar():
    """Valida que la normalización limpie espacios y mayúsculas."""
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Queja \n")
    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"mensaje": "algo salió mal"}
    )
    assert resultado == "queja"


def test_enrutamiento_va_a_cadena_queja():
    """Verifica que el enrutamiento dirija correctamente a la rama de quejas."""
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "queja"
    
    # Usamos RunnableLambda en lugar de un MagicMock suelto para la ruta
    cadena_queja_falsa = RunnableLambda(lambda x: "respuesta empática de queja")

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=cadena_queja_falsa,
    )
    resultado = cadena.invoke({"mensaje": "esto no funciona nunca"})
    assert resultado == "respuesta empática de queja"


def test_cadena_queja_usa_fallback_ante_fallo_del_modelo():
    """Confirma que el with_fallbacks ejecute la respuesta genérica si la ruta principal falla."""
    def fallar_a_proposito(x):
        raise ConnectionError("simulado")
        
    cadena_queja_falsa = RunnableLambda(fallar_a_proposito)
    cadena_queja_segura = construir_cadena_queja_segura(cadena_queja_falsa)

    resultado = cadena_queja_segura.invoke(
        {"mensaje": "esto no funciona"}
    )
    assert "equipo" in resultado.lower()


def test_procesar_mensaje_seguro_no_propaga_excepciones():
    """Valida que el bloque try/except general capture cualquier fallo en la cadena y responda de forma segura."""
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.side_effect = ConnectionError("simulado")

    cadena_falsa = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
    )

    resultado = procesar_mensaje_seguro(
        cadena_falsa, "mensaje de prueba"
    )
    assert "no pudimos procesar" in resultado.lower()