"""Websuche panel: aus ``vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QWidget
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from framework.ki.dienst import ki as K
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter


class WebsuchePanel(QWidget):
    """Websuche für den KI-Chat: Anbieter, Adresse oder Schlüssel, Zahl der Treffer. Ein: die Frage geht an den Suchanbieter."""

    def __init__(self, konfig: K.KIKonfig):
        super().__init__()
        from PySide6.QtWidgets import QCheckBox, QSpinBox
        from framework.ki.suche import websuche as W
        self.k = konfig
        o = konfig.websuche_optionen()
        v = _spalte("oben", self)
        self.an = haken("standard", "Websuche im KI-Chat verwenden", an=bool(o["an"]))
        v.addWidget(self.an)
        h = QLabel("Ist die Websuche an, geht Ihre Frage an den Suchanbieter (bei einer SearXNG-Instanz auf diesem Rechner bleibt sie hier). "
                   "Die Treffer werden der KI als Quellen mitgegeben.")
        h.setWordWrap(True); hinweis_stil(h)
        v.addWidget(h)
        f = FormularGitter()
        self.anbieter = Auswahlfeld()
        for schl, name in W.ANBIETER:
            self.anbieter.addItem(name, schl)
        self.anbieter.setCurrentIndex(max(0, self.anbieter.findData(o["anbieter"])))
        self.url = zeilenfeld("frei", o["url"], platzhalter="https://searx.example.org")
        self.schluessel = zeilenfeld("frei", o["schluessel"], passwort=True)
        self.anzahl = QSpinBox(); self.anzahl.setRange(1, 10); self.anzahl.setValue(int(o["anzahl"]))
        f.zeile("Anbieter", self.anbieter); f.zeile("Adresse (SearXNG)", self.url); f.zeile("API-Schlüssel (Brave)", self.schluessel)
        f.zeile("Treffer", self.anzahl)
        v.addLayout(f)
        t = knopf("standard", "Testen", aktion=self._testen)
        self.stand = QLabel(""); self.stand.setWordWrap(True)
        v.addWidget(t, 0, Qt.AlignLeft); v.addWidget(self.stand); v.addStretch(1)

    def werte(self) -> dict:
        return {"an": self.an.isChecked(), "anbieter": self.anbieter.currentData(), "url": self.url.text().strip(),
                "schluessel": self.schluessel.text().strip(), "anzahl": self.anzahl.value()}

    def _testen(self) -> None:
        from framework.ki.suche import websuche as W
        try:
            t = W.suche(self.werte(), "Lunivo Writer")
            self.stand.setText(f"Verbunden — {len(t)} Treffer.")
        except (OSError, ValueError) as e:
            self.stand.setText(f"Nicht erreichbar: {getattr(e, 'reason', e)}")

    def uebernehmen(self) -> None:
        self.k.websuche_setzen(**self.werte())
