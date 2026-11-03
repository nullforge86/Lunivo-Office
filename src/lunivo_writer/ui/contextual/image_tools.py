"""Kontext-Reiter „Bildtools“ und „Zeichentools“ (für Formen im Text: ``form``; für freie Objekte inkl. WordArt/Textfeld: ``zeichen``)."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import anordnen_gruppe as _gruppe, anordnen_knopf as _a, k as _k


BILDTOOLS = {"name": "Bildtools", "kontext": "bild", "gruppen": [
    {"name": "Bild", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("bild", "Bild einfügen", None, text=True, klappe="bildKlappe"),
        _k("replace", "Bild ändern", "bildAendern", text=True),
        _k("shapes", "Formen", None, True, klappe="formenKlappe")]},
    {"name": "Komprimieren", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("image-down", "Bilder komprimieren", "bildKomprimieren", text=True),
        _k("einpassen", "Weitere", text=True, menue=[                               # Größen-Befehle, Alternativtext und Entfernen hinter einem Knopf
            {"name": "Auf Seitenbreite", "tun": "bildBreite"}, {"name": "Originalgröße", "tun": "bildOriginal"},
            {"name": "Zuschneiden nach Maß …", "tun": "bildZuschneiden"}, {"trenner": True},
            {"name": "Alternativtext …", "tun": "bildAltText"}, {"name": "Bild entfernen", "tun": "bildEntfernen"}])]},
    {"name": "Größe", "felder": "masse", "sperre": "bild", "ohne_titel": True, "pfeil": "bildGroesse", "knoepfe": [
        _k("crop", "Zuschneiden", "bildZuschneidenModus", True, klappe="bildZuschneiden"),
        _k("sperren", "Seitenverhältnis sperren", "bildSeitenverhaeltnis", text=True),
        _k("maximize", "Größe zurücksetzen", "bildGroesseZuruecksetzen", text=True)]},
    {"name": "Farbe", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("farbe", "Farbe", "bildFarbe", text=True),
        _k("pipette", "Transparente Farbe einstellen", "bildTransparent", text=True),
        _k("sun", "Helligkeit", text=True, menue=[{"name": "Heller", "tun": "bildHelligkeit:[10]"}, {"name": "Dunkler", "tun": "bildHelligkeit:[-10]"}]),
        _k("contrast", "Kontrast", text=True, menue=[{"name": "Kontrast erhöhen", "tun": "bildKontrast:[10]"},
                                                      {"name": "Kontrast verringern", "tun": "bildKontrast:[-10]"}]),
        _k("sparkles", "Bildeffekte", "zeichenEffekte", True),
        _k("frame", "Rahmen", None, text=True, klappe="zeichenGliederung"),
        _k("undo-2", "Bild zurücksetzen", "bildZuruecksetzen", text=True)]},
    _gruppe(_a("drehen", "Frei drehen", text=True), _a("umbruch", text=True), _a("objekte", text=True)),
]}

FORMTOOLS = {"name": "Zeichentools", "kontext": "form", "gruppen": [
    {"name": "Formen", "knoepfe": [_k("stift", "Formen einfügen", klappe="formenKlappe", gross=True)]},
    {"name": "Formvorlagen", "knoepfe": [_k("stift", "Formvorlagen", klappe="formVorlagen", gross=True)]},
    {"name": "Formenstile", "knoepfe": [_k("toenung", "Formfüllung", klappe="formFuellung", text=True),
                                         _k("linie", "Formkontur", klappe="formKontur", text=True),
                                         _k("notiz", "Text in der Form …", "formText", text=True)]},
    {"name": "Anordnen", "knoepfe": [_k("gruppieren", "Gruppieren", "gruppieren", text=True),
                                     _k("gruppieren", "Gruppierung aufheben", "gruppeAufheben", text=True),
                                     _k("textflussumbruch", "Textumbruch / Position", "anordnen", text=True)]}]}


ZEICHENTOOLS = {"name": "Zeichentools", "kontext": "zeichen", "gruppen": [
    {"name": "Linien", "ohne_titel": True, "galerie": "zeichenLinien", "zeilen": 2, "kacheln": 6, "knoepfe": []},
    {"name": "Formen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("stift", "Formen einfügen", klappe="formenKlappe", gross=True),
        _k("textrahmen", "Textfeld", None, text=True, klappe="textfeldKlappe"),
        _k("stift", "Form bearbeiten", None, text=True, klappe="formBearbeiten")]},
    {"name": "Formstile", "ohne_titel": True, "galerie": "zeichenFormstile", "kacheln": 4, "knoepfe": []},
    {"name": "Formen formatieren", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("toenung", "Formfüllung", klappe="zeichenFuellung", text=True),
        _k("linie", "Gliederung", klappe="zeichenGliederung", text=True),
        _k("pinselchen", "Format übertragen", "zeichenFormatUebertragen", text=True),
        _k("texteffekt", "Formeffekte", "zeichenEffekte", text=True)]},
    _gruppe(_a("ausrichten", text=True), _a("gruppieren", text=True), _a("drehen", text=True), _a("ebene", text=True),
            _a("umbruch", text=True), _a("auswahlbereich", text=True)),
    {"name": "Größe", "felder": "masse", "pfeil": "zeichenLayout", "knoepfe": []},
]}


SMARTARTTOOLS = {"name": "SmartArt-Design", "kontext": "smartart", "gruppen": [
    {"name": "Grafik erstellen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("smartart", "Form einfügen", None, text=True, klappe="smartartFormEinfuegen"),
        _k("punkte", "Aufzählungszeichen einfügen", "smartartAufzaehlung", text=True),
        _k("arrow-left", "Level erhöhen", "smartartLevelErhoehen", text=True),
        _k("arrow-right", "Level reduzieren", "smartartLevelReduzieren", text=True),
        _k("arrow-up", "Vorwärts", "smartartVorwaerts", text=True),
        _k("arrow-down", "Rückwärts", "smartartRueckwaerts", text=True),
        _k("arrow-left-right", "Layout von rechts nach links", "smartartRechtsLinks", text=True),
        _k("network", "Layout", None, text=True, klappe="smartartHierarchie")]},
    {"name": "Layouts", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("layout-template", "Layout ändern", None, True, klappe="smartartLayout"),
        _k("palette", "Farben ändern", None, True, klappe="smartartFarben")]},
    {"name": "SmartArt-Stile", "ohne_titel": True, "galerie": "smartartStile", "knoepfe": []},
    _gruppe(_a("umbruch", "Textfluss", text=True), _a("ausrichten", text=True), _a("auswahlbereich", text=True), _a("ebene", text=True)),
    {"name": "Größe", "felder": "masse", "praefix": "sa_", "pfeil": "zeichenLayout", "knoepfe": []},
]}
