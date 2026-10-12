import pandas as pd


def average_temperature(frame: pd.DataFrame) -> float:
    """Calcula la temperatura media"""

    return float(frame["temperature"].mean())


def average_humidity(frame: pd.DataFrame) -> float:
    """Calcula la humedad media"""

    return float(frame["humidity"].mean())


def total_precipitation(frame: pd.DataFrame) -> float:
    """Calcula la precipitación total"""

    return float(frame["precipitation"].sum())


def max_wind_speed(frame: pd.DataFrame) -> float:
    """Calcula la velocidad máxima del viento"""

    return float(frame["wind_speed"].max())