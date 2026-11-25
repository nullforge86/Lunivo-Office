from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.interaktion.option.option import option
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem, QWidget
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
from writer.werkzeugleisten.plan import plan
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_LISTE_KNOEPFE, HOEHE_LISTE_REITER, ICON_GROSS
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.oberflaeche_dialoge_hilfen import _satz, lade_json


IMMER = ("Datei",)          # dieser Reiter lässt sich nicht ausblenden


class RegisterAnpassenDialog(PanelFaehig, QDialog):
    """Reiter ein-/ausblenden und umordnen — wie „Menüband anpassen“."""

    def __init__(self, parent, settings, daten: dict):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Register anpassen")
        v = _spalte("standard", self)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        g.breit(_satz("Haken = Reiter wird gezeigt. Mit den Pfeilen ändern Sie die Reihenfolge."))
        self.liste = QListWidget(); self.liste.setMinimumHeight(HOEHE_LISTE_REITER); self.liste.setAccessibleName("Reiter")
        g.breit(self.liste)
        namen = [r["name"] for r in plan(daten) if not r.get("kontext")]
        cfg = lade_json(settings, "ui/register_plan", {})
        reihenfolge = [n for n in cfg.get("reihenfolge", []) if n in namen] + [n for n in namen if n not in cfg.get("reihenfolge", [])]
        from vcl.qt.widgets.ribbon.band_leiste import STANDARD_VERSTECKT
        versteckt = set(cfg["versteckt"] if "versteckt" in cfg else STANDARD_VERSTECKT)
        for n in reihenfolge:
            it = QListWidgetItem(n)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Unchecked if n in versteckt else Qt.Checked)
            if n in IMMER:
                it.setFlags(it.flags() & ~Qt.ItemIsUserCheckable)
            self.liste.addItem(it)
        z = FlussLayout(6)
        for text, d in (("▲ Nach oben", -1), ("▼ Nach unten", 1)):
            z.addWidget(knopf("standard", text, aktion=lambda d=d: self._schieben(d)))
        g.breit(z)
        v.addWidget(inhalt)
        fussleiste(self, v, bei_ok=self._speichern)

    def _schieben(self, d: int):
        i = self.liste.currentRow(); j = i + d
        if i < 0 or not 0 <= j < self.liste.count():
            return
        it = self.liste.takeItem(i)
        self.liste.insertItem(j, it)
        self.liste.setCurrentRow(j)

    def _speichern(self):
        namen = [self.liste.item(i).text() for i in range(self.liste.count())]
        versteckt = [self.liste.item(i).text() for i in range(self.liste.count())
                     if self.liste.item(i).checkState() == Qt.Unchecked and self.liste.item(i).text() not in IMMER]
        self.settings.set("ui/register_plan", json.dumps({"reihenfolge": namen, "versteckt": versteckt}))
        self.accept()


class SchnellzugriffDialog(PanelFaehig, QDialog):
    """Welche Knöpfe in der Schnellzugriffsleiste neben dem ☰-Menü stehen."""

    def __init__(self, parent, settings, alle: list[tuple[str, str, str]], aktuell: list[str]):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Symbolleiste für den Schnellzugriff")
        v = _spalte("standard", self)
        v.addWidget(_satz("Haken = Knopf steht in der Schnellzugriffsleiste."))
        self.liste = QListWidget(); self.liste.setMinimumHeight(HOEHE_LISTE_KNOEPFE); self.liste.setAccessibleName("Knöpfe")
        v.addWidget(self.liste)
        for sym, name, aktion in alle:
            it = QListWidgetItem(symbole.icon(sym, ICON_GROSS), name)
            it.setData(Qt.UserRole, aktion)
            it.setFlags(it.flags() | Qt.ItemIsUserCheckable)
            it.setCheckState(Qt.Checked if aktion in aktuell else Qt.Unchecked)
            self.liste.addItem(it)
        fussleiste(self, v, bei_ok=self._speichern)

    def _speichern(self):
        gewaehlt = [self.liste.item(i).data(Qt.UserRole) for i in range(self.liste.count())
                    if self.liste.item(i).checkState() == Qt.Checked]
        self.settings.set("ui/schnellzugriff", json.dumps(gewaehlt))
        self.accept()


class OberflaecheDialog(PanelFaehig, QDialog):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.setWindowTitle("Benutzeroberfläche")
        v = _spalte("standard", self)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        g.breit(_satz("Wie sollen die Befehle angeordnet sein?"))
        self.reg = option("standard", "Register (Menüband mit Reitern)")
        self.sym = option("standard", "Symbolleisten (zwei Zeilen mit Knöpfen)")
        (self.sym if settings.get("ui/oberflaeche", "register") == "symbolleisten" else self.reg).setChecked(True)
        wahl = FlussLayout(6); wahl.addWidget(self.reg); wahl.addWidget(self.sym)
        g.breit(wahl)
        self.menue = UmbruchSchalter("Menüleiste zusätzlich anzeigen")
        self.menue.setChecked(settings.get_bool("ui/menueleiste", False))
        g.breit(self.menue)
        v.addWidget(inhalt)
        fussleiste(self, v)

    def wahl(self) -> str:
        return "symbolleisten" if self.sym.isChecked() else "register"
