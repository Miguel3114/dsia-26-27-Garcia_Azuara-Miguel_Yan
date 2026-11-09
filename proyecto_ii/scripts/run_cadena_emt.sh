#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"

if [ -f "$REPO/.venv/bin/activate" ]; then
    source "$REPO/.venv/bin/activate"
elif [ -f "$REPO/.venv/Scripts/activate" ]; then
    source "$REPO/.venv/Scripts/activate"
fi

# Carpeta con los CSV anuales de la EMT (2019 ... 2026), no versionada.
RAW_DIR="proyecto_ii/data/raw"

echo "== 1/7 descargar CSV 2026 y preparar inferencia =="
# Sin --input descarga el CSV del año en curso a $RAW_DIR (sobrescribe la copia anterior).
python -m proyecto_ii.ingest --start-date 2026-09-01 --end-date 2026-09-30 --download-path "$RAW_DIR/2026demdialineafranjaanual.csv" --output proyecto_ii/data/emt_2026_09.csv
echo "== 2/7 preparar entrenamiento =="
python -m proyecto_ii.ingest --start-date 2024-01-01 --end-date 2026-08-31 --input "$RAW_DIR" --output proyecto_ii/data/emt_train.csv
echo "== 3/7 limpiar y verificar =="
python -m proyecto_ii.pipeline_emt --input proyecto_ii/data/emt_train.csv --output-dir proyecto_ii/output/clean_train --max-error-rate 0.05
python -m proyecto_ii.check_metrics --metrics proyecto_ii/output/clean_train/metrics.json --max-error-rate 0.05 --min-rows-out 7000
echo "== 4/7 entrenar sklearn =="
python -m proyecto_ii.train --input proyecto_ii/output/clean_train/clean.csv --model proyecto_ii/models/demand_model.joblib --output-dir proyecto_ii/output/train
echo "== 5/7 limpiar inferencia =="
python -m proyecto_ii.pipeline_emt --input proyecto_ii/data/emt_2026_09.csv --output-dir proyecto_ii/output/clean_inference --max-error-rate 0.05
echo "== 6/7 predecir y resumir en mock =="
python -m proyecto_ii.predict --input proyecto_ii/output/clean_inference/clean.csv --model proyecto_ii/models/demand_model.joblib --output-dir proyecto_ii/output/inference --provider mock
echo "== 7/7 notificar OK =="
bash proyecto_ii/scripts/notify_ok.sh "$(date +%F)"
echo "Cadena OK"
