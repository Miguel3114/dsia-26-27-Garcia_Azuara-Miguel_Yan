# AI_USAGE — Proyecto II: Predicción de demanda EMT Madrid

## 1. Componentes de IA del proyecto

- **Modelo local de Machine Learning:** `RandomForestRegressor` de scikit-learn, entrenado con la demanda de viajeros de EMT Madrid. Estima los viajeros por fecha, línea y franja. Se guarda con `joblib` y no necesita ningún proveedor externo para predecir.
- **Cliente de modelo externo:** `proyecto_ii/ai_api_client.py`, con el contrato `AIResponse(provider, text)` y la función `complete(provider, prompt, model)`. Genera un texto explicativo a partir de un resumen agregado de las predicciones; **no** calcula la demanda.

## 2. Proveedor, tarea y modelo del cliente externo
El proveedor por defecto, y el único usado en tests y CI, es `mock` (respuesta sin red ni clave). Hay dos proveedores reales, con el mismo contrato y la misma gestión de errores:

| Elemento | Hugging Face (`hf`) | NVIDIA (`nvidia`) |
| --- | --- | --- |
| Servicio | Hugging Face Inference Providers | build.nvidia.com (API compatible con OpenAI) |
| SDK | `huggingface_hub.InferenceClient` (timeout de 15 s) | `openai.OpenAI` con `base_url=https://integrate.api.nvidia.com/v1` (timeout de 60 s) |
| Tarea | `chat_completion` | `chat.completions`, con el razonamiento desactivado (`enable_thinking: False`) |
| Modelo | `openai/gpt-oss-20b` (Hub) | `nvidia/nemotron-3.5-super-vl-120b-a12b` |
| Configuración | `HF_TOKEN` y opcionalmente `HF_MODEL` en `.env` | `NVIDIA_API_KEY` y opcionalmente `NVIDIA_MODEL` en `.env` |

En los dos casos el modelo también puede cambiarse con `--hf-model` en la CLI.
El prompt se construye en `predict.py` con `make_prompt()`. Incluye el periodo, el número de predicciones y de líneas, el total de viajeros estimados, la franja más demandada y la línea con mayor demanda. No se envía el CSV ni registros individuales.

**Pruebas con el proveedor real (8 de noviembre de 2026):**
- `openai/gpt-oss-20b` → HTTP 402, sin créditos en la cuenta gratuita. Comprobé con `huggingface_hub.whoami` que el token y los permisos eran correctos, así que el error se debe solo a la falta de créditos.
- No he conseguido una respuesta real de Hugging Face. El cliente convierte el 402 en `AIClientError` sin reintentar, y la demo completa funciona con `mock`, como contempla el enunciado.
- Por eso añadí NVIDIA (Nemotron, presentado en el tema 5) como segundo proveedor real, con la API de prueba de build.nvidia.com.

**Prueba con NVIDIA (23 de noviembre de 2026):**
- Comando: `python -m proyecto_ii.predict ... --output-dir proyecto_ii/output/inference_nvidia --provider nvidia`, con `NVIDIA_API_KEY` en `.env`.
- Resultado: exit 0 en unos 8 s, con un resumen en español en `ai_summary.json`.
- Comprobé que las cifras del texto (113.794 predicciones, 236 líneas, 42.335.105 viajeros, franja H14, línea 034) coinciden con `predictions.csv`. El modelo no añadió datos que no estuvieran en el prompt.
- En una prueba anterior, con `max_tokens=300`, la respuesta salió cortada a mitad de frase. Subí el límite a 512, el mismo valor que usa el ejemplo de clase, y la respuesta salió completa.

## 3. Asistentes de IA usados durante el desarrollo

**Herramienta utilizada: Claude (Anthropic)**

Se ha utilizado como apoyo para:

- Analizar la viabilidad del dataset candidato (EMT).
- Adaptar el código del proyecto i del dominio de Open Meteo a la demanda de EMT.
- Revisar el pipeline y el procesamiento e inferencia.
- Pruebas automatizadas.
- Resolver errores y documentación.

**Qué acepté:** la reutilización de `EmtApiRepository`/`CsvEmtRepository` en la ingesta, la estructura `load/transform/save` con el umbral de calidad y el cliente con `mock` por defecto. Revisé y ejecuté el código antes de incorporarlo.