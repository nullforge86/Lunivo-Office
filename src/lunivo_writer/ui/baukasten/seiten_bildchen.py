"""Kleine Seitenbilder für Galerien (Einfügen ▸ Seitenzahl, Wasserzeichen, Deckblatt). Jede Funktion gibt einen Zeichner
``f(QPainter, QRectF)`` zurück, wie ihn ``RasterAuswahl.kachel`` annimmt. Alles selbst gezeichnet, keine fremden Grafiken.

    seitenzahl_zeichner("fuss", "right")     # Blatt mit Textzeilen, die „1“ unten rechts
    wasserzeichen_zeichner("ENTWURF", -45)   # Blatt mit schräger grauer Schrift
    deckblatt_zeichner("Mit Linie")          # Blatt mit Titelblock
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPen

from lunivo_writer.core.farben import Farbe

Zeichner = Callable[[QPainter, QRectF], None]
_LINIE = QColor("#5c636a")
_RAND = QColor("#495057")


def _blatt(p: QPainter, r: QRectF, verhaeltnis: float = 1.36) -> QRectF:
    """Ein weißes Hochformat-Blatt mittig in ``r``; gibt das Blattrechteck zurück."""
    h = r.height() - 2
    b = min(r.width() - 2, h / verhaeltnis)
    blatt = QRectF(r.center().x() - b / 2, r.top() + 1, b, h)
    p.setPen(QPen(_RAND, 1.2)); p.setBrush(QColor(Farbe.WEISS)); p.drawRect(blatt)
    return blatt


def _zeilen(p: QPainter, r: QRectF, n: int) -> None:
    p.setPen(QPen(_LINIE, 1.3))
    for i in range(n):
        y = r.top() + (i + 0.5) * r.height() / n
        p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))


def seitenzahl_zeichner(ort: str, ausrichtung: str) -> Zeichner:
    """``ort``: "kopf" | "fuss"; ``ausrichtung``: "left" | "center" | "right" | "aussen" | "innen" (zwei Seiten nebeneinander)."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        doppelt = ausrichtung in ("aussen", "innen")
        blaetter = []
        if doppelt:
            halb = QRectF(r.left(), r.top(), r.width() / 2 - 2, r.height())
            blaetter = [(_blatt(p, halb, 2.4), "right" if ausrichtung == "innen" else "left"),
                        (_blatt(p, halb.translated(r.width() / 2 + 2, 0), 2.4), "left" if ausrichtung == "innen" else "right")]
        else:
            blaetter = [(_blatt(p, r), ausrichtung)]
        for b, wo in blaetter:
            rand = b.width() * 0.14
            zahl_h = b.height() * 0.12
            text = QRectF(b.left() + rand, b.top() + rand + (zahl_h if ort == "kopf" else 0), b.width() - 2 * rand,
                          b.height() - 2 * rand - zahl_h)
            _zeilen(p, text, 9)
            feld = QRectF(b.left() + rand * 0.6, b.top() + 2 if ort == "kopf" else b.bottom() - zahl_h - 2, b.width() - rand * 1.2, zahl_h)
            schrift = p.font(); schrift.setPixelSize(max(7, int(zahl_h * 0.9))); p.setFont(schrift)
            p.setPen(QColor(Farbe.ROT))
            p.drawText(feld, {"left": Qt.AlignLeft, "right": Qt.AlignRight}.get(wo, Qt.AlignHCenter) | Qt.AlignVCenter, "1")
        p.restore()
    return f


def wasserzeichen_zeichner(text: str, winkel: float = -45, farbe: str = "#b4b9be") -> Zeichner:
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        b = _blatt(p, r)
        schrift = QFont(p.font()); schrift.setPixelSize(40)
        breite = QFontMetricsF(schrift).horizontalAdvance(text) or 1
        laenge = (b.width() ** 2 + b.height() ** 2) ** 0.5 * 0.78 if winkel else b.width() * 0.86
        schrift.setPixelSize(max(6, int(40 * laenge / breite)))
        if len(text) <= 4 and not winkel:
            schrift.setPixelSize(min(schrift.pixelSize(), int(b.height() * 0.3)))
        p.setFont(schrift); p.setPen(QColor(farbe))
        p.translate(b.center()); p.rotate(winkel)
        p.drawText(QRectF(-laenge, -b.height() / 2, 2 * laenge, b.height()), Qt.AlignCenter, text)
        p.restore()
    return f


