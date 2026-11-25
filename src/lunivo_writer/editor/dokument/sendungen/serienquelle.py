"""Datenquelle des Seriendrucks: Empfängerliste aus Text lesen und Spalten den Feldern im Text zuordnen."""
from __future__ import annotations

import re


def tabelle_lesen(roh: str):
    zeilen = [z for z in re.split(r"\r?\n", roh) if z.strip()]
    if len(zeilen) < 2:
        return None
    tr = "\t" if "\t" in zeilen[0] else (";" if ";" in zeilen[0] else ",")
    spalten = [s.strip() for s in zeilen[0].split(tr)]
    saetze = []
    for z in zeilen[1:]:
        w = [x.strip() for x in z.split(tr)]
        saetze.append({n: (w[i] if i < len(w) else "") for i, n in enumerate(spalten)})
    return spalten, saetze


def quelle_lesen(pfad: str):
    """Empfängerliste aus einer Textdatei (CSV mit ; oder , oder Tabulator; erste Zeile = Spaltennamen). → (Spalten, Sätze) oder None."""
    for enc in ("utf-8-sig", "cp1252"):
        try:
            with open(pfad, encoding=enc) as fh:
                return tabelle_lesen(fh.read())
        except UnicodeDecodeError:
            continue
    return None


def zugeordnet(satz: dict, zuordnung: dict) -> dict:
    """Satz mit den Namen der Felder im Text: ``zuordnung`` {Feld im Text: Spalte der Quelle}; ohne Eintrag gilt der gleiche Name."""
    aus = dict(satz)
    for feld, spalte in zuordnung.items():
        if spalte in satz:
            aus[feld] = satz[spalte]
    return aus
