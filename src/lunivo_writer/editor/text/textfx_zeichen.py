"""Was Lunivo am Text selbst zeichnet, das Qt nicht kann und das nicht zu den Effekten von ``textfx`` gehört: Unterstreichungsarten,
doppelt Durchgestrichenes, Betonungszeichen, umschlossene Zeichen, Ruby (Leittext)


``textfx`` führt die Namen von hier wieder auf (Aufrufer bleiben bei ``textfx.<Name>``); dieses Modul wird nur über ``textfx`` geladen.
"""
from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFontMetricsF, QPainter, QPainterPath, QPen, QPolygonF

from lunivo_writer.kern.farben import Farbe
from lunivo_writer.editor.text import zeichenzusatz
from lunivo_writer.editor.text.textfx import PX, aus_text, fx_zeichnen


def _woerter(text: str) -> list[tuple[int, int]]:
    """Die Wörter eines Textes als (Anfang, Ende); Leerzeichen bleiben frei („Nur Wörter“)."""
    aus, start = [], None
    for i, ch in enumerate(text + " "):
        if ch.isspace():
            if start is not None:
                aus.append((start, i)); start = None
        elif start is None:
            start = i
    return aus


# Strichmuster der selbst gezeichneten Unterstreichungen (in Linienbreiten) und ob sie dick, doppelt oder wellig sind
_UNTER_MUSTER = {"einfach": ([], 1, False), "gepunktet": ([1.0, 1.0], 1, False), "gestrichelt": ([3.0, 2.0], 1, False),
                 "strichpunkt": ([4.0, 2.0, 1.0, 2.0], 1, False), "strichpunktpunkt": ([4.0, 2.0, 1.0, 2.0, 1.0, 2.0], 1, False),
                 "wellig": ([], 1, True), "woerter": ([], 1, False), "doppelt": ([], 1, False), "dick": ([], 2, False), "dick_gepunktet": ([1.0, 1.0], 2, False),
                 "dick_gestrichelt": ([3.0, 2.0], 2, False), "lang": ([7.0, 3.0], 1, False), "dick_lang": ([7.0, 3.0], 2, False),
                 "dick_strichpunkt": ([4.0, 2.0, 1.0, 2.0], 2, False), "dick_strichpunktpunkt": ([4.0, 2.0, 1.0, 2.0, 1.0, 2.0], 2, False),
                 "dick_wellig": ([], 2, True), "doppelwellig": ([], 1, True)}


