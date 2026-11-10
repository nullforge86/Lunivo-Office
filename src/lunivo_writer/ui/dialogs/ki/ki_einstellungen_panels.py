"""KI-Einstellungen, Seiten (Panels): Offline-Sprachen, Sprache, MCP-Werkzeuge, Datenschutz, Websuche, Dokumentensuche.

Die Seiten setzt ``KIEinstellungenDialog`` (ki_dialoge.py) zusammen."""
from __future__ import annotations

import os

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtWidgets import (
    QSizePolicy, QDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld

from lunivo_writer.ui.baukasten.basis.texte import hinweis_stil
from lunivo_writer.ai import ki as K
from lunivo_writer.ui.baukasten.geruest.fenster_stapel import zeige_unter
from lunivo_writer.ui.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.ui.baukasten.controls.formular_gitter import FlussLayout, FormularGitter, UmbruchSchalter, abschnittstitel


from lunivo_writer.ui.baukasten.controls.auswahl_liste import AuswahlListe
from lunivo_writer.ui.baukasten.basis.karte import als_karte
from lunivo_writer.ui.baukasten.controls.listen_leiste import ListenLeiste
from lunivo_writer.ui.baukasten.basis.mass import (
    GROESSE_FENSTER_MCP,
    HOEHE_BEREICH_MITTEL,
    HOEHE_KNOPF_GROSS,
    HOEHE_LISTE_KURZ,
    RAND_KEIN,
    RAND_OBEN_SEITE,
)


class _NetzLauf(QRunnable):
    """Ein Netzaufruf der Sprachpakete im Hintergrund; das Ergebnis kommt als Signal zurück."""

    def __init__(self, sender, funktion, *args):
        super().__init__()
        self.sender, self.funktion, self.args = sender, funktion, args

    def run(self) -> None:
        try:
            erg = self.funktion(*self.args)
        except Exception as e:                     # nie den Thread mit Ausnahme beenden
            erg = {"fehler": str(e)}
        try:
            self.sender.fertig.emit(erg)
        except RuntimeError:                       # Fenster schon geschlossen
            pass


class _NetzSender(QObject):
    fertig = Signal(object)


class OfflineSprachen(QWidget):
    """„Offline-Sprachen“: installierte Richtungen der lokalen Übersetzung und das Nachladen weiterer Sprachpakete (nur auf Klick, im Hintergrund)."""

    def __init__(self):
        super().__init__()
        self._pool = QThreadPool(self)
        self._sender = _NetzSender(self)
        self._sender.fertig.connect(self._ergebnis)
        self._modus = ""
        self._ziel: tuple[str, str] | None = None
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_KEIN)
        self.installiert = QLabel(); self.installiert.setWordWrap(True)
        v.addWidget(self.installiert)
        self.laden = QPushButton("Weitere Sprachen laden …"); self.laden.setMinimumHeight(HOEHE_KNOPF_GROSS)
        self.laden.clicked.connect(self._verfuegbare_holen)
        fl = FlussLayout(6); fl.addWidget(self.laden); v.addLayout(fl)
        self.stand = QLabel(); self.stand.setWordWrap(True); hinweis_stil(self.stand); v.addWidget(self.stand)
        self.auswahl = QWidget(); self._av = QVBoxLayout(self.auswahl); self._av.setContentsMargins(*RAND_KEIN)
        self.auswahl.setVisible(False)
        v.addWidget(self.auswahl)
        self.aktualisieren()

    def aktualisieren(self) -> None:
        from lunivo_writer.ai import argos
        r = argos.installierte_richtungen()                       # lokal, kein Netz
        self.installiert.setText("Installiert: " + ", ".join(x["name"] for x in r) if r else
                                 "Keine Sprachpakete gefunden. Deutsch ↔ Englisch gehört zum Programm; weitere Sprachen laden Sie bei Bedarf.")

    def _sperren(self, an: bool) -> None:
        self.laden.setEnabled(not an)
        for b in self.auswahl.findChildren(QPushButton):
            b.setEnabled(not an)

    def _verfuegbare_holen(self) -> None:
        from lunivo_writer.ai import argos
        self._modus = "liste"; self._sperren(True)
        self.stand.setText("Verfügbare Sprachen werden aus dem Internet abgefragt …")
        self._pool.start(_NetzLauf(self._sender, argos.verfuegbare_richtungen))

    def _herunterladen(self, von: str, nach: str, name: str, mb) -> None:
        gr = f" (ca. {mb} MB)" if mb else ""
        if QMessageBox.question(self, "Sprachpaket laden", f"„{name}“{gr} jetzt aus dem Internet herunterladen und installieren?") != QMessageBox.Yes:
            return
        from lunivo_writer.ai import argos
        self._modus = "paket"; self._ziel = (von, nach); self._sperren(True)
        self.stand.setText(f"„{name}“ wird geladen und installiert … Das kann etwas dauern.")
        self._pool.start(_NetzLauf(self._sender, argos.richtung_installieren, von, nach))

    def _ergebnis(self, erg: dict) -> None:
        self._sperren(False)
        if erg.get("fehler"):
            self.stand.setText(erg["fehler"])
            return
        if self._modus == "paket":
            self.stand.setText(f"Fertig: „{erg.get('name', '')}“ ist jetzt offline verfügbar.")
            self.aktualisieren()
            self._ziel = None
            self._verfuegbare_holen()                            # Liste ohne das neue Paket
            return
        while self._av.count():
            w = self._av.takeAt(0).widget()
            if w is not None:
                w.setParent(None); w.deleteLater()
        liste = erg.get("richtungen", [])
        self.stand.setText("Wählen Sie eine Sprache zum Herunterladen." if liste else "Es gibt keine weiteren Sprachpakete.")
        for r in liste:
            mb = r.get("groesse_mb")
            b = QPushButton(f"{r['name']}" + (f" · {mb} MB" if mb else "") + "  –  Herunterladen")
            b.setMinimumHeight(HOEHE_KNOPF_GROSS); b.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            b.clicked.connect(lambda _=False, r=r: self._herunterladen(r["von"], r["nach"], r["name"], r.get("groesse_mb")))
            self._av.addWidget(b)
        self.auswahl.setVisible(bool(liste))


