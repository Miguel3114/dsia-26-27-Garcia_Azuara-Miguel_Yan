import pandas as pd


class ValidationError(Exception):
    """Error cuando faltan columnas obligatorias"""

    pass

# Franjas horarias válidas: H00-H23 (horas del día) y M00-M07 (madrugada
# de los búhos nocturnos, que la EMT publica con prefijo M).
VALID_TIME_SLOTS = (
    {f"H{hour:02d}" for hour in range(24)}
    | {f"M{hour:02d}" for hour in range(8)}
)

def normalize_line(series: pd.Series) -> pd.Series:
    """Normaliza el código de línea: texto sin espacios y 3 dígitos ('1' -> '001')"""

    text = series.astype("string").str.strip()

    is_number = text.str.isdigit().fillna(False)

    return text.where(~is_number, text.str.zfill(3))


def normalize_time_slot(series: pd.Series) -> pd.Series:
    """Normaliza la franja horaria a mayúsculas y sin espacios"""

    return series.astype("string").str.strip().str.upper()


def validate(
    frame: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Separa los registros de demanda válidos e inválidos"""

    required_columns = {
        "date",
        "line",
        "time_slot",
        "passengers",
    }

    missing_columns = required_columns - set(frame.columns)

    if missing_columns:
        raise ValidationError(
            f"Faltan columnas obligatorias: {missing_columns}"
        )

    work = frame.copy()

    work["date"] = pd.to_datetime(
        work["date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    work["line"] = normalize_line(work["line"])

    work["time_slot"] = normalize_time_slot(work["time_slot"])

    work["passengers"] = pd.to_numeric(
        work["passengers"],
        errors="coerce",
    )

    valid_mask = (
        work["date"].notna()
        & work["line"].notna()
        & (work["line"] != "")
        & work["time_slot"].isin(VALID_TIME_SLOTS)
        & work["passengers"].notna()
        & (work["passengers"] >= 0)
        & (work["passengers"] % 1 == 0)
    )

    # Cada (fecha, línea, franja) debe aparecer una sola vez:
    # se conserva el primer registro y el resto se considera inválido.
    duplicated = work.duplicated(
        subset=["date", "line", "time_slot"],
        keep="first",
    )

    valid_mask = (valid_mask & ~duplicated).fillna(False).astype(bool)

    valid_rows = work.loc[valid_mask].copy()
    invalid_rows = work.loc[~valid_mask].copy()

    valid_rows["passengers"] = valid_rows["passengers"].astype(int)

    return valid_rows, invalid_rows
