import logging
import os
import time
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("ai_api_client")

DEFAULT_HF_MODEL = "openai/gpt-oss-20b"


@dataclass
class AIResponse:
    provider: str
    text: str


class AIClientError(RuntimeError):
    """Error controlado del borde de IA."""


def complete(provider: str, prompt: str, model: str | None = None) -> AIResponse:
    """Ejecuta un resumen mock o chat_completion de Hugging Face."""
    provider = provider.lower().strip()
    if provider == "mock":
        return AIResponse(provider="mock", text="[mock] Resumen generado sin IA externa")
    if provider != "hf":
        raise AIClientError(f"Proveedor no soportado: {provider}")

    token = os.getenv("HF_TOKEN")
    if not token:
        raise AIClientError("Falta HF_TOKEN en el entorno")

    from huggingface_hub import InferenceClient
    client = InferenceClient(api_key=token, provider="auto", timeout=15)
    chosen = model or os.getenv("HF_MODEL", DEFAULT_HF_MODEL)
    for attempt in range(2):
        try:
            result = client.chat_completion(
                messages=[{"role": "user", "content": prompt}],
                model=chosen,
                max_tokens=200,
            )
            return AIResponse(provider="hf", text=result.choices[0].message.content or "")
        except Exception as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            transient = isinstance(exc, TimeoutError) or status in (429, 502, 503, 504)
            if transient and attempt == 0:
                logger.warning("hf_retry attempt=1 status=%s", status)
                time.sleep(0.2)
                continue
            if status == 402:
                raise AIClientError("HF 402: no hay créditos disponibles para Inference Providers") from exc
            raise AIClientError(f"Error en Hugging Face ({status or type(exc).__name__})") from exc

    raise AIClientError("Error en Hugging Face")
