from __future__ import annotations
from PySide6.QtCore import QRectF
from PySide6.QtGui import QColor, QPainter
from core.objekte.formen.sprechblasen_modell import BLASE_RAND, BLASE_UEBERABTASTUNG, Blase, KOPF_HOEHE, _ortszeit


def menue_rect(r: QRectF) -> QRectF:
    """Die Fläche des Menüzeichens „☰“ oben rechts in der Blase (für den Klick)."""
    return QRectF(r.right() - 28, r.y() + 6, 24, KOPF_HOEHE + 4)


def zeichnen(p: QPainter, bl: Blase, r: QRectF, font, druck: bool = False) -> None:
    """Eine Blase zeichnen wie eine Karte: Kreis mit Initial, Name fett, Datum, Menüzeichen, darunter der Text — Farben des Designs, Kreis in der Farbe des Kommentars. Gezeichnet vom Kern."""
    from PySide6.QtGui import QGuiApplication, QPalette
    from vcl.qt.rendering.formen.anzeige import kern_malen
    from core.geometrie import Rect
    from core.layout.drucklayout.ausgabe.objekte import blasen
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    pal = QPalette() if druck else QGuiApplication.palette()                # im Druck immer helle Farben, nie die des dunklen Designs

    def farbe(c: QColor) -> tuple:
        return c.red(), c.green(), c.blue(), c.alpha()
    farben = (farbe(pal.color(QPalette.Button)), farbe(pal.color(QPalette.Mid)), farbe(pal.color(QPalette.ButtonText)))
    fb = QColor(bl.farbe)
    engine = standard_engine()
    kern_malen(p, r, lambda z: blasen.zeichne_blase(z, engine, bl.autor, _ortszeit(bl.datum), farbe(fb), bl.text or "", Rect(r.x(), r.y(), r.width(), r.height()), font, farben), rand=BLASE_RAND, ueber=BLASE_UEBERABTASTUNG)


def verbindung(p: QPainter, bl: Blase, x_text: float, y_text: float, r: QRectF, rechts: bool) -> None:
    """Linie vom Text zur Blase: waagerecht aus dem Seitenrand, dann zur Mitte der Kopfzeile."""
    from vcl.qt.rendering.formen.anzeige import kern_malen
    from core.geometrie import Rect
    from core.layout.drucklayout.ausgabe.objekte import blasen
    c = QColor(bl.farbe)
    flaeche = QRectF(min(x_text, r.left()) - 12, min(y_text, r.top()) - 2, abs(r.left() - x_text) + r.width() + 24, abs(y_text - r.top()) + r.height() + 4)
    kern_malen(p, flaeche, lambda z: blasen.verbindung(z, (c.red(), c.green(), c.blue(), c.alpha()), x_text, y_text, Rect(r.x(), r.y(), r.width(), r.height()), rechts), rand=BLASE_RAND, ueber=BLASE_UEBERABTASTUNG)
