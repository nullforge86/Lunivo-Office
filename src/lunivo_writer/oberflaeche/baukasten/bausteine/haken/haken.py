"""Haken (Kontrollkästchen) als Baustein aus Form, Inhalt und Verhalten (das Optionsfeld steht im Baustein ``option``)."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import QCheckBox, QWidget

from lunivo_writer.oberflaeche.baukasten.bausteine.haken.form import formen
from lunivo_writer.oberflaeche.baukasten.bausteine.haken.inhalt import beschriften
from lunivo_writer.oberflaeche.baukasten.bausteine.haken.verhalten import verbinden


def haken(form: str = "standard", text: str = "", *, an: bool = False, aktion: Callable[[bool], object] | None = None, tooltip: str = "",
          name: str = "", aktiv: bool = True, eltern: QWidget | None = None) -> QCheckBox:
    h = QCheckBox(eltern)
    formen(h, form)
    beschriften(h, text, tooltip, name)
    verbinden(h, an, aktion, aktiv)
    return h

