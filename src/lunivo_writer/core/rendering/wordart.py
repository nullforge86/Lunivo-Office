"""WordArt ohne Qt: Text mit Farbverlauf, Kontur und Schatten als Zeichenanweisungen für ein ``RenderTarget`` (die Galerie „Formatvorlage“ von WordArt)."""
from __future__ import annotations

from lunivo_writer.core.geometry import Point
from lunivo_writer.core.rendering.backend import LinearGradient, RenderTarget, Style, rgba
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine

RAND = 20                                        # Bildpunkte Rand um den Text


def masse(engine: TextLayoutEngine, text: str, schrift: str, pt: float) -> tuple[int, int]:
    """Größe des Bildes (Breite, Höhe) für den Text."""
    f = FontSpec(schrift, pt, 700)
    m = engine.font_metrics(f)
    return int(engine.measure_text(text, f)) + 2 * RAND, int(m.ascent + m.descent) + 2 * RAND


def zeichne(b: RenderTarget, engine: TextLayoutEngine, text: str, vorlage: tuple, schrift: str = "Liberation Sans", pt: float = 48) -> None:
    """WordArt nach einer Vorlage ``(Name, Füllung oben, Füllung unten, Kontur oder None, Konturbreite, Schatten oder None)``: Schatten, dann Verlaufsfüllung mit Kontur."""
    _n, f1, f2, kontur, kb, schatten = vorlage
    f = FontSpec(schrift, pt, 700)
    m = engine.font_metrics(f)
    _bw, h = masse(engine, text, schrift, pt)
    ursprung = Point(RAND, RAND + m.ascent)
    if schatten:
        d = max(2.0, pt / 14)
        b.push_state(translate=Point(d, d))                      # der Schatten ist der Text, um (d, d) verschoben
        b.draw_text_path(text, f, ursprung, Style(color=rgba(schatten), width=0, filled=True))
        b.pop_state()
    verlauf = LinearGradient(Point(0, RAND), Point(0, h - RAND), ((0.0, rgba(f1)), (1.0, rgba(f2))))
    b.draw_text_path(text, f, ursprung, Style(color=rgba(kontur) if kontur else (0, 0, 0, 255), width=kb * max(1.0, pt / 36) if kontur else 0, filled=True,
                                              fill=verlauf, join="round"))
