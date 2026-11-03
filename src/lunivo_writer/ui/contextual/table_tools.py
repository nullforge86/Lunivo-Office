"""Kontext-Reiter „Tabellentools“ (erscheint, wenn die Schreibmarke in einer Tabelle steht)."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k


# Namen und Reihenfolge wie in der Vorlage; „Einfügen“ und „Löschen“ kommen aus ``core/tabellenaktionen.py`` (dieselbe Definition wie Mini-Leiste und Kontextmenü)
TABELLENTOOLS = {"name": "Tabellentools", "kontext": "tabelle", "gruppen": [
    {"name": "Tabelle", "reihenfolge": True, "knoepfe": [
        _k("tabelleEigenschaften", "Tabelleneigenschaften", "tabelleEigenschaften", text=True),
        _k("tabelleGitternetz", "Gitternetzlinien anzeigen", "tabelleGitternetz", haken=True, text=True),
        _k("tabelleZeichnen", "Tabelle zeichnen", "tabelleZeichnen", gross=True),
        _k("tabelleRadierer", "Radiergummi", "tabelleRadierer", gross=True),
        _k("tabelleLoeschen", "Löschen", klappe="tabelleLoeschenAktionen", gross=True)]},
    {"name": "Zeilen und Spalten", "reihenfolge": True, "knoepfe": [
        _k("tabelleZeileOben", "Darüber einfügen", "tabelleZeileOben", text=True),
        _k("tabelleZeileUnten", "Darunter einfügen", "tabelleZeileUnten", text=True),
        _k("tabelleSpalteLinks", "Links einfügen", "tabelleSpalteLinks", text=True),
        _k("tabelleSpalteRechts", "Rechts einfügen", "tabelleSpalteRechts", text=True)]},
    {"name": "Zellen", "reihenfolge": True, "knoepfe": [
        _k("tabelleVerbinden", "Zellen zusammenführen", "tabelleVerbinden", gross=True),
        _k("tabelleTeilen", "Zellen teilen", "tabelleTeilen", text=True),
        _k("tabelleTabelleTeilen", "Tabelle teilen", "tabelleTabelleTeilen", text=True),
        _k("tabelleAutoAnpassen", "AutoAnpassen", klappe="tabelleAutoAnpassen", gross=True),
        _k("sortieren", "Tabelle sortieren", "tabelleSortieren", text=True)]},
    {"name": "Zellengröße", "felder": "masse", "praefix": "tab_", "befehl": "tabelleMasse", "verhaeltnis": False, "knoepfe": []},
    {"name": "Ausrichtung", "knoepfe": [
        _k("zelleOben", "Oben ausrichten", "zelleOben"),
        _k("zelleMitte", "Mittig ausrichten", "zelleMitte"),
        _k("zelleUnten", "Unten ausrichten", "zelleUnten"),
        _k("links", "Links im Feld", "zelleLinks"),
        _k("mitte", "Zentriert im Feld", "zelleZentriert"),
        _k("rechts", "Rechts im Feld", "zelleRechts"),
        _k("tabelleTextrichtung", "Textrichtung", klappe="tabelleTextrichtung")]},
    {"name": "Schrift", "felder": "tab_zeile", "knoepfe": [
        _k("groesserA", "Schrift vergrößern", "schriftGroesser"),
        _k("kleinerA", "Schrift verkleinern", "schriftKleiner"),
        {"zeilenumbruch": True},
        _k("F", "Fett", "fett", haken=True),
        _k("K", "Kursiv", "kursiv", haken=True),
        _k("U", "Unterstrichen", "unter", haken=True)]},
]}


# Reiter „Tabellenstil“ neben „Tabellentools“ (gleicher Kontext: beide erscheinen, wenn die Schreibmarke in einer Tabelle steht)
TABELLENSTIL = {"name": "Tabellenstil", "kontext": "tabelle", "gruppen": [
    {"name": "Tabellenformatvorlagen", "knoepfe": [
        _k("tabelle", "Tabellenformatvorlagen", klappe="tabelleVorlagen", gross=True),
        _k("haken", "Kopfzeile", "tabelleKopfzeile", haken=True, text=True),
        _k("haken", "Gebänderte Zeilen", "tabelleStreifen", haken=True, text=True),
        _k("haken", "Erste Spalte", "tabelleErsteSpalte", haken=True, text=True)]},
    {"name": "Rahmen und Farbe", "knoepfe": [
        _k("rahmen", "Rahmenlinien ein/aus", "tabelleRahmen", True, haken=True),
        _k("toenung", "Zellenschattierung", klappe="tabelleSchattierung", gross=True)]},
]}
