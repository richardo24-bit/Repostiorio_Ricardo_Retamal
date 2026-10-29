import pytest
from pipeline_texto import limpiar_texto, tokenizar, procesar_texto

def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]

def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto("¡¡¡...!!!")
    assert resultado == []

def test_limpiar_texto_maneja_tipos_invalidos():
    # Verifica que un argumento no string no rompa la ejecución
    assert limpiar_texto(None) == "" # type: ignore