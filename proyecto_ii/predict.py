import argparse
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import mean_absolute_error

from proyecto_ii.ai_api_client import AIClientError, DEFAULT_HF_MODEL, complete
from proyecto_ii.pipeline_emt import setup_logging
from proyecto_ii.train import FEATURES, add_profiles, load_model, make_features


def predict(frame: pd.DataFrame, model, profiles: dict) -> pd.DataFrame:
    """Realiza predicciones usando el mismo preprocesado que en train.

    La entrada necesita date, line y time_slot; passengers es opcional
    (si existe, permite comparar predicción y valor real).
    """
    data = add_profiles(make_features(frame), profiles)
    columns = ["date", "line", "time_slot"] + (["passengers"] if "passengers" in data.columns else [])
    result = data[columns].copy()
    result["baseline_passengers"] = data["profile_line_slot_day_type"].round(1)
    result["predicted_passengers"] = model.predict(data[FEATURES]).round(1)
    return result


def make_prompt(predictions: pd.DataFrame) -> str:
    """Resume únicamente agregados: nunca envía el CSV completo a la IA."""
    column = predictions["predicted_passengers"]
    by_slot = predictions.groupby("time_slot")["predicted_passengers"].sum()
    by_line = predictions.groupby("line")["predicted_passengers"].sum()
    return (
        "Explica brevemente en español los resultados de un modelo sklearn que estima "
        "la demanda de viajeros de autobuses EMT de Madrid por línea y franja horaria. "
        "Son estimaciones, no viajeros reales. No inventes datos. "
        f"Periodo: {predictions['date'].min():%Y-%m-%d} a {predictions['date'].max():%Y-%m-%d}. "
        f"Predicciones: {len(column)}. Líneas: {predictions['line'].nunique()}. "
        f"Viajeros estimados en total: {column.sum():.0f}. "
        f"Franja con más demanda: {by_slot.idxmax()}. "
        f"Línea con más demanda: {by_line.idxmax()}."
    )


def main(argv: list[str] | None = None) -> int:
    """CLI con contrato de entrada, artefactos y códigos de salida."""
    parser = argparse.ArgumentParser(description="Predecir viajeros por línea, día y franja")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--provider", choices=["mock", "hf"], default="mock")
    parser.add_argument("--hf-model", default=None)
    args = parser.parse_args(argv)
    logger = setup_logging(args.output_dir / "run.log")

    try:
        frame = pd.read_csv(args.input, dtype={"line": str, "time_slot": str})
        if frame.empty:
            raise ValueError("No hay registros para predecir")
        model, profiles = load_model(args.model)
        predictions = predict(frame, model, profiles)
        if predictions.empty:
            raise ValueError("Ninguna línea/franja de la entrada aparece en el modelo")
        logger.info("predict_start rows_in=%d provider=%s", len(frame), args.provider)
    except (FileNotFoundError, pd.errors.ParserError, pd.errors.EmptyDataError, ValueError, KeyError, TypeError) as exc:
        logger.error("predict_invalid_input error_type=%s", type(exc).__name__)
        return 2

    try:
        response = complete(args.provider, make_prompt(predictions), args.hf_model)
    except AIClientError as exc:
        logger.error("predict_provider_failed provider=%s message=%s", args.provider, exc)
        return 1

    report = {
        "rows_in": int(len(frame)),
        "rows_predicted": int(len(predictions)),
        "rows_skipped": int(len(frame) - len(predictions)),
        "provider": response.provider,
        "total_predicted_passengers": float(predictions["predicted_passengers"].sum()),
    }
    if "passengers" in predictions.columns:
        report["mae"] = float(mean_absolute_error(predictions["passengers"], predictions["predicted_passengers"]))
        report["baseline_mae"] = float(mean_absolute_error(predictions["passengers"], predictions["baseline_passengers"]))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(args.output_dir / "predictions.csv", index=False, date_format="%Y-%m-%d")
    (args.output_dir / "metrics.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (args.output_dir / "ai_summary.json").write_text(
        json.dumps({
            "provider": response.provider,
            "task": "chat_completion",
            "model": (args.hf_model or DEFAULT_HF_MODEL) if response.provider == "hf" else None,
            "text": response.text,
        }, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    logger.info(
        "predict_ok rows_predicted=%d rows_skipped=%d provider=%s",
        report["rows_predicted"], report["rows_skipped"], response.provider,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
