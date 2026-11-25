"""Absatz-Layout-Symbol: ein kleiner Knopf links neben dem Absatz der Schreibmarke (Absatzzeichen mit Pfeil). Sein Menü bietet
„Absatzformat zurücksetzen“ (Befehl ``absatzFormatZuruecksetzen``) und „Symbol vom Absatz-Layout ausblenden“ (Schalter ``ui/absatz_symbol``
in den Optionen ▸ Ansicht, dort auch wieder einzuschalten).

    AbsatzSymbol(editor)       # hängt sich an den Editor (``KernEditor``)

Der Knopf ist ein Kind des Sichtbereichs. In Tabellen bleibt er weg (dort sitzen die Tabellengriffe), ebenso bei Auswahl über mehrere Absätze,
im Nur-Lesen-Modus und bei ausgeschaltetem Schalter.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QToolButton

from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_GRIFF as GRIFF       # Seitenlänge der Griffe: eine Quelle in mass.py


def dunkel(symbol: str, px: int = 16) -> QIcon:
    """Symbol in dunkler Tinte für die hellen Knöpfe auf dem Papier."""
    return QIcon(symbole._pixmap(symbol, Farbe.TINTE, max(10, px)))
from vcl.qt.widgets.menues.dropdown.dropdown_knopf import DropdownKnopf

OPTION = "ui/absatz_symbol"


class AbsatzSymbol(QObject):
    def __init__(self, ed):
        super().__init__(ed)
        self.ed = ed
        self.pausiert = False                 # während eines Tabellen-Ziehvorgangs ruht die Neuberechnung
        vp = ed.viewport()
        self.knopf = b = DropdownKnopf(vp)
        b.groesse_rolle("griff", "dokument"); b.setFocusPolicy(Qt.NoFocus); b.setAutoRaise(False)
        b.setIcon(dunkel("pilcrow-left", 14)); b.setProperty("papierKnopf", "griff")
        b.setToolTip("Absatz-Layout")
        self.menue = m = MenueListe(b)
        self.a_zuruecksetzen = m.eintrag("Absatzformat zurücksetzen", self._zuruecksetzen)
        self.a_ausblenden = m.eintrag("Symbol vom Absatz-Layout ausblenden", self._ausblenden)
        b.menue_setzen(m, geteilt=False)
        b.hide()
        self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.setInterval(0); self._timer.timeout.connect(self.aktualisieren)
        for sig in (ed.cursorPositionChanged, ed.selectionChanged, ed.document().contentsChanged, ed.zoomChanged):
            sig.connect(self._timer.start)

    def sichtbar_soll(self) -> bool:
        ed = self.ed
        a = ed.sitzung.auswahl
        if ed.isReadOnly() or not ed.opt(OPTION, True) or ed.textCursor().currentTable() is not None:
            return False
        return a.leer or a.anker.absatz_id == a.kopf.absatz_id

    def aktualisieren(self) -> None:
        if self.pausiert:
            return
        if not self.sichtbar_soll():
            self.knopf.hide(); return
        ansicht = self.ed.ansicht
        stelle = ansicht.ergebnis().cursor(self.ed.sitzung.auswahl.kopf.absatz_id, 0)
        if stelle is None:
            self.knopf.hide(); return
        blatt = ansicht.blatt(stelle[0])
        x, y = blatt.left() + stelle[1].x * ansicht.zoom, blatt.top() + stelle[1].y * ansicht.zoom
        hoehe = 16 * ansicht.zoom
        self.knopf.move(int(max(1, x - GRIFF - 6)), int(y + max(0, (hoehe - GRIFF) // 2)))
        self.knopf.show(); self.knopf.raise_()

    def _zuruecksetzen(self) -> None:
        self.ed.fenster.befehle.absatzFormatZuruecksetzen()
        self.ed.setFocus()

    def _ausblenden(self) -> None:
        self.ed.fenster.settings.set(OPTION, False)
        self.knopf.hide()
        self.ed.setFocus()
