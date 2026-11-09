import json
from proyecto_ii.check_metrics import main


def test_check_metrics_gate(tmp_path):
    path = tmp_path / "metrics.json"
    path.write_text(json.dumps({"rows_out": 90, "error_rate": 0.02}), encoding="utf-8")
    args = ["--metrics", str(path), "--max-error-rate", "0.05", "--min-rows-out", "50"]
    assert main(args) == 0
    assert main(args[:-1] + ["100"]) == 1
    assert main(["--metrics", str(tmp_path / "missing.json")]) == 2
