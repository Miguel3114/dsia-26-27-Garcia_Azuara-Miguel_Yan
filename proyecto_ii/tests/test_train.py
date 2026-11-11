import json
import pandas as pd
import pytest
from proyecto_ii.train import (
    FEATURES, load_model, main, make_features, save_model, train_model, transform,
)


def test_make_features(emt_frame):
    data = make_features(emt_frame)
    first = data.iloc[0]
    assert first["date"] == pd.Timestamp("2026-01-01")
    assert first["is_holiday"] == 1      # 1 de enero
    assert first["day_type"] == 2        # festivo
    night = data.loc[data["time_slot"] == "M02", "service_hour"].iloc[0]
    assert night == 26                   # madrugada de búhos tras las 23 h


@pytest.mark.parametrize("day,is_holiday,day_type", [
    ("2026-04-03", 1, 2),  
    ("2026-11-02", 1, 2),   
    ("2026-05-02", 1, 2),   
    ("2026-11-03", 0, 0),   
    ("2026-11-07", 0, 1),   
])
def test_festivos_y_tipo_de_dia(day, is_holiday, day_type):
    frame = pd.DataFrame({"date": [day], "line": ["001"], "time_slot": ["H08"], "passengers": [10]})
    row = make_features(frame).iloc[0]
    assert row["is_holiday"] == is_holiday
    assert row["day_type"] == day_type


def test_transform_descarta_servicios_especiales(emt_frame):
    special = pd.DataFrame({
        "date": ["2026-01-10", "2026-01-11"], "line": ["861", "861"],
        "time_slot": ["H20", "H21"], "passengers": [500, 700],
    })
    data = transform(pd.concat([emt_frame, special], ignore_index=True))
    assert "861" not in set(data["line"])
    assert len(data) == 840


def test_transform_conserva_lineas_nuevas(emt_frame):
    # Línea que empieza el día 31 y circula a diario hasta el final (40 días)
    new_line = emt_frame.loc[(emt_frame["line"] == "027") & (emt_frame["date"] >= "2026-01-31")].copy()
    new_line["line"] = "180"
    data = transform(pd.concat([emt_frame, new_line], ignore_index=True))
    assert "180" in set(data["line"])


def test_transform_conserva_lineas_solo_laborables(emt_frame):
    weekdays = emt_frame.loc[
        (emt_frame["line"] == "001") & (pd.to_datetime(emt_frame["date"]).dt.dayofweek < 5)
    ].copy()
    weekdays["line"] = "451"
    data = transform(pd.concat([emt_frame, weekdays], ignore_index=True))
    assert "451" in set(data["line"])


def test_modelo_guardado_conoce_lineas_del_periodo_de_test(emt_frame):
    late = emt_frame.loc[(emt_frame["line"] == "027") & (emt_frame["date"] >= "2026-01-31")].copy()
    late["line"] = "180"
    data = transform(pd.concat([emt_frame, late], ignore_index=True))
    _, profiles, _ = train_model(data)
    assert "180_H08" in profiles["line_slot"]


def test_train_model_metricas(emt_frame):
    data = transform(emt_frame)
    model, profiles, report = train_model(data)
    assert report["rows_train"] > report["rows_test"]
    assert report["train_end"] < report["test_start"]
    assert report["mae"] >= 0
    assert report["rmse"] >= 0
    assert "baseline_mae" in report
    assert set(profiles) == {"line_slot", "line_slot_day_type"}


def test_save_load_model(emt_frame, tmp_path):
    from proyecto_ii.train import add_profiles
    data = transform(emt_frame)
    model, profiles, _ = train_model(data)
    path = tmp_path / "model.joblib"
    save_model(model, profiles, path)
    loaded, loaded_profiles = load_model(path)
    sample = add_profiles(data.iloc[:2], loaded_profiles)[FEATURES]
    assert loaded.predict(sample) == pytest.approx(model.predict(sample))


def test_load_model_contrato_incompatible(tmp_path):
    import joblib
    path = tmp_path / "old.joblib"
    joblib.dump({"model": None, "features": ["temperature"]}, path)
    with pytest.raises(ValueError):
        load_model(path)


def test_too_few_days(emt_frame):
    data = transform(emt_frame)
    with pytest.raises(ValueError):
        train_model(data.loc[data["date"] < "2026-01-05"])


def test_train_cli_modelo_y_metricas(emt_frame, tmp_path):
    csv = tmp_path / "clean.csv"
    model = tmp_path / "model.joblib"
    out = tmp_path / "out"
    emt_frame.to_csv(csv, index=False)
    assert main(["--input", str(csv), "--model", str(model), "--output-dir", str(out)]) == 0
    assert model.exists()
    assert (out / "run.log").exists()
    report = json.loads((out / "metrics.json").read_text())
    assert {"mae", "rmse", "r2", "baseline_mae", "improvement_vs_baseline"} <= report.keys()


def test_train_invalid_input(tmp_path):
    assert main(["--input", str(tmp_path / "missing.csv"), "--model", str(tmp_path / "model.joblib"), "--output-dir", str(tmp_path / "out")]) == 2
