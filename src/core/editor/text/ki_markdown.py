"""KI-Antworten als Markdown: die eine Stelle, die Chat-Anzeige, Vorschau und Übernahme ins Dokument gemeinsam nutzen. Qt-frei.

Einfaches Markdown (Überschriften, Aufzählungen, Nummerierungen, Fett, Kursiv, Code) wird in Absätze des Dokumentenmodells zerlegt (``markdown_bloecke``);
eine eigene Syntax darüber hinaus gibt es nicht. Davor sorgt ``normalisieren`` für die Regeln, die für alle gelten: einzelne Zeilenumbrüche bleiben
Zeilenumbrüche, rohe Auszeichnungen im Text werden nicht gedeutet.

* ``hat_struktur(text)`` — gibt es Überschriften, Listen, Tabellen oder Hervorhebungen? Wenn nicht, bleibt der Text einfacher Text.
* ``klartext(text)`` — der sichtbare Text ohne Markdown-Zeichen.
* ``markdown_bloecke(text)`` — die Absätze ``{"text", "vorlage", "liste", "laeufe"}``, die die Übernahme ins Dokument über die zentrale Bearbeitung schreibt.
"""
from __future__ import annotations

import re

_BLOCKANFANG = re.compile(r"^\s*(?:[-*+]\s|\d+[.)]\s|#{1,6}\s|>|\||```|~~~|-{3,}\s*$|\*{3,}\s*$|={3,}\s*$)")
_ROHE_MARKE = re.compile(r"<(?=[A-Za-z/!?])")
_TABELLENZEILE = re.compile(r"^\s*\|.+\|\s*$")
AUFZAEHLUNG_EBENEN = ("disc", "circle", "square")            # Aufzählungszeichen je Ebene


def normalisieren(text: str) -> str:
    """Einheitliche Vorbereitung: einzelne Zeilenumbrüche werden harte Umbrüche (außer vor Listen, Tabellen, Überschriften, Codeblöcken);
    ``<`` vor Buchstaben wird maskiert, damit nichts als Auszeichnung gedeutet wird."""
    zeilen = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    aus: list[str] = []
    im_code = False
    for i, z in enumerate(zeilen):
        if z.lstrip().startswith(("```", "~~~")):
            im_code = not im_code
            aus.append(z)
            continue
        if im_code:
            aus.append(z)
            continue
        z = _ROHE_MARKE.sub("\\<", z)
        weiter = zeilen[i + 1] if i + 1 < len(zeilen) else ""
        if z.strip() and weiter.strip() and not z.endswith("  ") and not _BLOCKANFANG.match(z) and not _BLOCKANFANG.match(weiter):
            z += "  "
        aus.append(z)
    return "\n".join(aus)


_INLINE = re.compile(r"\*\*(.+?)\*\*|__(.+?)__|\*(?!\s)(.+?)(?<!\s)\*|(?<!\w)_(?!\s)(.+?)(?<!\s)_(?!\w)|`(.+?)`")


def _inline(zeile: str) -> tuple:
    """Fett (**…**), kursiv (*…*), Code (`…`) aus einer Zeile: (reiner Text, [(von, bis, Zeichenformat)])."""
    text, laeufe, pos = "", [], 0
    for m in _INLINE.finditer(zeile):
        text += zeile[pos:m.start()]
        inhalt = next(g for g in m.groups() if g is not None)
        fmt = ({"fett": True} if m.group(1) or m.group(2) else {"kursiv": True} if m.group(3) or m.group(4) else {"schrift": "Courier New"})
        laeufe.append((len(text), len(text) + len(inhalt), fmt))
        text += inhalt
        pos = m.end()
    return text + zeile[pos:], laeufe


def markdown_bloecke(text: str) -> list:
    """Einfaches Markdown (Überschriften, Aufzählungen, Nummerierungen, Fett, Kursiv, Code) als Absatzliste:
    ``{"text", "vorlage", "liste", "laeufe"}`` je Absatz. Qt-frei."""
    aus = []
    for zeile in text.replace("\r\n", "\n").split("\n"):
        vorlage, liste = "", ""
        if m := re.match(r"^\s{0,3}(#{1,6})\s+(.*)$", zeile):
            vorlage, zeile = f"Überschrift {min(len(m.group(1)), 9)}", m.group(2)
        elif m := re.match(r"^\s*[-*+]\s+(.*)$", zeile):
            liste, zeile = "disc", m.group(1)
        elif m := re.match(r"^\s*\d+[.)]\s+(.*)$", zeile):
            liste, zeile = "dezimal", m.group(1)
        klar, laeufe = _inline(zeile)
        if vorlage:
            laeufe = []
        aus.append({"text": klar, "vorlage": vorlage, "liste": liste, "laeufe": laeufe})
    return aus or [{"text": "", "vorlage": "", "liste": "", "laeufe": []}]


def hat_struktur(text: str) -> bool:
    """Wahr, wenn der Text Überschriften, Listen, Tabellen oder Hervorhebungen enthält. Sonst bleibt er einfacher Text (auch ohne Markdown-Deutung)."""
    if not text or not text.strip():
        return False
    if any(_TABELLENZEILE.match(z) for z in text.split("\n")):
        return True
    return any(b["vorlage"] or b["liste"] or b["laeufe"] for b in markdown_bloecke(text))


def klartext(text: str) -> str:
    """Der sichtbare Text ohne Markdown-Zeichen (z. B. für Zähler und Vergleiche)."""
    return "\n".join(b["text"] for b in markdown_bloecke(text))
