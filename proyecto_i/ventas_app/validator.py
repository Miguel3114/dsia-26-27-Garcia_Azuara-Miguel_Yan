import pandas as pd


class ValidationError(Exception):
    pass


def validate(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required_columns = {
        "region",
        "producto",
        "unidades",
        "precio_unitario",
    }

    missing_columns = required_columns - set(frame.columns)

    if missing_columns:
        raise ValidationError(
            f"Faltan columnas obligatorias: {missing_columns}"
        )

    work = frame.copy()

    work["unidades"] = pd.to_numeric(
        work["unidades"],
        errors="coerce",
    )

    work["precio_unitario"] = pd.to_numeric(
        work["precio_unitario"],
        errors="coerce",
    )

    valid_mask = (
        work["unidades"].notna()
        & work["precio_unitario"].notna()
        & (work["unidades"] > 0)
        & (work["precio_unitario"] > 0)
    )

    valid_rows = work.loc[valid_mask].copy()
    invalid_rows = work.loc[~valid_mask].copy()

    return valid_rows, invalid_rows