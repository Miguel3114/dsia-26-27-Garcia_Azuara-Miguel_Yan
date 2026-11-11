import json
import pandas as pd
import pytest

from proyecto_i.emt_app.validator import ValidationError
from proyecto_ii.pipeline_emt import main, transform


def test_transform_report_counts(emt_frame):
    emt_frame.loc[0, "passengers"] = -5
    clean, report = transform(emt_frame)
    assert len(clean) == 839
    assert report["rows_in"] == 840
    assert report["rows_dropped"] == 1
    assert report["rows_out"] == 839
    assert report["lines"] == 3


def test_transform_columnas_incorrectas_raises(emt_frame):
    with pytest.raises(ValidationError):
        transform(emt_frame.drop(columns=["passengers"]))


def test_pipeline_guarda_artefactos_idempotentes(emt_frame, tmp_path):
    csv = tmp_path / "data.csv"
    out = tmp_path / "out"
    emt_frame.to_csv(csv, index=False)
    args = ["--input", str(csv), "--output-dir", str(out)]
    assert main(args) == 0
    assert main(args) == 0
    clean = pd.read_csv(out / "clean.csv", dtype={"line": str})
    assert len(clean) == 840
    assert set(clean["line"]) == {"001", "027", "501"}
    assert json.loads((out / "metrics.json").read_text())["rows_out"] == 840
    assert (out / "run.log").exists()


def test_gate_impide_publicacion(emt_frame, tmp_path):
    csv = tmp_path / "bad.csv"
    out = tmp_path / "out"
    emt_frame.loc[0, "time_slot"] = "X99"
    emt_frame.to_csv(csv, index=False)
    args = ["--input", str(csv), "--output-dir", str(out), "--max-error-rate", "0"]
    assert main(args) == 1
    assert not (out / "clean.csv").exists()
    assert json.loads((out / "metrics.json").read_text())["status"] == "failed"


def test_missing_input(tmp_path):
    assert main(["--input", str(tmp_path / "missing.csv"), "--output-dir", str(tmp_path / "out")]) == 2


def test_empty_csv_calidad(tmp_path):
    csv = tmp_path / "empty.csv"
    csv.write_text("date,line,time_slot,passengers\n")
    assert main(["--input", str(csv), "--output-dir", str(tmp_path / "out")]) == 1