def plus_zeichner(beschriftung: str = "") -> Zeichner:
    """Kachel „Hinzufügen“: großes graues Plus auf hellem Feld."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        q = QRectF(r.center().x() - r.height() * 0.35, r.top() + r.height() * 0.08, r.height() * 0.7, r.height() * 0.6)
        p.setPen(QPen(QColor("#ced4da"), 1, Qt.DashLine)); p.setBrush(QColor("#f1f3f5")); p.drawRoundedRect(q, 4, 4)
        p.setPen(QPen(QColor("#adb5bd"), q.width() * 0.16, Qt.SolidLine, Qt.FlatCap))
        m = q.center(); a = q.width() * 0.3
        p.drawLine(QPointF(m.x() - a, m.y()), QPointF(m.x() + a, m.y())); p.drawLine(QPointF(m.x(), m.y() - a), QPointF(m.x(), m.y() + a))
        if beschriftung:
            schrift = p.font(); schrift.setPixelSize(max(8, int(r.height() * 0.13))); p.setFont(schrift)
            p.setPen(QColor(Farbe.GRAU)); p.drawText(QRectF(r.left(), q.bottom() + 2, r.width(), r.bottom() - q.bottom() - 2), Qt.AlignCenter, beschriftung)
        p.restore()
    return f


def deckblatt_zeichner(vorlage: str) -> Zeichner:
    """Die Deckblätter aus ``editor.einfuegen.DECKBLATT_VORLAGEN`` im Kleinen: Titel als dicker Balken, Angaben als dünne Zeilen."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        b = _blatt(p, r)
        mitte = vorlage != "Schlicht"
        w = b.width()

        def balken(y: float, breite: float, dicke: float, farbe: str) -> None:
            x = b.center().x() - breite / 2 if mitte else b.left() + w * 0.12
            p.setPen(Qt.NoPen); p.setBrush(QColor(farbe)); p.drawRect(QRectF(x, b.top() + y * b.height(), breite, dicke))
        if vorlage == "Farbband":
            p.setPen(Qt.NoPen); p.setBrush(QColor(Farbe.AKZENT)); p.drawRect(QRectF(b.left(), b.top() + b.height() * 0.28, w, b.height() * 0.16))
            balken(0.33, w * 0.62, b.height() * 0.05, Farbe.WEISS)
        else:
            balken(0.32, w * 0.62, b.height() * 0.05, Farbe.AKZENT if vorlage != "Schlicht" else Farbe.TINTE_DUNKEL)
        balken(0.40, w * 0.44, b.height() * 0.02, Farbe.GRAU)
        if vorlage == "Mit Linie":
            balken(0.45, w * 0.7, 1.2, Farbe.AKZENT)
        for i in range(3):
            balken(0.74 + i * 0.05, w * (0.34 - i * 0.04), b.height() * 0.018, Farbe.GRAU_HELL)
        p.restore()
    return f


def raender_zeichner(oben: float, unten: float, links: float, rechts: float) -> Zeichner:
    """Blatt mit dem Satzspiegel als Rahmen (Seitenlayout ▸ Ränder); die Maße in mm, Blatt A4."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        b = _blatt(p, r)
        sx, sy = b.width() / 210, b.height() / 297
        innen = QRectF(b.left() + links * sx, b.top() + oben * sy, b.width() - (links + rechts) * sx, b.height() - (oben + unten) * sy)
        p.setPen(QPen(_LINIE, 1)); p.setBrush(Qt.NoBrush); p.drawRect(innen)
        p.restore()
    return f


def format_zeichner(quer: bool) -> Zeichner:
    """Hoch- oder Querformat: ein Blatt mit gestrichelter Mittellinie."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        h = r.height() - 2
        b = QRectF(0, 0, h * 1.36, h * 0.82) if quer else QRectF(0, 0, h / 1.36, h)
        b.moveCenter(r.center())
        p.setPen(QPen(_RAND, 1.2)); p.setBrush(QColor(Farbe.WEISS)); p.drawRoundedRect(b, 2, 2)
        p.setPen(QPen(_LINIE, 1, Qt.DashLine))
        if quer:
            p.drawLine(QPointF(b.left() + 4, b.center().y()), QPointF(b.right() - 4, b.center().y()))
        else:
            p.drawLine(QPointF(b.center().x(), b.top() + 4), QPointF(b.center().x(), b.bottom() - 4))
        p.restore()
    return f


def papier_zeichner() -> Zeichner:
    """Blatt mit Eselsohr (Seitenlayout ▸ Größe)."""
    def f(p: QPainter, r: QRectF) -> None:
        from PySide6.QtGui import QPolygonF
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        h = r.height() - 4; w = h / 1.36
        x, y = r.center().x() - w / 2, r.top() + 2
        e = w * 0.3
        p.setPen(QPen(_RAND, 1.2)); p.setBrush(QColor(Farbe.WEISS))
        p.drawPolygon(QPolygonF([QPointF(x, y), QPointF(x + w - e, y), QPointF(x + w, y + e), QPointF(x + w, y + h), QPointF(x, y + h)]))
        p.drawPolyline(QPolygonF([QPointF(x + w - e, y), QPointF(x + w - e, y + e), QPointF(x + w, y + e)]))
        p.restore()
    return f


def textrichtung_zeichner(art: str) -> Zeichner:
    """Kästchen mit „ABC“ in der jeweiligen Richtung: "waagerecht", "senkrecht_rl", "senkrecht_lr", "dreh90", "dreh270", "asiatisch270"."""
    def f(p: QPainter, r: QRectF) -> None:
        p.save(); p.setRenderHint(QPainter.Antialiasing)
        k = QRectF(0, 0, r.height() - 2, r.height() - 2); k.moveCenter(r.center())
        p.setPen(QPen(_RAND, 1.2)); p.setBrush(QColor(Farbe.WEISS)); p.drawRect(k)
        schrift = p.font(); schrift.setPixelSize(max(7, int(k.height() * 0.3))); p.setFont(schrift)
        p.setPen(QColor(Farbe.TINTE_DUNKEL))
        if art == "waagerecht":
            p.drawText(k, Qt.AlignCenter, "ABC")
        elif art in ("senkrecht_rl", "senkrecht_lr"):
            spalten = ("AB", "CD") if art == "senkrecht_lr" else ("CD", "AB")
            for i, s in enumerate(spalten):
                sp = QRectF(k.left() + k.width() * (0.18 + i * 0.36), k.top() + 2, k.width() * 0.3, k.height() - 4)
                p.drawText(sp, Qt.AlignCenter, "\n".join(s))
        else:
            p.translate(k.center()); p.rotate(90 if art == "dreh90" else -90)
            p.drawText(QRectF(-k.width() / 2, -k.height() / 2, k.width(), k.height()), Qt.AlignCenter, "ABC" if art != "asiatisch270" else "A文")
        p.restore()
    return f
