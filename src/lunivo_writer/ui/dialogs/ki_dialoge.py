"""KI-Konfiguration: Aufgaben-Modellzuweisung, Liste der KI-Modelle, „Eigenen Anbieter hinzufügen“.

Der Anbieter wird hier festgelegt — in „KI-Konfiguration“ (Reiter Schreibhilfe/KI) oder in den Optionen.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtWidgets import (
    QSizePolicy, QComboBox, QDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QToolButton, QVBoxLayout, QWidget,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld

from lunivo_writer.ui.baukasten.texte import hinweis_stil
from lunivo_writer.ui.baukasten.beschriftung import text_label
from lunivo_writer.ai import ki as K
from lunivo_writer.ui.baukasten.fenster_stapel import zeige_unter
from lunivo_writer.ui.baukasten.dialog_rahmen import knopfzeile
from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig
from lunivo_writer.ui.baukasten.formular_gitter import FlussLayout, FormularGitter, UmbruchSchalter, abschnittstitel
from lunivo_writer.ui.widgets import icons


from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.flache_reiter_leiste import HAUPT, FlacheReiterLeiste
from lunivo_writer.ui.baukasten.auswahl_liste import AuswahlListe
from lunivo_writer.ui.baukasten.karte import als_karte
from lunivo_writer.ui.baukasten.listen_leiste import ListenLeiste
from lunivo_writer.ui.baukasten.mass import (
    BREITE_KNOPF_KLEIN,
    GROESSE_FENSTER_ANBIETER,
    GROESSE_FENSTER_KI,
    GROESSE_FENSTER_MCP,
    HOEHE_BEREICH_MITTEL,
    HOEHE_KNOPF_GROSS,
    HOEHE_LISTE_ANBIETER,
    HOEHE_LISTE_AUSWAHL,
    HOEHE_LISTE_KURZ,
    HOEHE_LISTE_MITTEL,
    HOEHE_LISTE_REITER,
    HOEHE_TEXT_NORMAL,
    ICON_NORMAL,
    RAND_KEIN,
    RAND_OBEN_SEITE,
)
from lunivo_writer.ui.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.ui.baukasten.mass import DROPDOWN_ZEICHEN_LANG
from lunivo_writer.ui.dialogs.ki_modelle_dialoge import (
    AnbieterDialog, KIKonfigurationDialog, ModellListe, ModellListeDialog,
    ModellZuweisung, _Antwort, _tags_text, modell_combo,
    modell_felder_fuellen, modell_passt,
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
    """Lokale Dokumentensuche für den KI-Chat: freigegebene Ordner, Zahl der Abschnitte, Index aufbauen. Der Text bleibt auf dem Rechner, solange das
    Chat-Modell lokal ist; bei einem Online-Modell fragt der Chat vorher nach der Zustimmung für Auszüge."""

    def __init__(self, konfig: K.KIKonfig):
        super().__init__()
        from PySide6.QtWidgets import QCheckBox, QSpinBox
        from lunivo_writer.ai import dokumentensuche as DS
        from lunivo_writer.ui.baukasten.speichern_fenster import Dateifenster
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
        self.stand = QLabel(""); self.stand.setWordWrap(True)
        v.addWidget(self.los, 0, Qt.AlignLeft); v.addWidget(self.stand); v.addStretch(1)
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

    def uebernehmen(self) -> None:
        self.k.dokumentsuche_setzen(an=self.an.isChecked(), ordner=self.ordner(), anzahl=self.anzahl.value())


REITER = ("KI-Modelle", "Modellzuweisung", "Sprache", "KI-Werkzeuge", "Websuche", "Datenschutz", "Assistenten", "Dokumente")


from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig
from lunivo_writer.ui.baukasten.vorlagen_chips import AufklappBereich
from lunivo_writer.ui.baukasten.erstellen_fenster import ErstellenFenster


class KIEinstellungenDialog(PanelFaehig, QDialog):
    """Das eine Fenster für alles zur KI: verbundene Modelle, Modellzuweisung, MCP-Server und Websuche.

    Dieselbe Konfiguration (``KIKonfig``) wie in der Seitenleiste der Schreibhilfe, im KI-Chat und in den Optionen. """

    def __init__(self, fenster, start: int = 0):
        super().__init__(fenster)
        from PySide6.QtWidgets import QStackedWidget, QTabBar
        self.fenster = fenster
        self.k = fenster.ki.konfig
        self.setWindowTitle("KI-Einstellungen")
        self.resize(*GROESSE_FENSTER_KI)
        v = QVBoxLayout(self)
        self.reiter = FlacheReiterLeiste(HAUPT)                  # der Baustein für flache Reiter: Beschriftung bricht um, nichts wird abgeschnitten
        for n in REITER:
            self.reiter.addTab(n)
        v.addWidget(self.reiter)
        self.stapel = QStackedWidget()
        v.addWidget(self.stapel, 1)
        # 1 KI-Modelle
        seite = QWidget(); sv = QVBoxLayout(seite); sv.setContentsMargins(*RAND_OBEN_SEITE)
        sv.addWidget(QLabel("Verbinden Sie Ihre eigene KI-Quelle — entweder über den API-Schlüssel eines Anbieters oder ein lokal gehostetes Modell."))
        self.liste = ModellListe(fenster, self.k)
        sv.addWidget(self.liste, 1)
        neu = QPushButton("Neues KI-Modell verbinden …"); neu.clicked.connect(self.neues_modell)
        sv.addWidget(neu, 0, Qt.AlignLeft)
        self.stapel.addWidget(seite)
        # 2 Modellzuweisung
        z = QWidget(); zv = QVBoxLayout(z); zv.setContentsMargins(*RAND_OBEN_SEITE)
        self.zuweisung = ModellZuweisung(fenster)
        zv.addWidget(self.zuweisung)
        from lunivo_writer.ui.baukasten.chat_regler import ChatReglerBlock
        self.chat_regler = ChatReglerBlock(self.k)                 # Länge, Temperatur, Top P, Stoppfolgen, direkt einfügen (zugeklappt)
        zv.addWidget(self.chat_regler)
        self.stapel.addWidget(z)
        # 3 Sprache, 4 MCP-Server, 5 Websuche
        self.sprache = SprachePanel(fenster)
        self.stapel.addWidget(self.sprache)
        self.mcp = McpListe(fenster, self.k)
        self.stapel.addWidget(self.mcp)
        self.websuche = WebsuchePanel(self.k)
        self.stapel.addWidget(self.websuche)
        self.datenschutz = EinwilligungenPanel(self.k)
        self.stapel.addWidget(self.datenschutz)
        from lunivo_writer.ui.baukasten.assistenten_liste import AssistentenListe
        seite = QWidget(); av = QVBoxLayout(seite); av.setContentsMargins(*RAND_OBEN_SEITE)
        self.assistenten = AssistentenListe(fenster)
        av.addWidget(self.assistenten); av.addStretch(1)
        self.stapel.addWidget(seite)
        self.dokumente = DokumentePanel(self.k)
        self.stapel.addWidget(self.dokumente)
        v.addWidget(knopfzeile(self, bei_ok=self._ok))
        self.reiter.currentChanged.connect(self.stapel.setCurrentIndex)
        self.freischalten()
        self.reiter.setCurrentIndex(start if self.reiter.isTabEnabled(start) else 0)

    def kompakt_machen(self) -> None:
        """In der Seitenleiste: kurze Reiternamen (die langen stehen im Tipp), damit alle fünf nebeneinander passen."""
        for i, (kurz, voll) in enumerate((("Modelle", "KI-Modelle"), ("Zuweisung", "Modellzuweisung"), ("Sprache", "Sprache"), ("Werkzeuge", "KI-Werkzeuge"),
                                          ("Websuche", "Websuche"), ("Daten", "Datenschutz"), ("Assistenten", "Assistenten"), ("Dokumente", "Dokumente"))):
            self.reiter.setTabText(i, kurz)
            if self.reiter.isTabEnabled(i):
                self.reiter.setTabToolTip(i, voll)
                self.reiter.setProperty("kompakt", True)                              # schmaler Innenabstand, damit alle Reiter in die Seitenleiste passen
        self.reiter.style().unpolish(self.reiter); self.reiter.style().polish(self.reiter)
        self.liste.setMinimumSize(0, 0)
        for l in self.stapel.widget(0).findChildren(QLabel):
            l.setWordWrap(True)
        self.sprache.kompakt_machen()

        def hoehe_der_seite(i: int) -> None:                                  # nur die gewählte Seite bestimmt die Höhe, die anderen zählen nicht mit
            from PySide6.QtWidgets import QSizePolicy
            for k in range(self.stapel.count()):
                w = self.stapel.widget(k); sp = w.sizePolicy()
                sp.setVerticalPolicy(QSizePolicy.Preferred if k == i else QSizePolicy.Ignored); w.setSizePolicy(sp)
            self.stapel.updateGeometry()
            e = self.stapel.parentWidget()
            while e is not None:
                if e.layout() is not None:
                    e.layout().invalidate()
                e = e.parentWidget()
        self.reiter.currentChanged.connect(hoehe_der_seite)
        hoehe_der_seite(self.reiter.currentIndex())
        self.setMinimumSize(0, 0)

    def freischalten(self) -> None:
        """Alle Reiter sind immer anklickbar; Sprache, MCP und Websuche brauchen kein Modell, die Zuweisung zeigt ohne Modell eine leere Auswahl."""
        for i in range(self.reiter.count()):
            self.reiter.setTabEnabled(i, True)
            self.reiter.setTabToolTip(i, "")

    def neues_modell(self) -> None:
        def fertig():
            self.liste._fuellen()
            self.zuweisung.aufbauen()
            self.fenster.ki.geaendert.emit()
            self.freischalten()
        zeige_unter(self, AnbieterDialog(self.fenster, self.k), fertig)

    def _ok(self) -> None:
        self.zuweisung.uebernehmen()
        self.sprache.uebernehmen()
        self.websuche.uebernehmen()
        self.dokumente.uebernehmen()
        self.accept()


VORLAGEN_AKTION = [
    ("Übersetzen", "Übersetze den Text ins Englische."), ("Ton ändern", "Schreibe den Text in einem freundlicheren, höflichen Ton."),
    ("Professionelle Umschreibung", "Schreibe den Text professionell und sachlich um."),
    ("Zusammenfassung als Liste", "Fasse den Text als kurze Aufzählung zusammen."), ("Text vereinfachen", "Schreibe den Text in einfacher Sprache."),
    ("Text erweitern", "Erweitere den Text um passende Einzelheiten."), ("Grammatik korrigieren", "Korrigiere Grammatik und Rechtschreibung."),
    ("Kürzer machen", "Kürze den Text, ohne Wichtiges wegzulassen."), ("Länger machen", "Mache den Text ausführlicher."),
    ("Kernpunkte herausziehen", "Nenne die Kernpunkte des Textes."), ("Tabelle erstellen", "Fasse die Angaben des Textes in einer Tabelle zusammen."),
    ("Beispiele hinzufügen", "Ergänze passende Beispiele."), ("Einfach erklären", "Erkläre den Inhalt so, dass ihn ein Kind versteht.")]
ERGEBNIS_ARTEN = (("ersetzen", "Ersetzen (ersetzt den markierten Text durch das Ergebnis)"), ("anhaengen", "Anhängen (setzt das Ergebnis hinter den Text)"),
                  ("hinweis", "Als Hinweis zeigen (Karte in der Seitenleiste)"))


class SchnelleAktionDialog(ErstellenFenster):
    """„Schnelle KI-Aktion erstellen“: eine einmalige KI-Aufgabe mit Name, Anweisung, Ergebnisart und Zugriff.

    Speichert als „Eigener Assistent“ (``KIKonfig.assistenten``) — dieselbe Liste wie im Band und in den Optionen."""

    def __init__(self, fenster):
        from PySide6.QtWidgets import QRadioButton
        super().__init__(fenster, TEXTE_AKTION["titel"], TEXTE_AKTION["hinweis"], [n for n, _p in VORLAGEN_AKTION], meldung=TEXTE_AKTION["meldung"])
        g = self.gitter
        self.name_zeile("Name *", TEXTE_AKTION["name"])
        self.prompt_zeile("Was soll die Aktion tun? *", TEXTE_AKTION["prompt"])
        self.ergebnis = Auswahlfeld()
        self.ergebnis.zeichen(DROPDOWN_ZEICHEN_LANG)
        for schl, text in ERGEBNIS_ARTEN:
            self.ergebnis.addItem(text, schl)
        g.zeile("Ergebnis anwenden als", self.ergebnis)
        g.breit(abschnittstitel("Zugriff von"))
        self.r_kontext = QRadioButton("Verfügbar über das Kontextmenü"); self.r_kontext.setChecked(True)
        self.r_schnell = QRadioButton("Schnellzugriff über die Symbolleiste")
        zugriff = FlussLayout(); zugriff.addWidget(self.r_kontext); zugriff.addWidget(self.r_schnell)
        g.breit(zugriff)
        self.abschliessen()

    def vorlage_gewaehlt(self, i: int) -> None:
        self.name.setText(VORLAGEN_AKTION[i][0]); self.prompt.setPlainText(VORLAGEN_AKTION[i][1])

    def werte(self) -> tuple:
        return (self.name.text(), self.prompt.toPlainText(), self.ergebnis.currentData(), "schnell" if self.r_schnell.isChecked() else "kontext")


TEXTE_AKTION = {"titel": "Schnelle KI-Aktion erstellen", "hinweis": "Eine schnelle KI-Aktion führt einmalige KI-Aufgaben aus.",
                "meldung": "Name und Beschreibung werden gebraucht.", "name": "Geben Sie einen kurzen Namen für die Aktion ein",
                "prompt": "Beschreiben Sie die Aktion, die die KI ausführen soll, z. B. „Grammatik korrigieren“ oder „In einem formellen Ton umschreiben“"}
TEXTE_ASSISTENT = {"titel": "Neuen Assistenten erstellen", "hinweis": "Ein KI-Assistent kann fortlaufend arbeiten und auf Änderungen im Dokument reagieren.",
                    "meldung": "Name und Prompt werden gebraucht.", "name": "Geben Sie Ihrem Werkzeug einen kurzen Namen für die Symbolleiste",
                    "prompt": "Sagen Sie der KI, was Sie mit dem Text tun möchten (z. B. „Faktenfehler finden“ oder „Zusammenfassung“)"}
AKTION_TEXTE = {"ersetzen": "Ersetzen (Ersetzt den ausgewählten Text mit dem KI-Ergebnis)",
                "anhaengen": "Anhängen (Setzt das KI-Ergebnis hinter den Text)",
                "hinweis": "Hinweis (Zeigt das Ergebnis als Karte in der Seitenleiste)",
                "kommentar": "Kommentar (Legt das Ergebnis als Kommentar am Text an)",
                "hervorheben": "Hervorheben (Meldet Funde in der Schreibhilfe)"}
AUSLOESER_TEXTE = {"knopf": "Nur auf Knopfdruck (keine Überwachung)", "absatz": "Wenn ein Absatz geändert wird", "markierung": "Wenn Text markiert wird"}
UMFANG_TEXTE = {"absatz": "Der geänderte Absatz", "markierung": "Die Markierung"}
ASSISTENT_DATENSCHUTZ = ("Ein fortlaufender Assistent sendet den geänderten Absatz an das gewählte KI-Modell. Bei einem Anbieter im Internet verlässt der Text "
                         "den Rechner und kann Kosten verursachen; er läuft nur bei eingeschaltetem Hauptschalter und gesetztem Haken.")


class KIAssistentDialog(ErstellenFenster):
    """„Neuen Assistenten erstellen“: ein KI-Assistent, der fortlaufend arbeitet und auf Änderungen im Dokument reagiert.

    ``werte()`` liefert ``(name, prompt, modus, mehr)``; der Befehl ``w_kiAssistentErstellen`` speichert mit ``art="fortlaufend"``."""

    def __init__(self, fenster):
        from lunivo_writer.ai.assistent_lauf import VERZOEGERUNG_MAX, VERZOEGERUNG_MIN, VERZOEGERUNG_VORGABE
        from lunivo_writer.ui.baukasten.dropdown.symbol_auswahl import SymbolWahl
        from lunivo_writer.ui.baukasten.mass_feld import spin
        t = TEXTE_ASSISTENT
        super().__init__(fenster, t["titel"], t["hinweis"], [e[0] for e in K.VORLAGEN_ASSISTENT], meldung=t["meldung"])
        g = self.gitter
        self.symbol = SymbolWahl()
        self.name_zeile("Name *", t["name"], symbol=self.symbol)
        self.aktion = Auswahlfeld(); self.aktion.zeichen(DROPDOWN_ZEICHEN_LANG)
        for schl in K.FORTLAUFEND_MODI:
            self.aktion.addItem(AKTION_TEXTE[schl], schl)
        g.zeile("Aktion", self.aktion)
        self.prompt_zeile("Prompt *", t["prompt"])
        self.kommentar = UmbruchSchalter("Erklärender Kommentar")
        self.kommentar.setToolTip("Die KI begründet jede Änderung kurz in einem Kommentar.")
        g.breit(self.kommentar)
        self.erweitert = AufklappBereich("Erweiterte Einstellungen")
        eg = FormularGitter(self.erweitert.inhalt); eg.setContentsMargins(*RAND_KEIN)
        self.modell = Auswahlfeld(); modell_felder_fuellen(self.modell, fenster.ki.konfig, "assistent", "")
        eg.zeile("Modell", self.modell)
        self.ausloeser = Auswahlfeld(); self.ausloeser.zeichen(DROPDOWN_ZEICHEN_LANG)
        for schl in K.ASSISTENT_AUSLOESER:
            self.ausloeser.addItem(AUSLOESER_TEXTE[schl], schl)
        self.ausloeser.setCurrentIndex(max(0, self.ausloeser.findData(K.ASSISTENT_AUSLOESER[1])))
        eg.zeile("Auslöser", self.ausloeser)
        self.verzoegerung = spin(VERZOEGERUNG_VORGABE, VERZOEGERUNG_MIN, VERZOEGERUNG_MAX, " s", 1, 0)
        eg.zeile("Verzögerung", self.verzoegerung)
        self.umfang = Auswahlfeld()
        for schl in K.ASSISTENT_UMFAENGE:
            self.umfang.addItem(UMFANG_TEXTE[schl], schl)
        eg.zeile("Umfang", self.umfang)
        self.an = UmbruchSchalter("Sofort einschalten"); self.an.setChecked(True)
        eg.breit(self.an)
        hinweis = QLabel(ASSISTENT_DATENSCHUTZ); hinweis.setWordWrap(True); hinweis_stil(hinweis)
        eg.breit(hinweis)
        g.breit(self.erweitert)
        self.abschliessen()

    def vorlage_gewaehlt(self, i: int) -> None:
        name, prompt, modus, kommentar = K.VORLAGEN_ASSISTENT[i]
        self.name.setText(name); self.prompt.setPlainText(prompt); self.aktion.setCurrentIndex(max(0, self.aktion.findData(modus)))
        self.kommentar.setChecked(bool(kommentar))

    def werte(self) -> tuple:
        mehr = {"symbol": self.symbol.wert(), "kommentar": self.kommentar.isChecked(), "modell": self.modell.currentData() or "",
                "ausloeser": self.ausloeser.currentData(), "umfang": self.umfang.currentData(), "verzoegerung": int(self.verzoegerung.value()),
                "an": self.an.isChecked()}
        return (self.name.text().strip(), self.prompt.toPlainText().strip(), self.aktion.currentData(), mehr)


class ErgebnisseDialog(PanelFaehig, QDialog):
    """„Alle Ergebnisse anzeigen“: die KI-Antworten dieser Sitzung; Kopieren oder an der Schreibmarke einfügen."""

    def __init__(self, fenster):
        super().__init__(fenster)
        from PySide6.QtWidgets import QApplication, QPlainTextEdit
        self.fenster = fenster
        self.setWindowTitle("Alle Ergebnisse")
        self.liste_daten = list(reversed(fenster.ki.ergebnisse))                     # neueste oben
        v = QVBoxLayout(self)
        self.liste = QListWidget()
        self.liste.setMaximumHeight(HOEHE_LISTE_AUSWAHL)
        for e in self.liste_daten:
            self.liste.addItem(f"{e['zeit']}  {e['titel']}")
        v.addWidget(self.liste)
        self.text = QPlainTextEdit(); self.text.setReadOnly(True); self.text.setMinimumHeight(HOEHE_LISTE_KURZ)
        v.addWidget(self.text, 1)
        if not self.liste_daten:
            v.addWidget(QLabel("In dieser Sitzung hat die KI noch nichts geliefert."))
        bb = knopfzeile(self, schliessen=True)
        self.kopieren = bb.zusatz_knopf(QPushButton("Kopieren"))
        self.einfuegen = bb.zusatz_knopf(QPushButton("Einfügen"))
        self.kopieren.clicked.connect(lambda: QApplication.clipboard().setText(self.text.toPlainText()))
        self.einfuegen.clicked.connect(self._einfuegen)
        v.addWidget(bb)
        self.liste.currentRowChanged.connect(self._zeigen)
        if self.liste_daten:
            self.liste.setCurrentRow(0)
        self._zeigen(self.liste.currentRow())

    def _zeigen(self, i: int) -> None:
        an = 0 <= i < len(self.liste_daten)
        self.text.setPlainText(self.liste_daten[i]["text"] if an else "")
        self.kopieren.setEnabled(an); self.einfuegen.setEnabled(an)

    def _einfuegen(self) -> None:
        e = self.fenster.current_editor()
        if e is not None and self.text.toPlainText():
            e.textCursor().insertText(self.text.toPlainText())
