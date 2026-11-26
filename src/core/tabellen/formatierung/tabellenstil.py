"""Tabellenformatvorlagen und Formatoptionen (Kopfzeile, gebänderte Zeilen, erste Spalte).

Die Vorlage wird auf die Zellen angewendet (Füllung, Fettdruck, Rahmen) — nicht als lebende Verknüpfung: spätere Änderungen an
einzelnen Zellen bleiben erhalten, bis die Vorlage erneut angewendet wird. Angewendet wird sie über die zentrale Bearbeitung
(``KernBefehle.tabelle_vorlage``); hier stehen nur die Vorlagenwerte und die Streifenregel."""
from __future__ import annotations

# Name: (Kopf-Füllung, Kopf-Schrift, Streifen-Füllung, Rahmen)
from core.formatierung.farben.farben import Farbe
VORLAGEN = {
    "Gitternetz": (None, None, None, 1),
    "Einfach": (None, None, None, 0),
    "Blau": (Farbe.AKZENT, Farbe.WEISS, "#e7f0fa", 1),
    "Grün": ("#2d8a4e", Farbe.WEISS, "#e6f4ea", 1),
    "Orange": ("#e67700", Farbe.WEISS, "#fff0e0", 1),
    "Grau": ("#495057", Farbe.WEISS, "#f1f3f5", 1),
    "Hell": ("#dee2e6", Farbe.SCHWARZ, "#f8f9fa", 0),
}


def zeilengrund(r: int, kopf: bool, kopf_fill: str, streifen_fill: str) -> str:
    """Hintergrundfarbe der Zeile ``r``: Kopfzeile, jede zweite Zeile darunter als Streifen, sonst keine (leer)."""
    if kopf and r == 0 and kopf_fill:
        return kopf_fill
    return streifen_fill if streifen_fill and (r - (1 if kopf else 0)) % 2 == 1 else ""
