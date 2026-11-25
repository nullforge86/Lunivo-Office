"""Form dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QComboBox, QDialog, QDoubleSpinBox, QLineEdit, QSpinBox
from vcl.qt.rendering import formen as E
from vcl.qt.rendering import formen as FE
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import VORGABE_LINIE
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge_hilfen import VorschauMixin, _Farbknopf, _ok


class FormDialog(PanelFaehig, QDialog, VorschauMixin):
    def __init__(self, parent, form: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Form einfügen")
        v = _spalte("standard", self); f = FormularGitter(); v.addLayout(f)
        self.art = Auswahlfeld(); self.art.addItems(E.FORMEN)
        if form:
            self.art.setCurrentText(form)
        self.fuell = _Farbknopf(Farbe.AKZENT_DUNKEL, "Füllfarbe"); self.linie = _Farbknopf(VORGABE_LINIE, "Linienfarbe")
        self.breite = QSpinBox(); self.breite.setRange(20, 1200); self.breite.setValue(240)
        self.hoehe = QSpinBox(); self.hoehe.setRange(10, 1200); self.hoehe.setValue(140)
        self.strich = QDoubleSpinBox(); self.strich.setRange(0.5, 12); self.strich.setValue(2.0)
        self.text = zeilenfeld("frei")
        for lab, w in (("Form", self.art), ("Füllfarbe", self.fuell), ("Linienfarbe", self.linie), ("Breite (px)", self.breite),
                       ("Höhe (px)", self.hoehe), ("Linienstärke", self.strich), ("Text in der Form", self.text)):
            f.zeile(lab, w)
        self._vorschau_bauen(v)
        v.addWidget(_ok(self))
        for w in (self.art, self.breite, self.hoehe, self.strich, self.text):
            (w.currentTextChanged if isinstance(w, QComboBox) else w.textChanged if isinstance(w, QLineEdit) else w.valueChanged).connect(self.aktualisieren)
        self.fuell.clicked.connect(self.aktualisieren); self.linie.clicked.connect(self.aktualisieren)
        self.aktualisieren()

    def bild(self):
        return FE.form_bild(self.art.currentText(), self.breite.value(), self.hoehe.value(), self.fuell.farbe, self.linie.farbe,
                           self.strich.value(), self.text.text())

    def daten(self):
        return {"form": self.art.currentText(), "fuell": self.fuell.farbe, "linie": self.linie.farbe,
                "strich": self.strich.value(), "text": self.text.text()}

    def aktualisieren(self, *_):
        self._zeige(self.bild())


class FormDialog(PanelFaehig, QDialog, VorschauMixin):
    def __init__(self, parent, form: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Form einfügen")
        v = _spalte("standard", self); f = FormularGitter(); v.addLayout(f)
        self.art = Auswahlfeld(); self.art.addItems(E.FORMEN)
        if form:
            self.art.setCurrentText(form)
        self.fuell = _Farbknopf(Farbe.AKZENT_DUNKEL, "Füllfarbe"); self.linie = _Farbknopf(VORGABE_LINIE, "Linienfarbe")
        self.breite = QSpinBox(); self.breite.setRange(20, 1200); self.breite.setValue(240)
        self.hoehe = QSpinBox(); self.hoehe.setRange(10, 1200); self.hoehe.setValue(140)
        self.strich = QDoubleSpinBox(); self.strich.setRange(0.5, 12); self.strich.setValue(2.0)
        self.text = zeilenfeld("frei")
        for lab, w in (("Form", self.art), ("Füllfarbe", self.fuell), ("Linienfarbe", self.linie), ("Breite (px)", self.breite),
                       ("Höhe (px)", self.hoehe), ("Linienstärke", self.strich), ("Text in der Form", self.text)):
            f.zeile(lab, w)
        self._vorschau_bauen(v)
        v.addWidget(_ok(self))
        for w in (self.art, self.breite, self.hoehe, self.strich, self.text):
            (w.currentTextChanged if isinstance(w, QComboBox) else w.textChanged if isinstance(w, QLineEdit) else w.valueChanged).connect(self.aktualisieren)
        self.fuell.clicked.connect(self.aktualisieren); self.linie.clicked.connect(self.aktualisieren)
        self.aktualisieren()

    def bild(self):
        return FE.form_bild(self.art.currentText(), self.breite.value(), self.hoehe.value(), self.fuell.farbe, self.linie.farbe,
                           self.strich.value(), self.text.text())

    def daten(self):
        return {"form": self.art.currentText(), "fuell": self.fuell.farbe, "linie": self.linie.farbe,
                "strich": self.strich.value(), "text": self.text.text()}

    def aktualisieren(self, *_):
        self._zeige(self.bild())
