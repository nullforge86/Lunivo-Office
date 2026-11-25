"""Modell liste: aus ``vcl.qt.widgets.dialoge.ki.ki_modelle_dialoge`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem, QMessageBox, QWidget
from writer.funktionen import ki as KD
from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import zeige_unter
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter import FormularGitter
from vcl.qt.widgets.bausteine.interaktion.felder.listen_leiste import ListenLeiste
from vcl.qt.widgets.bausteine.abstaende.mass import HOEHE_LISTE_ANBIETER, HOEHE_LISTE_MITTEL, RAND_KEIN
from vcl.qt.widgets.dialoge.ki.ki_modelle_dialoge_hilfen import AnbieterDialog


def _tags_text(a: dict) -> str:
    n = dict(KD.anbieter_tags())
    return ", ".join(n[t] for t in a.get("verwendungFuer", []) if t in n)


class ModellListe(QWidget):
    """Die Liste der verbundenen KI-Modelle: hinzufügen, bearbeiten, entfernen (im Fenster „KI-Einstellungen“ und als eigenes Fenster)."""

    def __init__(self, fenster, konfig):
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
            teile = [a["modell"], _tags_text(a), "Lokaler Anbieter" if KD.ist_lokale_url(a["url"]) else "Über das Internet"]
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
