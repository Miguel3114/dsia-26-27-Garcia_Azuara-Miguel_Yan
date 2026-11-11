import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validar métricas de calidad")
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--max-error-rate", type=float, default=0.05)
    parser.add_argument("--min-rows-out", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        report = json.loads(args.metrics.read_text(encoding="utf-8"))
        if not 0 <= args.max_error_rate <= 1 or args.min_rows_out < 1:
            raise ValueError("Umbral inválido")
        if report["error_rate"] > args.max_error_rate or report["rows_out"] < args.min_rows_out:
            print("KO: no se cumplen los umbrales de calidad")
            return 1
        print("OK: datos válidos para entrenar")
        return 0
    except (OSError, ValueError, KeyError):
        print("ERROR: metrics.json inexistente o no válido")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
