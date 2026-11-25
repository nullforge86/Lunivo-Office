"""Dialog zum Anlegen eines Formularfelds (Textfeld, Auswahlliste, Datum, Kontrollkästchen, Schaltfläche)."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QLineEdit, QPlainTextEdit

from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.rendering.textfelder import formular as FO
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_TEXT_NORMAL
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld

TITEL = {"text": "Textfeld", "auswahl": "Auswahlliste", "datum": "Datumsfeld", "kasten": "Kontrollkästchen", "knopf": "Schaltfläche"}


from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
class FormFeldDialog(PanelFaehig, QDialog):
    def __init__(self, fenster, art: str, bestehend: dict | None = None):
        super().__init__(fenster)
        self.art = art
        m = bestehend or {}
        self.setWindowTitle(TITEL[art] + " einfügen" if not bestehend else TITEL[art] + " bearbeiten")
        f = FormularGitter()
        self.name = zeilenfeld("frei", m.get("name", ""))
        self.name.setPlaceholderText("z. B. Vorname")
        f.zeile("Name des Feldes", self.name)
        self.platz = zeilenfeld("frei", m.get("platzhalter", ""))
        self.beschriftung = zeilenfeld("frei", m.get("beschriftung", ""))
        self.liste = QPlainTextEdit("\n".join(m.get("optionen", [])))
        self.aufschrift = zeilenfeld("frei", m.get("aufschrift", "Absenden"))
        self.aktion = Auswahlfeld(); self.aktion.addItems(FO.AKTIONEN); self.aktion.setCurrentText(m.get("aktion", "Keine"))
        if art in ("text", "auswahl", "datum"):
            self.platz.setPlaceholderText({"text": "Text eingeben", "auswahl": "Auswahl treffen", "datum": "Datum wählen"}[art])
            f.zeile("Hinweis im leeren Feld", self.platz)
        if art == "auswahl":
            self.liste.setPlaceholderText("Ein Eintrag pro Zeile")
            self.liste.setFixedHeight(HOEHE_TEXT_NORMAL)
            f.zeile("Einträge", self.liste)
        if art == "kasten":
            f.zeile("Beschriftung daneben", self.beschriftung)
        if art == "knopf":
            f.zeile("Aufschrift", self.aufschrift)
            f.zeile("Aktion beim Klicken", self.aktion)
        v = _spalte("standard", self)
        v.addLayout(f)
        info = QLabel("Felder werden in DOCX als Inhaltssteuerelemente gespeichert und lassen sich auch in anderen Textprogrammen ausfüllen.")
        info.setWordWrap(True)
        hinweis_stil(info)
        v.addWidget(info)
        v.addWidget(knopfzeile(self, bei_ok=self._ok))

    def _ok(self) -> None:
        if self.art == "auswahl" and not [z for z in self.liste.toPlainText().splitlines() if z.strip()]:
            self.liste.setFocus()
            return
        self.accept()

    def meta(self) -> dict:
        if self.art == "auswahl":
            return FO.meta("auswahl", self.name.text().strip(), platzhalter=self.platz.text().strip(),
                           optionen=[z.strip() for z in self.liste.toPlainText().splitlines() if z.strip()])
        if self.art == "kasten":
            return FO.meta("kasten", self.name.text().strip(), beschriftung=self.beschriftung.text().strip())
        if self.art == "knopf":
            return FO.meta("knopf", self.name.text().strip(), aufschrift=self.aufschrift.text().strip() or "Schaltfläche",
                           aktion=self.aktion.currentText())
        return FO.meta(self.art, self.name.text().strip(), platzhalter=self.platz.text().strip())
