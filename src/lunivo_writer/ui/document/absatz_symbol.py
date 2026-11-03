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
from PySide6.QtWidgets import QMenu, QToolButton

from lunivo_writer.ui.document.tabelle_griffe import GRIFF, GRIFF_STIL, dunkel

OPTION = "ui/absatz_symbol"


class AbsatzSymbol(QObject):
    def __init__(self, ed):
        super().__init__(ed)
        self.ed = ed
        self.pausiert = False                 # während eines Tabellen-Ziehvorgangs ruht die Neuberechnung
        vp = ed.viewport()
        self.knopf = b = QToolButton(vp)
        b.setFixedSize(GRIFF, GRIFF); b.setFocusPolicy(Qt.NoFocus); b.setAutoRaise(False)
        b.setIcon(dunkel("pilcrow-left", 14)); b.setStyleSheet(GRIFF_STIL + "QToolButton::menu-indicator { image: none; width: 0px; }")
        b.setToolTip("Absatz-Layout"); b.setPopupMode(QToolButton.InstantPopup)
        self.menue = m = QMenu(b)
        self.a_zuruecksetzen = m.addAction("Absatzformat zurücksetzen", self._zuruecksetzen)
        self.a_ausblenden = m.addAction("Symbol vom Absatz-Layout ausblenden", self._ausblenden)
        b.setMenu(m)
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
