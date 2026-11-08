"""Absatz-Layout-Symbol: ein kleiner Knopf links neben dem Absatz der Schreibmarke (Absatzzeichen mit Pfeil). Sein Menü bietet
„Absatzformat zurücksetzen“ (Befehl ``absatzFormatZuruecksetzen``) und „Symbol vom Absatz-Layout ausblenden“ (Schalter ``ui/absatz_symbol``
in den Optionen ▸ Ansicht, dort auch wieder einzuschalten).

    AbsatzSymbol(editor)       # hängt sich an den Editor wie ``TabellenGriffe``

Der Knopf ist ein Kind des Sichtbereichs. In Tabellen bleibt er weg (dort sitzen die Tabellengriffe), ebenso bei Auswahl über mehrere Absätze,
im Nur-Lesen-Modus und bei ausgeschaltetem Schalter.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QToolButton

from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe

from lunivo_writer.ui.document.tabelle.tabelle_griffe import GRIFF, dunkel
from lunivo_writer.ui.baukasten.dropdown.dropdown_knopf import DropdownKnopf

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
        for sig in (ed.cursorPositionChanged, ed.selectionChanged, ed.document().contentsChanged):
            sig.connect(self._timer.start)

    def sichtbar_soll(self) -> bool:
        ed = self.ed
        c = ed.textCursor()
        if ed.isReadOnly() or not ed.opt(OPTION, True) or c.currentTable() is not None:
            return False
        return not c.hasSelection() or c.block() == ed.document().findBlock(c.anchor())

    def aktualisieren(self) -> None:
        if self.pausiert:
            return
        if not self.sichtbar_soll():
            self.knopf.hide(); return
        c = QTextCursor(self.ed.textCursor())
        c.movePosition(QTextCursor.StartOfBlock)
        r = self.ed.cursorRect(c)
        self.knopf.move(max(1, r.left() - GRIFF - 6), r.top() + max(0, (r.height() - GRIFF) // 2))
        self.knopf.show(); self.knopf.raise_()

    def _zuruecksetzen(self) -> None:
        self.ed.window().befehle.absatzFormatZuruecksetzen()
        self.ed.setFocus()

    def _ausblenden(self) -> None:
        self.ed.window().settings.set(OPTION, False)
        self.knopf.hide()
        self.ed.setFocus()
