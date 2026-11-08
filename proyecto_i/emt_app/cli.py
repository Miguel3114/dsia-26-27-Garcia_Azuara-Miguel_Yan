import argparse
from pathlib import Path

from emt_app.loader import (
    CsvEmtRepository,
    DataLoadError,
    DemandRepository,
    EmtApiRepository,
)
from emt_app.metrics import (
    average_passengers,
    passengers_by_line,
    peak_time_slot,
    total_passengers,
)
from emt_app.validator import (
    ValidationError,
    validate,
)

# Copia completa del CSV descargado del portal (no se sube a Git)
DOWNLOAD_PATH = Path("datos/emt_2026_completo.csv")


def parse_args() -> argparse.Namespace:
    """Obtiene las fechas de consulta y las rutas de entrada y salida"""

    parser = argparse.ArgumentParser(
        description="Procesamiento de la demanda de viajeros de la EMT"
    )

    parser.add_argument(
        "--start-date",
        required=True,
        help="Fecha inicial en formato YYYY-MM-DD",
    )

    parser.add_argument(
        "--end-date",
        required=True,
        help="Fecha final en formato YYYY-MM-DD",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="CSV de salida",
    )

    parser.add_argument(
        "--input",
        default=None,
        help=(
            "CSV o carpeta con CSV ya descargados. "
            "Si no se indica, se descarga el CSV de 2026 del portal de la EMT"
        ),
    )

    return parser.parse_args()


def main() -> None:
    """Ejecuta la carga, validación y análisis de la demanda"""

    args = parse_args()

    output_path = Path(args.output)

    if args.input:
        repo: DemandRepository = CsvEmtRepository(
            Path(args.input),
            args.start_date,
            args.end_date,
        )
    else:
        repo = EmtApiRepository(
            DOWNLOAD_PATH,
            args.start_date,
            args.end_date,
        )

    try:
        frame = repo.load()

        valid_rows, invalid_rows = validate(frame)

    except (DataLoadError, ValidationError, ValueError) as error:
        print(f"Error: {error}")
        return

    valid_rows.to_csv(
        output_path,
        index=False,
    )

    print(
        f"Registros válidos: {len(valid_rows)} | "
        f"inválidos: {len(invalid_rows)}"
    )

    if valid_rows.empty:
        return

    total = total_passengers(valid_rows)
    average = average_passengers(valid_rows)
    peak = peak_time_slot(valid_rows)
    top_lines = passengers_by_line(valid_rows).head(5)

    print(f"Viajeros totales: {total:.0f}")
    print(f"Media por línea, día y franja: {average:.2f}")
    print(f"Franja con más viajeros: {peak}")
    print("Líneas con más viajeros:")

    for line, passengers in top_lines.items():
        print(f"  {line}: {passengers:.0f}")


if __name__ == "__main__":
    main()
