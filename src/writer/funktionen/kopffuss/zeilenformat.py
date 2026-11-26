"""Zeichenformat einer Kopf- oder Fußzeile: übersetzt zwischen den Namen, mit denen die Start-Werkzeuge ein Zeichenformat ändern
(``fett``, ``schrift``, ``groesse_pt`` …), und den Namen im Format der Zeile in der Seiteneinrichtung (``bold``, ``family``, ``size_pt`` …).

So wirken Schrift, Größe, Fett, Kursiv, Unterstrichen, Durchgestrichen, Farbe, Hervorheben und Hoch-/Tiefstellen auf die ganze Zeile,
solange die Schreibmarke im Kopf- oder Fußfeld steht."""
from __future__ import annotations

# Name im Zeichenformat des Textes → Name im Format der Zeile
NAMEN = {"schrift": "family", "groesse_pt": "size_pt", "fett": "bold", "kursiv": "italic", "unterstrichen": "underline",
         "durchgestrichen": "strike", "farbe": "color", "marker": "highlight"}
HOCH_TIEF = {"hoch": "sup", "tief": "sub"}                # Wert von ``hoch_tief`` → Wert von ``script``
STELLUNG_TEXT, STELLUNG_ZEILE = "hoch_tief", "script"


def aendern(fmt: dict, aenderung: dict) -> dict:
    """Das Format der Zeile nach einer Änderung der Start-Werkzeuge; ein leerer Wert nimmt die Eigenschaft weg. Unbekannte Namen bleiben ohne Wirkung."""
    neu = dict(fmt)
    for name, wert in aenderung.items():
        if name == STELLUNG_TEXT:
            ziel, wert = STELLUNG_ZEILE, HOCH_TIEF.get(wert)
        elif name in NAMEN:
            ziel = NAMEN[name]
        else:
            continue
        if wert:
            neu[ziel] = wert
        else:
            neu.pop(ziel, None)
    return neu


def als_zeichenformat(fmt: dict, groesse_vorgabe_pt: float) -> dict:
    """Das Format der Zeile mit den Namen der Start-Werkzeuge (für deren Schalterstellung); ohne eigene Größe gilt ``groesse_vorgabe_pt``."""
    zurueck = {ziel: name for name, ziel in NAMEN.items()}
    zeichen = {zurueck[ziel]: wert for ziel, wert in fmt.items() if ziel in zurueck and wert}
    stellung = {wert: name for name, wert in HOCH_TIEF.items()}.get(fmt.get(STELLUNG_ZEILE))
    if stellung:
        zeichen[STELLUNG_TEXT] = stellung
    zeichen.setdefault("groesse_pt", groesse_vorgabe_pt)
    return zeichen
