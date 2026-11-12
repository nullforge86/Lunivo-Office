"""Eigene Geometrie ohne Qt: Maße in Bildpunkten (96 dpi), y wächst nach unten. Umrechnung zu und von Qt: ``adapter/qt/geometrie.py``."""
from lunivo_writer.core.geometry.margins import Margins
from lunivo_writer.core.geometry.point import Point
from lunivo_writer.core.geometry.rect import Rect
from lunivo_writer.core.geometry.size import Size

__all__ = ["Margins", "Point", "Rect", "Size"]
