"""Anzeige fertig gerenderter Bilder des Kerns: Der Kern rendert (ohne Qt, erreichbar über ``writer.anbindung.zeichnen``), die Oberfläche legt das Rasterbild nur auf ihren Zeichner."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QImage, QPainter



def _ausgerichtet(p: QPainter, x: float, y: float, b: float, h: float, hoechst: float) -> tuple:
    """Das Bild passgenau auf das Pixelraster des Bildschirms legen: → ``(Faktor, x, y, Breite, Höhe)`` in Koordinaten des Zeichners. Der Faktor enthält die Bildschirm-
    skalierung (HiDPI); Ursprung und Größe liegen auf ganzen Bildschirmpixeln, so wird jedes Bildpixel genau ein Bildschirmpixel (nichts wird verschmiert)."""
    t = p.worldTransform()
    dpr = p.device().devicePixelRatioF() if p.device() is not None else 1.0
    faktor = max(0.5, min(hoechst, math.hypot(t.m11(), t.m12()) * dpr))
    umkehr, ok = t.inverted()
    if not ok or abs(t.m12()) > 1e-6 or abs(t.m21()) > 1e-6:                      # gedrehter Zeichner: keine Ausrichtung möglich
        return faktor, x, y, b, h
    gx, gy = t.map(QPointF(x, y)).x() * dpr, t.map(QPointF(x, y)).y() * dpr
    ax, ay = math.floor(gx + 0.5) / dpr, math.floor(gy + 0.5) / dpr
    o = umkehr.map(QPointF(ax, ay))
    return faktor, o.x(), o.y(), math.ceil(b * faktor) / faktor, math.ceil(h * faktor) / faktor


def seite_malen(p: QPainter, breite_px: float, hoehe_px: float, erzeuge, hoechst: float = 4.0) -> None:
    """Ein vom Kern gesetztes Blatt der Größe ``breite_px`` × ``hoehe_px`` (Bildpunkte bei 96 dpi) mit dem Ursprung links oben auf ``p`` legen; die Auflösung
    folgt dem Maßstab des Zeichners. ``erzeuge(faktor)`` → ``(breite, hoehe, rgba)`` liefert das Rasterbild in dieser Auflösung (über ``writer.anbindung.zeichnen``)."""
    faktor, x, y, bb, hh = _ausgerichtet(p, 0.0, 0.0, breite_px, hoehe_px, hoechst)
    breite, hoehe, roh = erzeuge(faktor)
    p.drawImage(QRectF(x, y, breite / faktor, hoehe / faktor), QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888))


def raster_malen(p: QPainter, bereich: QRectF, erzeuge, rand: float = 8.0, hoechst: float = 4.0, ueber: float = 1.0) -> None:
    """Was der Kern über ``writer.anbindung.zeichnen`` zeichnet, als fertiges Rasterbild auf ``p`` legen: ``erzeuge(flaeche)`` → ``(breite, hoehe, rgba)``; ``flaeche``
    ist ``(Breite, Höhe, Faktor, x, y, Papierfarbe)`` in Koordinaten des Zeichners. ``bereich`` ist die Fläche (in Koordinaten des Zeichners), die das Bild belegt,
    ``rand`` Platz ringsum (Schatten, Konturen, Drehung); die Auflösung folgt dem Maßstab des Zeichners. ``ueber`` > 1: der Kern rechnet so viel feiner
    (Überabtastung) und Qt verkleinert glatt auf das Pixelraster — scharfe, glatte Kanten bei kleinen Rundungen und Schrift."""
    b, h = max(1.0, bereich.width() + 2 * rand), max(1.0, bereich.height() + 2 * rand)
    basis, x, y, bb, hh = _ausgerichtet(p, bereich.x() - rand, bereich.y() - rand, b, h, hoechst)
    faktor = basis * ueber
    breite, hoehe, roh = erzeuge((bb, hh, faktor, x, y, (255, 255, 255, 0)))
    if ueber != 1.0:
        p.save()
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
    p.drawImage(QRectF(x, y, breite / faktor, hoehe / faktor), QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888))
    if ueber != 1.0:
        p.restore()


def raster_bild(breite_px: float, hoehe_px: float, erzeuge, grund: tuple = (255, 255, 255, 0), faktor: float = 1.0) -> QImage:
    """Das Bild, das der Kern über ``writer.anbindung.zeichnen`` zeichnet (Fläche der Größe ``breite_px`` × ``hoehe_px``, Ursprung links oben), als ``QImage``:
    ``erzeuge(flaeche)`` → ``(breite, hoehe, rgba)``; ``grund``: Papierfarbe (Standard durchsichtig)."""
    breite, hoehe, roh = erzeuge((breite_px, hoehe_px, faktor, 0.0, 0.0, tuple(grund)))
    return QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888).copy()
