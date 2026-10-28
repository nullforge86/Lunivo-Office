"""Reiter „Überprüfen“ nach Kays Vorlagen (ueberpruefen/01–10): Rechtschreibprüfung, Wörter zählen, Kommentare, Änderungen
nachverfolgen mit Anzeige und Markup, Überprüfen, Annehmen/Ablehnen, Vergleichen, Freihand, Bearbeitung einschränken.

Gründliche Prüfung, Thesaurus und KI stehen im Reiter „Schreibhilfe“ (Menü „Dokumentprüfung“) und in der Seitenleiste.
"""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k


def bauen(register: dict) -> dict:
    tab = next(t for t in register["register"] if t["name"] == "Überprüfen")
    gruppen = [
        {"name": "Dokumentprüfung", "reihenfolge": True, "knoepfe": [
            _k("rechtschreibpruefung", "Rechtschreibprüfung", "rechtschreibung", True, klappe="rechtschreibKlappe"),
            _k("woerter", "Wörter zählen", "woerterZaehlen", True)]},
        {"name": "Kommentare", "reihenfolge": True, "knoepfe": [
            _k("kommentarneu", "Kommentar einfügen", "kommentar", True),
            _k("kommentarloeschen", "Löschen", "kommentarWeg", True, klappe="kommentarLoeschenKlappe"),
            _k("zurueck", "Vorherige", "kommentarZurueck", text=True),
            _k("vor", "Weiter", "kommentarWeiter", text=True)]},
        {"name": "Nachverfolgung", "reihenfolge": True, "knoepfe": [
            _k("nachverfolgen", "Änderungen nachverfolgen", "verfolgen", True, klappe="verfolgenKlappe"),
            {"feld": "anzeige", "name": "Anzeige zur Überprüfung"},
            _k("ueberpruefenfenster", "Überprüfen", gross=True, klappe="ueberpruefenKlappe")]},
        {"name": "Änderungen", "reihenfolge": True, "knoepfe": [
            _k("aenderungannehmen", "Annehmen", "aenderungAnnehmen", True, klappe="annehmenKlappe"),
            _k("aenderungablehnen", "Ablehnen", "aenderungAblehnen", True, klappe="ablehnenKlappe"),
            _k("zurueck", "Vorherige", "aenderungZurueck", text=True),
            _k("vor", "Weiter", "aenderungWeiter", text=True)]},
        {"name": "Vergleichen", "reihenfolge": True, "knoepfe": [
            _k("vergleichen", "Vergleichen", "dokumenteVergleichen", True, klappe="vergleichenKlappe")]},
        {"name": "Freihand", "reihenfolge": True, "knoepfe": [
            _k("freihand", "Freihand", gross=True)]},
        {"name": "Schützen", "reihenfolge": True, "knoepfe": [
            _k("einschraenken", "Bearbeitung einschränken", "bearbeitungEinschraenken", True)]},
    ]
    return dict(tab, gruppen=gruppen)
