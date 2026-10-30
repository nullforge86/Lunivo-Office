"""Felder einfügen (Einfügen ▸ Schnellbausteine ▸ Felder …) wie in der WPS-Vorlage: Feldnamen, Feldfunktionen und Assistent.
Der Text ist das Feldergebnis, die Feldanweisung steht in ``P_FELD`` und geht als echtes Feld ins DOCX (Word rechnet es dort neu).
Keine Oberfläche.

    anweisung = vorgabe("Seite")                         # "PAGE"
    text = ergebnis(anweisung, kontext)                  # "3"
    feld_einfuegen(ed, anweisung, text)
    kontext = kontext_sammeln(ed, autor="Autor")           # Seite, Seitenzahlen, Textmarken, Tabellenzahlen, Formatvorlagen …

Formel (``= …``): + − * / ^, Klammern, Zahlen (Komma oder Punkt), Textmarken, ABOVE/BELOW/LEFT/RIGHT in Tabellen und die Funktionen
aus ``FUNKTIONEN``; ``\\# "0,00"`` gibt das Zahlenformat vor.
"""
from __future__ import annotations

import math
import re

from PySide6.QtCore import QDateTime, QLocale

from lunivo_writer.editor.zusatz import P_FELD

# Feldname (wie in der Vorlage) → (Beschreibung, Feldanweisung zu Beginn)
FELDER = {
    "Formel": ("Berechnet das Ergebnis eines Ausdrucks (in Tabellen auch mit ABOVE, LEFT …).", "="),
    "Hyperlink": ("Fügt einen Link zu einer Datei oder Webseite ein.", 'HYPERLINK ""'),
    "Seite": ("Die Nummer der aktuellen Seite.", "PAGE"),
    "PageRef": ("Die Seitenzahl einer Textmarke.", "PAGEREF"),
    "SectionPages": ("Die Zahl der Seiten im aktuellen Abschnitt.", "SECTIONPAGES"),
    "Seq": ("Eine fortlaufende Nummer (Abbildungen, Tabellen, Formeln).", "SEQ Abbildung \\* ARABIC"),
    "TC": ("Ein Eintrag für das Inhaltsverzeichnis; im Text unsichtbar.", 'TC "" \\l 1'),
    "Uhrzeit": ("Das aktuelle Datum oder die aktuelle Uhrzeit.", 'TIME \\@ "HH:mm"'),
    "PrintDate": ("Das Datum, an dem das Dokument zuletzt gedruckt wurde.", 'PRINTDATE \\@ "dd.MM.yyyy"'),
    "TOC": ("Ein Inhaltsverzeichnis aus den Überschriften.", 'TOC \\o "1-3" \\h'),
    "NumPages": ("Die Zahl der Seiten im Dokument.", "NUMPAGES"),
    "Dokumentvariable": ("Der Wert einer Dokumentvariablen.", "DOCVARIABLE"),
    "Seriendruckfeld": ("Ein Feld aus der Empfängerliste des Seriendrucks.", "MERGEFIELD"),
    "StyleRef": ("Der Text des letzten Absatzes mit der gewählten Formatvorlage.", 'STYLEREF "Überschrift 1"'),
}

ZAHLENFORMATE = ["0", "0,00", "#.##0", "#.##0,00", "#.##0,00 €", "0 %", "0,00 %"]
FUNKTIONEN = ["ABS", "AND", "AVERAGE", "COUNT", "DEFINED", "FALSE", "IF", "INT", "MAX", "MIN", "MOD", "NOT", "OR", "PRODUCT",
              "ROUND", "SIGN", "SUM", "TRUE"]
BEREICHE = ["ABOVE", "BELOW", "LEFT", "RIGHT"]
SCHREIBWEISEN = [("ARABIC", "1, 2, 3, …"), ("ROMAN", "I, II, III, …"), ("roman", "i, ii, iii, …"), ("ALPHABETIC", "A, B, C, …"),
                 ("alphabetic", "a, b, c, …")]
DATUMSFORMATE = ["dd.MM.yyyy", "d. MMMM yyyy", "dddd, d. MMMM yyyy", "dd.MM.yy", "yyyy-MM-dd", "HH:mm", "HH:mm:ss",
                 "dd.MM.yyyy HH:mm"]
SEQ_KATEGORIEN = ["Abbildung", "Tabelle", "Formel"]
MERGEFORMAT = "\\* MERGEFORMAT"


