"""Dialog „Querverweis“ wie die Vorlage: Verweistyp, Verweisen auf, „Als Hyperlink einfügen“, „Oben/unten einschließen“, die Liste „Für welche …“;
„Einfügen“ meldet ``einfuegen(ziel, wie, link, oben_unten)`` und lässt das Fenster offen, „Abbrechen“ wird danach zu „Schließen“.

    d = QuerverweisDialog(parent, ziele)        # d.einfuegen(ziel, wie, link, oben_unten)"""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem

from writer.anbindung.verweise_konstanten import verweistypen, verweisen_auf
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_MIN_ZEICHEN, HOEHE_LISTE_ZIEL
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.verweise.dialog_hilfen import titel as _titel


class QuerverweisDialog(PanelFaehig, QDialog):
    einfuegen = Signal(dict, str, bool, bool)

    _FUER = {"Nummeriertes Element": "Für welches nummerierte Element:", "Überschrift": "Für welche Überschrift:",
             "Textmarke": "Für welche Textmarke:", "Fußnote": "Für welche Fußnote:", "Endnote": "Für welche Endnote:"}

    def __init__(self, parent=None, ziele: list[dict] | None = None):
        super().__init__(parent)
        self.ziele = list(ziele or [])
        self.setWindowTitle("Querverweis")
        v = _spalte("standard", self)
        g = FormularGitter()                                                   # breit: nebeneinander wie die Vorlage, Seitenleiste: untereinander
        self.art = Auswahlfeld(); self.art.addItems(list(verweistypen())); self.art.setAccessibleName("Verweistyp")
        self.auf = Auswahlfeld(); self.auf.setAccessibleName("Verweisen auf")
        self.auf.zeichen(DROPDOWN_MIN_ZEICHEN)
        g.reihe((_titel("&Verweistyp:", self.art), self.art), (_titel("Verweisen &auf:", self.auf), self.auf))
        self.link = UmbruchSchalter("Als &Hyperlink einfügen"); self.link.setChecked(True)
        self.oben_unten = UmbruchSchalter("Oben/unten einschließen (&O)")
        g.breit(self.link); g.breit(self.oben_unten)
        v.addLayout(g)
        self.liste = QListWidget(); self.liste.setMinimumHeight(HOEHE_LISTE_ZIEL); self.liste.setAccessibleName("Ziel")
        self.fuer = _titel("", self.liste)
        v.addWidget(self.fuer); v.addWidget(self.liste, 1)
        self.zeile = knopfzeile(self, ok_text="Einfügen", bei_ok=self._melden)
        v.addWidget(self.zeile)
        self.art.currentTextChanged.connect(self._art_gewaehlt)
        self.auf.currentIndexChanged.connect(lambda _i: self._auffrischen())
        self.liste.currentRowChanged.connect(lambda _i: self._auffrischen())
        self.liste.itemDoubleClicked.connect(lambda _it: self._melden())
        self._art_gewaehlt(self.art.currentText())

    def _art_gewaehlt(self, art: str) -> None:
        self.auf.clear()
        for k, t in verweisen_auf(art):
            self.auf.addItem(t, k)
        self.fuer.setText(self._FUER.get(art, f"Für welche Beschriftung „{art}“:"))
        self.liste.clear()
        for z in self.ziele:
            if z["art"] == art:
                it = QListWidgetItem(z["text"][:90]); it.setData(Qt.UserRole, z); self.liste.addItem(it)
        self._auffrischen()

    def _auffrischen(self) -> None:
        self.oben_unten.setEnabled(self.auf.currentData() in ("seite", "nummer"))
        self.zeile.ok.setEnabled(self.liste.currentItem() is not None)

    def ergebnis(self):
        it = self.liste.currentItem()
        return (it.data(Qt.UserRole) if it else None), self.auf.currentData()

    def _melden(self) -> None:
        ziel, wie = self.ergebnis()
        if ziel is None:
            return
        self.einfuegen.emit(ziel, wie, self.link.isChecked(), self.oben_unten.isEnabled() and self.oben_unten.isChecked())
        self.zeile.abbrechen.setText("Schließen")
