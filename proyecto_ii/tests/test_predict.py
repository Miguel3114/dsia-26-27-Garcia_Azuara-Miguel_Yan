import json
import pandas as pd
from proyecto_ii.predict import main, make_prompt, predict
from proyecto_ii.train import save_model, train_model, transform


def test_predict_modelo_local(emt_frame):
    model, profiles, _ = train_model(transform(emt_frame))
    predicted = predict(emt_frame, model, profiles)
    assert len(predicted) == len(emt_frame)
    assert {"predicted_passengers", "baseline_passengers", "passengers"} <= set(predicted.columns)
    prompt = make_prompt(predicted)
    assert "Viajeros estimados" in prompt
    assert "001;" not in prompt


def test_predict_fechas_futuras_sin_viajeros(emt_frame):
    model, profiles, _ = train_model(transform(emt_frame))
    future = pd.DataFrame({
        "date": ["2026-11-10", "2026-11-10", "2026-11-10"],
        "line": ["027", "027", "999"],          # 999: línea desconocida
        "time_slot": ["H08", "M02", "H08"],
    })
    predicted = predict(future, model, profiles)
    assert len(predicted) == 2
    assert "passengers" not in predicted.columns
    assert (predicted["predicted_passengers"] > 0).all()


def test_predict_cli_mock(emt_frame, tmp_path):
    model, profiles, _ = train_model(transform(emt_frame))
    model_path = tmp_path / "model.joblib"
    save_model(model, profiles, model_path)
    csv = tmp_path / "clean.csv"
    emt_frame.to_csv(csv, index=False)
    out = tmp_path / "out"
    args = ["--input", str(csv), "--model", str(model_path), "--output-dir", str(out), "--provider", "mock"]
    assert main(args) == 0
    assert main(args) == 0  # idempotencia
    assert len(pd.read_csv(out / "predictions.csv")) == len(emt_frame)
    assert json.loads((out / "ai_summary.json").read_text())["provider"] == "mock"
    report = json.loads((out / "metrics.json").read_text())
    assert report["rows_skipped"] == 0
    assert {"mae", "baseline_mae"} <= report.keys()
    assert (out / "run.log").exists()


def test_predict_fallo_modelo(emt_frame, tmp_path):
    csv = tmp_path / "data.csv"
    emt_frame.to_csv(csv, index=False)
    assert main(["--input", str(csv), "--model", str(tmp_path / "missing.joblib"), "--output-dir", str(tmp_path / "out")]) == 2


def test_predict_proveedor_falla(emt_frame, tmp_path, monkeypatch):
    from proyecto_ii.ai_api_client import AIClientError
    model, profiles, _ = train_model(transform(emt_frame))
    model_path = tmp_path / "model.joblib"
    save_model(model, profiles, model_path)
    csv = tmp_path / "data.csv"
    emt_frame.to_csv(csv, index=False)
    def fail(*args, **kwargs):
        raise AIClientError("HF 402: sin créditos")
    monkeypatch.setattr("proyecto_ii.predict.complete", fail)
    out = tmp_path / "out"
    assert main(["--input", str(csv), "--model", str(model_path), "--output-dir", str(out), "--provider", "hf"]) == 1
    assert not (out / "predictions.csv").exists()
    assert "sin créditos" in (out / "run.log").read_text(encoding="utf-8")
