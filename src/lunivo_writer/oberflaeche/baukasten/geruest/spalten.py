"""Zweispalter: links Navigation/Blatt/Liste, rechts Inhalt — der eine Baustein für alle zweispaltigen Seiten.

Breit (ab ``breit_ab`` Pixel) stehen beide Widgets nebeneinander, schmal (Seitenleiste) untereinander. Welches Widget schmal oben steht,
bestimmt ``oben``. Optionen, Datei öffnen/speichern, Hilfe, Druck und Datei-Ansicht bauen darauf auf, statt je ein eigenes
``QHBoxLayout`` mit eigener Breitenlogik zu führen."""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QBoxLayout, QWidget

from lunivo_writer.oberflaeche.baukasten.basis.mass import BREITE_AB_ZWEISPALTER, RAND_KEIN

_MAX = 16777215   # QWIDGETSIZE_MAX


class ZweiSpalter(QWidget):
    """``links``/``rechts``: beliebige Widgets. ``breit_ab``: Breite, ab der sie nebeneinander stehen (``0`` = immer nebeneinander,
    ohne Umbruch). ``links_breite``: feste Breite von ``links`` im breiten Zustand (schmal wieder frei), sonst gilt ``breit_stretch``.
    ``oben``: ``"links"`` oder ``"rechts"`` — das Widget, das gestapelt oben steht. ``gestapelt_stretch``: (oben, unten).
    ``angeordnet(breit)`` kommt bei jedem Wechsel des Zustands."""
    angeordnet = Signal(bool)

    def __init__(self, links: QWidget, rechts: QWidget, *, breit_ab: int = BREITE_AB_ZWEISPALTER, links_breite: int | None = None,
                 oben: str = "links", breit_stretch: tuple[int, int] | None = None, gestapelt_stretch: tuple[int, int] = (0, 1),
                 raender_breit: tuple = RAND_KEIN, raender_gestapelt: tuple = RAND_KEIN, abstand: int = 0, parent: QWidget | None = None):
        super().__init__(parent)
        if oben not in ("links", "rechts"):
            raise ValueError("oben: 'links' oder 'rechts'")
        self.links, self.rechts = links, rechts
        self.breit_ab, self.links_breite, self.oben = breit_ab, links_breite, oben
        self._breit_stretch = breit_stretch or ((0, 1) if links_breite else (1, 1))
        self._gestapelt_stretch = gestapelt_stretch
        self._raender = (raender_breit, raender_gestapelt)
        self._lay = QBoxLayout(QBoxLayout.TopToBottom, self)
        self._lay.setSpacing(abstand)
        self.breit: bool | None = None
        self.anordnen(breit_ab <= 0)

    def anordnen(self, breit: bool) -> None:
        """Setzt Richtung, Reihenfolge, Ränder und Breite neu; bei gleichem Zustand geschieht nichts."""
        if breit == self.breit:
            return
        self.breit = breit
        h = self._lay
        h.removeWidget(self.links); h.removeWidget(self.rechts)
        if breit:
            h.setDirection(QBoxLayout.LeftToRight); h.setContentsMargins(*self._raender[0])
            if self.links_breite:
                self.links.setFixedWidth(self.links_breite)
            h.addWidget(self.links, self._breit_stretch[0]); h.addWidget(self.rechts, self._breit_stretch[1])
        else:
            h.setDirection(QBoxLayout.TopToBottom); h.setContentsMargins(*self._raender[1])
            if self.links_breite:
                self.links.setMinimumWidth(0); self.links.setMaximumWidth(_MAX)
            erst, dann = (self.links, self.rechts) if self.oben == "links" else (self.rechts, self.links)
            h.addWidget(erst, self._gestapelt_stretch[0]); h.addWidget(dann, self._gestapelt_stretch[1])
        self.angeordnet.emit(breit)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.breit_ab > 0:
            self.anordnen(self.width() >= self.breit_ab)
