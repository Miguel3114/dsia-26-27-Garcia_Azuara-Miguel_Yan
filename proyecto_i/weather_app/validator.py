import pandas as pd


class ValidationError(Exception):
    pass


def validate(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:

    required_columns = {
        "datetime",
        "temperature",
        "humidity",
        "pressure",
        "cloud_cover",
        "precipitation",
        "wind_speed",
    }

    missing_columns = required_columns - set(frame.columns)

    if missing_columns:
        raise ValidationError(
            f"Faltan columnas obligatorias: {missing_columns}"
        )

    work = frame.copy()

    numeric_columns = [
        "temperature",
        "humidity",
        "pressure",
        "cloud_cover",
        "precipitation",
        "wind_speed",
    ]

    for column in numeric_columns:
        work[column] = pd.to_numeric(
            work[column],
            errors="coerce",
        )

    work["datetime"] = pd.to_datetime(
        work["datetime"],
        errors="coerce",
    )

    valid_mask = (
        work["datetime"].notna()
        & work["temperature"].notna()
        & work["humidity"].notna()
        & work["pressure"].notna()
        & work["cloud_cover"].notna()
        & work["precipitation"].notna()
        & work["wind_speed"].notna()
        & work["humidity"].between(0, 100)
        & work["cloud_cover"].between(0, 100)
        & (work["pressure"] > 0)
        & (work["precipitation"] >= 0)
        & (work["wind_speed"] >= 0)
    )

    valid_rows = work.loc[valid_mask].copy()
    invalid_rows = work.loc[~valid_mask].copy()

    return valid_rows, invalid_rows