"""Trenner und Zellenteilung für das Fenster „Text in Tabelle umwandeln“ (Einfügen ▸ Tabelle). Keine Oberfläche, kein Dokumentzugriff: die Umwandlung selbst
leisten ``Bearbeitungssitzung.text_zu_tabelle`` und ``tabelle_zu_text`` (``core/editing/tabellenbearbeitung.py``)."""
from __future__ import annotations

# Schlüssel → Beschriftung im Fenster („Andere“ gibt der Benutzer selbst ein)
TRENNER = [("\n", "Absatzmarken"), ("\t", "Tabstopps"), (";", "Semikolons"), (",", "Kommata"), (" ", "Leerzeichen")]


def zellen(texte: list[str], trenner: str) -> list[list[str]]:
    """Absätze in Zeilen und Zellen teilen. Bei „Absatzmarken“ wird jeder Absatz eine Zeile mit einer Zelle."""
    if trenner == "\n" or not trenner:
        return [[t] for t in texte]
    return [t.split(trenner) for t in texte]