def vorgabe(name: str) -> str:
    return FELDER.get(name, ("", ""))[1]


# ---- Ergebnis ----------------------------------------------------------------------------------------------------------
def _schalter(anweisung: str, zeichen: str) -> str | None:
    m = re.search(r"\\" + re.escape(zeichen) + r'\s*"([^"]*)"', anweisung) or re.search(r"\\" + re.escape(zeichen) + r"\s*(\S+)", anweisung)
    return m.group(1) if m else None


def _ohne_schalter(anweisung: str) -> str:
    return re.split(r"\s\\[#@*lohn]", " " + anweisung, maxsplit=1)[0].strip()


def schreibweise(n: int, art: str | None) -> str:
    from lunivo_writer.editor.zahlformat import zahl_text
    return zahl_text(n, {"ROMAN": "roemisch", "roman": "roemisch_klein", "ALPHABETIC": "gross", "alphabetic": "klein"}.get(art or "", "arabisch"))


def zahl_formatieren(wert: float, muster: str | None) -> str:
    """Zahl nach einem Muster wie ``#.##0,00``, ``0 %`` (deutsche Schreibweise); ohne Muster so kurz wie möglich."""
    de = QLocale(QLocale.German, QLocale.Germany)
    if not muster:
        return de.toString(int(wert)) if float(wert).is_integer() else de.toString(wert, "g", 12)
    prozent = "%" in muster
    wert = wert * 100 if prozent else wert
    stellen = len(muster.split(",", 1)[1].rstrip(" %€").replace("#", "0")) if "," in muster else 0
    text = de.toString(round(wert, stellen), "f", stellen)
    if "." not in muster.split(",")[0]:
        text = text.replace(".", "")
    zusatz = muster[len(muster.rstrip(" %€")):]
    return text + zusatz


def ergebnis(anweisung: str, kontext: dict) -> str:
    """Das Feldergebnis jetzt. ``kontext`` aus ``kontext_sammeln`` (alle Angaben freiwillig)."""
    roh = anweisung.strip()
    if not roh:
        return ""
    if roh.startswith("="):
        try:
            return zahl_formatieren(formel(roh[1:], kontext), _schalter(roh, "#"))
        except ValueError:
            return "!Syntaxfehler"
    kern = _ohne_schalter(roh)
    teile = kern.split(None, 1)
    wort, rest = teile[0].upper(), (teile[1] if len(teile) > 1 else "").strip().strip('"')
    art = _schalter(roh, "*")
    art = art if art and art.upper() != "MERGEFORMAT" else None
    de = QLocale(QLocale.German, QLocale.Germany)
    if wort == "PAGE":
        return schreibweise(int(kontext.get("seite", 1)), art)
    if wort in ("NUMPAGES", "SECTIONPAGES"):
        return schreibweise(int(kontext.get("abschnittsseiten" if wort == "SECTIONPAGES" else "seiten", kontext.get("seiten", 1))), art)
    if wort == "PAGEREF":
        return str(kontext.get("textmarken_seiten", {}).get(rest.split()[0] if rest else "", "")) or "Fehler! Textmarke nicht definiert."
    if wort == "SEQ":
        kat = rest.split()[0] if rest else "Abbildung"
        return schreibweise(int(kontext.get("seq", {}).get(kat, 0)) + 1, art)
    if wort == "TC":
        return ""
    if wort in ("TIME", "DATE", "PRINTDATE"):
        muster = _schalter(roh, "@") or ("HH:mm" if wort == "TIME" else "dd.MM.yyyy")
        zeit = kontext.get("druckdatum") if wort == "PRINTDATE" else QDateTime.currentDateTime()
        return de.toString(zeit, muster) if zeit is not None else "00.00.0000"
    if wort == "HYPERLINK":
        return rest
    if wort == "DOCVARIABLE":
        return str(kontext.get("variablen", {}).get(rest, ""))
    if wort == "MERGEFIELD":
        return f"«{rest}»" if rest else ""
    if wort == "STYLEREF":
        return str(kontext.get("stilref", {}).get(rest, "")) or "Fehler! Kein Text mit angegebener Formatvorlage im Dokument."
    if wort == "TOC":
        return ""
    return ""


