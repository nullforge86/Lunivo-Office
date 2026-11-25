"""Zusatzdaten am Text: Kommentare, Fuß-/Endnoten, nachverfolgte Änderungen.

Im Dokumentenmodell hängen sie als Schlüssel am Zeichenformat (``kommentar``, ``note``, ``aenderung`` …, siehe ``core/document/formate.py``); hier stehen
nur noch Namen, Farben und Hilfen für die Fenster. Die Texte der Kommentare und Noten liegen in `meta`:

    meta["kommentare"] = {id: {"autor", "initialen", "datum", "text"}}
    meta["noten"]      = {"f": {id: text}, "e": {id: text}}      # Fußnoten, Endnoten
"""
from __future__ import annotations

from core.dokument.farben import Farbe
KI_AUTOR = "KI"                                   # Autor nachverfolgter Änderungen, die die KI-Überarbeitung einträgt

ROEMISCH = [(1000, "m"), (900, "cm"), (500, "d"), (400, "cd"), (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
            (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]


def roemisch(n: int) -> str:
    s = ""
    for w, r in ROEMISCH:
        while n >= w:
            s += r; n -= w
    return s


def neue_id(vorhanden) -> int:
    return max([int(k) for k in vorhanden] + [0]) + 1


def leere_meta() -> dict:
    return {"kommentare": {}, "noten": {"f": {}, "e": {}}, "quellen": [], "zitierweise": "APA"}


BESCHRIFTUNGEN = ("Abbildung", "Tabelle", "Gleichung")



# Farben der Kommentare wie in der alten Fassung: orange Kreis mit Initial, gelbe Markierung im Text; ein gelöster Kommentar wird grau
AUTOR_FARBEN = [Farbe.ROT, "#1971c2", Farbe.GRUEN, Farbe.ORANGE, "#7048a8", "#0b7285", "#a61e4d", "#5c940d"]      # eine Farbe je Autor — die einzige Liste dafür
KOMMENTAR_FARBE = "#d9822b"
KOMMENTAR_GELOEST = Farbe.GRAU_HELL


def kommentar_farbe(geloest: bool = False) -> str:
    return KOMMENTAR_GELOEST if geloest else KOMMENTAR_FARBE
