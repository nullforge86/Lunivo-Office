"""Zeilenfeld als Baustein aus Form, Inhalt und Verhalten."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QLineEdit, QWidget

from lunivo_writer.oberflaeche.baukasten.bausteine.feld.form import formen
from lunivo_writer.oberflaeche.baukasten.bausteine.feld.inhalt import beschriften
from lunivo_writer.oberflaeche.baukasten.bausteine.feld.verhalten import verbinden


def zeilenfeld(form: str = "standard", text: str = "", *, platzhalter: str = "", name: str = "", nur_lesen: bool = False,
               bei_aenderung: Callable[[str], object] | None = None, bei_eingabe: Callable[[], object] | None = None,
               passwort: bool = False, aktiv: bool = True, eltern: QWidget | None = None) -> QLineEdit:
    f = QLineEdit(eltern)
    formen(f, form)
    beschriften(f, text, platzhalter, name)
    verbinden(f, nur_lesen, bei_aenderung, bei_eingabe, passwort, aktiv)
    return f
