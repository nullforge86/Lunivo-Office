"""Der Rahmen um die Seite („Rahmen und Schattierung“ ▸ Seitenrand): Lage, Abstände, Kunstrahmen.

Ein Seitenrahmen ist ein Wörterbuch (``PageSettings.border``): ``farbe``, ``breite_pt``, ``art`` (Linienart), ``seiten`` („tblr“) und dazu

* ``abstand``: "oben,unten,links,rechts" in pt; fehlt es, gilt ``abstand_mm`` (ältere Dateien) rundherum
* ``messen``: "text" (vom Text aus nach außen) oder "seitenrand" (vom Blattrand nach innen); ohne Angabe: Seitenrand
* ``ausrichten``: Absatzrahmen und Tabellenränder am Seitenrand ausrichten; ``vordergrund`` (Vorgabe: an); ``kopf`` / ``fuss``: Kopf-/Fußzeile umgeben
* ``kunst``: Art des Rahmens aus ``KUNST`` (leer = Linie)
"""
from __future__ import annotations

from PySide6.QtCore import QRectF

from writer.anbindung import zeichnen as ZW
from writer.anbindung.seitenrahmen import abstaende_pt  # noqa: F401  (Rechnung und Zeichnen: Kern; ``abstaende_pt`` für das Rahmenfenster)

KUNST = (("", "(keine)"), ("stars", "Sterne"), ("hearts", "Herzen"), ("triangles", "Dreiecke"), ("gems", "Edelsteine"), ("zigZag", "Zickzack"))


def _raender_mm(page) -> tuple[float, float, float, float]:
    return page.margin_left_mm, page.margin_top_mm, page.margin_right_mm, page.margin_bottom_mm


def rechteck(b: dict, page, seite: QRectF) -> QRectF:
    """Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite`` (gerechnet im Kern)."""
    return QRectF(*ZW.seitenrahmen_rechteck(b, _raender_mm(page), (seite.x(), seite.y(), seite.width(), seite.height())))


def zeichnen(p, b: dict, page, seite: QRectF) -> None:
    """Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen), über das Rendering-Backend."""
    from vcl.qt.rendering.formen.anzeige import raster_malen
    raender, r = _raender_mm(page), (seite.x(), seite.y(), seite.width(), seite.height())
    raster_malen(p, seite, lambda f: ZW.seitenrahmen(f, b, raender, r), rand=16.0)
