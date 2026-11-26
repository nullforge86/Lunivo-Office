"""Beschriftungen und Hinweise der Bearbeitung von Kopf- und Fußzeile auf dem Blatt – die eine Stelle für diese Texte."""
from __future__ import annotations

ZONEN = ("kopf", "fuss")
ZONE_VORGABE = "kopf"
ZONENNAMEN = {"kopf": "Kopfzeile", "fuss": "Fußzeile"}
ZUSATZ_GERADE = "gerader Seiten"
ZUSATZ_UNGERADE = "ungerader Seiten"
KENNUNG_GERADE = "even_"                      # so beginnt der Feldname der Zeile für gerade Seiten

PANEL_FORMAT = "Format"
PANEL_POSITION = "Position:"
PANEL_BEREICH = "Übernehmen für:"
PANEL_OK = "OK"
NUMMERIERUNG = "Seitennummerierung"
NUMMERIERUNG_FORTSETZEN = "Nummerierung fortsetzen"

HINWEIS_DOPPELKLICK = "Doppelklick bearbeitet die {name}"     # Hinweis beim Überfahren des Kopf- bzw. Fußbereichs
HINWEIS_NICHT_DARSTELLBAR = "Das lässt sich nur für die erste Seite oder einen ganzen Abschnitt einstellen."
HINWEIS_KEINE_SEITENZAHL = "Hier steht keine Seitenzahl."

FELD_SEITE = "PAGE"                           # Feld im Text der Zeile: die Nummer der Seite
FELD_SEITEN = "PAGES"                         # Feld im Text der Zeile: die Anzahl der Seiten
MARKE_SEITENZAHL = "{" + FELD_SEITE           # so beginnt ein Seitenzahl-Feld im Text ({PAGE} und {PAGES})
TABULATOR = "\t"


def etikett(zone: str, gerade_ungerade: bool, feldname: str) -> str:
    """Das Etikett am Bereich: „Kopfzeile“ / „Fußzeile“, bei „Gerade und ungerade Seiten unterschiedlich“ mit dem Zusatz, für welche Seiten."""
    name = ZONENNAMEN[zone]
    if gerade_ungerade:
        return name + " " + (ZUSATZ_GERADE if feldname.startswith(KENNUNG_GERADE) else ZUSATZ_UNGERADE)
    return name
