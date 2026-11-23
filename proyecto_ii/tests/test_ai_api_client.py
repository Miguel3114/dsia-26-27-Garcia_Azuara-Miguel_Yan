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


def _chat_response(text):
    return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=text))])


def test_nvidia_sin_clave(monkeypatch):
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    with pytest.raises(AIClientError, match="Falta NVIDIA_API_KEY"):
        complete("nvidia", "Hola")


def test_nvidia_mock_sdk(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-de-prueba")
    monkeypatch.delenv("NVIDIA_MODEL", raising=False)
    calls = []
    class FakeCompletions:
        def create(self, **kwargs):
            calls.append(kwargs)
            return _chat_response("Resumen Nemotron")
    class FakeOpenAI:
        def __init__(self, base_url, api_key, timeout, max_retries):
            assert base_url == "https://integrate.api.nvidia.com/v1"
            assert api_key == "nvapi-de-prueba"
            assert max_retries == 0  # el reintento lo controla el cliente propio
            self.chat = SimpleNamespace(completions=FakeCompletions())
    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)
    response = complete("nvidia", "Hola")
    assert (response.provider, response.text) == ("nvidia", "Resumen Nemotron")
    assert calls[0]["model"] == "nvidia/nemotron-3.5-super-vl-120b-a12b"
    assert calls[0]["extra_body"] == {"chat_template_kwargs": {"enable_thinking": False}}
    assert calls[0]["messages"] == [{"role": "user", "content": "Hola"}]


def _fake_openai(monkeypatch, create):
    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))
    monkeypatch.setattr("openai.OpenAI", FakeOpenAI)


def test_nvidia_402_no_reintenta(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-de-prueba")
    calls = []
    class HTTP402(Exception):
        response = SimpleNamespace(status_code=402)
    def create(**kwargs):
        calls.append(1)
        raise HTTP402("sin créditos")
    _fake_openai(monkeypatch, create)
    with pytest.raises(AIClientError, match="NVIDIA 402"):
        complete("nvidia", "Hola")
    assert len(calls) == 1


def test_nvidia_timeout_reintenta(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-de-prueba")
    monkeypatch.setattr("proyecto_ii.ai_api_client.time.sleep", lambda _: None)
    calls = []
    class APITimeoutError(Exception):
        pass
    def create(**kwargs):
        calls.append(1)
        if len(calls) == 1:
            raise APITimeoutError("lento")
        return _chat_response("OK")
    _fake_openai(monkeypatch, create)
    assert complete("nvidia", "Hola").text == "OK"
    assert len(calls) == 2
