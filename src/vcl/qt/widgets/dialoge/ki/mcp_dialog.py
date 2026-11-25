"""Mcp dialog: aus ``vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QDialog, QLabel, QMessageBox
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, UmbruchSchalter
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_MCP


class McpDialog(QDialog):
    """Ein MCP-Server: Name, Startbefehl, ein/aus; „Testen“ startet ihn kurz und zeigt seine Werkzeuge."""

    def __init__(self, fenster, e: dict | None = None):
        super().__init__(fenster)
        self.setWindowTitle("KI-Werkzeug bearbeiten" if e else "KI-Werkzeug hinzufügen"); self.resize(*GROESSE_FENSTER_MCP)
        v = _spalte("standard", self)
        f = FormularGitter()
        self.name = zeilenfeld("frei", e["name"] if e else "", platzhalter="Name")
        self.befehl = zeilenfeld("frei", e["befehl"] if e else "")
        self.befehl.setPlaceholderText("Startbefehl, z. B. npx -y @modelcontextprotocol/server-filesystem ~/Dokumente")
        f.zeile("Name *", self.name); f.zeile("Befehl *", self.befehl)
        info = QLabel("Der Server läuft auf diesem Rechner und startet nur während einer Chat-Frage. Jeder Werkzeugaufruf der KI wird vorher erfragt.")
        info.setWordWrap(True); f.breit(info)
        self.an = UmbruchSchalter("Im KI-Chat verwenden"); self.an.setChecked(e["an"] if e else True)
        f.breit(self.an)
        self.stand = QLabel(""); self.stand.setWordWrap(True)
        t = knopf("standard", "Testen", aktion=self._testen)
        tz = FlussLayout(6); tz.addWidget(t); f.breit(tz)
        f.breit(self.stand)
        v.addLayout(f); v.addStretch(1)
        v.addWidget(knopfzeile(self, bei_ok=self._ok, ok_text="Speichern"))

    def _testen(self) -> None:
        from writer.funktionen import ki as M
        w, fehler = M.mcp_pruefen(self.befehl.text())
        if fehler:
            self.stand.setText(f"Nicht erreichbar: {fehler}")
        else:
            self.stand.setText(f"Verbunden — {len(w)} Werkzeug(e): " + ", ".join(w[:12]))

    def _ok(self) -> None:
        if not self.name.text().strip() or not self.befehl.text().strip():
            QMessageBox.information(self, "KI-Werkzeug", "Name und Befehl werden gebraucht.")
            return
        self.accept()

    def werte(self) -> tuple:
        return self.name.text(), self.befehl.text(), self.an.isChecked()
