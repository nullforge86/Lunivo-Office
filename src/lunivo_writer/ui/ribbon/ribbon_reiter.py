"""Reiter-, Seiten- und Kontextnavigation des Menübands."""
from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QFrame, QHBoxLayout, QWidget

from lunivo_writer.ui.ribbon.plan import plan
from lunivo_writer.ui.baukasten.mass import RAND_BANDREITER
from lunivo_writer.ui.ribbon.ribbon_bausteine import (
    STANDARD_VERSTECKT, _BandSeite, _GruppenTrenner,
)


class BandReiterBaustein:
    """Verwaltet Menüband-Reiter, Seitenaufbau und Kontextregister."""

    def _reiter_gewaehlt(self, i: int) -> None:
        self._seite_bauen(i)
        self.stapel.setCurrentIndex(i)

    def _seite_bauen(self, i: int) -> None:
        eintrag = self._offen.pop(i, None)
        if eintrag is None:
            return
        scroll, r = eintrag
        seite = QWidget()
        h = QHBoxLayout(seite)
        h.setContentsMargins(*RAND_BANDREITER)
        h.setSpacing(0)
        for n, g in enumerate(r["gruppen"]):
            if n:
                h.addWidget(_GruppenTrenner())
            h.addWidget(self._gruppe(g))
        h.addStretch(1)
        scroll.setWidget(seite)
        self.aktualisieren(self._hat_dok)                  # Zustand (aktiv/Haken) auch für die neuen Knöpfe

    def _alle_bauen(self) -> None:
        for i in list(self._offen):
            self._seite_bauen(i)

    def _im_leerlauf_bauen(self) -> None:
        """Nach dem Anzeigen: je Durchlauf einen Reiter bauen, damit die Oberfläche dazwischen bedienbar bleibt."""
        try:
            if self._offen:
                self._seite_bauen(next(iter(self._offen)))
            if self._offen:
                QTimer.singleShot(0, self._im_leerlauf_bauen)
        except RuntimeError:                                    # Band wurde inzwischen abgebaut
            pass

    def _reiter_geklickt(self, _i):
        if self._eingeklappt:
            self._eingeklappt = False
            self.stapel.setVisible(True)

    def einklappen_umschalten(self):
        if not self.einklappbar:
            return
        self._eingeklappt = not self._eingeklappt
        self.stapel.setVisible(not self._eingeklappt)

    def _plan_angepasst(self) -> list[dict]:
        """Reiter in der Reihenfolge der Struktur — ausgeblendete weglassen, eigene Reihenfolge beachten (Register anpassen)."""
        alle = plan(self.daten)
        haupt = [r for r in alle if not r.get("kontext")]
        kontext = [r for r in alle if r.get("kontext")]
        ordnung = self.cfg.get("reihenfolge") or []
        versteckt = set(self.cfg["versteckt"] if "versteckt" in self.cfg else STANDARD_VERSTECKT) - {"Datei"}
        haupt.sort(key=lambda r: ordnung.index(r["name"]) if r["name"] in ordnung else 999)
        return [r for r in haupt if r["name"] not in versteckt] + kontext

    def _reiter(self, r: dict):
        scroll = _BandSeite()
        scroll.setObjectName("bandSeite")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.stapel.addWidget(scroll)
        i = self.reiter.addTab(r["name"])
        self._offen[i] = (scroll, r)                              # Inhalt wird beim ersten Wählen oder im Leerlauf gebaut
        if r.get("kontext"):
            if r["kontext"] in self.kontext_index:
                self.kontext_weitere.setdefault(r["kontext"], []).append(i)
            else:
                self.kontext_index[r["kontext"]] = i
            self.reiter.setTabVisible(i, False)
            self.reiter.setTabData(i, "kontext")

    def kontext(self, name: str, sichtbar: bool, aktivieren: bool = False) -> None:
        """Kontext-Register (Tabellentools, Bildtools …) ein- oder ausblenden; ``aktivieren``: gleich öffnen."""
        i = self.kontext_index.get(name)
        if i is None:
            return
        alle = (i, *self.kontext_weitere.get(name, ()))              # die weiteren Reiter des Kontexts folgen dem ersten
        if sichtbar and aktivieren:
            for j in alle:
                self.reiter.setTabVisible(j, True)
            self.reiter.setCurrentIndex(i)
            return
        if self.reiter.isTabVisible(i) == sichtbar:
            return
        war_aktiv = self.reiter.currentIndex() in alle                 # Qt springt beim Ausblenden selbst zu einem Nachbarn: vorher merken
        for j in alle:
            self.reiter.setTabVisible(j, sichtbar)
        if not sichtbar and war_aktiv:
            self.reiter.setCurrentIndex(self._start_index())

    def _start_index(self) -> int:
        for i in range(self.reiter.count()):
            if self.reiter.tabText(i) == "Start":
                return i
        return 0
