"""Zellenverbund: aus ``core.tabellen.modell.tabellenbearbeitung`` herausgelöst."""
from __future__ import annotations
import dataclasses
from core.dokument.dokument import Absatz, Zelle
from core.bearbeitung.verlauf import BearbeitungsFehler


def _anker(gitter: list):
    for z, zeile in enumerate(gitter):
        for s, c in enumerate(zeile):
            if c is not None and c.verdeckt_von is None:
                yield z, s, c


def verbinden(gitter: list, zeile: int, spalte: int, zeilen: int, spalten: int) -> tuple:
    """Verbindet das Rechteck zu einer Zelle. Gibt (Gitter, weggefallene leere Absätze) zurück."""
    if zeilen < 1 or spalten < 1 or zeile < 0 or spalte < 0 or zeile + zeilen > len(gitter) or spalte + spalten > len(gitter[0]):
        raise BearbeitungsFehler("Der Zellbereich liegt nicht in der Tabelle")
    g = [list(z) for z in gitter]
    inhalt: list = []
    weg: list = []
    for z, s, c in list(_anker(g)):
        drin_z = zeile <= z and z + c.zeilenspanne <= zeile + zeilen
        drin_s = spalte <= s and s + c.spaltenspanne <= spalte + spalten
        beruehrt = z < zeile + zeilen and z + c.zeilenspanne > zeile and s < spalte + spalten and s + c.spaltenspanne > spalte
        if not beruehrt:
            continue
        if not (drin_z and drin_s):
            raise BearbeitungsFehler("Der Bereich schneidet eine verbundene Zelle")
        if ist_leer(c):
            weg += c.bloecke
        else:
            inhalt += c.bloecke
        if (z, s) != (zeile, spalte):
            g[z][s] = None
    erste = g[zeile][spalte]
    if erste is None or erste.verdeckt_von is not None:
        raise BearbeitungsFehler("Der Bereich schneidet eine verbundene Zelle")
    if not inhalt:
        inhalt, weg = list(erste.bloecke), [b for b in weg if b not in erste.bloecke]
    g[zeile][spalte] = dataclasses.replace(erste, bloecke=inhalt, zeilenspanne=zeilen, spaltenspanne=spalten)
    return g, weg


def ist_leer(zelle: Zelle) -> bool:
    return len(zelle.bloecke) == 1 and isinstance(zelle.bloecke[0], Absatz) and zelle.bloecke[0].laenge == 0


def _aufteilung(gesamt: int, teile_: int) -> list:
    grund, rest = divmod(gesamt, teile_)
    return [grund + (1 if i < rest else 0) for i in range(teile_)]
