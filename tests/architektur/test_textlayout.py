"""Textsatz-Schnittstelle (Phase 6): die Basisklasse meldet fehlende Umsetzungen, die Qt-Umsetzung misst und bricht Zeilen um."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import pytest

from lunivo_writer.core.textlayout import FontSpec, TextLayoutEngine


def test_basisklasse_verlangt_umsetzung():
    with pytest.raises(NotImplementedError):
        TextLayoutEngine().measure_text("x", FontSpec("Arial", 11))


def test_qt_umsetzung_misst_und_bricht_um(app):
    from lunivo_writer.adapter.qt.textlayout import QtTextLayoutEngine
    e = QtTextLayoutEngine()
    schrift = FontSpec("Liberation Sans", 11)
    assert e.measure_text("Hallo", schrift) > 0
    assert e.measure_text("Hallo Welt", schrift) > e.measure_text("Hallo", schrift)
    m = e.font_metrics(schrift)
    assert m.line_spacing >= m.ascent + m.descent - 0.5
    lang = "Wort " * 60
    zeilen = e.layout_paragraph(lang, schrift, 200.0)
    assert len(zeilen) > 3 and all(z.width <= 200.5 for z in zeilen)
    assert sum(z.length for z in zeilen) == len(lang)                                # kein Zeichen geht verloren
    glyphen = e.shape_text("abc", schrift)
    assert [g.index for g in glyphen] == [0, 1, 2] and glyphen[1].x > glyphen[0].x


def test_rendering_qt_backend_zeichnet(app):
    from PySide6.QtGui import QImage, QPainter, QColor
    from lunivo_writer.adapter.qt.rendering import QtRenderBackend
    from lunivo_writer.core.geometry import Point, Rect
    from lunivo_writer.core.rendering import RenderBackend, Style
    with pytest.raises(NotImplementedError):
        RenderBackend().draw_line(Point(0, 0), Point(1, 1), Style())
    img = QImage(40, 40, QImage.Format_RGB32); img.fill(QColor("white"))
    p = QPainter(img)
    b = QtRenderBackend(p)
    b.draw_rect(Rect(5, 5, 20, 20), Style(color=(255, 0, 0, 255), width=0, filled=True))
    b.draw_line(Point(0, 35), Point(39, 35), Style(color=(0, 0, 255, 255), width=1))
    p.end()
    assert QColor(img.pixel(10, 10)).red() == 255 and QColor(img.pixel(10, 35)).blue() > 200
