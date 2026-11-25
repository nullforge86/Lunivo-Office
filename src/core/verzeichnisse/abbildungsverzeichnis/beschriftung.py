"""Beschriftungen („Abbildung 1: Text“): Nummern, Liste der Beschriftungen und Einfügen. Alles wirkt über die Bearbeitungssitzung auf das Dokumentmodell; Stellen im
Text sind Zeichenstellen des Rohtextes (Absätze durch ein Zeichen getrennt, wie ``textCursor().position()``)."""
from __future__ import annotations

import re

from core.dokument.dokument import Auswahl, Lauf, Position
from core.listen.listen import nummer_text

# Zahlschreibweise der Beschriftung (editor/text/zahlformat.py) ↔ Zahlenart des Modells ↔ Schalter des Felds SEQ
SEQ_FORMAT = {"arabisch": "ARABIC", "gross": "ALPHABETIC", "klein": "alphabetic", "roemisch": "ROMAN", "roemisch_klein": "roman"}
ZAHLENART = {"arabisch": "dezimal", "gross": "gross", "klein": "klein", "roemisch": "roem_gross", "roemisch_klein": "roem_klein"}


def seq_format(anweisung: str) -> str:
    """Zahlschreibweise aus einer Feldanweisung ``SEQ Abbildung \\* ROMAN`` (Vorgabe arabisch)."""
    m = re.search(r"\\\*\s*(\w+)", anweisung)
    if m:
        for k, v in SEQ_FORMAT.items():
            if v == m.group(1):
                return k
    return "arabisch"


def seq_lauf(a):
    """(Versatz, Lauf) des SEQ-Feldes eines Absatzes, sonst ``None``."""
    versatz = 0
    for x in a.inhalte:
        n = len(x.text) if isinstance(x, Lauf) else 1
        if isinstance(x, Lauf) and str(x.format.get("feld", "")).upper().startswith("SEQ"):
            return versatz, x
        versatz += n
    return None


def beschriftungen_liste(k) -> list[dict]:
    """[{label, text, pos, block}] — die Beschriftungsabsätze in Dokumentreihenfolge (``pos``: Stelle im Rohtext, ``block``: Id des Absatzes)."""
    d = k.sitzung.dokument
    aus, n = [], 0
    for a in d.absaetze():
        if a.format.get("beschriftung") and a.text().strip():
            aus.append({"label": a.format["beschriftung"], "text": a.text().strip(), "pos": n, "block": a.id})
        n += a.laenge + 1
    return aus


def naechste_nummer(k, label: str, zahl: str = "arabisch") -> str:
    """Nummer, die eine neue Beschriftung ``label`` an der Schreibmarke bekäme (für die Anzeige im Fenster)."""
    pos = k.position()
    n = 1 + sum(1 for k in beschriftungen_liste(k) if k["label"] == label and k["pos"] < pos)
    return nummer_text(ZAHLENART.get(zahl, "dezimal"), n)


def beschriftung_einfuegen(k, label: str, text: str, oben: bool = False, *, nach: str | None = None,
                           ohne_bezeichnung: bool = False, zahl: str = "arabisch") -> None:
    """Beschriftung „Abbildung 1: Text“ unter (``oben``: über) dem Objekt oder Absatz. ``nach`` ersetzt „: Text“ durch genau diesen
    Text hinter der Nummer, ``ohne_bezeichnung`` lässt „Abbildung “ weg, ``zahl`` ist die Schreibweise der Nummer."""
    s = k.sitzung
    t = k.tabelle_an_marke()
    if t is not None:
        block = t.id
    else:
        block = s.auswahl.kopf.absatz_id
    schluss = nach if nach is not None else (": " + text if text else "")

    def f(sitz):
        with sitz.gruppe("Beschriftung"):
            neu = sitz.beschriftung_einfuegen(label, "", block, davor=oben, zahlenart=ZAHLENART.get(zahl, "dezimal"))
            a = sitz._absatz(neu)
            if ohne_bezeichnung:                                    # „Abbildung “ vor der Nummer weglassen
                sitz.loeschen(Auswahl(Position(neu, 0), Position(neu, len(label) + 1)))
            if schluss:
                sitz.text_einfuegen(schluss, Position(neu, sitz._absatz(neu).laenge))
            sitz.absatzformat_anwenden({"abstand_vor": 4 / 0.75, "abstand_nach": 8 / 0.75}, absatz_ids=[neu])
            sitz.zeichenformat_anwenden({"kursiv": True, "groesse_pt": 9.0, "farbe": "#44546a"}, Auswahl(Position(neu, 0), Position(neu, sitz._absatz(neu).laenge)))
            sitz.setze_auswahl(Position(neu, sitz._absatz(neu).laenge))
    k.aendern(f)


def beschriftungen_nummerieren(k) -> None:
    k.aendern(lambda s: s.beschriftungen_nummerieren())
