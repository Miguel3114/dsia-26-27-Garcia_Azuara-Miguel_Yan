from typing import Protocol

import pandas as pd
import requests


class DataLoadError(Exception):
    """Error al cargar los datos meteorológicos"""

    pass


class WeatherRepository(Protocol):
    """Define el contrato para cargar datos meteorológicos"""

    def load(self) -> pd.DataFrame:
        """Devuelve los datos meteorológicos en un DataFrame"""

        ...


COLUMN_MAP = {
    "time": "datetime",
    "temperature_2m": "temperature",
    "relative_humidity_2m": "humidity",
    "surface_pressure": "pressure",
    "cloud_cover": "cloud_cover",
    "precipitation": "precipitation",
    "wind_speed_10m": "wind_speed",
}


class OpenMeteoRepository:
    """Obtiene datos meteorológicos desde la API de Open-Meteo"""

    URL = "https://archive-api.open-meteo.com/v1/archive"

    def __init__(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str,
    ) -> None:
        """Inicializa las coordenadas y el intervalo de fechas"""

        self.latitude = latitude
        self.longitude = longitude
        self.start_date = start_date
        self.end_date = end_date

    def load(self) -> pd.DataFrame:
        """Descarga los datos horarios y devuelve un DataFrame"""

        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "surface_pressure",
                "cloud_cover",
                "precipitation",
                "wind_speed_10m",
            ],
            "timezone": "UTC",
        }

        try:
            response = requests.get(
                self.URL,
                params=params,
                timeout=30,
            )

            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:
            raise DataLoadError(
                "No se pudieron obtener los datos de Open-Meteo"
            ) from error

        if "hourly" not in data:
            raise DataLoadError(
                "La respuesta de Open-Meteo no contiene datos horarios"
            )

        frame = pd.DataFrame(data["hourly"])

        return frame.rename(columns=COLUMN_MAP)