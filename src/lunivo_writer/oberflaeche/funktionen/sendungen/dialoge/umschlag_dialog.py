"""Dialog „Umschlag“: Format, Absender und Empfänger."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QPlainTextEdit

from lunivo_writer.farmwork.funktionen.sendungen.formate import umschlag_formate
from lunivo_writer.oberflaeche.baukasten.basis.mass import HOEHE_TEXT_KURZ, HOEHE_TEXT_MITTEL
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FormularGitter
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.funktionen.sendungen.dialoge.dialog_hilfen import hinweis, ok_zeile


class UmschlagDialog(PanelFaehig, QDialog):
    def __init__(self, parent, absender: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Umschlag")
        f = FormularGitter(self)
        f.breit(hinweis("Das Blatt wird auf Umschlagformat gestellt und beides eingesetzt.\nDanach steht der Umschlag allein im Dokument."))
        self.format = Auswahlfeld(); self.format.addItems(list(umschlag_formate()))
        self.absender = QPlainTextEdit(absender); self.absender.setFixedHeight(HOEHE_TEXT_KURZ)
        self.empfaenger = QPlainTextEdit("Vorname Nachname\nStraße 1\n12345 Ort"); self.empfaenger.setFixedHeight(HOEHE_TEXT_MITTEL)
        f.zeile("Format", self.format); f.zeile("Absender", self.absender); f.zeile("Empfänger", self.empfaenger)
        f.breit(ok_zeile(self, "Anlegen"))
