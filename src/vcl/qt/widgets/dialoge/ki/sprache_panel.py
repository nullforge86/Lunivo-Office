"""Sprache panel: aus ``vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.zustaende.geruest.rollen import spalte as _spalte
from PySide6.QtWidgets import QSizePolicy, QLabel, QWidget
from vcl.qt.widgets.bausteine.schrift.texte import hinweis_stil
from writer.funktionen import ki as KD
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter, abschnittstitel
from vcl.qt.widgets.bausteine.interaktion.felder.auswahl_liste import AuswahlListe
from vcl.qt.widgets.bausteine.farben.karte import als_karte
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_BEREICH_MITTEL
from vcl.qt.widgets.dialoge.ki.ki_einstellungen_panels_hilfen import OfflineSprachen


class SprachePanel(QWidget):
    """Die Sprachen der Schreibhilfe, nebeneinander: „Sprache für die Überprüfung“ (Sprache des Dokuments) und „Übersetzen nach“ (Ziel der KI-Übersetzung).
    Das Modell für die Übersetzung steht in der Modellzuweisung."""

    def __init__(self, fenster):
        super().__init__()
        self.fenster = fenster
        b = fenster.befehle
        v = _spalte("oben", self)
        g = FormularGitter(); v.addLayout(g); v.addStretch(1)
        self.pruefung = AuswahlListe(list(b.SPRACHEN))
        self.pruefung.setCurrentIndex(max(0, self.pruefung.findData(b.pruefsprache_aktuell())))
        self.pruefung.setEnabled(fenster.current_tab() is not None)
        self.sprache = AuswahlListe([(n, n) for n in KD.sprachen()])
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
