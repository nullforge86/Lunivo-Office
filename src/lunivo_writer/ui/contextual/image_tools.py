"""Kontext-Reiter „Bildtools“ und „Zeichentools“ (für Formen im Text: ``form``; für freie Objekte inkl. WordArt/Textfeld: ``zeichen``)."""
from __future__ import annotations

from lunivo_writer.ui.ribbon.tabs.baustein import k as _k


BILDTOOLS = {"name": "Bildtools", "kontext": "bild", "gruppen": [
    {"name": "Bild", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("bild", "Bild einfügen", None, text=True, klappe="bildKlappe"),
        _k("replace", "Bild ändern", "bildAendern", text=True),
        _k("shapes", "Formen", None, True, klappe="formenKlappe")]},
    {"name": "Komprimieren", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("image-down", "Bilder komprimieren", "bildKomprimieren", True)]},
    {"name": "Größe", "felder": "masse", "sperre": "bild", "ohne_titel": True, "pfeil": "bildGroesse", "knoepfe": [
        _k("crop", "Zuschneiden", "bildZuschneidenModus", True, klappe="bildZuschneiden"),
        _k("sperren", "Seitenverhältnis sperren", "bildSeitenverhaeltnis", text=True),
        _k("maximize", "Größe zurücksetzen", "bildGroesseZuruecksetzen", text=True)]},
    {"name": "Farbe", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("pipette", "Transparente Farbe einstellen", "bildTransparent", True),
        _k("farbe", "Farbe", "bildFarbe", True),
        _k("sun", "Heller", "bildHelligkeit:[10]", text=True),
        _k("sun-dim", "Dunkler", "bildHelligkeit:[-10]", text=True),
        _k("contrast", "Kontrast erhöhen", "bildKontrast:[10]", text=True),
        _k("blend", "Kontrast verringern", "bildKontrast:[-10]", text=True),
        _k("rotate-cw", "Um 90° nach rechts drehen", "zeichenDrehen:[90]"),
        _k("rotate-ccw", "Um 90° nach links drehen", "zeichenDrehen:[-90]"),
        _k("sparkles", "Bildeffekte", "zeichenEffekte", True),
        _k("frame", "Rahmen", None, text=True, klappe="zeichenGliederung"),
        _k("undo-2", "Bild zurücksetzen", "bildZuruecksetzen", text=True)]},
    {"name": "Anordnen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("objektdrehen", "Frei drehen", None, True, klappe="zeichenDrehen"),
        _k("gruppieren", "Gruppieren", "gruppieren", text=True),
        _k("ausrichten", "Ausrichten", None, text=True, klappe="zeichenAusrichten"),
        _k("textflussumbruch", "Textumbruch Stil", "zeichenUmbruch", True),
        _k("ebeneHoch", "Eine Ebene nach vorne", "zeichenVorn", text=True),
        _k("ebeneTief", "Eine Ebene nach hinten", "zeichenHinten", text=True)]},
    {"name": "Weitere", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("ruler", "Größe und Seitenverhältnis …", "bildGroesse", text=True),
        _k("einpassen", "Auf Seitenbreite", "bildBreite", text=True),
        _k("bild", "Originalgröße", "bildOriginal", text=True),
        _k("notiz", "Alternativtext …", "bildAltText", text=True),
        _k("kanteKeine", "Bild entfernen", "bildEntfernen", text=True),
        _k("crop", "Zuschneiden nach Maß …", "bildZuschneiden", text=True)]},
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
    {"name": "Linien", "ohne_titel": True, "galerie": "zeichenLinien", "zeilen": 2, "knoepfe": []},
    {"name": "Formen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("stift", "Formen einfügen", klappe="formenKlappe", gross=True),
        _k("textrahmen", "Textfeld", None, text=True, klappe="textfeldKlappe"),
        _k("stift", "Form bearbeiten", None, text=True, klappe="formBearbeiten")]},
    {"name": "Formstile", "ohne_titel": True, "galerie": "zeichenFormstile", "knoepfe": []},
    {"name": "Formen formatieren", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("toenung", "Formfüllung", klappe="zeichenFuellung", gross=True),
        _k("linie", "Gliederung", klappe="zeichenGliederung", gross=True),
        _k("pinselchen", "Format übertragen", "zeichenFormatUebertragen", text=True),
        _k("texteffekt", "Formeffekte", "zeichenEffekte", text=True)]},
    {"name": "Anordnen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("ausrichten", "Ausrichten", klappe="zeichenAusrichten", gross=True),
        _k("gruppieren", "Gruppieren", "gruppieren", text=True),
        _k("objektdrehen", "Drehen", klappe="zeichenDrehen", text=True),
        _k("textflussumbruch", "Textumbruch Stil", "zeichenUmbruch", gross=True),
        _k("ebeneHoch", "Eine Ebene nach vorne", "zeichenVorn", text=True),
        _k("ebeneTief", "Eine Ebene nach hinten", "zeichenHinten", text=True),
        _k("auswahlbereich", "Auswahlbereich", "auswahlbereich", gross=True)]},
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
    {"name": "Anordnen", "reihenfolge": True, "ohne_titel": True, "knoepfe": [
        _k("textflussumbruch", "Textfluss", "zeichenUmbruch", gross=True),
        _k("ausrichten", "Ausrichten", None, True, klappe="zeichenAusrichten"),
        _k("auswahlbereich", "Auswahlbereich", "auswahlbereich", gross=True),
        _k("ebeneHoch", "Eine Ebene nach vorne", "zeichenVorn", text=True),
        _k("ebeneTief", "Eine Ebene nach hinten", "zeichenHinten", text=True)]},
    {"name": "Größe", "felder": "masse", "praefix": "sa_", "pfeil": "zeichenLayout", "knoepfe": []},
]}
