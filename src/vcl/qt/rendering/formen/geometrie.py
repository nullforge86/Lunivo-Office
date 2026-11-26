"""Qt-Geometrie ↔ Geometrie der Oberfläche ohne Qt (``writer.werte``; alle Maße in Bildpunkten, y nach unten — wie bei Qt, also ohne Umrechnung der Einheit)."""
from __future__ import annotations

from PySide6.QtCore import QMarginsF, QPointF, QRectF, QSizeF

from writer.werte import Groesse, Punkt, Raender, Rechteck


def point_from_qt(p) -> Punkt:
    """``QPointF`` oder ``QPoint`` → ``Punkt``."""
    return Punkt(float(p.x()), float(p.y()))


def point_to_qt(p: Punkt) -> QPointF:
    return QPointF(p.x, p.y)


def size_from_qt(s) -> Groesse:
    """``QSizeF`` oder ``QSize`` → ``Groesse``."""
    return Groesse(float(s.width()), float(s.height()))


def size_to_qt(s: Groesse) -> QSizeF:
    return QSizeF(s.width, s.height)


def rect_from_qt(r) -> Rechteck:
    """``QRectF`` oder ``QRect`` → ``Rechteck``."""
    return Rechteck(float(r.x()), float(r.y()), float(r.width()), float(r.height()))


def rect_to_qt(r: Rechteck) -> QRectF:
    return QRectF(r.x, r.y, r.width, r.height)


def margins_from_qt(m) -> Raender:
    """``QMarginsF`` oder ``QMargins`` → ``Raender``."""
    return Raender(float(m.left()), float(m.top()), float(m.right()), float(m.bottom()))


def margins_to_qt(m: Raender) -> QMarginsF:
    return QMarginsF(m.left, m.top, m.right, m.bottom)
