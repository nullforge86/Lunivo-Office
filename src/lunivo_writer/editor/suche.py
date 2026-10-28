"""Suchen und Ersetzen wie im Fenster der Vorlage: Sonderzeichen (^p, ^t, ^? …), Platzhalter, Präfix/Suffix, Satzzeichen und Leerzeichen
ignorieren, Formatierung als Bedingung — ohne Oberfläche. Die Bedienung steht in der linken Seitenleiste (``ui/document/suchen_feld.py``).

    a = Suchauftrag("Haus^p", gross=True)
    bereiche = treffer(doc, a)                     # [(von, bis), …] in Dokumentpositionen
    n = alle_ersetzen(doc, a, "Heim^p")

Gesucht wird im Rohtext des Dokuments (``toRawText``: eine Stelle je Dokumentposition). Zeichen, die keine Buchstaben sind — Fußnoten- und
Endnotenzeichen, Felder, Grafiken, Seiten-, Spalten- und Abschnittsumbrüche — bekommen dafür ein eigenes Kennzeichen (Privatbereich von Unicode),
damit ``^f``, ``^e``, ``^d``, ``^g``, ``^m``, ``^n`` und ``^b`` sie finden. Ein Seiten-, Spalten- oder Abschnittsumbruch ist zugleich eine Absatzmarke.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Callable

from PySide6.QtGui import QTextCharFormat, QTextCursor, QTextDocument, QTextFormat

from lunivo_writer.editor.zusatz import B_SPALTE, P_FELD, P_NOTE

ABSATZ = " "
ZEILE = " "
FUSS, END, FELD, GRAFIK, SEITE, SPALTE, ABSCHNITT = "", "", "", "", "", "", ""
MARKEN = ABSATZ + SEITE + SPALTE + ABSCHNITT                       # alles, was einen Absatz beendet
_NIE = MARKEN + "﷐﷑"                                     # Zellen- und Rahmengrenzen: kein Treffer geht darüber

# (Name im Menü „Spezial“, Kürzel) — wie in der Vorlage, in derselben Reihenfolge
SPEZIAL = (("Absatzmarke", "^p"), ("Tabstoppzeichen", "^t"), ("Beliebiges Zeichen", "^?"), ("Beliebige Ziffer", "^#"),
           ("Beliebiger Buchstabe", "^$"), ("Spaltenumbruch", "^n"), ("Endnotenzeichen", "^e"), ("Feld", "^d"),
           ("Fußnotenzeichen", "^f"), ("Grafik", "^g"), ("Manueller Zeilenumbruch", "^l"), ("Manueller Seitenumbruch", "^m"),
           ("Abschnittsumbruch", "^b"))
SPEZIAL_ERSETZEN = (("Absatzmarke", "^p"), ("Tabstoppzeichen", "^t"), ("Suchtext", "^&"), ("Inhalt der Zwischenablage", "^c"),
                    ("Spaltenumbruch", "^n"), ("Manueller Zeilenumbruch", "^l"), ("Manueller Seitenumbruch", "^m"))

_CODES = {"p": "[" + MARKEN + "]", "t": "\t", "?": "[^" + _NIE + "]", "#": "[0-9]", "$": "[^\\W\\d_]", "n": SPALTE, "e": END,
          "d": FELD, "f": FUSS, "g": GRAFIK, "l": ZEILE, "m": SEITE, "b": ABSCHNITT, "w": "[  \t]", "^": "\\^"}
_SATZZEICHEN = r"!\"#%&'()*,\-./:;?@\[\\\]_{}¡§«»¿‐‑‒–—―‘’‚“”„•…‹›"


@dataclass
class Suchauftrag:
    text: str = ""
    gross: bool = False                    # Groß-/Kleinschreibung beachten
    ganz: bool = False                     # Nur ganzes Wort suchen
    platzhalter: bool = False              # Platzhalter verwenden (? * [ ] { } < > @ wie in Word)
    praefix: bool = False                  # Präfix beachten: der Treffer steht am Wortanfang
    suffix: bool = False                   # Suffix beachten: der Treffer steht am Wortende
    ohne_satzzeichen: bool = False         # Interpunktionszeichen ignorieren
    ohne_leerzeichen: bool = False         # Leerzeichen ignorieren
    zeichen: list[Callable[[QTextCharFormat], bool]] = field(default_factory=list)   # Formatbedingungen an jedes Zeichen des Treffers
    absatz: list[Callable] = field(default_factory=list)                           # Bedingungen an den Absatz (QTextBlock)

    @property
    def hat_format(self) -> bool:
        return bool(self.zeichen or self.absatz)

    @property
    def leer(self) -> bool:
        return not self.text and not self.hat_format


def roh_text(doc: QTextDocument) -> str:
    """Der Text des Dokuments, eine Stelle je Position, mit Kennzeichen für Noten, Felder, Grafiken und Umbrüche."""
    t = list(doc.toRawText())
    from lunivo_writer.editor.abschnitte import B_ABSCHNITT
    b = doc.firstBlock()
    while b.isValid():
        it = b.begin()
        while not it.atEnd():
            f = it.fragment()
            if f.isValid():
                cf = f.charFormat()
                art = ""
                if cf.isImageFormat():
                    art = GRAFIK
                elif cf.hasProperty(P_NOTE):
                    art = FUSS if cf.stringProperty(P_NOTE).startswith("f:") else END
                elif cf.hasProperty(P_FELD):
                    art = FELD
                if art:
                    for i in range(f.position(), min(f.position() + f.length(), len(t))):
                        if art != GRAFIK or t[i] == "￼":
                            t[i] = art
            it += 1
        ende = b.position() + b.length() - 1
        if ende < len(t) and t[ende] == ABSATZ:
            n = b.next()
            if b.blockFormat().hasProperty(B_ABSCHNITT):
                t[ende] = ABSCHNITT
            elif n.isValid() and n.blockFormat().property(B_SPALTE):
                t[ende] = SPALTE
            elif n.isValid() and n.blockFormat().pageBreakPolicy() & QTextFormat.PageBreak_AlwaysBefore:
                from lunivo_writer.editor.zusatz import B_AUTOUMBRUCH
                if not n.blockFormat().property(B_AUTOUMBRUCH):
                    t[ende] = SEITE
        b = b.next()
    return "".join(t)


def _woertlich(text: str) -> list[str]:
    """Suchtext ohne Platzhalter → Liste von Regex-Stücken (ein Stück je Zeichen oder Sonderzeichen)."""
    out, i = [], 0
    while i < len(text):
        ch = text[i]
        if ch == "^" and i + 1 < len(text) and text[i + 1] in _CODES:
            out.append(_CODES[text[i + 1]]); i += 2; continue
        out.append(re.escape(ch)); i += 1
    return out


def _platzhalter(text: str) -> list[str]:
    """Platzhalter wie in Word: ? ein Zeichen, * beliebig viele, [abc] [a-z] [!x] eines davon/keines, {n,m} Wiederholung, @ eins oder mehr,
    < Wortanfang, > Wortende, \\ nimmt das nächste Zeichen wörtlich; ( ) bilden Gruppen für \\1 im Ersatz."""
    out, i = [], 0
    beliebig = "[^" + _NIE + "]"
    while i < len(text):
        ch = text[i]
        if ch == "^" and i + 1 < len(text) and text[i + 1] in _CODES:
            out.append(_CODES[text[i + 1]]); i += 2; continue
        if ch == "\\" and i + 1 < len(text):
            out.append(re.escape(text[i + 1])); i += 2; continue
        if ch == "?":
            out.append(beliebig)
        elif ch == "*":
            out.append(beliebig + "*?")
        elif ch == "@":
            out.append("+")
        elif ch == "<":
            out.append(r"\b(?=\w)")
        elif ch == ">":
            out.append(r"(?<=\w)\b")
        elif ch in "()":
            out.append(ch)
        elif ch == "{":
            j = text.find("}", i)
            if j < 0:
                out.append(re.escape(ch))
            else:
                out.append("{" + text[i + 1:j].replace(";", ",") + "}"); i = j
        elif ch == "[":
            j = text.find("]", i + 1)
            if j < 0:
                out.append(re.escape(ch))
            else:
                innen = text[i + 1:j]
                if innen.startswith("!"):
                    innen = "^" + innen[1:]
                out.append("[" + innen.replace("\\", "\\\\") + "]"); i = j
        else:
            out.append(re.escape(ch))
        i += 1
    return out


def muster(a: Suchauftrag) -> re.Pattern | None:
    """Der reguläre Ausdruck des Auftrags; ``None`` bei leerem Text (dann sucht nur die Formatierung) oder ungültigen Platzhaltern."""
    text = a.text
    if not text:
        return None
    ignor = ""
    if a.ohne_satzzeichen:
        ignor += _SATZZEICHEN
    if a.ohne_leerzeichen:
        ignor += "  \t"
    if ignor and not a.platzhalter:
        text = "".join(ch for ch in text if ch not in ignor) or text
    stuecke = _platzhalter(text) if a.platzhalter else _woertlich(text)
    zwischen = "(?:[" + re.escape(ignor) + "])*" if ignor and not a.platzhalter else ""
    kern = zwischen.join(stuecke)
    vor = r"(?<!\w)" if (a.ganz or a.praefix) else ""
    nach = r"(?!\w)" if (a.ganz or a.suffix) else ""
    try:
        return re.compile(vor + "(?:" + kern + ")" + nach, 0 if a.gross else re.IGNORECASE)
    except re.error:
        return None


def gueltig(a: Suchauftrag) -> bool:
    return not a.text or muster(a) is not None


def _zeichen_passen(doc: QTextDocument, von: int, bis: int, a: Suchauftrag) -> bool:
    if not a.hat_format:
        return True
    pos = von
    while pos < max(bis, von + 1):
        b = doc.findBlock(pos)
        if not b.isValid():
            return False
        if any(not p(b) for p in a.absatz):
            return False
        if a.zeichen:
            it = b.begin()
            while not it.atEnd():
                f = it.fragment()
                if f.isValid() and f.position() < bis and f.position() + f.length() > pos:
                    if any(not p(f.charFormat()) for p in a.zeichen):
                        return False
                it += 1
        pos = b.position() + b.length()
    return True


def _nur_format(doc: QTextDocument, a: Suchauftrag, von: int, bis: int) -> list[tuple[int, int]]:
    """Ohne Suchtext: jede zusammenhängende Strecke mit der gesuchten Formatierung (je Absatz)."""
    out = []
    b = doc.findBlock(von)
    while b.isValid() and b.position() < bis:
        if all(p(b) for p in a.absatz):
            if not a.zeichen:
                s, e = max(von, b.position()), min(bis, b.position() + b.length() - 1)
                if e > s:
                    out.append((s, e))
            else:
                lauf = None
                it = b.begin()
                while not it.atEnd():
                    f = it.fragment()
                    if f.isValid():
                        s, e = max(von, f.position()), min(bis, f.position() + f.length())
                        if e > s and all(p(f.charFormat()) for p in a.zeichen):
                            if lauf and lauf[1] == s:
                                lauf = (lauf[0], e)
                            else:
                                if lauf:
                                    out.append(lauf)
                                lauf = (s, e)
                        elif lauf:
                            out.append(lauf); lauf = None
                    it += 1
                if lauf:
                    out.append(lauf)
        b = b.next()
    return out


def treffer(doc: QTextDocument, a: Suchauftrag, von: int = 0, bis: int | None = None, grenze: int = 5000) -> list[tuple[int, int]]:
    """Alle Treffer im Bereich [von, bis) als (von, bis)."""
    roh = roh_text(doc)
    bis = len(roh) if bis is None else min(bis, len(roh))
    if a.leer:
        return []
    m = muster(a)
    if m is None:
        return [] if a.text else _nur_format(doc, a, von, bis)[:grenze]
    out = []
    for x in m.finditer(roh, von, bis):
        if x.end() == x.start():
            continue
        if _zeichen_passen(doc, x.start(), x.end(), a):
            out.append((x.start(), x.end()))
            if len(out) >= grenze:
                break
    return out


def naechster(doc: QTextDocument, a: Suchauftrag, ab: int, rueckwaerts: bool = False, von: int = 0, bis: int | None = None,
              umlauf: bool = True) -> tuple[int, int] | None:
    """Der nächste Treffer hinter (oder vor) ``ab``; mit ``umlauf`` geht es am Ende vorn weiter (und umgekehrt)."""
    alle = treffer(doc, a, von, bis)
    if not alle:
        return None
    if rueckwaerts:
        vor = [t for t in alle if t[0] < ab]
        return vor[-1] if vor else (alle[-1] if umlauf else None)
    nach = [t for t in alle if t[0] >= ab]
    return nach[0] if nach else (alle[0] if umlauf else None)


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


def ersetzen(doc: QTextDocument, von: int, bis: int, neu: str, format_: QTextCharFormat | None = None,
             absatz_format: Callable | None = None) -> int:
    """Den Bereich durch ``neu`` ersetzen (Text mit Kennzeichen aus ``ersatz_text``). Die Formatierung des ersetzten Textes bleibt,
    ``format_`` kommt darüber (Format für „Ersetzen durch“). → Ende des eingesetzten Textes."""
    c = QTextCursor(doc)
    c.setPosition(von)
    c.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor)
    cf = QTextCharFormat(c.charFormat())                  # das Format des ersten ersetzten Zeichens
    if format_ is not None:
        cf.merge(format_)
    c.setPosition(von); c.setPosition(bis, QTextCursor.KeepAnchor)
    roh = roh_text(doc)[von:bis]
    if roh in (SEITE, SPALTE, ABSCHNITT) and neu == "":
        _umbruch_weg(doc, von, roh)                         # nur der Umbruch geht, die Absätze bleiben getrennt
        return bis
    c.removeSelectedText()
    for teil in re.split("([" + ABSATZ + SEITE + SPALTE + "])", neu):
        if not teil:
            continue
        if teil in (ABSATZ, SEITE, SPALTE):
            c.insertBlock()
            if teil != ABSATZ:
                bf = c.blockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_AlwaysBefore)
                if teil == SPALTE:
                    bf.setProperty(B_SPALTE, 1)
                c.setBlockFormat(bf)
        else:
            c.insertText(teil, cf)
    if absatz_format is not None:
        absatz_format(c)
    return c.position()


def _umbruch_weg(doc: QTextDocument, pos: int, art: str) -> None:
    b = doc.findBlock(pos)
    if art == ABSCHNITT:
        from lunivo_writer.editor.abschnitte import B_ABSCHNITT
        bf = b.blockFormat(); bf.clearProperty(B_ABSCHNITT); QTextCursor(b).setBlockFormat(bf)
        return
    n = b.next()
    if n.isValid():
        bf = n.blockFormat(); bf.setPageBreakPolicy(QTextFormat.PageBreak_Auto); bf.clearProperty(B_SPALTE)
        QTextCursor(n).setBlockFormat(bf)


def alle_ersetzen(doc: QTextDocument, a: Suchauftrag, ersatz: str, von: int = 0, bis: int | None = None,
                  format_: QTextCharFormat | None = None, absatz_format: Callable | None = None, zwischenablage: str = "") -> int:
    """Alle Treffer im Bereich ersetzen, als ein Schritt für Rückgängig. → Zahl der Ersetzungen."""
    alle = treffer(doc, a, von, bis)
    if not alle:
        return 0
    roh = roh_text(doc)
    c = QTextCursor(doc)
    c.beginEditBlock()
    try:
        for s, e in reversed(alle):                         # von hinten: die vorderen Positionen bleiben gültig
            ersetzen(doc, s, e, ersatz_text(a, ersatz, roh[s:e], zwischenablage), format_, absatz_format)
    finally:
        c.endEditBlock()
    return len(alle)
