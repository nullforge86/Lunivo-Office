"""Qt-Umsetzung von ``core.textlayout.TextLayoutEngine``: Schriftmaße aus ``QFontMetricsF``, Umbruch aus ``QTextLayout``.

Die Maße sind die Bildpunkte bei 96 dpi wie im übrigen Kern (Schriftgröße in Punkt wird mit 96/72 in Bildpunkte umgerechnet)."""
from __future__ import annotations

from PySide6.QtGui import QFont, QFontMetricsF, QTextLayout, QTextOption

from lunivo_writer.core.textlayout import FontMetrics, FontSpec, GlyphPosition, LineBox, TextLayoutEngine

PX_JE_PT = 96.0 / 72.0


def _schrift(font: FontSpec) -> QFont:
    f = QFont(font.family)
    f.setPixelSize(max(1, round(font.size_pt * PX_JE_PT)))
    f.setWeight(QFont.Weight.Bold if font.weight >= 600 else QFont.Weight.Normal)
    f.setItalic(font.italic)
    return f


class QtTextLayoutEngine(TextLayoutEngine):
    def font_metrics(self, font: FontSpec) -> FontMetrics:
        m = QFontMetricsF(_schrift(font))
        return FontMetrics(m.ascent(), m.descent(), m.lineSpacing())

    def measure_text(self, text: str, font: FontSpec) -> float:
        return QFontMetricsF(_schrift(font)).horizontalAdvance(text)

    def shape_text(self, text: str, font: FontSpec) -> list[GlyphPosition]:
        layout = QTextLayout(text, _schrift(font))
        layout.beginLayout()
        zeile = layout.createLine()
        layout.endLayout()
        if not zeile.isValid():
            return []
        x = [zeile.cursorToX(i)[0] for i in range(len(text) + 1)]                       # cursorToX liefert (x, Lage)
        return [GlyphPosition(i, x[i], x[i + 1] - x[i]) for i in range(len(text))]

    def layout_paragraph(self, text: str, font: FontSpec, width: float) -> list[LineBox]:
        layout = QTextLayout(text, _schrift(font))
        opt = QTextOption()
        opt.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        layout.setTextOption(opt)
        layout.beginLayout()
        zeilen = []
        while True:
            zeile = layout.createLine()
            if not zeile.isValid():
                break
            zeile.setLineWidth(max(1.0, width))
            zeilen.append(LineBox(zeile.textStart(), zeile.textLength(), zeile.naturalTextWidth(), zeile.height(), zeile.ascent()))
        layout.endLayout()
        return zeilen


def _fontspec_aus(f: QFont) -> FontSpec:
    """``FontSpec`` zu einem ``QFont`` (Größe in Punkt, wie ``_schrift`` sie wieder in ganze Bildpunkte rechnet)."""
    px = f.pixelSize() if f.pixelSize() > 0 else round(f.pointSizeF() * PX_JE_PT)
    return FontSpec(f.family(), px / PX_JE_PT, 700 if f.weight() >= QFont.Weight.DemiBold else 400, f.italic())
