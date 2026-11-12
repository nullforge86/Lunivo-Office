"""Seitenschmuck ohne Qt: Seitenfarbe, Seitenrahmen und Wasserzeichen einer Seite in der richtigen Reihenfolge und Schicht (hinter oder vor dem Text)."""
from __future__ import annotations

from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.rendering import seitenrahmen as SR, wasserzeichen as WZ
from lunivo_writer.core.rendering.backend import RenderBackend, Style, rgba
from lunivo_writer.core.textlayout.engine import TextLayoutEngine

PX_JE_MM = 96.0 / 25.4


def zeichne_seitenschmuck(b: RenderBackend, engine: TextLayoutEngine, page, hintergrund: bool = True, flaeche: Rect | None = None, rahmen: str = "immer",
                          wasserzeichen: bool = True) -> None:
    """Seitenfarbe, Seitenrahmen und Wasserzeichen. Maße in 96-dpi-Bildpunkten, Ursprung links oben; ``flaeche`` überschreibt das Seitenrechteck.
    ``rahmen``: der Rahmen liegt über dem Text (``"vorn"``) oder dahinter (``"hinten"``, „Immer im Vordergrund anzeigen“ aus); ``"immer"`` zeichnet ihn in jedem Fall."""
    r = flaeche or Rect(0, 0, page.width_mm * PX_JE_MM, page.height_mm * PX_JE_MM)
    if hintergrund and page.color:
        b.draw_rect(r, Style(color=rgba(page.color), width=0, filled=True))
    rb = page.border
    if rb and (rahmen == "immer" or (rahmen == "vorn") == bool(rb.get("vordergrund", True))):
        SR.zeichnen(b, rb, page, r)
    if wasserzeichen and page.watermark:
        WZ.zeichne(b, engine, page.watermark, r)
