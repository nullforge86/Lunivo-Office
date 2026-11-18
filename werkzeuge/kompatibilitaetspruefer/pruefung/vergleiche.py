"""Gemeinsame Vergleichsfunktionen für Zählwerte und Texte. Beide Seiten sind Messwerte; es wird nichts geschätzt."""
from __future__ import annotations

import difflib
import re

from . import klassifikation as K

LABEL = {
    "absaetze": "Absätze (gesamt)", "nichtleere_absaetze": "Absätze mit Text", "zeichen": "Zeichen (ohne Leerraum)", "woerter": "Wörter",
    "tabellen": "Tabellen", "verschachtelte_tabellen": "Verschachtelte Tabellen", "tabellenzellen": "Tabellenzellen", "bilder": "Bilder",
    "abschnitte": "Abschnitte", "fussnoten": "Fußnoten", "endnoten": "Endnoten", "kommentare": "Kommentare", "listen_absaetze": "Listenabsätze",
    "ueberschriften": "Überschriften", "fett_zeichen": "Fette Zeichen", "kursiv_zeichen": "Kursive Zeichen",
    "unterstrichen_zeichen": "Unterstrichene Zeichen", "mitte_absaetze": "Zentrierte Absätze", "rechts_absaetze": "Rechtsbündige Absätze",
    "block_absaetze": "Blocksatz-Absätze", "seiten": "Seitenanzahl", "objekte_frei": "Frei positionierte Objekte",
    "formatvorlagen": "Formatvorlagen", "listen_definitionen": "Listendefinitionen",
}
STRUKTURSCHLUESSEL = ("absaetze", "nichtleere_absaetze", "zeichen", "woerter", "tabellen", "verschachtelte_tabellen", "tabellenzellen", "bilder", "abschnitte",
                      "fussnoten", "endnoten", "kommentare", "listen_absaetze", "ueberschriften", "objekte_frei", "formatvorlagen", "listen_definitionen")
FORMATSCHLUESSEL = ("fett_zeichen", "kursiv_zeichen", "unterstrichen_zeichen", "mitte_absaetze", "rechts_absaetze", "block_absaetze")
NICHT_GEPRUEFT_STRUKTUR = ("Listen und Nummerierungen (Inhalt der Nummern)", "Kopf- und Fußzeilen", "Felder und Verweise", "Formatvorlagen-Zuordnung",
                           "Tabelleninhalt je Zelle (nur Summen)")
NICHT_GEPRUEFT_FORMAT = ("Schriftart und -größe", "Farben", "Absatzabstände und Einzüge", "Zeichenabstände", "Formatierung aus Formatvorlagen (Vererbung)")


def norm(s: str) -> str:
    return re.sub(r"[\s​￼ ]+", "", s)


def vergleiche_werte(soll: dict, ist: dict, schluessel, fehlerart: str, *, format_: bool = False, nur_verlust: bool = False,
                     soll_name: str = "Referenz", ist_name: str = "Lunivo") -> list[dict]:
    """Je Schlüssel einen Prüfpunkt. Schlüssel ohne Referenzwert werden nicht aufgeführt (sie sind weder bestanden noch auffällig)."""
    aus = []
    for k in schluessel:
        s = soll.get(k)
        if s is None:
            continue
        name = LABEL.get(k, k)
        if k not in ist or ist[k] is None:
            aus.append(K.nicht_pruefbar(name, f"{ist_name} liefert keinen Wert für „{name}“"))
            continue
        i = ist[k]
        if s == i or (nur_verlust and i >= s):
            aus.append(K.passt(name, f"{soll_name} {s} · {ist_name} {i}", s, i))
            continue
        if format_:
            schwere = K.schwere_format(s, i)
        else:
            schwere = K.schwere_menge(s, i)
            if k == "absaetze" and soll.get("nichtleere_absaetze") == ist.get("nichtleere_absaetze") and "nichtleere_absaetze" in soll:
                schwere = "gering"                                # nur leere Absätze unterscheiden sich
        richtung = "fehlen" if i < s else "zusätzlich"
        aus.append(K.befund(name, K.ABWEICHEND, fehlerart, schwere, f"{name}: {soll_name} {s}, {ist_name} {i} ({abs(s - i)} {richtung})", s, i))
    return aus


def vergleiche_texte(soll: list[str], ist: list[str], fehlerart: str, soll_name: str = "Referenz", ist_name: str = "Lunivo") -> list[dict]:
    """Textinhalt und Reihenfolge der Absätze mit Text. In den Befunden stehen nur Zahlen und Positionen, nie Dokumenttext."""
    a = [x for x in (norm(t) for t in soll) if x]
    b = [x for x in (norm(t) for t in ist) if x]
    if a == b:
        return [K.passt("Textinhalt und Reihenfolge", f"{len(a)} Absätze mit Text stimmen überein", len(a), len(b))]
    erste = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    if sorted(a) == sorted(b):
        return [K.befund("Textinhalt und Reihenfolge", K.ABWEICHEND, fehlerart, "schwer",
                         f"Gleicher Text, aber andere Reihenfolge der Absätze; erste Abweichung bei Absatz {erste + 1} (nur Absätze mit Text gezählt)",
                         len(a), len(b), element=f"Absatz {erste + 1}")]
    zeichen_a, zeichen_b = sum(map(len, a)), sum(map(len, b))
    if len(a) <= 4000 and len(b) <= 4000:
        ops = [o for o in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes() if o[0] != "equal"]
        ersetzt = sum(max(o[2] - o[1], o[4] - o[3]) for o in ops if o[0] == "replace")
        fehlend = sum(o[2] - o[1] for o in ops if o[0] == "delete")
        zusaetzlich = sum(o[4] - o[3] for o in ops if o[0] == "insert")
        teile = [f"{n} {t}" for n, t in ((ersetzt, "Absätze verändert"), (fehlend, "Absätze fehlen"), (zusaetzlich, "Absätze zusätzlich")) if n]
        beschreibung = "Text weicht ab: " + ", ".join(teile) + f"; erste Abweichung bei Absatz {erste + 1}"
        betroffen = ersetzt + fehlend + zusaetzlich
    else:
        betroffen = sum(1 for x, y in zip(a, b) if x != y) + abs(len(a) - len(b))
        beschreibung = f"Text weicht ab (großes Dokument, Positionsvergleich): {betroffen} Absätze betroffen; erste Abweichung bei Absatz {erste + 1}"
    if not b and a:
        schwere = "kritisch"
    elif betroffen / max(len(a), 1) >= 0.5 or (zeichen_a and zeichen_b < zeichen_a * 0.5):
        schwere = "schwer"
    else:
        schwere = "mittel"
    return [K.befund("Textinhalt und Reihenfolge", K.ABWEICHEND, fehlerart, schwere, beschreibung + f" ({soll_name}: {zeichen_a} Zeichen, {ist_name}: {zeichen_b})",
                     len(a), len(b), element=f"Absatz {erste + 1}")]
