"""Kleine Fenster des Reiters Einfügen nach den WPS-Vorlagen: „Zahl“, „Felder“, „Text in Tabelle umwandeln“, „Tabelle in Text konvertieren“.

    d = ZahlDialog(parent)                 # if d.exec(): d.ergebnis() → "XIV"
    d = FelderDialog(parent, kontext)      # if d.exec(): d.feld() → (Anweisung, Ergebnis)
    d = TrennerDialog(parent, zu_tabelle=True, texte=[…])   # if d.exec(): d.trenner(), d.spalten()

Die Fenster ändern das Dokument nicht; der Aufrufer (``Befehle``) fügt das Ergebnis ein.
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QRadioButton, QSpinBox, QVBoxLayout,
)

from lunivo_writer.editor import felder as F
from lunivo_writer.editor import tabelle_text as TT
from lunivo_writer.editor import zahlformat as Z
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste


def _titel(text: str, feld) -> QLabel:
    t = QLabel(text); t.setBuddy(feld)
    return t


class ZahlDialog(QDialog):
    """Feld „Zahl“, darunter die Liste „Zahlentyp“ (wie die Vorlage „Zahl“)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zahl")
        v = QVBoxLayout(self)
        self.zahl = QLineEdit(); self.zahl.setMinimumHeight(34); self.zahl.setAccessibleName("Zahl")
        v.addWidget(_titel("&Zahl", self.zahl)); v.addWidget(self.zahl)
        self.typ = QListWidget(); self.typ.setAccessibleName("Zahlentyp")
        for k, t in Z.TYPEN:
            it = QListWidgetItem(t); it.setData(Qt.UserRole, k); self.typ.addItem(it)
        self.typ.setCurrentRow(0)
        self.typ.setMinimumHeight(self.typ.sizeHintForRow(0) * 5 + 8)
        v.addWidget(_titel("Zahlen&typ", self.typ)); v.addWidget(self.typ)
        self.hinweis = QLabel(""); self.hinweis.setStyleSheet("color: palette(mid);"); self.hinweis.setWordWrap(True)
        v.addWidget(self.hinweis)
        self.ok = fussleiste(self, v, bei_ok=self._pruefen)
        self.typ.itemDoubleClicked.connect(lambda _i: self._pruefen())
        self.zahl.textChanged.connect(lambda _t: self.hinweis.setText(""))
        self.resize(300, 0)

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


