"""Wasserzeichen einer Seite: Text oder Bild, mit Lage, Größe und Transparenz (Einfügen ▸ Wasserzeichen). Keine Oberfläche.

Ein Wasserzeichen ist ein Wörterbuch in ``PageSettings.watermark``:

    {"text": "VERTRAULICH", "schrift": "Liberation Sans", "groesse_pt": 0 (= automatisch), "farbe": "#c0c0c0", "winkel": -45 | 0,
     "bild": PNG als Base64, "zoom": 0 (= automatisch) | Prozent, "auswaschen": True,
     "h": "mitte" | "links" | "rechts", "h_mm": Abstand vom Rand, "v": "mitte" | "oben" | "unten", "v_mm": …,
     "transparenz": 0…100, "abschnitt": True (gilt nur für diesen Abschnitt)}

Ältere Einträge haben nur text, farbe, winkel, groesse_pt; für sie gelten die bisherigen Werte (Mitte, 57 % Deckkraft).

    zeichnen(p, w, rechteck)          # Seite in 96-dpi-Bildpunkten
"""
from __future__ import annotations

import base64

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QImage, QPainter

from lunivo_writer.models.page import mm_to_px

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


def ausgewaschen(img: QImage) -> QImage:
    """„Auswaschen“ wie in Textverarbeitungen: hell und kontrastarm (85 % zum Weiß hin)."""
    out = img.convertToFormat(QImage.Format_ARGB32)
    p = QPainter(out)
    p.setCompositionMode(QPainter.CompositionMode_SourceAtop)
    p.fillRect(out.rect(), QColor(255, 255, 255, 217))
    p.end()
    return out


def _deckkraft(w: dict) -> float:
    if "transparenz" not in w:
        return ALT_DECKKRAFT
    return max(0.0, min(1.0, 1.0 - float(w["transparenz"]) / 100.0))


def _lage(w: dict, r: QRectF, b: float, h: float) -> QPointF:
    """Mittelpunkt des Wasserzeichens (Breite b, Höhe h) im Seitenrechteck r."""
    x = {"links": r.left() + mm_to_px(float(w.get("h_mm", 0))) + b / 2,
         "rechts": r.right() - mm_to_px(float(w.get("h_mm", 0))) - b / 2}.get(w.get("h", "mitte"), r.center().x())
    y = {"oben": r.top() + mm_to_px(float(w.get("v_mm", 0))) + h / 2,
         "unten": r.bottom() - mm_to_px(float(w.get("v_mm", 0))) - h / 2}.get(w.get("v", "mitte"), r.center().y())
    return QPointF(x, y)


def schrift(w: dict, r: QRectF) -> QFont:
    """Schrift des Textwasserzeichens; „automatisch“ füllt die Seite (waagerecht 80 % der Breite, schräg 78 % der Diagonale)."""
    f = QFont(w.get("schrift") or "Liberation Sans")
    f.setBold(True)
    pt = float(w.get("groesse_pt", 80) or 0)
    if pt > 0:
        f.setPixelSize(max(4, int(pt * 96 / 72)))
        return f
    f.setPixelSize(100)
    breite = QFontMetricsF(f).horizontalAdvance(w.get("text") or "") or 1
    laenge = (r.width() ** 2 + r.height() ** 2) ** 0.5 * 0.78 if w.get("winkel", -45) else r.width() * 0.8
    f.setPixelSize(max(4, min(int(r.height() * 0.4), int(100 * laenge / breite))))
    return f


def zeichnen(p: QPainter, w: dict | None, r: QRectF) -> None:
    """Das Wasserzeichen ``w`` auf die Seite ``r`` (96-dpi-Bildpunkte) zeichnen."""
    if not da(w):
        return
    p.save()
    p.setOpacity(p.opacity() * _deckkraft(w))
    winkel = float(w.get("winkel", -45) or 0)
    if w.get("bild"):
        img = bild_aus_text(w["bild"])
        if not img.isNull():
            if w.get("auswaschen", True):
                img = ausgewaschen(img)
            zoom = float(w.get("zoom", 0) or 0)
            if zoom > 0:
                b, h = img.width() * zoom / 100, img.height() * zoom / 100
            else:                                                     # automatisch: in die Seite mit 15 % Rand
                f = min(r.width() * 0.7 / max(1, img.width()), r.height() * 0.7 / max(1, img.height()))
                b, h = img.width() * f, img.height() * f
            p.translate(_lage(w, r, b, h)); p.rotate(winkel)
            p.setRenderHint(QPainter.SmoothPixmapTransform)
            p.drawImage(QRectF(-b / 2, -h / 2, b, h), img)
    else:
        text = w["text"]
        f = schrift(w, r)
        p.setFont(f)
        p.setPen(QColor(w.get("farbe") or STANDARD_FARBE))
        fm = QFontMetricsF(f)
        b, h = fm.horizontalAdvance(text), fm.height()
        p.translate(_lage(w, r, b, h)); p.rotate(winkel)
        p.drawText(QRectF(-r.width(), -h / 2, 2 * r.width(), h), Qt.AlignCenter, text)
    p.restore()
