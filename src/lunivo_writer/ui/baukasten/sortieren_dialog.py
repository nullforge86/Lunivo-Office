"""Das Fenster „Text sortieren“ als Baustein (Start ▸ Absatz ▸ Sortieren): ein Hauptschlüssel und bis zu zwei weitere („Anschließend nach“),
je mit Typ (Text, Zahl, Datum) und Richtung; „Meine Liste enthält“ eine Überschriftenzeile oder nicht. „Option …“ öffnet die Sortieroptionen
(Feldtrenner, Groß-/Kleinschreibung, Sortiersprache) als Unterfenster.

    d = SortierenDialog(parent, texte)        # texte: die zu sortierenden Absätze — daraus ergibt sich die Zahl der Felder
    if ausfuehren(d): d.werte()               # {"schluessel": [(feld|None, typ, absteigend), …], "trenner", "gross_klein", "sprache", "kopfzeile"}

Das Fenster sortiert nicht selbst; der Aufrufer ruft ``editor.schreibweise.reihenfolge`` mit ``**d.werte()`` auf (``Befehle.sortieren``).
"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QButtonGroup, QCheckBox, QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QVBoxLayout,
    QWidget,
)

from lunivo_writer.editor.schreibweise import SPRACHEN, feldzahl
from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
from lunivo_writer.ui.baukasten.fenster_stapel import zeige_unter
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig

TYPEN = (("text", "Text"), ("zahl", "Zahl"), ("datum", "Datum"))
TRENNER = (("\t", "Tabstopps"), (",", "Kommata"))


def _titel(text: str) -> QWidget:
    """Abschnittstitel mit Linie bis zum rechten Rand, wie in der Vorlage."""
    w = QWidget(); h = QHBoxLayout(w); h.setContentsMargins(0, 6, 0, 0)
    h.addWidget(QLabel(text))
    linie = QFrame(); linie.setFrameShape(QFrame.HLine); linie.setFrameShadow(QFrame.Plain); linie.setStyleSheet("color: palette(midlight);")
    h.addWidget(linie, 1)
    return w


def _feld(w: QWidget, breite: int = 150) -> QWidget:
    w.setMinimumHeight(34); w.setMinimumWidth(breite)
    return w


class SortierOptionenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, trenner: str = "\t", gross_klein: bool = False, sprache: str = "de_DE", nur_spalte: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Sortieroptionen")
        v = QVBoxLayout(self)
        v.addWidget(_titel("Felder trennen bei"))
        self._trenner = QButtonGroup(self)
        for i, (_z, t) in enumerate(TRENNER):
            r = QRadioButton(t); self._trenner.addButton(r, i); v.addWidget(r)
        z = QHBoxLayout(); r = QRadioButton("Andere:"); self._trenner.addButton(r, len(TRENNER)); z.addWidget(r)
        self.andere = _feld(QLineEdit("-"), 44); self.andere.setMaximumWidth(48); self.andere.setMaxLength(1); self.andere.setAlignment(Qt.AlignCenter)
        z.addWidget(self.andere); z.addStretch(1); v.addLayout(z)
        bekannt = [k for k, _t in TRENNER]
        if trenner in bekannt:
            self._trenner.button(bekannt.index(trenner)).setChecked(True)
        else:
            r.setChecked(True); self.andere.setText(trenner or "-")
        self.andere.textEdited.connect(lambda _t: r.setChecked(True))
        v.addWidget(_titel("Sortieroptionen"))
        self.nur_spalte = QCheckBox("Nur Spalte sortieren"); self.nur_spalte.setChecked(nur_spalte); self.nur_spalte.setEnabled(False)
        self.gross_klein = QCheckBox("Groß-/Kleinschreibung beachten"); self.gross_klein.setChecked(gross_klein)
        v.addWidget(self.nur_spalte); v.addWidget(self.gross_klein)
        v.addWidget(_titel("Sortiersprache"))
        self.sprache = _feld(QComboBox(), 220)
        for k, t in SPRACHEN:
            self.sprache.addItem(t, k)
        self.sprache.setCurrentIndex(max(0, self.sprache.findData(sprache)))
        v.addWidget(self.sprache); v.addStretch(1)
        fussleiste(self, v)

    def trenner(self) -> str:
        i = self._trenner.checkedId()
        return TRENNER[i][0] if i < len(TRENNER) else (self.andere.text() or "-")


class _Schluessel:
    """Eine Zeile „nach … Typ … Aufsteigend/Absteigend“ im Raster ``g`` ab Zeile ``zeile`` (zwei Zeilen hoch)."""

    def __init__(self, g: QGridLayout, zeile: int, eltern: QDialog, mit_keine: bool):
        self.mit_keine = mit_keine
        self.feld = _feld(QComboBox(), 170)
        self.typ_text = QLabel("Typ:")
        self.typ = _feld(QComboBox(), 130)
        for k, t in TYPEN:
            self.typ.addItem(t, k)
        self.ordnung = QButtonGroup(eltern)
        self.auf, self.ab = QRadioButton("Aufsteigend"), QRadioButton("Absteigend")
        self.ordnung.addButton(self.auf, 0); self.ordnung.addButton(self.ab, 1); self.auf.setChecked(True)
        g.addWidget(self.feld, zeile, 0); g.addWidget(self.typ_text, zeile, 1); g.addWidget(self.typ, zeile, 2)
        g.addWidget(self.auf, zeile, 3); g.addWidget(self.ab, zeile + 1, 3)
        self.feld.currentIndexChanged.connect(lambda _i: self._aktiv())

    def fuellen(self, felder: int) -> None:
        alt = self.feld.currentData()
        self.feld.blockSignals(True); self.feld.clear()
        if self.mit_keine:
            self.feld.addItem("(Keine)", "keine")
        else:
            self.feld.addItem("Absätze", None)
        for i in range(felder if felder > 1 else 0):
            self.feld.addItem(f"Feld {i + 1}", i)
        i = self.feld.findData(alt)
        self.feld.setCurrentIndex(i if i >= 0 else 0)
        self.feld.blockSignals(False); self._aktiv()

    def _aktiv(self) -> None:
        an = self.feld.isEnabled() and self.feld.currentData() != "keine"
        for w in (self.typ_text, self.typ, self.auf, self.ab):
            w.setEnabled(an)

    def wert(self):
        d = self.feld.currentData()
        if not self.feld.isEnabled() or d == "keine":
            return None
        return (d, self.typ.currentData(), self.ordnung.checkedId() == 1)


class SortierenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, texte: list[str] | None = None):
        super().__init__(parent)
        self.setWindowTitle("Text sortieren")
        self.texte = list(texte or [])
        self._trenner, self._gross_klein, self._sprache = "\t", False, "de_DE"
        v = QVBoxLayout(self)
        g = QGridLayout(); g.setHorizontalSpacing(10); g.setVerticalSpacing(4)
        self.schluessel: list[_Schluessel] = []
        for n, titel in enumerate(("Sortieren nach", "Anschließend nach", "Anschließend nach")):
            g.addWidget(_titel(titel), n * 3, 0, 1, 4)
            self.schluessel.append(_Schluessel(g, n * 3 + 1, self, mit_keine=n > 0))
        g.setColumnStretch(0, 1)
        v.addLayout(g)
        v.addWidget(_titel("Meine Liste enthält"))
        kz = QFrame(); kz.setFrameShape(QFrame.StyledPanel); h = QHBoxLayout(kz)
        self._kopf = QButtonGroup(self)
        self.mit_kopf, self.ohne_kopf = QRadioButton("Überschriftenzeile"), QRadioButton("Keine Überschriftenzeile")
        self._kopf.addButton(self.mit_kopf, 1); self._kopf.addButton(self.ohne_kopf, 0); self.ohne_kopf.setChecked(True)
        h.addWidget(self.mit_kopf); h.addWidget(self.ohne_kopf); h.addStretch(1)
        self.kopf_rahmen = kz
        v.addWidget(kz); v.addStretch(1)
        optionen = QPushButton("Option …"); optionen.setMinimumHeight(34); optionen.clicked.connect(self._optionen)
        fussleiste(self, v, optionen)
        self._aktualisieren()

    def _aktualisieren(self) -> None:
        """Felder gibt es erst, wenn die Absätze durch den Trenner geteilt sind; ohne Felder sind die weiteren Schlüssel und die
        Überschriftenzeile gesperrt (wie in der Vorlage)."""
        n = feldzahl(self.texte, self._trenner)
        for i, s in enumerate(self.schluessel):
            s.feld.setEnabled(i == 0 or n > 1)
            s.fuellen(n)
        self.kopf_rahmen.setEnabled(n > 1)
        if n <= 1:
            self.ohne_kopf.setChecked(True)

    def _optionen(self) -> None:
        d = SortierOptionenDialog(self, self._trenner, self._gross_klein, self._sprache)

        def fertig():
            self._trenner, self._gross_klein, self._sprache = d.trenner(), d.gross_klein.isChecked(), d.sprache.currentData()
            self._aktualisieren()
        zeige_unter(self, d, fertig)

    def werte(self) -> dict:
        return {"schluessel": [w for w in (s.wert() for s in self.schluessel) if w is not None], "trenner": self._trenner,
                "gross_klein": self._gross_klein, "sprache": self._sprache, "kopfzeile": self._kopf.checkedId() == 1}
