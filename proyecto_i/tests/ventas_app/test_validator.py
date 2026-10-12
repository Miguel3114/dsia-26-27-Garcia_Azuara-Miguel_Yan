from pathlib import Path

import pandas as pd
import pytest

from ventas_app.loader import CsvSalesRepository
from ventas_app.validator import ValidationError, validate


@pytest.fixture
def ventas_mini():
    return pd.DataFrame({
        "region": ["Norte", "Sur", "Norte"],
        "producto": ["A", "B", "A"],
        "unidades": [2, None, 5],
        "precio_unitario": [10, 20, -1],
    })


def test_validate_filas_validas_invalidas(ventas_mini):
    validas, invalidas = validate(ventas_mini)

    assert len(validas) == 1
    assert len(invalidas) == 2


def test_validate_no_modifica_original(ventas_mini):
    original = ventas_mini.copy()

    validate(ventas_mini)

    pd.testing.assert_frame_equal(ventas_mini, original)


def test_validate_columnas_obligatorias():
    frame = pd.DataFrame({
        "producto": ["A"],
        "unidades": [2],
        "precio_unitario": [10],
    })

    with pytest.raises(ValidationError):
        validate(frame)


@pytest.mark.parametrize(
    "precio,esperadas_validas",
    [
        (0, 0),
        (-1, 0),
        (1, 1),
    ],
)
def test_validate_precio(precio, esperadas_validas):
    frame = pd.DataFrame({
        "region": ["Norte"],
        "producto": ["A"],
        "unidades": [2],
        "precio_unitario": [precio],
    })

    validas, invalidas = validate(frame)

    assert len(validas) == esperadas_validas
    assert len(invalidas) == 1 - esperadas_validas


@pytest.mark.parametrize("unidades", [0, -1, None, "texto"])
def test_validate_unidades_invalidas(unidades):
    frame = pd.DataFrame({
        "region": ["Norte"],
        "producto": ["A"],
        "unidades": [unidades],
        "precio_unitario": [10],
    })

    validas, invalidas = validate(frame)

    assert len(validas) == 0
    assert len(invalidas) == 1


@pytest.mark.integration
def test_csv_real():
    path = (
        Path(__file__).resolve().parents[2]
        / "datos"
        / "ventas.csv"
    )

    repo = CsvSalesRepository(path)
    frame = repo.load()

    validas, invalidas = validate(frame)

    assert len(validas) == 140
    assert len(invalidas) == 10
