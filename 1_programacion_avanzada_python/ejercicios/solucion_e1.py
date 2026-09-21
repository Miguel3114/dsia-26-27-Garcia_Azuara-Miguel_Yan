from pathlib import Path
import json
import pandas as pd


DATA_DIR = Path("1_programacion_avanzada_python/datos")

def cargar_ventas(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No existe el fichero: {path}")
    return pd.read_csv(path)


ventas = cargar_ventas(DATA_DIR / "ventas.csv")

print("Shape:")
print(ventas.shape)

print("\nTipos:")
print(ventas.dtypes)

print("\nValores nulos:")
print(ventas.isna().sum())


def validar_ventas(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    datos = frame.copy()

    datos["unidades"] = pd.to_numeric(datos["unidades"], errors="coerce")
    datos["precio_unitario"] = pd.to_numeric(
        datos["precio_unitario"],
        errors="coerce"
    )

    condicion = (
        datos["unidades"].notna()
        & (datos["unidades"] > 0)
        & datos["precio_unitario"].notna()
        & (datos["precio_unitario"] > 0)
    )

    validos = datos[condicion].copy()
    errores = datos[~condicion].copy()

    validos["importe"] = (
        validos["unidades"]
        * validos["precio_unitario"]
    )

    return validos, errores


validos, errores = validar_ventas(ventas)

print("\nFilas válidas:", len(validos))
print("Filas inválidas:", len(errores))


importe_region = (
    validos
    .groupby("region")["importe"]
    .sum()
    .sort_values(ascending=False)
)

print("\nImporte total por región:")
print(importe_region)


top_productos = (
    validos
    .groupby("producto")["importe"]
    .sum()
    .sort_values(ascending=False)
    .head(3)
)

print("\nTop 3 productos por importe:")
print(top_productos)


compras_cliente = validos["cliente_id"].value_counts()

clientes_mas_una_compra = compras_cliente[
    compras_cliente > 1
]

print("\nClientes con más de una compra:")
print(clientes_mas_una_compra)


ruta_limpias = Path("1_programacion_avanzada_python/datos") / "ventas_limpias.csv"

validos.to_csv(
    ruta_limpias,
    index=False
)


calidad = {
    "filas_totales": len(ventas),
    "filas_validas": len(validos),
    "filas_invalidas": len(errores),
    "importe_total": float(validos["importe"].sum())
}

ruta_json = Path("1_programacion_avanzada_python/datos") / "calidad_datos.json"

with open(ruta_json, "w", encoding="utf-8") as archivo:
    json.dump(
        calidad,
        archivo,
        indent=4,
        ensure_ascii=False
    )

print("\nCalidad de datos:")
print(calidad)