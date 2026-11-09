import pandas as pd
from proyecto_i.emt_app.loader import DataLoadError, EmtApiRepository
from proyecto_ii.ingest import main


def test_ingest_sin_red(emt_frame, tmp_path, monkeypatch):
    monkeypatch.setattr(EmtApiRepository, "load", lambda self: emt_frame)
    out = tmp_path / "raw.csv"
    status = main(["--start-date", "2026-01-01", "--end-date", "2026-03-11", "--output", str(out)])
    assert status == 0
    assert len(pd.read_csv(out)) == 840


def test_ingest_fechas_invalidas(tmp_path):
    status = main(["--start-date", "2026-03-05", "--end-date", "2026-01-01", "--output", str(tmp_path / "raw.csv")])
    assert status == 2


def test_ingest_error_fuente(monkeypatch, tmp_path):
    def fail(self):
        raise DataLoadError("Fallo simulado")
    monkeypatch.setattr(EmtApiRepository, "load", fail)
    status = main(["--start-date", "2026-01-01", "--end-date", "2026-01-03", "--output", str(tmp_path / "raw.csv")])
    assert status == 2


def test_ingest_fichero_local(emt_frame, tmp_path):
    source = tmp_path / "emt.csv"
    emt_frame.rename(columns={
        "date": "Fecha", "line": "Linea", "time_slot": "Franja", "passengers": "TotalViajeros",
    }).to_csv(source, sep=";", index=False)
    out = tmp_path / "raw.csv"
    status = main(["--start-date", "2026-01-01", "--end-date", "2026-01-31", "--input", str(source), "--output", str(out)])
    assert status == 0
    assert len(pd.read_csv(out)) == 31 * 12


def test_ingest_carpeta_de_csv(emt_frame, tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()
    original = emt_frame.rename(columns={
        "date": "Fecha", "line": "Linea", "time_slot": "Franja", "passengers": "TotalViajeros",
    })
    original.iloc[:420].to_csv(raw / "2026_parte1.csv", sep=";", index=False)
    original.iloc[420:].to_csv(raw / "2026_parte2.csv", sep=";", index=False)
    out = tmp_path / "raw.csv"
    status = main(["--start-date", "2026-01-01", "--end-date", "2026-12-31", "--input", str(raw), "--output", str(out)])
    assert status == 0
    assert len(pd.read_csv(out)) == 840
