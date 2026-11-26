"""Der weiche Schatten um das Blatt auf der Arbeitsfläche.

Gezeichnet wird er direkt mit dem Zeichner der Ansicht (Ringe mit abnehmender Deckkraft), nicht über einen Grafikeffekt: ein Effekt müsste die ganze
Ansicht bei jedem Zeichnen zwischenspeichern und weichzeichnen. Weite und Versatz stehen in ``mass``, die Deckkraft in ``farben``."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen

from vcl.qt.widgets.bausteine.abstaende import BLATTSCHATTEN_VERSATZ, BLATTSCHATTEN_WEITE
from vcl.qt.widgets.bausteine.farben import BLATTSCHATTEN_DECKKRAFT_DUNKEL, BLATTSCHATTEN_DECKKRAFT_HELL, SCHWARZ_RGB


def blattschatten(p: QPainter, blatt: QRectF, dunkel: bool) -> None:
    """Zeichnet den Schatten um ``blatt`` (vor dem Blatt aufrufen: das Blatt deckt den inneren Teil zu). ``dunkel``: dunkle Arbeitsfläche."""
    staerke = BLATTSCHATTEN_DECKKRAFT_DUNKEL if dunkel else BLATTSCHATTEN_DECKKRAFT_HELL
    p.save()
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(Qt.NoBrush)
    for k in range(BLATTSCHATTEN_WEITE):
        rest = 1.0 - k / BLATTSCHATTEN_WEITE                       # außen blasser: die Deckkraft fällt mit dem Quadrat des Abstands
        p.setPen(QPen(QColor(*SCHWARZ_RGB, round(staerke * rest * rest / 2)), 1))
        aussen = k + 0.5
        ring = blatt.adjusted(-aussen, -aussen, aussen, aussen).translated(0, BLATTSCHATTEN_VERSATZ)
        p.drawRoundedRect(ring, aussen, aussen)
    p.restore()
