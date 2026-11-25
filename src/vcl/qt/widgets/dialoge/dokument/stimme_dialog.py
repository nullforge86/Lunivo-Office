"""Das Fenster „Stimme und Tempo“ als Baustein: Stimme aus einer ``AuswahlListe``, die den freien Platz füllt, Tempo mit Regler.

    d = StimmeDialog(parent, stimmen, kennung, tempo, (tempo_min, tempo_max, schritt))   # ``stimmen``: Liste aus {"kennung", "name"}; den Tempobereich liefert der Aufrufer (``dienste/vorlesen``)
    if d.exec(): d.stimme(), d.tempo()

Das Fenster speichert nichts selbst; der Aufrufer wertet das Ergebnis aus.
"""
from __future__ import annotations

from PySide6.QtWidgets import QDialog

from vcl.qt.widgets.bausteine.interaktion.felder.auswahl_liste import AuswahlListe
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import abschnittstitel
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_NORMAL, PANEL_HOEHE_ABZUG
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.interaktion.felder.schiebe_feld import SchiebeFeld
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_label
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig

PROZENT = " %"
HINWEIS_TEMPO = "Links langsamer, rechts schneller; 0 ist das normale Tempo."


class StimmeDialog(PanelFaehig, QDialog):
    def __init__(self, parent, stimmen: list[dict], kennung: str, tempo: int, bereich: tuple[int, int, int]):
        super().__init__(parent)
        self.setWindowTitle("Stimme und Tempo")
        v = _spalte("panel_inhalt", self)
        v.addWidget(abschnittstitel("Stimme"))
        self.liste = AuswahlListe([(x["kennung"], x["name"]) for x in stimmen], 0)           # füllt den freien Platz der Seitenleiste
        self.liste.setAccessibleName("Stimme")
        self.liste.setCurrentIndex(max(0, self.liste.findData(kennung)))
        self.liste.itemDoubleClicked.connect(lambda _i: self.accept())
        v.addWidget(self.liste, 1)
        v.addWidget(abschnittstitel("Tempo"))
        lo, hi, schritt = bereich
        self.regler = SchiebeFeld(lo, hi, PROZENT, schritt, 0, max(lo, min(hi, int(tempo or 0))))
        self.regler.regler.setAccessibleName("Tempo")
        v.addWidget(self.regler)
        v.addWidget(hinweis_label(HINWEIS_TEMPO, klein=True))
        fussleiste(self, v)

    def passe_an(self, _breite: int, hoehe: int) -> None:
        """Die Seite nimmt die ganze Höhe der Seitenleiste; die Stimmenliste füllt, was Tempo und Hinweis übrig lassen."""
        self.setMinimumHeight(hoehe - PANEL_HOEHE_ABZUG)

    def stimme(self) -> str:
        return self.liste.currentData() or ""

    def tempo(self) -> int:
        return int(round(self.regler.value()))
