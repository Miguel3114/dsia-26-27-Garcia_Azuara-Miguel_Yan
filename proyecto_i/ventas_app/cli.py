import argparse
from pathlib import Path

from ventas_app.metrics import total_by_region
from ventas_app.validator import ValidationError, validate
from ventas_app.loader import (
    CsvSalesRepository,
    DataLoadError,
    SalesRepository,
)

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Procesamiento de ventas"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="CSV de entrada",
    )

    parser.add_argument(
        "--output",
        required=True,
        help="CSV de salida",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    repo: SalesRepository = CsvSalesRepository(input_path)

    try:
        frame = repo.load()
        valid_rows, invalid_rows = validate(frame)

    except (DataLoadError, ValidationError) as error:
        print(f"Error: {error}")
        return

    valid_rows.to_csv(output_path, index=False)

    totals = total_by_region(valid_rows)

    print(
        f"Registros válidos: {len(valid_rows)} | "
        f"inválidos: {len(invalid_rows)}"
    )

    print("Importe por región:")

    for region, total in totals.items():
        print(f"  {region}: {total:.2f}")


if __name__ == "__main__":
    main()