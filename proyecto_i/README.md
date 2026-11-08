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
python -m ventas_app.cli --input datos/ventas.csv --output datos/ventas_limpias.csv
```

## Parte B — Demanda de viajeros EMT Madrid

Procesamiento de la demanda de viajeros de los autobuses de la EMT de Madrid por **línea, día y franja horaria**.

**Fuente:** EMT Madrid, conjunto de datos *Demanda diaria de viajeros de autobús* — https://datos.emtmadrid.es/dataset/demanda-diaria-viajeros-autobus.

**Ficheros:** un CSV por año (2019–2025, descargables en un ZIP) y el CSV del año en curso, que se actualiza cada mes:
`https://datos.emtmadrid.es/dataset/29b27217-429f-44a0-a90a-2db7f13529b6/resource/07622d4b-6c64-43ea-a398-69134d6128bc/download/2026demdialineafranjaanual.csv`

**Licencia / condiciones de uso:** datos abiertos de la EMT; reutilización con atribución de la fuente.

**Fecha de consulta:** 7 de noviembre de 2026.

**Datos:** `Fecha;Linea;Franja;TotalViajeros`, separador `;`. El loader los renombra a `date`, `line`, `time_slot`, `passengers`.

**Validación:**
- Columnas obligatorias (`ValidationError` si falta alguna).
- Fecha con formato `YYYY-MM-DD`.
- Línea normalizada a texto de 3 dígitos (`1` → `001`).
- Franja `H00`–`H23` (horas del día) o `M00`–`M07` (madrugada de los búhos nocturnos, líneas 501–528).
- Viajeros numéricos, enteros y no negativos.
- Sin duplicados por (fecha, línea, franja): se conserva el primero.

**Métricas:**
- Viajeros totales.
- Media de viajeros por línea, día y franja.
- Franja horaria con más viajeros.
- Total de viajeros por línea (las 5 líneas con más demanda).

**Comandos desde la carpeta proyecto_i:**

Ejecución con descarga desde el portal (descarga el CSV de 2026 a `datos/emt_2026_completo.csv`, ignorado por Git, y procesa las fechas pedidas):

```bash
python -m emt_app.cli --start-date 2026-09-01 --end-date 2026-09-02 --output datos/emt_2026_09_muestra.csv
```

Ejecución con CSV ya descargados (`--input` admite un fichero o una carpeta con los CSV anuales):

```bash
python -m emt_app.cli --start-date 2026-09-01 --end-date 2026-09-02 --input datos/emt_2026_completo.csv --output datos/emt_2026_09_local.csv
```

La muestra incluida en el repositorio (`datos/emt_2026_09_muestra.csv`, dos días, 7746 filas) se genera con el primer comando. Los ficheros completos no se suben (más de un millón de filas por año).

**Diseño (DIP):** `cli.py` trabaja contra el protocolo `DemandRepository`, con dos implementaciones intercambiables: `EmtApiRepository` descarga el CSV del portal con `requests` y `CsvEmtRepository` lee CSV locales (un fichero o una carpeta). Ambas filtran el intervalo de fechas.

## Tests

Los tests se realizan con pytest y cubren los módulos `loader`, `validator`, `metrics` y `cli` de ambas partes. Ningún test accede a Internet: las descargas se simulan con `monkeypatch` y los ficheros se crean con `tmp_path`.

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
python -m pytest -q --cov=ventas_app --cov=emt_app --cov-report=term-missing --cov-fail-under=60
```

## Integración continua

GitHub Actions ejecuta automáticamente los tests de ambas partes y comprueba que la cobertura conjunta sea igual o superior al 60 %.

**Workflow:** [ci.yml](../.github/workflows/ci.yml)

**Evidencia:** [Ejecución correcta en GitHub Actions](https://github.com/Miguel3114/dsia-26-27-Garcia_Azuara-Miguel_Yan/actions/runs/42474238559) 
