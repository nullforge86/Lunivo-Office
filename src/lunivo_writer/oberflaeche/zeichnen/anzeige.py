"""Anzeige fertig gerenderter Dokumentseiten: Der Kern rendert (``core.rendering.rasterziel``, ohne Qt), die Oberfläche legt das Bild nur auf ihren Zeichner."""
from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF
from PySide6.QtGui import QImage, QPainter

from lunivo_writer.kern.geometrie import mm_to_px
from lunivo_writer.kern.rendering import DokumentRenderer
from lunivo_writer.kern.rendering.rasterziel import RasterZiel


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


def seite_malen(p: QPainter, engine, dok, erg, index: int = 0, grund=None, hoechst: float = 4.0) -> None:
    """Die Seite ``index`` mit dem Ursprung links oben auf ``p`` legen (Maße in Bildpunkten bei 96 dpi); die Auflösung folgt dem Maßstab des Zeichners."""
    einr = erg.seiten[index].einrichtung
    b, h = (mm_to_px(einr.width_mm), mm_to_px(einr.height_mm)) if einr is not None else (mm_to_px(210), mm_to_px(297))
    faktor, x, y, bb, hh = _ausgerichtet(p, 0.0, 0.0, b, h, hoechst)
    ziel = RasterZiel(engine, b, h, faktor, (255, 255, 255, 0))
    DokumentRenderer(engine).zeichne_seite(ziel, dok, erg, index, grund)
    breite, hoehe, roh = ziel.als_rgba()
    p.drawImage(QRectF(x, y, breite / faktor, hoehe / faktor), QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888))


def _engine():
    from lunivo_writer.dienste.textsatz import standard_engine
    return standard_engine()


def kern_malen(p: QPainter, bereich: QRectF, zeichne, rand: float = 8.0, hoechst: float = 4.0, ueber: float = 1.0) -> None:
    """Was ``zeichne(ziel)`` auf eine Zeichenfläche des Kerns zeichnet, als fertiges Rasterbild auf ``p`` legen. Koordinaten wie auf dem Zeichner: ``bereich`` ist die
    Fläche (in Koordinaten des Zeichners), die das Bild belegt, ``rand`` Platz ringsum (Schatten, Konturen, Drehung); die Auflösung folgt dem Maßstab des Zeichners.
    ``ueber`` > 1: der Kern rechnet so viel feiner (Überabtastung) und Qt verkleinert glatt auf das Pixelraster — scharfe, glatte Kanten bei kleinen Rundungen und Schrift."""
    b, h = max(1.0, bereich.width() + 2 * rand), max(1.0, bereich.height() + 2 * rand)
    basis, x, y, bb, hh = _ausgerichtet(p, bereich.x() - rand, bereich.y() - rand, b, h, hoechst)
    faktor = basis * ueber
    from lunivo_writer.kern.geometrie import Point
    ziel = RasterZiel(_engine(), bb, hh, faktor, (255, 255, 255, 0))
    ziel.push_state(translate=Point(-x, -y))                                       # die Fläche beginnt am ausgerichteten Ursprung; der Inhalt behält seine Koordinaten
    zeichne(ziel)
    breite, hoehe, roh = ziel.als_rgba()
    if ueber != 1.0:
        p.save()
        p.setRenderHint(QPainter.SmoothPixmapTransform, True)
    p.drawImage(QRectF(x, y, breite / faktor, hoehe / faktor), QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888))
    if ueber != 1.0:
        p.restore()


def kern_bild(breite_px: float, hoehe_px: float, zeichne, grund: tuple = (255, 255, 255, 0), faktor: float = 1.0) -> QImage:
    """Das Bild von ``zeichne(ziel)`` (Kern-Zeichenfläche der Größe ``breite_px`` × ``hoehe_px``, Ursprung links oben) als ``QImage``; ``grund``: Papierfarbe (Standard durchsichtig)."""
    ziel = RasterZiel(_engine(), breite_px, hoehe_px, faktor, grund)
    zeichne(ziel)
    breite, hoehe, roh = ziel.als_rgba()
    return QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888).copy()
