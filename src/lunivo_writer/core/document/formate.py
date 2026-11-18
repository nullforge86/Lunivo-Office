"""Formate des Dokumentmodells: Zeichen, Absatz, Tabelle, Zelle, Rahmen — als einfache Wörterbücher mit festem Schema.

Ein Format ist ein ``dict`` mit Namen aus dem Schema seiner Art; nur was gesetzt ist, steht drin. Maße sind Bildpunkte bei 96 dpi,
Schriftgrößen Punkt, Farben ``#rrggbb``. Formate gelten als unveränderlich: Wer eines ändert, erzeugt mit ``verschmelze`` ein neues.
Hier stehen auch alle fachlichen Eigenschaften wie Kommentar, Note, Feld, Verzeichnis oder Muster — mit Namen statt Nummern.
"""
from __future__ import annotations

ZAHL = (int, float)

ZEICHEN: dict[str, tuple] = {
    # Schrift
    "schrift": (str, list), "groesse_pt": ZAHL, "fett": (bool,), "kursiv": (bool,), "gewicht": (int,),
    "unterstrichen": (bool,), "unter_stil": (int,), "unter_art": (str,), "unter_farbe": (str,), "durchgestrichen": (bool,), "doppelt_durch": (bool,),
    "ueberstrichen": (bool,), "farbe": (str,), "marker": (str,), "hoch_tief": (str,),                 # "hoch" | "tief"
    "kapitaelchen": (bool,), "grossbuchstaben": (bool,), "zeichenabstand": ZAHL, "zeichenabstand_art": (int,), "tooltip": (str,),
    "skalierung": ZAHL, "versatz_pt": ZAHL,
    "unterschneidung": (bool,), "sprache": (str,), "vorlage": (str,),                                    # Zeichenvorlage
    "font_asien": (str,), "font_komplex": (str,), "raster": (bool,),
    # Verweise
    "link": (str,), "anker": (list, tuple),                                                              # Sprungziel, Textmarken-Namen
    # Zusätzliche textbezogene Formatierungsdaten
    "kommentar": (int,), "note": (str,), "aenderung": (str,), "autor": (str,), "datum": (str, list),
    "feld": (str,), "index": (str,), "index_opt": (str,), "zitat": (str,), "versteckt": (bool,),
    "effekt": (dict, str), "objekt": (str,), "betonung": (str,), "umschlossen": (str,), "ruby": (str,),
    "regel": (str,), "formular": (dict, str),
    "docx_roh": (list,),                                                                                 # unbekannte DOCX-Eigenschaften als XML-Texte (bleiben erhalten)
    "docx_sdt": (dict,),                                                                                 # DOCX-Inhaltssteuerelement (w:sdt), das den Text umschließt: gruppe, pr (w:sdtPr als XML)
}

ABSATZ: dict[str, tuple] = {
    "vorlage": (str,), "ausrichtung": (str,),                                                            # links | mitte | rechts | block
    "einzug_links": ZAHL, "einzug_rechts": ZAHL, "einzug_erste": ZAHL, "abstand_vor": ZAHL, "abstand_nach": ZAHL,
    "zeilenabstand_art": (str,), "zeilenabstand": ZAHL,                                                  # einfach | vielfach | genau | mindestens
    "seitenumbruch_vor": (bool,), "seitenumbruch_nach": (bool,), "spaltenumbruch_vor": (bool,), "gliederungsebene": (int,), "richtung": (str, int),
    "tabstopps": (list, tuple), "tabfuell": (str,), "hintergrund": (str,), "rahmen": (str,), "muster": (str,),
    "optionen": (dict, str),                                                                             # Absatzkontrolle, zusammenhalten …
    "liste_start": (int,),                                                                               # Zählung der Liste beginnt hier neu
    # Verzeichnisse und Beschriftungen
    "toc": (str,), "verzeichnis_art": (str,), "toc_opt": (str,), "beschriftung": (str,), "notenziel": (str,),
    # Sonstiges
    "deckblatt": (str,), "deckblatt_umbruch": (bool,), "zeilenluft": (str,), "formular": (dict, str),
    "hilfsabsatz": (bool,), "mehrstufig": (str,), "bildanker": (str,), "autoumbruch": (int,), "abstand_vorher": ZAHL, "querbreite": ZAHL,
    "docx_roh": (list,),                                                                                 # unbekannte DOCX-Eigenschaften als XML-Texte (bleiben erhalten)
    "docx_sdt": (dict,),                                                                                 # DOCX-Inhaltssteuerelement (w:sdt) um den Absatz: gruppe, pr, ende (XML)
}

