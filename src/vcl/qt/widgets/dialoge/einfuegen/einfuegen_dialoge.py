from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QDialog, QLabel
from core.bearbeitung import einfuegen as E
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from framework.schnittstellen.datentypen.farben import Farbe
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge_hilfen import _Vorschau, _ok


_BILDCHEN: dict = {}


class FormelDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Formel")
        v = _spalte("standard", self)
        hilfe = QLabel("Schreibweise: hoch  a^2 oder a^{n+1}  · tief  x_1  · Wurzel  sqrt(x)  · Bruch  frac(a,b)  · Griechisch  \\alpha \\pi \\Sigma  ·  \\infty \\leq \\geq \\neq \\pm \\times")
        hilfe.setWordWrap(True); v.addWidget(hilfe)
        self.eingabe = zeilenfeld("frei", "E = m c^2"); v.addWidget(self.eingabe)
        self.vorschau = _Vorschau()                                            # verkleinert lange Formeln auf die Breite
        v.addWidget(self.vorschau); v.addWidget(_ok(self))
        self.eingabe.textChanged.connect(self._zeige); self._zeige()

    def _zeige(self, *_):
        from PySide6.QtGui import QColor, QPainter, QPixmap
        img = E.formel_bild(self.eingabe.text())
        pm = QPixmap(img.width() + 16, img.height() + 12); pm.fill(QColor(Farbe.PAPIER))
        p = QPainter(pm); p.drawImage(8, 6, img); p.end()
        self.vorschau.setze(pm.toImage())


class DeckblattDialog(PanelFaehig, QDialog):
    def __init__(self, parent, autor: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Deckblatt")
        v = _spalte("standard", self); f = FormularGitter(); v.addLayout(f)
        self.vorlage = Auswahlfeld(); self.vorlage.addItems(E.DECKBLATT_VORLAGEN)
        self.titel = zeilenfeld("frei", "Titel des Dokuments"); self.unter = zeilenfeld("frei"); self.autor = zeilenfeld("frei", autor)
        self.datum = zeilenfeld("frei", E.datum_text("d. MMMM yyyy"))
        for lab, w in (("Vorlage", self.vorlage), ("Titel", self.titel), ("Untertitel", self.unter), ("Autor", self.autor), ("Datum", self.datum)):
            f.zeile(lab + ":", w)
        v.addWidget(_ok(self))


_BILDCHEN: dict = {}


class FormelDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Formel")
        v = _spalte("standard", self)
        hilfe = QLabel("Schreibweise: hoch  a^2 oder a^{n+1}  · tief  x_1  · Wurzel  sqrt(x)  · Bruch  frac(a,b)  · Griechisch  \\alpha \\pi \\Sigma  ·  \\infty \\leq \\geq \\neq \\pm \\times")
        hilfe.setWordWrap(True); v.addWidget(hilfe)
        self.eingabe = zeilenfeld("frei", "E = m c^2"); v.addWidget(self.eingabe)
        self.vorschau = _Vorschau()                                            # verkleinert lange Formeln auf die Breite
        v.addWidget(self.vorschau); v.addWidget(_ok(self))
        self.eingabe.textChanged.connect(self._zeige); self._zeige()

    def _zeige(self, *_):
        from PySide6.QtGui import QColor, QPainter, QPixmap
        img = E.formel_bild(self.eingabe.text())
        pm = QPixmap(img.width() + 16, img.height() + 12); pm.fill(QColor(Farbe.PAPIER))
        p = QPainter(pm); p.drawImage(8, 6, img); p.end()
        self.vorschau.setze(pm.toImage())


class DeckblattDialog(PanelFaehig, QDialog):
    def __init__(self, parent, autor: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Deckblatt")
        v = _spalte("standard", self); f = FormularGitter(); v.addLayout(f)
        self.vorlage = Auswahlfeld(); self.vorlage.addItems(E.DECKBLATT_VORLAGEN)
        self.titel = zeilenfeld("frei", "Titel des Dokuments"); self.unter = zeilenfeld("frei"); self.autor = zeilenfeld("frei", autor)
        self.datum = zeilenfeld("frei", E.datum_text("d. MMMM yyyy"))
        for lab, w in (("Vorlage", self.vorlage), ("Titel", self.titel), ("Untertitel", self.unter), ("Autor", self.autor), ("Datum", self.datum)):
            f.zeile(lab + ":", w)
        v.addWidget(_ok(self))
