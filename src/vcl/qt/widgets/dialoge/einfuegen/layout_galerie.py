"""Layout galerie: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import KACHEL_SEITENVERHAELTNIS
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_KACHEL_VORSCHAU, ZUGABE_KACHEL


class _LayoutGalerie(QWidget):
    """Galerie der SmartArt-Layouts: Bildchen (selbst gezeichnet) in einem KachelFeld, die Spaltenzahl folgt der Breite."""
    gewaehlt = Signal(str)
    KACHEL = BREITE_KACHEL_VORSCHAU

    def __init__(self, namen, zeichner, aktuell):
        super().__init__()
        self._namen, self._zeichner, self._aktuell, self._spalten = list(namen), zeichner, aktuell, 0
        self._v = _spalte("standard", self)
        self.feld = None
        self._bauen(3)

    def _bauen(self, spalten: int) -> None:
        from vcl.qt.widgets.bausteine.interaktion.felder.kachel_feld import KachelFeld
        if self.feld is not None:
            self._v.removeWidget(self.feld); self.feld.deleteLater()
        self._spalten = spalten
        self.feld = KachelFeld(spalten=spalten, groesse=QSize(self.KACHEL, self.KACHEL * 3 // 4), mit_text=False)
        for n in self._namen:
            self.feld.hinzu(n, n, lambda p, r, n=n: self._zeichner(p, r, n))
            self.feld.knoepfe[n].setAccessibleName(n)
            self.feld.knoepfe[n].setFixedSize(self.KACHEL + ZUGABE_KACHEL, self.KACHEL * KACHEL_SEITENVERHAELTNIS[0] // KACHEL_SEITENVERHAELTNIS[1] + ZUGABE_KACHEL)
            self.feld.knoepfe[n].setProperty("kachel", True)      # die gewählte Kachel ist hinterlegt (Theme)
        self.feld.gewaehlt.connect(self._klick)
        self.feld.setze(self._aktuell)
        self._v.addWidget(self.feld)
        self.updateGeometry()

    def _klick(self, name: str) -> None:
        self._aktuell = name
        self.gewaehlt.emit(name)

    def setze(self, name: str) -> None:
        self._aktuell = name; self.feld.setze(name)

    def aktuell(self) -> str:
        return self._aktuell

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        s = max(1, min(len(self._namen), (self.width() + 4) // (self.KACHEL + 14)))
        if s != self._spalten:
            self._bauen(s)


class _LayoutGalerie(QWidget):
    """Galerie der SmartArt-Layouts: Bildchen (selbst gezeichnet) in einem KachelFeld, die Spaltenzahl folgt der Breite."""
    gewaehlt = Signal(str)
    KACHEL = BREITE_KACHEL_VORSCHAU

    def __init__(self, namen, zeichner, aktuell):
        super().__init__()
        self._namen, self._zeichner, self._aktuell, self._spalten = list(namen), zeichner, aktuell, 0
        self._v = _spalte("standard", self)
        self.feld = None
        self._bauen(3)

    def _bauen(self, spalten: int) -> None:
        from vcl.qt.widgets.bausteine.interaktion.felder.kachel_feld import KachelFeld
        if self.feld is not None:
            self._v.removeWidget(self.feld); self.feld.deleteLater()
        self._spalten = spalten
        self.feld = KachelFeld(spalten=spalten, groesse=QSize(self.KACHEL, self.KACHEL * 3 // 4), mit_text=False)
        for n in self._namen:
            self.feld.hinzu(n, n, lambda p, r, n=n: self._zeichner(p, r, n))
            self.feld.knoepfe[n].setAccessibleName(n)
            self.feld.knoepfe[n].setFixedSize(self.KACHEL + ZUGABE_KACHEL, self.KACHEL * KACHEL_SEITENVERHAELTNIS[0] // KACHEL_SEITENVERHAELTNIS[1] + ZUGABE_KACHEL)
            self.feld.knoepfe[n].setProperty("kachel", True)      # die gewählte Kachel ist hinterlegt (Theme)
        self.feld.gewaehlt.connect(self._klick)
        self.feld.setze(self._aktuell)
        self._v.addWidget(self.feld)
        self.updateGeometry()

    def _klick(self, name: str) -> None:
        self._aktuell = name
        self.gewaehlt.emit(name)

    def setze(self, name: str) -> None:
        self._aktuell = name; self.feld.setze(name)

    def aktuell(self) -> str:
        return self._aktuell

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        s = max(1, min(len(self._namen), (self.width() + 4) // (self.KACHEL + 14)))
        if s != self._spalten:
            self._bauen(s)
