"""Groß-/Kleinschreibung und Sortierreihenfolge als reine Textfunktionen (ohne Oberfläche, einzeln testbar)."""
from __future__ import annotations

import re

# Schlüssel und Text im Fenster „Groß-/Kleinschreibung“ — in der Reihenfolge und mit den Worten der Vorlage
SCHREIBWEISEN = (("satz", "Ersten Buchstaben im Satz groß schreiben"), ("lower", "Kleinbuchstaben"), ("upper", "Großbuchstaben"),
                 ("toggle", "gROSS-/kLEINSCHREIBUNG umkehren"), ("title", "Erster Buchstabe groß"))


def umwandeln(text: str, art: str) -> str:
    if art == "upper":
        return text.upper()
    if art == "lower":
        return text.lower()
    if art == "title":
        return re.sub(r"[^\W\d_]+(?:['’][^\W\d_]+)?", lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), text)
    if art == "toggle":
        return text.swapcase()
    if art == "satz":
        return re.sub(r"(^\s*|[.!?…]\s+)([^\W\d_])", lambda m: m.group(1) + m.group(2).upper(), text.lower())
    raise ValueError(art)


def _zahl(t: str) -> float:
    """Die erste Zahl im Text (Komma oder Punkt als Dezimalzeichen); ohne Zahl ganz vorn."""
    m = re.search(r"-?\d+(?:[.,]\d+)?", t.replace(" ", ""))
    return float(m.group(0).replace(",", ".")) if m else float("-inf")


def _datum(t: str) -> tuple:
    m = re.search(r"(\d{1,2})\.(\d{1,2})\.(\d{2,4})", t)
    return (int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else (0, 0, 0)


def sortiert(texte: list[str], *, absteigend: bool = False, typ: str = "text", gross_klein: bool = False) -> list[str]:
    """Die Texte in der gewünschten Reihenfolge. ``typ``: ``text``, ``zahl`` (erste Zahl im Text) oder ``datum`` (TT.MM.JJJJ)."""
    schluessel = {"zahl": _zahl, "datum": _datum}.get(typ) or (lambda t: t if gross_klein else t.casefold())
    return sorted(texte, key=schluessel, reverse=absteigend)


# ---- „Text sortieren“ mit Feldern (Start ▸ Absatz ▸ Sortieren) ----------------------------------------------------------------------------
SPRACHEN = (("de_DE", "Deutsch (Deutschland)"), ("de_AT", "Deutsch (Österreich)"), ("de_CH", "Deutsch (Schweiz)"), ("en_GB", "Englisch (Großbritannien)"),
            ("en_US", "Englisch (USA)"), ("fr_FR", "Französisch"), ("it_IT", "Italienisch"), ("es_ES", "Spanisch"), ("nl_NL", "Niederländisch"),
            ("pl_PL", "Polnisch"), ("tr_TR", "Türkisch"))


def felder(text: str, trenner: str) -> list[str]:
    """Die Felder eines Absatzes (getrennt durch Tab, Komma oder ein anderes Zeichen)."""
    return text.split(trenner) if trenner else [text]


def feldzahl(texte: list[str], trenner: str) -> int:
    return max((len(felder(t, trenner)) for t in texte), default=1)


def reihenfolge(texte: list[str], schluessel: list[tuple[int | None, str, bool]], *, trenner: str = "\t", gross_klein: bool = False,
                sprache: str = "de_DE", kopfzeile: bool = False) -> list[int]:
    """Neue Reihenfolge der Absätze (Indizes). ``schluessel``: bis zu drei (Feld oder None für den ganzen Absatz, Typ, absteigend) — der erste
    entscheidet zuerst. Text wird nach den Regeln der Sortiersprache verglichen; ``kopfzeile`` lässt den ersten Absatz oben stehen."""
    from functools import cmp_to_key
    from PySide6.QtCore import QCollator, QLocale, Qt
    col = QCollator(QLocale(sprache))
    col.setCaseSensitivity(Qt.CaseSensitive if gross_klein else Qt.CaseInsensitive)
    col.setNumericMode(False)

    def wert(i: int, feld: int | None) -> str:
        t = texte[i]
        if feld is None:
            return t
        f = felder(t, trenner)
        return f[feld].strip() if feld < len(f) else ""

    start = 1 if kopfzeile and texte else 0
    idx = list(range(start, len(texte)))
    for feld, typ, ab in reversed([s for s in schluessel if s is not None]):        # stabil: zuletzt nach dem wichtigsten Schlüssel
        if typ == "zahl":
            idx.sort(key=lambda i: _zahl(wert(i, feld)), reverse=ab)
        elif typ == "datum":
            idx.sort(key=lambda i: _datum(wert(i, feld)), reverse=ab)
        else:
            idx.sort(key=cmp_to_key(lambda a, b: col.compare(wert(a, feld), wert(b, feld))), reverse=ab)
    return list(range(start)) + idx


def absaetze(doc, von: int | None = None, bis: int | None = None) -> list:
    """Die Absätze zwischen ``von`` und ``bis`` (ohne Angabe: das ganze Dokument). → [] wenn eine Tabelle dazwischenliegt."""
    from PySide6.QtGui import QTextCursor
    b = doc.findBlock(von) if von is not None else doc.firstBlock()
    out = []
    while b.isValid() and (bis is None or b.position() <= bis):
        if QTextCursor(b).currentTable() is not None:
            return []
        out.append(b); b = b.next()
    return out


def umstellen(doc, bloecke: list, ordnung: list[int]) -> None:
    """Stellt die (aufeinanderfolgenden) Absätze ``bloecke`` in die Reihenfolge ``ordnung`` — mit Absatz- und Zeichenformat, als ein Rückgängig-Schritt."""
    from PySide6.QtGui import QTextCursor
    if not bloecke or ordnung == list(range(len(bloecke))):
        return
    teile = []
    for b in bloecke:
        c = QTextCursor(b); c.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
        teile.append((c.selection(), b.blockFormat(), b.charFormat()))
    c = QTextCursor(doc)
    c.beginEditBlock()
    c.setPosition(bloecke[0].position())
    c.setPosition(bloecke[-1].position() + bloecke[-1].length() - 1, QTextCursor.KeepAnchor)
    c.removeSelectedText()
    for n, i in enumerate(ordnung):
        frag, bf, cf = teile[i]
        if n:
            c.insertBlock(bf, cf)
        else:
            c.setBlockFormat(bf); c.setBlockCharFormat(cf)
        c.insertFragment(frag)
    c.endEditBlock()
