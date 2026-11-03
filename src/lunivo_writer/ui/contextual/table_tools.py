"""Kontext-Reiter „Tabellentools“ (erscheint, wenn die Schreibmarke in einer Tabelle steht)."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k


TABELLENTOOLS = {"name": "Tabellentools", "kontext": "tabelle", "gruppen": [
    {"name": "Tabelle", "knoepfe": [
        _k("stift", "Tabelle zeichnen", "tabelleZeichnen", gross=True),
        _k("table-properties", "Tabellen-eigenschaften", "tabelleEigenschaften", gross=True),
        _k("grid-3x3", "Gitternetz-linien anzeigen", "tabelleGitternetz", haken=True, gross=True)]},
    {"name": "Tabellenformatvorlagen", "knoepfe": [
        _k("tabelle", "Tabellenformatvorlagen", klappe="tabelleVorlagen", gross=True),
        _k("haken", "Kopfzeile", "tabelleKopfzeile", haken=True, text=True),
        _k("haken", "Gebänderte Zeilen", "tabelleStreifen", haken=True, text=True),
        _k("haken", "Erste Spalte", "tabelleErsteSpalte", haken=True, text=True)]},
    {"name": "Entwurf: Rahmen und Farbe", "knoepfe": [
        _k("rahmen", "Rahmenlinien ein/aus", "tabelleRahmen", True, haken=True),
        _k("toenung", "Zellenschattierung", klappe="tabelleSchattierung", gross=True)]},
    {"name": "Layout: Zeilen und Spalten", "knoepfe": [
        _k("kanteOben", "Zeile oberhalb einfügen", "tabelleZeileOben"),
        _k("kanteUnten", "Zeile unterhalb einfügen", "tabelleZeileUnten"),
        _k("kanteLinks", "Spalte links einfügen", "tabelleSpalteLinks"),
        _k("kanteRechts", "Spalte rechts einfügen", "tabelleSpalteRechts"),
        _k("//", "x"),
        _k("kanteKeine", "Zeile löschen", "tabelleZeileLoeschen"),
        _k("kanteKeine", "Spalte löschen", "tabelleSpalteLoeschen"),
        _k("kanteKeine", "Tabelle löschen", "tabelleLoeschen")]},
    {"name": "Zellen", "knoepfe": [
        _k("kanteAlle", "Zellen verbinden", "tabelleVerbinden"),
        _k("kanteInnen", "Zelle teilen", "tabelleTeilen"),
        _k("kanteInnen", "Tabelle teilen", "tabelleTabelleTeilen"),
        _k("kanteAlle", "AutoAnpassen", klappe="tabelleAutoAnpassen"),
        _k("unfold-vertical", "Zeilenhöhe", "tabelleHoehe"),
        _k("kanteAlle", "Spaltenbreite", "tabelleBreite"),
        _k("sortieren", "Tabelle sortieren", "tabelleSortieren")]},
    {"name": "Ausrichtung", "knoepfe": [
        _k("links", "Oben ausrichten", "zelleOben"),
        _k("mitte", "Mittig ausrichten", "zelleMitte"),
        _k("rechts", "Unten ausrichten", "zelleUnten"),
        _k("links", "Links im Feld", "zelleLinks"),
        _k("mitte", "Zentriert im Feld", "zelleZentriert"),
        _k("rechts", "Rechts im Feld", "zelleRechts"),
        _k("textrichtung", "Textrichtung", klappe="tabelleTextrichtung")]},
    {"name": "Schrift", "knoepfe": [
        _k("F", "Fett", "fett", haken=True),
        _k("K", "Kursiv", "kursiv", haken=True),
        _k("U", "Unterstrichen", "unter", haken=True)]},
]}
