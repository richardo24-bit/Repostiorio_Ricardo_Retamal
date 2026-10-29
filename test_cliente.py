from unittest.mock import patch, Mock
import pytest
import cliente
from cliente import enviar_peticion, con_reintento, registrar_costo, consultar_modelo

# Fixture automático para evitar que el costo acumulado contamine las siguientes pruebas
@pytest.fixture(autouse=True)
def reiniciar_costo_total():
    cliente.costo_total_sesion = 0
    yield

# 1 Pruebas para enviar_peticion (vivida en cliente_api, pero probada mediante su interfaz de red)
def test_enviar_peticion_credencial_invalida():
    respuesta_falsa = Mock(status_code=401)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa):
        with pytest.raises(ValueError):
            enviar_peticion({"pregunta": "test"})

def test_enviar_peticion_limite_de_uso():
    respuesta_falsa = Mock(status_code=429)
    with patch("cliente_api.requests.post", return_value=respuesta_falsa):
        with pytest.raises(TimeoutError):
            enviar_peticion({"pregunta": "test"})

def test_enviar_peticion_exito():
    respuesta_falsa = Mock(status_code=200)
    respuesta_falsa.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": "respuesta simulada"}]
                }
            }
        ],
        "usageMetadata": {"totalTokenCount": 50}
    }
    with patch("cliente_api.requests.post", return_value=respuesta_falsa):
        resultado = enviar_peticion({"pregunta": "test"})
    assert "respuesta simulada" in resultado["candidates"][0]["content"]["parts"][0]["text"]

# 2 Pruebas para con_reintento
def test_con_reintento_agota_intentos():
    def siempre_falla():
        raise TimeoutError("simulado")

    with patch("cliente.time.sleep"):
        with pytest.raises(TimeoutError):
            con_reintento(siempre_falla, intentos=3)

def test_con_reintento_no_reintenta_value_error():
    intentos = {"n": 0}
    def falla_con_value_error():
        intentos["n"] += 1
        raise ValueError("error no retryable")

    with pytest.raises(ValueError):
        con_reintento(falla_con_value_error, intentos=3)
    
    # Valida que solo lo intentó 1 vez y no reintentó
    assert intentos["n"] == 1

# 3 Pruebas para registrar_costo
def test_registrar_costo_acumula():
    respuesta_falsa = {"usageMetadata": {"totalTokenCount": 1000}}
    costo = registrar_costo(respuesta_falsa)

    assert costo == cliente.COSTO_POR_1000_TOKENS
    assert cliente.costo_total_sesion == cliente.COSTO_POR_1000_TOKENS

# 4 Pruebas para consultar_modelo
def test_consultar_modelo_convierte_error():
    error_simulado = TimeoutError("simulado")

    with patch("cliente.con_reintento", side_effect=error_simulado):
        with pytest.raises(RuntimeError):
            consultar_modelo("pregunta de prueba")