def _unterstrich(p: QPainter, strecken: list[tuple[float, float]], art: str, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Unterstreichungen, die Qt nicht kennt: doppelt, dick, lang gestrichelt, Wellen in zwei Stärken, nur Wörter."""
    muster, dicke, wellig = _UNTER_MUSTER.get(art, ([], 1, False))
    w = max(1.0, groesse * 0.05) * dicke
    y = grundlinie + max(1.5, groesse * 0.12)
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    pen = QPen(farbe, w); pen.setCapStyle(Qt.FlatCap)
    if muster:
        pen.setDashPattern(muster)
    p.setPen(pen)
    for x0, x1 in strecken:
        if x1 <= x0:
            continue
        zeilen = (y, y + w * 2.2) if art == "doppelt" else (y,)
        for yy in zeilen:
            if wellig:
                pf = QPainterPath(); pf.moveTo(x0, yy)
                x, rich = x0, 1
                schritt = max(2.0, groesse * 0.12)
                while x < x1:
                    pf.quadTo(x + schritt / 2, yy + rich * schritt * 0.5, min(x + schritt, x1), yy); x += schritt; rich = -rich
                p.drawPath(pf)
                if art == "doppelwellig":
                    p.translate(0, w * 2.6); p.drawPath(pf); p.translate(0, -w * 2.6)
            else:
                p.drawLine(QPointF(x0, yy), QPointF(x1, yy))
    p.restore()


def unter_zeichnen(p: QPainter, x0: float, y: float, x1: float, art: str, farbe, groesse: float = 11.0) -> None:
    """Eine Unterstreichungsart als Linie von ``x0`` bis ``x1`` in Höhe ``y`` (für Auswahllisten wie das Menü am Knopf „Unterstrichen“)."""
    _unterstrich(p, [(x0, x1)], art, y - max(1.5, groesse * 0.12), groesse, QColor(farbe))


def unter_symbol(art: str, groesse=(70, 16), farbe: str = "#e6e9ec"):
    """Bildchen einer Unterstreichungsart für Auswahllisten (dieselbe Zeichnung wie im Text)."""
    from PySide6.QtGui import QIcon, QPixmap
    pm = QPixmap(*groesse); pm.fill(Qt.transparent)
    p = QPainter(pm)
    if art:
        _unterstrich(p, [(3, groesse[0] - 3)], art, groesse[1] * 0.38, 9.0, QColor(farbe))
    p.end()
    return QIcon(pm)


def _doppelt_durch(p: QPainter, rect: QRectF, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Die zweite Durchstreichlinie (die erste zeichnet Qt): zwei Linien in Höhe der Kleinbuchstaben."""
    p.save(); p.setPen(QPen(farbe, max(1.0, groesse * 0.05)))
    for dy in (0.26, 0.38):
        y = grundlinie - groesse * dy
        p.drawLine(QPointF(rect.left(), y), QPointF(rect.right(), y))
    p.restore()


def _betonung(p: QPainter, glyphen: list[tuple[float, float, float]], art: str, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Betonungszeichen: ein Punkt, Kreis oder Komma über (oder ein Punkt unter) jedem Buchstaben."""
    r = max(1.2, groesse * 0.065)
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    for x, oben, unten in glyphen:
        if art == "unten":
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(QPointF(x, max(unten, grundlinie) + r * 2.2), r, r)
            continue
        y = oben - r * 2.2
        if art == "kreis":
            p.setPen(QPen(farbe, max(0.8, r * 0.5))); p.setBrush(Qt.NoBrush); p.drawEllipse(QPointF(x, y), r, r)
        elif art == "komma":
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(QPointF(x, y), r, r)
            p.setPen(QPen(farbe, max(0.8, r * 0.6))); p.drawLine(QPointF(x + r * 0.6, y + r * 0.4), QPointF(x - r * 0.4, y + r * 2.0))
        else:
            p.setPen(Qt.NoPen); p.setBrush(farbe); p.drawEllipse(QPointF(x, y), r, r)
    p.restore()


# ---- im Dokument -----------------------------------------------------------------------------------------------------------
def _umschlossen(p: QPainter, kasten: QRectF, wie: tuple[str, str], farbe: QColor, groesse: float) -> None:
    """Die Form um die Zeichen: „reduzieren“ legt sie eng an, „erweitern“ lässt dem Symbol Raum."""
    form, vorlage = wie
    rand = groesse * (0.08 if vorlage == "reduzieren" else 0.22)
    r = kasten.adjusted(-rand, 0, rand, 0)
    if form in ("kreis", "raute"):
        r = r.adjusted(-groesse * 0.1, 0, groesse * 0.1, 0)
    p.save(); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(farbe, max(0.6, groesse * 0.06))); p.setBrush(Qt.NoBrush)
    if form == "kreis":
        p.drawEllipse(r)
    elif form == "quadrat":
        p.drawRect(r)
    elif form == "dreieck":
        p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.bottom()), QPointF(r.left(), r.bottom())]))
    else:
        p.drawPolygon(QPolygonF([QPointF(r.center().x(), r.top()), QPointF(r.right(), r.center().y()), QPointF(r.center().x(), r.bottom()),
                                 QPointF(r.left(), r.center().y())]))
    p.restore()


def _ruby(p: QPainter, x0: float, x1: float, grundlinie: float, groesse: float, ruby: dict, farbe: QColor) -> None:
    """Der Leittext über dem Basistext, in kleinerer Schrift, nach der gewählten Ausrichtung."""
    f = p.font(); f.setPixelSize(max(4, int(ruby["groesse"] * PX))); p.save(); p.setFont(f); p.setPen(farbe)
    fm = QFontMetricsF(f)
    breite = fm.horizontalAdvance(ruby["ruby"])
    y = grundlinie - groesse * 0.95 - ruby["abstand"] * PX
    if ruby["ausrichtung"] == "links":
        x = x0
    elif ruby["ausrichtung"] == "rechts":
        x = x1 - breite
    else:
        x = (x0 + x1 - breite) / 2
    if ruby["ausrichtung"] == "verteilt" and len(ruby["ruby"]) > 1 and x1 - x0 > breite:
        schritt = (x1 - x0 - breite) / (len(ruby["ruby"]) - 1)
        for i, ch in enumerate(ruby["ruby"]):
            p.drawText(QPointF(x0 + fm.horizontalAdvance(ruby["ruby"][:i]) + schritt * i, y), ch)
    else:
        p.drawText(QPointF(max(x0, x) if breite < x1 - x0 else x, y), ruby["ruby"])
    p.restore()
