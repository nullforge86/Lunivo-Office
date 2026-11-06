"""Basis der Erstellen-Fenster „Schnelle KI-Aktion“ und „Neuen Assistenten erstellen“: Hinweis, Vorlagen-Chips, Name, Prompt, Knopfzeile.

    class MeinFenster(ErstellenFenster):
        def __init__(self, fenster):
            super().__init__(fenster, "Titel", "Hinweis", vorlagen_namen, meldung="Name und Prompt werden gebraucht.")
            self.name_zeile("Name *", "Platzhalter"); self.prompt_zeile("Prompt *", "Platzhalter")      # Reihenfolge bestimmt das Fenster
            self.abschliessen()
Die Felder landen in ``self.gitter`` (FormularGitter); Unterklassen hängen eigene Zeilen dazwischen."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QLineEdit, QMessageBox, QPlainTextEdit, QVBoxLayout, QWidget

from lunivo_writer.ui.baukasten.dialog_rahmen import knopfzeile
from lunivo_writer.ui.baukasten.formular_gitter import FormularGitter, abschnittstitel
from lunivo_writer.ui.baukasten.mass import GEWICHT_SYMBOL_NAME, HOEHE_TEXT_NORMAL, NAME_MAX_ZEICHEN
from lunivo_writer.ui.baukasten.vorlagen_chips import VorlagenChips
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

TITEL_VORLAGEN = "Mit einer Vorlage beginnen"


class ErstellenFenster(PanelFaehig, QDialog):
    def __init__(self, fenster, titel: str, hinweis: str, vorlagen_namen, *, meldung: str, ok_text: str = "Erstellen"):
        super().__init__(fenster)
        self.fenster, self._meldung, self._ok_text = fenster, meldung, ok_text
        self.setWindowTitle(titel)
        self._wurzel = QVBoxLayout(self)
        self._inhalt = QWidget(); self.gitter = FormularGitter(self._inhalt)
        kopf = QLabel(hinweis); kopf.setWordWrap(True)
        self.gitter.breit(kopf)
        self.gitter.breit(abschnittstitel(TITEL_VORLAGEN))
        self.chips = VorlagenChips(vorlagen_namen)
        self.chips.gewaehlt.connect(self.vorlage_gewaehlt)
        self.gitter.breit(self.chips)
        self.name = QLineEdit(); self.name.setMaxLength(NAME_MAX_ZEICHEN)
        self.prompt = QPlainTextEdit(); self.prompt.setMinimumHeight(HOEHE_TEXT_NORMAL)

    def name_zeile(self, beschriftung: str, platzhalter: str, symbol=None) -> None:
        """Namensfeld; mit ``symbol`` (Symbolwahl) steht es links daneben, die Beschriftungen darüber."""
        self.name.setPlaceholderText(platzhalter)
        if symbol is None:
            self.gitter.zeile(beschriftung, self.name)
        else:
            self.gitter.reihe(("Symbol", symbol), (beschriftung, self.name), gewichte=GEWICHT_SYMBOL_NAME)

    def prompt_zeile(self, beschriftung: str, platzhalter: str) -> None:
        self.prompt.setPlaceholderText(platzhalter)
        self.gitter.zeile(beschriftung, self.prompt)

    def abschliessen(self) -> None:
        self._wurzel.addWidget(self._inhalt)
        z = knopfzeile(self, bei_ok=self._ok, ok_text=self._ok_text)
        self.ok = z.ok
        self._wurzel.addWidget(z)

    def vorlage_gewaehlt(self, i: int) -> None:
        """Hier füllt die Unterklasse die Felder aus der Vorlage Nr. ``i``."""

    def _ok(self) -> None:
        if not self.name.text().strip() or not self.prompt.toPlainText().strip():
            QMessageBox.information(self, self.windowTitle(), self._meldung)
            return
        self.accept()
