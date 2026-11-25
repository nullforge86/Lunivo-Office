"""Einfuegen dialoge hilfen: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy
from vcl.qt.widgets.bausteine import FarbFeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_VORSCHAU_KLEIN
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile


def _ok(dlg):
    return knopfzeile(dlg)


_Farbknopf = FarbFeld


class _Vorschau(QLabel):
    """Vorschaubild, das sich der Breite anpasst (in der Seitenleiste kleiner, nie breiter als 460 px)."""

    def __init__(self):
        super().__init__()
        self._bild = None
        self.setMinimumHeight(HOEHE_VORSCHAU_KLEIN); self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        eigenschaft(self, rolle="vorschaublatt")

    def setze(self, img) -> None:
        self._bild = img
        self._neu()

    def _neu(self) -> None:
        if self._bild is None:
            return
        pm = QPixmap.fromImage(self._bild)
        b = min(460, max(40, self.width() - 8))
        if pm.width() > b:
            pm = pm.scaledToWidth(b, Qt.SmoothTransformation)
        self.setPixmap(pm)

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._neu()


class VorschauMixin:
    def _vorschau_bauen(self, layout):
        self.vorschau = _Vorschau()
        layout.addWidget(self.vorschau) if not isinstance(layout, FormularGitter) else layout.breit(self.vorschau)

    def _zeige(self, img):
        self.vorschau.setze(img)


def _layout_bildchen(p, r, name: str) -> None:
    """Graue Miniatur eines SmartArt-Layouts (selbst gezeichnet, ``oberflaeche/baukasten/dropdown/objektmenues/smartart_menues.py``)."""
    from vcl.qt.widgets.menues.dropdown.objektmenues.smartart_menues import zeichne_miniatur
    zeichne_miniatur(p, r.adjusted(3, 3, -3, -3), name, True)


class VorschauMixin:
    def _vorschau_bauen(self, layout):
        self.vorschau = _Vorschau()
        layout.addWidget(self.vorschau) if not isinstance(layout, FormularGitter) else layout.breit(self.vorschau)

    def _zeige(self, img):
        self.vorschau.setze(img)
