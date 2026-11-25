"""Dialog „Beschriftung“ wie die Vorlage: Feld mit „Tabelle 1“ zum Weiterschreiben, Bezeichnung, Position (nur bei markiertem Objekt), „Bezeichnung nicht in der
Beschriftung verwenden“, Neues Etikett / Bezeichnung löschen / Nummerierung.

    d = BeschriftungDialog(parent, eigene, naechste, objekt=True, label="Tabelle")     # if d.exec(): d.ergebnis(), d.eigene

``naechste(label, zahl)`` liefert die Nummer der neuen Beschriftung. ``ergebnis()`` → label, nach, oben, ohne, zahl; ``eigene`` ist die (geänderte) Liste
eigener Bezeichnungen, die der Aufrufer sich merkt."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLineEdit, QPushButton

from lunivo_writer.farmwork.funktionen.verweise.konstanten import BESCHRIFTUNGS_BEZEICHNUNGEN
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import fussleiste
from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_MIN_ZEICHEN, HOEHE_KNOPF, HOEHE_KNOPF_GROSS
from lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster import EingabeFenster
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout, FormularGitter, UmbruchSchalter
from lunivo_writer.oberflaeche.baukasten.geruest.rollen import spalte as _spalte
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.funktionen.verweise.dialoge.dialog_hilfen import titel as _titel
from lunivo_writer.oberflaeche.funktionen.verweise.dialoge.nummerierung_dialog import NummerierungDialog


class BeschriftungDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, eigene: list[str] | None = None, naechste=None, objekt: bool = False, label: str = "Abbildung"):
        super().__init__(parent)
        self.setWindowTitle("Beschriftung")
        self._naechste = naechste or (lambda _l, _z: "1")
        self.eigene = list(eigene or [])
        self.zahl = "arabisch"
        self._vorne = ""
        v = _spalte("standard", self)
        g = FormularGitter()                                                   # passt sich der Breite an (Seitenleiste), nichts abgeschnitten
        self.text = QLineEdit(); self.text.setMinimumHeight(HOEHE_KNOPF); self.text.setAccessibleName("Beschriftung")
        g.breit(_titel("&Beschriftung:", self.text)); g.breit(self.text)
        self.label = Auswahlfeld(); self.label.setAccessibleName("Bezeichnung")
        self.label.addItems(list(BESCHRIFTUNGS_BEZEICHNUNGEN) + [x for x in self.eigene if x not in BESCHRIFTUNGS_BEZEICHNUNGEN])
        self.label.setCurrentText(label)
        self.pos = Auswahlfeld(); self.pos.addItems(["Unter dem ausgewählten Element", "Über dem ausgewählten Element"])
        self.pos.setEnabled(objekt); self.pos.setAccessibleName("Position")
        self.pos.zeichen(DROPDOWN_MIN_ZEICHEN)
        g.zeile(_titel("B&ezeichnung:", self.label), self.label)
        g.zeile(_titel("&Position:", self.pos), self.pos)
        self.ohne = UmbruchSchalter("Be&zeichnung nicht in der Beschriftung verwenden"); g.breit(self.ohne)
        z = FlussLayout(8)
        self.neu, self.loeschen, self.nummerierung = QPushButton("Neues &Etikett…"), QPushButton("Bezeichnung &löschen"), QPushButton("N&ummerierung…")
        for k in (self.neu, self.loeschen, self.nummerierung):
            k.setMinimumHeight(HOEHE_KNOPF_GROSS); z.addWidget(k)
        g.breit(z)
        v.addLayout(g); v.addStretch(1)
        fussleiste(self, v)
        self.neu.clicked.connect(self._neu); self.loeschen.clicked.connect(self._loeschen); self.nummerierung.clicked.connect(self._nummerierung)
        self.label.currentTextChanged.connect(lambda _t: self._vorspann())
        self.ohne.toggled.connect(lambda _a: self._vorspann())
        self._vorspann()

    def _vorspann(self) -> None:
        """Den Anfang „Tabelle 1“ im Feld erneuern, Geschriebenes dahinter behalten."""
        rest = self.text.text()[len(self._vorne):] if self.text.text().startswith(self._vorne) else ""
        nr = self._naechste(self.label.currentText(), self.zahl)
        self._vorne = nr if self.ohne.isChecked() else f"{self.label.currentText()} {nr}"
        self.text.setText(self._vorne + rest)
        self.loeschen.setEnabled(self.label.currentText() not in BESCHRIFTUNGS_BEZEICHNUNGEN)

    def _neu(self) -> None:
        t, ok = EingabeFenster.getText(self, "Neue Bezeichnung", "&Bezeichnung:")
        t = " ".join(t.split())
        if ok and t:
            if self.label.findText(t) < 0:
                self.label.addItem(t); self.eigene.append(t)
            self.label.setCurrentText(t)

    def _loeschen(self) -> None:
        t = self.label.currentText()
        if t in self.eigene:
            self.eigene.remove(t)
            self.label.removeItem(self.label.currentIndex())

    def _nummerierung(self) -> None:
        d = NummerierungDialog(self, self.zahl)
        if d.exec():
            self.zahl = d.zahl()
            self._vorspann()

    def ergebnis(self) -> dict:
        t = self.text.text()
        nach = t[len(self._vorne):] if t.startswith(self._vorne) else (": " + t.strip() if t.strip() else "")
        return {"label": self.label.currentText(), "nach": nach, "oben": self.pos.isEnabled() and self.pos.currentIndex() == 1,
                "ohne": self.ohne.isChecked(), "zahl": self.zahl}
