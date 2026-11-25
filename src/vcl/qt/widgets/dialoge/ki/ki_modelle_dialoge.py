from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog
from vcl.qt.widgets.bausteine.schrift.beschriftung import text_label
from writer.funktionen import ki as KD
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.dialoge.ki.modell_liste import ModellListe
from vcl.qt.widgets.dialoge.ki.modell_zuweisung import ModellZuweisung


class ModellListeDialog(QDialog):
    """„Liste der KI-Modelle“ als eigenes Fenster (Optionen)."""

    def __init__(self, fenster, konfig):
        super().__init__(fenster)
        self.setWindowTitle("Liste der KI-Modelle")
        v = _spalte("standard", self)
        v.addWidget(text_label("Liste der KI-Modelle", fett=True, pt=13, umbruch=False))
        self.liste_widget = ModellListe(fenster, konfig)
        self._fuellen = self.liste_widget._fuellen
        v.addWidget(self.liste_widget, 1)
        v.addWidget(knopfzeile(self, nur_ok=True))


class KIKonfigurationDialog(QDialog):
    """Die Modellzuweisung als eigenes Fenster (nur noch für Altaufrufe; im Alltag öffnet „KI-Einstellungen“)."""

    def __init__(self, fenster):
        super().__init__(fenster)
        self.setWindowTitle("KI-Konfiguration")
        v = _spalte("standard", self)
        v.addWidget(text_label("KI-Konfiguration", fett=True, pt=13, umbruch=False))
        self.zuweisung = ModellZuweisung(fenster)
        self.felder = self.zuweisung.felder
        v.addWidget(self.zuweisung)
        v.addWidget(knopfzeile(self, bei_ok=self._ok))

    def _ok(self) -> None:
        self.zuweisung.uebernehmen()
        self.accept()
