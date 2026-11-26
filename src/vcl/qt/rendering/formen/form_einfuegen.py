"""Form einfuegen: aus ``vcl.qt.rendering.formen.einfuegen`` herausgelöst."""
from __future__ import annotations
import math
from PySide6.QtCore import QRectF
from PySide6.QtGui import QImage
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.rendering.formen import formen_katalog as K


# ---- Formen ---------------------------------------------------------------------------------------------------
TEXTFELD_VERTIKAL = "Textfeld vertikal"


# ---- Formen: Umrisse als Vektoranweisungen, gezeichnet vom Kern (Qt hält nur Katalogpfade als Geometrie) ----------------------------
_GRUNDFORMEN = ("Rechteck", "Abgerundetes Rechteck", "Ellipse", "Dreieck", "Raute", "Pfeil nach rechts", "Stern", "Sprechblase", "Linie")


_KAPPA = 0.5522847498


def _abgerundet(x: float, y: float, w: float, h: float, rad: float) -> list:
    rad = min(rad, w / 2, h / 2)
    k = rad * _KAPPA
    r, b = x + w, y + h
    return [("M", x + rad, y), ("L", r - rad, y), ("C", r - rad + k, y, r, y + rad - k, r, y + rad), ("L", r, b - rad), ("C", r, b - rad + k, r - rad + k, b, r - rad, b),
            ("L", x + rad, b), ("C", x + rad - k, b, x, b - rad + k, x, b - rad), ("L", x, y + rad), ("C", x, y + rad - k, x + rad - k, y, x + rad, y), ("Z",)]


def _polygon(punkte: list) -> list:
    return [("M", *punkte[0])] + [("L", *q) for q in punkte[1:]] + [("Z",)]


def _form_pfad(art: str, r, adj, punkte):
    """(Umriss als Pfad, offen?) für Freiformen, Anpassungsformen und Katalogformen; ``None`` für die eingebauten Grundformen."""
    if punkte:
        from vcl.qt.rendering.formen import freiform as FF
        return FF.pfad(punkte, r), not FF.geschlossen(punkte)
    if adj and K.anpassbar(art):
        return K.pfad(art, r, adj), False
    if art not in _GRUNDFORMEN and K.hat(art):
        return K.pfad(art, r), bool(K.ist_linie(art))
    return None


def _grundform_ops(art: str, x: float, y: float, w: float, h: float) -> tuple[list, bool]:
    """(Umriss, offen?) einer eingebauten Grundform im Rechteck (x, y, w, h)."""
    cx, cy = x + w / 2, y + h / 2
    if art == "Abgerundetes Rechteck":
        return _abgerundet(x, y, w, h, 16), False
    if art == "Ellipse":
        return [("E", cx, cy, w / 2, h / 2)], False
    if art == "Dreieck":
        return _polygon([(cx, y), (x + w, y + h), (x, y + h)]), False
    if art == "Raute":
        return _polygon([(cx, y), (x + w, cy), (cx, y + h), (x, cy)]), False
    if art == "Pfeil nach rechts":
        h4, r3 = h / 4, x + w - w * .3
        return _polygon([(x, y + h4), (r3, y + h4), (r3, y), (x + w, cy), (r3, y + h), (r3, y + h - h4), (x, y + h - h4)]), False
    if art == "Stern":
        ra, ri = min(w, h) / 2, min(w, h) / 4.6
        return _polygon([(cx + (ra if i % 2 == 0 else ri) * math.cos(-math.pi / 2 + i * math.pi / 5), cy + (ra if i % 2 == 0 else ri) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(10)]), False
    if art == "Sprechblase":
        korper_h = h * 0.78
        spitze = _polygon([(x + w * .2, y + korper_h - 1), (x + w * .12, y + h), (x + w * .36, y + korper_h - 1)])
        return _abgerundet(x, y, w, korper_h, 14) + spitze, False
    if art == "Linie":
        return [("M", x, cy), ("L", x + w, cy)], True
    return [("R", x, y, w, h)], False                                    # Rechteck und das Textfeld mit senkrechtem Text


def form_bild(art: str, breite: int = 240, hoehe: int = 140, fuell: str = Farbe.AKZENT_DUNKEL, linie: str = Farbe.FORM_LINIE,
              strich: float = 2.0, text: str = "", skala: float = 1.0, adj=None, fuell_art: str = "", punkte=None) -> QImage:
    """``skala``: Bild in dieser Auflösung (Maße und Strich bleiben logisch, das Bild ist ``skala``-mal so groß) — für scharfe freie Formen.
    ``adj``: Parameter der Anpassungsgriffe (``formen_anpassen``); ``fuell_art``: Verlauf der Füllung; ``punkte``: Punktliste einer Freiform (``editor/objekte/freiform.py``).
    Gezeichnet wird vom Kern (``RasterZiel``); Qt liefert nur den Pfad der Katalog- und Freiformen als Geometrie."""
    from vcl.qt.rendering.formen.anzeige import raster_bild
    from vcl.qt.rendering.formen.pfad import pfad_zu_vektor
    from writer.anbindung import zeichnen as ZW
    strich = max(float(strich), 1.0)                         # eine Haarlinie (Word: 0,25–0,75 pt) bleibt auf dem Bildschirm mindestens einen Bildpunkt dick
    x, y, w, h = strich, strich, breite - 2 * strich, hoehe - 2 * strich
    r = QRectF(x, y, w, h)
    gefunden = _form_pfad(art, r, adj, punkte)
    if gefunden is not None:
        ops, offen = list(pfad_zu_vektor(gefunden[0]).ops), gefunden[1]
    else:
        ops, offen = _grundform_ops(art, x, y, w, h)

    return raster_bild(breite, hoehe, lambda f: ZW.form(f, ops, offen, art == "Linie", art == TEXTFELD_VERTIKAL, (x, y, w, h), fuell, fuell_art, linie, strich, text),
                       faktor=skala)
