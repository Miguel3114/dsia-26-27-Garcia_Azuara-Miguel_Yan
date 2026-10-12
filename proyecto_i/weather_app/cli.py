import argparse
from pathlib import Path

from weather_app.loader import (
    DataLoadError,
    OpenMeteoRepository,
    WeatherRepository,
)
from weather_app.metrics import (
    average_humidity,
    average_temperature,
    max_wind_speed,
    total_precipitation,
)
from weather_app.validator import (
    ValidationError,
    validate,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Procesamiento de datos meteorológicos"
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

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_path = Path(args.output)

    repo: WeatherRepository = OpenMeteoRepository(
        latitude=40.4168,
        longitude=-3.7038,
        start_date=args.start_date,
        end_date=args.end_date,
    )

    try:
        frame = repo.load()

        valid_rows, invalid_rows = validate(frame)

    except (DataLoadError, ValidationError) as error:
        print(f"Error: {error}")
        return

    valid_rows.to_csv(
        output_path,
        index=False,
    )

    temperature = average_temperature(valid_rows)
    humidity = average_humidity(valid_rows)
    precipitation = total_precipitation(valid_rows)
    wind_speed = max_wind_speed(valid_rows)

    print(
        f"Registros válidos: {len(valid_rows)} | "
        f"inválidos: {len(invalid_rows)}"
    )

    print(f"Temperatura media: {temperature:.2f} °C")
    print(f"Humedad media: {humidity:.2f} %")
    print(f"Precipitación total: {precipitation:.2f} mm")
    print(f"Velocidad máxima del viento: {wind_speed:.2f} km/h")


if __name__ == "__main__":
    main()