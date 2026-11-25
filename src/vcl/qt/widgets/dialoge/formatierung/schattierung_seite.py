"""Schattierung seite: aus ``vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QWidget
from vcl.qt.rendering import formen as M
from writer.funktionen.objekte import muster as MW
from vcl.qt.widgets.menues.dropdown.auswahl.farb_feld import FarbFeld
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_RAHMENVORSCHAU, ICON_NORMAL, RAND_SCHATTIERUNG_SEITE
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel, mittig
from vcl.qt.widgets.dialoge.formatierung.rahmen_schattierung_hilfen import _Vorschau


def _muster_symbol(schluessel: str, px: int = 16) -> QIcon:
    pm = QPixmap(px, px); pm.fill(QColor(Farbe.WEISS))
    p = QPainter(pm)
    if schluessel != "loeschen":
        p.drawTiledPixmap(0, 0, px, px, M.kachel(schluessel, Farbe.SCHWARZ, None))
    p.setPen(QColor(Farbe.GRAU)); p.setBrush(Qt.NoBrush); p.drawRect(0, 0, px - 1, px - 1)
    p.end()
    return QIcon(pm)


class _SchattierungSeite(QWidget):
    """Ausfüllen (Farbe) · Muster (Art, Farbe) · Vorschau · Übernehmen für."""
    geaendert = Signal()

    def __init__(self, fuell: str | None, muster: tuple[str, str] | None, fuer: list[str] | None):
        super().__init__()
        g = FormularGitter(self); g.setContentsMargins(*RAND_SCHATTIERUNG_SEITE)
        self.fuell = FarbFeld(fuell or "", "Füllfarbe", keine_text="Keine Farbe")
        self.art = Auswahlfeld(); self.art.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL))
        for k, name, _o in MW.muster_vorlagen():
            self.art.addItem(_muster_symbol(k), name, k)
        self.farbe = FarbFeld("" if not muster or muster[1] in ("", Farbe.SCHWARZ) else muster[1], "Musterfarbe", keine_text="Automatisch")
        self.vorschau = _Vorschau(kanten_klick=False); self.vorschau.setFixedSize(*GROESSE_RAHMENVORSCHAU)         # klein, in der Mitte
        self.fuer = Auswahlfeld(); self.fuer.addItems(fuer or ["Absatz"])
        g.breit(abschnittstitel("Ausfüllen")); g.breit(self.fuell)
        g.breit(abschnittstitel("Muster")); g.reihe(("Formatvorlage:", self.art)); g.reihe(("Farbe:", self.farbe))
        g.breit(abschnittstitel("Vorschau")); g.breit(mittig(self.vorschau))
        g.reihe(("Übernehmen für:", self.fuer))
        self.art.setCurrentIndex(max(0, self.art.findData(muster[0] if muster else "loeschen")))
        self.art.currentIndexChanged.connect(lambda _i: self._neu())
        self.fuell.farbeGeaendert.connect(lambda _f: self._neu())
        self.farbe.farbeGeaendert.connect(lambda _f: self._neu())
        self._neu()

    def werte(self) -> tuple[str | None, tuple[str, str] | None]:
        k = self.art.currentData()
        muster = None if k == "loeschen" else (k, self.farbe.farbe or Farbe.SCHWARZ)
        return (self.fuell.farbe or None), muster

    def _neu(self) -> None:
        fuell, muster = self.werte()
        self.farbe.setEnabled(muster is not None)
        self.vorschau.pinsel = M.pinsel(muster[0], muster[1], fuell) if muster else (M.pinsel("", Farbe.SCHWARZ, fuell) if fuell else None)
        self.vorschau.update()
        self.geaendert.emit()
