"""Schriftauswahl: aus ``vcl.qt.widgets.menues.dropdown.auswahlfeld`` herausgelöst."""
from __future__ import annotations
from PySide6.QtWidgets import QComboBox, QFontComboBox
from vcl.qt.widgets.bausteine.abstaende.mass import QWIDGETSIZE_MAX
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_HOEHE, DROPDOWN_MIN_ZEICHEN, DROPDOWN_SCHRIFT_POPUP_BREITE
from vcl.qt.widgets.menues.dropdown.auswahlfeld_hilfen import MAX_ZEILEN, popup_begrenzen
from vcl.qt.widgets.menues.dropdown.feldlaenge import _Feldlaenge


class Schriftauswahl(_Feldlaenge, QFontComboBox):
    """Schriftart-Auswahl; behält die Schriftvorschau der Einträge."""

    def __init__(
        self,
        parent=None,
        *,
        min_zeichen: int = DROPDOWN_MIN_ZEICHEN,
        popup_min: int = DROPDOWN_SCHRIFT_POPUP_BREITE,
    ):
        super().__init__(parent)

        self._popup_min = popup_min
        self.setSizeAdjustPolicy(
            QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon
        )
        self.setMinimumContentsLength(min_zeichen)
        self.setMaxVisibleItems(MAX_ZEILEN)
        self.setMinimumHeight(DROPDOWN_HOEHE)

    def showPopup(self) -> None:
        view = self.view()
        pop = view.window() if view is not None else None
        if pop is not None:
            pop.setMinimumWidth(0)
            pop.setMaximumWidth(QWIDGETSIZE_MAX)
            view.setMinimumWidth(0)
            view.setMaximumWidth(QWIDGETSIZE_MAX)

        super().showPopup()

        # QFontComboBox behält seine eigene Positionierung.
        # Angepasst wird ausschließlich die Breite des Popup-Fensters.
        popup_begrenzen(self, self._popup_min)
