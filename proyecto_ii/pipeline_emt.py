import argparse
import json
import logging
from pathlib import Path

import pandas as pd

from proyecto_i.emt_app.validator import ValidationError, validate


def setup_logging(log_file: Path) -> logging.Logger:
    """Configura el mismo formato de log en consola y fichero."""
    logger = logging.getLogger("pipeline_emt")
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        handler.close()
    logger.setLevel(logging.INFO)
    logger.propagate = False
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    log_file.parent.mkdir(parents=True, exist_ok=True)
    for handler in (logging.StreamHandler(), logging.FileHandler(log_file, mode="w", encoding="utf-8")):
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    return logger


def load(path: Path, logger: logging.Logger) -> pd.DataFrame:
    """Lee un CSV; la validación de columnas se hace en transform."""
    logger.info("load path=%s", path)
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_csv(path, dtype={"line": str, "time_slot": str})


def transform(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Separa filas válidas sin tocar disco ni red (función pura)."""
    valid, invalid = validate(frame) 
    report = {
        "rows_in": int(len(frame)),
        "rows_out": int(len(valid)),
        "rows_dropped": int(len(invalid)),
        "error_rate": float(len(invalid) / len(frame)) if len(frame) else 1.0,
        "lines": int(valid["line"].nunique()),
        "date_start": str(valid["date"].min().date()) if len(valid) else None,
        "date_end": str(valid["date"].max().date()) if len(valid) else None,
        "passengers_total": int(valid["passengers"].sum()),
    }
    return valid, report


def save(clean: pd.DataFrame, report: dict, out_dir: Path, logger: logging.Logger) -> None:
    """Guarda clean.csv y metrics.json (sobrescribe en cada ejecución)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    clean.to_csv(out_dir / "clean.csv", index=False, date_format="%Y-%m-%d")
    (out_dir / "metrics.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info("save rows_out=%s", report["rows_out"])


def main(argv: list[str] | None = None) -> int:
    """Exit 0=correcto, 1=gate de calidad, 2=entrada inválida."""
    parser = argparse.ArgumentParser(description="Pipeline de demanda EMT")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--max-error-rate", type=float, default=0.05)
    args = parser.parse_args(argv)
    logger = setup_logging(args.output_dir / "run.log")
    try:
        if not 0 <= args.max_error_rate <= 1:
            raise ValueError("max-error-rate debe estar entre 0 y 1")
        frame = load(args.input, logger)
        clean, report = transform(frame)
    except (FileNotFoundError, pd.errors.ParserError, pd.errors.EmptyDataError, ValueError, ValidationError) as exc:
        logger.error("invalid_input error_type=%s", type(exc).__name__)
        return 2

    if report["error_rate"] > args.max_error_rate or clean.empty:
        logger.error("quality_gate_failed error_rate=%.3f", report["error_rate"])
        (args.output_dir / "metrics.json").write_text(
            json.dumps({**report, "status": "failed"}, indent=2), encoding="utf-8"
        )
        (args.output_dir / "clean.csv").unlink(missing_ok=True)
        return 1

    save(clean, report, args.output_dir, logger)
    logger.info("pipeline_ok rows_in=%d rows_out=%d", report["rows_in"], report["rows_out"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
