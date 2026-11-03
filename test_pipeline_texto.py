import pytest
from pipeline_texto import (
    limpiar_texto,
    tokenizar,
    procesar_texto,
    contar_coincidencias,
    calcular_precision_cobertura_f1,
    resumir_metricas
)

def test_procesar_texto_normaliza_mayusculas_y_puntuacion():
    resultado = procesar_texto("El Cielo, es AZUL!")
    assert resultado == ["el", "cielo", "es", "azul"]

def test_procesar_texto_solo_puntuacion_devuelve_lista_vacia():
    resultado = procesar_texto("¡¡¡...!!!")
    assert resultado == []

def test_limpiar_texto_maneja_tipos_invalidos():
    assert limpiar_texto(None) == ""  # type: ignore

def test_contar_coincidencias_respeta_frecuencias():
    ref = ["el", "gato", "el", "gato"]
    resp = ["el", "gato"]
    # La intersección mínima toma 1 "el" y 1 "gato"
    assert contar_coincidencias(ref, resp) == 2

def test_calcular_precision_cobertura_f1_valores_vacios():
    resultado = calcular_precision_cobertura_f1([], ["token"])
    assert resultado == {"precision": 0.0, "cobertura": 0.0, "f1": 0.0}

def test_resumir_metricas_vacio():
    resultado = resumir_metricas([])
    assert resultado == {
        "precision_promedio": 0.0,
        "cobertura_promedio": 0.0,
        "f1_promedio": 0.0,
    }