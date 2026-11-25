"""Schreibmarke und Auswahl auf dem gesetzten Dokument, ohne Qt: wo die Schreibmarke steht, welche Flächen eine Auswahl bedeckt und wohin eine
Bewegung (Zeichen, Wort, Zeile, Zeilenanfang/-ende, Seite, Dokumentanfang/-ende) führt. Arbeitet nur auf dem ``Ergebnis`` der Layoutberechnung
und auf ``Position`` des Dokumentmodells; verändert weder das eine noch das andere."""
from __future__ import annotations

from lunivo_writer.kern.dokument.dokument import Auswahl, Position
from lunivo_writer.kern.geometrie import Point, Rect
from .ergebnis import Ergebnis
from .navigation import BEWEGUNGEN, ZEILENENDE, _zeile, bewegen, wort_bei  # noqa: F401  (Navigation steht in navigation.py)

CURSOR_BREITE = 1.5                     # Breite der Schreibmarke in Bildpunkten
ABSATZENDE_BREITE = 6.0                 # so breit zeigt die Auswahl ein mitgewähltes Absatzende


def cursor_rechteck(erg: Ergebnis, pos: Position):
    """(Seitenindex, Rechteck der Schreibmarke in Seitenkoordinaten) oder ``None``, wenn der Absatz nicht gesetzt ist."""
    z = _zeile(erg, pos)
    if z is None:
        return None
    seite, zi, r = z
    return seite, Rect(r.x + erg.absaetze[pos.absatz_id].satz.cursor_x(pos.versatz, zi), r.y, CURSOR_BREITE, r.height)


def auswahl_rechtecke(erg: Ergebnis, auswahl: Auswahl) -> dict:
    """Seitenindex → Flächen der Auswahl (je Zeile ein Rechteck; ein mitgewähltes Absatzende zeigt sich als schmales Stück hinter der letzten Zeile)."""
    rang = {aid: i for i, aid in enumerate(erg.reihenfolge)}
    von, bis = auswahl
    if rang.get(von.absatz_id, -1) > rang.get(bis.absatz_id, -1) or (von.absatz_id == bis.absatz_id and von.versatz > bis.versatz):
        von, bis = bis, von
    aus: dict = {}
    if von.absatz_id not in rang or bis.absatz_id not in rang:
        return aus
    for aid in erg.reihenfolge[rang[von.absatz_id]:rang[bis.absatz_id] + 1]:
        ort = erg.absaetze[aid]
        satz = ort.satz
        a = von.versatz if aid == von.absatz_id else 0
        e = bis.versatz if aid == bis.absatz_id else len(satz.text)
        letzte = len(satz.zeilen) - 1
        for seite, zi, r in ort.zeilen:
            z = satz.zeilen[zi]
            s, t = max(a, z.box.start), min(e, z.ende)
            mit_ende = aid != bis.absatz_id and zi == letzte
            if s > t or (s == t and not mit_ende):
                continue
            streifen = satz.auswahl_x(s, t, zi)
            if mit_ende:                                                    # das mitgewählte Absatzende liegt am Zeilenende (rechts, bei rechts nach links links)
                if streifen:
                    l, rr = streifen[-1] if satz.basis == 0 else streifen[0]
                    streifen[-1 if satz.basis == 0 else 0] = (l - ABSATZENDE_BREITE, rr) if satz.basis else (l, rr + ABSATZENDE_BREITE)
                else:
                    x = satz.cursor_x(t, zi)
                    streifen = [(x - ABSATZENDE_BREITE, x) if satz.basis else (x, x + ABSATZENDE_BREITE)]
            for x1, x2 in streifen:
                if x2 > x1:
                    aus.setdefault(seite, []).append(Rect(r.x + x1, r.y, x2 - x1, r.height))
    return aus
