from unittest.mock import MagicMock
from langchain_core.messages import AIMessage
from enrutamiento import (
    construir_cadena_con_enrutamiento,
    construir_paso_clasificacion,
)


def test_enrutamiento_va_a_cadena_queja():
    """Verifica que el enrutador derive correctamente la entrada hacia la rama de quejas."""
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "queja"
    
    cadena_queja_falsa = MagicMock()
    cadena_queja_falsa.return_value = "respuesta empática de queja"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_queja=cadena_queja_falsa,
    )
    resultado = cadena.invoke({"mensaje": "esto no funciona nunca"})

    assert cadena_queja_falsa.called
    assert resultado == "respuesta empática de queja"


def test_enrutamiento_va_a_cadena_pregunta():
    """Verifica que el enrutador derive correctamente la entrada hacia la rama de preguntas."""
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "pregunta"
    
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta técnica precisa"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "¿cómo cambio mi contraseña?"})

    assert cadena_pregunta_falsa.called
    assert resultado == "respuesta técnica precisa"


def test_clasificacion_normaliza_antes_de_comparar():
    """Valida que el paso de clasificación aplique .strip().lower() correctamente a la salida del modelo."""
    modelo_falso = MagicMock()
    modelo_falso.return_value = AIMessage(content=" Queja \n")

    resultado = construir_paso_clasificacion(modelo_falso).invoke(
        {"mensaje": "algo salió mal"}
    )

    assert resultado == "queja"


def test_enrutamiento_usa_default_ante_categoria_desconocida():
    """Confirma que ante una categoría no contemplada, el sistema recurre a la ruta por defecto."""
    clasificacion_falsa = MagicMock()
    clasificacion_falsa.return_value = "categoria_inventada"
    
    cadena_pregunta_falsa = MagicMock()
    cadena_pregunta_falsa.return_value = "respuesta por defecto"

    cadena = construir_cadena_con_enrutamiento(
        paso_clasificacion=clasificacion_falsa,
        cadena_pregunta=cadena_pregunta_falsa,
    )
    resultado = cadena.invoke({"mensaje": "mensaje ambiguo"})

    assert cadena_pregunta_falsa.called
    assert resultado == "respuesta por defecto"