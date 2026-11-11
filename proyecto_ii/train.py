import argparse
import json
import logging
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from proyecto_i.emt_app.validator import normalize_line, normalize_time_slot
from proyecto_ii.pipeline_emt import setup_logging

FEATURES = [
    "service_hour", "day_of_week", "day_type", "is_holiday", "month", "day_of_year",
    "profile_line_slot", "profile_line_slot_day_type",
]
TARGET = "passengers"
# Una línea es regular si tiene datos en al menos 30 días. Los servicios
# especiales (eventos, fiestas) duran 1-3 días. No se exige cobertura diaria:
# hay líneas regulares solo de laborables, solo de fines de semana o que paran en verano.
MIN_LINE_DAYS = 30


# Festivos oficiales en la ciudad de Madrid: 12 de la Comunidad de Madrid + 2 locales
# (San Isidro y la Almudena). Fuentes: calendario laboral de la Comunidad de Madrid
# (Decretos del BOCM) y acuerdos del Pleno del Ayuntamiento.
MADRID_HOLIDAYS = pd.to_datetime([
    # 2024
    "2024-01-01", "2024-01-06", "2024-03-28", "2024-03-29", "2024-05-01", "2024-05-02",
    "2024-05-15", "2024-07-25", "2024-08-15", "2024-10-12", "2024-11-01", "2024-11-09",
    "2024-12-06", "2024-12-25",
    # 2025
    "2025-01-01", "2025-01-06", "2025-04-17", "2025-04-18", "2025-05-01", "2025-05-02",
    "2025-05-15", "2025-07-25", "2025-08-15", "2025-11-01", "2025-11-10", "2025-12-06",
    "2025-12-08", "2025-12-25",
    # 2026
    "2026-01-01", "2026-01-06", "2026-04-02", "2026-04-03", "2026-05-01", "2026-05-02",
    "2026-05-15", "2026-08-15", "2026-10-12", "2026-11-02", "2026-11-09", "2026-12-07",
    "2026-12-08", "2026-12-25",
])


def make_features(frame: pd.DataFrame) -> pd.DataFrame:
    """Normaliza las claves y crea las características de calendario (sin usar el objetivo)."""
    work = frame.copy()
    work["date"] = pd.to_datetime(work["date"])
    work["line"] = normalize_line(work["line"])
    work["time_slot"] = normalize_time_slot(work["time_slot"])
    hour = work["time_slot"].str[1:].astype(int)
    # Hora de servicio: H00-H23 -> 0-23 y madrugada de búhos M00-M07 -> 24-31.
    work["service_hour"] = hour.where(work["time_slot"].str[0] == "H", hour + 24)
    work["day_of_week"] = work["date"].dt.dayofweek
    work["is_holiday"] = work["date"].isin(MADRID_HOLIDAYS).astype(int)
    # Tipo de día: 0 laborable, 1 sábado, 2 domingo o festivo
    work["day_type"] = 0
    work.loc[work["day_of_week"] == 5, "day_type"] = 1
    work.loc[(work["day_of_week"] == 6) | (work["is_holiday"] == 1), "day_type"] = 2
    work["month"] = work["date"].dt.month
    work["day_of_year"] = work["date"].dt.dayofyear
    return work.sort_values(["date", "line", "service_hour"]).reset_index(drop=True)


def transform(frame: pd.DataFrame) -> pd.DataFrame:
    """Crea las características y conserva solo las líneas regulares."""
    work = make_features(frame)
    days_per_line = work.groupby("line")["date"].nunique()
    regular = days_per_line[days_per_line >= MIN_LINE_DAYS].index
    return work.loc[work["line"].isin(regular)].reset_index(drop=True)


