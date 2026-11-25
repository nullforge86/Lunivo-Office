"""Dokumenttext zeichnen, ohne dass die Zeichenfläche Schriften kennt: Die Glyphenkonturen kommen aus der Textsatz-Engine des Kerns (FreeType, HarfBuzz) und gehen als
gefüllter Pfad an ``draw_path``. Schrift, Größe (auch Bruchgrößen), Vorschübe und Kerning bestimmt allein der Kern."""
from __future__ import annotations

from lunivo_writer.kern.geometrie import Point
from lunivo_writer.kern.textsatz.engine import FontSpec
from ..schrift import HarfBuzzEngine
from .backend import RenderTarget, Style

_engine: HarfBuzzEngine | None = None


def gemeinsame_engine() -> HarfBuzzEngine:
    """Die Engine, deren Schriftcache alle Zeichenvorgänge teilen."""
    global _engine
    if _engine is None:
        _engine = HarfBuzzEngine()
    return _engine


def zeichne_text(b: RenderTarget, text: str, position: Point, font, style: Style, engine=None) -> None:
    """``text`` mit der Grundlinie bei ``position.y`` ab ``position.x`` als gefüllte Glyphenpfade zeichnen."""
    if not text:
        return
    if getattr(b, "glyphen_aus_kern", False) or not isinstance(font, FontSpec):      # Ausgabe des Kerns (echter Text mit eingebetteter Schrift) oder kein Schriftbeschreiber des Kerns
        b.draw_text(text, position, font, style)
        return
    ops = (engine or gemeinsame_engine()).glyphen_pfad(text, font, position.x, position.y)
    if ops:
        b.draw_path(ops, Style(color=style.color, width=0, filled=True), True, True)           # Nichtnull-Regel: sich überlappende Konturen bleiben gefüllt


def zeichne_text_kontur(b: RenderTarget, text: str, font, origin: Point, style: Style, engine=None) -> None:
    """Wie ``zeichne_text``, aber mit dem Stil des Aufrufers (Füllung und Kontur, zum Beispiel für WordArt)."""
    if not text:
        return
    if not isinstance(font, FontSpec):
        b.draw_text_path(text, font, origin, style)
        return
    ops = (engine or gemeinsame_engine()).glyphen_pfad(text, font, origin.x, origin.y)
    if ops:
        b.draw_path(ops, style, True, False)


class TextAusKern:
    """Textkasten, Textmaße und Texteffekte für Zeichenflächen des Kerns, allein aus der Engine (``self.engine``) und ``draw_text`` / ``draw_path`` der Fläche."""

    def _zeilen(self, text: str, font: FontSpec, breite: float, wrap: bool) -> list[str]:
        aus = []
        for absatz in text.split("\n"):
            if not wrap or not absatz:
                aus.append(absatz)
                continue
            for box in self.engine.layout_paragraph(absatz, font, max(1.0, breite)):
                aus.append(absatz[box.start:box.start + box.length])
        return aus

    def draw_text_box(self, text: str, rect, font, style: Style, align: str = "left", wrap: bool = True, valign: str = "center") -> None:
        if not isinstance(font, FontSpec):
            return
        zeilen = self._zeilen(text, font, rect.width, wrap)
        m = self.engine.font_metrics(font)
        gesamt = len(zeilen) * m.line_spacing
        y = rect.y + (0.0 if valign == "top" else max(0.0, (rect.height - gesamt) / 2) if valign == "center" else max(0.0, rect.height - gesamt))
        for z in zeilen:
            b = self.engine.measure_text(z.rstrip(), font)
            x = rect.x + (rect.width - b) / 2 if align == "center" else rect.x + rect.width - b if align == "right" else rect.x
            self.draw_text(z.rstrip(), Point(x, y + m.ascent), font, style)
            y += m.line_spacing

    def text_bounds(self, text: str, rect, font, align: str = "left", wrap: bool = True):
        from lunivo_writer.kern.geometrie import Rect
        if not isinstance(font, FontSpec):
            return Rect(rect.x, rect.y, 0.0, 0.0)
        zeilen = self._zeilen(text, font, rect.width, wrap)
        return Rect(rect.x, rect.y, max((self.engine.measure_text(z.rstrip(), font) for z in zeilen), default=0.0), len(zeilen) * self.engine.font_metrics(font).line_spacing)

    def draw_text_path(self, text: str, font, origin: Point, style: Style) -> None:
        if isinstance(font, FontSpec):
            self.draw_path(self.engine.glyphen_pfad(text, font, origin.x, origin.y), style)

    def draw_text_effects(self, text: str, font, origin: Point, color: tuple, effects, contour, highlight, width: float, line_height: float, ascent: float, underline: bool = False) -> None:
        from lunivo_writer.kern.geometrie import Rect
        if effects:
            self.hinweise.append("Texteffekte stehen in dieser Ausgabe als einfacher Text.")
        if highlight:
            self.draw_rect(Rect(origin.x, origin.y - ascent, width, line_height), Style(color=highlight, width=0, filled=True))
        self.draw_text(text, origin, font, Style(color=color))
        if underline:
            self.draw_line(Point(origin.x, origin.y + 2), Point(origin.x + width, origin.y + 2), Style(color=color, width=1.0))
