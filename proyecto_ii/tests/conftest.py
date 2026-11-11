import pandas as pd
import pytest


@pytest.fixture
def emt_frame():
    """Demanda sintética (3 líneas x 4 franjas x 70 días) sin llamadas HTTP reales."""
    rows = []
    for day, date in enumerate(pd.date_range("2026-01-01", periods=70, freq="D")):
        weekend = 0.5 if date.dayofweek >= 5 else 1.0
        for line, scale in (("001", 100), ("027", 300), ("501", 40)):
            for slot, factor in (("H07", 1.0), ("H08", 1.5), ("H18", 1.2), ("M02", 0.3)):
                rows.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "line": line,
                    "time_slot": slot,
                    "passengers": int(scale * factor * weekend + day % 7),
                })
    return pd.DataFrame(rows)
