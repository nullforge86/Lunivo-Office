"""Bildchen für die Galerien Designs, Farben, Schriftarten und Effekte (Reiter Seitenlayout). Jede Funktion gibt einen Zeichner
``f(QPainter, QRectF)`` zurück, wie ihn ``RasterAuswahl.kachel`` annimmt. Alles selbst gezeichnet.

    design_zeichner(farben, "Liberation Serif")   # „Aa“ und ein Farbband
    farbreihe_zeichner(farben, "Ostsee")          # acht Farbfelder und der Name daneben
    schriftpaar_zeichner("Klar", kopf, text)      # Kästchen „Aa“, Name, beide Schriften in sich selbst
    effekt_zeichner(fx)                           # Blockpfeil mit Schatten/Leuchten/Spiegelung
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QApplication

Zeichner = Callable[[QPainter, QRectF], None]
_RAND = QColor("#adb5bd")


def _text(p: QPainter, r: QRectF, text: str, familie: str | None, px: int, ausr=Qt.AlignLeft | Qt.AlignVCenter, fett: bool = False,
          farbe: QColor | None = None) -> None:
    f = QFont(p.font())
    if familie:
        f.setFamilies([familie])
    f.setPixelSize(px); f.setBold(fett); p.setFont(f)
    p.setPen(farbe or QApplication.palette().text().color())
    p.drawText(r, ausr, p.fontMetrics().elidedText(text, Qt.ElideRight, int(r.width())))


def design_zeichner(farben: list[str], kopf: str) -> Zeichner:
    """Weiße Karte mit „Aa“ in der Überschriftschrift und den sechs Akzentfarben als Band."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        k = r.adjusted(1, 1, -1, -1)
        p.setPen(QPen(_RAND, 1)); p.setBrush(QColor("#ffffff")); p.drawRect(k)
        _text(p, QRectF(k.left() + 6, k.top() + 3, k.width() - 8, k.height() * 0.55), "Aa", kopf, int(k.height() * 0.32),
              farbe=QColor(farben[0]))
        b = (k.width() - 12) / 6
        for i, c in enumerate(farben[2:8]):
            p.fillRect(QRectF(k.left() + 6 + i * b, k.bottom() - k.height() * 0.24, b - 1, k.height() * 0.12), QColor(c))
        p.restore()
    return f


def farbreihe_zeichner(farben: list[str], name: str) -> Zeichner:
    """Eine Zeile der Liste „Farben“: acht Farbfelder, rechts daneben der Name."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save()
        s = min(r.height() - 4, 18)
        for i, c in enumerate(farben[:8]):
            q = QRectF(r.left() + 4 + i * (s + 6), r.center().y() - s / 2, s, s)
            p.fillRect(q, QColor(c)); p.setPen(QPen(_RAND, 1)); p.drawRect(q)
        x = r.left() + 4 + 8 * (s + 6) + 6
        _text(p, QRectF(x, r.top(), r.right() - x, r.height()), name, None, 13)
        p.restore()
    return f


def schriftpaar_zeichner(name: str, kopf: str, text: str) -> Zeichner:
    """Eine Zeile der Liste „Schriftarten“: Kästchen „Aa“, darüber der Name, dann die Überschrift- und die Textschrift in sich selbst."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        k = QRectF(r.left() + 4, r.top() + 6, r.height() - 12, r.height() - 12)
        p.setPen(QPen(_RAND, 1)); p.setBrush(QColor("#ffffff")); p.drawRect(k)
        _text(p, k.adjusted(5, 0, 0, -4), "Aa", kopf, int(k.height() * 0.3), Qt.AlignLeft | Qt.AlignBottom, farbe=QColor("#212529"))
        x = k.right() + 12; w = r.right() - x
        h = r.height()
        _text(p, QRectF(x, r.top() + 2, w, h * 0.24), name, None, 11)
        _text(p, QRectF(x, r.top() + h * 0.24, w, h * 0.42), kopf, kopf, 19)
        _text(p, QRectF(x, r.top() + h * 0.64, w, h * 0.32), text, text, 14)
        p.restore()
    return f


def effekt_zeichner(fx: dict) -> Zeichner:
    """Blauer Blockpfeil auf hellem Feld, mit dem Effekt gezeichnet (wie er an Formen erscheint)."""
    def f(p: QPainter, r: QRectF) -> None:
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.editor import freie_bilder as FB
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        k = r.adjusted(1, 1, -1, -1)
        p.setPen(QPen(_RAND, 1)); p.setBrush(QColor("#ffffff")); p.drawRect(k)
        z = QRectF(k.left() + k.width() * 0.14, k.top() + k.height() * 0.16, k.width() * 0.66, k.height() * 0.5)
        p.setClipRect(k.adjusted(1, 1, -1, -1))
        FB.bild_zeichnen(p, E.form_bild("Pfeil nach rechts", 240, 160, "#4a8fd8", "#2f6fb5", 3.0), z, fx=fx or None)
        p.restore()
    return f
