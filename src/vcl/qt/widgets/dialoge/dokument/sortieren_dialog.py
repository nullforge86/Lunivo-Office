"""Das Fenster „Text sortieren“ als Baustein (Start ▸ Absatz ▸ Sortieren): ein Hauptschlüssel und bis zu zwei weitere („Anschließend nach“),
je mit Typ (Text, Zahl, Datum) und Richtung; „Meine Liste enthält“ eine Überschriftenzeile oder nicht. „Option …“ öffnet die Sortieroptionen
(Feldtrenner, Groß-/Kleinschreibung, Sortiersprache) als Unterfenster.

    d = SortierenDialog(parent, texte)        # texte: die zu sortierenden Absätze — daraus ergibt sich die Zahl der Felder
    if ausfuehren(d): d.werte()               # {"schluessel": [(feld|None, typ, absteigend), …], "trenner", "gross_klein", "sprache", "kopfzeile"}

Das Fenster sortiert nicht selbst; der Aufrufer ruft ``editor.text.schreibweise.reihenfolge`` mit ``**d.werte()`` auf (``Befehle.sortieren``).
"""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.bausteine.rahmen.rahmen.rahmen import rahmen as rahmen_baustein

from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import reihe as _reihe, spalte as _spalte

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QComboBox, QDialog, QFrame, QLabel, QLineEdit, QPushButton, QRadioButton, QWidget

from core.formatierung.schrift.schreibweise import SPRACHEN, feldzahl
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter, abschnittstitel
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_SCHIENE, HOEHE_KNOPF, RAND_BOX_KOMPAKT
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld

TYPEN = (("text", "Text"), ("zahl", "Zahl"), ("datum", "Datum"))
TRENNER = (("\t", "Tabstopps"), (",", "Kommata"))


def _feld(w: QWidget, breite: int = 0) -> QWidget:
    """Feldhöhe wie überall; ``breite`` nur für kleine Felder (ein Zeichen), sonst richtet sich das Feld nach dem Gitter."""
    if not isinstance(w, QComboBox):                        # Dropdowns bekommen ihre Höhe vom Baustein (DROPDOWN_HOEHE)
        w.setMinimumHeight(HOEHE_KNOPF)
    if breite:
        w.setMinimumWidth(breite)
    return w


class SortierOptionenDialog(PanelFaehig, QDialog):
    def __init__(self, parent=None, trenner: str = "\t", gross_klein: bool = False, sprache: str = "de_DE", nur_spalte: bool = False):
        super().__init__(parent)
        self.setWindowTitle("Sortieroptionen")
        v = _spalte("standard", self)
        v.addWidget(abschnittstitel("Felder trennen bei"))
        self._trenner = QButtonGroup(self)
        for i, (_z, t) in enumerate(TRENNER):
            r = option("standard", t, gruppe=self._trenner, nummer=i); v.addWidget(r)
        z = FlussLayout(8); r = option("standard", "Andere:", gruppe=self._trenner, nummer=len(TRENNER)); z.addWidget(r)
        self.andere = _feld(zeilenfeld("frei", "-"), 44); self.andere.setMaximumWidth(BREITE_SCHIENE); self.andere.setMaxLength(1); self.andere.setAlignment(Qt.AlignCenter)
        z.addWidget(self.andere); v.addLayout(z)
        bekannt = [k for k, _t in TRENNER]
        if trenner in bekannt:
            self._trenner.button(bekannt.index(trenner)).setChecked(True)
        else:
            r.setChecked(True); self.andere.setText(trenner or "-")
        self.andere.textEdited.connect(lambda _t: r.setChecked(True))
        v.addWidget(abschnittstitel("Sortieroptionen"))
        self.nur_spalte = UmbruchSchalter("Nur Spalte sortieren"); self.nur_spalte.setChecked(nur_spalte); self.nur_spalte.setEnabled(False)
        self.gross_klein = UmbruchSchalter("Groß-/Kleinschreibung beachten"); self.gross_klein.setChecked(gross_klein)
        v.addWidget(self.nur_spalte); v.addWidget(self.gross_klein)
        v.addWidget(abschnittstitel("Sortiersprache"))
        self.sprache = _feld(Auswahlfeld())
        for k, t in SPRACHEN:
            self.sprache.addItem(t, k)
        self.sprache.setCurrentIndex(max(0, self.sprache.findData(sprache)))
        v.addWidget(self.sprache); v.addStretch(1)
        fussleiste(self, v)

    def trenner(self) -> str:
        i = self._trenner.checkedId()
        return TRENNER[i][0] if i < len(TRENNER) else (self.andere.text() or "-")


class _Schluessel:
    """Ein Schlüssel „nach … Typ … Aufsteigend/Absteigend“ im ``FormularGitter`` ``g``: Feld über die Breite, darunter Typ, dann die Richtung."""

    def __init__(self, g: FormularGitter, eltern: QDialog, mit_keine: bool):
        self.mit_keine = mit_keine
        self.feld = _feld(Auswahlfeld())
        self.typ_text = QLabel("Typ:")
        self.typ = _feld(Auswahlfeld())
        for k, t in TYPEN:
            self.typ.addItem(t, k)
        self.ordnung = QButtonGroup(eltern)
        self.auf, self.ab = option("standard", "Aufsteigend"), option("standard", "Absteigend")
        self.ordnung.addButton(self.auf, 0); self.ordnung.addButton(self.ab, 1); self.auf.setChecked(True)
        g.breit(self.feld); g.zeile(self.typ_text, self.typ)
        richtung = FlussLayout(14); richtung.addWidget(self.auf); richtung.addWidget(self.ab); g.breit(richtung)
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
        v = _spalte("standard", self)
        seite = QWidget(); g = FormularGitter(seite)
        self.schluessel: list[_Schluessel] = []
        for n, titel in enumerate(("Sortieren nach", "Anschließend nach", "Anschließend nach")):
            g.breit(abschnittstitel(titel))
            self.schluessel.append(_Schluessel(g, self, mit_keine=n > 0))
        g.breit(abschnittstitel("Meine Liste enthält"))
        kz = rahmen_baustein("panel"); h = FlussLayout(14); h.setContentsMargins(*RAND_BOX_KOMPAKT); kz.setLayout(h)
        self._kopf = QButtonGroup(self)
        self.mit_kopf, self.ohne_kopf = option("standard", "Überschriftenzeile"), option("standard", "Keine Überschriftenzeile")
        self._kopf.addButton(self.mit_kopf, 1); self._kopf.addButton(self.ohne_kopf, 0); self.ohne_kopf.setChecked(True)
        h.addWidget(self.mit_kopf); h.addWidget(self.ohne_kopf)
        self.kopf_rahmen = kz
        g.breit(kz)
        v.addWidget(seite); v.addStretch(1)
        optionen = knopf("klein", "Option …", aktion=self._optionen)
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
