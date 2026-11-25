"""Piktogramm dialog: aus ``vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.farben.farben import VORGABE_SCHRIFT
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_AUSWAHL, GROESSE_RASTER_SYMBOLE, ICON_VORSCHAU
from vcl.qt.widgets.bausteine.zustaende.geruest.zusatz_panel import PanelFaehig
from vcl.qt.widgets.dialoge.einfuegen.einfuegen_dialoge_hilfen import _Farbknopf, _ok


class PiktogrammDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Piktogramm einfügen")
        self.resize(*GROESSE_FENSTER_AUSWAHL)
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        v = _spalte("standard", self)
        self.suche = zeilenfeld("frei", platzhalter="Suchen (englische Symbolnamen, z. B. heart, home, star)")
        v.addWidget(self.suche)
        self.liste = QListWidget(); self.liste.setViewMode(QListWidget.IconMode); self.liste.setIconSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(ICON_VORSCHAU, ICON_VORSCHAU))
        self.liste.setResizeMode(QListWidget.Adjust); self.liste.setGridSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(*GROESSE_RASTER_SYMBOLE))
        self.liste.setUniformItemSizes(True); self.liste.itemDoubleClicked.connect(lambda _: self.accept())
        v.addWidget(self.liste)
        self.farbe = _Farbknopf(VORGABE_SCHRIFT)
        fg = FormularGitter(); fg.zeile("Farbe:", self.farbe); v.addLayout(fg)
        v.addWidget(_ok(self))
        self.namen = sorted(symbole.katalog())
        self.suche.textChanged.connect(self._fuellen)
        self.farbe.clicked.connect(lambda: self._fuellen(self.suche.text()))
        self._fuellen("")

    def _fuellen(self, q):
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        self.liste.clear()
        q = (q or "").lower().strip()
        for n in self.namen:
            if q and q not in n.lower():
                continue
            if self.liste.count() >= 240:
                break
            from PySide6.QtGui import QIcon
            it = QListWidgetItem(QIcon(QPixmap.fromImage(symbole.katalog_bild(n, 40, self.farbe.farbe))), n)
            it.setData(Qt.UserRole, n)
            self.liste.addItem(it)

    def ergebnis(self):
        it = self.liste.currentItem()
        return (it.data(Qt.UserRole), self.farbe.farbe) if it else (None, None)


class PiktogrammDialog(PanelFaehig, QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Piktogramm einfügen")
        self.resize(*GROESSE_FENSTER_AUSWAHL)
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        v = _spalte("standard", self)
        self.suche = zeilenfeld("frei", platzhalter="Suchen (englische Symbolnamen, z. B. heart, home, star)")
        v.addWidget(self.suche)
        self.liste = QListWidget(); self.liste.setViewMode(QListWidget.IconMode); self.liste.setIconSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(ICON_VORSCHAU, ICON_VORSCHAU))
        self.liste.setResizeMode(QListWidget.Adjust); self.liste.setGridSize(__import__("PySide6.QtCore", fromlist=["QSize"]).QSize(*GROESSE_RASTER_SYMBOLE))
        self.liste.setUniformItemSizes(True); self.liste.itemDoubleClicked.connect(lambda _: self.accept())
        v.addWidget(self.liste)
        self.farbe = _Farbknopf(VORGABE_SCHRIFT)
        fg = FormularGitter(); fg.zeile("Farbe:", self.farbe); v.addLayout(fg)
        v.addWidget(_ok(self))
        self.namen = sorted(symbole.katalog())
        self.suche.textChanged.connect(self._fuellen)
        self.farbe.clicked.connect(lambda: self._fuellen(self.suche.text()))
        self._fuellen("")

    def _fuellen(self, q):
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        self.liste.clear()
        q = (q or "").lower().strip()
        for n in self.namen:
            if q and q not in n.lower():
                continue
            if self.liste.count() >= 240:
                break
            from PySide6.QtGui import QIcon
            it = QListWidgetItem(QIcon(QPixmap.fromImage(symbole.katalog_bild(n, 40, self.farbe.farbe))), n)
            it.setData(Qt.UserRole, n)
            self.liste.addItem(it)

    def ergebnis(self):
        it = self.liste.currentItem()
        return (it.data(Qt.UserRole), self.farbe.farbe) if it else (None, None)
