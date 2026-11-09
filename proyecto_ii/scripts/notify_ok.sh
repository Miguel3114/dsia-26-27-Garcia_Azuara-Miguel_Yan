#!/usr/bin/env bash
set -euo pipefail
mkdir -p proyecto_ii/output
echo "PIPELINE_OK ${1:-$(date -Iseconds)}" > proyecto_ii/output/LAST_OK.txt
