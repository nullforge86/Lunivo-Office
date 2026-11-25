from __future__ import annotations
import base64
from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF
from PySide6.QtGui import QImage, QPainter
from core.geometrie import Rect
from core.layout.drucklayout.ausgabe.seite.wasserzeichen import zeichne
from writer.funktionen.objekte.wasserzeichen import FORMATE, GROESSEN, HORIZONTAL, STANDARD_FARBE, VERTIKAL, VORGABEN, ZOOMS  # noqa: F401  (Namen der Oberfläche)


def bild_zu_text(img: QImage) -> str:
    ba = QByteArray()
    buf = QBuffer(ba); buf.open(QIODevice.WriteOnly)
    img.save(buf, "PNG")
    return base64.b64encode(bytes(ba)).decode("ascii")


def bild_aus_text(text: str) -> QImage:
    img = QImage()
    try:
        img.loadFromData(base64.b64decode(text))
    except (ValueError, TypeError):
        pass
    return img


def zeichnen(p: QPainter, w: dict | None, r: QRectF) -> None:
    """Das Wasserzeichen ``w`` auf die Seite ``r`` (96-dpi-Bildpunkte) zeichnen: Lage, Größe und Deckkraft rechnet ``core/rendering/wasserzeichen.py``, gezeichnet wird über das Backend."""
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    from vcl.qt.rendering.formen.anzeige import kern_malen
    kern_malen(p, r, lambda z: zeichne(z, standard_engine(), w, Rect(r.x(), r.y(), r.width(), r.height())), rand=0.0)
