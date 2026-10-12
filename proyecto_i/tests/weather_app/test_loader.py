
import pytest
import requests

from weather_app.loader import DataLoadError, OpenMeteoRepository


@pytest.fixture
def repo():
    return OpenMeteoRepository(
        40.4168, -3.7038, "2025-01-01", "2025-01-02"
    )


def test_load_correcto(repo, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "hourly": {
                    "time": ["2025-01-01T00:00"],
                    "temperature_2m": [10],
                    "relative_humidity_2m": [60],
                    "surface_pressure": [1010],
                    "cloud_cover": [20],
                    "precipitation": [0],
                    "wind_speed_10m": [5],
                }
            }

    monkeypatch.setattr(
        requests, "get", lambda *args, **kwargs: FakeResponse()
    )

    frame = repo.load()

    assert len(frame) == 1
    assert frame["temperature"].iloc[0] == 10
    assert "datetime" in frame.columns


def test_load_error(repo, monkeypatch):
    def fake_get(*args, **kwargs):
        raise requests.ConnectionError()

    monkeypatch.setattr(requests, "get", fake_get)

    with pytest.raises(DataLoadError):
        repo.load()


def test_load_sin_hourly(repo, monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {}

    monkeypatch.setattr(
        requests, "get", lambda *args, **kwargs: FakeResponse()
    )

    with pytest.raises(DataLoadError):
        repo.load()