# ---- Formel ------------------------------------------------------------------------------------------------------------
_TOKEN = re.compile(r"\s*(?:(\d+(?:[.,]\d+)?)|([A-Za-zÄÖÜäöüß_][A-Za-z0-9ÄÖÜäöüß_]*)|(<=|>=|<>|[-+*/^(),;<>=%]))")


def formel(text: str, kontext: dict) -> float:
    """Ausdruck rechnen; ValueError bei Fehlern. Bereiche (ABOVE …) kommen aus ``kontext["bereiche"]``, Textmarken aus
    ``kontext["textmarken_werte"]``."""
    text = re.split(r"\\[#*]", text, maxsplit=1)[0]
    pos, toks = 0, []
    while pos < len(text):
        if text[pos:].strip() == "":
            break
        m = _TOKEN.match(text, pos)
        if not m:
            raise ValueError(text[pos:])
        toks.append(m.group(1) and ("zahl", float(m.group(1).replace(",", "."))) or m.group(2) and ("name", m.group(2))
                    or ("op", m.group(3)))
        pos = m.end()
    i = 0

    def nimm(op=None):
        nonlocal i
        if i >= len(toks) or (op is not None and toks[i] != ("op", op)):
            raise ValueError(op)
        i += 1
        return toks[i - 1]

    def schau():
        return toks[i] if i < len(toks) else ("ende", None)

    def vergleich():
        a = summe()
        while schau()[0] == "op" and schau()[1] in ("<", ">", "=", "<=", ">=", "<>"):
            o = nimm()[1]; b = summe()
            a = float({"<": a < b, ">": a > b, "=": a == b, "<=": a <= b, ">=": a >= b, "<>": a != b}[o])
        return a

    def summe():
        a = produkt()
        while schau() in (("op", "+"), ("op", "-")):
            o = nimm()[1]; b = produkt(); a = a + b if o == "+" else a - b
        return a

    def produkt():
        a = potenz()
        while schau() in (("op", "*"), ("op", "/")):
            o = nimm()[1]; b = potenz()
            if o == "/" and b == 0:
                raise ValueError("Division durch null")
            a = a * b if o == "*" else a / b
        return a

    def potenz():
        a = einzeln()
        if schau() == ("op", "^"):
            nimm(); a = a ** potenz()
        return a

    def einzeln():
        if schau() == ("op", "-"):
            nimm(); return -einzeln()
        if schau() == ("op", "+"):
            nimm(); return einzeln()
        art, wert = nimm()
        if art == "zahl":
            v = wert
        elif art == "op" and wert == "(":
            v = vergleich(); nimm(")")
        elif art == "name":
            n = wert.upper()
            if schau() == ("op", "("):
                nimm("(")
                werte = []
                if schau() != ("op", ")"):
                    werte.extend(argument())
                    while schau() in (("op", ","), ("op", ";")):
                        nimm(); werte.extend(argument())
                nimm(")")
                v = _funktion(n, werte)
            elif n in ("TRUE", "FALSE"):
                v = 1.0 if n == "TRUE" else 0.0
            elif wert in kontext.get("textmarken_werte", {}):
                v = float(kontext["textmarken_werte"][wert])
            else:
                raise ValueError(wert)
        else:
            raise ValueError(wert)
        if schau() == ("op", "%"):
            nimm(); v /= 100
        return v

    def argument() -> list[float]:
        if schau()[0] == "name" and schau()[1].upper() in BEREICHE and (i + 1 >= len(toks) or toks[i + 1] != ("op", "(")):
            return [float(x) for x in kontext.get("bereiche", {}).get(nimm()[1].upper(), [])]
        return [vergleich()]

    if not toks:
        raise ValueError("leer")
    ergebnis_ = vergleich()
    if i != len(toks):
        raise ValueError("Rest")
    return ergebnis_


def _funktion(n: str, w: list[float]) -> float:
    if n == "SUM": return sum(w)
    if n == "PRODUCT": return math.prod(w) if w else 0.0
    if n == "AVERAGE":
        if not w: raise ValueError(n)
        return sum(w) / len(w)
    if n == "COUNT": return float(len(w))
    if n == "MAX": return max(w) if w else 0.0
    if n == "MIN": return min(w) if w else 0.0
    if n == "ABS" and len(w) == 1: return abs(w[0])
    if n == "INT" and len(w) == 1: return float(math.trunc(w[0]))
    if n == "SIGN" and len(w) == 1: return float((w[0] > 0) - (w[0] < 0))
    if n == "ROUND" and len(w) == 2: return float(round(w[0], int(w[1])))
    if n == "MOD" and len(w) == 2 and w[1]: return math.fmod(w[0], w[1])
    if n == "AND": return float(all(w))
    if n == "OR": return float(any(w))
    if n == "NOT" and len(w) == 1: return float(not w[0])
    if n == "IF" and len(w) == 3: return w[1] if w[0] else w[2]
    if n == "DEFINED": return 1.0
    if n in ("TRUE", "FALSE") and not w: return 1.0 if n == "TRUE" else 0.0
    raise ValueError(n)


