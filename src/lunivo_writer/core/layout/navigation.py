"""Bewegung der Schreibmarke auf dem gesetzten Dokument: Zeichen, Wort, Zeile, Zeilenanfang/-ende, Seite, Dokumentanfang/-ende; Wortgrenzen. Ohne Qt,
verändert weder das Ergebnis der Layoutberechnung noch das Dokument."""
from __future__ import annotations

from lunivo_writer.core.dokument.dokument import Position
from lunivo_writer.core.geometrie import Point, Rect
from .ergebnis import Ergebnis

ZEILENENDE = " \n "                # Zeichen am Zeilenende, hinter die die Schreibmarke in der Zeile nicht tritt
BEWEGUNGEN = ("links", "rechts", "hoch", "runter", "zeilenanfang", "zeilenende", "anfang", "ende", "wort_links", "wort_rechts", "seite_hoch", "seite_runter")


def _zeile(erg: Ergebnis, pos: Position):
    """(Seite, Zeilenindex im Satz, Rechteck) der Zeile, in der die Stelle steht."""
    ort = erg.absaetze.get(pos.absatz_id)
    if ort is None or not ort.zeilen:
        return None
    zi = ort.satz.zeile_von(pos.versatz)
    return next(((s, z, r) for s, z, r in ort.zeilen if z == zi), ort.zeilen[-1])


def _zeilen_der_seite(erg: Ergebnis, seite: int) -> list:
    return [p for p in erg.seiten[seite].plaetze if p.art == "zeile" and not p.kopie] if 0 <= seite < len(erg.seiten) else []


def _stelle_in(erg: Ergebnis, platz, x: float) -> Position:
    satz = erg.absaetze[platz.block_id].satz
    return Position(platz.block_id, satz.treffer(x - platz.rect.x, satz.zeilen[platz.zeile].y + 0.1))


def _senkrecht(erg: Ergebnis, seite: int, r: Rect, x: float, runter: bool):
    """Die Stelle in der nächsten Zeile unter (über) der Zeile ``r``: zuerst eine Zeile, über der x liegt (dieselbe Spalte oder Zelle), sonst die
    nächstgelegene; am Seitenrand die Nachbarseite."""
    def kandidaten(s: int, alle: bool):
        for p in _zeilen_der_seite(erg, s):
            if alle or (p.rect.y >= r.bottom - 0.5 if runter else p.rect.bottom <= r.y + 0.5):
                yield p

    def wahl(liste: list):
        if not liste:
            return None
        ueber = [p for p in liste if p.rect.x - 0.5 <= x <= p.rect.right + 0.5] or liste
        return min(ueber, key=lambda p: ((p.rect.y if runter else -p.rect.bottom), max(p.rect.x - x, 0.0, x - p.rect.right)))
    best = wahl(list(kandidaten(seite, False)))
    s = seite
    while best is None and 0 <= (s := s + (1 if runter else -1)) < len(erg.seiten):
        best = wahl(list(kandidaten(s, True)))
    return _stelle_in(erg, best, x) if best is not None else None


def _wortgrenze(text: str, i: int, vor: bool) -> int:
    """Die nächste Wortgrenze rechts (``vor``) oder links von ``i`` im Text eines Absatzes."""
    def wort(c: str) -> bool:
        return c.isalnum() or c == "_"
    if vor:
        while i < len(text) and not wort(text[i]):
            i += 1
        while i < len(text) and wort(text[i]):
            i += 1
        return i
    while i > 0 and not wort(text[i - 1]):
        i -= 1
    while i > 0 and wort(text[i - 1]):
        i -= 1
    return i


def wort_bei(erg: Ergebnis, pos: Position) -> tuple:
    """Anfang und Ende des Wortes an der Stelle (für den Doppelklick)."""
    text = erg.absaetze[pos.absatz_id].satz.text
    i = min(pos.versatz, len(text))
    a = i
    while a > 0 and (text[a - 1].isalnum() or text[a - 1] == "_"):
        a -= 1
    e = i
    while e < len(text) and (text[e].isalnum() or text[e] == "_"):
        e += 1
    return Position(pos.absatz_id, a), Position(pos.absatz_id, e)


def bewegen(erg: Ergebnis, pos: Position, art: str, x: float | None = None) -> tuple:
    """Die Stelle nach der Bewegung ``art`` (siehe ``BEWEGUNGEN``) und der gemerkte x-Wert: bei „hoch“/„runter“ und Seitenwechsel bleibt die
    Schreibmarke in ihrer Spalte (``x``, Seitenkoordinaten), jede andere Bewegung vergisst ihn. Am Dokumentrand bleibt die Stelle stehen."""
    liste = erg.reihenfolge
    if not liste or pos.absatz_id not in erg.absaetze:
        return pos, None
    satz = erg.absaetze[pos.absatz_id].satz
    i = liste.index(pos.absatz_id) if pos.absatz_id in liste else 0
    n = len(satz.text)
    if satz.basis == 1 and art in ("links", "rechts", "wort_links", "wort_rechts"):       # in Text rechts nach links zeigen die Pfeile zur Anzeigeseite
        art = {"links": "rechts", "rechts": "links", "wort_links": "wort_rechts", "wort_rechts": "wort_links"}[art]
    if art == "links":
        if pos.versatz > 0:
            return Position(pos.absatz_id, pos.versatz - 1), None
        return (Position(liste[i - 1], len(erg.absaetze[liste[i - 1]].satz.text)), None) if i > 0 else (pos, None)
    if art == "rechts":
        if pos.versatz < n:
            return Position(pos.absatz_id, pos.versatz + 1), None
        return (Position(liste[i + 1], 0), None) if i + 1 < len(liste) else (pos, None)
    if art == "wort_links":
        if pos.versatz > 0:
            return Position(pos.absatz_id, _wortgrenze(satz.text, pos.versatz, False)), None
        return bewegen(erg, pos, "links")
    if art == "wort_rechts":
        if pos.versatz < n:
            return Position(pos.absatz_id, _wortgrenze(satz.text, pos.versatz, True)), None
        return bewegen(erg, pos, "rechts")
    if art == "anfang":
        return Position(liste[0], 0), None
    if art == "ende":
        return Position(liste[-1], len(erg.absaetze[liste[-1]].satz.text)), None
    z = _zeile(erg, pos)
    if z is None:
        return pos, None
    seite, zi, r = z
    zeile = satz.zeilen[zi]
    if art == "zeilenanfang":
        return Position(pos.absatz_id, zeile.box.start), None
    if art == "zeilenende":
        ende = zeile.ende
        if ende > zeile.box.start and zi < len(satz.zeilen) - 1 and satz.text[ende - 1] in ZEILENENDE:
            ende -= 1
        return Position(pos.absatz_id, ende), None
    x = r.x + satz.cursor_x(pos.versatz, zi) if x is None else x
    if art in ("hoch", "runter"):
        ziel = _senkrecht(erg, seite, r, x, art == "runter")
        return (ziel, x) if ziel is not None else (pos, x)
    if art in ("seite_hoch", "seite_runter"):
        s = seite + (1 if art == "seite_runter" else -1)
        if not 0 <= s < len(erg.seiten):
            return bewegen(erg, pos, "ende" if art == "seite_runter" else "anfang")
        t = erg.treffer(s, Point(x, r.y + r.height / 2))
        return (Position(t[0], t[1]), x) if t is not None else (pos, x)
    raise ValueError(f"unbekannte Bewegung {art!r}")
