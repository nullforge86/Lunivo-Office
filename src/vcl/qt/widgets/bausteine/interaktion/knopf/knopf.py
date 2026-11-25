"""Der Knopf als Baustein: setzt Form (``form.py``), Inhalt (``inhalt.py``) und Verhalten (``verhalten.py``) zusammen. Jede Funktion baut ihre Knöpfe so – ein Knopf wird
nie in einer einzelnen Datei zusammengebastelt, und die Form wirkt überall gleich.

    knopf("gross", "&Alle", aktion=self._alle)                     # Druckknopf mit Text
    werkzeugknopf("symbol", symbol="plus", tooltip="Neu", aktion=neu)   # Symbolknopf"""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QPushButton, QToolButton, QWidget

from vcl.qt.widgets.bausteine.interaktion.knopf.form import formen
from vcl.qt.widgets.bausteine.interaktion.knopf.inhalt import beschriften
from vcl.qt.widgets.bausteine.interaktion.knopf.verhalten import verbinden


def knopf(form: str = "standard", text: str = "", *, symbol: str | None = None, symbolgroesse: str = "normal", aktion: Callable[[], object] | None = None,
          tooltip: str = "", name: str = "", aktiv: bool = True, kuerzel: str = "", standard: bool = False, umschaltbar: bool = False, an: bool = False,
          hand: bool = False, ohne_rand: bool = False, symbol_einpassen: bool = False, symbol_merken: bool = False, objektname: str = "", rolle: str = "",
          eltern: QWidget | None = None) -> QPushButton:
    """Druckknopf aus Form, Inhalt und Verhalten."""
    k = QPushButton(eltern)
    formen(k, form, None, ohne_rand)
    beschriften(k, text, symbol, tooltip, name, symbolgroesse, None, symbol_einpassen, None, None, symbol_merken, objektname, rolle)
    verbinden(k, aktion, aktiv, kuerzel, standard, umschaltbar, an, hand)
    return k


def werkzeugknopf(form: str = "symbol", text: str = "", *, symbol: str | None = None, symbolgroesse: str = "normal", symbolfarbe: str | None = None,
                  symbol_einpassen: bool = False, symbolbild: QIcon | None = None, bildgroesse: QSize | None = None, groesse: tuple[int, int] | None = None,
                  aktion: Callable[[], object] | None = None, tooltip: str = "", name: str = "", aktiv: bool = True, kuerzel: str = "",
                  umschaltbar: bool = False, an: bool = False, hand: bool = False, flach: bool = True, symbol_merken: bool = False, objektname: str = "",
                  rolle: str = "", eltern: QWidget | None = None) -> QToolButton:
    """Werkzeugknopf (flach, meist nur Symbol) aus Form, Inhalt und Verhalten. ``flach=False``: ohne Hervorhebung beim Überfahren (``autoRaise`` aus)."""
    k = QToolButton(eltern)
    k.setAutoRaise(flach)
    formen(k, form, groesse)
    beschriften(k, text, symbol, tooltip, name, symbolgroesse, symbolfarbe, symbol_einpassen, symbolbild, bildgroesse, symbol_merken, objektname, rolle)
    verbinden(k, aktion, aktiv, kuerzel, False, umschaltbar, an, hand)
    return k
