
import pytest
import requests

from emt_app.loader import CsvEmtRepository, DataLoadError, EmtApiRepository


CSV_EMT = (
    "Fecha;Linea;Franja;TotalViajeros\n"
    "2026-01-01;001;H07;17\n"
    "2026-01-01;001;H08;21\n"
    "2026-01-02;501;M02;15\n"
    "2026-02-01;001;H07;30\n"
)


def test_load_csv_correcto(tmp_path):
    path = tmp_path / "emt.csv"
    path.write_text(CSV_EMT, encoding="utf-8")

    repo = CsvEmtRepository(path, "2026-01-01", "2026-01-31")
    frame = repo.load()

    assert len(frame) == 3
    assert list(frame.columns) == ["date", "line", "time_slot", "passengers"]
    assert frame["line"].iloc[0] == "001"
    assert frame["time_slot"].iloc[2] == "M02"


def test_load_carpeta_de_csv(tmp_path):
    (tmp_path / "2025_dem_linea_franja.csv").write_text(
        CSV_EMT.replace("2026", "2025"), encoding="utf-8"
    )
    (tmp_path / "2026demdialineafranjaanual.csv").write_text(CSV_EMT, encoding="utf-8")
    (tmp_path / "LEEME.txt").write_text("se ignora", encoding="utf-8")

    repo = CsvEmtRepository(tmp_path, "2025-01-01", "2026-01-31")
    frame = repo.load()

    # 4 filas de 2025 + 3 de enero de 2026 (la de febrero queda fuera)
    assert len(frame) == 7


def test_load_csv_inexistente(tmp_path):
    repo = CsvEmtRepository(tmp_path / "no_existe.csv", "2026-01-01", "2026-01-31")

    with pytest.raises(DataLoadError):
        repo.load()


def test_load_carpeta_vacia(tmp_path):
    repo = CsvEmtRepository(tmp_path, "2026-01-01", "2026-01-31")

    with pytest.raises(DataLoadError):
        repo.load()


def test_load_sin_columnas(tmp_path):
    path = tmp_path / "otro.csv"
    path.write_text("a;b\n1;2\n", encoding="utf-8")

    with pytest.raises(DataLoadError):
        CsvEmtRepository(path, "2026-01-01", "2026-01-31").load()


def test_load_sin_datos_en_intervalo(tmp_path):
    path = tmp_path / "emt.csv"
    path.write_text(CSV_EMT, encoding="utf-8")

    with pytest.raises(DataLoadError):
        CsvEmtRepository(path, "2030-01-01", "2030-01-31").load()


def test_descarga_correcta(tmp_path, monkeypatch):
    class FakeResponse:
        content = CSV_EMT.encode("utf-8")

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        requests, "get", lambda *args, **kwargs: FakeResponse()
    )

    download_path = tmp_path / "datos" / "emt_2026.csv"
    repo = EmtApiRepository(download_path, "2026-01-01", "2026-01-31")
    frame = repo.load()

    assert download_path.exists()
    assert len(frame) == 3


def test_descarga_error(tmp_path, monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, "get", fake_get)

    repo = EmtApiRepository(tmp_path / "emt_2026.csv", "2026-01-01", "2026-01-31")

    with pytest.raises(DataLoadError):
        repo.load()
