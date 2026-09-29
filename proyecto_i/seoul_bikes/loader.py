from pathlib import Path
from typing import Protocol

import pandas as pd


class DataLoadError(Exception):
    pass


class BikeRepository(Protocol):
    def load(self) -> pd.DataFrame:
        ...


COLUMN_MAP = {
    "Date": "date",
    "Rented Bike Count": "rented_bike_count",
    "Hour": "hour",
    "Temperature(°C)": "temperature",
    "Humidity(%)": "humidity",
    "Wind speed (m/s)": "wind_speed",
    "Visibility (10m)": "visibility",
    "Dew point temperature(°C)": "dew_point_temperature",
    "Solar Radiation (MJ/m2)": "solar_radiation",
    "Rainfall(mm)": "rainfall",
    "Snowfall (cm)": "snowfall",
    "Seasons": "season",
    "Holiday": "holiday",
    "Functioning Day": "functioning_day",
}


class CsvBikeRepository:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> pd.DataFrame:
        if not self.path.exists():
            raise DataLoadError(f"No existe el fichero: {self.path}")

        frame = pd.read_csv(
            self.path,
            encoding="latin1",
        )

        return frame.rename(columns=COLUMN_MAP)