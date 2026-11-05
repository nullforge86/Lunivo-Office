"""KI-Konfiguration: Aufgaben-Modellzuweisung, Liste der KI-Modelle, „Eigenen Anbieter hinzufügen“.

Der Anbieter wird hier festgelegt — in „KI-Konfiguration“ (Reiter Schreibhilfe/KI) oder in den Optionen.
"""
from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtWidgets import (
    QSizePolicy, QComboBox, QDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QToolButton, QVBoxLayout, QWidget,
)

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
    PADDING_KI_ANBIETER_EINTRAG,
    PADDING_KI_LISTENEINTRAG,
    RADIUS_FELD,
    RAND_KEIN,
    RAND_OBEN_SEITE,
)
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
        self.vorlage = QComboBox()
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
        self.modell = QComboBox()
        self.modell.setEditable(True)
        self.modell.setInsertPolicy(QComboBox.NoInsert)
        self.modell.lineEdit().setPlaceholderText("z. B. gpt-4o-mini")
        self.modell.setCurrentText(bestehend["modell"] if bestehend else "")
        self.modell.setMinimumContentsLength(10)
        self.modell.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)
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
        alle.setStyleSheet(_chip())
        alle.toggled.connect(lambda an: [b.setChecked(an) for b in self.tags.values()])
        self._chips = [alle]
        for key, name in K.ANBIETER_TAGS:
            b = QPushButton(name)
            b.setCheckable(True)
            b.setChecked(key in gesetzt)
            b.setStyleSheet(_chip())
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

    def _holen(self, still: bool) -> None:
        url, schl = self.url.text().strip(), self.schluessel.text().strip()
        if not url:
            if not still:
                self.stand.setText("Erst die URL eintragen.")
            return
        self.stand.setText("Wird geholt …")

        class _L(QRunnable):
            def run(s_):
                try:
                    r = {"namen": K.anbieter_modelle(url, schl)}
                except Exception as e:                  # Netz, Schlüssel, falsche Adresse — alles landet als Hinweis
                    r = {"fehler": str(e)}
                try:
                    self._antwort.da.emit(r)
                except RuntimeError:
                    pass                                # Dialog war schon zu
        QThreadPool.globalInstance().start(_L())

    def _geholt(self, r: dict) -> None:
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


def _chip() -> str:
    """Auswahl-Chip (Baustein ``schalter.chip_stil``)."""
    from lunivo_writer.ui.baukasten.schalter import chip_stil
    return chip_stil()


class ModellListe(QWidget):
    """Die Liste der verbundenen KI-Modelle: hinzufügen, bearbeiten, entfernen (im Fenster „KI-Einstellungen“ und als eigenes Fenster)."""

    def __init__(self, fenster, konfig: K.KIKonfig):
        super().__init__()
        self.fenster, self.k = fenster, konfig
        self.setMinimumHeight(HOEHE_LISTE_ANBIETER)
        g = FormularGitter(self)
        g.setContentsMargins(*RAND_KEIN)
        self.liste = QListWidget(); self.liste.setMinimumHeight(HOEHE_LISTE_MITTEL)
        g.breit(self.liste)
        self.neu = QToolButton(); self.neu.setIcon(icons.icon("plus", ICON_NORMAL)); self.neu.setToolTip("Anbieter hinzufügen")
        self.bearb = QToolButton(); self.bearb.setIcon(icons.icon("pencil", ICON_NORMAL)); self.bearb.setToolTip("Bearbeiten")
        self.weg = QToolButton(); self.weg.setIcon(icons.icon("trash-2", ICON_NORMAL)); self.weg.setToolTip("Entfernen")
        s = FlussLayout(6)
        for b in (self.neu, self.bearb, self.weg):
            b.setMinimumWidth(BREITE_KNOPF_KLEIN); s.addWidget(b)
        g.breit(s)
        self.neu.clicked.connect(self._neu)
        self.bearb.clicked.connect(self._bearbeiten)
        self.weg.clicked.connect(self._entfernen)
        self.liste.currentRowChanged.connect(self._knoepfe)
        self.liste.itemDoubleClicked.connect(lambda _i: self._bearbeiten())
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
        self._knoepfe()

    def _knoepfe(self, *_):
        an = self.liste.currentRow() >= 0
        self.bearb.setEnabled(an)
        self.weg.setEnabled(an)

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


