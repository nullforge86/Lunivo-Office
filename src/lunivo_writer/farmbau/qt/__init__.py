"""Qt-Implementierung der Farmbau-Kompositionsgrenze."""
from __future__ import annotations

def starten(argv: list[str]) -> int:
    from lunivo_writer.farmbau.qt.anwendung import LunivoQtApplication
    return LunivoQtApplication(argv).start()
