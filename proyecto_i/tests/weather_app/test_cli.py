
from argparse import Namespace

import pandas as pd
import pytest

from weather_app.cli import main
from weather_app.loader import OpenMeteoRepository


@pytest.mark.integration
def test_main(tmp_path, monkeypatch):
    output_path = tmp_path / "weather.csv"

    frame = pd.DataFrame({
        "datetime": ["2025-01-01"],
        "temperature": [10],
        "humidity": [60],
        "pressure": [1010],
        "cloud_cover": [20],
        "precipitation": [0],
        "wind_speed": [5],
    })

    monkeypatch.setattr(
        OpenMeteoRepository,
        "load",
        lambda self: frame,
    )

    monkeypatch.setattr(
        "weather_app.cli.parse_args",
        lambda: Namespace(
            start_date="2025-01-01",
            end_date="2025-01-02",
            output=str(output_path),
        ),
    )

    main()

    assert output_path.exists()

    resultado = pd.read_csv(output_path)

    assert len(resultado) == 1
    assert resultado["temperature"].iloc[0] == 10
