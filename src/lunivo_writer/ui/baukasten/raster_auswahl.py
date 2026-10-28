"""Kachel-Auswahl: ein Popup mit Bildchen im Raster und einem „Mehr …“-Fuß (Aufzählung, Vorlagen, Ränder, Deckblätter …)."""
from __future__ import annotations

from typing import Callable

from PySide6.QtCore import QRectF, QSize, Qt, Signal
from PySide6.QtGui import QIcon, QPainter, QPixmap
from PySide6.QtWidgets import (
    QApplication, QFrame, QGridLayout, QLabel, QMenu, QPushButton, QScrollArea, QToolButton, QVBoxLayout, QWidget, QWidgetAction,
)


def _symbol(bild, groesse: QSize, blass: bool = False) -> QIcon:
    """Aus QIcon, QPixmap oder einer Zeichenfunktion ``f(QPainter, QRectF)`` ein Symbol machen; ``blass``: für Graues (nicht möglich)."""
    if bild is None:
        return QIcon()
    if isinstance(bild, QIcon):
        return bild
    if isinstance(bild, QPixmap):
        return QIcon(bild)
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    if blass:
        p.setOpacity(0.4)
    bild(p, QRectF(0, 0, groesse.width(), groesse.height()))
    p.end()
    return QIcon(pm)


def textkachel(text: str, pixel: int = 17) -> Callable:
    """Zeichenfunktion für eine Kachel, die nur ein Zeichen oder kurzes Wort zeigt (Symbole, Einheiten)."""
    def f(p: QPainter, r: QRectF) -> None:
        schrift = p.font(); schrift.setPixelSize(pixel if len(text) == 1 else max(9, pixel - 5)); p.setFont(schrift)
        p.setPen(QApplication.palette().text().color()); p.drawText(r, Qt.AlignCenter, text)
    return f


def zeilenkachel(bild, titel: str, angaben: list[str] = (), spalten: int = 1, bild_breite: int = 44) -> Callable:
    """Zeichenfunktion für eine Listenzeile: links ein Bildchen (Zeichner), daneben der Titel fett und darunter die Angaben,
    auf Wunsch zweispaltig (Ränder: „Oben: 25 mm   Unten: 25 mm“). Für ``RasterAuswahl`` mit ``spalten=1``."""
    def f(p: QPainter, r: QRectF) -> None:
        if bild is not None:
            bild(p, QRectF(r.left() + 2, r.top() + 4, bild_breite, r.height() - 8))
        x = r.left() + bild_breite + 12
        zeilen = 1 + (len(angaben) + spalten - 1) // spalten
        h = r.height() / zeilen if angaben else r.height()
        schrift = p.font(); schrift.setPixelSize(13); schrift.setBold(True); p.setFont(schrift)
        p.setPen(QApplication.palette().text().color())
        p.drawText(QRectF(x, r.top(), r.right() - x, h), Qt.AlignLeft | Qt.AlignVCenter, titel)
        schrift.setBold(False); p.setFont(schrift)
        breite = (r.right() - x) / spalten
        for i, t in enumerate(angaben):
            z, s = divmod(i, spalten)
            p.drawText(QRectF(x + s * breite, r.top() + (z + 1) * h, breite, h), Qt.AlignLeft | Qt.AlignVCenter, t)
    return f


