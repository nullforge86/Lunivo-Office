"""Dropdown-Knopf: der Knopf mit Pfeil, der ein Menü öffnet (Stufe 4 der Dropdown-Pyramide).

Alle Knöpfe, die ein Menü öffnen (Band, Leisten, Dialoge, Seitenleiste), sind ``DropdownKnopf`` (Werkzeugknopf) oder ``DropdownTaste`` (Taste mit Text).
Modus, Pfeilzone und Breitenverhalten stehen nur hier."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMenu, QPushButton, QSizePolicy, QToolButton

from lunivo_writer.ui.baukasten.basis.mass import (DROPDOWN_GROSS_BREITE_MIN, DROPDOWN_GROSS_BREITE_ZUGABE, DROPDOWN_GROSS_HOEHE, DROPDOWN_HOEHE,
                                              DROPDOWN_KNOPF, DROPDOWN_PFEIL_ZONE)


class _DropdownBasis:
    def groesse_rolle(self, rolle: str, variante: str) -> None:
        """Die Größe des Knopfes aus der zentralen Tabelle ``DROPDOWN_KNOPF`` (Rolle × Layoutvariante: band, mini, kopf, dokument)."""
        b, h, fest = DROPDOWN_KNOPF[(rolle, variante)]
        if fest:
            self.setFixedSize(b, h) if (b is not None and h is not None) else (self.setFixedWidth(b) if b is not None else self.setFixedHeight(h))
        else:
            if b is not None:
                self.setMinimumWidth(b)
            if h is not None:
                self.setMinimumHeight(h)

    def gross(self, textbreite: int, kompakt: bool) -> None:
        """Großer Bandknopf (Text unter dem Symbol): Breite folgt dem Text, Höhe je Dichte (kompakt oder normal) aus ``mass.py``."""
        self.setMinimumWidth(max(DROPDOWN_GROSS_BREITE_MIN[kompakt], textbreite + DROPDOWN_GROSS_BREITE_ZUGABE[kompakt]))
        self.setFixedHeight(DROPDOWN_GROSS_HOEHE[kompakt])

    def band_zeile(self) -> None:
        """Knopf in einer Bandzeile: Mindesthöhe der Kopf-Dropdowns (eine Quelle in ``mass.py``), damit die Zeilen fluchten."""
        self.setMinimumHeight(DROPDOWN_HOEHE)

    def menue_setzen(self, menue: QMenu, *, geteilt: bool | None = None, gross: bool = False, fuellend: bool = False, besitzen: bool = False) -> None:
        """``geteilt``: True = Symbol und Pfeil getrennt (``MenuButtonPopup``), False = ein Klick öffnet das Menü (``InstantPopup``), None = Modus bleibt.
        ``gross``: großer Knopf mit Text unter dem Symbol, bekommt die Pfeilzone dazu. ``fuellend``: der Knopf füllt die Breite seiner Spalte,
        damit gestapelte Dropdown-Knöpfe gleich breit sind und ihre Pfeile untereinander stehen.
        ``besitzen``: das Menü gehört dem Knopf (Popup-Kind, sonst räumt Python es weg); nur für Menüs, die kein anderer Knopf teilt."""
        if besitzen:
            menue.setParent(self, Qt.WindowType.Popup)
        if geteilt is not None and hasattr(self, "setPopupMode"):
            self.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup if geteilt else QToolButton.ToolButtonPopupMode.InstantPopup)
        self.setMenu(menue)
        if gross:
            self.setMinimumWidth(self.minimumWidth() + DROPDOWN_PFEIL_ZONE)
        if fuellend:
            self.setSizePolicy(QSizePolicy.Policy.Expanding, self.sizePolicy().verticalPolicy())


class DropdownKnopf(_DropdownBasis, QToolButton):
    """Werkzeugknopf, der ein Menü öffnet."""


class DropdownTaste(_DropdownBasis, QPushButton):
    """Taste mit Text, die ein Menü öffnet."""

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.setMinimumHeight(DROPDOWN_HOEHE); self.setProperty("dropdownFeld", True)
