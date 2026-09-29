import pandas as pd


class ValidationError(Exception):
    pass


def validate(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required_columns = {
        "date",
        "rented_bike_count",
        "hour",
        "temperature",
        "humidity",
        "wind_speed",
        "visibility",
        "dew_point_temperature",
        "solar_radiation",
        "rainfall",
        "snowfall",
        "season",
        "holiday",
        "functioning_day",
    }

    missing_columns = required_columns - set(frame.columns)

    if missing_columns:
        raise ValidationError(
            f"Faltan columnas obligatorias: {missing_columns}"
        )

    work = frame.copy()

    numeric_columns = [
        "rented_bike_count",
        "hour",
        "temperature",
        "humidity",
        "wind_speed",
        "visibility",
        "dew_point_temperature",
        "solar_radiation",
        "rainfall",
        "snowfall",
    ]

    for column in numeric_columns:
        work[column] = pd.to_numeric(
            work[column],
            errors="coerce",
        )

    valid_dates = pd.to_datetime(
        work["date"],
        format="%d/%m/%Y",
        errors="coerce",
    ).notna()

    valid_mask = (
        valid_dates
        & work["rented_bike_count"].notna()
        & work["hour"].notna()
        & work["temperature"].notna()
        & work["humidity"].notna()
        & work["wind_speed"].notna()
        & work["visibility"].notna()
        & work["dew_point_temperature"].notna()
        & work["solar_radiation"].notna()
        & work["rainfall"].notna()
        & work["snowfall"].notna()
        & (work["rented_bike_count"] >= 0)
        & work["hour"].between(0, 23)
        & work["humidity"].between(0, 100)
        & (work["wind_speed"] >= 0)
        & (work["visibility"] >= 0)
        & (work["solar_radiation"] >= 0)
        & (work["rainfall"] >= 0)
        & (work["snowfall"] >= 0)
        & work["season"].isin(
            ["Winter", "Spring", "Summer", "Autumn"]
        )
        & work["holiday"].isin(
            ["Holiday", "No Holiday"]
        )
        & work["functioning_day"].isin(
            ["Yes", "No"]
        )
    )

    valid_rows = work.loc[valid_mask].copy()
    invalid_rows = work.loc[~valid_mask].copy()

    return valid_rows, invalid_rows