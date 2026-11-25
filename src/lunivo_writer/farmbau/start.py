"""Einziger öffentlicher Einstieg in die grafische Lunivo-Anwendung."""
from __future__ import annotations
import sys

def main(argv: list[str] | None = None) -> int:
    """Fehlende Qt-Abhängigkeiten sind Fehler, kein Fallback."""
    argv = list(sys.argv if argv is None else argv)
    try:
        from lunivo_writer.farmbau.qt import starten
    except ImportError as exc:
        if exc.name and (exc.name == "PySide6" or exc.name.startswith("PySide6.")):
            print("PySide6 fehlt. Installation: ./skripte/starten-qt.sh oder pip install -r requirements.txt", file=sys.stderr)
            return 2
        raise
    return starten(argv)
