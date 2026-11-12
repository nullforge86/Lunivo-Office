"""Abschnitt „ALTERNATIVTEXT“ (Titel und Beschreibung) für die Seite „Größe und Eigenschaften“ — nach der Vorlage.

``geaendert(titel, beschreibung)`` kommt 400 ms nach der letzten Eingabe; ``setze(titel, text)`` füllt die Felder, ohne etwas zu melden.
Mit ``mit_dekorativ`` steht darunter „Als dekorativ markieren“ (``dekorativ_geaendert(bool)``, ``setze_dekorativ``): ist es gesetzt, sind die Felder
gesperrt. ``mit_titel=False`` lässt das Titelfeld weg (Bilder haben nur eine Beschreibung).
"""
from __future__ import annotations

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import QCheckBox, QLineEdit, QPlainTextEdit

from lunivo_writer.oberflaeche.baukasten.formatierung.texteffekt_dialog import Abschnitt
from lunivo_writer.oberflaeche.baukasten.basis.mass import HOEHE_BEREICH_MITTEL


class AlternativtextAbschnitt(Abschnitt):
    geaendert = Signal(str, str)
    dekorativ_geaendert = Signal(bool)

    def __init__(self, parent=None, mit_titel: bool = True, mit_dekorativ: bool = False):
        super().__init__("Alternativtext")
        self.titel_feld = QLineEdit()
        self.text_feld = QPlainTextEdit(); self.text_feld.setMinimumHeight(HOEHE_BEREICH_MITTEL)
        self.titel_feld.setPlaceholderText("Titel eingeben"); self.text_feld.setPlaceholderText("Beschreibung eingeben")
        if mit_titel:
            self.gitter.reihe(("Titel", self.titel_feld))
        self.gitter.reihe(("Beschreibung", self.text_feld))       # Eingabe braucht Platz: Beschriftung darüber, Feld über die ganze Breite
        self._stumm = False
        self.dekorativ = QCheckBox("Als dekorativ markieren") if mit_dekorativ else None
        if self.dekorativ is not None:
            self.gitter.breit(self.dekorativ)
            self.dekorativ.toggled.connect(self._dekorativ)
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

    def _dekorativ(self, an: bool) -> None:
        self._felder_sperren(an)
        if not self._stumm:
            self.dekorativ_geaendert.emit(an)

    def _felder_sperren(self, an: bool) -> None:
        self.titel_feld.setEnabled(not an)
        self.text_feld.setEnabled(not an)

    def setze_dekorativ(self, an: bool) -> None:
        """Ohne Meldung."""
        if self.dekorativ is None:
            return
        self._stumm = True
        try:
            self.dekorativ.setChecked(bool(an))
            self._felder_sperren(bool(an))
        finally:
            self._stumm = False
