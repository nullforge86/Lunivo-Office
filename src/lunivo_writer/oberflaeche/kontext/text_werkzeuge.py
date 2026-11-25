"""Kontext-Reiter „Texttools“ nach der Vorlage (erscheint bei markiertem WordArt oder Textfeld, zusammen mit „Zeichentools“).

Gruppen von links nach rechts: Textfeld ▾ · Format übertragen · Schriftart/Größe, A⁺ A⁻, Formatierung löschen, F K U ▾, Durchgestrichen ▾, x² x₂,
Hervorhebung ▾, Schriftfarbe ▾ · Aufzählung ▾, Nummerierung ▾, Einzug −/+, Textrichtung ▾, Sortieren, fünf Ausrichtungen, Zeilenabstand ▾ ·
Galerie WordArt-Stile · Textfüllung ▾, Textkontur ▾, Texteffekte ▾ · Galerie Formstile · Füllung ▾, Kontur ▾, Formeffekte · Verknüpfung erstellen ▾
mit „Voriges/Nächstes Textfeld“ · Einstellungen ▾. Jeder Knopf ist ein ``tt…``-Befehl (kern/befehle/kontextreiter/texttools.py) oder ein Menü des Bandes."""
from __future__ import annotations

from lunivo_writer.oberflaeche.band.reiter.baustein import k as _k

TEXTTOOLS = {"name": "Texttools", "kontext": "text", "gruppen": [
    {"name": "Textfeld", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("textrahmen", "Textfeld", None, text=True, klappe="textfeldKlappe"),
        _k("pinsel", "Format übertragen", "ttFormatUebertragen", text=True)]},
    {"name": "Schriftart", "felder": "tt_zeile", "ohne_titel": True, "knoepfe": [
        _k("groesserA", "Schrift vergrößern", "ttGroesser"),
        _k("kleinerA", "Schrift verkleinern", "ttKleiner"),
        _k("radierer", "Formatierung löschen", "ttSchlicht"),
        {"zeilenumbruch": True},
        _k("F", "Fett", "ttFett"), _k("K", "Kursiv", "ttKursiv"),
        _k("U", "Unterstrichen", "ttUnter", klappe="ttUnter"),
        _k("durchgestrichen", "Durchgestrichen", "ttDurch", klappe="ttDurch"),
        _k("X²", "Hochgestellt", "ttHoch"), _k("X₂", "Tiefgestellt", "ttTief"),
        _k("marker", "Hervorhebung", "ttHervorJetzt", klappe="ttHervor"),
        _k("schriftfarbe", "Schriftfarbe", "ttSchriftfarbeJetzt", klappe="ttSchriftfarbe")]},
    {"name": "Absatz", "ohne_titel": True, "knoepfe": [
        _k("punkte", "Aufzählung", "ttPunkte", klappe="ttPunkte"),
        _k("zahlen", "Nummerierung", "ttZahlen", klappe="ttZahlen"),
        _k("ebeneTief", "Einzug verringern", "ttEinzugWeniger"),
        _k("ebeneHoch", "Einzug vergrößern", "ttEinzugMehr"),
        _k("textrichtung", "Textrichtung", None, klappe="ttTextrichtung"),
        _k("sortieren", "Sortieren", "ttSortieren"),
        {"zeilenumbruch": True},
        _k("links", "Linksbündig", "ttLinks"), _k("mitte", "Zentriert", "ttMitte"), _k("rechts", "Rechtsbündig", "ttRechts"),
        _k("block", "Blocksatz", "ttBlock"), _k("verteilt", "Verteilt", "ttVerteilt"),
        _k("abstand", "Zeilenabstand", None, klappe="ttZeilenabstand")]},
    {"name": "WordArt-Stile", "ohne_titel": True, "galerie": "ttWordartStile", "kacheln": 1, "knoepfe": []},
    {"name": "Text", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("toenung", "Textfüllung", None, text=True, klappe="ttTextfuellung"),
        _k("linie", "Textkontur", None, text=True, klappe="ttTextkontur")]},
    {"name": "Formstile", "ohne_titel": True, "galerie": "ttFormstile", "kacheln": 1, "knoepfe": []},
    {"name": "Form", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("toenung", "Füllung", None, text=True, klappe="ttFormFuellung"),
        _k("linie", "Kontur", None, text=True, klappe="ttFormKontur")]},
    {"name": "Effekte", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("texteffekt", "Texteffekte", None, text=True, klappe="ttTexteffekte"),
        _k("flaeche", "Formeffekte", None, text=True, klappe="ttFormEffekte")]},
    {"name": "Verknüpfung", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("kette", "Verknüpfung erstellen", None, text=True, klappe="ttVerknuepfung"),
        _k("zahnrad", "Einstellungen", None, text=True, klappe="ttEinstellungen"),
        _k("voriges", "Voriges Textobjekt", "ttVoriges"),
        _k("naechstes", "Nächstes Textobjekt", "ttNaechstes")]},
]}
