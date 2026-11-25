"""Umbruchregeln eines Absatzes (Witwen/Waisen, Absatz zusammenhalten, mit dem nächsten Absatz zusammen), ohne Qt: die eine Stelle, die der Qt-freie Seitenumbruch (``seitenumbruch.py``)
und der Seitenlauf (``editor/layout/seitenlauf.py``) beide nutzen."""
from __future__ import annotations

from typing import Callable, Iterable


def umbruch_stelle(hs: list[float], regeln: dict, rest: float, ganz: float, oben: bool, folge: Callable[[], Iterable[tuple[dict, list[float], float]]]) -> int | None:
    """Vor welcher Zeile (0 = vor dem ganzen Absatz) beginnt die nächste Spalte oder Seite, damit die Regeln gelten? ``None``: kein Umbruch nötig.

    ``hs``: Höhen der Zeilen des Absatzes; ``regeln``: ``kontrolle``, ``nicht_trennen``, ``zusammen``; ``rest``: Platz, der in der Spalte noch bleibt; ``ganz``: Höhe einer ganzen Spalte;
    ``oben``: steht der Absatz am Anfang der Spalte (dann bringt ein Umbruch nichts); ``folge()``: liefert die folgenden Absätze als (Regeln, Höhen der ersten Zeilen, Abstand oben)."""
    gesamt = sum(hs)
    n = len(hs)
    if n == 0:
        return None
    passt_ganz = gesamt <= rest + 0.01
    if regeln["nicht_trennen"] and not oben:                         # mit dem Anfang des nächsten Absatzes zusammen auf einer Seite (auch über mehrere solcher Absätze)
        noetig, tiefe, w_b = gesamt, 0, regeln
        for nb_regeln, hn, nb_oben in folge():
            if not (w_b["nicht_trennen"] and tiefe < 4) or not hn:
                break
            w_b = nb_regeln
            nb = min(len(hn), 2 if w_b["kontrolle"] and len(hn) >= 2 else 1)
            noetig += nb_oben + sum(hn[:nb])
            tiefe += 1
        if noetig > rest + 0.01 and gesamt <= ganz:
            return 0
    if passt_ganz:
        return None
    if regeln["zusammen"] and gesamt <= ganz and not oben:
        return 0
    k, acc = 0, 0.0
    for h in hs:
        if acc + h > rest + 0.01:
            break
        acc += h
        k += 1
    if regeln["kontrolle"] and n >= 2:
        if k < 2 and not oben:
            return 0 if k < n else None                               # ein Schusterjunge: der Absatz beginnt auf der nächsten Seite
        if 0 < n - k < 2:                                               # ein Hurenkind: die vorletzte Zeile geht mit hinüber
            k = n - 2
            if k < 2:
                return 0 if not oben else None
    return k if 0 < k < n else (0 if k == 0 and not oben and n > 0 and gesamt > rest else None)