def modell_combo(konfig: K.KIKonfig, aufgabe: str, gewaehlt: str | None = None) -> QComboBox:
    """Die Auswahl „welches Modell für diese Aufgabe?“ — dieselbe in der Modellzuweisung und in den erweiterten Einstellungen des Chats."""
    c = QComboBox()
    c.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon)       # lange Modellnamen machen das Feld nicht breiter als die Seitenleiste
    c.setMinimumContentsLength(12)
    c.addItem("Standard (KI-Modell der Optionen)", "")
    for m in konfig.alle_modelle():
        if not modell_passt(m, aufgabe):
            continue
        c.addItem(m["name"] + ("  · lokal" if m["lokal"] else ""), m["id"])
    g = konfig["aufgaben"].get(aufgabe, "") if gewaehlt is None else gewaehlt
    c.setCurrentIndex(max(0, c.findData(g)))
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


class SprachListe(QListWidget):
    """Eine Sprachliste mit hohen Zeilen (wie das alte Fenster „Einstellungen der Übersetzung“); bedienbar wie eine Auswahl: ``currentData()``,
    ``currentText()``, ``setCurrentText()``, ``findData()``, ``setCurrentIndex()``."""

    def __init__(self, eintraege: list[tuple[str, str]]):
        super().__init__()
        for daten, text in eintraege:
            it = QListWidgetItem(text); it.setData(Qt.UserRole, daten); self.addItem(it)
        self.setStyleSheet("QListWidget { border: 1px solid palette(mid); border-radius: " f"{RADIUS_FELD}" "px; }"
                           "QListWidget::item { padding: " f"{PADDING_KI_ANBIETER_EINTRAG}" "; border-bottom: 1px solid palette(midlight); }"
                           "QListWidget::item:selected { background: palette(highlight); color: palette(highlighted-text); }"
                           "QListWidget::item:hover:!selected { background: palette(alternate-base); }")
        self.setMinimumHeight(HOEHE_LISTE_REITER)

    def currentData(self):
        it = self.currentItem()
        return it.data(Qt.UserRole) if it else None

    def currentText(self) -> str:
        it = self.currentItem()
        return it.text() if it else ""

    def findData(self, daten) -> int:
        return next((i for i in range(self.count()) if self.item(i).data(Qt.UserRole) == daten), -1)

    def setCurrentIndex(self, i: int) -> None:
        self.setCurrentRow(i)
        if 0 <= i < self.count():
            self.scrollToItem(self.item(i))

    def setCurrentText(self, text: str) -> None:
        self.setCurrentIndex(next((i for i in range(self.count()) if self.item(i).text() == text), -1))


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
        self.pruefung = SprachListe(list(b.SPRACHEN))
        self.pruefung.setCurrentIndex(max(0, self.pruefung.findData(b.pruefsprache_aktuell())))
        self.pruefung.setEnabled(fenster.current_tab() is not None)
        self.sprache = SprachListe([(n, n) for n in K.SPRACHEN])
        self.sprache.setCurrentText(fenster.ki.konfig["sprache"])
        for titel, unter, liste in (("Sprache für die Überprüfung", "Sprache des Dokuments — wird in der Datei vermerkt.", self.pruefung),
                                    ("Übersetzen nach", "Sprache für die KI-Übersetzung wählen.", self.sprache)):
            g.breit(abschnittstitel(titel))
            hint = QLabel(unter); hint.setWordWrap(True); hinweis_stil(hint); g.breit(hint)
            liste.setMinimumHeight(0); liste.setFixedHeight(HOEHE_BEREICH_MITTEL); liste.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            liste.setStyleSheet(liste.styleSheet() + "QListWidget::item { padding: " f"{PADDING_KI_LISTENEINTRAG}" "; border-bottom: 1px solid palette(midlight); }")
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
        self.setWindowTitle("MCP-Server bearbeiten" if e else "MCP-Server hinzufügen"); self.resize(*GROESSE_FENSTER_MCP)
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
            QMessageBox.information(self, "MCP-Server", "Name und Befehl werden gebraucht.")
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
        info = QLabel("MCP-Server geben der KI im Chat Werkzeuge (Dateien lesen, Daten abfragen …). Gilt für Ollama und eigene Anbieter.")
        info.setWordWrap(True); g.breit(info)
        self.liste = QListWidget(); self.liste.setMinimumHeight(HOEHE_LISTE_KURZ); g.breit(self.liste)
        s = FlussLayout(6)
        self.neu = QToolButton(); self.neu.setIcon(icons.icon("plus", ICON_NORMAL)); self.neu.setToolTip("Server hinzufügen")
        self.bearb = QToolButton(); self.bearb.setIcon(icons.icon("pencil", ICON_NORMAL)); self.bearb.setToolTip("Bearbeiten")
        self.weg = QToolButton(); self.weg.setIcon(icons.icon("trash-2", ICON_NORMAL)); self.weg.setToolTip("Entfernen")
        for b in (self.neu, self.bearb, self.weg):
            b.setMinimumWidth(BREITE_KNOPF_KLEIN); s.addWidget(b)
        g.breit(s); v.addStretch(1)
        self.neu.clicked.connect(self._neu); self.bearb.clicked.connect(self._bearbeiten); self.weg.clicked.connect(self._entfernen)
        self.liste.currentRowChanged.connect(self._knoepfe)
        self.liste.itemDoubleClicked.connect(lambda _i: self._bearbeiten())
        self.fuellen()

    def fuellen(self) -> None:
        self.liste.clear()
        for m in self.k["mcp"]:
            it = QListWidgetItem(f"{m['name']}{'' if m['an'] else '  (aus)'}\n{m['befehl']}")
            it.setData(Qt.UserRole, m["id"]); self.liste.addItem(it)
        if self.liste.count():
            self.liste.setCurrentRow(0)
        self._knoepfe()

    def _knoepfe(self, *_) -> None:
        an = self.liste.currentRow() >= 0
        self.bearb.setEnabled(an); self.weg.setEnabled(an)

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
        self.anbieter = QComboBox()
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


