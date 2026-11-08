
import pandas as pd
import pytest

from emt_app.validator import ValidationError, validate


@pytest.fixture
def emt_mini():
    return pd.DataFrame({
        "date": [
            "2026-01-01",
            "2026-01-01",
            "fecha_invalida",
            "2026-01-01",
        ],
        "line": ["001", "1", "027", "501"],
        "time_slot": ["H07", "H07", "H08", "M02"],
        "passengers": ["17", "21", "30", "-5"],
    })


def test_validate_filas(emt_mini):
    validas, invalidas = validate(emt_mini)

    # "1" se normaliza a "001" y duplica la primera fila
    assert len(validas) == 1
    assert len(invalidas) == 3
    assert validas["line"].iloc[0] == "001"


def test_validate_columnas_obligatorias(emt_mini):
    frame = emt_mini.drop(columns=["time_slot"])

    with pytest.raises(ValidationError):
        validate(frame)


@pytest.mark.parametrize(
    "passengers,expected",
    [
        (-1, 0),
        (0, 1),
        (250, 1),
        (2.5, 0),
        (None, 0),
        ("abc", 0),
    ],
)
def test_validate_passengers(emt_mini, passengers, expected):
    frame = emt_mini.iloc[[0]].copy()
    frame["passengers"] = passengers

    validas, invalidas = validate(frame)

    assert len(validas) == expected
    assert len(invalidas) == 1 - expected


@pytest.mark.parametrize(
    "time_slot,expected",
    [
        ("H00", 1),
        ("H23", 1),
        ("m03", 1),
        ("M07", 1),
        ("H24", 0),
        ("M08", 0),
        ("X01", 0),
        ("", 0),
    ],
)
def test_validate_time_slot(emt_mini, time_slot, expected):
    frame = emt_mini.iloc[[0]].copy()
    frame["time_slot"] = time_slot

    validas, invalidas = validate(frame)

    assert len(validas) == expected
    assert len(invalidas) == 1 - expected
