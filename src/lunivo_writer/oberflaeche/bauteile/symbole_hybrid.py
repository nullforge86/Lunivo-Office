"""Lunivo Hybrid: die eigene, farbige Iconfamilie (ressourcen/icons/lunivo-hybrid/hell|dunkel/*.svg).

Ordnet die semantischen Symbolnamen der Oberfläche den Hybrid-Symbolen zu. Namen ohne Zuordnung behalten ihr bisheriges Strichsymbol.
"""
from __future__ import annotations

import os

from lunivo_writer.plattform.pfade import ressourcen_pfade as paths

ORDNER = os.path.join(paths.SYMBOLE, "lunivo-hybrid")

ZUORDNUNG = {
    # Datei
    "neu": "neu", "file-plus": "neu", "oeffnen": "oeffnen", "folder-open": "oeffnen", "speichern": "speichern", "save": "speichern",
    "drucken": "drucken", "printer": "drucken", "drucker2": "drucken", "pdf": "pdf_exportieren",
    # Zwischenablage
    "schere": "ausschneiden", "kopie": "kopieren", "kleben": "einfuegen", "einfStandard": "einfuegen",
    "inhalteEinfuegen": "inhalte_einfuegen", "einfInhalte": "inhalte_einfuegen",
    # Schrift & Absatz
    "bold": "fett", "italic": "kursiv", "underline": "unterstrichen", "strikethrough": "durchgestrichen", "durchgestrichen": "durchgestrichen",
    "schriftfarbe": "textfarbe", "marker": "markieren", "highlighter": "markieren", "hervorheben": "markieren",
    "text-align-start": "links", "links": "links", "mitte": "zentriert", "text-align-center": "zentriert",
    "text-align-end": "rechts", "rechts": "rechts", "text-align-justify": "blocksatz", "block": "blocksatz",
    "list": "aufzaehlung", "punkte": "aufzaehlung", "list-ordered": "nummerierung", "zahlen": "nummerierung",
    # Tabelle
    "tabelle": "tabelle_einfuegen", "tabelleEinfuegen": "tabelle_einfuegen", "tabelleZeileOben": "zeile_oberhalb",
    "tabelleZeileUnten": "zeile_unterhalb", "tabelleSpalteLinks": "spalte_links", "tabelleSpalteRechts": "spalte_rechts",
    "tabelleVerbinden": "zellen_verbinden",
    # Einfügen
    "bild": "bild", "image": "bild", "formel": "formel", "kette": "link", "sprechblase": "kommentar", "kommentarneu": "kommentar_einfuegen",
    # Seitenlayout
    "raender": "seitenraender", "ausrichtung": "ausrichtung", "querformat": "ausrichtung", "papiergroesse": "groesse",
    "spalten": "spalten", "umbruch": "umbrueche", "seitenzahl": "seitenzahl",
    # Überprüfen
    "rechtschreibpruefung": "rechtschreibung", "nachverfolgen": "aenderungen_nachverfolgen", "vergleichen": "vergleichen", "vorlesen": "vorlesen",
    # Ansicht
    "lupe": "suchen", "kleinerLupe": "zoom_minus", "blattansicht": "seitenansicht", "navigation": "navigation",
    "linealIcon": "lineal", "tabelleGitternetz": "gitter",
    # Serienbrief
    "empfaenger": "empfaenger", "feld": "felder", "serienvorschau": "vorschau", "vorschau": "vorschau", "serie": "serienbrief_starten",
    # Seitenleisten, Schnellzugriff, Chat
    "notiz": "notiz", "gliederung": "gliederung", "verfolgt": "aenderungen_nachverfolgen", "fussnote": "fussnote", "haken": "haken",
    "brille": "brille", "stift": "stift", "assistent": "assistent", "ki": "assistent", "chat": "chat",
    "undo": "rueckgaengig", "undo-2": "rueckgaengig", "redo": "wiederholen", "annehmen": "annehmen", "aenderungannehmen": "annehmen",
    "ablehnen": "ablehnen", "aenderungablehnen": "ablehnen", "schliessen": "schliessen", "kommentarloeschen": "kommentar_loeschen",
    "kommentareweg": "kommentar_loeschen", "kommentarweg": "kommentar_loeschen", "arrow-left": "nach_links", "chevron-left": "nach_links",
    "chevron-right": "nach_rechts", "plus": "plus", "minus": "minus", "ersetzen": "ersetzen", "gehezu": "sprung", "zuletzt": "zuletzt",
    "tabelleLoeschen": "tabelle_loeschen", "vorherSatz": "nach_links", "weiterSatz": "nach_rechts", "voriges": "nach_links", "naechstes": "nach_rechts",
    "trefferHoch": "nach_links", "trefferRunter": "nach_rechts", "mehr": "plus", "list-plus": "plus", "user-plus": "empfaenger",
    "ueberpruefenfenster": "rechtschreibung", "verfolgoptionen": "aenderungen_nachverfolgen", "markup": "aenderungen_nachverfolgen",
    "kommentareweg2": "kommentar_loeschen", "einfFormatiert": "einfuegen", "einfPassend": "einfuegen", "einfUnformatiert": "einfuegen",
    "schriftFenster": "fett", "absatzFenster": "links", "datumuhrzeit": "zuletzt", "uhrzeit": "zuletzt", "datum": "zuletzt",
    "umbenennen": "stift", "bearbeiter": "empfaenger", "benutzername": "empfaenger", "user": "empfaenger",
    # Oberfläche
    "einstellungen": "einstellungen", "settings": "einstellungen", "zahnrad": "einstellungen", "circle-question-mark": "hilfe",
}

def _weitere() -> None:
    """Die vom Erzeugungsskript geschriebene Zuordnung (zuordnung.json) ergänzt die Liste oben; Einträge oben haben Vorrang."""
    import json
    try:
        with open(os.path.join(ORDNER, "zuordnung.json"), encoding="utf-8") as fh:
            for alt, neu in json.load(fh).items():
                ZUORDNUNG.setdefault(alt, neu)
    except (OSError, ValueError):
        pass


_weitere()
_DATEIEN: dict = {}


def datei(name: str, dunkel: bool) -> str | None:
    """Pfad der Hybrid-SVG zu einem Oberflächen-Symbolnamen, sonst ``None``."""
    ziel = ZUORDNUNG.get(name)
    if not ziel:
        return None
    key = (ziel, dunkel)
    if key not in _DATEIEN:
        p = os.path.join(ORDNER, "dunkel" if dunkel else "hell", f"{ziel}.svg")
        _DATEIEN[key] = p if os.path.isfile(p) else None
    return _DATEIEN[key]
