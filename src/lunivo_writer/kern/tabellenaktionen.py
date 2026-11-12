"""Die Tabellenaktionen „Einfügen“ und „Löschen“ - eine gemeinsame Definition für Tabellentools, Mini-Leiste und Kontextmenü.

Reine Daten (keine Qt-Widgets): ``name`` ist der angezeigte Text (wie in der Vorlage), ``befehl`` der Befehlsname in ``kern/befehlsliste.py``
(``Befehle.<befehl>``), ``symbol`` der Name in ``ressourcen/icons/symbole.json``.

    for a in EINFUEGEN: ...        # a.name, a.befehl, a.symbol
    GRUPPEN                         # {"Einfügen": EINFUEGEN, "Löschen": LOESCHEN}
"""
from __future__ import annotations

from typing import NamedTuple


class Tabellenaktion(NamedTuple):
    name: str
    befehl: str
    symbol: str


EINFUEGEN = (
    Tabellenaktion("Zeile oberhalb einfügen", "tabelleZeileOben", "tabelleZeileOben"),
    Tabellenaktion("Zeile unterhalb einfügen", "tabelleZeileUnten", "tabelleZeileUnten"),
    Tabellenaktion("Spalte links einfügen", "tabelleSpalteLinks", "tabelleSpalteLinks"),
    Tabellenaktion("Spalte rechts einfügen", "tabelleSpalteRechts", "tabelleSpalteRechts"),
)

LOESCHEN = (
    Tabellenaktion("Zellen löschen …", "tabelleZellenLoeschen", "tabelleZellenLoeschen"),   # Symbol legt die Oberfläche an
    Tabellenaktion("Spalten löschen", "tabelleSpalteLoeschen", "tabelleSpalteLoeschen"),
    Tabellenaktion("Zeilen löschen", "tabelleZeileLoeschen", "tabelleZeileLoeschen"),
    Tabellenaktion("Tabelle löschen", "tabelleLoeschen", "tabelleLoeschen"),
)

GRUPPEN = {"Einfügen": EINFUEGEN, "Löschen": LOESCHEN}
