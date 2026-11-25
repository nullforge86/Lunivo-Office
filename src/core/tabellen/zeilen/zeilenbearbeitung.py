"""Zeilenbearbeitung: aus ``core.tabellen.modell.tabellenbearbeitung`` herausgelöst."""
from __future__ import annotations
import dataclasses
from core.tabellen.zellen.zellenverbund import _anker


def zeilen_einfuegen(gitter: list, index: int, anzahl: int) -> list:
    g = [list(zeile) for zeile in gitter]
    for z, s, c in list(_anker(g)):
        if z < index < z + c.zeilenspanne:
            g[z][s] = dataclasses.replace(c, zeilenspanne=c.zeilenspanne + anzahl)
    spalten = len(g[0])
    g[index:index] = [[None] * spalten for _ in range(anzahl)]
    return g


def zeilen_loeschen(gitter: list, index: int, anzahl: int) -> list:
    g = [list(zeile) for zeile in gitter]
    ende = index + anzahl
    for z, s, c in list(_anker(g)):
        unten = z + c.zeilenspanne
        if z < index and unten > index:
            g[z][s] = dataclasses.replace(c, zeilenspanne=c.zeilenspanne - (min(unten, ende) - index))
        elif index <= z < ende and unten > ende:             # die Zelle beginnt in einer gelöschten Zeile und reicht darunter
            g[ende][s] = dataclasses.replace(c, zeilenspanne=unten - ende)
    del g[index:ende]
    return g


def zeilen_dehnen(gitter: list, index: int, anzahl: int) -> list:
    """Fügt Zeilen ein, die keine neuen Zellen bringen: Jede Zelle, die bis zur Zeile ``index - 1`` reicht, wird höher."""
    g = [list(zeile) for zeile in gitter]
    gesehen = set()
    for s in range(len(g[0])):
        c = g[index - 1][s]
        z0, s0 = c.verdeckt_von or (index - 1, s)
        if (z0, s0) not in gesehen:
            gesehen.add((z0, s0))
            g[z0][s0] = dataclasses.replace(g[z0][s0], zeilenspanne=g[z0][s0].zeilenspanne + anzahl)
    g[index:index] = [[None] * len(g[0]) for _ in range(anzahl)]
    return g
