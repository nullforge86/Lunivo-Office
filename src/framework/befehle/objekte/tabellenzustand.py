"""Zustand der Schreibmarke gegenüber einer Tabelle: entscheidet, ob die Minileiste Tabellen- oder Textfunktionen anbietet.

Die Regel liegt in ``core.tabellen.modell.tabellenzustand``; maßgeblich sind die Auswahl der Bearbeitungssitzung und der Schreibschutz des
Dokuments, beides im Framework."""
from __future__ import annotations

from core.tabellen.modell import AUSSEN, EINZELZELLE_GANZ, GANZE_TABELLE, MEHRERE_ZELLEN
from core.tabellen.modell import tabellenmodus as _kern_modus, zustand as _kern_zustand
from framework.befehle import lesen
from framework.sitzungen import sitzung as _steuerung

TABELLE_GEWAEHLT: tuple[str, ...] = (MEHRERE_ZELLEN, GANZE_TABELLE, EINZELZELLE_GANZ)     # Zellen als Ganzes markiert


def tabellen_zustand(kennung: int) -> str:
    """``aussen``, ``text_in_zelle``, ``mehrere_zellen``, ``ganze_tabelle``, ``einzelzelle_ganz`` oder ``nur_lesen``."""
    nur_lesen = _steuerung.ist_nur_lesen(kennung)
    return lesen(kennung, lambda s: _kern_zustand(s, nur_lesen)) or AUSSEN


def tabellenmodus(kennung: int, rechtsklick: bool = False, per_griff: bool = False) -> bool:
    """``True``, wenn Tabellenfunktionen (Einfügen/Löschen, Rahmen, Schattierung …) angeboten werden."""
    nur_lesen = _steuerung.ist_nur_lesen(kennung)
    return bool(lesen(kennung, lambda s: int(_kern_modus(s, nur_lesen, rechtsklick, per_griff))))
