"""Ein runder Knopf, der unten rechts über dem Blatt schwebt."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.basis.darstellung import eigenschaft

from PySide6.QtCore import QEvent, QObject, QSize
from PySide6.QtWidgets import QToolButton

from vcl.qt.widgets.bausteine.bauteile import symbole


from framework.datentypen.farben import Farbe
from writer.baukasten.basis.mass import GROESSE_SCHWEBKNOPF, ICON_SCHWEBKNOPF, RADIUS_MITTEL
class SchwebKnopf(QToolButton):
    RAND = 16

    def __init__(self, editor, symbol: str, tipp: str, aktion):
        super().__init__(editor)
        self.editor = editor
        symbole.setze(self, symbol, ICON_SCHWEBKNOPF); self.setIconSize(QSize(ICON_SCHWEBKNOPF, ICON_SCHWEBKNOPF)); self.setToolTip(tipp); self.setAccessibleName(tipp)
        self.setFixedSize(*GROESSE_SCHWEBKNOPF)
        self.setCursor(self.cursor())
        eigenschaft(self, rolle="schweb")
        self.clicked.connect(lambda: aktion())
        editor.installEventFilter(self)
        self.platzieren()

    def platzieren(self) -> None:
        r = self.editor.rect()                                   # das Blatt-Fenster (der Reiter des Dokuments), nicht das lange Blatt
        bar = self.editor.verticalScrollBar().width() if self.editor.verticalScrollBar().isVisible() else 0
        unten = self.editor.horizontalScrollBar().height() if self.editor.horizontalScrollBar().isVisible() else 0
        self.move(r.width() - self.width() - self.RAND - bar, r.height() - self.height() - self.RAND - unten)
        self.raise_()

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if e.type() in (QEvent.Resize, QEvent.Show):
            self.platzieren()
        return False
