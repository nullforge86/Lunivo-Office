"""Mcp liste: aus ``vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidgetItem, QMessageBox, QWidget
from writer.funktionen import ki as KD
from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.interaktion.felder.listen_leiste import ListenLeiste
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_LISTE_KURZ
from vcl.qt.widgets.dialoge.ki.mcp_dialog import McpDialog


class McpListe(QWidget):
    """Die eingetragenen MCP-Server: hinzufügen, bearbeiten, entfernen."""

    def __init__(self, fenster, konfig):
        super().__init__()
        self.fenster, self.k = fenster, konfig
        v = _spalte("oben", self)
        g = FormularGitter(); v.addLayout(g)
        info = QLabel("KI-Werkzeuge sind kleine Zusatzprogramme, die die KI im Chat benutzen darf (zum Beispiel Dateien lesen oder Daten abfragen). Fachbegriff: MCP-Server. Gilt für Ollama und eigene Anbieter.")
        info.setWordWrap(True); g.breit(info)
        self.leiste = ListenLeiste("Server hinzufügen", HOEHE_LISTE_KURZ); g.breit(self.leiste); v.addStretch(1)
        self.liste, self.neu, self.bearb, self.weg = self.leiste.liste, self.leiste.neu, self.leiste.bearb, self.leiste.weg
        self.leiste.neu_angefordert.connect(self._neu)
        self.leiste.bearbeiten_angefordert.connect(self._bearbeiten)
        self.leiste.entfernen_angefordert.connect(self._entfernen)
        self.fuellen()

    def fuellen(self) -> None:
        self.liste.clear()
        for m in self.k["mcp"]:
            it = QListWidgetItem(f"{m['name']}{'' if m['an'] else '  (aus)'}\n{m['befehl']}")
            it.setData(Qt.UserRole, m["id"]); self.liste.addItem(it)
        if self.liste.count():
            self.liste.setCurrentRow(0)
        self.leiste.knoepfe_pruefen()

    def _aktuell(self):
        it = self.liste.currentItem()
        return next((m for m in self.k["mcp"] if it and m["id"] == it.data(Qt.UserRole)), None)

    def _neu(self) -> None:
        d = McpDialog(self.fenster)
        zeige_unter(self, d, lambda: (self.k.mcp_speichern(None, *d.werte()), self.fuellen()))

    def _bearbeiten(self) -> None:
        m = self._aktuell()
        if m:
            d = McpDialog(self.fenster, m)
            zeige_unter(self, d, lambda: (self.k.mcp_speichern(m["id"], *d.werte()), self.fuellen()))

    def _entfernen(self) -> None:
        m = self._aktuell()
        if m and QMessageBox.question(self, "Entfernen", f"„{m['name']}“ aus der Liste entfernen?") == QMessageBox.Yes:
            self.k.mcp_entfernen(m["id"]); self.fuellen()
