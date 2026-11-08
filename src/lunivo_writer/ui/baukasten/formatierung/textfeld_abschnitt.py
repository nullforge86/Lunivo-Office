"""Abschnitt „AUSRICHTUNG“ der Seite „Textfeld“ (Textoptionen eines Diagrammteils) — nach der Vorlage.

``setze(feld)`` / ``werte()`` im Format von ``diagramm_format.feld_von`` (vertikal, richtung, winkel, raender in pt, anpassen, umbruch, gerade); ``geaendert()``
kommt bei jeder Eingabe. Die Ränder zeigt der Abschnitt in Inch („0,10Inch“, Umrechnung ×72 nur hier). ``freigeben(raender, gerade)`` schaltet die Felder
bedienbar oder grau (Ränder samt „Größe der Form dem Text anpassen“ und „Text in Form umbrechen“ bzw. „Text nicht drehen“).
"""
from __future__ import annotations

from PySide6.QtCore import QLocale, Signal
from PySide6.QtWidgets import QComboBox, QLabel

from lunivo_writer.editor import diagramm_format as F
from lunivo_writer.ui.baukasten.controls.formular_gitter import UmbruchSchalter
from lunivo_writer.ui.baukasten.controls.schiebe_feld import SchrittFeld
from lunivo_writer.ui.baukasten.formatierung.texteffekt_dialog import Abschnitt
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld

RICHTUNGEN = (("waagerecht", "Horizontal"), ("dreh90", "Um 90° drehen"), ("dreh270", "Um 270° drehen"), ("gestapelt", "Gestapelt"))
_PT = 72.0                                                   # Punkt je Inch


def _still(x, wert, setter: str) -> None:
    x.blockSignals(True); getattr(x, setter)(wert); x.blockSignals(False)


class TextfeldAbschnitt(Abschnitt):
    geaendert = Signal()

    def __init__(self, parent=None):
        super().__init__("Ausrichtung")
        self.vertikal, self.richtung = Auswahlfeld(), Auswahlfeld()
        for k, n in F.VERTIKAL:
            self.vertikal.addItem(n, k)
        for k, n in RICHTUNGEN:
            self.richtung.addItem(n, k)
        self.winkel = SchrittFeld(-180, 180, "°", 5, 0, 0)
        self.raender = {k: SchrittFeld(0, 60 / _PT, "Inch", 0.05, 2, 0) for k in "lrou"}
        for x in self.raender.values():
            x.feld.setLocale(QLocale(QLocale.German, QLocale.Germany))
            x.feld.setValue(0.0)
        self.gerade = UmbruchSchalter("Text nicht drehen")
        self.anpassen = UmbruchSchalter("Größe der Form dem Text anpassen"); self.anpassen.setChecked(True)
        self.umbruch = UmbruchSchalter("Text in Form umbrechen"); self.umbruch.setChecked(True)
        self.zeile("Vertikale Ausrichtung:", self.vertikal); self.zeile("Textrichtung:", self.richtung)
        self.zeile("Benutzerdefinierter Textwinkel:", self.winkel)
        self._rand_texte = []
        for k, t in (("l", "Linker Rand:"), ("r", "Rechter Rand:"), ("o", "Oberer Rand:"), ("u", "Unterer Rand:")):
            l = QLabel(t); self._rand_texte.append(l); self.zeile(l, self.raender[k])
        for x in (self.gerade, self.anpassen, self.umbruch):
            self.breit(x)
        for c in (self.vertikal, self.richtung):
            c.currentIndexChanged.connect(lambda *_: self.geaendert.emit())
        for x in (self.winkel, *self.raender.values()):
            x.valueChanged.connect(lambda *_: self.geaendert.emit())
        for x in (self.gerade, self.anpassen, self.umbruch):
            x.toggled.connect(lambda *_: self.geaendert.emit())
        self.freigeben(False, False)
        self.knopf.setChecked(True)

    def freigeben(self, raender: bool, gerade: bool) -> None:
        for x in (*self.raender.values(), self.anpassen, self.umbruch, *self._rand_texte):
            x.setEnabled(raender)
        self.gerade.setEnabled(gerade)

    def setze(self, feld: dict) -> None:
        """Ohne Meldung."""
        for c, d in ((self.vertikal, feld["vertikal"]), (self.richtung, feld["richtung"])):
            _still(c, max(0, c.findData(d)), "setCurrentIndex")
        _still(self.winkel, float(feld["winkel"] or 0.0), "setValue")
        for k, x in self.raender.items():
            _still(x.feld, round(float(feld["raender"][k]) / _PT, 2), "setValue")
        for x, w in ((self.gerade, bool(feld.get("gerade"))), (self.anpassen, feld["anpassen"] is not False), (self.umbruch, feld["umbruch"] is not False)):
            _still(x, w, "setChecked")

    def werte(self) -> dict:
        return {"vertikal": self.vertikal.currentData(), "richtung": self.richtung.currentData(), "winkel": self.winkel.value(),
                "anpassen": self.anpassen.isChecked(), "umbruch": self.umbruch.isChecked(), "gerade": self.gerade.isChecked(),
                "raender": {k: round(x.value() * _PT, 2) for k, x in self.raender.items()}}
