import argparse
from pathlib import Path

from seoul_bikes.metrics import (
    total_rentals,
    average_rentals_by_season,
    average_rentals_by_hour,
    average_rentals_by_holiday,
)
from seoul_bikes.validator import ValidationError, validate
from seoul_bikes.loader import (
    CsvBikeRepository,
    DataLoadError,
    BikeRepository,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Procesamiento de alquileres de bicicletas de Seúl"
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

    repo: BikeRepository = CsvBikeRepository(input_path)

    try:
        frame = repo.load()
        valid_rows, invalid_rows = validate(frame)

    except (DataLoadError, ValidationError) as error:
        print(f"Error: {error}")
        return

    valid_rows.to_csv(output_path, index=False)

    total = total_rentals(valid_rows)
    by_season = average_rentals_by_season(valid_rows)
    by_hour = average_rentals_by_hour(valid_rows)
    by_holiday = average_rentals_by_holiday(valid_rows)

    print(
        f"Registros válidos: {len(valid_rows)} | "
        f"inválidos: {len(invalid_rows)}"
    )

    print(f"Total de bicicletas alquiladas: {total}")

    print("Media de alquileres por estación:")

    for season, average in by_season.items():
        print(f"  {season}: {average:.2f}")

    print("Media de alquileres por hora:")

    for hour, average in by_hour.items():
        print(f"  {hour}:00: {average:.2f}")

    print("Media de alquileres según festivo:")

    for holiday, average in by_holiday.items():
        print(f"  {holiday}: {average:.2f}")


if __name__ == "__main__":
    main()