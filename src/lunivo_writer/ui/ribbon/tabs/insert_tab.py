"""Reiter „Einfügen“ in der Anordnung von WPS Office (Vorlagen im Ordner einfuegen/): Deckblatt, Leere Seite ▾, Umbrüche ▾, Tabelle ▾,
Bild ▾, Formen, Diagramm, Kommentar, Kopf- und Fußzeile, Textfeld ▾, Schnellbausteine ▾, Symbol ▾, Gleichung, Zahl, Hyperlink.
Die Klappmenüs baut ``core/befehle/einfuegen.py`` (``menue_…Klappe``). Keine Gruppe „Weitere“: was WPS nicht im Band hat, steht in
den Klappen (Bildschirmfoto und Piktogramm unter Bild, Text aus Datei unter Objekt, eigene Form unter
Formen); die Tabellen-Eigenschaften im Kontext-Reiter Tabelle."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import alle, k as _k


def bauen(register: dict) -> dict:
    tab = next(t for t in register["register"] if t["name"] == "Einfügen")
    kn = alle(tab)
    benutzt: set = set()

    def nimm(_name, **kw):
        benutzt.add(_name)
        return {s: w for s, w in dict(kn[_name], **kw).items() if w is not None}

    kommentar = next(e for t in register["register"] if t["name"] == "Überprüfen" for g in t["gruppen"]
                     for e in g["knoepfe"] if e.get("tun") == "kommentar")
    formulare = _k("formfeld", "Formulare", gross=True, menue=[
        {"name": "Textfeld", "tun": "formTextfeld"}, {"name": "Auswahlliste", "tun": "formAuswahl"},
        {"name": "Datumsfeld", "tun": "formDatum"}, {"name": "Kontrollkästchen", "tun": "formKasten"},
        {"name": "Schaltfläche", "tun": "formKnopf"}, {"trenner": True}, {"name": "Felder zurücksetzen", "tun": "formLeeren"}])
    gruppen = [
        {"name": "Seiten", "reihenfolge": True, "knoepfe": [
            nimm("Deckblatt", gross=True, klappe="deckblattKlappe", tun=None),
            nimm("Leere Seite", gross=True, tun="leereSeite", klappe="leereSeiteKlappe", menue=None),
            nimm("Seitenumbruch", name="Umbrüche", gross=True, klappe="umbruecheKlappe")]},
        {"name": "Tabellen", "reihenfolge": True, "knoepfe": [
            nimm("Tabelle einfügen", name="Tabelle", gross=True)]},
        {"name": "Illustrationen", "reihenfolge": True, "knoepfe": [
            nimm("Bild", gross=True, klappe="bildKlappe"), nimm("Formen", gross=True, tun=None, klappe="formenKlappe"),
            nimm("Diagramm", text=True), nimm("SmartArt", text=True)]},
        {"name": "Kommentar", "reihenfolge": True, "knoepfe": [dict(kommentar, name="Kommentar", gross=True)]},
        {"name": "Kopf- und Fußzeile", "reihenfolge": True, "knoepfe": [
            nimm("Kopf- und Fußzeile", gross=True), nimm("Seitenzahl", gross=True, tun=None),
            _k("wasserzeichen", "Wasserzeichen", gross=True, klappe="wasserzeichenKlappe")]},
        {"name": "Text", "reihenfolge": True, "knoepfe": [
            nimm("Textfeld", gross=True, klappe="textfeldKlappe"), nimm("WordArt", gross=True, tun=None, klappe="wordartKlappe"),
            nimm("Datum und Uhrzeit", gross=True),
            _k("objekte", "Objekt", "objekt", text=True, klappe="objektKlappe"), _k("ausdatei", "Datei-Objekt", "dateiObjekt", text=True),
            nimm("Initiale", text=True), _k("baustein", "Schnellbausteine", text=True, klappe="schnellbausteineKlappe")]},
        {"name": "Symbole", "reihenfolge": True, "knoepfe": [
            nimm("Sonderzeichen", name="Symbol", gross=True, tun=None, klappe="symbolKlappe"), nimm("Formel", name="Gleichung", gross=True, klappe="gleichungKlappe"),
            _k("zahl", "Zahl", "zahl", True)]},
        {"name": "Links", "reihenfolge": True, "knoepfe": [
            nimm("Hyperlink", gross=True), nimm("Querverweis", text=True), nimm("Lesezeichen / Textmarke", name="Lesezeichen", text=True)]},
        {"name": "Formulare", "reihenfolge": True, "knoepfe": [formulare]},
    ]
    return dict(tab, gruppen=gruppen)