def profile_keys(data: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Claves de texto para los perfiles: 'línea_franja' y 'línea_franja_tipodía'."""
    slot_key = data["line"] + "_" + data["time_slot"]
    day_type_key = slot_key + "_" + data["day_type"].astype(str)
    return slot_key, day_type_key


def build_profiles(train: pd.DataFrame) -> dict:
    """Demanda media histórica por línea y franja (y por tipo de día), como diccionarios."""
    slot_key, day_type_key = profile_keys(train)
    return {
        "line_slot": train.groupby(slot_key)[TARGET].mean().to_dict(),
        "line_slot_day_type": train.groupby(day_type_key)[TARGET].mean().to_dict(),
    }


def add_profiles(data: pd.DataFrame, profiles: dict) -> pd.DataFrame:
    """Añade los perfiles históricos con map; descarta combinaciones línea-franja nunca vistas."""
    work = data.copy()
    slot_key, day_type_key = profile_keys(work)
    work["profile_line_slot"] = slot_key.map(profiles["line_slot"])
    # Si esa línea-franja no tiene historia en ese tipo de día, se usa su media general.
    work["profile_line_slot_day_type"] = (
        day_type_key.map(profiles["line_slot_day_type"]).fillna(work["profile_line_slot"])
    )
    return work.dropna(subset=["profile_line_slot"]).reset_index(drop=True)


def train_model(data: pd.DataFrame):
    """Entrena con el 80 % inicial de los días y evalúa en el 20 % final."""
    dates = data["date"].drop_duplicates().sort_values()
    if len(dates) < 10:
        raise ValueError("Se necesitan al menos 10 días de datos")
    split_date = dates.iloc[int(len(dates) * 0.8)]
    train = data.loc[data["date"] < split_date]
    test = data.loc[data["date"] >= split_date]
    profiles = build_profiles(train)
    train = add_profiles(train, profiles)
    test = add_profiles(test, profiles)

    model = RandomForestRegressor(
        n_estimators=100, min_samples_leaf=20, max_samples=min(200_000, len(train)),
        n_jobs=-1, random_state=42,
    )
    model.fit(train[FEATURES], train[TARGET])
    predictions = model.predict(test[FEATURES])
    baseline = test["profile_line_slot_day_type"]
    mae = float(mean_absolute_error(test[TARGET], predictions))
    baseline_mae = float(mean_absolute_error(test[TARGET], baseline))
    report = {
        "model": "RandomForestRegressor",
        "rows_train": int(len(train)),
        "rows_test": int(len(test)),
        "lines": int(train["line"].nunique()),
        "mae": mae,
        "rmse": float(mean_squared_error(test[TARGET], predictions) ** 0.5),
        "r2": float(r2_score(test[TARGET], predictions)),
        "wape": float((test[TARGET] - predictions).abs().sum() / test[TARGET].sum()),
        "baseline": "media histórica por línea, franja y tipo de día (solo train)",
        "baseline_mae": baseline_mae,
        "improvement_vs_baseline": float(1 - mae / baseline_mae) if baseline_mae else 0.0,
        "features": FEATURES,
        "train_start": train["date"].min().date().isoformat(),
        "train_end": train["date"].max().date().isoformat(),
        "test_start": test["date"].min().date().isoformat(),
        "test_end": test["date"].max().date().isoformat(),
    }
    return model, build_profiles(data), report


def save_model(model, profiles: dict, path: Path) -> None:
    """Guarda modelo, orden de variables y perfiles para reproducir la inferencia."""
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURES, "profiles": profiles}, path, compress=3)


def load_model(path: Path):
    """Carga un artefacto joblib de confianza y comprueba sus variables."""
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or bundle.get("features") != FEATURES or "profiles" not in bundle:
        raise ValueError("El modelo tiene un contrato de variables incompatible")
    return bundle["model"], bundle["profiles"]


def main(argv: list[str] | None = None) -> int:
    """CLI reproducible de entrenamiento con logs y métricas."""
    parser = argparse.ArgumentParser(description="Entrenar modelo de demanda de viajeros EMT")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    logger = setup_logging(args.output_dir / "run.log")
    try:
        frame = pd.read_csv(args.input, dtype={"line": str, "time_slot": str})
        data = transform(frame)
        model, profiles, report = train_model(data)
        save_model(model, profiles, args.model)
        (args.output_dir / "metrics.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        logger.info(
            "train_ok rows_train=%d rows_test=%d mae=%.2f baseline_mae=%.2f",
            report["rows_train"], report["rows_test"], report["mae"], report["baseline_mae"],
        )
        return 0
    except (FileNotFoundError, pd.errors.ParserError, pd.errors.EmptyDataError, ValueError, KeyError, TypeError) as exc:
        logger.error("train_failed error_type=%s", type(exc).__name__)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
