# Proyecto I — Programación avanzada en Python

## Entorno

Python 3.12

Crear el entorno virtual:

```bash
python -m venv .venv
```

Instalar dependencias:

```bash
python -m pip install -r requirements.txt
```

## Parte A — Pipeline de ventas

Procesamiento de datos de ventas mediante carga de CSV, validación de registros y cálculo del importe total por región.

**Dataset:** `datos/ventas.csv`

**Ejecución:**

```bash
python -m ventas_app.cli --input datos/ventas.csv --output ventas_validas.csv
```

## Parte B — Open-Meteo

Procesamiento de datos meteorológicos históricos de Madrid obtenidos mediante la API REST de Open-Meteo.

**Fuente:** https://open-meteo.com/en/docs/historical-weather-api

**Licencia:** CC BY 4.0 (requiere atribución). API gratuita para uso no comercial.

**Condiciones de uso:** https://open-meteo.com/en/terms

**Fecha de consulta:** 5 de octubre de 2026

**Datos:** temperatura, humedad, presión, nubosidad, precipitación y velocidad del viento.

**Validación:** columnas obligatorias, tipos de datos, valores nulos y rangos válidos.

**Métricas:**
- Temperatura media.
- Humedad media.
- Precipitación total.
- Velocidad máxima del viento.

**Ejecución y descarga de datos:**

```bash
python -m weather_app.cli --start-date 2025-01-01 --end-date 2025-12-31 --output datos/madrid_weather_2025.csv
```

## Tests

Los tests se realizan con pytest y cubren los módulos `loader`, `validator`, `metrics` y `cli` de ambas partes.

Ejecutar todos los tests:

```bash
python -m pytest -q
```

Ejecutar únicamente tests sin la marca de integración:

```bash
python -m pytest -q -m "not integration"
```

Comprobar la cobertura mínima del 60 %:

```bash
python -m pytest -q --cov=ventas_app --cov=weather_app --cov-report=term-missing --cov-fail-under=60
```

## Integración continua

GitHub Actions ejecuta automáticamente los tests de ambas partes y comprueba que la cobertura conjunta sea igual o superior al 60 %.

**Workflow:** [ci.yml](../.github/workflows/ci.yml)

**Evidencia:** [Ejecución correcta en GitHub Actions](https://github.com/Miguel3114/dsia-26-27-Garcia_Azuara-Miguel_Yan/actions/runs/38241008288)
