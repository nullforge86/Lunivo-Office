"""Nach dem Verschieben von Modulen: alle Module importierbar, alle Pfade im Text vorhanden, keine Weiterleitungen."""
import importlib.util
from pathlib import Path


def test_importpfade_stimmen():
    ziel = Path(__file__).resolve().parents[2] / "werkzeug" / "pruefen" / "importpruefung.py"
    spec = importlib.util.spec_from_file_location("importpruefung", ziel)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    ergebnis = modul.pruefen()
    assert not any(ergebnis.values()), {k: v[:10] for k, v in ergebnis.items() if v}