class SprachePanel(QWidget):
    """Die Sprachen der Schreibhilfe, nebeneinander: „Sprache für die Überprüfung“ (Sprache des Dokuments) und „Übersetzen nach“ (Ziel der KI-Übersetzung).
    Das Modell für die Übersetzung steht in der Modellzuweisung."""

    def __init__(self, fenster):
        super().__init__()
        self.fenster = fenster
        b = fenster.befehle
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_OBEN_SEITE)
        g = FormularGitter(); v.addLayout(g); v.addStretch(1)
        self.pruefung = AuswahlListe(list(b.SPRACHEN))
        self.pruefung.setCurrentIndex(max(0, self.pruefung.findData(b.pruefsprache_aktuell())))
        self.pruefung.setEnabled(fenster.current_tab() is not None)
        self.sprache = AuswahlListe([(n, n) for n in K.SPRACHEN])
        self.sprache.setCurrentText(fenster.ki.konfig["sprache"])
        for titel, unter, liste in (("Sprache für die Überprüfung", "Sprache des Dokuments — wird in der Datei vermerkt.", self.pruefung),
                                    ("Übersetzen nach", "Sprache für die KI-Übersetzung wählen.", self.sprache)):
            g.breit(abschnittstitel(titel))
            hint = QLabel(unter); hint.setWordWrap(True); hinweis_stil(hint); g.breit(hint)
            liste.setMinimumHeight(0); liste.setFixedHeight(HOEHE_BEREICH_MITTEL); liste.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            als_karte(liste, "liste_eng")
            g.breit(liste)
        h = QLabel("Die Schreibhilfe selbst prüft weiter auf Deutsch. Das Modell für die Übersetzung wählen Sie im Reiter „Modellzuweisung“ (Aufgabe „Übersetzung“).")
        h.setWordWrap(True); hinweis_stil(h)
        g.breit(h)
        g.breit(abschnittstitel("Offline-Sprachen"))
        u = QLabel("Für die lokale Übersetzung ohne Internet. Weitere Sprachen werden nur auf Ihren Wunsch heruntergeladen.")
        u.setWordWrap(True); hinweis_stil(u); g.breit(u)
        self.offline = OfflineSprachen(); g.breit(self.offline)

    def kompakt_machen(self) -> None:
        """Die zwei Listen stehen schon untereinander (je sechs sichtbare Zeilen, der Rest rollt); nichts mehr umzubauen."""

    def uebernehmen(self) -> None:
        if self.sprache.currentItem() is not None:
            self.fenster.ki.konfig.setze("sprache", self.sprache.currentText())
        if self.pruefung.isEnabled() and self.pruefung.currentData() and self.pruefung.currentData() != self.fenster.befehle.pruefsprache_aktuell():
            self.fenster.befehle.pruefsprache_setzen(self.pruefung.currentData())


