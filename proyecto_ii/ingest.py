import argparse
from pathlib import Path

from proyecto_i.emt_app.loader import CsvEmtRepository, DataLoadError, EmtApiRepository

DOWNLOAD_PATH = Path("proyecto_ii/data/raw/2026demdialineafranjaanual.csv")


def main(argv: list[str] | None = None) -> int:
    """Lee la demanda de la EMT de un intervalo y la guarda en CSV."""
    parser = argparse.ArgumentParser(description="Ingesta de la demanda de viajeros EMT")
    parser.add_argument("--start-date", required=True)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--input", type=Path, default=None,
        help="CSV o carpeta con CSV descargados. Sin --input se descarga el CSV de 2026 del portal",
    )
    parser.add_argument("--download-path", type=Path, default=DOWNLOAD_PATH)
    args = parser.parse_args(argv)

    try:
        from datetime import date
        start = date.fromisoformat(args.start_date)
        end = date.fromisoformat(args.end_date)
        if start > end:
            raise ValueError("La fecha inicial debe ser anterior a la final")
        if args.input:
            repo = CsvEmtRepository(args.input, args.start_date, args.end_date)
        else:
            repo = EmtApiRepository(args.download_path, args.start_date, args.end_date)
        frame = repo.load()
        if frame.empty:
            raise ValueError("La EMT no devolvió registros")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(args.output, index=False)
        print(f"Escrito {len(frame)} registros en {args.output}")
        return 0
    except (ValueError, DataLoadError) as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
