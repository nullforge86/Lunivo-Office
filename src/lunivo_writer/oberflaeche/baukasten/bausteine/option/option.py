"""Optionsfeld als Baustein aus Form, Inhalt und Verhalten.

    option("standard", "&Alle", an=True, gruppe=self.gruppe)"""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QButtonGroup, QRadioButton, QWidget

from lunivo_writer.oberflaeche.baukasten.bausteine.option.form import formen
from lunivo_writer.oberflaeche.baukasten.bausteine.option.inhalt import beschriften
from lunivo_writer.oberflaeche.baukasten.bausteine.option.verhalten import verbinden


def option(form: str = "standard", text: str = "", *, an: bool = False, aktion: Callable[[bool], object] | None = None, tooltip: str = "",
           name: str = "", aktiv: bool = True, gruppe: QButtonGroup | None = None, nummer: int = -1, eltern: QWidget | None = None) -> QRadioButton:
    o = QRadioButton(eltern)
    formen(o, form)
    beschriften(o, text, tooltip, name)
    verbinden(o, an, aktion, aktiv, gruppe, nummer)
    return o
