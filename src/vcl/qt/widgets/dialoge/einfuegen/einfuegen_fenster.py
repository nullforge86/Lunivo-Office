from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QListWidgetItem
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from writer.anbindung import zahlformat as Z
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.abstaende.mass import EINFUEGEN_TYP_ZEILEN
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_SEITENLEISTE, ZUGABE_LISTE
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster_hilfen import _titel


class ZahlDialog(PanelFaehig, QDialog):
    """Feld „Zahl“, darunter die Liste „Zahlentyp“ (wie die Vorlage „Zahl“)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zahl")
        v = _spalte("standard", self)
        self.zahl = zeilenfeld("standard", name="Zahl")
        v.addWidget(_titel("&Zahl", self.zahl)); v.addWidget(self.zahl)
        self.typ = QListWidget(); self.typ.setAccessibleName("Zahlentyp")
        for k, t in Z.typen():
            it = QListWidgetItem(t); it.setData(Qt.UserRole, k); self.typ.addItem(it)
        self.typ.setCurrentRow(0)
        self.typ.setMinimumHeight(self.typ.sizeHintForRow(0) * EINFUEGEN_TYP_ZEILEN + ZUGABE_LISTE)
        v.addWidget(_titel("Zahlen&typ", self.typ)); v.addWidget(self.typ)
        self.hinweis = QLabel(""); hinweis_stil(self.hinweis); self.hinweis.setWordWrap(True)
        v.addWidget(self.hinweis)
        self.ok = fussleiste(self, v, bei_ok=self._pruefen)
        self.typ.itemDoubleClicked.connect(lambda _i: self._pruefen())
        self.zahl.textChanged.connect(lambda _t: self.hinweis.setText(""))
        self.resize(BREITE_SEITENLEISTE, 0)

    def ergebnis(self) -> str:
        """Die Zahl im gewählten Typ; ``ValueError`` bei falscher Eingabe."""
        text = self.zahl.text().strip().replace(".", "")
        if not text.isdigit():
            raise ValueError("Bitte eine ganze Zahl eingeben.")
        return Z.zahl_text(int(text), self.typ.currentItem().data(Qt.UserRole))

    def _pruefen(self) -> None:
        try:
            self.ergebnis()
        except ValueError as e:
            self.hinweis.setText(str(e)); self.zahl.setFocus()
            return
        self.accept()


class AutoTextDialog(PanelFaehig, QDialog):
    """„AutoText erstellen“: Name für die Markierung (Vorschlag: ihre ersten Wörter)."""

    def __init__(self, parent=None, markierung: str = ""):
        super().__init__(parent)
        self.setWindowTitle("AutoText erstellen")
        v = _spalte("standard", self)
        self.feld = zeilenfeld("gross", " ".join(markierung.split()[:4])[:40])
        t = _titel("Bitte geben Sie einen &Namen für den AutoText-Eintrag an:", self.feld); t.setWordWrap(True)
        v.addWidget(t); v.addWidget(self.feld); v.addStretch(1)
        self.ok = fussleiste(self, v)
        self.feld.textChanged.connect(lambda x: self.ok.setEnabled(bool(x.strip())))
        self.ok.setEnabled(bool(self.feld.text().strip()))

    def name(self) -> str:
        return self.feld.text().strip()
