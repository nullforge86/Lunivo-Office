"""Dropdown im Kopf eines Abschnitts („FÜLLUNG ▾ [Feld ▾]“, „LINIE ▾ [Strich ▾]“ der Vorlage): ein weißes Feld mit dem aktuellen Ergebnis und kleinem
Pfeil; ein Klick öffnet ein ``VoreinstellungMenue``.

    k = KopfDropdown(lambda parent: fuell_menue(parent, aktuell))      # die Fabrik baut das Popup bei jedem Öffnen neu
    k.gewaehlt.connect(lambda schluessel: …)                            # "" = die Zeile „Keine …“ (siehe ``keine_zeile``)
    k.setSymbol(QIcon(pixmap_der_Größe_KopfDropdown.SYMBOL))            # das aktuelle Ergebnis im Feld; leeres Symbol = leeres weißes Feld
    k.an(abschnitt)                                                     # hängt den Knopf rechts in den Kopf des ``Abschnitt`` (texteffekt_dialog.py)

Das Feld kennt nur Schlüssel und Symbol; was sie bedeuten, weiß der Aufrufer. Abhängigkeit zum ``Abschnitt``: Dessen Kopf ist die erste Zeile seines
Layouts (``layout().itemAt(0).layout()``) — nur ``an`` greift darauf zu.
"""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QPoint, QPointF, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPalette, QPen, QPixmap, QPolygonF
from PySide6.QtWidgets import QMenu, QPushButton, QSizePolicy, QStyle, QStyleOptionButton, QStylePainter, QWidget

from lunivo_writer.ui.baukasten.dropdown.voreinstellung_menue import VoreinstellungMenue
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.mass import BREITE_KOPFDROPDOWN, GROESSE_KOPFDROPDOWN_SYMBOL, GROESSE_KOPFDROPDOWN_WUNSCH, HOEHE_KOPFDROPDOWN


def keine_symbol(groesse: int = 16) -> QIcon:
    """Das Zeichen der Zeile „Keine …“: Quadrat mit rotem Schrägstrich."""
    pm = QPixmap(groesse, groesse); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    r = QRectF(1.5, 1.5, groesse - 3, groesse - 3)
    p.setPen(QPen(QColor(Farbe.GRAU), 1.2)); p.drawRect(r)
    p.setPen(QPen(QColor(Farbe.ROT), 1.4)); p.drawLine(r.bottomLeft(), r.topRight())
    p.end()
    return QIcon(pm)


def keine_zeile(menue: VoreinstellungMenue, text: str) -> None:
    """Die klickbare Zeile „Keine …“ ganz oben im Popup (Zeichen + Text); sie meldet den Schlüssel ``""``."""
    a = QAction(keine_symbol(), text, menue)
    a.triggered.connect(lambda *_: menue.gewaehlt.emit(""))
    menue.insertAction(menue.actions()[0] if menue.actions() else None, a)


class KopfDropdown(QPushButton):
    gewaehlt = Signal(str)
    SYMBOL = QSize(*GROESSE_KOPFDROPDOWN_SYMBOL)                           # so groß sind die Pixmaps, die ``setSymbol`` erwartet

    def __init__(self, fabrik: Callable[[QWidget], QMenu], symbol: QIcon | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self._fabrik = fabrik
        self._symbol = symbol or QIcon()
        self.setFixedHeight(HOEHE_KOPFDROPDOWN); self.setMinimumWidth(BREITE_KOPFDROPDOWN); self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.clicked.connect(self._popup)

    def sizeHint(self) -> QSize:
        return QSize(*GROESSE_KOPFDROPDOWN_WUNSCH)                                        # Symbol + Pfeil; schrumpft bis zum Mindestmaß, wächst nie über den Kopf hinaus

    def setSymbol(self, symbol: QIcon) -> None:
        self._symbol = symbol or QIcon()
        self.update()

    def an(self, abschnitt) -> None:
        """Rechts in den Kopf des ``Abschnitt`` setzen (hinter den Streckungsraum)."""
        abschnitt.kopffeld(self)                                    # rechts im Kopf, so breit wie die Felder darunter

    def _popup(self) -> None:
        m = self._fabrik(self)
        getattr(m, "schluessel_gewaehlt", m.gewaehlt).connect(self.gewaehlt)      # die Farbpalette meldet über ``schluessel_gewaehlt``
        ziel = self.mapToGlobal(QPoint(self.width(), self.height()))
        scr = self.screen().availableGeometry() if self.screen() else None
        x, y = ziel.x() - m.sizeHint().width(), ziel.y()          # rechtsbündig unter dem Feld, nie über den Bildschirmrand
        if scr is not None:
            x = min(max(scr.left(), x), scr.right() - m.sizeHint().width()); y = min(y, max(scr.top(), scr.bottom() - m.sizeHint().height()))
        m.exec(QPoint(max(0, x), y))
        m.deleteLater()

    def paintEvent(self, _e) -> None:
        """Ein Feld wie die übrigen der Seitenleiste (Farbfeld „Automatisch“): Rahmen, Hintergrund und Rundung vom Thema, darin nur das Ergebnis und der Pfeil."""
        sp = QStylePainter(self)
        opt = QStyleOptionButton(); self.initStyleOption(opt); opt.text = ""; opt.icon = QIcon()
        sp.drawControl(QStyle.CE_PushButtonBevel, opt)
        sp.setRenderHint(QPainter.Antialiasing)
        r = QRectF(self.rect()).adjusted(7, 0, -7, 0)
        if not self._symbol.isNull():
            pm = self._symbol.pixmap(self.SYMBOL)                                      # das Ergebnis klein und mit dünnem Rand, wie das Farbfeld im Fenster
            z = QRectF(r.left(), r.center().y() - 7, r.width() - 14, 14)
            sp.drawPixmap(z.toRect(), pm)
            sp.setBrush(Qt.NoBrush); sp.setPen(QPen(self.palette().color(QPalette.Mid), 1)); sp.drawRect(z.adjusted(0.5, 0.5, -0.5, -0.5))
        x, y = r.right() - 3, r.center().y()
        sp.setPen(Qt.NoPen); sp.setBrush(self.palette().color(QPalette.ButtonText if self.isEnabled() else QPalette.Mid))
        sp.drawPolygon(QPolygonF([QPointF(x - 3.5, y - 1.5), QPointF(x + 3.5, y - 1.5), QPointF(x, y + 2.5)]))
