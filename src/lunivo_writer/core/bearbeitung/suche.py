"""Suchen und Ersetzen im Dokumentmodell, ohne Qt.

Der Suchtext (mit Sonderzeichen ^p ^t …, Platzhaltern, Präfix/Suffix, ohne Satzzeichen/Leerzeichen) wird zu einem regulären Ausdruck über dem
„Rohtext“ des Dokuments: jede Textstelle ein Zeichen, Absätze durch eine Marke getrennt, Noten, Felder, Grafiken und Umbrüche mit eigenem
Kennzeichen. Positionen sind Stellen im Rohtext (``offset_zu_position`` und ``position_zu_offset`` bilden sie auf ``Position`` ab).
Das Ersetzen läuft über die Bearbeitungssitzung (``SuchTeil``).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from lunivo_writer.core.dokument.dokument import Absatz, Auswahl, Dokument, InlineObjekt, Lauf, Position, Zelle, format_an
from lunivo_writer.core.dokument.formate import verschmelze
from .texteingabe import NICHT_ERSETZEN, tippformat_bei
from .verlauf import schritt

ABSATZ = "\u2029"
ZEILE = "\u2028"
FUSS, END, FELD, GRAFIK, SEITE, SPALTE, ABSCHNITT = "\ue001", "\ue002", "\ue003", "\ue004", "\ue005", "\ue006", "\ue007"
GRENZE = "\ufdd0"                                                   # Zellen- und Rahmengrenze: kein Treffer geht darüber
MARKEN = ABSATZ + SEITE + SPALTE + ABSCHNITT                       # alles, was einen Absatz beendet
_NIE = MARKEN + GRENZE + "\ufdd1"

# (Name im Menü „Spezial“, Kürzel) — in derselben Reihenfolge wie in der Vorlage
SPEZIAL = (("Absatzmarke", "^p"), ("Tabstoppzeichen", "^t"), ("Beliebiges Zeichen", "^?"), ("Beliebige Ziffer", "^#"),
           ("Beliebiger Buchstabe", "^$"), ("Spaltenumbruch", "^n"), ("Endnotenzeichen", "^e"), ("Feld", "^d"),
           ("Fußnotenzeichen", "^f"), ("Grafik", "^g"), ("Manueller Zeilenumbruch", "^l"), ("Manueller Seitenumbruch", "^m"),
           ("Abschnittsumbruch", "^b"))
SPEZIAL_ERSETZEN = (("Absatzmarke", "^p"), ("Tabstoppzeichen", "^t"), ("Suchtext", "^&"), ("Inhalt der Zwischenablage", "^c"),
                    ("Spaltenumbruch", "^n"), ("Manueller Zeilenumbruch", "^l"), ("Manueller Seitenumbruch", "^m"))

_CODES = {"p": "[" + MARKEN + "]", "t": "\t", "?": "[^" + _NIE + "]", "#": "[0-9]", "$": "[^\\W\\d_]", "n": SPALTE, "e": END,
          "d": FELD, "f": FUSS, "g": GRAFIK, "l": ZEILE, "m": SEITE, "b": ABSCHNITT, "w": "[\u00a0 \t]", "^": "\\^"}
_SATZZEICHEN = r"!\"#%&'()*,\-./:;?@\[\\\]_{}¡§«»¿‐‑‒–—―‘’‚“”„•…‹›"


@dataclass
class Suchauftrag:
    text: str = ""
    gross: bool = False                    # Groß-/Kleinschreibung beachten
    ganz: bool = False                     # Nur ganzes Wort suchen
    platzhalter: bool = False              # Platzhalter verwenden (? * [ ] { } < >)
    praefix: bool = False                  # Präfix beachten: der Treffer steht am Wortanfang
    suffix: bool = False                   # Suffix beachten: der Treffer steht am Wortende
    ohne_satzzeichen: bool = False         # Interpunktionszeichen ignorieren
    ohne_leerzeichen: bool = False         # Leerzeichen ignorieren
    zeichen: list = field(default_factory=list)      # Formatbedingungen: ``f(Zeichenformat-Wörterbuch) -> bool`` für jedes Textstück des Treffers
    absatz: list = field(default_factory=list)       # Bedingungen an den Absatz: ``f(Absatz) -> bool``

    @property
    def hat_format(self) -> bool:
        return bool(self.zeichen or self.absatz)

    @property
    def leer(self) -> bool:
        return not self.text and not self.hat_format



# ---- Rohtext und Stellen ----------------------------------------------------------------------------------------------------------
def _besitzer(dok: Dokument) -> dict:
    """Absatz-Id → Besitzer der Blockliste (Abschnitt, Zelle oder Rahmen), in dem er steht."""
    aus: dict = {}
    for besitzer, bloecke in dok.behaelter():
        for b in bloecke:
            if isinstance(b, Absatz):
                aus[b.id] = besitzer
    return aus


def roh_text(dok: Dokument) -> str:
    """Der Text des Dokuments, eine Stelle je Position (Absätze durch ein Zeichen getrennt), mit Kennzeichen für Noten, Felder, Grafiken und Umbrüche."""
    absaetze = list(dok.absaetze())
    besitzer = _besitzer(dok)
    letzte_je_abschnitt = {id(ab): (ab.bloecke[-1].id if ab.bloecke and isinstance(ab.bloecke[-1], Absatz) else None) for ab in dok.abschnitte}
    teile: list = []
    for i, a in enumerate(absaetze):
        for x in a.inhalte:
            if isinstance(x, Lauf):
                art = ""
                note = x.format.get("note")
                if isinstance(note, str):
                    art = FUSS if note.startswith("f:") else END
                elif "feld" in x.format:
                    art = FELD
                teile.append(art * len(x.text) if art else x.text)
            else:
                teile.append(GRAFIK)
        if i + 1 >= len(absaetze):
            break
        naechster = absaetze[i + 1]
        if besitzer[a.id] is not besitzer[naechster.id]:
            teile.append(GRENZE)
        elif letzte_je_abschnitt.get(id(besitzer[a.id])) == a.id:
            teile.append(ABSCHNITT)
        elif naechster.format.get("spaltenumbruch_vor"):
            teile.append(SPALTE)
        elif naechster.format.get("seitenumbruch_vor"):
            teile.append(SEITE)
        else:
            teile.append(ABSATZ)
    return "".join(teile)


def offset_zu_position(dok: Dokument, offset: int) -> Position:
    """Die Textstelle zu einer Stelle im Rohtext (hinter dem Ende: das Dokumentende)."""
    n = 0
    letzter = None
    for a in dok.absaetze():
        if offset <= n + a.laenge:
            return Position(a.id, max(0, offset - n))
        n += a.laenge + 1
        letzter = a
    return Position(letzter.id, letzter.laenge)


def position_zu_offset(dok: Dokument, pos: Position) -> int:
    n = 0
    for a in dok.absaetze():
        if a.id == pos.absatz_id:
            return n + pos.versatz
        n += a.laenge + 1
    return n


# ---- Muster -------------------------------------------------------------------------------------------------------------------------
def _woertlich(text: str) -> list[str]:
    """Suchtext ohne Platzhalter → Liste von Regex-Stücken (ein Stück je Zeichen oder Sonderzeichen)."""
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch == "^" and i + 1 < len(text) and text[i + 1] in _CODES:
            out.append(_CODES[text[i + 1]]); i += 2; continue
        out.append(re.escape(ch)); i += 1
    return out


_BELIEBIG = "[^" + _NIE + "]"
# Platzhalter aus einem Zeichen → Regex-Stück
_EINFACH = {"?": _BELIEBIG, "*": _BELIEBIG + "*?", "@": "+", "<": r"\b(?=\w)", ">": r"(?<=\w)\b", "(": "(", ")": ")"}


def _klammer(text: str, i: int) -> tuple[str, int]:
    """``{n,m}`` (Wiederholung) oder ``[abc]``/``[!x]`` (Zeichenklasse) ab Stelle ``i`` → (Regex-Stück, Stelle des letzten verbrauchten Zeichens).
    Ohne schließende Klammer steht das Zeichen für sich selbst."""
    auf = text[i]
    j = text.find("}", i) if auf == "{" else text.find("]", i + 1)
    if j < 0:
        return re.escape(auf), i
    innen = text[i + 1:j]
    if auf == "{":
        return "{" + innen.replace(";", ",") + "}", j
    if innen.startswith("!"):
        innen = "^" + innen[1:]
    return "[" + innen.replace("\\", "\\\\") + "]", j


def _platzhalter(text: str) -> list[str]:
    """Platzhalter: ? ein Zeichen, * beliebig viele, [abc] [a-z] [!x] eines davon/keines, {n,m} Wiederholung, @ eins oder mehr,
    < Wortanfang, > Wortende, \\ nimmt das nächste Zeichen wörtlich; ( ) bilden Gruppen für \\1 im Ersatz."""
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        zwei = i + 1 < len(text)
        if ch == "^" and zwei and text[i + 1] in _CODES:
            out.append(_CODES[text[i + 1]]); i += 2
        elif ch == "\\" and zwei:
            out.append(re.escape(text[i + 1])); i += 2
        elif ch in "{[":
            stueck, i = _klammer(text, i)
            out.append(stueck); i += 1
        else:
            out.append(_EINFACH.get(ch) or re.escape(ch)); i += 1
    return out


def _ignoriert(a: Suchauftrag) -> str:
    """Die Zeichen, über die die Suche hinweggeht (Satzzeichen, Leerzeichen); mit Platzhaltern gilt das nicht."""
    if a.platzhalter:
        return ""
    return (_SATZZEICHEN if a.ohne_satzzeichen else "") + (" \u00a0\t" if a.ohne_leerzeichen else "")


def muster(a: Suchauftrag) -> re.Pattern | None:
    """Der reguläre Ausdruck des Auftrags; ``None`` bei leerem Text (dann sucht nur die Formatierung) oder ungültigen Platzhaltern."""
    text = a.text
    if not text:
        return None
    ignor = _ignoriert(a)
    if ignor:
        text = "".join(ch for ch in text if ch not in ignor) or text
    stuecke = _platzhalter(text) if a.platzhalter else _woertlich(text)
    zwischen = "(?:[" + re.escape(ignor) + "])*" if ignor else ""
    vor = r"(?<!\w)" if (a.ganz or a.praefix) else ""
    nach = r"(?!\w)" if (a.ganz or a.suffix) else ""
    try:
        return re.compile(vor + "(?:" + zwischen.join(stuecke) + ")" + nach, 0 if a.gross else re.IGNORECASE)
    except re.error:
        return None


def gueltig(a: Suchauftrag) -> bool:
    return not a.text or muster(a) is not None


def ersatz_text(a: Suchauftrag, ersatz: str, gefunden: str, zwischenablage: str = "") -> str:
    """Der Ersatztext mit seinen Sonderzeichen: ^p Absatz, ^t Tab, ^l Zeilenumbruch, ^m Seiten-, ^n Spaltenumbruch, ^& der gefundene Text,
    ^c die Zwischenablage, ^^ ein Zirkumflex; mit Platzhaltern zusätzlich \\1 … \\9 für die Gruppen."""
    out, i = [], 0
    m = muster(a) if a.platzhalter else None
    gruppen = m.fullmatch(gefunden).groups() if m is not None and m.fullmatch(gefunden) else ()
    while i < len(ersatz):
        ch = ersatz[i]
        if ch == "^" and i + 1 < len(ersatz):
            k = ersatz[i + 1]
            wert = {"p": ABSATZ, "t": "\t", "l": ZEILE, "m": SEITE, "n": SPALTE, "&": gefunden, "c": zwischenablage, "^": "^"}.get(k)
            if wert is not None:
                out.append(wert); i += 2; continue
        if ch == "\\" and a.platzhalter and i + 1 < len(ersatz) and ersatz[i + 1].isdigit():
            n = int(ersatz[i + 1])
            out.append((gruppen[n - 1] or "") if 0 < n <= len(gruppen) else ""); i += 2; continue
        out.append(ch); i += 1
    return "".join(out)


def _stuecke_im_bereich(dok: Dokument, von: int, bis: int):
    """(Absatz, Anfang im Absatz, Ende im Absatz) der Absätze, die der Bereich [von, bis) berührt."""
    n = 0
    for a in dok.absaetze():
        a0, a1 = n, n + a.laenge
        if a0 < max(bis, von + 1) and a1 >= von:
            yield a, max(von, a0) - a0, min(bis, a1) - a0
        n = a1 + 1
        if n > bis:
            break


def _zeichen_passen(dok: Dokument, von: int, bis: int, a: Suchauftrag) -> bool:
    if not a.hat_format:
        return True
    for absatz, s, e in _stuecke_im_bereich(dok, von, bis):
        if any(not p(absatz) for p in a.absatz):
            return False
        if a.zeichen:
            pos = 0
            for x in absatz.inhalte:
                n = len(x.text) if isinstance(x, Lauf) else 1
                if pos < e and pos + n > s and any(not p(x.format) for p in a.zeichen):
                    return False
                pos += n
    return True


def _nur_format(dok: Dokument, a: Suchauftrag, von: int, bis: int) -> list:
    """Ohne Suchtext: jede zusammenhängende Strecke mit der gesuchten Formatierung (je Absatz)."""
    aus = []
    n = 0
    for absatz in dok.absaetze():
        a0 = n
        n += absatz.laenge + 1
        if a0 >= bis:
            break
        if n <= von or not all(p(absatz) for p in a.absatz):
            continue
        if not a.zeichen:
            s, e = max(von, a0), min(bis, a0 + absatz.laenge)
            if e > s:
                aus.append((s, e))
            continue
        lauf, pos = None, a0
        for x in absatz.inhalte:
            laenge = len(x.text) if isinstance(x, Lauf) else 1
            s, e = max(von, pos), min(bis, pos + laenge)
            if e > s and all(p(x.format) for p in a.zeichen):
                lauf = (lauf[0], e) if lauf and lauf[1] == s else (s, e) if not lauf else (aus.append(lauf) or (s, e))
            elif lauf:
                aus.append(lauf); lauf = None
            pos += laenge
        if lauf:
            aus.append(lauf)
    return aus


def treffer(dok: Dokument, a: Suchauftrag, von: int = 0, bis: int | None = None, grenze: int = 5000) -> list:
    """Alle Treffer im Bereich [von, bis) als (von, bis)."""
    roh = roh_text(dok)
    bis = len(roh) if bis is None else min(bis, len(roh))
    if a.leer:
        return []
    m = muster(a)
    if m is None:
        return [] if a.text else _nur_format(dok, a, von, bis)[:grenze]
    aus = []
    for x in m.finditer(roh, von, bis):
        if x.end() == x.start():
            continue
        if _zeichen_passen(dok, x.start(), x.end(), a):
            aus.append((x.start(), x.end()))
            if len(aus) >= grenze:
                break
    return aus


def naechster(dok: Dokument, a: Suchauftrag, ab: int, rueckwaerts: bool = False, von: int = 0, bis: int | None = None, umlauf: bool = True):
    """Der nächste Treffer hinter (oder vor) ``ab``; mit ``umlauf`` geht es am Ende vorn weiter (und umgekehrt)."""
    alle = treffer(dok, a, von, bis)
    if not alle:
        return None
    if rueckwaerts:
        vor = [t for t in alle if t[0] < ab]
        return vor[-1] if vor else (alle[-1] if umlauf else None)
    nach = [t for t in alle if t[0] >= ab]
    return nach[0] if nach else (alle[0] if umlauf else None)


class SuchTeil:
    @schritt("Ersetzen", "text")
    def ersetzen_durch(self, von: int, bis: int, neu: str, format: dict | None = None, absatzformat: dict | None = None) -> Position:
        """Ersetzt den Bereich [von, bis) des Rohtextes durch ``neu`` (Text mit Kennzeichen aus ``ersatz_text``). Die Formatierung des ersetzten Textes
        bleibt, ``format`` kommt darüber (Format für „Ersetzen durch“); ``absatzformat`` gilt für den Absatz am Ende. → Ende des eingesetzten Textes."""
        roh = roh_text(self.dokument)[von:bis]
        start, ende = offset_zu_position(self.dokument, von), offset_zu_position(self.dokument, bis)
        if roh in (SEITE, SPALTE, ABSCHNITT) and neu == "":                      # nur der Umbruch geht, die Absätze bleiben getrennt
            if roh == ABSCHNITT:
                self.abschnitt_entfernen(self.abschnitt_index(ende.absatz_id))
            else:
                self.absatzformat_anwenden({"spaltenumbruch_vor" if roh == SPALTE else "seitenumbruch_vor": None}, absatz_ids=[ende.absatz_id])
            return ende
        a = self._absatz(start.absatz_id)
        if start != ende:
            basis = {k: v for k, v in format_an(a, min(start.versatz + 1, a.laenge)).items() if k not in NICHT_ERSETZEN}
        else:
            basis = tippformat_bei(a, start.versatz)
        if format:
            basis = verschmelze(basis, format)
        pos = self.loeschen(Auswahl(start, ende)) if start != ende else start
        for teil in re.split("([" + ABSATZ + SEITE + SPALTE + "])", neu):
            if not teil:
                continue
            if teil in (ABSATZ, SEITE, SPALTE):
                pos = self.absatz_teilen(pos)
                if teil != ABSATZ:
                    self.absatzformat_anwenden({"seitenumbruch_vor": True} if teil == SEITE else {"spaltenumbruch_vor": True}, absatz_ids=[pos.absatz_id])
            else:
                pos = self.text_einfuegen(teil, pos, basis)
        if absatzformat:
            self.absatzformat_anwenden(absatzformat, absatz_ids=[pos.absatz_id])
        return pos

    @schritt("Alle ersetzen", "text")
    def alle_ersetzen_auftrag(self, a: Suchauftrag, ersatz: str, von: int = 0, bis: int | None = None, format: dict | None = None,
                              absatzformat: dict | None = None, zwischenablage: str = "") -> int:
        """Alle Treffer im Bereich ersetzen, als ein Schritt für Rückgängig. → Zahl der Ersetzungen."""
        alle = treffer(self.dokument, a, von, bis)
        roh = roh_text(self.dokument)
        for s, e in reversed(alle):                                              # von hinten: die vorderen Positionen bleiben gültig
            self.ersetzen_durch(s, e, ersatz_text(a, ersatz, roh[s:e], zwischenablage), format, absatzformat)
        return len(alle)
