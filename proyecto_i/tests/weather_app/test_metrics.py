
import pandas as pd
import pytest

from weather_app.metrics import (
    average_temperature,
    average_humidity,
    total_precipitation,
    max_wind_speed,
)


@pytest.fixture
def weather_mini():
    return pd.DataFrame({
        "temperature": [10, 20],
        "humidity": [40, 60],
        "precipitation": [0, 1.5],
        "wind_speed": [5, 12],
    })


def test_average_temperature(weather_mini):
    assert average_temperature(weather_mini) == 15


def test_average_humidity(weather_mini):
    assert average_humidity(weather_mini) == 50


def test_total_precipitation(weather_mini):
    assert total_precipitation(weather_mini) == 1.5


def test_max_wind_speed(weather_mini):
    assert max_wind_speed(weather_mini) == 12
