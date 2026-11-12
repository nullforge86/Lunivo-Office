"""Schreibmarke und Auswahl auf dem gesetzten Dokument, ohne Qt: wo die Schreibmarke steht, welche Flächen eine Auswahl bedeckt, und wohin eine Bewegung
(Zeichen, Wort, Zeile, Zeilenanfang/-ende, Seite, Dokumentanfang/-ende) führt. Arbeitet nur auf dem Ergebnis des Seitenumbruchs (``Ergebnis``) und Stellen (``Caret``)."""
from __future__ import annotations

from lunivo_writer.core.editing.sitzung import Caret
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.layout.seitenumbruch import Ergebnis

CURSOR_BREITE = 1.5                     # Breite der Schreibmarke in Bildpunkten
ABSATZENDE_BREITE = 6.0                 # so breit zeigt die Auswahl ein mitgewähltes Absatzende
ZEILENENDE = " \n "                # Zeichen am Zeilenende, hinter die die Schreibmarke in der Zeile nicht tritt
BEWEGUNGEN = ("links", "rechts", "hoch", "runter", "zeilenanfang", "zeilenende", "anfang", "ende", "wort_links", "wort_rechts", "seite_hoch", "seite_runter")


def pfade(erg: Ergebnis) -> list[tuple]:
    """Die Pfade aller gesetzten Absätze in Dokumentreihenfolge."""
    return sorted(k for k, v in erg.absaetze.items() if v.zeilen)


def _zeile(erg: Ergebnis, caret: Caret) -> tuple[int, int, Rect] | None:
    """(Seite, Zeilenindex im Satz, Rechteck) der Zeile, in der die Stelle steht."""
    ort = erg.absaetze.get(caret.pfad)
    if ort is None or not ort.zeilen:
        return None
    zi = ort.satz.zeile_von(caret.versatz)
    return next(((s, z, r) for s, z, r in ort.zeilen if z == zi), ort.zeilen[-1])


def cursor_rechteck(erg: Ergebnis, caret: Caret) -> tuple[int, Rect] | None:
    """(Seitenindex, Rechteck der Schreibmarke in Seitenkoordinaten) oder ``None``, wenn der Absatz nicht gesetzt ist."""
    z = _zeile(erg, caret)
    if z is None:
        return None
    seite, zi, r = z
    return seite, Rect(r.x + erg.absaetze[caret.pfad].satz.cursor_x(caret.versatz, zi), r.y, CURSOR_BREITE, r.height)


def auswahl_rechtecke(erg: Ergebnis, von: Caret, bis: Caret) -> dict[int, list[Rect]]:
    """Seitenindex → Flächen der Auswahl zwischen zwei Stellen (je Zeile ein Rechteck; ein mitgewähltes Absatzende zeigt sich als schmales Stück hinter der letzten Zeile)."""
    if bis < von:
        von, bis = bis, von
    aus: dict[int, list[Rect]] = {}
    for pfad in pfade(erg):
        if pfad < von.pfad or pfad > bis.pfad:
            continue
        ort = erg.absaetze[pfad]
        satz = ort.satz
        a = von.versatz if pfad == von.pfad else 0
        e = bis.versatz if pfad == bis.pfad else len(satz.text)
        letzte = len(satz.zeilen) - 1
        for seite, zi, r in ort.zeilen:
            z = satz.zeilen[zi]
            s, t = max(a, z.box.start), min(e, z.ende)
            mit_ende = pfad != bis.pfad and zi == letzte
            if s > t or (s == t and not mit_ende):
                continue
            x1 = r.x + satz.cursor_x(s, zi)
            x2 = r.x + satz.cursor_x(t, zi) + (ABSATZENDE_BREITE if mit_ende else 0.0)
            if x2 > x1:
                aus.setdefault(seite, []).append(Rect(x1, r.y, x2 - x1, r.height))
    return aus


def _zeilen_der_seite(erg: Ergebnis, seite: int) -> list:
    return [p for p in erg.seiten[seite].plaetze if p.art == "zeile" and not p.kopie] if 0 <= seite < len(erg.seiten) else []


