"""Kompatibilitätsregeln für Dateiformate (zuerst DOCX): Welche Eigenschaft einer Datei das Modell abbildet, erhält oder nicht kennt. Ohne Qt.

Jede Regel nennt das Element, den Umgang damit (``Umgang``), ob es sichtbar wirkt und die Formatvorgabe, aus der die Regel stammt. Eine Regel entsteht nur aus einer
benannten Vorgabe, nie aus einer Vermutung über das Verhalten eines Programms:

* ``ECMA-376`` Teil 1 (Office Open XML, WordprocessingML und DrawingML) — die Kapitel sind nach Abschnitt angegeben; die Angabe ist die Kapitelebene, in der das Element
  beschrieben ist (``17.3.2`` Lauf-Eigenschaften, ``17.3.1`` Absatz-Eigenschaften, ``17.4`` Tabellen, ``17.6`` Abschnitte, ``17.5.2`` Inhaltssteuerelemente, ``17.7`` Stile,
  ``17.15`` Einstellungen, ``20.4`` Zeichnungen im Text, ``20.1`` DrawingML);
* ``VML`` (ECMA-376 Teil 4, Übergangsformat) für das Wasserzeichen der Kopfzeile.

Das Verhalten von Word, LibreOffice und ONLYOFFICE ist hier nicht festgeschrieben: Wo es von der Vorgabe abweicht, entscheidet das Vergleichssystem
(``werkzeuge/pruefungen/dokument_vergleich.py``) an Referenzdokumenten, nicht diese Tabelle.

``Umgang``:
  ``abgebildet``  der Leser übersetzt das Element in ein Feld des Modells, der Schreiber schreibt es aus dem Modell (Teile davon können dabei verloren gehen: siehe ``verlust``)
  ``erhalten``    das Modell trägt das Element unverändert (``docx_roh``) und der Schreiber setzt es wieder ein; es wird nicht dargestellt und nicht bearbeitet
  ``ausserhalb``  das Element liegt außerhalb dessen, was Leser und Schreiber behandeln (zum Beispiel Teile der Datei, die nicht Text sind); es geht beim Speichern verloren
"""
from __future__ import annotations

from dataclasses import dataclass

ABGEBILDET, ERHALTEN, AUSSERHALB = "abgebildet", "erhalten", "ausserhalb"
UMGAENGE = (ABGEBILDET, ERHALTEN, AUSSERHALB)

ECMA = "ECMA-376 Teil 1"


@dataclass(frozen=True)
class Regel:
    element: str                     # Pfad wie "w:rPr/w:b"
    umgang: str                      # abgebildet | erhalten | ausserhalb
    wirkt: bool                      # beeinflusst die sichtbare Darstellung (dann meldet der Import „erhalten, nicht dargestellt“)
    quelle: str                      # Formatvorgabe, Kapitel
    modell: str = ""                 # Feld im Modell bei „abgebildet“
    verlust: str = ""                # was bei „abgebildet“ nicht ins Modell kommt


def _r(element: str, umgang: str, wirkt: bool, quelle: str, modell: str = "", verlust: str = "") -> Regel:
    return Regel(element, umgang, wirkt, quelle, modell, verlust)


_LAUF, _ABSATZ, _TABELLE, _ABSCHNITT, _SDT, _STIL, _ZEICHNUNG = (f"{ECMA}, 17.3.2", f"{ECMA}, 17.3.1", f"{ECMA}, 17.4", f"{ECMA}, 17.6", f"{ECMA}, 17.5.2",
                                                                f"{ECMA}, 17.7", f"{ECMA}, 20.4")

