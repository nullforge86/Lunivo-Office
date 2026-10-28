"""Kontext-Reiter „Mailings“ (Seriendruck) nach der WPS-Vorlage: erscheint über Verweise ▸ Seriendruck und bleibt, bis
„Seriendruck schließen“. Datenquelle, Felder, Vorschau mit Datensatz-Blättern, Zusammenführen."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k

SERIENDRUCK = {"name": "Mailings", "kontext": "serien", "gruppen": [
    {"name": "Datenquelle", "reihenfolge": True, "knoepfe": [
        _k("datenquelle", "Datenquelle öffnen", "serienQuelle", True, klappe="serienQuelleKlappe"),
        _k("empfaenger", "Seriendruckempfänger", "serienEmpfaenger", True)]},
    {"name": "Felder", "reihenfolge": True, "knoepfe": [
        _k("seriefeld", "Seriendruckfeld einfügen", "serienFeld", text=True),
        _k("naechstesfeld", "Nächstes Feld einfügen", "serienNaechster", text=True),
        _k("hervorheben", "Seriendruckfelder hervorheben", "serienHervorheben", text=True),
        _k("zuordnen", "Übereinstimmende Felder festlegen", "serienZuordnen", text=True)]},
    {"name": "Vorschau", "reihenfolge": True, "knoepfe": [
        _k("serienvorschau", "Seriendruck-Vorschau", "serienVorschau", True),
        _k("ersterSatz", "Erster Datensatz", "serienErster", True),
        _k("vorherSatz", "Vorheriger Datensatz", "serienVorheriger", True),
        {"feld": "datensatz", "name": "Datensatz"},
        _k("weiterSatz", "Nächster Datensatz", "serienNaechsterSatz", True),
        _k("letzterSatz", "Letzter Datensatz", "serienLetzter", True)]},
    {"name": "Fertigstellen", "reihenfolge": True, "knoepfe": [
        _k("zusammenfuehren", "In neuem Dokument zusammenführen", "serienNeuesDokument", text=True),
        _k("einzeldokumente", "In anderem neuen Dokument zusammenführen", "serienEinzeln", text=True),
        _k("drucken", "An Drucker zusammenführen", "serienDrucker", text=True),
        _k("serienschliessen", "Seriendruck schließen", "serienSchliessen", True)]},
]}
