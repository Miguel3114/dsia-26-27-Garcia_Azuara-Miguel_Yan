
import pandas as pd
import pytest

from weather_app.validator import ValidationError, validate


@pytest.fixture
def weather_mini():
    return pd.DataFrame({
        "datetime": [
            "2025-01-01",
            "2025-01-02",
            "fecha_invalida",
        ],
        "temperature": [10, 15, 20],
        "humidity": [50, 120, 60],
        "pressure": [1010, 1015, 1020],
        "cloud_cover": [20, 30, 40],
        "precipitation": [0, 1, 0],
        "wind_speed": [5, 10, 15],
    })


def test_validate_filas(weather_mini):
    validas, invalidas = validate(weather_mini)

    assert len(validas) == 1
    assert len(invalidas) == 2


def test_validate_columnas_obligatorias(weather_mini):
    frame = weather_mini.drop(columns=["pressure"])

    with pytest.raises(ValidationError):
        validate(frame)


@pytest.mark.parametrize(
    "humidity,expected",
    [
        (-1, 0),
        (0, 1),
        (100, 1),
        (101, 0),
        (None, 0),
    ],
)
def test_validate_humidity(weather_mini, humidity, expected):
    frame = weather_mini.iloc[[0]].copy()
    frame["humidity"] = humidity

    validas, invalidas = validate(frame)

    assert len(validas) == expected
    assert len(invalidas) == 1 - expected


def test_validate_precipitation(weather_mini):
    frame = weather_mini.iloc[[0]].copy()
    frame["precipitation"] = -1

    validas, invalidas = validate(frame)

    assert len(validas) == 0
    assert len(invalidas) == 1
