"""Ansichtswahl der Statusleiste: je Dokumentansicht ein Symbolknopf (Drucklayout, Gliederung, Lesemodus, Weblayout); genau einer ist gedrückt.
Welche Ansichten es gibt, steht Qt-frei in ``writer.funktionen.ansicht``; die Knöpfe melden nur die gewählte Kennung."""
from __future__ import annotations

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QButtonGroup, QToolButton

from vcl.qt.widgets.bausteine.interaktion.knopf import werkzeugknopf
from writer.funktionen.ansicht import ANSICHTSARTEN


class Ansichtswahl(QObject):
    gewaehlt = Signal(str)                # Kennung der gewählten Ansicht

    def __init__(self, eltern: QObject | None = None):
        super().__init__(eltern)
        self._gruppe = QButtonGroup(self)
        self._gruppe.setExclusive(True)
        self.knoepfe: dict[str, QToolButton] = {}
        for art in ANSICHTSARTEN:
            k = werkzeugknopf("standard", symbol=art.symbol, tooltip=art.hinweis, name=art.name, umschaltbar=True, symbol_merken=True,
                              aktion=lambda kennung=art.kennung: self.gewaehlt.emit(kennung))
            self._gruppe.addButton(k)
            self.knoepfe[art.kennung] = k

    def zeigen(self, kennung: str) -> None:
        """Drückt den Knopf der geltenden Ansicht, ohne eine Aktion auszulösen."""
        k = self.knoepfe.get(kennung)
        if k is not None:
            k.setChecked(True)