TABELLE: dict[str, tuple] = {
    "breite": ZAHL, "breite_art": (str,), "ausrichtung": (str,), "einzug_links": ZAHL,                   # breite_art: fest | prozent | auto
    "rahmen": (str,), "rahmen_breite": ZAHL, "rahmen_farbe": (str,), "rahmen_art": (str,),
    "zellabstand": ZAHL, "zellpolster": ZAHL, "hintergrund": (str,),
    "optionen": (int,), "vorlage": (str,), "kopfzeilen": (int,), "alt_text": (str,), "alt_titel": (str,),
    "umbruch": (str,), "abstand_vor": ZAHL, "abstand_nach": ZAHL,
    "spaltenlaengen": (list,), "rahmen_zusammen": (bool,), "rahmen_stil": (int,), "querbreite": ZAHL,
    "docx_roh": (list,), "docx_roh_zeilen": (dict,),                                                    # erhaltene Eigenschaften der Tabelle und ihrer Zeilen (Zeilennummer → XML-Texte)
}

ZELLE: dict[str, tuple] = {
    "hintergrund": (str,), "muster": (str,), "vertikal": (str,), "textrichtung": (str,),                 # vertikal: oben | mitte | unten
    "rahmen_oben": (str,), "rahmen_unten": (str,), "rahmen_links": (str,), "rahmen_rechts": (str,),
    "rahmen_diagonal": (str,), "polster_oben": ZAHL, "polster_unten": ZAHL, "polster_links": ZAHL, "polster_rechts": ZAHL,
    "kein_umbruch": (bool,), "zeichenformat": (dict,),
    "docx_roh": (list,),
}

RAHMEN: dict[str, tuple] = {
    "umfluss": (int,),                                                                                 # 0 keiner, 1 links, 2 rechts
    "rahmen_breite": ZAHL, "rahmen_farbe": (str,), "rahmen_stil": (int,), "rand": ZAHL, "polster": ZAHL,
    "rand_oben": ZAHL, "rand_unten": ZAHL, "rand_links": ZAHL, "rand_rechts": ZAHL, "hintergrund": (str,),
    "breite": ZAHL, "breite_art": (str,), "hoehe": ZAHL, "hoehe_art": (str,), "seitenumbruch_vor": (bool,), "seitenumbruch_nach": (bool,),
}

SCHEMATA = {"zeichen": ZEICHEN, "absatz": ABSATZ, "tabelle": TABELLE, "zelle": ZELLE, "rahmen": RAHMEN}

AUSRICHTUNGEN = ("links", "mitte", "rechts", "block")


class FormatFehler(ValueError):
    """Ein Format enthält einen unbekannten Namen oder einen Wert der falschen Art."""


def pruefe(art: str, werte: dict, *, leer_erlaubt: bool = False) -> dict:
    """Prüft ``werte`` gegen das Schema ``art`` und gibt eine Kopie zurück. ``None`` ist nur mit ``leer_erlaubt`` zulässig
    (bedeutet beim Verschmelzen: Eigenschaft entfernen)."""
    schema = SCHEMATA[art]
    for name, wert in werte.items():
        if name not in schema:
            raise FormatFehler(f"Unbekannte Eigenschaft im Format „{art}“: {name}")
        if wert is None:
            if not leer_erlaubt:
                raise FormatFehler(f"Eigenschaft ohne Wert: {name}")
            continue
        typen = schema[name]
        if isinstance(wert, bool) and bool not in typen:
            raise FormatFehler(f"Falscher Wert für {name}: {wert!r}")
        if not isinstance(wert, typen):
            raise FormatFehler(f"Falscher Wert für {name}: {wert!r}")
    if art == "absatz" and werte.get("ausrichtung") not in (None, *AUSRICHTUNGEN):
        raise FormatFehler(f"Unbekannte Ausrichtung: {werte['ausrichtung']!r}")
    if art == "zeichen" and werte.get("hoch_tief") not in (None, "", "hoch", "tief"):
        raise FormatFehler(f"Unbekannte Stellung: {werte['hoch_tief']!r}")
    return dict(werte)


# Paare, die dasselbe Merkmal zwei Mal beschreiben (Kurzform / Rohwert): Wer eines setzt, löscht das andere
GEGENSEITIG = (("fett", "gewicht"), ("unterstrichen", "unter_stil"))


def verschmelze(basis: dict, aenderung: dict) -> dict:
    """Neues Format: ``basis`` mit den Werten aus ``aenderung``; ein Wert ``None`` entfernt die Eigenschaft."""
    neu = dict(basis)
    for name, wert in aenderung.items():
        if wert is None:
            neu.pop(name, None)
        else:
            neu[name] = wert
            for a, b in GEGENSEITIG:
                if name in (a, b):
                    neu.pop(b if name == a else a, None)
    return neu
