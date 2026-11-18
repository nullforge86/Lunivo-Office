"""Der Rahmen um die Seite („Rahmen und Schattierung“ ▸ Seitenrand): Lage, Abstände, Kunstrahmen.

Ein Seitenrahmen ist ein Wörterbuch (``PageSettings.border``): ``farbe``, ``breite_pt``, ``art`` (Linienart), ``seiten`` („tblr“) und dazu

* ``abstand``: "oben,unten,links,rechts" in pt; fehlt es, gilt ``abstand_mm`` (ältere Dateien) rundherum
* ``messen``: "text" (vom Text aus nach außen) oder "seitenrand" (vom Blattrand nach innen); ohne Angabe: Seitenrand
* ``ausrichten``: Absatzrahmen und Tabellenränder am Seitenrand ausrichten; ``vordergrund`` (Vorgabe: an); ``kopf`` / ``fuss``: Kopf-/Fußzeile umgeben
* ``kunst``: Art des Rahmens aus ``KUNST`` (leer = Linie)
"""
from __future__ import annotations

from PySide6.QtCore import QRectF

from lunivo_writer.adapter.qt.rendering import QtRenderBackend
from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.rendering.seitenrahmen import KOPF_MM, abstaende_pt, kunst_zeichnen, rechteck as _rechteck, zeichnen as _zeichnen  # noqa: F401  (Rechnung und Zeichnen: Kern)

KUNST = (("", "(keine)"), ("stars", "Sterne"), ("hearts", "Herzen"), ("triangles", "Dreiecke"), ("gems", "Edelsteine"), ("zigZag", "Zickzack"))


def rechteck(b: dict, page, seite: QRectF) -> QRectF:
    """Das Rechteck des Rahmens in Bildpunkten, auf einer Seite mit dem Rechteck ``seite`` (Qt-Hülle um ``core.rendering.seitenrahmen.rechteck``)."""
    r = _rechteck(b, page, Rect(seite.x(), seite.y(), seite.width(), seite.height()))
    return QRectF(r.x, r.y, r.width, r.height)


def zeichnen(p, b: dict, page, seite: QRectF) -> None:
    """Den Seitenrahmen auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen), über das Rendering-Backend."""
    _zeichnen(QtRenderBackend(p), b, page, Rect(seite.x(), seite.y(), seite.width(), seite.height()))
