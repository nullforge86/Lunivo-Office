from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_TEXTEFFEKT
from vcl.qt.widgets.dialoge.formatierung.texteffekt_panel import TexteffektPanel


class TexteffektDialog(PanelFaehig, QDialog):
    """Das Fenster „Texteffekte formatieren“: das Panel mit „OK“ (wie in der Vorlage; das Schließen-Kreuz bricht ab). Felder des Panels sind hier erreichbar."""

    def __init__(self, parent=None, werte: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Texteffekte formatieren")
        v = _spalte("standard", self)
        self.panel = TexteffektPanel(self, werte)
        v.addWidget(self.panel, 1)
        self.resize(*GROESSE_FENSTER_TEXTEFFEKT)
        fussleiste(self, v, nur_ok=True)

    def passe_an(self, breite: int, hoehe: int) -> None:
        """Die Seite nimmt die ganze Höhe der Seitenleiste: die Abschnitte rollen sonst in einem winzigen Streifen."""
        self.setMinimumHeight(max(300, hoehe - 20))                       # abzüglich Knopfzeile

    def __getattr__(self, name: str):
        if name == "panel":                                  # noch nicht gebaut: kein Umweg über das Panel
            raise AttributeError(name)
        return getattr(self.panel, name)