def _stelle_in(erg: Ergebnis, platz, x: float) -> Caret:
    satz = erg.absaetze[platz.pfad].satz
    return Caret(platz.pfad, satz.treffer(x - platz.rect.x, satz.zeilen[platz.zeile].y + 0.1))


def _senkrecht(erg: Ergebnis, seite: int, r: Rect, x: float, runter: bool) -> Caret | None:
    """Die Stelle in der nächsten Zeile unter (über) der Zeile ``r``: zuerst eine Zeile, über der x liegt (dieselbe Spalte oder Zelle), sonst die nächstgelegene; am Seitenrand die Nachbarseite."""
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


def wort_bei(erg: Ergebnis, caret: Caret) -> tuple[Caret, Caret]:
    """Anfang und Ende des Wortes an der Stelle (für den Doppelklick)."""
    text = erg.absaetze[caret.pfad].satz.text
    i = min(caret.versatz, len(text))
    a = i
    while a > 0 and (text[a - 1].isalnum() or text[a - 1] == "_"):
        a -= 1
    e = i
    while e < len(text) and (text[e].isalnum() or text[e] == "_"):
        e += 1
    return Caret(caret.pfad, a), Caret(caret.pfad, e)


def bewegen(erg: Ergebnis, caret: Caret, art: str, x: float | None = None) -> tuple[Caret, float | None]:
    """Die Stelle nach der Bewegung ``art`` (siehe ``BEWEGUNGEN``) und der gemerkte x-Wert: bei „hoch“/„runter“ und Seitenwechsel bleibt die Schreibmarke in ihrer
    Spalte (``x``, Seitenkoordinaten), jede andere Bewegung vergisst ihn. Am Dokumentrand bleibt die Stelle stehen."""
    liste = pfade(erg)
    if not liste or caret.pfad not in erg.absaetze:
        return caret, None
    satz = erg.absaetze[caret.pfad].satz
    i = liste.index(caret.pfad) if caret.pfad in liste else 0
    n = len(satz.text)
    if art == "links":
        if caret.versatz > 0:
            return Caret(caret.pfad, caret.versatz - 1), None
        return (Caret(liste[i - 1], len(erg.absaetze[liste[i - 1]].satz.text)), None) if i > 0 else (caret, None)
    if art == "rechts":
        if caret.versatz < n:
            return Caret(caret.pfad, caret.versatz + 1), None
        return (Caret(liste[i + 1], 0), None) if i + 1 < len(liste) else (caret, None)
    if art == "wort_links":
        if caret.versatz > 0:
            return Caret(caret.pfad, _wortgrenze(satz.text, caret.versatz, False)), None
        return bewegen(erg, caret, "links")
    if art == "wort_rechts":
        if caret.versatz < n:
            return Caret(caret.pfad, _wortgrenze(satz.text, caret.versatz, True)), None
        return bewegen(erg, caret, "rechts")
    if art == "anfang":
        return Caret(liste[0], 0), None
    if art == "ende":
        return Caret(liste[-1], len(erg.absaetze[liste[-1]].satz.text)), None
    z = _zeile(erg, caret)
    if z is None:
        return caret, None
    seite, zi, r = z
    zeile = satz.zeilen[zi]
    if art == "zeilenanfang":
        return Caret(caret.pfad, zeile.box.start), None
    if art == "zeilenende":
        ende = zeile.ende
        if ende > zeile.box.start and zi < len(satz.zeilen) - 1 and satz.text[ende - 1] in ZEILENENDE:
            ende -= 1
        return Caret(caret.pfad, ende), None
    x = r.x + satz.cursor_x(caret.versatz, zi) if x is None else x
    if art in ("hoch", "runter"):
        ziel = _senkrecht(erg, seite, r, x, art == "runter")
        return (ziel, x) if ziel is not None else (caret, x)
    if art in ("seite_hoch", "seite_runter"):
        s = seite + (1 if art == "seite_runter" else -1)
        if not 0 <= s < len(erg.seiten):
            return bewegen(erg, caret, "ende" if art == "seite_runter" else "anfang")
        t = erg.treffer(s, Point(x, r.y + r.height / 2))
        return (Caret(t[0], t[1]), x) if t is not None else (caret, x)
    raise ValueError(f"unbekannte Bewegung {art!r}")
