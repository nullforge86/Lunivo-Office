"""Lineal hilfen: aus ``vcl.qt.widgets.dokumentansicht.ansicht.lineal`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QWidget
from writer.werte import px_je_mm
from vcl.qt.widgets.bausteine.farben import LINEAL_HELLER_RAND, LINEAL_HELLER_RAND_HELL, LINEAL_HELLER_TEXT
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import LINEAL_ALPHA_STRICH, LINEAL_ALPHA_ZAHL, RADIUS_LINEAL, SCHRIFT_LINEAL_PX
from vcl.qt.widgets.dokumentansicht.ansicht.lineal_hilfslinie import Hilfslinie


HOEHE = 26          # Dicke des Lineals


class _Lineal(QWidget):
    LINIE_SENKRECHT = True                             # das waagerechte Lineal zieht eine senkrechte Hilfslinie; das senkrechte stellt es um

    def __init__(self, tab):
        super().__init__(tab)
        self.tab = tab
        self.e = tab.editor
        self._zieh = None
        self._wert = None
        self.hilfslinie = Hilfslinie(tab, self.LINIE_SENKRECHT)        # nur während des Ziehens einer Marke sichtbar
        self.setMouseTracking(True)
        self.e.zoomChanged.connect(lambda *_: self.update())
        self.e.pageApplied.connect(self.update)
        self.e.cursorPositionChanged.connect(self.update)

    def _versatz(self) -> QPoint:
        """Wo der Editor (das Blatt) im Fenster steht — ändert sich beim Rollen."""
        return self.e.ansicht.mapTo(self.tab.viewport(), QPoint(0, 0))

    def px(self, mm: float) -> float:
        return mm * px_je_mm() * self.e.zoom

    def farben(self) -> dict:
        """Zurückhaltende Farben aus der Arbeitsfläche: ``aussen`` ist die Arbeitsfläche selbst (das Lineal hebt sich außerhalb des Blatts nicht ab),
        ``grund`` der Seitenrand und ``text`` der Textbereich als leichte Aufhellungen davon."""
        pal = self.palette()
        flaeche = pal.color(pal.ColorRole.Dark)
        schrift = pal.color(pal.ColorRole.WindowText)
        if flaeche.lightness() < schrift.lightness():                     # dunkles Thema
            return {"grund": flaeche.lighter(LINEAL_HELLER_RAND), "schrift": schrift, "aussen": flaeche, "text": flaeche.lighter(LINEAL_HELLER_TEXT)}
        return {"grund": flaeche.lighter(LINEAL_HELLER_RAND_HELL), "schrift": schrift, "aussen": flaeche, "text": QColor(Farbe.WEISS)}

    def koerper_zeichnen(self, p: QPainter, koerper, text, c: dict) -> None:
        """Der Körper des Lineals: nur so lang wie das Blatt, mit weichen Ecken; darin heller der Textbereich. Keine Kante, kein Balken über die ganze Fläche."""
        p.fillRect(self.rect(), c["aussen"])
        p.setPen(Qt.NoPen)
        p.setBrush(c["grund"])
        p.drawRoundedRect(koerper, RADIUS_LINEAL, RADIUS_LINEAL)
        p.fillRect(text.intersected(koerper), c["text"])

    def stifte(self, c: dict) -> tuple:
        """Farben für Zahlen und Teilstriche: die Schrift des Themas, deutlich zurückgenommen."""
        zahl, strich = QColor(c["schrift"]), QColor(c["schrift"])
        zahl.setAlpha(LINEAL_ALPHA_ZAHL); strich.setAlpha(LINEAL_ALPHA_STRICH)
        return zahl, strich

    def _schrift(self, p: QPainter) -> None:
        f = QFont(p.font())
        f.setPixelSize(SCHRIFT_LINEAL_PX); f.setBold(False)
        p.setFont(f)
