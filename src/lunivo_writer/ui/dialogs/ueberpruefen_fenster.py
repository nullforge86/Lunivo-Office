"""Fenster des Reiters „Überprüfen“ nach den Vorlagen (ueberpruefen/02, 10).

    d = WoerterDialog(parent, ohne, mit)        # Statistiken; ohne/mit: Werte aus editor/statistik.zaehlen, mit = samt Noten
    d = SchutzDialog(parent, art)               # Bearbeitung einschränken (Seitenleiste); if d.exec(): d.ergebnis() → art | None

Die Fenster ändern das Dokument nicht; der Aufrufer (``Befehle``) setzt das Ergebnis um.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QDialog, QGridLayout, QLabel, QPushButton, QRadioButton, QVBoxLayout

from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

ZEILEN = (("seiten", "Seiten"), ("woerter", "Wörter"), ("zeichen_ohne", "Zeichen (keine Leerzeichen)"),
          ("zeichen_mit", "Zeichen (mit Leerzeichen)"), ("absaetze", "Absätze"), ("nicht_asiatisch", "Nicht-asiatische Wörter"),
          ("asiatisch", "Asiatische Zeichen"))

# Arten des Dokumentschutzes wie in der Vorlage; Formulare kennt Lunivo noch nicht (bleibt grau)
SCHUTZ_ARTEN = (("lesen", "Schreibgeschützt"), ("aenderungen", "Nachverfolgte Änderungen"), ("kommentare", "Kommentare"),
                ("formulare", "Ausfüllen von Formularen"))


from lunivo_writer.ui.baukasten.formular_gitter import UmbruchSchalter  # noqa: E402

class WoerterDialog(PanelFaehig, QDialog):
    """„Wörter zählen“: die Statistiken untereinander, Werte rechtsbündig; der Haken nimmt Fuß- und Endnoten dazu."""

    def __init__(self, parent=None, ohne: dict | None = None, mit: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Wörter zählen")
        self.ohne, self.mit = dict(ohne or {}), dict(mit or ohne or {})
        v = QVBoxLayout(self)
        v.addWidget(QLabel("Statistiken:"))
        g = QGridLayout(); g.setContentsMargins(6, 8, 6, 8); g.setHorizontalSpacing(16); g.setVerticalSpacing(6)
        self.werte: dict[str, QLabel] = {}
        for i, (key, text) in enumerate(ZEILEN):
            wert = QLabel(); wert.setAlignment(Qt.AlignRight | Qt.AlignVCenter); wert.setAccessibleName(text)
            g.addWidget(QLabel(text), i, 0); g.addWidget(wert, i, 1)
            self.werte[key] = wert
        g.setColumnStretch(0, 1)
        v.addLayout(g)
        self.noten = UmbruchSchalter("Textfelder, Fußnoten und Endnoten einbeziehen(&F)")
        self.noten.setToolTip("Textfelder stehen in Lunivo im Text und zählen immer; der Haken nimmt Fuß- und Endnoten dazu.")
        self.noten.toggled.connect(self._zeigen)
        v.addWidget(self.noten)
        fussleiste(self, v, ok_text="Schließen", nur_ok=True)
        self._zeigen()

    def _zeigen(self, *_):
        quelle = self.mit if self.noten.isChecked() else self.ohne
        for key, lab in self.werte.items():
            lab.setText(f"{quelle.get(key, 0):n}")


class SchutzDialog(PanelFaehig, QDialog):
    """„Bearbeitung einschränken“ in der Seitenleiste: Dokumentschutz einstellen und „Schutz starten …“; steht ein Schutz,
    heißt der Knopf „Schutz beenden“. Formatvorlagen-Einschränkung kennt Lunivo noch nicht (grau, wie in der Vorlage ohne Haken)."""

    def __init__(self, parent=None, art: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Bearbeitung einschränken")
        self.art = art
        v = QVBoxLayout(self)
        self.formate = UmbruchSchalter("Formatierungen auf eine Auswahl von Formatvorlagen beschränken")
        self.formate.setEnabled(False); self.formate.setToolTip("Das kann Lunivo noch nicht.")
        v.addWidget(self.formate)
        einst = QPushButton("Einstellungen …"); einst.setEnabled(False); einst.setMinimumHeight(36)
        v.addWidget(einst, 0, Qt.AlignLeft)
        self.schutz = UmbruchSchalter("Dokumentschutz einstellen")
        self.schutz.setChecked(art is not None)
        v.addWidget(self.schutz)
        self.gruppe = QButtonGroup(self)
        self.wahl: dict[str, QRadioButton] = {}
        for key, text in SCHUTZ_ARTEN:
            r = QRadioButton(text); r.setProperty("art", key)
            self.gruppe.addButton(r); self.wahl[key] = r
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
