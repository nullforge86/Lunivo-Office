"""Dokumente panel: aus ``vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.haken.haken import haken
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
import os
from PySide6.QtCore import QThreadPool, Signal
from PySide6.QtWidgets import QLabel, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from framework.ki.dienst import ki as K
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.interaktion.felder.listen_leiste import ListenLeiste
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_LISTE_KURZ
from vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels_hilfen import _NetzLauf, _NetzSender


class DokumentePanel(QWidget):
    werkzeug_eingetragen = Signal()                  # die Dokumentensuche steht jetzt in der Liste „KI-Werkzeuge“

    """Lokale Dokumentensuche für den KI-Chat: freigegebene Ordner, Zahl der Abschnitte, Index aufbauen. Der Text bleibt auf dem Rechner, solange das
    Chat-Modell lokal ist; bei einem Online-Modell fragt der Chat vorher nach der Zustimmung für Auszüge."""

    def __init__(self, konfig: K.KIKonfig):
        super().__init__()
        from PySide6.QtWidgets import QCheckBox, QSpinBox
        from framework.ki.suche import dokumentensuche as DS
        from vcl.qt.widgets.dialoge.dokument.speichern_fenster import Dateifenster
        self.k, self._DS, self._Dateifenster = konfig, DS, Dateifenster
        o = konfig.dokumentsuche_optionen()
        v = _spalte("oben", self)
        self.an = haken("standard", "Eigene Dokumente im KI-Chat durchsuchen", an=bool(o["an"]))
        v.addWidget(self.an)
        h = QLabel("Lunivo liest nur die Ordner, die Sie hier freigeben (DOCX, ODT, RTF, TXT und PDF mit Text), und legt einen Suchindex auf diesem "
                   "Rechner an. Zur Frage im Chat werden die passenden Abschnitte der KI als Quelle mitgegeben; unter der Antwort stehen die Fundstellen.")
        h.setWordWrap(True); hinweis_stil(h)
        v.addWidget(h)
        self.leiste = ListenLeiste("Ordner freigeben", HOEHE_LISTE_KURZ)
        self.leiste.bearb.hide()
        self.liste = self.leiste.liste
        for p in o["ordner"]:
            self.liste.addItem(p)
        self.leiste.neu_angefordert.connect(self._neu)
        self.leiste.entfernen_angefordert.connect(self._weg)
        self.leiste.knoepfe_pruefen()
        v.addWidget(self.leiste)
        f = FormularGitter()
        self.anzahl = QSpinBox(); self.anzahl.setRange(1, 10); self.anzahl.setValue(int(o["anzahl"]))
        f.zeile("Abschnitte je Frage", self.anzahl)
        v.addLayout(f)
        self.los = knopf("standard", "Jetzt indexieren", aktion=self._indexieren)
        self.werkzeug = knopf("standard", "Als KI-Werkzeug eintragen", aktion=self._werkzeug_eintragen)
        self.werkzeug.setToolTip("Macht die Suche als MCP-Server für den KI-Chat verfügbar (Ollama und eigene Anbieter). Jeder Aufruf wird einzeln abgefragt.")
        self.stand = QLabel(""); self.stand.setWordWrap(True)
        fl = FlussLayout(); fl.addWidget(self.los); fl.addWidget(self.werkzeug); v.addLayout(fl)
        v.addWidget(self.stand); v.addStretch(1)
        self._sender = _NetzSender(); self._sender.fertig.connect(self._fertig)
        self._pool = QThreadPool(self)
        self._stand_zeigen()

    def ordner(self) -> list[str]:
        return [self.liste.item(i).text() for i in range(self.liste.count())]

    def _stand_zeigen(self) -> None:
        d, a = self._DS.Index(self.k.dokumentindex_pfad()).anzahl()
        self.stand.setText(f"Im Index: {d} Dateien, {a} Abschnitte." if d else "Der Index ist noch leer.")

    def _neu(self) -> None:
        p = self._Dateifenster.getExistingDirectory(self, "Ordner freigeben", os.path.expanduser("~"))
        if p and p not in self.ordner():
            self.liste.addItem(os.path.abspath(p))
            self.leiste.knoepfe_pruefen()

    def _weg(self) -> None:
        r = self.liste.currentRow()
        if r >= 0:
            self.liste.takeItem(r)
            self.leiste.knoepfe_pruefen()

    def _indexieren(self) -> None:
        ordner = self.ordner()
        self.los.setEnabled(False); self.stand.setText("Die Dokumente werden gelesen … Das kann etwas dauern.")
        pfad = self.k.dokumentindex_pfad()
        self._pool.start(_NetzLauf(self._sender, lambda: {"bericht": self._DS.Index(pfad).aktualisieren(ordner)}))

    def _fertig(self, b: dict) -> None:
        self.los.setEnabled(True)
        if "fehler" in b:
            self.stand.setText(f"Das hat nicht geklappt: {b['fehler']}")
            return
        b = b["bericht"]
        self._stand_zeigen()
        self.stand.setText(self.stand.text() + f" Neu: {b['neu']}, geändert: {b['geaendert']}, entfernt: {b['entfernt']}"
                           + (f", nicht lesbar: {b['fehler']}" if b["fehler"] else "") + ".")

    def _werkzeug_eintragen(self) -> None:
        self.uebernehmen()
        if not self.ordner():
            self.stand.setText("Zuerst mindestens einen Ordner freigeben.")
            return
        self.k.suchdienst_eintragen()
        self.werkzeug_eingetragen.emit()
        self.stand.setText("Eingetragen unter „KI-Werkzeuge“. Nach Änderungen der Ordner bitte erneut auf den Knopf drücken.")

    def uebernehmen(self) -> None:
        self.k.dokumentsuche_setzen(an=self.an.isChecked(), ordner=self.ordner(), anzahl=self.anzahl.value())
