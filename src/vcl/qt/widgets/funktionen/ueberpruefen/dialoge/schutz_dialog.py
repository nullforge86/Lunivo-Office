"""Dialog „Bearbeitung einschränken“ (Seitenleiste): Dokumentschutz einstellen und „Schutz starten …“; steht ein Schutz, heißt der Knopf „Schutz beenden“.

    d = SchutzDialog(parent, art)               # if d.exec(): d.ergebnis() → art | None

Das Fenster ändert das Dokument nicht; der Aufrufer setzt das Ergebnis um."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QDialog, QRadioButton

from vcl.qt.widgets.bausteine.basis.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.bausteine.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.bausteine.option.option import option
from vcl.qt.widgets.bausteine.felder.formular_gitter import UmbruchSchalter
from vcl.qt.widgets.bausteine.geruest.rollen import spalte as _spalte
from vcl.qt.widgets.bausteine.geruest.zusatz_panel import PanelFaehig

# Arten des Dokumentschutzes wie in der Vorlage; Formulare kennt Lunivo noch nicht (bleibt grau)
SCHUTZ_ARTEN = (("lesen", "Schreibgeschützt"), ("aenderungen", "Nachverfolgte Änderungen"), ("kommentare", "Kommentare"),
                ("formulare", "Ausfüllen von Formularen"))


class SchutzDialog(PanelFaehig, QDialog):
    """„Bearbeitung einschränken“ in der Seitenleiste: Dokumentschutz einstellen und „Schutz starten …“; steht ein Schutz,
    heißt der Knopf „Schutz beenden“. Formatvorlagen-Einschränkung kennt Lunivo noch nicht (grau, wie in der Vorlage ohne Haken)."""

    def __init__(self, parent=None, art: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Bearbeitung einschränken")
        self.art = art
        v = _spalte("panel", self)
        self.formate = UmbruchSchalter("Formatierungen auf eine Auswahl von Formatvorlagen beschränken")
        self.formate.setEnabled(False); self.formate.setToolTip("Das kann Lunivo noch nicht.")
        v.addWidget(self.formate)
        einst = knopf("gross", "Einstellungen …", aktiv=False)
        v.addWidget(einst, 0, Qt.AlignLeft)
        self.schutz = UmbruchSchalter("Dokumentschutz einstellen")
        self.schutz.setChecked(art is not None)
        v.addWidget(self.schutz)
        self.gruppe = QButtonGroup(self)
        self.wahl: dict[str, QRadioButton] = {}
        for key, text in SCHUTZ_ARTEN:
            r = option("standard", text, name=text, gruppe=self.gruppe); r.setProperty("art", key)
            self.wahl[key] = r
            v.addWidget(r)
        self.wahl[art if art in self.wahl else "lesen"].setChecked(True)
        self.wahl["formulare"].setToolTip("Formularfelder kennt Lunivo noch nicht.")
        v.addStretch(1)
        self.ok = fussleiste(self, v, ok_text="Schutz beenden" if art else "Schutz starten …")
        self.schutz.toggled.connect(self._zustand)
        self._zustand()

    def _zustand(self, *_):
        an = self.schutz.isChecked() and self.art is None
        for key, r in self.wahl.items():
            r.setEnabled(an and key != "formulare")
        self.ok.setEnabled(self.art is not None or self.schutz.isChecked())

    def ergebnis(self) -> str | None:
        """Die gewählte Art des Schutzes; None: kein Schutz (auch nach „Schutz beenden“)."""
        if self.art is not None or not self.schutz.isChecked():
            return None
        return next(k for k, r in self.wahl.items() if r.isChecked())
