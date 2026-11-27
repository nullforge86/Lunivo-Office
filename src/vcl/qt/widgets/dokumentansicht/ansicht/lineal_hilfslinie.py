"""Hilfslinie der Lineale: solange eine Marke am Lineal gezogen wird, zeigt eine gestrichelte Linie ihre Stelle quer über das Dokument.

Nur Darstellung: die Linie liegt über dem sichtbaren Ausschnitt des Dokuments, nimmt keine Maus an und verschwindet beim Loslassen.
``zeigen(wo)``: ``wo`` ist die Stelle in Bildpunkten des Lineals (waagerechtes Lineal: x, senkrechtes Lineal: y)."""
from __future__ import annotations

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.farben import Farbe


class Hilfslinie(QWidget):
    def __init__(self, tab, senkrecht: bool):
        super().__init__(tab)
        self.tab = tab
        self.senkrecht = senkrecht                    # senkrechte Linie (waagerechtes Lineal) oder waagerechte Linie (senkrechtes Lineal)
        self.wo = 0.0
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.hide()

    def zeigen(self, wo: float) -> None:
        self.wo = wo
        self.setGeometry(self.tab.viewport().geometry())      # die Lineale beginnen an derselben Kante wie der Ausschnitt: gleiche Bildpunkte
        self.show()
        self.raise_()
        self.update()

    def weg(self) -> None:
        self.hide()

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setPen(QPen(QColor(Farbe.AKZENT_DUNKEL), 1, Qt.DashLine))
        if self.senkrecht:
            p.drawLine(QPointF(self.wo, 0), QPointF(self.wo, self.height()))
        else:
            p.drawLine(QPointF(0, self.wo), QPointF(self.width(), self.wo))
        p.end()
