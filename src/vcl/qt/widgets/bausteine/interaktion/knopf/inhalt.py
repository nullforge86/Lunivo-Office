"""Inhalt des Knopfes: Beschriftung, Symbol, Quickinfo und Name für die Bedienungshilfen – unabhängig von seiner Form und seinem Verhalten."""
from __future__ import annotations

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QAbstractButton

from vcl.qt.widgets.bausteine.farben.darstellung import eigenschaft
from vcl.qt.widgets.bausteine.abstaende.mass import ICON_GROSS, ICON_KLEIN, ICON_KNOPF_GROSS, ICON_MITTEL, ICON_NORMAL
from vcl.qt.widgets.bausteine.symbole.bauteile import symbole

SYMBOLGROESSEN = {"klein": ICON_KLEIN, "normal": ICON_NORMAL, "mittel": ICON_MITTEL, "gross": ICON_GROSS,      # Name → Kantenlänge des Symbols
                  "knopf_gross": ICON_KNOPF_GROSS}                                                              # Gruppen-Icon im Band


def beschriften(knopf: QAbstractButton, text: str = "", symbol: str | None = None, tooltip: str = "", name: str = "",
                symbolgroesse: str = "normal", symbolfarbe: str | None = None, symbol_einpassen: bool = False, symbolbild: QIcon | None = None,
                bildgroesse: QSize | None = None, symbol_merken: bool = False, objektname: str = "", rolle: str = "") -> QAbstractButton:
    """Setzt Text (mit ``&`` für das Tastenkürzel), Symbol (Name aus dem Symbolsatz, Größe nach ``SYMBOLGROESSEN``, auf Wunsch in fester Farbe), Quickinfo und den Namen
    für Bedienungshilfen. ``symbol_einpassen`` setzt auch die Anzeigegröße des Symbols; ``symbolbild`` (mit ``bildgroesse``) nimmt ein fertiges Bild statt eines Namens.
    ``symbol_merken``: das Symbol wird beim Wechsel hell/dunkel neu bezogen (``symbole.setze``); ``objektname`` und ``rolle`` bestimmen das Aussehen im Thema."""
    if text:
        knopf.setText(text)
    if objektname:
        knopf.setObjectName(objektname)
    if rolle:
        eigenschaft(knopf, rolle=rolle)
    if symbol:
        px = SYMBOLGROESSEN[symbolgroesse] if isinstance(symbolgroesse, str) else symbolgroesse      # Name der Größe oder ein benanntes Maß aus ``basis/mass``
        if symbol_merken:
            symbole.setze(knopf, symbol, px)
        else:
            knopf.setIcon(symbole.icon(symbol, px, symbolfarbe) if symbolfarbe else symbole.icon(symbol, px))
        if symbol_einpassen:
            knopf.setIconSize(QSize(px, px))
    if symbolbild is not None:
        knopf.setIcon(symbolbild)
        if bildgroesse is not None:
            knopf.setIconSize(bildgroesse)
    if tooltip:
        knopf.setToolTip(tooltip)
    knopf.setAccessibleName(name or tooltip or text.replace("&", ""))
    return knopf
