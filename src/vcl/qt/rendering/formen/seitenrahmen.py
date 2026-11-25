"""Der Rahmen um die Seite („Rahmen und Schattierung“ ▸ Seitenrand): Lage, Abstände, Kunstrahmen.

Ein Seitenrahmen ist ein Wörterbuch (``PageSettings.border``): ``farbe``, ``breite_pt``, ``art`` (Linienart), ``seiten`` („tblr“) und dazu

* ``abstand``: "oben,unten,links,rechts" in pt; fehlt es, gilt ``abstand_mm`` (ältere Dateien) rundherum
* ``messen``: "text" (vom Text aus nach außen) oder "seitenrand" (vom Blattrand nach innen); ohne Angabe: Seitenrand
* ``ausrichten``: Absatzrahmen und Tabellenränder am Seitenrand ausrichten; ``vordergrund`` (Vorgabe: an); ``kopf`` / ``fuss``: Kopf-/Fußzeile umgeben
* ``kunst``: Art des Rahmens aus ``KUNST`` (leer = Linie)
"""
from __future__ import annotations

from PySide6.QtCore import QRectF

from core.geometrie import Rect
from core.layout.drucklayout.ausgabe.seite.seitenrahmen import rechteck as _rechteck, zeichnen as _zeichnen
from writer.anbindung.seitenrahmen import abstaende_pt  # noqa: F401  (Rechnung und Zeichnen: Kern; ``abstaende_pt`` für das Rahmenfenster)

KUNST = (("", "(keine)"), ("stars", "Sterne"), ("hearts", "Herzen"), ("triangles", "Dreiecke"), ("gems", "Edelsteine"), ("zigZag", "Zickzack"))


def rechteck(b: dict, page, seite: QRectF) -> QRectF:
    """Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite`` (Qt-Hülle um ``core.layout.drucklayout.ausgabe.seitenrahmen.rechteck``)."""
    r = _rechteck(b, page, Rect(seite.x(), seite.y(), seite.width(), seite.height()))
    return QRectF(r.x, r.y, r.width, r.height)


def zeichnen(p, b: dict, page, seite: QRectF) -> None:
    """Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen), über das Rendering-Backend."""
    from vcl.qt.rendering.formen.anzeige import kern_malen
    kern_malen(p, seite, lambda z: _zeichnen(z, b, page, Rect(seite.x(), seite.y(), seite.width(), seite.height())), rand=16.0)
