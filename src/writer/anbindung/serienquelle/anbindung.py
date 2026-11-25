"""Anbindung der Oberfläche an ``framework.serienbriefe.datenquellen.serienquelle``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.serienbriefe.datenquellen as _fw


def quelle_lesen(pfad: str):
    """Empfängerliste aus einer Textdatei (CSV mit ; oder , oder Tabulator; erste Zeile = Spaltennamen). → (Spalten, Sätze) oder None."""
    return _fw.quelle_lesen(pfad)


def tabelle_lesen(roh: str):
    return _fw.tabelle_lesen(roh)


def zugeordnet(satz: dict, zuordnung: dict) -> dict:
    """Satz mit den Namen der Felder im Text: ``zuordnung`` {Feld im Text: Spalte der Quelle}; ohne Eintrag gilt der gleiche Name."""
    return _fw.zugeordnet(satz, zuordnung)
