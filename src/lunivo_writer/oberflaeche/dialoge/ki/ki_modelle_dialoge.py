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
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld

from lunivo_writer.oberflaeche.baukasten.basis.texte import hinweis_stil
from lunivo_writer.oberflaeche.baukasten.basis.beschriftung import text_label
from lunivo_writer.ki import ki as K
from lunivo_writer.oberflaeche.baukasten.geruest.fenster_stapel import zeige_unter
from lunivo_writer.oberflaeche.baukasten.basis.dialog_rahmen import knopfzeile
from lunivo_writer.oberflaeche.baukasten.geruest.zusatz_panel import PanelFaehig
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import FlussLayout, FormularGitter, UmbruchSchalter, abschnittstitel
from lunivo_writer.oberflaeche.bauteile import symbole


from lunivo_writer.kern.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.felder.flache_reiter_leiste import HAUPT, FlacheReiterLeiste
from lunivo_writer.oberflaeche.baukasten.felder.auswahl_liste import AuswahlListe
from lunivo_writer.oberflaeche.baukasten.basis.karte import als_karte
from lunivo_writer.oberflaeche.baukasten.felder.listen_leiste import ListenLeiste
from lunivo_writer.oberflaeche.baukasten.basis.mass import (
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
from lunivo_writer.oberflaeche.baukasten.dropdown.auswahlfeld import Auswahlfeld
from lunivo_writer.oberflaeche.baukasten.basis.mass import DROPDOWN_ZEICHEN_LANG
def _tags_text(a: dict) -> str:
    n = dict(K.ANBIETER_TAGS)
    return ", ".join(n[t] for t in a.get("verwendungFuer", []) if t in n)


class _Antwort(QObject):
    da = Signal(object)


class AnbieterDialog(QDialog):
    """Neuer oder zu bearbeitender Anbieter: Name, Vorlage, URL, Schlüssel, Modell (Liste vom Anbieter), Fähigkeiten."""

    def __init__(self, fenster, konfig: K.KIKonfig, bestehend: dict | None = None):
        super().__init__(fenster)
        self.k, self.alt = konfig, bestehend
        self.setWindowTitle("Modell bearbeiten" if bestehend else "Eigenen Anbieter hinzufügen"); self.resize(*GROESSE_FENSTER_ANBIETER)
        v = QVBoxLayout(self)
        t = self._titel = text_label(self.windowTitle(), fett=True, pt=13, umbruch=False)
        v.addWidget(t)
        f = FormularGitter()
        self.name = QLineEdit(bestehend["name"] if bestehend else "")
        self.name.setPlaceholderText("Modellname")
        f.zeile("Modellname *", self.name)
        h = QLabel("Oben den Anbieter wählen — die URL füllt sich von selbst und lässt sich danach noch ändern. "
                   "Nur bei „Andere“ bleibt sie leer und will von Hand eingetragen werden.")
        h.setWordWrap(True)
        hinweis_stil(h)
        f.breit(h)
        self.vorlage = Auswahlfeld()
        for key, name, url in K.ANBIETER_VORLAGEN:
            self.vorlage.addItem(name, url)
        self.url = QLineEdit(bestehend["url"] if bestehend else "")
        self.url.setPlaceholderText("https://…/v1")
        self.schluessel = QLineEdit(bestehend["schluessel"] if bestehend else "")
        self.schluessel.setEchoMode(QLineEdit.Password)
        self.schluessel.setPlaceholderText("Nicht erforderlich")
        f.zeile("Anbieter *", self.vorlage)
        f.zeile("URL *", self.url)
        f.zeile("Schlüssel", self.schluessel)
        self.modell = Auswahlfeld()
        self.modell.setEditable(True)
        self.modell.setInsertPolicy(QComboBox.NoInsert)
        self.modell.lineEdit().setPlaceholderText("z. B. gpt-4o-mini")
        self.modell.setCurrentText(bestehend["modell"] if bestehend else "")
        self.modell.zeichen(DROPDOWN_ZEICHEN_LANG)
        self.stand = QLabel(""); self.stand.setWordWrap(True)
        hinweis_stil(self.stand)
        holen = QPushButton("Liste der Modelle aktualisieren")
        holen.setFlat(True)
        holen.setCursor(Qt.PointingHandCursor)
        holen.clicked.connect(lambda: self._holen(False))
        f.zeile("Modell *", self.modell)
        holen_zeile = FlussLayout(6); holen_zeile.addWidget(holen)
        f.breit(holen_zeile)
        f.breit(self.stand)
        f.breit(abschnittstitel("Modell verwenden für"))
        self._chipgitter = FlussLayout(6)
        f.breit(self._chipgitter)
        v.addLayout(f)
        self.tags = {}
        gesetzt = set(bestehend["verwendungFuer"]) if bestehend else {"text"}
        alle = QPushButton("Alle")
        alle.setCheckable(True)
        als_karte(alle, "chip")
        alle.toggled.connect(lambda an: [b.setChecked(an) for b in self.tags.values()])
        self._chips = [alle]
        for key, name in K.ANBIETER_TAGS:
            b = QPushButton(name)
            b.setCheckable(True)
            b.setChecked(key in gesetzt)
            als_karte(b, "chip")
            self.tags[key] = b
            self._chips.append(b)
        for b in self._chips:
            pass
            self._chipgitter.addWidget(b)
        v.addStretch(1)
        z = knopfzeile(self, bei_ok=self._ok, ok_text="Speichern" if bestehend else "Hinzufügen")
        self.ok = z.ok
        v.addWidget(z)
        self._antwort = _Antwort()
        self._antwort.da.connect(self._geholt)
        self._modell_abfrage = 0
        self.url.textChanged.connect(self._modell_abfrage_ungueltig)
        self.schluessel.textChanged.connect(self._modell_abfrage_ungueltig)
        self.vorlage.currentIndexChanged.connect(self._vorlage_gewaehlt)
        if bestehend:
            i = next((i for i in range(self.vorlage.count()) if self.vorlage.itemData(i) == bestehend["url"]), 0)
            self.vorlage.blockSignals(True)
            self.vorlage.setCurrentIndex(i)
            self.vorlage.blockSignals(False)
        elif not bestehend:
            self.vorlage.setCurrentIndex(1)           # Ollama ist die Vorbelegung

    def kompakt_machen(self) -> None:
        """In der Seitenleiste: der Titel steht schon im Kopf der Seite; die Fähigkeiten laufen als Fluss in die Breite."""
        self._titel.setVisible(False)

    def _vorlage_gewaehlt(self, i: int) -> None:
        url = self.vorlage.itemData(i)
        if self.vorlage.currentText() == "Andere":
            self.url.clear()
        else:
            self.url.setText(url)
            if not self.name.text().strip() or self.name.text() in [n for _, n, _ in K.ANBIETER_VORLAGEN]:
                self.name.setText(self.vorlage.currentText())
            self._holen(True)

    def _modell_abfrage_ungueltig(self, *_args) -> None:
        """Antworten für eine alte URL oder einen alten Schlüssel dürfen die aktuelle Modellliste nicht überschreiben."""
        self._modell_abfrage += 1

    def _holen(self, still: bool) -> None:
        url, schl = self.url.text().strip(), self.schluessel.text().strip()
        if not url:
            if not still:
                self.stand.setText("Erst die URL eintragen.")
            return
        self._modell_abfrage += 1
        kennung = self._modell_abfrage
        self.stand.setText("Wird geholt …")

        class _L(QRunnable):
            def run(s_):
                try:
                    r = {"namen": K.anbieter_modelle(url, schl)}
                except Exception as e:                  # Netz, Schlüssel, falsche Adresse — alles landet als Hinweis
                    r = {"fehler": str(e)}
                r["kennung"] = kennung
                try:
                    self._antwort.da.emit(r)
                except RuntimeError:
                    pass                                # Dialog war schon zu
        QThreadPool.globalInstance().start(_L())

    def _geholt(self, r: dict) -> None:
        if r.get("kennung") != self._modell_abfrage:
            return
        if "fehler" in r:
            self.stand.setText("Nicht abrufbar — Modell von Hand eintragen.")
            return
        namen = r["namen"]
        if not namen:
            self.stand.setText("Der Anbieter nennt keine Modelle.")
            return
        aktuell = self.modell.currentText()
        self.modell.clear()
        self.modell.addItems(namen)
        self.modell.setCurrentText(aktuell if aktuell in namen or aktuell else "")
        if not aktuell:
            self.modell.setCurrentIndex(-1)
            self.modell.lineEdit().setPlaceholderText("— Modell wählen —")
        self.stand.setText(f"{len(namen)} gefunden.")

    def _ok(self) -> None:
        if not self.name.text().strip() or not self.url.text().strip() or not self.modell.currentText().strip():
            QMessageBox.information(self, "Anbieter", "Name, URL und Modell werden gebraucht.")
            return
        werte = (self.name.text(), self.url.text(), self.schluessel.text(), self.modell.currentText(),
                 [k for k, b in self.tags.items() if b.isChecked()])
        if self.alt:
            self.k.anbieter_aktualisieren(self.alt["id"], *werte)
        else:
            self.k.anbieter_hinzufuegen(*werte)
        self.accept()


class ModellListe(QWidget):
    """Die Liste der verbundenen KI-Modelle: hinzufügen, bearbeiten, entfernen (im Fenster „KI-Einstellungen“ und als eigenes Fenster)."""

    def __init__(self, fenster, konfig: K.KIKonfig):
        super().__init__()
        self.fenster, self.k = fenster, konfig
        self.setMinimumHeight(HOEHE_LISTE_ANBIETER)
        g = FormularGitter(self)
        g.setContentsMargins(*RAND_KEIN)
        self.leiste = ListenLeiste("Anbieter hinzufügen", HOEHE_LISTE_MITTEL)
        self.liste, self.neu, self.bearb, self.weg = self.leiste.liste, self.leiste.neu, self.leiste.bearb, self.leiste.weg
        g.breit(self.leiste)
        self.leiste.neu_angefordert.connect(self._neu)
        self.leiste.bearbeiten_angefordert.connect(self._bearbeiten)
        self.leiste.entfernen_angefordert.connect(self._entfernen)
        self._fuellen()

    def _fuellen(self) -> None:
        self.liste.clear()
        for a in self.k["anbieter"]:
            teile = [a["modell"], _tags_text(a), "Lokaler Anbieter" if K.ist_lokale_url(a["url"]) else "Über das Internet"]
            it = QListWidgetItem(f"{a['name']}\n{' · '.join(t for t in teile if t)}")
            it.setData(Qt.UserRole, a["id"])
            self.liste.addItem(it)
        if self.liste.count():
            self.liste.setCurrentRow(0)                    # der erste Eintrag ist gewählt: ✎ und 🗑 sind sofort bedienbar
        self.leiste.knoepfe_pruefen()

    def _aktuell(self):
        it = self.liste.currentItem()
        return self.k.anbieter_holen(it.data(Qt.UserRole)) if it else None

    def _neu(self) -> None:
        zeige_unter(self, AnbieterDialog(self.fenster, self.k), self._fuellen)

    def _bearbeiten(self) -> None:
        a = self._aktuell()
        if a:
            zeige_unter(self, AnbieterDialog(self.fenster, self.k, a), self._fuellen)

    def _entfernen(self) -> None:
        a = self._aktuell()
        if a and QMessageBox.question(self, "Entfernen", f"„{a['name']}“ aus der Liste entfernen?") == QMessageBox.Yes:
            self.k.anbieter_entfernen(a["id"])
            self._fuellen()


class ModellListeDialog(QDialog):
    """„Liste der KI-Modelle“ als eigenes Fenster (Optionen)."""

    def __init__(self, fenster, konfig: K.KIKonfig):
        super().__init__(fenster)
        self.setWindowTitle("Liste der KI-Modelle")
        v = QVBoxLayout(self)
        v.addWidget(text_label("Liste der KI-Modelle", fett=True, pt=13, umbruch=False))
        self.liste_widget = ModellListe(fenster, konfig)
        self._fuellen = self.liste_widget._fuellen
        v.addWidget(self.liste_widget, 1)
        v.addWidget(knopfzeile(self, nur_ok=True))


def modell_passt(m: dict, aufgabe: str) -> bool:
    """Lokale Übersetzung („argos:“) und „Automatisch“ („auto:“) gelten nur für ihre Aufgabe (``verwendungFuer``); Bildgenerierung hat ihre eigene Regel."""
    if m["id"].startswith((K.ARGOS_MARKE, K.AUTO_MARKE)) and aufgabe not in m["verwendungFuer"]:
        return False
    if aufgabe == "bildgenerierung":               # nur Anbieter mit „Bilder“ — Claude und Text-Modelle kennen das nicht
        return "bilder" in m["verwendungFuer"] and m["id"].startswith(K.EIGEN_MARKE)
    return True


def modell_felder_fuellen(combo: QComboBox, konfig: K.KIKonfig, aufgabe: str, gewaehlt: str | None = None, standard: str = "Standard (KI-Modell der Optionen)") -> None:
    """Die eine Stelle, die ein Modell-Auswahlfeld füllt (Modellzuweisung, Optionen, Chat): Eintrag „Standard“, dann alle passenden Modelle; Signale ruhen dabei."""
    combo.blockSignals(True)
    combo.clear()
    combo.addItem(standard, "")
    for m in konfig.alle_modelle():
        if modell_passt(m, aufgabe):
            combo.addItem(m["name"] + ("  · lokal" if m["lokal"] else ""), m["id"])
    g = konfig["aufgaben"].get(aufgabe, "") if gewaehlt is None else gewaehlt
    combo.setCurrentIndex(max(0, combo.findData(g)))
    combo.blockSignals(False)


def modell_combo(konfig: K.KIKonfig, aufgabe: str, gewaehlt: str | None = None) -> QComboBox:
    """Die Auswahl „welches Modell für diese Aufgabe?“ — dieselbe in der Modellzuweisung und in den erweiterten Einstellungen des Chats."""
    c = Auswahlfeld()                                                            # lange Modellnamen machen das Feld nicht breiter als die Seitenleiste
    modell_felder_fuellen(c, konfig, aufgabe, gewaehlt)
    return c


class ModellZuweisung(QWidget):
    """Je Aufgabe ein Modell: Chatbot, Zusammenfassen, Übersetzung, Textanalyse, Bildgenerierung."""

    def __init__(self, fenster):
        super().__init__()
        self.fenster = fenster
        self.k = fenster.ki.konfig
        self._v = v = QVBoxLayout(self)
        v.setContentsMargins(*RAND_KEIN)
        hinweis = QLabel("Fügen Sie hinzu und wählen Sie KI-Modelle für verschiedene Aufgaben aus."); hinweis.setWordWrap(True)
        v.addWidget(hinweis)
        self.halter: QWidget | None = None
        self.felder: dict[str, QComboBox] = {}
        v.addStretch(1)
        self.aufbauen()

    def aufbauen(self) -> None:
        alt = {a: c.currentData() for a, c in self.felder.items()}
        if self.halter is not None:
            self._v.removeWidget(self.halter); self.halter.setParent(None); self.halter.deleteLater()
        self.felder.clear()
        self.halter = QWidget(); g = FormularGitter(self.halter)               # Beschriftung links, bei 300 px über dem Feld
        for aufgabe, name in K.AUFGABEN:
            c = modell_combo(self.k, aufgabe, alt.get(aufgabe, self.k["aufgaben"].get(aufgabe, "")))
            self.felder[aufgabe] = c
            g.zeile(name, c)
        self._v.insertWidget(1, self.halter)

    def uebernehmen(self) -> None:
        for aufgabe, c in self.felder.items():
            self.k.aufgabe_setzen(aufgabe, c.currentData() or "")
        self.fenster.ki.geaendert.emit()


class KIKonfigurationDialog(QDialog):
    """Die Modellzuweisung als eigenes Fenster (nur noch für Altaufrufe; im Alltag öffnet „KI-Einstellungen“)."""

    def __init__(self, fenster):
        super().__init__(fenster)
        self.setWindowTitle("KI-Konfiguration")
        v = QVBoxLayout(self)
        v.addWidget(text_label("KI-Konfiguration", fett=True, pt=13, umbruch=False))
        self.zuweisung = ModellZuweisung(fenster)
        self.felder = self.zuweisung.felder
        v.addWidget(self.zuweisung)
        v.addWidget(knopfzeile(self, bei_ok=self._ok))

    def _ok(self) -> None:
        self.zuweisung.uebernehmen()
        self.accept()


