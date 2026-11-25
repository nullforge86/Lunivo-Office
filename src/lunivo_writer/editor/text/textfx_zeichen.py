"""Zeichenzusätze am Text: Unterstreichungsarten, doppelt Durchgestrichenes, Betonungszeichen, umschlossene Zeichen, Ruby (Leittext).

Gezeichnet wird vom Qt-freien Kern (``core/rendering/zeichenzusatz.py``); die Funktionen hier nehmen einen ``QPainter`` und legen das vom Kern gerenderte Bild darauf
(Aufrufer bleiben bei ``textfx.<Name>``; dieses Modul wird nur über ``textfx`` geladen)."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter

from lunivo_writer.oberflaeche.zeichnen.anzeige import kern_bild, kern_malen
from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.rendering import zeichenzusatz as Z
from lunivo_writer.core.rendering.zeichenzusatz import UNTER_MUSTER as _UNTER_MUSTER  # noqa: F401  (Strichmuster der Unterstreichungen)
from lunivo_writer.editor.text import zeichenzusatz
from lunivo_writer.editor.text.textfx import PX, aus_text, fx_zeichnen  # noqa: F401


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


def _rgba(farbe) -> tuple:
    c = QColor(farbe)
    return c.red(), c.green(), c.blue(), c.alpha()


def _unterstrich(p: QPainter, strecken: list[tuple[float, float]], art: str, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Unterstreichungen (doppelt, dick, lang gestrichelt, Wellen in zwei Stärken, nur Wörter) vom Kern gezeichnet."""
    if not strecken:
        return
    x0, x1 = min(s[0] for s in strecken), max(s[1] for s in strecken)
    kern_malen(p, QRectF(x0, grundlinie - groesse, x1 - x0, groesse * 2.5), lambda z: Z.unterstrich(z, strecken, art, grundlinie, groesse, _rgba(farbe)), rand=groesse * 0.6 + 4)


def unter_zeichnen(p: QPainter, x0: float, y: float, x1: float, art: str, farbe, groesse: float = 11.0) -> None:
    """Eine Unterstreichungsart als Linie von ``x0`` bis ``x1`` in Höhe ``y`` (für Auswahllisten wie das Menü am Knopf „Unterstrichen“)."""
    _unterstrich(p, [(x0, x1)], art, y - max(1.5, groesse * 0.12), groesse, QColor(farbe))


def unter_symbol(art: str, groesse=(70, 16), farbe: str = "#e6e9ec"):
    """Bildchen einer Unterstreichungsart für Auswahllisten (dieselbe Zeichnung wie im Text)."""
    from PySide6.QtGui import QIcon, QPixmap
    c = _rgba(farbe)
    img = kern_bild(groesse[0], groesse[1], lambda z: Z.unterstrich(z, [(3, groesse[0] - 3)], art, groesse[1] * 0.38, 9.0, c) if art else None)
    return QIcon(QPixmap.fromImage(img))


def _doppelt_durch(p: QPainter, rect: QRectF, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Die zweite Durchstreichlinie (die erste zeichnet der Textsatz): zwei Linien in Höhe der Kleinbuchstaben."""
    kern_malen(p, rect, lambda z: Z.doppelt_durch(z, Rect(rect.left(), rect.top(), rect.width(), rect.height()), grundlinie, groesse, _rgba(farbe)), rand=4.0)


def _betonung(p: QPainter, glyphen: list[tuple[float, float, float]], art: str, grundlinie: float, groesse: float, farbe: QColor) -> None:
    """Betonungszeichen: ein Punkt, Kreis oder Komma über (oder ein Punkt unter) jedem Buchstaben."""
    if not glyphen:
        return
    xs = [g[0] for g in glyphen]
    kern_malen(p, QRectF(min(xs), grundlinie - groesse * 1.4, max(xs) - min(xs), groesse * 2.2), lambda z: Z.betonung(z, glyphen, art, grundlinie, groesse, _rgba(farbe)), rand=groesse)


def _umschlossen(p: QPainter, kasten: QRectF, wie: tuple[str, str], farbe: QColor, groesse: float) -> None:
    """Die Form um die Zeichen: „reduzieren“ legt sie eng an, „erweitern“ lässt dem Symbol Raum."""
    kern_malen(p, kasten, lambda z: Z.umschlossen(z, Rect(kasten.left(), kasten.top(), kasten.width(), kasten.height()), wie, _rgba(farbe), groesse), rand=groesse)


def _ruby(p: QPainter, x0: float, x1: float, grundlinie: float, groesse: float, ruby: dict, farbe: QColor) -> None:
    """Der Leittext über dem Basistext, in kleinerer Schrift, nach der gewählten Ausrichtung."""
    from lunivo_writer.dienste.textsatz import standard_engine
    kern_malen(p, QRectF(x0, grundlinie - groesse * 2, x1 - x0, groesse * 2.2), lambda z: Z.ruby(z, standard_engine(), x0, x1, grundlinie, groesse, ruby, _rgba(farbe)), rand=groesse)
