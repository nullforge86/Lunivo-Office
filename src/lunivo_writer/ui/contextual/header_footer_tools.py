"""Kontext-Reiter „Kopf- und Fußzeile“ nach der WPS-Vorlage: Gruppen ohne Namen, Klappen für Kopfzeile, Fußzeile, Seitenzahl,
Linie; Wechseln/Verknüpfen; Optionen, Tabstopp, Höhenfelder; Einstellungen und Schließen."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k

KOPFFUSS = {"name": "Kopf- und Fußzeile", "kontext": "kopffuss", "gruppen": [
    {"name": "Einfügen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("kopffuss", "Kopf-/Fußzeilengruppe", None, True, klappe="kfGruppeKlappe"),
        _k("kopfz", "Kopfzeile", None, True, klappe="kopfzeileKlappe"),
        _k("fussz", "Fußzeile", None, True, klappe="fusszeileKlappe"),
        _k("seitenzahl", "Seitenzahl", None, True, klappe="seitenzahlKlappe"),
        _k("linie", "Kopfzeilen", None, True, klappe="kopfLinieKlappe")]},
    {"name": "Felder", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("datumuhrzeit", "Datum und Uhrzeit", "datumUhrzeit", True),
        _k("bild", "Bild", None, True, klappe="bildKlappe"),
        _k("feld", "Felder", "felder", True)]},
    {"name": "Navigation", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("wechseln", "Zwischen Kopf- und Fußzeile wechseln", "kfWechseln", True),
        _k("voriges", "Vorige Kopfzeile", "kfVorige", text=True),
        _k("naechstes", "Nächste Kopfzeile", "kfNaechste", text=True),
        _k("verknuepft", "Mit vorheriger verknüpfen", "kfVerknuepfen", True)]},
    {"name": "Optionen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("optionen", "Optionen für Kopf- und Fußzeile", "kfOptionen", text=True),
        _k("tabstopp", "Ausrichtungstabstopp einfügen", "kfTabstopp", text=True),
        {"feld": "kopfHoehe", "name": "Kopfzeilenhöhe"},
        {"feld": "fussHoehe", "name": "Fußzeilenhöhe"}]},
    {"name": "Schließen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("einstellungen", "Einstellungen", None, True, klappe="kfEinstellungenKlappe"),
        _k("schliessen", "Schließen", "kopfFussSchliessen", True)]}]}
