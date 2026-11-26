"""Dialog „Indexeintrag festlegen“: Haupt- und Untereintrag mit Sortierung, Optionen (Querverweis „Siehe“, aktuelle Seite, Seitenbereich über eine
Textmarke), Seitenzahlenformat fett/kursiv; „Markieren“, „Alles markieren“, „Schließen“. Meldet jeden Klick mit ``markieren``.

    d = IndexeintragDialog(parent, "Apfel", ["Marke1"], auswahl=True)          # d.markieren(IndexEintrag, alle) bei jedem Klick"""
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QDialog

from writer.hauptfenster import index_eintrag
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.verweise.dialog_hilfen import titel as _titel


class IndexeintragDialog(PanelFaehig, QDialog):
    """Haupt- und Untereintrag mit Sortierung, Optionen (Querverweis „Siehe“, aktuelle Seite, Seitenbereich über eine Textmarke),
    Seitenzahlenformat fett/kursiv; „Markieren“, „Alles markieren“, „Schließen“. Meldet jeden Klick mit ``markieren``."""

    markieren = Signal(object, bool)

    def __init__(self, parent=None, vorschlag: str = "", marken: list[str] | None = None, auswahl: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Indexeintrag festlegen")
        v = _spalte("standard", self)

        def feld(name, text=""):
            return zeilenfeld("standard", text, name=name)
        g = FormularGitter()                                                   # breit: zwei Paare nebeneinander wie die Vorlage; schmal: untereinander
        g.breit(abschnittstitel("Index"))
        self.haupt, self.lesung = feld("Haupteintrag", vorschlag), feld("Sortieren als (Haupteintrag)")
        self.unter, self.lesung_unter = feld("Untereintrag"), feld("Sortieren als (Untereintrag)")
        for f in (self.haupt, self.lesung, self.unter, self.lesung_unter):
            f.setMinimumWidth(0)
        g.reihe((_titel("Haupteintrag (&e):", self.haupt), self.haupt), (_titel("Sortieren als (&H):", self.lesung), self.lesung))
        g.reihe((_titel("Untereintrag (&S):", self.unter), self.unter), (_titel("Sortieren als (&g):", self.lesung_unter), self.lesung_unter))
        g.breit(abschnittstitel("Optionen"))
        self.art = QButtonGroup(self)
        self.r_siehe = option("standard", "Querverweis (&r):", gruppe=self.art, nummer=0)
        self.r_seite = option("standard", "Aktuelle Seite (&p)", an=True, gruppe=self.art, nummer=1)
        self.r_bereich = option("standard", "Seitenbereich (&n)", gruppe=self.art, nummer=2)
        self.siehe = feld("Querverweis"); self.siehe.setPlaceholderText("Siehe"); self.siehe.setMinimumWidth(0)
        self.marke = Auswahlfeld(); self.marke.addItems(marken or []); self.marke.setAccessibleName("Textmarke")
        self.marke_titel = _titel("Textmarke:", self.marke)
        g.zeile(self.r_siehe, self.siehe); g.breit(self.r_seite); g.breit(self.r_bereich); g.zeile(self.marke_titel, self.marke)
        g.breit(abschnittstitel("Seitenzahlenformat"))
        self.fett, self.kursiv = UmbruchSchalter("&Fett"), UmbruchSchalter("&Kursiv")
        g.breit(self.fett); g.breit(self.kursiv)
        v.addLayout(g); v.addStretch(1)

        self.knopf_markieren = knopf("standard", "Markieren (&M)", aktion=lambda: self._melden(False))
        self.knopf_alle = knopf("standard", "Alles markieren (&a)", aktion=lambda: self._melden(True),
                                aktiv=auswahl and bool(vorschlag))       # nur mit markiertem Text: jede Stelle mit demselben Text
        zeile = knopfzeile(self, self.knopf_markieren, self.knopf_alle, schliessen=True)
        v.addWidget(zeile)
        self.knopf_markieren.setDefault(True); zeile.ok.setDefault(False)
        self.art.idToggled.connect(lambda _i, _an: self._auffrischen())
        self.haupt.textChanged.connect(lambda _t: self._auffrischen())
        self._auffrischen()

    def eintrag(self):
        return index_eintrag(self.haupt.text().strip(), self.unter.text().strip(), self.lesung.text().strip(), self.lesung_unter.text().strip(),
                            siehe=self.siehe.text().strip() if self.r_siehe.isChecked() else "",
                            marke=self.marke.currentText() if self.r_bereich.isChecked() else "",
                            fett=self.fett.isChecked(), kursiv=self.kursiv.isChecked())

    def _melden(self, alle: bool) -> None:
        self.markieren.emit(self.eintrag(), alle)

    def _auffrischen(self) -> None:
        self.siehe.setEnabled(self.r_siehe.isChecked())
        bereich = self.r_bereich.isChecked() and self.marke.count() > 0
        self.marke.setEnabled(bereich); self.marke_titel.setEnabled(bereich)
        self.r_bereich.setEnabled(self.marke.count() > 0)
        self.knopf_markieren.setEnabled(bool(self.haupt.text().strip()))
