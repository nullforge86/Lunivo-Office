"""Feldlaenge: aus ``vcl.qt.widgets.menues.dropdown.auswahlfeld`` herausgelöst."""
from __future__ import annotations
from PySide6.QtWidgets import QComboBox
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_BREITE


class _Feldlaenge:
    """Gemeinsam für ``Auswahlfeld`` und ``Schriftauswahl``."""

    def zeichen(self, n: int) -> None:
        self.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.setMinimumContentsLength(n)

    def rolle(
        self,
        rolle: str,
        variante: str,
        *,
        mindest: bool = False,
    ) -> None:
        """Breite aus ``DROPDOWN_BREITE`` (Rolle × Layoutvariante)."""
        b = DROPDOWN_BREITE[(rolle, variante)]
        self.setMinimumWidth(b) if mindest else self.setFixedWidth(b)

    def an_inhalt(self) -> None:
        """Das Feld ist so breit wie sein längster Eintrag."""
        self.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToContents
        )
