"""Lunivo Writer — native Textverarbeitung (Python 3, PySide6/Qt Widgets).

Beim Import des Pakets wird der Startwächter der Schichtensperre eingehängt (``sperre/waechter.py``); Regeln und Übergangsliste stehen in
``sperre/regeln.py`` und ``sperre/uebergang.py``."""
from lunivo_writer.farmwork.pruefung import importe as waechter

__version__ = "0.1.0"

waechter.einhaengen()
