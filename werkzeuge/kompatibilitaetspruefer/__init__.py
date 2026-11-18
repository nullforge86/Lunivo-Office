"""Lunivo Compatibility Tester — eigenständiges Entwicklerprogramm zur Prüfung der Dateiformat-Kompatibilität von Lunivo Office.

Start (aus dem Ordner ``werkzeuge``):  ``../.venv/bin/python -m kompatibilitaetspruefer``

Das Werkzeug enthält keine eigene Dokument-, Layout- oder Importimplementierung: Laden, Speichern, Layout und Rendering laufen über die vorhandenen
Komponenten von ``lunivo_writer`` (``dienste.modell_laden``, ``dienste.modell_speichern``, ``core.layout``, ``core.rendering``).
"""
import os
import sys

_SRC = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "src"))
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

PROGRAMMNAME = "Lunivo Compatibility Tester"