# ---- Kontext aus dem Dokument ------------------------------------------------------------------------------------------
def _zahl(text: str) -> float | None:
    t = text.strip().replace(".", "").replace(",", ".").rstrip(" %€")
    try:
        return float(t)
    except ValueError:
        return None


def tabellen_bereiche(ed) -> dict[str, list[float]]:
    """Zahlen über, unter, links und rechts der Zelle an der Schreibmarke (leer außerhalb von Tabellen)."""
    c = ed.textCursor()
    t = c.currentTable()
    if t is None:
        return {}
    z = t.cellAt(c)
    r0, s0 = z.row(), z.column()

    def wert(r, s):
        zelle = t.cellAt(r, s)
        a = zelle.firstCursorPosition(); a.setPosition(zelle.lastCursorPosition().position(), a.MoveMode.KeepAnchor)
        return _zahl(a.selectedText())

    def reihe(zellen):
        return [v for v in (wert(r, s) for r, s in zellen) if v is not None]
    return {"ABOVE": reihe((r, s0) for r in range(r0)), "BELOW": reihe((r, s0) for r in range(r0 + 1, t.rows())),
            "LEFT": reihe((r0, s) for s in range(s0)), "RIGHT": reihe((r0, s) for s in range(s0 + 1, t.columns()))}


def kontext_sammeln(ed, autor: str = "", pfad: str = "") -> dict:
    from lunivo_writer.editor import verweise as V
    from lunivo_writer.editor.verzeichnis import _seiten
    doc = ed.document()
    pos = ed.textCursor().position()
    marken = V.lesezeichen_liste(ed, versteckte=False)
    text = doc.toPlainText()
    try:
        seiten_marken = dict(zip([m["name"] for m in marken], _seiten(ed, [m["von"] for m in marken]))) if marken else {}
        seite = _seiten(ed, [pos])[0]
    except Exception:                                                 # ohne Seitenaufteilung (z. B. Weblayout)
        seiten_marken, seite = {}, 1
    werte = {m["name"]: v for m in marken if (v := _zahl(text[m["von"]:m["bis"]])) is not None}
    seq: dict[str, int] = {}
    for k in V.beschriftungen_liste(ed):
        if k["pos"] < pos:
            seq[k["label"]] = seq.get(k["label"], 0) + 1
    stilref: dict[str, str] = {}
    b = doc.findBlock(pos)
    while b.isValid():
        lv = b.blockFormat().headingLevel()
        if lv and b.text().strip():
            stilref.setdefault(f"Überschrift {lv}", b.text().strip())
        b = b.previous()
    return {"seite": seite, "seiten": max(1, int(getattr(ed, "_pages", 1) or 1)), "textmarken": [m["name"] for m in marken],
            "textmarken_seiten": seiten_marken, "textmarken_werte": werte, "seq": seq, "bereiche": tabellen_bereiche(ed),
            "stilref": stilref, "autor": autor, "pfad": pfad, "in_tabelle": ed.textCursor().currentTable() is not None}


def feld_einfuegen(ed, anweisung: str, text: str, versteckt: bool = False) -> None:
    """``versteckt``: ausgeblendeter Text (TC-Einträge stehen wie in Word unsichtbar im Text)."""
    from lunivo_writer.editor.zusatz import P_VERSTECKT
    c = ed.textCursor()
    f = c.charFormat()
    f.setProperty(P_FELD, anweisung)
    if versteckt:
        f.setProperty(P_VERSTECKT, 1)
    c.insertText(text, f)
    f.clearProperty(P_FELD); f.clearProperty(P_VERSTECKT)
    c.setCharFormat(f)                                      # danach geschriebener Text gehört nicht mehr zum Feld
    ed.setTextCursor(c)
    ed.document().setModified(True)
