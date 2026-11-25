"""Eigene Geometrie ohne Qt: Maße in Bildpunkten (96 dpi), y wächst nach unten. Umrechnung zu und von Qt: ``adapter/qt/geometrie.py``."""
from core.geometrie.margins import Margins
from core.geometrie.point import Point
from core.geometrie.rect import Rect
from core.geometrie.size import Size
from core.geometrie.units import PX_PER_MM, mm_to_px, px_to_mm, umbruchraster

__all__ = ["Margins", "PX_PER_MM", "Point", "Rect", "Size", "mm_to_px", "px_to_mm", "umbruchraster", "GRUNDFORMEN"]

# Erst beim ersten Zugriff geladen.
_SPAET: dict[str, tuple[str, str]] = {"GRUNDFORMEN": ("grundformen", "FORMEN")}

def __getattr__(name: str):
    datei, original = _SPAET.get(name, (None, None))
    if datei == "grundformen":
        from . import grundformen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert
