"""Rendering-Schnittstelle ohne Qt (Phase 8 der Qt-Entkopplung). Die Layout-Schicht liefert Zeichenanweisungen, ein Backend setzt sie um.
Qt bleibt als Backend in ``adapter/qt/rendering.py``; ein anderes Backend (PDF-Writer, Bildausgabe) braucht nur diese Schnittstelle."""
from lunivo_writer.core.rendering.backend import ImageFill, LinearGradient, PatternFill, RadialGradient, RenderBackend, RenderTarget, Style, TextureFill, rgba
from lunivo_writer.core.rendering.dokument import zeichne_dokumentseite

__all__ = ["ImageFill", "LinearGradient", "PatternFill", "RadialGradient", "RenderBackend", "RenderTarget", "Style", "TextureFill", "rgba", "zeichne_dokumentseite"]
