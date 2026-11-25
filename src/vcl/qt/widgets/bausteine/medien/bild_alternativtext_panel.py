"""Seitenleiste „Alternativtext“ für ein Bild: Beschreibung und „Als dekorativ markieren“ (der Abschnitt ``AlternativtextAbschnitt``).

``geaendert({"alt": str, "dekor": bool})`` bei jeder Änderung; ``setze(werte)`` mit denselben Schlüsseln füllt das Panel ohne Meldung."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from writer.baukasten.basis.mass import ABSTAND_SPALTE, RAND_FORMATSEITE
from vcl.qt.widgets.bausteine.medien.alternativtext_abschnitt import AlternativtextAbschnitt


class BildAlternativtextPanel(QWidget):
    geaendert = Signal(dict)

    def __init__(self, parent=None, werte: dict | None = None):
        super().__init__(parent)
        v = _spalte("abschnitt", self)
        self.abschnitt = AlternativtextAbschnitt(mit_titel=False, mit_dekorativ=True)
        self.abschnitt.geaendert.connect(lambda _t, b: self._melde())
        self.abschnitt.dekorativ_geaendert.connect(lambda _an: self._melde())
        v.addWidget(self.abschnitt); v.addStretch(1)
        self.setze(werte or {})

    def werte(self) -> dict:
        return {"alt": self.abschnitt.text_feld.toPlainText(), "dekor": self.abschnitt.dekorativ.isChecked()}

    def _melde(self) -> None:
        self.geaendert.emit(self.werte())

    def setze(self, werte: dict) -> None:
        self.abschnitt.setze_dekorativ(bool(werte.get("dekor")))
        self.abschnitt.setze("", str(werte.get("alt") or ""))
