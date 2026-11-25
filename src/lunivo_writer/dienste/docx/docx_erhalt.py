"""Unbekannte DOCX-Eigenschaften im Modell erhalten (ohne Qt).

Was der Leser nicht in ein Feld des Modells übersetzt, geht nicht verloren: Das Element wird als XML-Text in die Eigenschaft ``docx_roh`` des Formats gelegt
(Zeichen-, Absatz-, Tabellen-, Zellformat, ``PageSettings.docx_roh``, ``Formatvorlage.zusatz``) und vom Schreiber an der schemagerechten Stelle wieder eingesetzt.
Das gilt für alle Kinder von ``w:rPr``, ``w:pPr``, ``w:tblPr``, ``w:tcPr``, ``w:trPr`` und ``w:sectPr``, die der Leser nicht selbst abbildet.

Grenzen, ehrlich: Ein erhaltenes Element wird nicht dargestellt und nicht bearbeitet, nur wieder geschrieben. Trägt es eine Beziehung zu einem anderen Teil der Datei
(``r:id``, ``r:embed`` …), lässt es sich nicht allein weitergeben; ``sammeln`` meldet das mit ``Beziehung``, und der Aufrufer nimmt dann den bisherigen Weg."""
from __future__ import annotations

import copy

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
W = "{" + W_NS + "}"
ROH = "docx_roh"


class Beziehung(ValueError):
    """Das Element verweist auf einen anderen Teil der Datei und lässt sich deshalb nicht allein erhalten."""


# Reihenfolge der Kindelemente nach ECMA-376 (Teil 1): Der Schreiber sortiert nach dem Einsetzen stabil in diese Folge.
REIHENFOLGE: dict[str, tuple[str, ...]] = {
    "rPr": ("rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "dstrike", "outline", "shadow", "emboss", "imprint", "noProof", "snapToGrid",
            "vanish", "webHidden", "color", "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd", "fitText", "vertAlign", "rtl",
            "cs", "em", "lang", "eastAsianLayout", "specVanish", "oMath", "rPrChange"),
    "pPr": ("pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
            "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
            "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection", "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
            "rPr", "sectPr", "pPrChange"),
    "tblPr": ("tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize", "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd", "tblBorders",
              "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption", "tblDescription", "tblPrChange"),
    "trPr": ("cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter", "cantSplit", "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden", "ins", "del",
             "trPrChange"),
    "tcPr": ("cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd", "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark", "headers",
             "cellIns", "cellDel", "cellMerge", "tcPrChange"),
    "sectPr": ("headerReference", "footerReference", "footnotePr", "endnotePr", "type", "pgSz", "pgMar", "paperSrc", "pgBorders", "lnNumType", "pgNumType", "cols",
               "formProt", "vAlign", "noEndnote", "titlePg", "textDirection", "bidi", "rtlGutter", "docGrid", "printerSettings", "sectPrChange"),
}

# Was der Leser selbst in Felder des Modells übersetzt (alles andere wird erhalten); ``rStyle`` und ``pStyle`` gehören den Vorlagen.
ABGEBILDET: dict[str, frozenset] = {
    "rPr": frozenset({"rStyle", "rFonts", "sz", "b", "i", "strike", "dstrike", "caps", "smallCaps", "u", "vertAlign", "color", "highlight", "shd", "spacing"}),
    "pPr": frozenset({"pStyle", "jc", "ind", "spacing", "pageBreakBefore", "shd", "numPr", "tabs", "rPr", "sectPr", "bidi", "outlineLvl"}),
    "tblPr": frozenset({"tblStyle", "tblBorders", "tblDescription"}),
    "trPr": frozenset({"trHeight", "tblHeader"}),
    "tcPr": frozenset({"tcW", "gridSpan", "vMerge", "shd", "vAlign", "tcBorders"}),
    "sectPr": frozenset({"pgSz", "pgMar", "headerReference", "footerReference", "titlePg", "cols", "type", "pgBorders", "lnNumType", "pgNumType"}),
}


def _name(e) -> str:
    return etree.QName(e).localname


def als_text(element) -> str:
    """Ein Element mit seinen Namensraumangaben als eigenständigen XML-Text."""
    kopie = copy.deepcopy(element)
    kopie.tail = None
    return etree.tostring(kopie, encoding="unicode")


def hat_beziehung(element) -> bool:
    """Ob das Element oder ein Nachfahre ein Attribut aus dem Namensraum der Beziehungen (``r:``) trägt."""
    return any(isinstance(a, str) and a.startswith("{" + R_NS + "}") for k in element.iter() if isinstance(k.tag, str) for a in k.attrib)


def sammeln(eltern, art: str, extra_bekannt: frozenset | set = frozenset(), ausser: frozenset | set = frozenset()) -> list[str]:
    """Die Kinder von ``eltern`` (``w:rPr`` …), die der Leser nicht abbildet, als XML-Texte. ``extra_bekannt``: weitere Namen, die der Aufrufer selbst übernimmt; ``ausser``:
    Namen, die sonst abgebildet werden, hier aber (weil das Modell sie nicht ganz fasst) im Original erhalten bleiben sollen. ``Beziehung`` bei Verweisen auf andere Teile."""
    if eltern is None:
        return []
    bekannt = (ABGEBILDET[art] | frozenset(extra_bekannt)) - frozenset(ausser)
    aus: list[str] = []
    for kind in eltern:
        if not isinstance(kind.tag, str) or _name(kind) in bekannt:
            continue
        if hat_beziehung(kind):
            raise Beziehung(_name(kind))
        aus.append(als_text(kind))
    return aus


def ordnen(eltern, art: str) -> None:
    """Die Kinder von ``eltern`` stabil in die Reihenfolge des Schemas bringen (Unbekanntes bleibt am Ende in seiner Reihenfolge)."""
    folge = REIHENFOLGE[art]
    rang = {n: i for i, n in enumerate(folge)}
    kinder = [k for k in eltern if isinstance(k.tag, str)]
    sortiert = sorted(kinder, key=lambda k: rang.get(_name(k), len(folge)))
    if sortiert != kinder:
        for k in sortiert:
            eltern.append(k)


def einsetzen(eltern, texte, art: str) -> None:
    """Erhaltene Elemente (XML-Texte) in ``eltern`` setzen und die Reihenfolge nach dem Schema herstellen. Ein Element, das es dort schon gibt, bleibt unverändert."""
    if not texte:
        return
    from docx.oxml import parse_xml
    for t in texte:
        e = parse_xml(t)
        if _name(e) not in ("ins", "del"):
            for alt in [k for k in eltern if isinstance(k.tag, str) and _name(k) == _name(e)]:      # das Original gewinnt gegen den Standard der Vorlage
                eltern.remove(alt)
        eltern.append(e)
    ordnen(eltern, art)


def in_format(format: dict, texte: list[str]) -> dict:
    """``format`` mit den erhaltenen Elementen (wenn es welche gibt)."""
    if texte:
        format[ROH] = list(texte)
    return format
