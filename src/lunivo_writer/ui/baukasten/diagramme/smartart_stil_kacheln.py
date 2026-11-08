"""Stilkacheln im Band „SmartArt-Design“ nach der Vorlage: Organigramm-Motiv (ein Kasten oben, zwei unten, Linien) in den fünf Stilen.

``stil_bild_org(nr, groesse)``  Kachel des Formenstils ``nr`` (``SA.STILE``: Flach, Einfach, Hell, Kräftig, 3D)
``stile_galerie_org(b)``        die fünf Kacheln im Band samt Popup (Aufbau wie ``diagramm_stile_galerie``); ``GALERIEN`` meldet sie als ``smartartStile``
Befehl bleibt ``smartartStil`` (``core/befehle/kontextreiter/smartarttools.py``); gerechnet wird hier nichts.
"""
from __future__ import annotations

from PySide6.QtCore import QRectF, QPointF, QSize, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPen, QPixmap

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.dropdown.auswahl.raster_auswahl import RasterAuswahl
from lunivo_writer.ui.baukasten.basis.mass import GROESSE_SMARTART_STIL_BAND, GROESSE_SMARTART_STIL_POPUP

BAND_KACHEL = QSize(*GROESSE_SMARTART_STIL_BAND)
POPUP_KACHEL = QSize(*GROESSE_SMARTART_STIL_POPUP)


def stil_bild_org(nr: int, groesse: QSize = BAND_KACHEL, blau: str | None = None) -> QPixmap:
    blau = Farbe.AKZENT if blau is None else blau
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    w, h = groesse.width(), groesse.height()
    c = QColor(blau)
    kw, kh = w * 0.34, h * 0.20
    oben = QRectF((w - kw) / 2, h * 0.16, kw, kh)
    unten = [QRectF(w * 0.12, h * 0.64, kw, kh), QRectF(w * 0.54, h * 0.64, kw, kh)]
    p.setPen(QPen(c.darker(110), 1))                                              # Linien: Stamm, Querstrich, zwei Äste
    mitte, quer = w / 2, h * 0.52
    p.drawLine(QPointF(mitte, oben.bottom()), QPointF(mitte, quer))
    p.drawLine(QPointF(unten[0].center().x(), quer), QPointF(unten[1].center().x(), quer))
    for r in unten:
        p.drawLine(QPointF(r.center().x(), quer), QPointF(r.center().x(), r.top()))
    for r in [oben, *unten]:
        if nr == 2:                                                               # Hell: blasse Fläche
            p.setBrush(c.lighter(160)); p.setPen(QPen(c.lighter(130), 1))
        elif nr == 3:                                                             # Kräftig: dunkler Rand
            p.setBrush(c); p.setPen(QPen(c.darker(150), 2))
        elif nr == 4:                                                             # 3D: Verlauf
            g = QLinearGradient(r.topLeft(), r.bottomLeft()); g.setColorAt(0, c.lighter(135)); g.setColorAt(1, c.darker(125))
            p.setBrush(g); p.setPen(QPen(c.darker(150), 1))
        elif nr == 1:                                                             # Einfach: Fläche mit dünnem Rand
            p.setBrush(c); p.setPen(QPen(c.darker(125), 1))
        else:                                                                     # Flach
            p.setBrush(c); p.setPen(Qt.NoPen)
        p.drawRect(r)
    p.end()
    return pm


def stile_menue_org(b) -> RasterAuswahl:
    from lunivo_writer.editor.objekte import smartart as SA
    from lunivo_writer.ui.baukasten.dropdown.objektmenues.smartart_menues import _sa
    m = RasterAuswahl(b.w, spalten=len(SA.STILE), groesse=POPUP_KACHEL)
    aktuell = _sa(b).get("stil", 1)
    for i, name in enumerate(SA.STILE):
        m.kachel(str(i), name, stil_bild_org(i, POPUP_KACHEL), aktuell=i == aktuell)
    m.gewaehlt.connect(lambda k: b.smartartStil(None, int(k)))
    return m


def stile_galerie_org(b) -> dict:
    from lunivo_writer.editor.objekte import smartart as SA
    return {"kacheln": [(name, stil_bild_org(i), lambda i=i: b.smartartStil(None, i)) for i, name in enumerate(SA.STILE)],
            "menue": stile_menue_org(b), "name": "SmartArt-Stile"}
