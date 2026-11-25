"""Dialog „Quelle“: Typ und Angaben einer Literaturquelle eingeben oder ändern."""
from __future__ import annotations

from PySide6.QtWidgets import QDialog

from framework.funktionen.verweise.konstanten import QUELLENTYPEN
from vcl.qt.widgets.bausteine.basis.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.bausteine.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.geruest.zusatz_panel import PanelFaehig


class QuelleDialog(PanelFaehig, QDialog):
    FELDER = [("autor", "Autor(en) — „Nachname, Vorname; …“"), ("titel", "Titel"), ("jahr", "Jahr"), ("verlag", "Verlag"),
              ("ort", "Ort"), ("url", "Adresse (URL)")]

    def __init__(self, parent, q: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Quelle")
        q = q or {}
        f = FormularGitter(self)
        self.typ = Auswahlfeld(); self.typ.addItems(list(QUELLENTYPEN)); self.typ.setCurrentText(q.get("typ", "Buch"))
        f.zeile("Typ", self.typ)
        self.eingaben = {}
        for k, t in self.FELDER:
            e = zeilenfeld("frei", q.get(k, "")); self.eingaben[k] = e; f.zeile(t, e)
        f.breit(knopfzeile(self))

    def ergebnis(self) -> dict:
        d = {k: e.text().strip() for k, e in self.eingaben.items()}
        d["typ"] = self.typ.currentText()
        return d
