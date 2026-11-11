from types import SimpleNamespace
import pytest
from proyecto_ii.ai_api_client import AIClientError, complete


def test_mock_no_necesita_token(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    a = complete("mock", "Hola")
    b = complete("mock", "Hola")
    assert a.provider == "mock"
    assert a.text == b.text


def test_proveedor_desconocido():
    with pytest.raises(AIClientError, match="no soportado"):
        complete("inexistente", "Hola")


def test_hf_sin_token(monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(AIClientError, match="Falta HF_TOKEN"):
        complete("hf", "Hola")


def test_hf_mock_sdk(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "token-de-prueba")
    class FakeHF:
        def __init__(self, api_key, provider, timeout):
            assert api_key == "token-de-prueba"
            assert provider == "auto"
            assert timeout == 15
        def chat_completion(self, messages, model, max_tokens):
            assert model == "org/modelo"
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Correcto"))])
    monkeypatch.setattr("huggingface_hub.InferenceClient", FakeHF)
    assert complete("hf", "Hola", "org/modelo").text == "Correcto"


def test_hf_402_no_reintenta(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "token-de-prueba")
    calls = []
    class HTTP402(Exception):
        response = SimpleNamespace(status_code=402)
    class FakeHF:
        def __init__(self, **kwargs):
            pass
        def chat_completion(self, **kwargs):
            calls.append(1)
            raise HTTP402("privado")
    monkeypatch.setattr("huggingface_hub.InferenceClient", FakeHF)
    with pytest.raises(AIClientError, match="HF 402"):
        complete("hf", "Hola")
    assert len(calls) == 1


def test_hf_503_reintenta(monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "token-de-prueba")
    monkeypatch.setattr("proyecto_ii.ai_api_client.time.sleep", lambda _: None)
    calls = []
    class HTTP503(Exception):
        response = SimpleNamespace(status_code=503)
    class FakeHF:
        def __init__(self, **kwargs):
            pass
        def chat_completion(self, **kwargs):
            calls.append(1)
            if len(calls) == 1:
                raise HTTP503("temporal")
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="OK"))])
    monkeypatch.setattr("huggingface_hub.InferenceClient", FakeHF)
    assert complete("hf", "Hola").text == "OK"
    assert len(calls) == 2