class RasterAuswahl(QMenu):
    """Meldet den Schlüssel der gewählten Kachel."""

    gewaehlt = Signal(str)

    def __init__(self, parent=None, *, titel: str = "", spalten: int = 4, groesse: QSize = QSize(56, 56), beschriftet: bool = False,
                 hoehe_max: int = 0):
        """``beschriftet``: der Name steht unter dem Bild (Seitenzahl-, Wasserzeichen-, Gleichungsgalerie), sonst nur im Tipp.
        ``hoehe_max``: lange Galerien (Designs, Schriftarten) rollen ab dieser Höhe; der Fuß bleibt darunter stehen."""
        super().__init__(parent)
        self._spalten, self._groesse, self._beschriftet = spalten, groesse, beschriftet
        self._wid = QWidget()
        self._v = QVBoxLayout(self._wid)
        self._v.setContentsMargins(6, 6, 6, 6); self._v.setSpacing(4)
        self._fuss_v, self._rollen, self._hoehe_max = self._v, None, hoehe_max
        if hoehe_max:
            aussen = QWidget(); self._fuss_v = QVBoxLayout(aussen); self._fuss_v.setContentsMargins(0, 0, 0, 4); self._fuss_v.setSpacing(2)
            self._rollen = QScrollArea(); self._rollen.setWidgetResizable(True); self._rollen.setFrameShape(QFrame.NoFrame)
            self._rollen.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff); self._rollen.setWidget(self._wid)
            self._fuss_v.addWidget(self._rollen)
            self.aboutToShow.connect(self._rollen_masse)
        if titel:
            t = QLabel(titel); t.setStyleSheet("color: palette(mid); font-size: 11px;")
            self._v.addWidget(t)
        self._gitter = QGridLayout(); self._gitter.setSpacing(4)
        self._gitter.setColumnStretch(self._spalten, 1)          # Kacheln bleiben links beisammen, auch wenn ein anderer Abschnitt breiter ist
        self._v.addLayout(self._gitter)
        self._n = 0
        self.knoepfe: dict[str, QToolButton] = {}
        a = QWidgetAction(self); a.setDefaultWidget(self._fuss_v.parentWidget() if self._rollen else self._wid); self.addAction(a)

    def _rollen_masse(self) -> None:
        inhalt = self._wid.sizeHint()
        self._rollen.setFixedSize(inhalt.width() + self._rollen.verticalScrollBar().sizeHint().width() + 2, min(inhalt.height(), self._hoehe_max))

    def kachel(self, schluessel: str, beschriftung: str = "", bild=None, *, aktuell: bool = False, aktiv: bool = True) -> QToolButton:
        """``aktiv=False``: die Kachel bleibt sichtbar, aber grau (blass gezeichnet) und nicht wählbar."""
        b = QToolButton()
        b.setIcon(_symbol(bild, self._groesse, blass=not aktiv)); b.setIconSize(self._groesse); b.setEnabled(aktiv)
        b.setToolTip(beschriftung or schluessel); b.setAccessibleName(beschriftung or schluessel); b.setCheckable(True); b.setChecked(aktuell)
        b.setFixedSize(self._groesse + QSize(10, 10))
        if self._beschriftet:
            b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            b.setText(b.fontMetrics().elidedText(beschriftung or schluessel, Qt.ElideRight, self._groesse.width() + 4))
            b.setFixedSize(self._groesse + QSize(10, 10 + b.fontMetrics().height() + 4))
        b.clicked.connect(lambda _c=False, k=schluessel: self._klick(k))
        self._gitter.addWidget(b, self._n // self._spalten, self._n % self._spalten)
        self._n += 1
        self.knoepfe[schluessel] = b
        return b

    def bild_setzen(self, schluessel: str, bild, beschriftung: str = "") -> None:
        """Bild und Tipp einer vorhandenen Kachel wechseln (z. B. „zuletzt verwendet“ vor dem Aufklappen)."""
        b = self.knoepfe[schluessel]
        b.setIcon(_symbol(bild, self._groesse)); b.setToolTip(beschriftung or schluessel); b.setAccessibleName(beschriftung or schluessel)

    def abschnitt(self, titel: str) -> None:
        """Neuer Abschnitt mit eigener Überschrift und eigenem Raster darunter (z. B. „Benutzerdefinierte Symbole:“)."""
        t = QLabel(titel); t.setStyleSheet("color: palette(mid); font-size: 11px;")
        self._v.addWidget(t)
        self._gitter = QGridLayout(); self._gitter.setSpacing(4)
        self._gitter.setColumnStretch(self._spalten, 1)          # Kacheln bleiben links beisammen, auch wenn ein anderer Abschnitt breiter ist
        self._v.addLayout(self._gitter)
        self._n = 0

    def kacheln(self, eintraege, aktuell: str | None = None) -> None:
        """``eintraege``: Liste aus (schluessel, beschriftung, bild)."""
        for schl, text, bild in eintraege:
            self.kachel(schl, text, bild, aktuell=schl == aktuell)

    def fuss(self, text: str, aktion: Callable) -> QPushButton:
        """Zeile unter dem Raster, z. B. „Weitere Aufzählungszeichen …“."""
        b = QPushButton(text); b.setFlat(True); b.setStyleSheet("text-align: left; padding: 6px 8px; border: none;")
        b.clicked.connect(lambda: (self.close(), aktion()))
        self._fuss_v.addWidget(b)
        return b

    def trenner(self) -> None:
        """Dünne Linie im Fuß (vor „Benutzerdefinierte Seitenränder …“ u. ä.)."""
        l = QFrame(); l.setFrameShape(QFrame.HLine); l.setStyleSheet("color: palette(midlight);")
        self._fuss_v.addWidget(l)

    def _klick(self, schluessel: str) -> None:
        self.gewaehlt.emit(schluessel)
        self.close()