class FelderDialog(QDialog):
    """Links die Feldnamen, rechts Beschreibung, Feldanweisung und Ergebnis."""

    def __init__(self, parent=None, kontext: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Felder")
        self.kontext = kontext or {}
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(12)
        self.liste = QListWidget(); self.liste.setAccessibleName("Feldnamen"); self.liste.addItems(list(F.FELDER))
        self.liste.setMinimumWidth(170)
        g.addWidget(_titel("&Feldnamen:", self.liste), 0, 0); g.addWidget(self.liste, 1, 0, 3, 1)
        self.beschreibung = QLabel(); self.beschreibung.setWordWrap(True)
        self.anweisung = QLineEdit(); self.anweisung.setReadOnly(True); self.anweisung.setMinimumHeight(34); self.anweisung.setMinimumWidth(240)
        self.ergebnis_text = QLineEdit(); self.ergebnis_text.setReadOnly(True); self.ergebnis_text.setMinimumHeight(34)
        g.addWidget(self.beschreibung, 1, 1)
        rechts = QVBoxLayout()
        rechts.addWidget(_titel("Feld&anweisung:", self.anweisung)); rechts.addWidget(self.anweisung)
        rechts.addWidget(_titel("&Ergebnis:", self.ergebnis_text)); rechts.addWidget(self.ergebnis_text); rechts.addStretch(1)
        g.addLayout(rechts, 2, 1)
        g.setColumnStretch(1, 1)
        v.addLayout(g)
        fussleiste(self, v)
        self.liste.currentTextChanged.connect(self._zeigen)
        self.liste.itemDoubleClicked.connect(lambda _i: self.accept())
        self.liste.setCurrentRow(0)
        self.resize(520, 300)

    def _zeigen(self, name: str) -> None:
        text, anweisung = F.FELDER.get(name, ("", ""))
        self.beschreibung.setText(text); self.anweisung.setText(anweisung); self.anweisung.setCursorPosition(0)
        self.ergebnis_text.setText(F.ergebnis(name, self.kontext)); self.ergebnis_text.setCursorPosition(0)

    def feld(self) -> tuple[str, str]:
        return self.anweisung.text(), self.ergebnis_text.text()


class TrennerDialog(QDialog):
    """„Text in Tabelle umwandeln“ (mit Spaltenzahl) oder „Tabelle in Text konvertieren“: woran getrennt wird."""

    def __init__(self, parent=None, *, zu_tabelle: bool = True, texte: list[str] | None = None):
        super().__init__(parent)
        self.zu_tabelle, self.texte = zu_tabelle, list(texte or [])
        self.setWindowTitle("Text in Tabelle umwandeln" if zu_tabelle else "Tabelle in Text konvertieren")
        v = QVBoxLayout(self)
        if zu_tabelle:
            g = QGridLayout()
            self._spalten = QSpinBox(); self._spalten.setRange(1, 63); self._spalten.setMinimumHeight(34); self._spalten.setMinimumWidth(90)
            self._zeilen = QLabel()
            g.addWidget(_titel("&Spaltenanzahl:", self._spalten), 0, 0); g.addWidget(self._spalten, 0, 1)
            g.addWidget(QLabel("Zeilenanzahl:"), 1, 0); g.addWidget(self._zeilen, 1, 1)
            g.setColumnStretch(2, 1)
            v.addLayout(g)
        t = QLabel("Text trennen bei" if zu_tabelle else "Zellen trennen durch"); f = t.font(); f.setBold(True); t.setFont(f)
        v.addWidget(t)
        self._gruppe = QButtonGroup(self)
        g = QGridLayout()
        for i, (_z, text) in enumerate(TT.TRENNER):
            r = QRadioButton(text); self._gruppe.addButton(r, i); g.addWidget(r, i // 3, i % 3)
        andere = QRadioButton("A&ndere:"); self._gruppe.addButton(andere, len(TT.TRENNER))
        self.andere = QLineEdit("-"); self.andere.setMaxLength(1); self.andere.setMaximumWidth(48); self.andere.setMinimumHeight(34)
        self.andere.setAlignment(Qt.AlignCenter); self.andere.setAccessibleName("Anderes Trennzeichen")
        z = QHBoxLayout(); z.addWidget(andere); z.addWidget(self.andere); z.addStretch(1)
        g.addLayout(z, 2, 0, 1, 3)
        v.addLayout(g)
        self.andere.textEdited.connect(lambda _t: andere.setChecked(True))
        vorgabe = "\t" if any("\t" in s for s in self.texte) or not zu_tabelle else "\n"
        self._gruppe.button([k for k, _t in TT.TRENNER].index(vorgabe)).setChecked(True)
        self._gruppe.idToggled.connect(lambda _i, an: an and self._zaehlen())
        self.andere.textChanged.connect(lambda _t: self._zaehlen())
        fussleiste(self, v)
        self._zaehlen()

    def trenner(self) -> str:
        i = self._gruppe.checkedId()
        return TT.TRENNER[i][0] if i < len(TT.TRENNER) else (self.andere.text() or "-")

    def spalten(self) -> int | None:
        return self._spalten.value() if self.zu_tabelle else None

    def _zaehlen(self) -> None:
        if not self.zu_tabelle:
            return
        z = TT.zellen(self.texte, self.trenner())
        self._spalten.setValue(max((len(r) for r in z), default=1))
        self._zeilen.setText(str(len(z)))


class SeitenzahlDialog(QDialog):
    """„Seitenzahl einfügen“: Position (Kopf-/Fußzeile), Ausrichtung und Schreibweise, mit kleinem Seitenbild."""

    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QComboBox
        from lunivo_writer.editor import seitenzahl as SZ
        from lunivo_writer.ui.baukasten.dialog_rahmen import VorschauFlaeche
        self.setWindowTitle("Seitenzahl einfügen")
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(12)
        self.muster = QComboBox(); self.ort = QComboBox(); self.ausrichtung = QComboBox()
        for k, t in SZ.MUSTER:
            self.muster.addItem(t, k)
        for k, t in (("kopf", "Kopfzeile"), ("fuss", "Fußzeile")):
            self.ort.addItem(t, k)
        for k, t in (("left", "Links"), ("center", "Mitte"), ("right", "Rechts")):
            self.ausrichtung.addItem(t, k)
        self.ort.setCurrentIndex(1); self.ausrichtung.setCurrentIndex(1)
        for i, (text, feld) in enumerate((("&Format:", self.muster), ("&Position:", self.ort), ("&Ausrichtung:", self.ausrichtung))):
            feld.setMinimumHeight(34); feld.setMinimumWidth(180)
            g.addWidget(_titel(text, feld), i, 0); g.addWidget(feld, i, 1)
        self.vorschau = VorschauFlaeche(self._male, 140, flaeche=False); self.vorschau.setFixedSize(110, 140)
        g.addWidget(self.vorschau, 0, 2, 4, 1)
        g.setRowStretch(3, 1)
        v.addLayout(g)
        fussleiste(self, v)
        for c in (self.muster, self.ort, self.ausrichtung):
            c.currentIndexChanged.connect(lambda _i: self.vorschau.update())

    def _male(self, p, r) -> None:
        from lunivo_writer.ui.baukasten.seiten_bildchen import seitenzahl_zeichner
        seitenzahl_zeichner(self.ort.currentData(), self.ausrichtung.currentData())(p, r)

    def werte(self) -> tuple[str, str, str]:
        return self.ort.currentData(), self.ausrichtung.currentData(), self.muster.currentData()
