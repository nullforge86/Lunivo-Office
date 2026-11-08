"""Abschnitt „ALTERNATIVTEXT“ (Titel und Beschreibung) für die Seite „Größe und Eigenschaften“ — nach der Vorlage.

``geaendert(titel, beschreibung)`` kommt 400 ms nach der letzten Eingabe; ``setze(titel, text)`` füllt die Felder, ohne etwas zu melden.
"""
from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QLineEdit, QPlainTextEdit

from lunivo_writer.ui.baukasten.formatierung.texteffekt_dialog import Abschnitt
from lunivo_writer.ui.baukasten.basis.mass import HOEHE_BEREICH_MITTEL


class AlternativtextAbschnitt(Abschnitt):
    geaendert = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__("Alternativtext")
        self.titel_feld = QLineEdit()
        self.text_feld = QPlainTextEdit(); self.text_feld.setMinimumHeight(HOEHE_BEREICH_MITTEL)
        self.titel_feld.setPlaceholderText("Titel eingeben"); self.text_feld.setPlaceholderText("Beschreibung eingeben")
        self.gitter.reihe(("Titel", self.titel_feld)); self.gitter.reihe(("Beschreibung", self.text_feld))       # Eingabe braucht Platz: Beschriftung darüber, Feld über die ganze Breite
        self._stumm = False
        self._timer = QTimer(self); self._timer.setSingleShot(True); self._timer.setInterval(400)
        self._timer.timeout.connect(lambda: self.geaendert.emit(self.titel_feld.text(), self.text_feld.toPlainText()))
        self.titel_feld.textChanged.connect(self._start); self.text_feld.textChanged.connect(self._start)
        self.knopf.setChecked(True)

    def _start(self, *_) -> None:
        if not self._stumm:
            self._timer.start()

    def setze(self, titel: str, text: str) -> None:
        """Ohne Meldung; ein Feld mit dem Fokus (Eingabe läuft) bleibt unberührt."""
        self._stumm = True
        try:
            if not self.titel_feld.hasFocus():
                self.titel_feld.setText(titel or "")
            if not self.text_feld.hasFocus():
                self.text_feld.setPlainText(text or "")
        finally:
            self._stumm = False
