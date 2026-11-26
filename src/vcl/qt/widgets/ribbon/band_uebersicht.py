"""Gruppenübersicht und Gruppendetail eines Reiters im Menüband.

Ein Reiter mit Übersicht zeigt zuerst je Gruppe ein Icon. Ein Klick tauscht an derselben Stelle die Übersicht gegen die Befehle dieser Gruppe
(die unveränderten Knöpfe, Klappen und Felder) und blendet „Zurück“ ein. Es entsteht keine zweite Leiste und kein Popup; die Reiterauswahl bleibt stehen."""
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QToolButton, QWidget

from vcl.qt.widgets.bausteine.interaktion.knopf import werkzeugknopf
from vcl.qt.widgets.bausteine.zustaende.geruest import reihe, spalte
from vcl.qt.widgets.ribbon.band_bausteine import _GruppenTrenner
from writer.werkzeugleisten.gruppen import kacheln, uebersicht


@dataclass
class _Ansicht:
    """Die Teile einer Reiterseite mit Übersicht; ``offen`` ist die gezeigte Gruppe (``None``: Gruppenübersicht)."""
    seite: QScrollArea
    kopf: QWidget
    titel: QLabel
    trenner: QWidget
    kacheln: QWidget
    gruppen: list[QWidget]
    namen: list[str]
    offen: int | None = None


class BandUebersichtBaustein:
    """Baut die Gruppenübersicht eines Reiters und wechselt zwischen Übersicht und Gruppendetail."""

    def _uebersicht_bauen(self, i: int, seite: QScrollArea, zeile, r: dict) -> None:
        """Die Seite des Reiters ``i``: „Zurück“ mit dem Gruppennamen, die Gruppen-Icons und jede Gruppe mit ihren Befehlen (zunächst verborgen)."""
        kopf = QWidget()
        v = spalte("eng", kopf)
        v.addWidget(werkzeugknopf("band_zurueck", "Zurück", symbol="zurueck", tooltip="Zurück zur Gruppenübersicht",
                                  aktion=lambda: self.gruppe_zeigen(i, None)))
        titel = QLabel()
        schrift = titel.font()
        schrift.setBold(True)                              # der Name der offenen Gruppe: fett, damit man sieht, wo man ist
        titel.setFont(schrift)
        v.addWidget(titel)
        v.addStretch(1)
        kacheln = QWidget()
        kh = reihe("leiste", kacheln)
        eintraege = uebersicht(r)
        gruppen = []
        for n, (g, e) in enumerate(zip(r["gruppen"], eintraege)):
            icon = werkzeugknopf("band_gruppe", e["name"].replace("&", "&&"), symbol=e["symbol"] or None, symbolgroesse="knopf_gross", symbol_einpassen=True,
                                 tooltip=e["name"] + " öffnen", name=e["name"], aktion=lambda n=n: self.gruppe_zeigen(i, n))
            kh.addWidget(icon)
            gruppen.append(self._kachelgruppe(g, icon.minimumWidth()))
        kh.addStretch(1)
        trenner = _GruppenTrenner()
        for w in (kopf, trenner, kacheln, *gruppen):
            zeile.addWidget(w)
        self._ansichten[i] = _Ansicht(seite, kopf, titel, trenner, kacheln, gruppen, [e["name"] for e in eintraege])
        self.gruppe_zeigen(i, None)

    def _kachelgruppe(self, g: dict, breite: int) -> QWidget:
        """Die Befehle der Gruppe als gleich breite Kacheln nebeneinander (Symbol oben, Text darunter) – dieselben Knöpfe mit Befehl, Klappe und Zustand."""
        w = self._gruppe(kacheln(g))
        for k in w.findChildren(QToolButton):
            if k.toolButtonStyle() == Qt.ToolButtonTextUnderIcon:
                k.setMinimumWidth(max(k.minimumWidth(), breite))     # nie schmaler als ein Gruppen-Icon: ruhige, gleichmäßige Reihe
        return w

    def gruppe_zeigen(self, i: int, nummer: int | None) -> None:
        """Im Reiter ``i`` die Gruppe ``nummer`` zeigen; ``None`` stellt die Gruppenübersicht wieder her. Am Dokument ändert sich nichts."""
        a = self._ansichten.get(i)
        if a is None:
            return
        a.offen = nummer
        offen = nummer is not None
        a.kacheln.setVisible(not offen)
        a.kopf.setVisible(offen)
        a.trenner.setVisible(offen)
        for n, w in enumerate(a.gruppen):
            w.setVisible(n == nummer)
        if offen:
            a.titel.setText(a.namen[nummer])
        a.seite.horizontalScrollBar().setValue(0)

    def offene_gruppe(self, i: int) -> int | None:
        """Die im Reiter ``i`` gezeigte Gruppe (``None``: Gruppenübersicht oder Reiter ohne Übersicht)."""
        a = self._ansichten.get(i)
        return a.offen if a is not None else None
