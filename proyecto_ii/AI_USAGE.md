# AI_USAGE — Proyecto II: Predicción de demanda EMT Madrid

## 1. Componentes de IA del proyecto

- **Modelo local de Machine Learning:** `RandomForestRegressor` de scikit-learn, entrenado con la demanda de viajeros de EMT Madrid. Estima los viajeros por fecha, línea y franja. Se guarda con `joblib` y no necesita ningún proveedor externo para predecir.
- **Cliente de modelo externo:** `proyecto_ii/ai_api_client.py`, con el contrato `AIResponse(provider, text)` y la función `complete(provider, prompt, model)`. Genera un texto explicativo a partir de un resumen agregado de las predicciones; **no** calcula la demanda.

## 2. Proveedor, tarea y modelo del cliente externo

| Elemento | Configuración |
| --- | --- |
| Proveedor por defecto, tests y CI | `mock` (respuesta sin red ni token) |
| Proveedor real | Hugging Face Inference Providers (`hf`) |
| SDK | `huggingface_hub.InferenceClient` (timeout de 15 s) |
| Tarea | `chat_completion` |
| Modelo del Hub | `openai/gpt-oss-20b` |
| Configuración | `HF_TOKEN` y opcionalmente `HF_MODEL` en `.env`; también `--hf-model` en la CLI |

El prompt se construye en `predict.py` con `make_prompt()`. Incluye el periodo, el número de predicciones y de líneas, el total de viajeros estimados, la franja más demandada y la línea con mayor demanda. No se envía el CSV ni registros individuales.

**Pruebas con el proveedor real (8 de noviembre de 2026):**
- `openai/gpt-oss-20b` → HTTP 402, sin créditos en la cuenta gratuita. Comprobé con `huggingface_hub.whoami` que el token y los permisos eran correctos, así que el error se debe solo a la falta de créditos.
- No he conseguido una respuesta real de Hugging Face. El cliente convierte el 402 en `AIClientError` sin reintentar, y la demo completa funciona con `mock`, como contempla el enunciado.

## 3. Asistentes de IA usados durante el desarrollo

**Herramienta utilizada: Claude (Anthropic)**

Se ha utilizado como apoyo para:

- Analizar la viabilidad del dataset candidato (EMT).
- Adaptar el código del proyecto i del dominio de Open Meteo a la demanda de EMT.
- Revisar el pipeline y el procesamiento e inferencia.
- Pruebas automatizadas.
- Resolver errores y documentación.

**Qué acepté:** la reutilización de `EmtApiRepository`/`CsvEmtRepository` en la ingesta, la estructura `load/transform/save` con el umbral de calidad y el cliente con `mock` por defecto. Revisé y ejecuté el código antes de incorporarlo.