REGELN: tuple[Regel, ...] = (
    # Läufe
    _r("w:rPr/w:rStyle", ABGEBILDET, True, _LAUF, "Zeichenformat.vorlage (Formatvorlage der Art zeichen)"),
    _r("w:rPr/w:rFonts", ABGEBILDET, True, _LAUF, "Zeichenformat.schrift", "nur ascii/hAnsi; eastAsia, cs und Themenschriften bleiben unbeachtet"),
    _r("w:rPr/w:sz", ABGEBILDET, True, _LAUF, "Zeichenformat.groesse_pt"),
    _r("w:rPr/w:b", ABGEBILDET, True, _LAUF, "Zeichenformat.fett"),
    _r("w:rPr/w:i", ABGEBILDET, True, _LAUF, "Zeichenformat.kursiv"),
    _r("w:rPr/w:strike", ABGEBILDET, True, _LAUF, "Zeichenformat.durchgestrichen"),
    _r("w:rPr/w:dstrike", ABGEBILDET, True, _LAUF, "Zeichenformat.durchgestrichen", "doppelt durchgestrichen wird einfach"),
    _r("w:rPr/w:caps", ABGEBILDET, True, _LAUF, "Zeichenformat.grossbuchstaben"),
    _r("w:rPr/w:smallCaps", ABGEBILDET, True, _LAUF, "Zeichenformat.kapitaelchen"),
    _r("w:rPr/w:u", ABGEBILDET, True, _LAUF, "Zeichenformat.unterstrichen", "Linienart und Farbe der Unterstreichung"),
    _r("w:rPr/w:vertAlign", ABGEBILDET, True, _LAUF, "Zeichenformat.hoch_tief"),
    _r("w:rPr/w:color", ABGEBILDET, True, _LAUF, "Zeichenformat.farbe", "Themenfarben"),
    _r("w:rPr/w:highlight", ABGEBILDET, True, _LAUF, "Zeichenformat.marker"),
    _r("w:rPr/w:shd", ABGEBILDET, True, _LAUF, "Zeichenformat.marker", "Muster der Schattierung"),
    _r("w:rPr/w:spacing", ABGEBILDET, True, _LAUF, "Zeichenformat.zeichenabstand (Art 1: Bildpunkte)"),
    _r("w:rPr/w:vanish", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:position", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:w", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:bdr", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:effect", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:em", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:emboss", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:imprint", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:outline", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:shadow", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:fitText", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:rtl", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:lang", ERHALTEN, False, _LAUF),
    _r("w:rPr/w:kern", ERHALTEN, False, _LAUF),
    _r("w:rPr/w:noProof", ERHALTEN, False, _LAUF),
    _r("w:rPr/w:bCs", ERHALTEN, False, _LAUF),
    _r("w:rPr/w:iCs", ERHALTEN, False, _LAUF),
    _r("w:rPr/w:szCs", ERHALTEN, False, _LAUF),
    _r("w:rPr/w:cs", ERHALTEN, False, _LAUF),
    _r("w:rPr/w:eastAsianLayout", ERHALTEN, True, _LAUF),
    _r("w:rPr/w:webHidden", ERHALTEN, False, _LAUF),
    # Absätze
    _r("w:pPr/w:pStyle", ABGEBILDET, True, _ABSATZ, "Absatzformat.vorlage"),
    _r("w:pPr/w:jc", ABGEBILDET, True, _ABSATZ, "Absatzformat.ausrichtung"),
    _r("w:pPr/w:ind", ABGEBILDET, True, _ABSATZ, "Absatzformat.einzug_*", "Einheiten in Zeichen (leftChars …)"),
    _r("w:pPr/w:spacing", ABGEBILDET, True, _ABSATZ, "Absatzformat.abstand_* und zeilenabstand*", "automatische Abstände (beforeAutospacing)"),
    _r("w:pPr/w:pageBreakBefore", ABGEBILDET, True, _ABSATZ, "Absatzformat.seitenumbruch_vor"),
    _r("w:pPr/w:shd", ABGEBILDET, True, _ABSATZ, "Absatzformat.hintergrund", "Muster der Schattierung"),
    _r("w:pPr/w:numPr", ABGEBILDET, True, _ABSATZ, "Absatz.liste_id und ebene"),
    _r("w:pPr/w:tabs", ABGEBILDET, True, _ABSATZ, "Absatzformat.tabstopps und tabfuell"),
    _r("w:pPr/w:pBdr", ABGEBILDET, True, _ABSATZ, "Absatzformat.rahmen", "unterschiedliche Linien je Seite, Linien zwischen Absätzen: dann bleibt das Original erhalten"),
    _r("w:pPr/w:rPr", ABGEBILDET, True, _ABSATZ, "Absatz.zeichenformat", "unbekannte Eigenschaften der Absatzmarke bleiben als docx_roh erhalten"),
    _r("w:pPr/w:sectPr", ABGEBILDET, True, _ABSCHNITT, "Abschnitt"),
    _r("w:pPr/w:framePr", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:keepNext", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:keepLines", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:widowControl", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:contextualSpacing", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:outlineLvl", ERHALTEN, False, _ABSATZ),
    _r("w:pPr/w:bidi", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:textDirection", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:suppressLineNumbers", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:suppressAutoHyphens", ERHALTEN, True, _ABSATZ),
    _r("w:pPr/w:textAlignment", ERHALTEN, True, _ABSATZ),
    # Inhaltssteuerelemente und Formulare
    _r("w:sdt", ABGEBILDET, False, _SDT, "Absatzformat.docx_sdt / Zeichenformat.docx_sdt", "Inhalt mit Tabelle in einem Block-Steuerelement und verschachtelte Steuerelemente: Datei wird auf dem bisherigen Weg gelesen"),
    _r("w:sdt/w:sdtPr", ERHALTEN, False, _SDT),
    _r("w:sdt/w:sdtEndPr", ERHALTEN, False, _SDT),
    # Tabellen
    _r("w:tblPr/w:tblStyle", ABGEBILDET, True, _TABELLE, "Tabellenformat.vorlage (Formatvorlage der Art tabelle, Original-XML erhalten)"),
    _r("w:tblPr/w:tblBorders", ABGEBILDET, True, _TABELLE, "Tabellenformat.rahmen_*", "unterschiedliche Linien je Kante: dann bleibt das Original erhalten"),
    _r("w:tblPr/w:tblDescription", ABGEBILDET, False, _TABELLE, "Tabellenformat.alt_text"),
    _r("w:tblPr/w:tblW", AUSSERHALB, True, _TABELLE),
    _r("w:tblPr/w:tblLayout", AUSSERHALB, True, _TABELLE),
    _r("w:tblPr/w:jc", ERHALTEN, True, _TABELLE),
    _r("w:tblPr/w:tblInd", ERHALTEN, True, _TABELLE),
    _r("w:tblPr/w:tblCellMar", ERHALTEN, True, _TABELLE),
    _r("w:tblPr/w:tblpPr", ERHALTEN, True, _TABELLE),
    _r("w:tblPr/w:tblLook", ERHALTEN, True, _TABELLE),
    _r("w:trPr/w:trHeight", ABGEBILDET, True, _TABELLE, "Tabelle.zeilenhoehen", "Regel „genau“ wird zu „mindestens“"),
    _r("w:trPr/w:tblHeader", ABGEBILDET, True, _TABELLE, "Tabellenformat.kopfzeilen"),
    _r("w:trPr/w:cantSplit", ERHALTEN, True, _TABELLE),
    _r("w:tcPr/w:tcW", ABGEBILDET, True, _TABELLE, "Tabelle.spaltenbreiten (aus w:tblGrid)"),
    _r("w:tcPr/w:gridSpan", ABGEBILDET, True, _TABELLE, "Zelle.spaltenspanne"),
    _r("w:tcPr/w:vMerge", ABGEBILDET, True, _TABELLE, "Zelle.zeilenspanne"),
    _r("w:tcPr/w:shd", ABGEBILDET, True, _TABELLE, "Zellformat.hintergrund"),
    _r("w:tcPr/w:vAlign", ABGEBILDET, True, _TABELLE, "Zellformat.vertikal"),
    _r("w:tcPr/w:tcBorders", ABGEBILDET, True, _TABELLE, "Zellformat.rahmen_*", "Diagonalen und innere Linien: dann bleibt das Original erhalten"),
    _r("w:tcPr/w:tcMar", ERHALTEN, True, _TABELLE),
    _r("w:tcPr/w:noWrap", ERHALTEN, True, _TABELLE),
    _r("w:tcPr/w:textDirection", ERHALTEN, True, _TABELLE),
    # Abschnitte und Seiten
    _r("w:sectPr/w:pgSz", ABGEBILDET, True, _ABSCHNITT, "PageSettings.width_mm, height_mm"),
    _r("w:sectPr/w:pgMar", ABGEBILDET, True, _ABSCHNITT, "PageSettings.margin_*, kopf_abstand_mm, fuss_abstand_mm", "gutter (Bundsteg)"),
    _r("w:sectPr/w:cols", ABGEBILDET, True, _ABSCHNITT, "PageSettings.spalten*"),
    _r("w:sectPr/w:type", ABGEBILDET, True, _ABSCHNITT, "Abschnitt.beginn"),
    _r("w:sectPr/w:titlePg", ABGEBILDET, True, _ABSCHNITT, "PageSettings.diff_first"),
    _r("w:sectPr/w:headerReference", ABGEBILDET, True, _ABSCHNITT, "PageSettings.header/first_header", "Kopfzeilen mit Tabellen und Objekten: Datei wird auf dem bisherigen Weg gelesen"),
    _r("w:sectPr/w:footerReference", ABGEBILDET, True, _ABSCHNITT, "PageSettings.footer/first_footer"),
    _r("w:sectPr/w:pgBorders", ABGEBILDET, True, _ABSCHNITT, "PageSettings.border", "unterschiedliche Linien je Seite: dann bleibt das Original erhalten"),
    _r("w:sectPr/w:lnNumType", ABGEBILDET, True, _ABSCHNITT, "PageSettings.zeilennummern/zeilennummern_neu", "Abstand und Schrittweite der Zahlen bleiben unbeachtet"),
    _r("w:sectPr/w:pgNumType", ABGEBILDET, True, _ABSCHNITT, "PageSettings.seiten_format/seiten_start", "Kapitelnummer vor der Seitenzahl bleibt unbeachtet"),
    _r("w:sectPr/w:docGrid", ERHALTEN, False, _ABSCHNITT),                       # Zeilenraster: Word schreibt es in jede Datei, ohne sichtbare Wirkung im Lauftext
    _r("w:sectPr/w:vAlign", ERHALTEN, True, _ABSCHNITT),
    _r("w:sectPr/w:footnotePr", ERHALTEN, True, _ABSCHNITT),
    _r("w:sectPr/w:endnotePr", ERHALTEN, True, _ABSCHNITT),
    _r("w:sectPr/w:textDirection", ERHALTEN, True, _ABSCHNITT),
    _r("w:sectPr/w:bidi", ERHALTEN, True, _ABSCHNITT),
    # Stile
    _r("w:style[@w:type='paragraph']", ABGEBILDET, True, _STIL, "Formatvorlage (art absatz)", "unbekannte Eigenschaften der Vorlage bleiben in Formatvorlage.zusatz erhalten"),
    _r("w:style[@w:type='character']", ABGEBILDET, True, _STIL, "Formatvorlage (art zeichen), Original-XML in zusatz"),
    _r("w:style[@w:type='table']", ABGEBILDET, True, _STIL, "Formatvorlage (art tabelle), Original-XML in zusatz"),
    _r("w:style[@w:type='numbering']", AUSSERHALB, False, _STIL),
    # Zeichnungen und Wasserzeichen
    _r("w:drawing/wp:inline/a:graphic/wps:wsp", ABGEBILDET, True, _ZEICHNUNG, "InlineObjekt (art form oder textfeld), Original-XML in daten.docx_roh",
       "Verläufe, Effekte, Textrichtung, Texteffekte bleiben im Original erhalten, werden aber nicht gezeichnet"),
    _r("w:drawing/wp:anchor/a:graphic/wps:wsp", ABGEBILDET, True, _ZEICHNUNG, "FreiesObjekt (art form oder textfeld), Original-XML in daten.docx_roh"),
    _r("w:drawing/a:graphic/wpg:wgp", AUSSERHALB, True, _ZEICHNUNG),
    _r("w:drawing/a:graphic/wps:wsp/wps:linkedTxbx", AUSSERHALB, True, _ZEICHNUNG),
    _r("w:pict/v:shape[PowerPlusWaterMarkObject]", ABGEBILDET, True, "VML (ECMA-376 Teil 4, Übergangsformat)", "PageSettings.watermark (nur Text)", "Bild-Wasserzeichen: nicht abgebildet"),
    _r("w:pict (übrige VML-Objekte)", AUSSERHALB, True, "VML (ECMA-376 Teil 4, Übergangsformat)"),
    # Einstellungen und Teile
    _r("w:settings/w:alignBordersAndEdges", ABGEBILDET, True, f"{ECMA}, 17.15", "PageSettings.border.ausrichten"),
    _r("w:settings/w:bordersDoNotSurroundHeader", ABGEBILDET, True, f"{ECMA}, 17.15", "PageSettings.border.kopf"),
    _r("w:settings/w:bordersDoNotSurroundFooter", ABGEBILDET, True, f"{ECMA}, 17.15", "PageSettings.border.fuss"),
    _r("w:settings (übrige Einstellungen)", AUSSERHALB, False, f"{ECMA}, 17.15"),
    _r("Teile ohne Text: theme, customXml, glossary, vbaProject, webSettings", AUSSERHALB, False, f"{ECMA}, Teil 2 (Open Packaging Conventions)"),
)

_NACH_ELEMENT = {r.element: r for r in REGELN}


def regel(element: str) -> Regel | None:
    """Die Regel zu einem Pfad wie ``w:rPr/w:spacing``; ``None``, wenn keine Vorgabe dazu aufgenommen ist."""
    return _NACH_ELEMENT.get(element)


def umgang(art: str, name: str) -> str | None:
    """Wie mit dem Element ``name`` (ohne Namensraum, zum Beispiel ``spacing``) unter ``art`` (``rPr``, ``pPr``, ``tblPr``, ``trPr``, ``tcPr``, ``sectPr``) umgegangen wird; ``None``: unbekannt."""
    r = _NACH_ELEMENT.get(f"w:{art}/w:{name}")
    return r.umgang if r is not None else None


def erhaltene_elemente(dok) -> dict[str, int]:
    """Zählt die erhaltenen (nicht dargestellten) Elemente im Dokument: Name („rPr/spacing“) → Anzahl. Nur Elemente, deren Regel sichtbare Wirkung angibt oder die keine Regel haben."""
    from lxml import etree
    zaehler: dict[str, int] = {}

    def zaehle(art: str, texte) -> None:
        for t in texte or ():
            try:
                name = etree.QName(etree.fromstring(t)).localname
            except etree.XMLSyntaxError:
                continue
            r = _NACH_ELEMENT.get(f"w:{art}/w:{name}")
            if r is None or r.wirkt:
                zaehler[f"{art}/{name}"] = zaehler.get(f"{art}/{name}", 0) + 1

    from core.dokument.dokument import Absatz, Lauf
    for ab in dok.abschnitte:
        zaehle("sectPr", getattr(ab.seite, "docx_roh", None))
    for a in dok.absaetze():
        zaehle("pPr", a.format.get("docx_roh"))
        zaehle("rPr", a.zeichenformat.get("docx_roh"))
        for x in a.inhalte:
            if isinstance(x, Lauf):
                zaehle("rPr", x.format.get("docx_roh"))
    for t in dok.tabellen():
        zaehle("tblPr", t.format.get("docx_roh"))
        for zeile in (t.format.get("docx_roh_zeilen") or {}).values():
            zaehle("trPr", zeile)
        for zeile in t.zellen:
            for z in zeile:
                zaehle("tcPr", z.format.get("docx_roh"))
    return zaehler


def hinweis_erhalten(dok) -> str | None:
    """Ein Satz für den Importbericht über Eigenschaften, die erhalten, aber nicht dargestellt werden; ``None``, wenn es keine gibt."""
    z = erhaltene_elemente(dok)
    if not z:
        return None
    teile = [f"{n}× {name}" for name, n in sorted(z.items(), key=lambda kv: (-kv[1], kv[0]))[:8]]
    mehr = len(z) - len(teile)
    return "Erhalten, aber nicht dargestellt (bleibt beim Speichern bestehen): " + ", ".join(teile) + (f" und {mehr} weitere Arten" if mehr > 0 else "")
