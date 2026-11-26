"""Leerzustand der Schreibhilfe: ein dezentes Symbol, die Meldung („Noch nicht geprüft.“) und ein kurzer Hinweis – mittig im Ergebnisbereich statt
einer großen leeren Fläche. Nur Darstellung; die Texte gibt die Seitenleiste vor."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QSize, Qt
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QLabel, QSizePolicy, QWidget

from vcl.qt.widgets.bausteine.abstaende import LEERZUSTAND_ICON
from vcl.qt.widgets.bausteine.schrift import hinweis_label
from vcl.qt.widgets.bausteine.symbole.bauteile import symbolbild
from vcl.qt.widgets.bausteine.zustaende.geruest import spalte


class SchreibLeerzustand(QWidget):
    """``titel`` ist die Meldung, ``hinweis`` der Satz darunter (darf leer sein). Das Feld ``titel`` trägt die Meldung als Beschriftung."""

    def __init__(self, titel: str, hinweis: str = "", symbol: str = "haken"):
        super().__init__()
        self._symbol = symbol
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        v = spalte("inhalt", self)
        v.addStretch(1)
        self.bild = QLabel(); self.bild.setAlignment(Qt.AlignCenter)
        v.addWidget(self.bild)
        self.titel = hinweis_label(titel); self.titel.setAlignment(Qt.AlignCenter)
        v.addWidget(self.titel)
        self.hinweis = hinweis_label(hinweis, klein=True); self.hinweis.setAlignment(Qt.AlignCenter)
        self.hinweis.setVisible(bool(hinweis))
        v.addWidget(self.hinweis)
        v.addStretch(1)
        self._bild_setzen()

    def _bild_setzen(self) -> None:
        groesse = QSize(LEERZUSTAND_ICON, LEERZUSTAND_ICON)
        grau = self.palette().color(QPalette.Mid).name()                                            # einfarbig in der Hinweisfarbe: das Symbol tritt zurück
        self.bild.setPixmap(symbolbild(self._symbol, LEERZUSTAND_ICON, grau).pixmap(groesse))

    def changeEvent(self, e) -> None:
        if e.type() in (QEvent.PaletteChange, QEvent.StyleChange) and hasattr(self, "bild"):
            self._bild_setzen()                                    # Themenwechsel: das Symbol in den neuen Farben
        super().changeEvent(e)
