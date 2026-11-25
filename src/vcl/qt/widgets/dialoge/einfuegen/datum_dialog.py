"""Datum dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QListWidget, QListWidgetItem
from vcl.qt.rendering.formen import einfuegen as E
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig


class DatumDialog(PanelFaehig, QDialog):
    """Wie die Vorlage: links „Verfügbare Formate“, rechts „Sprache“, darunter „Automatisch aktualisieren“ (dann als Datumsfeld)."""

    def __init__(self, parent, sprache: str = "de_DE"):
        super().__init__(parent)
        from PySide6.QtWidgets import QCheckBox
        from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
        self.setWindowTitle("Datum und Uhrzeit")
        v = _spalte("standard", self)
        g = FormularGitter(); v.addLayout(g)
        self.liste = QListWidget(); self.liste.setAccessibleName("Verfügbare Formate")
        self.sprache = Auswahlfeld(); self.sprache.setAccessibleName("Sprache")
        for k, (t, _f) in E.DATUM_SPRACHEN.items():
            self.sprache.addItem(t, k)
        self.sprache.setCurrentIndex(max(0, self.sprache.findData(sprache)))
        self.auto = haken("standard", "&Automatisch aktualisieren")
        self.auto.setToolTip("Das Datum wird als Feld gespeichert; Textprogramme rechnen es beim Öffnen neu (in DOCX).")
        t1 = QLabel("&Verfügbare Formate:"); t1.setBuddy(self.liste)
        t2 = QLabel("&Sprache:"); t2.setBuddy(self.sprache)
        g.zeile(t1, self.liste)
        g.zeile(t2, self.sprache)
        g.breit(self.auto)
        fussleiste(self, v)
        self.sprache.currentIndexChanged.connect(self._fuellen)
        self.liste.itemDoubleClicked.connect(lambda _: self.accept())
        self._fuellen()

    def _loc(self) -> str:
        return self.sprache.currentData()

    def _fuellen(self, *_):
        self.liste.clear()
        for fmt in E.DATUM_SPRACHEN[self._loc()][1]:
            it = QListWidgetItem(E.datum_text(fmt, self._loc())); it.setData(Qt.UserRole, fmt); self.liste.addItem(it)
        self.liste.setCurrentRow(0)

    def ergebnis(self) -> str:
        it = self.liste.currentItem()
        return it.text() if it else ""

    def feldanweisung(self) -> str | None:
        """Bei „Automatisch aktualisieren“ die Feldanweisung (DATE/TIME), sonst None."""
        it = self.liste.currentItem()
        return E.datum_feldanweisung(it.data(Qt.UserRole)) if it and self.auto.isChecked() else None


class DatumDialog(PanelFaehig, QDialog):
    """Wie die Vorlage: links „Verfügbare Formate“, rechts „Sprache“, darunter „Automatisch aktualisieren“ (dann als Datumsfeld)."""

    def __init__(self, parent, sprache: str = "de_DE"):
        super().__init__(parent)
        from PySide6.QtWidgets import QCheckBox
        from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import fussleiste
        self.setWindowTitle("Datum und Uhrzeit")
        v = _spalte("standard", self)
        g = FormularGitter(); v.addLayout(g)
        self.liste = QListWidget(); self.liste.setAccessibleName("Verfügbare Formate")
        self.sprache = Auswahlfeld(); self.sprache.setAccessibleName("Sprache")
        for k, (t, _f) in E.DATUM_SPRACHEN.items():
            self.sprache.addItem(t, k)
        self.sprache.setCurrentIndex(max(0, self.sprache.findData(sprache)))
        self.auto = haken("standard", "&Automatisch aktualisieren")
        self.auto.setToolTip("Das Datum wird als Feld gespeichert; Textprogramme rechnen es beim Öffnen neu (in DOCX).")
        t1 = QLabel("&Verfügbare Formate:"); t1.setBuddy(self.liste)
        t2 = QLabel("&Sprache:"); t2.setBuddy(self.sprache)
        g.zeile(t1, self.liste)
        g.zeile(t2, self.sprache)
        g.breit(self.auto)
        fussleiste(self, v)
        self.sprache.currentIndexChanged.connect(self._fuellen)
        self.liste.itemDoubleClicked.connect(lambda _: self.accept())
        self._fuellen()

    def _loc(self) -> str:
        return self.sprache.currentData()

    def _fuellen(self, *_):
        self.liste.clear()
        for fmt in E.DATUM_SPRACHEN[self._loc()][1]:
            it = QListWidgetItem(E.datum_text(fmt, self._loc())); it.setData(Qt.UserRole, fmt); self.liste.addItem(it)
        self.liste.setCurrentRow(0)

    def ergebnis(self) -> str:
        it = self.liste.currentItem()
        return it.text() if it else ""

    def feldanweisung(self) -> str | None:
        """Bei „Automatisch aktualisieren“ die Feldanweisung (DATE/TIME), sonst None."""
        it = self.liste.currentItem()
        return E.datum_feldanweisung(it.data(Qt.UserRole)) if it and self.auto.isChecked() else None
