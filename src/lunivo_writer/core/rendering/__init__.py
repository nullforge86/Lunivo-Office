"""Rendering-Schnittstelle ohne Qt (Phase 8 der Qt-Entkopplung). Die Layout-Schicht liefert Zeichenanweisungen, ein Backend setzt sie um.
Qt bleibt als Backend in ``adapter/qt/rendering.py``; ein anderes Backend (PDF-Writer, Bildausgabe) braucht nur diese Schnittstelle.

Maßgeblich ist ``DokumentRenderer`` (``renderer.py``) über ``core.document.Dokument`` und ``core.layout.LayoutErgebnis``;
``zeichne_dokumentseite`` arbeitet auf dem bisherigen Modell und entfällt, sobald seine Aufrufstellen umgestellt sind."""
from .backend import ImageFill, LinearGradient, PatternFill, RadialGradient, RenderBackend, RenderTarget, Style, TextureFill, rgba
from .dokument import zeichne_dokumentseite
from .renderer import DokumentRenderer
from .auswahlrenderer import zeichne_auswahl, zeichne_cursor

__all__ = ["DokumentRenderer", "ImageFill", "LinearGradient", "PatternFill", "RadialGradient", "RenderBackend", "RenderTarget", "Style", "TextureFill", "rgba",
           "zeichne_auswahl", "zeichne_cursor", "zeichne_dokumentseite"]
