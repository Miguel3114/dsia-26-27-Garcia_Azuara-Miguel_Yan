import pandas as pd


def total_passengers(frame: pd.DataFrame) -> float:
    """Calcula el número total de viajeros"""

    return float(frame["passengers"].sum())


def average_passengers(frame: pd.DataFrame) -> float:
    """Calcula la media de viajeros por línea, día y franja"""

    return float(frame["passengers"].mean())


def passengers_by_line(frame: pd.DataFrame) -> pd.Series:
    """Calcula el total de viajeros por línea, de mayor a menor"""

    return (
        frame.groupby("line")["passengers"]
        .sum()
        .sort_values(ascending=False)
    )


def peak_time_slot(frame: pd.DataFrame) -> str:
    """Devuelve la franja horaria con más viajeros"""

    return str(frame.groupby("time_slot")["passengers"].sum().idxmax())