REITER = ("KI-Modelle", "Modellzuweisung", "Sprache", "MCP-Server", "Websuche", "Datenschutz")


from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig


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
        v.addWidget(knopfzeile(self, bei_ok=self._ok))
        self.reiter.currentChanged.connect(self.stapel.setCurrentIndex)
        self.freischalten()
        self.reiter.setCurrentIndex(start if self.reiter.isTabEnabled(start) else 0)

    def kompakt_machen(self) -> None:
        """In der Seitenleiste: kurze Reiternamen (die langen stehen im Tipp), damit alle fünf nebeneinander passen."""
        for i, (kurz, voll) in enumerate((("Modelle", "KI-Modelle"), ("Zuweisung", "Modellzuweisung"), ("Sprache", "Sprache"), ("MCP", "MCP-Server"),
                                          ("Websuche", "Websuche"), ("Daten", "Datenschutz"))):
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


class SchnelleAktionDialog(PanelFaehig, QDialog):
    """„Schnelle KI-Aktion erstellen“: eine einmalige KI-Aufgabe mit Name, Anweisung, Ergebnisart und Zugriff.

    Speichert als „Eigener Assistent“ (``KIKonfig.assistenten``) — dieselbe Liste wie im Band und in den Optionen."""

    def __init__(self, fenster):
        super().__init__(fenster)
        from PySide6.QtWidgets import QPlainTextEdit, QRadioButton
        self.setWindowTitle("Schnelle KI-Aktion erstellen")
        v = QVBoxLayout(self)
        inhalt = QWidget(); g = FormularGitter(inhalt)
        kopf = QLabel("Eine schnelle KI-Aktion führt einmalige KI-Aufgaben aus."); kopf.setWordWrap(True)
        g.breit(kopf)
        g.breit(abschnittstitel("Mit einer Vorlage beginnen"))
        self.chipfluss = FlussLayout(6)
        self.chips = []
        for name, prompt in VORLAGEN_AKTION:
            b = QPushButton(name); b.setStyleSheet(_chip()); b.clicked.connect(lambda _=False, n=name, p=prompt: self._vorlage(n, p))
            self.chips.append(b)
        g.breit(self.chipfluss)
        self.mehr = QPushButton(); self.mehr.setFlat(True); self.mehr.setCursor(Qt.PointingHandCursor)
        self.mehr.clicked.connect(self._umschalten)
        g.breit(self.mehr)
        self.name = QLineEdit(); self.name.setPlaceholderText("Geben Sie einen kurzen Namen für die Aktion ein"); self.name.setMaxLength(40)
        g.zeile("Name *", self.name)
        self.prompt = QPlainTextEdit()
        self.prompt.setPlaceholderText("Beschreiben Sie die Aktion, die die KI ausführen soll, z. B. „Grammatik korrigieren“ oder „In einem formellen Ton umschreiben“")
        self.prompt.setMinimumHeight(HOEHE_TEXT_NORMAL)
        g.zeile("Was soll die Aktion tun? *", self.prompt)
        self.ergebnis = QComboBox()
        self.ergebnis.setSizeAdjustPolicy(QComboBox.AdjustToMinimumContentsLengthWithIcon); self.ergebnis.setMinimumContentsLength(10)
        for schl, text in ERGEBNIS_ARTEN:
            self.ergebnis.addItem(text, schl)
        g.zeile("Ergebnis anwenden als", self.ergebnis)
        g.breit(abschnittstitel("Zugriff von"))
        self.r_kontext = QRadioButton("Verfügbar über das Kontextmenü"); self.r_kontext.setChecked(True)
        self.r_schnell = QRadioButton("Schnellzugriff über die Symbolleiste")
        zugriff = FlussLayout(6); zugriff.addWidget(self.r_kontext); zugriff.addWidget(self.r_schnell)
        g.breit(zugriff)
        v.addWidget(inhalt)
        z = knopfzeile(self, bei_ok=self._ok, ok_text="Erstellen")
        self.ok = z.ok
        v.addWidget(z)
        self._alle = False
        self._umschalten()

    def _umschalten(self) -> None:
        """Erst die ersten sechs Vorlagen, mit „Alle anzeigen“ alle."""
        self._alle = not self._alle
        while self.chipfluss.count():                                    # ausgeblendete Vorlagen dürfen im Fluss keinen Platz belegen
            self.chipfluss.takeAt(0)
        for i, b in enumerate(self.chips):
            zeigen = self._alle or i < 6
            b.setVisible(zeigen)
            if zeigen:
                self.chipfluss.addWidget(b)
        self.mehr.setText("Ausblenden" if self._alle else "Alle anzeigen")
        self.chipfluss.invalidate()

    def _vorlage(self, name: str, prompt: str) -> None:
        self.name.setText(name)
        self.prompt.setPlainText(prompt)

    def _ok(self) -> None:
        if not self.name.text().strip() or not self.prompt.toPlainText().strip():
            QMessageBox.information(self, "Schnelle KI-Aktion", "Name und Beschreibung werden gebraucht.")
            return
        self.accept()

    def werte(self) -> tuple:
        return (self.name.text(), self.prompt.toPlainText(), self.ergebnis.currentData(), "schnell" if self.r_schnell.isChecked() else "kontext")


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
