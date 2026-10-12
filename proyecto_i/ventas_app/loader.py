from pathlib import Path
from typing import Protocol

import pandas as pd


class DataLoadError(Exception):
    """Error al cargar los datos de ventas"""

    pass


class SalesRepository(Protocol):
    """Define el contrato para cargar datos de ventas"""

    def load(self) -> pd.DataFrame:
        """Devuelve los datos de ventas en un DataFrame"""

        ...


class CsvSalesRepository:
    """Carga datos de ventas desde un archivo CSV"""

    def __init__(self, path: Path) -> None:
        """Inicializa la ruta del archivo CSV"""

        self.path = path

    def load(self) -> pd.DataFrame:
        """Lee el archivo CSV y devuelve los datos de ventas"""
        
        if not self.path.exists():
            raise DataLoadError(f"No existe el fichero: {self.path}")

        return pd.read_csv(self.path)