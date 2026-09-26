import pandas as pd


def total_by_region(frame: pd.DataFrame) -> pd.Series:
    work = frame.copy()

    work["importe"] = (
        work["unidades"] * work["precio_unitario"]
    )

    return (
        work.groupby("region")["importe"]
        .sum()
        .sort_values(ascending=False)
    )