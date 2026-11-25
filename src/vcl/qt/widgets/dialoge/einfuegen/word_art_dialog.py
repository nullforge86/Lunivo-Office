"""Word art dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QSpinBox
from core.bearbeitung import einfuegen as E
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.schrift.schriftarten import SANS
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge_hilfen import VorschauMixin, _Farbknopf, _ok


class WordArtDialog(PanelFaehig, QDialog, VorschauMixin):
    def __init__(self, parent, text: str = "Ihr Text", stil: str = "Verlauf", farbe: str | None = None, vorlage: int | None = None):
        """``vorlage``: Nummer eines Galerie-Stils (``E.WORDART_VORLAGEN``); ohne sie gelten ``stil`` und ``farbe``."""
        super().__init__(parent)
        farbe = Farbe.AKZENT if farbe is None else farbe
        self.setWindowTitle("WordArt")
        v = _spalte("standard", self); f = FormularGitter(); v.addLayout(f)
        self.text = zeilenfeld("frei", text or "Ihr Text"); self.stil = Auswahlfeld(); self.stil.addItems(E.WORDART_STILE)
        self.stil.setCurrentText(stil)
        self.vorlage = Auswahlfeld(); self.vorlage.addItem("(eigener Stil)")
        self.vorlage.addItems([n for n, *_r in E.WORDART_VORLAGEN])
        self.vorlage.setCurrentIndex(0 if vorlage is None else vorlage + 1)
        self.schrift = zeilenfeld("frei", SANS); self.pt = QSpinBox(); self.pt.setRange(12, 200); self.pt.setValue(48)
        self.farbe = _Farbknopf(farbe)
        for lab, w in (("Text", self.text), ("Formatvorlage", self.vorlage), ("Stil", self.stil), ("Schriftart", self.schrift), ("Größe (pt)", self.pt), ("Farbe", self.farbe)):
            f.zeile(lab, w)
        self._vorschau_bauen(v); v.addWidget(_ok(self))
        self.text.textChanged.connect(self.aktualisieren); self.stil.currentTextChanged.connect(self.aktualisieren)
        self.vorlage.currentIndexChanged.connect(self.aktualisieren)
        self.schrift.textChanged.connect(self.aktualisieren); self.pt.valueChanged.connect(self.aktualisieren)
        self.farbe.clicked.connect(self.aktualisieren)
        self.aktualisieren()

    def vorlage_nr(self) -> int | None:
        i = self.vorlage.currentIndex() - 1
        return i if i >= 0 else None

    def bild(self):
        return E.wordart_bild(self.text.text() or " ", self.stil.currentText(), self.schrift.text() or "Liberation Sans",
                              self.pt.value(), self.farbe.farbe, self.vorlage_nr())

    def aktualisieren(self, *_):
        self._zeige(self.bild())


class WordArtDialog(PanelFaehig, QDialog, VorschauMixin):
    def __init__(self, parent, text: str = "Ihr Text", stil: str = "Verlauf", farbe: str | None = None, vorlage: int | None = None):
        """``vorlage``: Nummer eines Galerie-Stils (``E.WORDART_VORLAGEN``); ohne sie gelten ``stil`` und ``farbe``."""
        super().__init__(parent)
        farbe = Farbe.AKZENT if farbe is None else farbe
        self.setWindowTitle("WordArt")
        v = _spalte("standard", self); f = FormularGitter(); v.addLayout(f)
        self.text = zeilenfeld("frei", text or "Ihr Text"); self.stil = Auswahlfeld(); self.stil.addItems(E.WORDART_STILE)
        self.stil.setCurrentText(stil)
        self.vorlage = Auswahlfeld(); self.vorlage.addItem("(eigener Stil)")
        self.vorlage.addItems([n for n, *_r in E.WORDART_VORLAGEN])
        self.vorlage.setCurrentIndex(0 if vorlage is None else vorlage + 1)
        self.schrift = zeilenfeld("frei", SANS); self.pt = QSpinBox(); self.pt.setRange(12, 200); self.pt.setValue(48)
        self.farbe = _Farbknopf(farbe)
        for lab, w in (("Text", self.text), ("Formatvorlage", self.vorlage), ("Stil", self.stil), ("Schriftart", self.schrift), ("Größe (pt)", self.pt), ("Farbe", self.farbe)):
            f.zeile(lab, w)
        self._vorschau_bauen(v); v.addWidget(_ok(self))
        self.text.textChanged.connect(self.aktualisieren); self.stil.currentTextChanged.connect(self.aktualisieren)
        self.vorlage.currentIndexChanged.connect(self.aktualisieren)
        self.schrift.textChanged.connect(self.aktualisieren); self.pt.valueChanged.connect(self.aktualisieren)
        self.farbe.clicked.connect(self.aktualisieren)
        self.aktualisieren()

    def vorlage_nr(self) -> int | None:
        i = self.vorlage.currentIndex() - 1
        return i if i >= 0 else None

    def bild(self):
        return E.wordart_bild(self.text.text() or " ", self.stil.currentText(), self.schrift.text() or "Liberation Sans",
                              self.pt.value(), self.farbe.farbe, self.vorlage_nr())

    def aktualisieren(self, *_):
        self._zeige(self.bild())
