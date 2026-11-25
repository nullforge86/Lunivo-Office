"""Ki modelle dialoge hilfen: aus ``vcl.qt.widgets.dialoge.ki.ki_modelle_dialoge`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.feld.feld import zeilenfeld
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import knopf
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtWidgets import QComboBox, QDialog, QLabel, QLineEdit, QMessageBox
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from vcl.qt.widgets.bausteine.schrift.beschriftung import text_label
from framework.ki.dienst import ki as K
from vcl.qt.widgets.bausteine.rahmen.dialog_rahmen import knopfzeile
from vcl.qt.widgets.bausteine.interaktion.felder.fluss_layout import FlussLayout
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.farben.karte import als_karte
from vcl.qt.widgets.bausteine.abstaende.mass import GROESSE_FENSTER_ANBIETER
from vcl.qt.widgets.menues.dropdown.auswahlfeld import Auswahlfeld
from vcl.qt.widgets.bausteine.abstaende.mass import DROPDOWN_ZEICHEN_LANG


class _Antwort(QObject):
    da = Signal(object)


class AnbieterDialog(QDialog):
    """Neuer oder zu bearbeitender Anbieter: Name, Vorlage, URL, Schlüssel, Modell (Liste vom Anbieter), Fähigkeiten."""

    def __init__(self, fenster, konfig: K.KIKonfig, bestehend: dict | None = None):
        super().__init__(fenster)
        self.k, self.alt = konfig, bestehend
        self.setWindowTitle("Modell bearbeiten" if bestehend else "Eigenen Anbieter hinzufügen"); self.resize(*GROESSE_FENSTER_ANBIETER)
        v = _spalte("standard", self)
        t = self._titel = text_label(self.windowTitle(), fett=True, pt=13, umbruch=False)
        v.addWidget(t)
        f = FormularGitter()
        self.name = zeilenfeld("frei", bestehend["name"] if bestehend else "")
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
        self.url = zeilenfeld("frei", bestehend["url"] if bestehend else "")
        self.url.setPlaceholderText("https://…/v1")
        self.schluessel = zeilenfeld("frei", bestehend["schluessel"] if bestehend else "")
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
        holen = knopf("standard", "Liste der Modelle aktualisieren")
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
        alle = knopf("standard", "Alle")
        alle.setCheckable(True)
        als_karte(alle, "chip")
        alle.toggled.connect(lambda an: [b.setChecked(an) for b in self.tags.values()])
        self._chips = [alle]
        for key, name in K.ANBIETER_TAGS:
            b = knopf("standard", name)
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
