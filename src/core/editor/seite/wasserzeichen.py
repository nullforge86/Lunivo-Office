"""Wasserzeichen einer Seite: Text oder Bild, mit Lage, Größe und Transparenz (Einfügen ▸ Wasserzeichen). Keine Oberfläche.

Ein Wasserzeichen ist ein Wörterbuch in ``PageSettings.watermark``:

    {"text": "VERTRAULICH", "schrift": "Liberation Sans", "groesse_pt": 0 (= automatisch), "farbe": "#c0c0c0", "winkel": -45 | 0,
     "bild": PNG als Base64, "zoom": 0 (= automatisch) | Prozent, "auswaschen": True,
     "h": "mitte" | "links" | "rechts", "h_mm": Abstand vom Rand, "v": "mitte" | "oben" | "unten", "v_mm": …,
     "transparenz": 0…100, "abschnitt": True (gilt nur für diesen Abschnitt),
     "ganzseitig": True (das Bild füllt das ganze Blatt: Grafik eines Deckblatts)}

Ältere Einträge haben nur text, farbe, winkel, groesse_pt; für sie gelten die bisherigen Werte (Mitte, 57 % Deckkraft).

    zeichnen(p, w, rechteck)          # Seite in 96-dpi-Bildpunkten
"""
from __future__ import annotations

import base64

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF
from PySide6.QtGui import QColor, QImage, QPainter

from core.geometrie import Point, Rect
from core.rendering.seite.wasserzeichen import zeichne
from core.dokument.seite import mm_to_px

VORGABEN = ("VERTRAULICH", "NICHT KOPIEREN", "ORIGINAL", "BEISPIEL", "STRENG GEHEIM", "EILT", "ENTWURF", "MUSTER", "KOPIE", "DRINGEND")
GROESSEN = (36, 40, 44, 48, 54, 60, 66, 72, 80, 90, 96, 105, 120, 144)
ZOOMS = (500, 200, 150, 100, 50)
HORIZONTAL = (("mitte", "Zentriert"), ("links", "Links"), ("rechts", "Rechts"))
VERTIKAL = (("mitte", "Zentriert"), ("oben", "Oben"), ("unten", "Unten"))
FORMATE = ((0, "Horizontal"), (-45, "Diagonal"))
STANDARD_FARBE = "#c0c0c0"
ALT_DECKKRAFT = 110 / 255                     # so sahen Wasserzeichen ohne Angabe „transparenz“ bisher aus


def da(w: dict | None) -> bool:
    """Ob das Wasserzeichen etwas zeigt (Text oder Bild)."""
    return bool(w and ((w.get("text") or "").strip() or w.get("bild")))


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
    from vcl.qt.rendering.zeichnen.anzeige import kern_malen
    kern_malen(p, r, lambda z: zeichne(z, standard_engine(), w, Rect(r.x(), r.y(), r.width(), r.height())), rand=0.0)
