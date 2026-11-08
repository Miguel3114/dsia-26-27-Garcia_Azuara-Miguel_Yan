# AI usage — Proyecto I (cambio de dataset de la Parte B)

## Resumen

- **Asistente:** Claude (Anthropic), usado en conversación el 7 y 8 de noviembre de 2026.
- **Para qué:** decidir con qué dataset sustituir Open-Meteo en la Parte B, comprobar su viabilidad con datos reales y adaptar el código de `weather_app` al nuevo dominio (`emt_app`).
- **Proveedor de IA dentro del código:** ninguno. El Proyecto I no llama a ninguna API de IA.

## 2. Adaptación del código

**Qué aportó la IA:**
- Propuestas de datasets públicos que pueden ser elegidos para el proyecto.
- Paquete `emt_app` con la misma estructura y nombres que `weather_app` y `ventas_app`: `loader`, `validator`, `metrics`, `cli`.
- Tests de los cuatro módulos.

**Qué revisé y cambié:**
- Elegí el dataset y el problema y contexto del proyecto.
- Pedí que se modificara lo mínimo posible la implementación que ya había hecho de Open-Meteo y que únicamente cambiara lo relacionado con el cambio del dataset.