class McpDialog(QDialog):
    """Ein MCP-Server: Name, Startbefehl, ein/aus; „Testen“ startet ihn kurz und zeigt seine Werkzeuge."""

    def __init__(self, fenster, e: dict | None = None):
        super().__init__(fenster)
        self.setWindowTitle("KI-Werkzeug bearbeiten" if e else "KI-Werkzeug hinzufügen"); self.resize(*GROESSE_FENSTER_MCP)
        v = QVBoxLayout(self)
        f = FormularGitter()
        self.name = QLineEdit(e["name"] if e else ""); self.name.setPlaceholderText("Name")
        self.befehl = QLineEdit(e["befehl"] if e else "")
        self.befehl.setPlaceholderText("Startbefehl, z. B. npx -y @modelcontextprotocol/server-filesystem ~/Dokumente")
        f.zeile("Name *", self.name); f.zeile("Befehl *", self.befehl)
        info = QLabel("Der Server läuft auf diesem Rechner und startet nur während einer Chat-Frage. Jeder Werkzeugaufruf der KI wird vorher erfragt.")
        info.setWordWrap(True); f.breit(info)
        self.an = UmbruchSchalter("Im KI-Chat verwenden"); self.an.setChecked(e["an"] if e else True)
        f.breit(self.an)
        self.stand = QLabel(""); self.stand.setWordWrap(True)
        t = QPushButton("Testen"); t.clicked.connect(self._testen)
        tz = FlussLayout(6); tz.addWidget(t); f.breit(tz)
        f.breit(self.stand)
        v.addLayout(f); v.addStretch(1)
        v.addWidget(knopfzeile(self, bei_ok=self._ok, ok_text="Speichern"))

    def _testen(self) -> None:
        from lunivo_writer.ai import mcp as M
        try:
            w = M.pruefen(self.befehl.text())
            self.stand.setText(f"Verbunden — {len(w)} Werkzeug(e): " + ", ".join(t["name"] for t in w[:12]))
        except M.McpFehler as e:
            self.stand.setText(f"Nicht erreichbar: {e}")

    def _ok(self) -> None:
        if not self.name.text().strip() or not self.befehl.text().strip():
            QMessageBox.information(self, "KI-Werkzeug", "Name und Befehl werden gebraucht.")
            return
        self.accept()

    def werte(self) -> tuple:
        return self.name.text(), self.befehl.text(), self.an.isChecked()


class McpListe(QWidget):
    """Die eingetragenen MCP-Server: hinzufügen, bearbeiten, entfernen."""

    def __init__(self, fenster, konfig: K.KIKonfig):
        super().__init__()
        self.fenster, self.k = fenster, konfig
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_OBEN_SEITE)
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


class EinwilligungenPanel(QWidget):
    """Wer darf welchen Text bekommen: die gespeicherten Einwilligungen, einzeln oder alle widerrufbar. Ohne Einwilligung wird nichts gesendet."""

    def __init__(self, konfig: K.KIKonfig):
        super().__init__()
        self.k = konfig
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_OBEN_SEITE)
        info = QLabel("Diese Dienste im Internet dürfen Text von Ihnen bekommen. Ohne Eintrag fragt Lunivo vor dem Senden und sendet bei „Nein“ nichts. "
                      "Modelle auf diesem Rechner (Ollama, lokale Adressen) brauchen keine Erlaubnis.")
        info.setWordWrap(True); v.addWidget(info)
        self.liste = QListWidget(); self.liste.setAccessibleName("Erteilte Einwilligungen"); v.addWidget(self.liste, 1)
        self.liste.setWordWrap(True); self.liste.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)          # lange Einträge brechen um statt zu rollen
        z = FlussLayout(6)
        self.widerruf = QPushButton("Widerrufen"); self.widerruf.setToolTip("Nimmt die ausgewählte Erlaubnis zurück")
        self.alle = QPushButton("Alle widerrufen")
        for b in (self.widerruf, self.alle):
            b.setMinimumHeight(HOEHE_KNOPF_GROSS); z.addWidget(b)
        v.addLayout(z)
        self.widerruf.clicked.connect(self._widerrufen); self.alle.clicked.connect(self._alle)
        self.liste.currentRowChanged.connect(self._knoepfe)
        self.fuellen()

    def fuellen(self) -> None:
        self.liste.clear()
        for e in self.k.einwilligungen():
            seit = f" — seit {e['seit']}" if e["seit"] else ""
            it = QListWidgetItem(f"{e['anbieter']}: darf {K.UMFAENGE[e['umfang']]} bekommen{seit}")
            it.setData(Qt.UserRole, (e["anbieter"], e["umfang"])); self.liste.addItem(it)
        if not self.liste.count():
            it = QListWidgetItem("Keine Einwilligung gespeichert — es wird nichts ohne Rückfrage gesendet."); it.setFlags(Qt.NoItemFlags); self.liste.addItem(it)
        else:
            self.liste.setCurrentRow(0)
        self._knoepfe()

    def _knoepfe(self, *_) -> None:
        self.widerruf.setEnabled(self.liste.currentItem() is not None and self.liste.currentItem().data(Qt.UserRole) is not None)
        self.alle.setEnabled(bool(self.k.einwilligungen()))

    def _widerrufen(self) -> None:
        d = self.liste.currentItem().data(Qt.UserRole) if self.liste.currentItem() else None
        if d:
            self.k.einwilligung_widerrufen(*d); self.fuellen()

    def _alle(self) -> None:
        if QMessageBox.question(self, "Alle widerrufen", "Alle gespeicherten Einwilligungen zurücknehmen?") == QMessageBox.Yes:
            self.k.einwilligung_widerrufen(); self.fuellen()


