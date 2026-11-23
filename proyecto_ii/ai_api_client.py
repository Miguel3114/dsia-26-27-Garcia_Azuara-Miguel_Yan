import logging
import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ai_api_client")

DEFAULT_HF_MODEL = "openai/gpt-oss-20b"
DEFAULT_NVIDIA_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"


@dataclass
class AIResponse:
    provider: str
    text: str


class AIClientError(RuntimeError):
    """Error controlado del borde de IA."""


def complete(provider: str, prompt: str, model: str | None = None) -> AIResponse:
    """Ejecuta un resumen mock, chat_completion de Hugging Face o Nemotron de NVIDIA."""
    provider = provider.lower().strip()
    if provider == "mock":
        return AIResponse(provider="mock", text="[mock] Resumen generado sin IA externa")

    messages = [{"role": "user", "content": prompt}]
    if provider == "hf":
        token = os.getenv("HF_TOKEN")
        if not token:
            raise AIClientError("Falta HF_TOKEN en el entorno")
        from huggingface_hub import InferenceClient
        client = InferenceClient(api_key=token, provider="auto", timeout=15)
        chosen = model or os.getenv("HF_MODEL", DEFAULT_HF_MODEL)
        call = lambda: client.chat_completion(messages=messages, model=chosen, max_tokens=200)
    elif provider == "nvidia":
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise AIClientError("Falta NVIDIA_API_KEY en el entorno")
        from openai import OpenAI
        # API de NVIDIA compatible con OpenAI. max_retries=0: el reintento es el del bucle de abajo.
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=api_key, timeout=60, max_retries=0)
        chosen = model or os.getenv("NVIDIA_MODEL", DEFAULT_NVIDIA_MODEL)
        call = lambda: client.chat.completions.create(
            model=chosen,
            messages=messages,
            max_tokens=512,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},  # sin razonamiento
        )
    else:
        raise AIClientError(f"Proveedor no soportado: {provider}")

    for attempt in range(2):
        try:
            result = call()
            return AIResponse(provider=provider, text=result.choices[0].message.content or "")
        except Exception as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            # "Timeout" en el nombre cubre openai.APITimeoutError, que no hereda de TimeoutError.
            transient = isinstance(exc, TimeoutError) or "Timeout" in type(exc).__name__ or status in (429, 502, 503, 504)
            if transient and attempt == 0:
                logger.warning("%s_retry attempt=1 status=%s", provider, status)
                time.sleep(0.2)
                continue
            if status == 402:
                raise AIClientError(f"{provider.upper()} 402: no hay créditos disponibles") from exc
            raise AIClientError(f"Error en {provider} ({status or type(exc).__name__})") from exc

    raise AIClientError(f"Error en {provider}")
