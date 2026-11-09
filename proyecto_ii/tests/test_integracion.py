import json
import pandas as pd
import pytest

from proyecto_i.emt_app.loader import EmtApiRepository
from proyecto_ii.ingest import main as ingest_main
from proyecto_ii.pipeline_emt import main as pipeline_main
from proyecto_ii.check_metrics import main as metrics_main
from proyecto_ii.train import main as train_main
from proyecto_ii.predict import main as predict_main


@pytest.mark.integration
def test_flujo_completo_sin_red(emt_frame, tmp_path, monkeypatch):
    """Fuente falsa -> clean -> gate -> train joblib -> predict mock."""
    monkeypatch.setattr(EmtApiRepository, "load", lambda self: emt_frame)
    raw = tmp_path / "raw.csv"
    clean = tmp_path / "clean"
    train = tmp_path / "train"
    inference = tmp_path / "inference"
    model = tmp_path / "model.joblib"
    assert ingest_main(["--start-date", "2026-01-01", "--end-date", "2026-03-11", "--output", str(raw)]) == 0
    assert pipeline_main(["--input", str(raw), "--output-dir", str(clean)]) == 0
    assert metrics_main(["--metrics", str(clean / "metrics.json"), "--min-rows-out", "800"]) == 0
    assert train_main(["--input", str(clean / "clean.csv"), "--output-dir", str(train), "--model", str(model)]) == 0
    args = ["--input", str(clean / "clean.csv"), "--model", str(model), "--output-dir", str(inference), "--provider", "mock"]
    assert predict_main(args) == 0
    assert predict_main(args) == 0
    assert len(pd.read_csv(inference / "predictions.csv")) == 840
    assert json.loads((inference / "ai_summary.json").read_text())["provider"] == "mock"
