"""Dialog „Wörter zählen“: die Statistiken untereinander, Werte rechtsbündig; der Haken nimmt Fuß- und Endnoten dazu.

    d = WoerterDialog(parent, ohne, mit)        # Statistiken; ohne/mit: Werte der Zählung, mit = samt Noten

Das Fenster ändert das Dokument nicht."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel

from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig

ZEILEN = (("seiten", "Seiten"), ("woerter", "Wörter"), ("zeichen_ohne", "Zeichen (keine Leerzeichen)"),
          ("zeichen_mit", "Zeichen (mit Leerzeichen)"), ("absaetze", "Absätze"), ("nicht_asiatisch", "Nicht-asiatische Wörter"),
          ("asiatisch", "Asiatische Zeichen"))


class WoerterDialog(PanelFaehig, QDialog):
    """„Wörter zählen“: die Statistiken untereinander, Werte rechtsbündig; der Haken nimmt Fuß- und Endnoten dazu."""

    def __init__(self, parent=None, ohne: dict | None = None, mit: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Wörter zählen")
        self.ohne, self.mit = dict(ohne or {}), dict(mit or ohne or {})
        v = _spalte("panel", self)
        v.addWidget(QLabel("Statistiken:"))
        g = FormularGitter()                                                   # eng: Wert unter der Beschriftung
        self.werte: dict[str, QLabel] = {}
        for i, (key, text) in enumerate(ZEILEN):
            wert = QLabel(); wert.setAlignment(Qt.AlignRight | Qt.AlignVCenter); wert.setAccessibleName(text)
            g.zeile(text, wert)
            self.werte[key] = wert
        v.addLayout(g)
        self.noten = UmbruchSchalter("Textfelder, Fußnoten und Endnoten einbeziehen(&F)")
        self.noten.setToolTip("Textfelder stehen in Lunivo im Text und zählen immer; der Haken nimmt Fuß- und Endnoten dazu.")
        self.noten.toggled.connect(self._zeigen)
        v.addWidget(self.noten)
        fussleiste(self, v, ok_text="Schließen", nur_ok=True)
        self._zeigen()

    def _zeigen(self, *_):
        quelle = self.mit if self.noten.isChecked() else self.ohne
        for key, lab in self.werte.items():
            lab.setText(f"{quelle.get(key, 0):n}")
