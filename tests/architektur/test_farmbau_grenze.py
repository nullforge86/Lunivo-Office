"""Verhindert Umgehungen der Farmbau-Kompositionsgrenze."""
from __future__ import annotations
import ast
from pathlib import Path
PAKET = Path(__file__).resolve().parents[2] / "src" / "lunivo_writer"
VERBOTEN = ("lunivo_writer.oberflaeche", "lunivo_writer.kern.anwendung", "PySide6")

def _importe(pfad: Path) -> list[str]:
    ergebnis = []
    for knoten in ast.walk(ast.parse(pfad.read_text(encoding="utf-8"))):
        if isinstance(knoten, ast.Import):
            ergebnis.extend(alias.name for alias in knoten.names)
        elif isinstance(knoten, ast.ImportFrom):
            ergebnis.append(knoten.module or "")
    return ergebnis

def test_oeffentliche_startpunkte_nur_ueber_farmbau():
    for pfad in (PAKET / "app.py", PAKET / "__main__.py"):
        assert not any(name.startswith(VERBOTEN) for name in _importe(pfad)), pfad
    assert "lunivo_writer.farmbau.start" in _importe(PAKET / "app.py")

def test_farmbau_start_ohne_direkte_qt_importe():
    assert not any(name.startswith(VERBOTEN) for name in _importe(PAKET / "farmbau" / "start.py"))

def test_core_kennt_keinen_farmbau():
    for pfad in (PAKET / "core").rglob("*.py"):
        assert not any(name.startswith(("lunivo_writer.farmbau", "lunivo_writer.oberflaeche", "PySide6"))
                       for name in _importe(pfad)), pfad
