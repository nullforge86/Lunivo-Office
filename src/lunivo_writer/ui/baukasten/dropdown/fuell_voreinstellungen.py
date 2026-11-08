"""Popup der Füllung im Kopf (Vorlage): „Keine Füllung“, Designfarben (10 × 6), Graduelle Füllung (10), Musterfüllung (5), Strukturfüllung (5).

    m = fuell_menue(parent, aktuell="farbe:#1971c2")      # ``VoreinstellungMenue``; ``gewaehlt(schluessel)``: "" | farbe:#hex | graduell:#hex | muster:key | textur:key
    pm = fuell_bild({"art": "farbe", "farbe": "#1971c2"}, KopfDropdown.SYMBOL)    # das Feld im Kopf; art: None (leer) | keine | farbe | graduell | muster | textur
    graduell_paar("#e03131") -> (dunkel, hell)             # die zwei Farben der graduellen Füllung zu einem Schlüssel

Der Baustein malt und benennt nur; die Füllung setzt der Aufrufer (``kopf_menue_mixin.py``).
"""
from __future__ import annotations

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor import muster as M
from lunivo_writer.ui.baukasten.basis import farben
from lunivo_writer.ui.baukasten.dropdown.kopf_dropdown import keine_symbol
from lunivo_writer.ui.baukasten.dropdown.objekt_menues import TEXTUREN, _textur, graduell_pixmap
from lunivo_writer.ui.baukasten.dropdown.farbpalette import FarbPalette
from lunivo_writer.ui.baukasten.basis.mass import GROESSE_FUELLVORGABE_KACHEL, GROESSE_MUSTER_KACHEL

KACHEL = QSize(*GROESSE_FUELLVORGABE_KACHEL)
MUSTER_AUSWAHL = ("pct5", "pct10", "pct20", "pct30", "pct50")            # von dünn nach dicht
TEXTUR_AUSWAHL = tuple(k for k, _n in TEXTUREN[:5])


def graduell_paar(farbe: str) -> tuple[str, str]:
    """(dunkel, hell) der graduellen Füllung einer Grundfarbe."""
    return QColor(farbe).name(), farben.mische(farbe, Farbe.WEISS, 0.7)


def _feld(farbe: str, groesse: QSize = KACHEL) -> QPixmap:
    pm = QPixmap(groesse); pm.fill(QColor(farbe))
    p = QPainter(pm); p.setPen(QColor(Farbe.VORSCHAU_RAND)); p.drawRect(pm.rect().adjusted(0, 0, -1, -1)); p.end()
    return pm


def _gekachelt(kachel: QPixmap, groesse: QSize) -> QPixmap:
    pm = QPixmap(groesse); pm.fill(QColor(Farbe.PAPIER))
    p = QPainter(pm); p.drawTiledPixmap(pm.rect(), kachel); p.end()
    return pm


def _muster_kachel(key: str, farbe: str | None = None) -> QPixmap:
    return M.kachel(key, Farbe.TINTE if farbe is None else farbe, Farbe.WEISS)


def fuell_bild(spec: dict, groesse: QSize) -> QPixmap:
    """Das Ergebnis der Füllung als Bild der Größe ``groesse`` (leer = durchsichtig)."""
    art = spec.get("art")
    if art == "keine":
        return keine_symbol(groesse.height()).pixmap(groesse.height(), groesse.height())
    pm = QPixmap(groesse); pm.fill(Qt.transparent)
    if art == "farbe":
        pm.fill(QColor(spec.get("farbe") or Farbe.BLAU))
    elif art == "graduell":
        return graduell_pixmap(spec.get("dunkel") or Farbe.BLAU_DUNKEL, spec.get("hell") or Farbe.WEISS, groesse.width(), groesse.height())
    elif art == "muster":
        return _gekachelt(_muster_kachel(spec.get("key") or "pct50", spec.get("farbe") or Farbe.TINTE), groesse)
    elif art == "textur":
        return _gekachelt(_textur(spec.get("key") or "papier", groesse.height()), groesse)
    return pm


class FuellPalette(FarbPalette):
    """Die Farbpalette des Programms als Popup der Füllung im Kopf; meldet den Schlüssel statt einer Farbe."""
    schluessel_gewaehlt = Signal(str)

    def __init__(self, parent=None, aktuell: str = "", **kw):
        super().__init__(parent, **kw)
        self.aktuell = aktuell
        self.gewaehlt.connect(lambda c: self.schluessel_gewaehlt.emit("" if c is None else f"farbe:{c.name()}"))
        self.verlauf_gewaehlt.connect(lambda c: self.schluessel_gewaehlt.emit(f"graduell:{c.name()}"))
        self.reihe_gewaehlt.connect(self.schluessel_gewaehlt)


def fuell_menue(parent: QWidget | None = None, aktuell: str = "") -> FarbPalette:
    namen = dict(TEXTUREN)
    reihen = [("Musterfüllung", [(f"muster:{k}", _gekachelt(_muster_kachel(k), QSize(*GROESSE_MUSTER_KACHEL)), M.name_von(k)) for k in MUSTER_AUSWAHL]),
              ("Strukturfüllung", [(f"textur:{k}", _textur(k, 18), namen[k]) for k in TEXTUR_AUSWAHL])]
    return FuellPalette(parent, aktuell, keine_text="Keine Füllung", verlauf=True, reihen=reihen, titel="Füllung")