class WebsuchePanel(QWidget):
    """Websuche für den KI-Chat: Anbieter, Adresse oder Schlüssel, Zahl der Treffer. Ein: die Frage geht an den Suchanbieter."""

    def __init__(self, konfig: K.KIKonfig):
        super().__init__()
        from PySide6.QtWidgets import QCheckBox, QSpinBox
        from lunivo_writer.ai import websuche as W
        self.k = konfig
        o = konfig.websuche_optionen()
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_OBEN_SEITE)
        self.an = QCheckBox("Websuche im KI-Chat verwenden"); self.an.setChecked(bool(o["an"]))
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
        self.url = QLineEdit(o["url"]); self.url.setPlaceholderText("https://searx.example.org")
        self.schluessel = QLineEdit(o["schluessel"]); self.schluessel.setEchoMode(QLineEdit.Password)
        self.anzahl = QSpinBox(); self.anzahl.setRange(1, 10); self.anzahl.setValue(int(o["anzahl"]))
        f.zeile("Anbieter", self.anbieter); f.zeile("Adresse (SearXNG)", self.url); f.zeile("API-Schlüssel (Brave)", self.schluessel)
        f.zeile("Treffer", self.anzahl)
        v.addLayout(f)
        t = QPushButton("Testen"); t.clicked.connect(self._testen)
        self.stand = QLabel(""); self.stand.setWordWrap(True)
        v.addWidget(t, 0, Qt.AlignLeft); v.addWidget(self.stand); v.addStretch(1)

    def werte(self) -> dict:
        return {"an": self.an.isChecked(), "anbieter": self.anbieter.currentData(), "url": self.url.text().strip(),
                "schluessel": self.schluessel.text().strip(), "anzahl": self.anzahl.value()}

    def _testen(self) -> None:
        from lunivo_writer.ai import websuche as W
        try:
            t = W.suche(self.werte(), "Lunivo Writer")
            self.stand.setText(f"Verbunden — {len(t)} Treffer.")
        except (OSError, ValueError) as e:
            self.stand.setText(f"Nicht erreichbar: {getattr(e, 'reason', e)}")

    def uebernehmen(self) -> None:
        self.k.websuche_setzen(**self.werte())


class DokumentePanel(QWidget):
    werkzeug_eingetragen = Signal()                  # die Dokumentensuche steht jetzt in der Liste „KI-Werkzeuge“

    """Lokale Dokumentensuche für den KI-Chat: freigegebene Ordner, Zahl der Abschnitte, Index aufbauen. Der Text bleibt auf dem Rechner, solange das
    Chat-Modell lokal ist; bei einem Online-Modell fragt der Chat vorher nach der Zustimmung für Auszüge."""

    def __init__(self, konfig: K.KIKonfig):
        super().__init__()
        from PySide6.QtWidgets import QCheckBox, QSpinBox
        from lunivo_writer.ai import dokumentensuche as DS
        from lunivo_writer.ui.baukasten.dokument.speichern_fenster import Dateifenster
        self.k, self._DS, self._Dateifenster = konfig, DS, Dateifenster
        o = konfig.dokumentsuche_optionen()
        v = QVBoxLayout(self); v.setContentsMargins(*RAND_OBEN_SEITE)
        self.an = QCheckBox("Eigene Dokumente im KI-Chat durchsuchen"); self.an.setChecked(bool(o["an"]))
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
        self.los = QPushButton("Jetzt indexieren"); self.los.clicked.connect(self._indexieren)
        self.werkzeug = QPushButton("Als KI-Werkzeug eintragen"); self.werkzeug.clicked.connect(self._werkzeug_eintragen)
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
