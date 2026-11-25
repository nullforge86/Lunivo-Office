"""Dialog „Umschlag“: Format, Absender und Empfänger."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog, QPlainTextEdit

from writer.anbindung.sendungsformate import umschlag_formate
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_TEXT_KURZ, HOEHE_TEXT_MITTEL
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.sendungen.dialog_hilfen import hinweis, ok_zeile


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
