"""Rendering-Schnittstelle ohne Qt (Phase 8 der Qt-Entkopplung). Die Layout-Schicht liefert Zeichenanweisungen, ein Backend setzt sie um.
Qt bleibt als Backend in ``adapter/qt/rendering.py``; ein anderes Backend (PDF-Writer, Bildausgabe) braucht nur diese Schnittstelle.

Maßgeblich ist ``DokumentRenderer`` (``renderer.py``) über ``core.document.Dokument`` und ``core.layout.LayoutErgebnis``."""
from core.layout.drucklayout.ausgabe.backend import ImageFill, LinearGradient, PatternFill, RadialGradient, RenderBackend, RenderTarget, Style, TextureFill, rgba
from core.layout.drucklayout.ausgabe.renderer import DokumentRenderer
from core.layout.drucklayout.ausgabe.objekte.auswahlrenderer import zeichne_auswahl, zeichne_cursor

__all__ = ["DokumentRenderer", "ImageFill", "LinearGradient", "PatternFill", "RadialGradient", "RenderBackend", "RenderTarget", "Style", "TextureFill", "rgba",
           "zeichne_auswahl", "zeichne_cursor"]
