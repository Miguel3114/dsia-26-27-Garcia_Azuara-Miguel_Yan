from pathlib import Path
from typing import Protocol

import pandas as pd
import requests


class DataLoadError(Exception):
    """Error al cargar los datos de demanda de la EMT"""

    pass


class DemandRepository(Protocol):
    """Define el contrato para cargar datos de demanda de viajeros"""

    def load(self) -> pd.DataFrame:
        """Devuelve los datos de demanda en un DataFrame"""

        ...


EMT_2026_URL = (
    "https://datos.emtmadrid.es/dataset/29b27217-429f-44a0-a90a-2db7f13529b6"
    "/resource/07622d4b-6c64-43ea-a398-69134d6128bc"
    "/download/2026demdialineafranjaanual.csv"
)

COLUMN_MAP = {
    "fecha": "date",
    "linea": "line",
    "franja": "time_slot",
    "totalviajeros": "passengers",
}


def read_emt_csv(path: Path) -> pd.DataFrame:
    """Lee un CSV de la EMT y renombra sus columnas"""

    df = pd.read_csv(path, sep=";", dtype=str)

    df.columns = [column.strip().lower() for column in df.columns]

    missing_columns = set(COLUMN_MAP) - set(df.columns)

    if missing_columns:
        raise DataLoadError(
            f"El CSV no tiene las columnas esperadas: {missing_columns}"
        )

    return df[list(COLUMN_MAP)].rename(columns=COLUMN_MAP)


def filter_dates(
    frame: pd.DataFrame,
    start_date: str,
    end_date: str,
) -> pd.DataFrame:
    """Conserva las filas del intervalo de fechas"""

    dates = pd.to_datetime(
        frame["date"],
        format="%Y-%m-%d",
        errors="coerce",
    )

    in_range = dates.between(pd.Timestamp(start_date), pd.Timestamp(end_date))

    return frame.loc[dates.isna() | in_range]


class CsvEmtRepository:
    """Carga la demanda desde CSV descargados: un fichero o una carpeta con varios"""

    def __init__(self, path: Path, start_date: str, end_date: str) -> None:
        """Inicializa la ruta y el intervalo de fechas"""

        self.path = path
        self.start_date = start_date
        self.end_date = end_date

    def load(self) -> pd.DataFrame:
        """Lee los CSV y devuelve las filas del intervalo"""

        if not self.path.exists():
            raise DataLoadError(f"No existe el fichero o carpeta: {self.path}")

        if self.path.is_dir():
            files = sorted(self.path.glob("*.csv"))
        else:
            files = [self.path]

        if not files:
            raise DataLoadError(f"La carpeta no contiene CSV: {self.path}")

        frames = []

        for file in files:
            try:
                frame = read_emt_csv(file)
            except (pd.errors.ParserError, pd.errors.EmptyDataError) as error:
                raise DataLoadError(f"CSV no válido: {file}") from error

            frames.append(filter_dates(frame, self.start_date, self.end_date))

        frame = pd.concat(frames, ignore_index=True)

        if frame.empty:
            raise DataLoadError(
                "No hay datos de la EMT en el intervalo indicado"
            )

        return frame


class EmtApiRepository:
    """Descarga el CSV del año en curso del portal de la EMT y lo carga"""

    def __init__(
        self,
        download_path: Path,
        start_date: str,
        end_date: str,
        url: str = EMT_2026_URL,
    ) -> None:
        """Inicializa la URL, dónde guardar la descarga y el intervalo de fechas"""

        self.url = url
        self.download_path = download_path
        self.start_date = start_date
        self.end_date = end_date

    def load(self) -> pd.DataFrame:
        """Descarga el CSV (sobrescribe la copia anterior) y devuelve las filas del intervalo"""

        try:
            response = requests.get(self.url, timeout=120)

            response.raise_for_status()

        except requests.RequestException as error:
            raise DataLoadError(
                "No se pudieron obtener los datos de la EMT"
            ) from error

        self.download_path.parent.mkdir(parents=True, exist_ok=True)
        self.download_path.write_bytes(response.content)

        repo = CsvEmtRepository(self.download_path, self.start_date, self.end_date)

        return repo.load()
