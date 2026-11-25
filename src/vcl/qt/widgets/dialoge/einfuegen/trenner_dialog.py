"""Trenner dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QButtonGroup, QDialog, QLabel, QSpinBox
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from writer.anbindung import tabelle_text as TT
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_SCHIENE, HOEHE_KNOPF
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_fenster_hilfen import _titel


class TrennerDialog(PanelFaehig, QDialog):
    """„Text in Tabelle umwandeln“ (mit Spaltenzahl) oder „Tabelle in Text konvertieren“: woran getrennt wird."""

    def __init__(self, parent=None, *, zu_tabelle: bool = True, texte: list[str] | None = None):
        super().__init__(parent)
        self.zu_tabelle, self.texte = zu_tabelle, list(texte or [])
        self.setWindowTitle("Text in Tabelle umwandeln" if zu_tabelle else "Tabelle in Text konvertieren")
        v = _spalte("standard", self)
        fg = FormularGitter()                                                  # passt sich der Breite an (Seitenleiste)
        v.addLayout(fg)
        if zu_tabelle:
            self._spalten = QSpinBox(); self._spalten.setRange(1, 63); self._spalten.setMinimumHeight(HOEHE_KNOPF)
            self._zeilen = QLabel()
            fg.zeile(_titel("&Spaltenanzahl:", self._spalten), self._spalten)
            fg.zeile("Zeilenanzahl:", self._zeilen)
        t = QLabel("Text trennen bei"); f = t.font(); f.setBold(True); t.setFont(f)
        fg.breit(t)
        # Tabelle → Text wie in der Vorlage: Absätze, Tabstopps, Kommata, Andere (untereinander)
        self._liste = TT.trenner() if zu_tabelle else [("\n", "&Absätze"), ("\t", "&Tabstopps"), (",", "&Kommata")]
        self._gruppe = QButtonGroup(self)
        g = FlussLayout(14) if zu_tabelle else _spalte("standard")                   # Text → Tabelle: Reihe, die umbricht; Tabelle → Text: untereinander
        for i, (_z, text) in enumerate(self._liste):
            r = option("standard", text, gruppe=self._gruppe, nummer=i); g.addWidget(r)
        andere = option("standard", "A&ndere:", gruppe=self._gruppe, nummer=len(self._liste))
        self.andere = zeilenfeld("standard", "-"); self.andere.setMaxLength(1); self.andere.setMaximumWidth(BREITE_SCHIENE)
        self.andere.setAlignment(Qt.AlignCenter); self.andere.setAccessibleName("Anderes Trennzeichen")
        z = FlussLayout(6); z.addWidget(andere); z.addWidget(self.andere)
        fg.breit(g); fg.breit(z)
        if not zu_tabelle:
            self.geschachtelt = UmbruchSchalter("&Geschachtelte Tabellen umwandeln"); self.geschachtelt.setChecked(True)
            self.geschachtelt.setToolTip("Ohne Haken bleiben Tabellen in Zellen Tabellen und stehen hinter dem Text.")
            fg.breit(self.geschachtelt)
        self.andere.textEdited.connect(lambda _t: andere.setChecked(True))
        vorgabe = "\t" if any("\t" in s for s in self.texte) or not zu_tabelle else "\n"
        self._gruppe.button([k for k, _t in self._liste].index(vorgabe)).setChecked(True)
        self._gruppe.idToggled.connect(lambda _i, an: an and self._zaehlen())
        self.andere.textChanged.connect(lambda _t: self._zaehlen())
        v.addStretch(1)
        fussleiste(self, v)
        self._zaehlen()

    def trenner(self) -> str:
        i = self._gruppe.checkedId()
        return self._liste[i][0] if i < len(self._liste) else (self.andere.text() or "-")

    def spalten(self) -> int | None:
        return self._spalten.value() if self.zu_tabelle else None

    def _zaehlen(self) -> None:
        if not self.zu_tabelle:
            return
        z = TT.zellen(self.texte, self.trenner())
        self._spalten.setValue(max((len(r) for r in z), default=1))
        self._zeilen.setText(str(len(z)))
