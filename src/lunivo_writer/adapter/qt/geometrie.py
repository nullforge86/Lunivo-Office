"""Qt-Geometrie ↔ ``core.geometry`` (alle Maße in Bildpunkten, y nach unten — wie bei Qt, also ohne Umrechnung der Einheit)."""
from __future__ import annotations

from PySide6.QtCore import QMarginsF, QPointF, QRectF, QSizeF

from lunivo_writer.core.geometry import Margins, Point, Rect, Size


def point_from_qt(p) -> Point:
    """``QPointF`` oder ``QPoint`` → ``Point``."""
    return Point(float(p.x()), float(p.y()))


def point_to_qt(p: Point) -> QPointF:
    return QPointF(p.x, p.y)


def size_from_qt(s) -> Size:
    """``QSizeF`` oder ``QSize`` → ``Size``."""
    return Size(float(s.width()), float(s.height()))


def size_to_qt(s: Size) -> QSizeF:
    return QSizeF(s.width, s.height)


def rect_from_qt(r) -> Rect:
    """``QRectF`` oder ``QRect`` → ``Rect``."""
    return Rect(float(r.x()), float(r.y()), float(r.width()), float(r.height()))


def rect_to_qt(r: Rect) -> QRectF:
    return QRectF(r.x, r.y, r.width, r.height)


def margins_from_qt(m) -> Margins:
    """``QMarginsF`` oder ``QMargins`` → ``Margins``."""
    return Margins(float(m.left()), float(m.top()), float(m.right()), float(m.bottom()))


def margins_to_qt(m: Margins) -> QMarginsF:
    return QMarginsF(m.left, m.top, m.right, m.bottom)
