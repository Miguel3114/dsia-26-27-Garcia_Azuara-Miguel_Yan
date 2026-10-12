import pytest

from ventas_app.loader import CsvSalesRepository, DataLoadError


def test_load_csv_correcto(tmp_path):
    path = tmp_path / "ventas.csv"
    path.write_text(
        "region,producto,unidades,precio_unitario\n"
        "Norte,A,2,10\n",
        encoding="utf-8",
    )

    repo = CsvSalesRepository(path)
    frame = repo.load()

    assert len(frame) == 1
    assert frame["region"].iloc[0] == "Norte"
    assert frame["unidades"].iloc[0] == 2


def test_load_csv_inexistente(tmp_path):
    path = tmp_path / "no_existe.csv"

    repo = CsvSalesRepository(path)

    with pytest.raises(DataLoadError):
        repo.load()
