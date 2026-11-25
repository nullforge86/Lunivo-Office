from __future__ import annotations
from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QBrush, QColor, QLinearGradient, QPainter, QPainterPath, QPen
from core.formatierung.farben.farben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import ANTEIL_SCHRIFT_KACHEL, ANTEIL_SCHRIFT_KACHEL_GROSS, STIFT_VORGABE_KONTUR
from vcl.qt.widgets.bausteine.farben.farben import DURCHSICHTIG
from vcl.qt.widgets.bausteine.schrift.schriftarten import SANS
from writer.funktionen.objekte.wordart import PX
from vcl.qt.rendering.wordart.textfx import fx_zeichnen, vorschau_zeichnen


def voreinstellung_icon(fx: dict, groesse=(52, 40), text: str = "A", farbe: str | None = None, kontur=None):
    """Kachelbild einer Voreinstellung: ein „A“ mit dem Effekt auf weißem Grund (``kontur``: (Farbe, Breite, Form) wie bei ``vorschau_zeichnen``)."""
    from PySide6.QtGui import QFont, QIcon, QPixmap
    pm = QPixmap(*groesse); pm.fill(QColor("white"))
    p = QPainter(pm)
    f = QFont(SANS); f.setPixelSize(int(groesse[1] * ANTEIL_SCHRIFT_KACHEL)); f.setBold(True)
    vorschau_zeichnen(p, QRectF(0, 0, groesse[0], groesse[1] * 0.92), text, f, fx, QColor(farbe if farbe is not None else Farbe.GRAU_HELL), kontur)
    p.end()
    return QIcon(pm)


def text_kachel_icon(fx: dict, groesse=(50, 50)):
    """Kachelbild der Effektmenüs im Text (Schatten, Spiegelung, Leuchten): ein hellblaues „A“ mit blauem Rand, plastisch, wie in der Vorlage."""
    return voreinstellung_icon(fx, groesse, "A", Farbe.VORGABE_GRUND, (QColor(Farbe.VORGABE_RAND), STIFT_VORGABE_KONTUR, "einfach"))


def form_kachel_icon(fx: dict, groesse=(50, 50)):
    """Kachelbild des Schattenmenüs eines Objekts: ein abgerundetes Rechteck mit weichem Verlauf (hellblau, blauer Rand) und dem Effekt auf weißem Grund."""
    from PySide6.QtGui import QIcon, QPixmap
    pm = QPixmap(*groesse); pm.fill(QColor("white"))
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    seite = min(groesse) * 0.58
    r = QRectF((groesse[0] - seite) / 2, (groesse[1] - seite) / 2 - 1, seite, seite)
    pfad = QPainterPath(); pfad.addRoundedRect(r, 5, 5)
    g = QLinearGradient(r.topLeft(), r.bottomLeft())
    g.setColorAt(0, QColor(Farbe.VORGABE_VERLAUF[0])); g.setColorAt(0.55, QColor(Farbe.VORGABE_VERLAUF[1])); g.setColorAt(1, QColor(Farbe.VORGABE_VERLAUF[2]))
    p.fillPath(pfad, QBrush(g))
    fx_zeichnen(p, pfad, fx, r.bottom(), seite)                          # Schatten außen, innen oder in Perspektive
    p.setPen(QPen(QColor(Farbe.VORGABE_FORMRAND), 1.0)); p.setBrush(Qt.NoBrush); p.drawPath(pfad)
    p.end()
    return QIcon(pm)


def wordart_icon(w: dict, groesse=(52, 40)):
    """Kachelbild einer WordArt-Formatvorlage."""
    from PySide6.QtGui import QFont, QIcon, QPixmap
    pm = QPixmap(*groesse); pm.fill(QColor("white"))
    p = QPainter(pm)
    f = QFont(SANS); f.setPixelSize(int(groesse[1] * ANTEIL_SCHRIFT_KACHEL_GROSS)); f.setBold(True)
    face = QColor(*DURCHSICHTIG) if w.get("fuell") == "keine" else QColor((w.get("verlauf") or {}).get("farbe1") or w.get("farbe") or Farbe.WORDART_TINTE)
    kontur = (QColor(w["kontur_farbe"]), w.get("kontur_breite", 1.0) * PX, "einfach", "einfach") if w.get("kontur") else None
    fx = {k: v for k, v in w.items() if k in ("verlauf", "schatten", "reflektion", "leuchten", "d3")}
    vorschau_zeichnen(p, QRectF(0, 0, groesse[0], groesse[1] * 0.95), "A", f, fx, face, kontur)
    p.end()
    return QIcon(pm)
