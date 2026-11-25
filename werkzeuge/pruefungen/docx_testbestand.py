"""Erzeugt den DOCX-Testbestand (1000 Dateien), der die Funktionen von Lunivo Writer abdeckt.

Aufruf (aus dem Projektordner):   python -I werkzeuge/pruefungen/docx_testbestand.py [Ausgabeordner] [--nur kategorie]
Vorgabe-Ausgabe: ``~/Lunivo-Testdateien/docx`` (dort sucht auch ``referenzbestand.py``).

Eigenschaften
* Nur Standardbibliothek: die Pakete werden als ZIP mit eigenem WordprocessingML geschrieben (kein python-docx, kein Qt, kein Lunivo-Code) —
  der Bestand ist damit eine unabhängige Quelle und wird nicht durch Fehler von Lunivos eigenem Leser/Schreiber verfälscht.
* Deterministisch: gleiche Eingabe → gleiche Dateien (Zufall nur aus festem Startwert je Datei).
* Nur eigener, erfundener Inhalt; keine Personendaten, kein geschütztes Material.
* ``manifest.csv``: je Datei Kategorie, Merkmal und die Rohzählung aus dem erzeugten XML (Absätze, Tabellen, Bilder, Formen …) als unabhängiger Sollwert.
Die Kategorien folgen dem Dokumentkern (core/document: Zeichen-, Absatz-, Tabellen-, Zellformat, Listen, Vorlagen, Objekte, Noten, Kommentare, Felder,
Steuerelemente, Kopf-/Fußzeilen, Abschnitte) und den Lesern in dienste/docx_*.py (Formen, Gruppen, WordArt, Diagramme, Füllungen, Effekte, Rohbewahrung).
Ehrliche Grenze: alles stammt aus einem Erzeuger; Dokumente aus Word, LibreOffice oder Google Docs bleiben Sache des Eigentümers (``tests/korpus_extern``).
"""
from __future__ import annotations

import base64
import csv
import io
import os
import random
import re
import struct
import sys
import zipfile
import zlib
from xml.dom import minidom
from xml.sax.saxutils import escape as _esc

# --------------------------------------------------------------------------------------------------------------------- Namen
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "wpg": "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup",
    "w14": "http://schemas.microsoft.com/office/word/2010/wordml",
    "w15": "http://schemas.microsoft.com/office/word/2012/wordml",
    "wp14": "http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "w10": "urn:schemas-microsoft-com:office:word",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "asvg": "http://schemas.microsoft.com/office/drawing/2016/SVG/main",
}
NSALL = " ".join(f'xmlns:{k}="{v}"' for k, v in NS.items()) + ' mc:Ignorable="w14 w15 wp14"'
RT = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
CT = {
    "dok": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
    "styles": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
    "settings": "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml",
    "numbering": "application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml",
    "fonttable": "application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml",
    "footnotes": "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml",
    "endnotes": "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml",
    "comments": "application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml",
    "commentsex": "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml",
    "header": "application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml",
    "footer": "application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml",
    "theme": "application/vnd.openxmlformats-officedocument.theme+xml",
    "chart": "application/vnd.openxmlformats-officedocument.drawingml.chart+xml",
    "core": "application/vnd.openxmlformats-package.core-properties+xml",
    "app": "application/vnd.openxmlformats-officedocument.extended-properties+xml",
    "custom": "application/vnd.openxmlformats-officedocument.custom-properties+xml",
    "customxml": "application/xml",
    "websettings": "application/vnd.openxmlformats-officedocument.wordprocessingml.webSettings+xml",
}
SAETZE = [
    "Der schnelle braune Fuchs springt über den faulen Hund.", "Heute prüfen wir, ob sich der Text sauber umbrechen lässt.",
    "Zwölf Boxkämpfer jagen Viktor quer über den großen Sylter Deich.", "Kleine Änderungen am Format dürfen den Inhalt nicht verändern.",
    "Die Tabelle enthält Zahlen wie 1.234,56 und Brüche wie ½ oder ¾.", "Ein längerer Satz mit Nebensätzen, der absichtlich mehrere Zeilen füllt, damit der Blocksatz sichtbar wird.",
    "Übung macht den Meister, aber Ordnung hält das Dokument zusammen.", "Silbentrennung, Zeilenabstand und Einzüge wirken erst bei mehreren Zeilen.",
    "Straßenbahnfahrer essen gern Äpfel, Öl und Übergrößen-Brötchen.", "Dieser Satz endet mit einem Doppelpunkt: danach folgt eine Aufzählung.",
]
FARBEN = ["FF0000", "00AA00", "0000FF", "FFA500", "800080", "008080", "808080", "000000", "C00000", "1F4E79", "7F6000", "FFD966", "A9D18E", "F4B183", "D9D9D9"]
SCHRIFTEN = ["Arial", "Times New Roman", "Courier New", "Calibri", "Cambria", "Verdana", "Georgia", "Liberation Serif", "DejaVu Sans", "Noto Sans"]


def e(s) -> str:
    return _esc(str(s), {'"': "&quot;"})


def pick(liste, i):
    return liste[i % len(liste)]


def satz(rng, n=1) -> str:
    return " ".join(rng.choice(SAETZE) for _ in range(n))


# --------------------------------------------------------------------------------------------------------------------- Reihenfolge der Eigenschaften
PPR_ORDER = "pStyle keepNext keepLines pageBreakBefore framePr widowControl numPr suppressLineNumbers pBdr shd tabs suppressAutoHyphens kinsoku wordWrap overflowPunct topLinePunct autoSpaceDE autoSpaceDN bidi adjustRightInd snapToGrid spacing ind contextualSpacing mirrorIndents suppressOverlap jc textDirection textAlignment textboxTightWrap outlineLvl divId cnfStyle rPr sectPr pPrChange".split()
RPR_ORDER = "rStyle rFonts b bCs i iCs caps smallCaps strike dstrike outline shadow emboss imprint noProof snapToGrid vanish webHidden color spacing w kern position sz szCs highlight u effect bdr shd fitText vertAlign rtl cs em lang eastAsianLayout specVanish oMath".split()
TCPR_ORDER = "cnfStyle tcW gridSpan hMerge vMerge tcBorders shd noWrap tcMar textDirection tcFitText vAlign hideMark".split()
TBLPR_ORDER = "tblStyle tblpPr tblOverlap bidiVisual tblStyleRowBandSize tblStyleColBandSize tblW jc tblCellSpacing tblInd tblBorders shd tblLayout tblCellMar tblLook tblCaption tblDescription".split()
SETTINGS_ORDER = "writeProtection view zoom mirrorMargins trackRevisions documentProtection defaultTabStop autoHyphenation consecutiveHyphenLimit hyphenationZone doNotHyphenateCaps evenAndOddHeaders bookFoldPrinting displayBackgroundShape characterSpacingControl footnotePr endnotePr compat docVars themeFontLang clrSchemeMapping decimalSymbol listSeparator".split()
_TAG = re.compile(r"<(?:w14:|w15:)?([A-Za-z]+)")


def ordne(teile, ordnung) -> str:
    """Sortiert Eigenschaften nach Schemareihenfolge; jede Eigenschaft höchstens einmal (die letzte gilt)."""
    vorhanden: dict[str, tuple[int, str]] = {}
    for t in teile:
        if not t:
            continue
        m = _TAG.match(t)
        name = m.group(1) if m else t
        rang = ordnung.index(name) if name in ordnung and not t.startswith("<w14:") else len(ordnung)
        vorhanden[t[: t.find(" ")] if t.startswith("<w14:") else name] = (rang, t)
    return "".join(t for _, t in sorted(vorhanden.values(), key=lambda x: x[0]))


# --------------------------------------------------------------------------------------------------------------------- Bausteine für Inhalt
def run(text="", rpr="", extra="") -> str:
    inner = (f'<w:t xml:space="preserve">{e(text)}</w:t>' if text != "" else "") + extra
    return f"<w:r>{f'<w:rPr>{rpr}</w:rPr>' if rpr else ''}{inner}</w:r>"


def para(text="", ppr="", rpr="", inhalt="") -> str:
    return f"<w:p>{f'<w:pPr>{ppr}</w:pPr>' if ppr else ''}{run(text, rpr) if text else ''}{inhalt}</w:p>"


def heading(text, stufe=1) -> str:
    return para(text, f'<w:pStyle w:val="Heading{stufe}"/>')


def feld(anweisung, ergebnis="1", rpr="", dirty=False) -> str:
    rp = f"<w:rPr>{rpr}</w:rPr>" if rpr else ""
    d = ' w:dirty="true"' if dirty else ""
    return (f'<w:r>{rp}<w:fldChar w:fldCharType="begin"{d}/></w:r><w:r>{rp}<w:instrText xml:space="preserve"> {e(anweisung)} </w:instrText></w:r>'
            f'<w:r>{rp}<w:fldChar w:fldCharType="separate"/></w:r><w:r>{rp}<w:t>{e(ergebnis)}</w:t></w:r><w:r>{rp}<w:fldChar w:fldCharType="end"/></w:r>')


def zelle(inhalt, tcpr="", breite=None) -> str:
    """Tabellenzelle; ``tcpr`` muss bereits in Schemareihenfolge stehen (gridSpan, vMerge, tcBorders, shd, noWrap, tcMar, textDirection, tcFitText, vAlign)."""
    w = f'<w:tcW w:w="{breite}" w:type="dxa"/>' if breite else ""
    return f"<w:tc><w:tcPr>{w}{tcpr}</w:tcPr>{inhalt if inhalt else para()}</w:tc>"


def tabelle(zeilen, spalten_breiten, tblpr="", zeilenpr=None, gitter=True) -> str:
    """``zeilen``: Liste von Listen mit Zellen-XML (fertig, mit ``zelle``). ``zeilenpr``: {zeilennr: trPr}."""
    g = "".join(f'<w:gridCol w:w="{b}"/>' for b in spalten_breiten)
    out = [f"<w:tbl><w:tblPr>{tblpr}</w:tblPr><w:tblGrid>{g}</w:tblGrid>"]
    for n, z in enumerate(zeilen):
        pr = (zeilenpr or {}).get(n, "")
        out.append(f"<w:tr>{f'<w:trPr>{pr}</w:trPr>' if pr else ''}{''.join(z)}</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


def einfache_tabelle(rng, zeilen, spalten, breite=9000, tblpr='<w:tblStyle w:val="TableGrid"/>', kopf=False) -> str:
    b = breite // spalten
    zl = []
    for r in range(zeilen):
        zl.append([zelle(para(("Kopf " if kopf and r == 0 else "") + f"Z{r + 1}S{c + 1} " + rng.choice(SAETZE).split()[0]), breite=b) for c in range(spalten)])
    return tabelle(zl, [b] * spalten, tblpr + f'<w:tblW w:w="{breite}" w:type="dxa"/>', {0: "<w:tblHeader/>"} if kopf else None)


# --------------------------------------------------------------------------------------------------------------------- Bilder
def png(b, h, rgb, muster=0) -> bytes:
    zeilen = []
    for y in range(h):
        z = bytearray([0])
        for x in range(b):
            if muster == 1:
                c = rgb if (x // 4 + y // 4) % 2 == 0 else (255 - rgb[0], 255 - rgb[1], 255 - rgb[2])
            elif muster == 2:
                c = (int(rgb[0] * x / b), int(rgb[1] * y / h), rgb[2])
            else:
                c = rgb
            z += bytes(c)
        zeilen.append(bytes(z))

    def teil(t, d):
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return b"\x89PNG\r\n\x1a\n" + teil(b"IHDR", struct.pack(">IIBBBBB", b, h, 8, 2, 0, 0, 0)) + teil(b"IDAT", zlib.compress(b"".join(zeilen))) + teil(b"IEND", b"")


def bmp(b, h, rgb) -> bytes:
    pad = (4 - (b * 3) % 4) % 4
    zeile = (bytes((rgb[2], rgb[1], rgb[0])) * b) + b"\0" * pad
    daten = zeile * h
    return b"BM" + struct.pack("<IHHI", 54 + len(daten), 0, 0, 54) + struct.pack("<IiiHHIIiiII", 40, b, h, 1, 24, 0, len(daten), 2835, 2835, 0, 0) + daten


GIF = base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
JPG = base64.b64decode("/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////wgALCAABAAEBAREA/8QAFBABAAAAAAAAAAAAAAAAAAAAAP/aAAgBAQABPxA=")
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="60" height="40" viewBox="0 0 60 40"><rect width="60" height="40" fill="#3366cc"/><circle cx="30" cy="20" r="14" fill="#ffcc00"/></svg>'
EMU_MM = 36000
EMU_PX = 9525


# --------------------------------------------------------------------------------------------------------------------- Dokument
class Dok:
    def __init__(s, rng: random.Random):
        s.rng = rng
        s.body: list[str] = []
        s.stile: list[str] = []
        s.num_abs: list[str] = []
        s.num: list[str] = []
        s.settings: list[str] = []
        s.sect = ""                       # inneres XML von w:sectPr des Dokuments
        s.teile: dict[str, tuple[str, bytes]] = {}
        s.rels: list[tuple[str, str, str, bool]] = []
        s.fussnoten: list[str] = []
        s.endnoten: list[str] = []
        s.kommentare: list[str] = []
        s.kommentare_ex: list[str] = []
        s.defaults = {"schrift": "Calibri", "groesse": 22, "nach": 160, "zeile": 259}
        s.stil_ohne = False
        s.ohne_stile = False
        s.ohne_nummerierung = False
        s.kern = {"titel": "Testdokument", "autor": "Lunivo Testbestand", "betreff": "", "stichwort": "", "beschreibung": ""}
        s.app_extra = ""
        s.eigene: list[tuple[str, str, str]] = []
        s.nid = 100
        s.bilder: dict[bytes, str] = {}
        s.hf_zaehler = 0
        s.diagramme = 0
        s.theme = True
        s.hintergrund = ""
        s.docvars = ""
        s.custom_xml = False

    # Beziehungen und Teile
    def rel(s, typ: str, ziel: str, extern=False) -> str:
        for r_id, t, z, ex in s.rels:
            if t == typ and z == ziel and ex == extern:
                return r_id
        r_id = f"rId{len(s.rels) + 10}"
        s.rels.append((r_id, typ, ziel, extern))
        return r_id

    def id(s) -> int:
        s.nid += 1
        return s.nid

    def bild(s, daten: bytes, ende="png") -> str:
        if daten in s.bilder:
            return s.bilder[daten]
        n = len(s.bilder) + 1
        pfad = f"media/image{n}.{ende}"
        s.teile["word/" + pfad] = ("", daten)
        s.bilder[daten] = s.rel(RT + "image", pfad)
        return s.bilder[daten]

    def kopf_fuss(s, art: str, inhalt: str, wurzel_extra="") -> str:
        s.hf_zaehler += 1
        pfad = f"{art}{s.hf_zaehler}.xml"
        tag = "hdr" if art == "header" else "ftr"
        s.teile["word/" + pfad] = (CT[art], f'<w:{tag} {NSALL}>{inhalt or para()}</w:{tag}>'.encode())
        return s.rel(RT + art, pfad)

    def fussnote(s, text, endnote=False, marke="", inhalt=None) -> str:
        liste = s.endnoten if endnote else s.fussnoten
        n = len(liste) + 2
        art = "endnote" if endnote else "footnote"
        ref = f'<w:r><w:rPr><w:rStyle w:val="{"EndnoteReference" if endnote else "FootnoteReference"}"/></w:rPr><w:{art}Ref/></w:r>'
        liste.append(f'<w:{art} w:id="{n}">' + (inhalt or para("", '<w:pStyle w:val="FootnoteText"/>', inhalt=ref + run(" " + text))) + f"</w:{art}>")
        mk = f' w:customMarkFollows="1"' if marke else ""
        return f'<w:r><w:rPr><w:rStyle w:val="{"EndnoteReference" if endnote else "FootnoteReference"}"/></w:rPr><w:{art}Reference w:id="{n}"{mk}/></w:r>' + (run(marke) if marke else "")

    def kommentar(s, text, autor="Prüfer", antwort_auf=None, erledigt=False, initialen="PR") -> tuple[int, str, str]:
        n = len(s.kommentare)
        pid = f"{0x10000000 + n:08X}"
        s.kommentare.append(f'<w:comment w:id="{n}" w:author="{e(autor)}" w:date="2026-03-0{1 + n % 8}T10:00:00Z" w:initials="{initialen}">'
                            f'<w:p w14:paraId="{pid}"><w:pPr><w:pStyle w:val="CommentText"/></w:pPr><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:annotationRef/></w:r>{run(text)}</w:p></w:comment>')
        par = f' w15:paraIdParent="{antwort_auf}"' if antwort_auf else ""
        s.kommentare_ex.append(f'<w15:commentEx w15:paraId="{pid}"{par} w15:done="{1 if erledigt else 0}"/>')
        return n, f'<w:commentRangeStart w:id="{n}"/>', f'<w:commentRangeEnd w:id="{n}"/><w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="{n}"/></w:r>', pid  # type: ignore[return-value]

    # Abschluss
    def styles_xml(s) -> str:
        d = s.defaults
        basis = f"""<w:styles {NSALL}><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="{d['schrift']}" w:hAnsi="{d['schrift']}" w:eastAsia="{d['schrift']}" w:cs="{d['schrift']}"/><w:sz w:val="{d['groesse']}"/><w:szCs w:val="{d['groesse']}"/><w:lang w:val="de-DE" w:eastAsia="en-US" w:bidi="ar-SA"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="{d['nach']}" w:line="{d['zeile']}" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:qFormat/></w:style>
<w:style w:type="character" w:default="1" w:styleId="DefaultParagraphFont"><w:name w:val="Default Paragraph Font"/><w:uiPriority w:val="1"/><w:semiHidden/><w:unhideWhenUsed/></w:style>
<w:style w:type="table" w:default="1" w:styleId="TableNormal"><w:name w:val="Normal Table"/><w:uiPriority w:val="99"/><w:semiHidden/><w:unhideWhenUsed/><w:tblPr><w:tblInd w:w="0" w:type="dxa"/><w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="108" w:type="dxa"/><w:bottom w:w="0" w:type="dxa"/><w:right w:w="108" w:type="dxa"/></w:tblCellMar></w:tblPr></w:style>
<w:style w:type="numbering" w:default="1" w:styleId="NoList"><w:name w:val="No List"/><w:uiPriority w:val="99"/><w:semiHidden/><w:unhideWhenUsed/></w:style>
<w:style w:type="table" w:styleId="TableGrid"><w:name w:val="Table Grid"/><w:basedOn w:val="TableNormal"/><w:uiPriority w:val="39"/><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:tblPr><w:tblBorders><w:top w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:left w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:bottom w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:right w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="auto"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="auto"/></w:tblBorders></w:tblPr></w:style>"""
        ueb = "".join(f'<w:style w:type="paragraph" w:styleId="Heading{n}"><w:name w:val="heading {n}"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="9"/><w:qFormat/><w:pPr><w:keepNext/><w:keepLines/><w:spacing w:before="{240 if n == 1 else 40}" w:after="0"/><w:outlineLvl w:val="{n - 1}"/></w:pPr><w:rPr><w:rFonts w:ascii="Cambria" w:hAnsi="Cambria"/><w:color w:val="2F5496"/><w:sz w:val="{max(22, 40 - 4 * n)}"/></w:rPr></w:style>' for n in range(1, 10))
        rest = """<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="10"/><w:qFormat/><w:pPr><w:spacing w:after="80" w:line="240" w:lineRule="auto"/><w:contextualSpacing/></w:pPr><w:rPr><w:sz w:val="56"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="11"/><w:qFormat/><w:rPr><w:color w:val="5A5A5A"/><w:spacing w:val="15"/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Quote"><w:name w:val="Quote"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="29"/><w:qFormat/><w:pPr><w:ind w:left="864" w:right="864"/><w:jc w:val="center"/></w:pPr><w:rPr><w:i/><w:iCs/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="34"/><w:qFormat/><w:pPr><w:ind w:left="720"/><w:contextualSpacing/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Header"><w:name w:val="header"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="99"/><w:pPr><w:tabs><w:tab w:val="center" w:pos="4513"/><w:tab w:val="right" w:pos="9026"/></w:tabs><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Footer"><w:name w:val="footer"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="99"/><w:pPr><w:tabs><w:tab w:val="center" w:pos="4513"/><w:tab w:val="right" w:pos="9026"/></w:tabs><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="TOCHeading"><w:name w:val="TOC Heading"/><w:basedOn w:val="Heading1"/><w:next w:val="Normal"/><w:uiPriority w:val="39"/></w:style>
<w:style w:type="paragraph" w:styleId="TOC1"><w:name w:val="toc 1"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="39"/><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9016"/></w:tabs><w:spacing w:after="100"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="TOC2"><w:name w:val="toc 2"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="39"/><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9016"/></w:tabs><w:spacing w:after="100"/><w:ind w:left="220"/></w:pPr></w:style>
<w:style w:type="paragraph" w:styleId="Caption"><w:name w:val="caption"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:uiPriority w:val="35"/><w:qFormat/><w:pPr><w:spacing w:after="200" w:line="240" w:lineRule="auto"/></w:pPr><w:rPr><w:i/><w:iCs/><w:color w:val="44546A"/><w:sz w:val="18"/></w:rPr></w:style>
<w:style w:type="character" w:styleId="Hyperlink"><w:name w:val="Hyperlink"/><w:uiPriority w:val="99"/><w:unhideWhenUsed/><w:rPr><w:color w:val="0563C1"/><w:u w:val="single"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="FootnoteText"><w:name w:val="footnote text"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="99"/><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="20"/></w:rPr></w:style>
<w:style w:type="character" w:styleId="FootnoteReference"><w:name w:val="footnote reference"/><w:uiPriority w:val="99"/><w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="EndnoteText"><w:name w:val="endnote text"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="99"/><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="20"/></w:rPr></w:style>
<w:style w:type="character" w:styleId="EndnoteReference"><w:name w:val="endnote reference"/><w:uiPriority w:val="99"/><w:rPr><w:vertAlign w:val="superscript"/></w:rPr></w:style>
<w:style w:type="character" w:styleId="CommentReference"><w:name w:val="annotation reference"/><w:uiPriority w:val="99"/><w:rPr><w:sz w:val="16"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="CommentText"><w:name w:val="annotation text"/><w:basedOn w:val="Normal"/><w:uiPriority w:val="99"/><w:pPr><w:spacing w:line="240" w:lineRule="auto"/></w:pPr><w:rPr><w:sz w:val="20"/></w:rPr></w:style>"""
        return basis + ueb + rest + "".join(s.stile) + "</w:styles>"

    def speichern(s, pfad: str) -> None:
        sect = f"<w:sectPr>{s.sect}</w:sectPr>" if s.sect != "KEIN" else ""
        if s.sect == "":
            sect = '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1417" w:right="1417" w:bottom="1134" w:left="1417" w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
        hint = f"<w:background {s.hintergrund}/>" if s.hintergrund else ""
        dok = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {NSALL}>{hint}<w:body>{"".join(s.body)}{sect}</w:body></w:document>'
        teile = dict(s.teile)
        rels = list(s.rels)
        if not s.ohne_stile:
            teile["word/styles.xml"] = (CT["styles"], ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + s.styles_xml()).encode())
            rels.append(("rId1", RT + "styles", "styles.xml", False))
        sett = list(s.settings)
        if s.fussnoten:
            sett.append('<w:footnotePr><w:footnote w:id="0"/><w:footnote w:id="1"/></w:footnotePr>')
        if s.endnoten:
            sett.append('<w:endnotePr><w:endnote w:id="0"/><w:endnote w:id="1"/></w:endnotePr>')
        sett.append('<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>') if not any(t.startswith("<w:compat") for t in sett) else None
        teile["word/settings.xml"] = (CT["settings"], f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings {NSALL}>{ordne(sett, SETTINGS_ORDER)}</w:settings>'.encode())
        rels.append(("rId2", RT + "settings", "settings.xml", False))
        if s.num_abs and not s.ohne_nummerierung:
            teile["word/numbering.xml"] = (CT["numbering"], f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:numbering {NSALL}>{"".join(s.num_abs)}{"".join(s.num)}</w:numbering>'.encode())
            rels.append(("rId3", RT + "numbering", "numbering.xml", False))
        teile["word/fontTable.xml"] = (CT["fonttable"], f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:fonts {NSALL}>' + "".join(f'<w:font w:name="{f}"><w:panose1 w:val="00000000000000000000"/><w:charset w:val="00"/><w:family w:val="auto"/><w:pitch w:val="variable"/></w:font>' for f in (s.defaults["schrift"], "Cambria", "Symbol", "Wingdings")) + "</w:fonts>")
        teile["word/fontTable.xml"] = (teile["word/fontTable.xml"][0], teile["word/fontTable.xml"][1].encode())
        rels.append(("rId4", RT + "fontTable", "fontTable.xml", False))
        if s.theme:
            teile["word/theme/theme1.xml"] = (CT["theme"], THEME.encode())
            rels.append(("rId5", RT + "theme", "theme/theme1.xml", False))
        sep = f'<w:p><w:r><w:separator/></w:r></w:p>'
        cont = f'<w:p><w:r><w:continuationSeparator/></w:r></w:p>'
        for art, liste, rid, nr in (("footnote", s.fussnoten, "rId6", "footnotes"), ("endnote", s.endnoten, "rId7", "endnotes")):
            if liste:
                teile[f"word/{nr}.xml"] = (CT[nr], (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:{nr} {NSALL}><w:{art} w:type="separator" w:id="0">{sep}</w:{art}><w:{art} w:type="continuationSeparator" w:id="1">{cont}</w:{art}>{"".join(liste)}</w:{nr}>').encode())
                rels.append((rid, RT + nr, f"{nr}.xml", False))
        if s.kommentare:
            teile["word/comments.xml"] = (CT["comments"], f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:comments {NSALL}>{"".join(s.kommentare)}</w:comments>'.encode())
            rels.append(("rId8", RT + "comments", "comments.xml", False))
            teile["word/commentsExtended.xml"] = (CT["commentsex"], f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w15:commentsEx {NSALL}>{"".join(s.kommentare_ex)}</w15:commentsEx>'.encode())
            rels.append(("rId9", "http://schemas.microsoft.com/office/2011/relationships/commentsExtended", "commentsExtended.xml", False))
        if s.custom_xml:
            teile["customXml/item1.xml"] = (CT["customxml"], '<?xml version="1.0" encoding="UTF-8"?><daten xmlns="urn:lunivo:test"><feld>Wert</feld><zahl>42</zahl></daten>'.encode())
            rels.append(("rId90", RT + "customXml", "../customXml/item1.xml", False))
        inhaltstypen = {"rels": "application/vnd.openxmlformats-package.relationships+xml", "xml": "application/xml", "png": "image/png", "jpeg": "image/jpeg", "jpg": "image/jpeg",
                        "gif": "image/gif", "bmp": "image/bmp", "svg": "image/svg+xml"}
        ct = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' + "".join(f'<Default Extension="{k}" ContentType="{v}"/>' for k, v in inhaltstypen.items())
        ct += f'<Override PartName="/word/document.xml" ContentType="{CT["dok"]}"/>'
        for p, (typ, _d) in teile.items():
            if typ:
                ct += f'<Override PartName="/{p}" ContentType="{typ}"/>'
        ct += f'<Override PartName="/docProps/core.xml" ContentType="{CT["core"]}"/><Override PartName="/docProps/app.xml" ContentType="{CT["app"]}"/>'
        if s.eigene:
            ct += f'<Override PartName="/docProps/custom.xml" ContentType="{CT["custom"]}"/>'
        ct += "</Types>"
        k = s.kern
        core = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                f'<dc:title>{e(k["titel"])}</dc:title><dc:subject>{e(k["betreff"])}</dc:subject><dc:creator>{e(k["autor"])}</dc:creator><cp:keywords>{e(k["stichwort"])}</cp:keywords><dc:description>{e(k["beschreibung"])}</dc:description>'
                f'<dcterms:created xsi:type="dcterms:W3CDTF">2026-01-15T09:00:00Z</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">2026-02-20T16:30:00Z</dcterms:modified></cp:coreProperties>')
        app = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Lunivo-Testbestand</Application><AppVersion>1.0</AppVersion>{s.app_extra}</Properties>'
        wurzel_rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                       f'<Relationship Id="rId1" Type="{RT}officeDocument" Target="word/document.xml"/>'
                       '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
                       f'<Relationship Id="rId3" Type="{RT}extended-properties" Target="docProps/app.xml"/>')
        if s.eigene:
            wurzel_rels += f'<Relationship Id="rId4" Type="{RT}custom-properties" Target="docProps/custom.xml"/>'
            eig = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/custom-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            for n, (name, typ, wert) in enumerate(s.eigene, 2):
                eig += f'<property fmtid="{{D5CDD505-2E9C-101B-9397-08002B2CF9AE}}" pid="{n}" name="{e(name)}"><vt:{typ}>{e(wert)}</vt:{typ}></property>'
            teile["docProps/custom.xml"] = ("", (eig + "</Properties>").encode())
        wurzel_rels += "</Relationships>"
        doc_rels = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + "".join(
            f'<Relationship Id="{i}" Type="{t}" Target="{e(z)}"{" TargetMode=" + chr(34) + "External" + chr(34) if ex else ""}/>' for i, t, z, ex in rels) + "</Relationships>"
        os.makedirs(os.path.dirname(pfad), exist_ok=True)
        with zipfile.ZipFile(pfad, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", ct)
            z.writestr("_rels/.rels", wurzel_rels)
            z.writestr("word/document.xml", dok)
            z.writestr("word/_rels/document.xml.rels", doc_rels)
            z.writestr("docProps/core.xml", core)
            z.writestr("docProps/app.xml", app)
            for p, (_t, d) in teile.items():
                z.writestr(p, d)


THEME = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Testdesign"><a:themeElements>
<a:clrScheme name="Test"><a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1><a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="44546A"/></a:dk2><a:lt2><a:srgbClr val="E7E6E6"/></a:lt2><a:accent1><a:srgbClr val="4472C4"/></a:accent1><a:accent2><a:srgbClr val="ED7D31"/></a:accent2><a:accent3><a:srgbClr val="A5A5A5"/></a:accent3><a:accent4><a:srgbClr val="FFC000"/></a:accent4><a:accent5><a:srgbClr val="5B9BD5"/></a:accent5><a:accent6><a:srgbClr val="70AD47"/></a:accent6><a:hlink><a:srgbClr val="0563C1"/></a:hlink><a:folHlink><a:srgbClr val="954F72"/></a:folHlink></a:clrScheme>
<a:fontScheme name="Test"><a:majorFont><a:latin typeface="Cambria"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Calibri"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
<a:fmtScheme name="Test"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
<a:lnStyleLst><a:ln w="6350"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="12700"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>"""


def text_absaetze(d: Dok, n: int, ppr="", rpr="") -> None:
    for _ in range(n):
        d.body.append(para(satz(d.rng, d.rng.randint(1, 3)), ppr, rpr))


# --------------------------------------------------------------------------------------------------------------------- Zeichenformat
RPR = {
    "fett": '<w:b/>', "fett_aus": '<w:b w:val="0"/>', "kursiv": '<w:i/>', "fett_komplex": '<w:bCs/>', "kursiv_komplex": '<w:iCs/>',
    "kapitaelchen": '<w:smallCaps/>', "gross": '<w:caps/>', "durch": '<w:strike/>', "doppeltdurch": '<w:dstrike/>', "kontur": '<w:outline/>', "schatten": '<w:shadow/>',
    "praegung": '<w:emboss/>', "gravur": '<w:imprint/>', "versteckt": '<w:vanish/>', "web_versteckt": '<w:webHidden/>', "ohne_pruefung": '<w:noProof/>',
    "farbe_rot": '<w:color w:val="FF0000"/>', "farbe_theme": '<w:color w:val="4472C4" w:themeColor="accent1" w:themeShade="BF"/>', "farbe_auto": '<w:color w:val="auto"/>',
    "abstand_weit": '<w:spacing w:val="40"/>', "abstand_eng": '<w:spacing w:val="-20"/>', "breite_150": '<w:w w:val="150"/>', "breite_60": '<w:w w:val="60"/>',
    "unterschneidung": '<w:kern w:val="28"/>', "hoch_pos": '<w:position w:val="8"/>', "tief_pos": '<w:position w:val="-8"/>',
    "gr_8": '<w:sz w:val="16"/><w:szCs w:val="16"/>', "gr_12": '<w:sz w:val="24"/><w:szCs w:val="24"/>', "gr_36": '<w:sz w:val="72"/><w:szCs w:val="72"/>', "gr_halb": '<w:sz w:val="21"/>', "gr_gross": '<w:sz w:val="400"/>',
    "markierung_gelb": '<w:highlight w:val="yellow"/>', "markierung_gruen": '<w:highlight w:val="green"/>', "markierung_dunkel": '<w:highlight w:val="darkMagenta"/>', "markierung_aus": '<w:highlight w:val="none"/>',
    "u_einfach": '<w:u w:val="single"/>', "u_doppelt": '<w:u w:val="double"/>', "u_worte": '<w:u w:val="words"/>', "u_dick": '<w:u w:val="thick" w:color="FF0000"/>', "u_punkt": '<w:u w:val="dotted"/>',
    "u_strich": '<w:u w:val="dash"/>', "u_wellen": '<w:u w:val="wave"/>', "u_wellen_doppelt": '<w:u w:val="wavyDouble"/>', "u_strichpunkt": '<w:u w:val="dotDash"/>', "u_lang": '<w:u w:val="dashLong"/>',
    "u_aus": '<w:u w:val="none"/>', "effekt_blink": '<w:effect w:val="blinkBackground"/>', "effekt_licht": '<w:effect w:val="lights"/>',
    "rahmen": '<w:bdr w:val="single" w:sz="4" w:space="0" w:color="000000"/>', "schattierung": '<w:shd w:val="clear" w:color="auto" w:fill="FFFF99"/>', "schattierung_muster": '<w:shd w:val="pct25" w:color="0000FF" w:fill="FFFFFF"/>',
    "hochgestellt": '<w:vertAlign w:val="superscript"/>', "tiefgestellt": '<w:vertAlign w:val="subscript"/>', "grundlinie": '<w:vertAlign w:val="baseline"/>',
    "rtl": '<w:rtl/>', "komplex": '<w:cs/>', "betonung_punkt": '<w:em w:val="dot"/>', "betonung_kreis": '<w:em w:val="circle"/>', "betonung_komma": '<w:em w:val="comma"/>', "betonung_unter": '<w:em w:val="underDot"/>',
    "sprache_en": '<w:lang w:val="en-GB"/>', "sprache_fr": '<w:lang w:val="fr-FR"/>', "sprache_ar": '<w:lang w:bidi="ar-SA"/>', "sprache_ja": '<w:lang w:eastAsia="ja-JP"/>', "sprache_aus": '<w:lang w:val="zxx"/>',
    "schrift_arial": '<w:rFonts w:ascii="Arial" w:hAnsi="Arial" w:cs="Arial"/>', "schrift_mono": '<w:rFonts w:ascii="Courier New" w:hAnsi="Courier New"/>', "schrift_theme": '<w:rFonts w:asciiTheme="majorHAnsi" w:hAnsiTheme="majorHAnsi"/>',
    "schrift_asien": '<w:rFonts w:eastAsia="MS Mincho" w:hint="eastAsia"/>', "schrift_fehlt": '<w:rFonts w:ascii="Nichtvorhandene Schrift XYZ" w:hAnsi="Nichtvorhandene Schrift XYZ"/>',
    "passend": '<w:fitText w:val="1440" w:id="1"/>', "layout_asien": '<w:eastAsianLayout w:id="1" w:vert="1"/>',
    "w14_kontur": '<w14:textOutline w14:w="9525" w14:cap="flat" w14:cmpd="sng" w14:algn="ctr"><w14:solidFill><w14:srgbClr w14:val="FF0000"/></w14:solidFill><w14:prstDash w14:val="solid"/><w14:round/></w14:textOutline>',
    "w14_fuellung": '<w14:textFill><w14:gradFill><w14:gsLst><w14:gs w14:pos="0"><w14:srgbClr w14:val="FF0000"/></w14:gs><w14:gs w14:pos="100000"><w14:srgbClr w14:val="0000FF"/></w14:gs></w14:gsLst><w14:lin w14:ang="0" w14:scaled="0"/></w14:gradFill></w14:textFill>',
    "w14_schatten": '<w14:shadow w14:blurRad="50800" w14:dist="38100" w14:dir="2700000" w14:sx="100000" w14:sy="100000" w14:kx="0" w14:ky="0" w14:algn="tl"><w14:srgbClr w14:val="000000"><w14:alpha w14:val="40000"/></w14:srgbClr></w14:shadow>',
    "w14_leuchten": '<w14:glow w14:rad="101600"><w14:srgbClr w14:val="FFC000"><w14:alpha w14:val="40000"/></w14:srgbClr></w14:glow>',
    "w14_spiegelung": '<w14:reflection w14:blurRad="6350" w14:stA="50000" w14:stPos="0" w14:endA="300" w14:endPos="50000" w14:dist="0" w14:dir="5400000" w14:fadeDir="5400000" w14:sx="100000" w14:sy="-100000" w14:kx="0" w14:ky="0" w14:algn="bl"/>',
    "w14_ligaturen": '<w14:ligatures w14:val="standardContextual"/>', "w14_ziffern": '<w14:numForm w14:val="oldStyle"/>', "w14_stilsatz": '<w14:stylisticSets><w14:styleSet w14:id="1"/></w14:stylisticSets>',
}
RPR_NAMEN = list(RPR)


def k_zeichen(i, rng):
    d = Dok(rng)
    haupt = pick(RPR_NAMEN, i)
    d.kern["beschreibung"] = f"Zeichenformat: {haupt}"
    d.body.append(para(f"Zeichenformat {haupt}", '<w:pStyle w:val="Heading1"/>'))
    for k in range(8):
        zusatz = rng.sample(RPR_NAMEN, rng.randint(0, 2)) if k > 1 else []
        namen = [haupt] + zusatz
        rpr = ordne([RPR[n] for n in namen], RPR_ORDER)
        d.body.append(para(inhalt=run("Vorher ") + run(f"Hauptmerkmal {haupt} ({', '.join(zusatz) or 'allein'}) ", rpr) + run(satz(rng)) + run(" Nachher.", rpr if k % 3 == 0 else "")))
    d.body.append(para(inhalt=run("Gemischt innerhalb eines Wortes: ") + run("Ein", RPR["fett"]) + run("zel", RPR["kursiv"]) + run("wort", RPR["u_einfach"]) + run("teile", RPR["farbe_rot"])))
    return d


# --------------------------------------------------------------------------------------------------------------------- Absatzformat
PPR = {
    "ausr_links": '<w:jc w:val="left"/>', "ausr_mitte": '<w:jc w:val="center"/>', "ausr_rechts": '<w:jc w:val="right"/>', "ausr_block": '<w:jc w:val="both"/>', "ausr_verteilt": '<w:jc w:val="distribute"/>',
    "ausr_start": '<w:jc w:val="start"/>', "ausr_ende": '<w:jc w:val="end"/>', "ausr_thai": '<w:jc w:val="thaiDistribute"/>', "ausr_hoch": '<w:jc w:val="highKashida"/>',
    "einzug_links": '<w:ind w:left="1134"/>', "einzug_rechts": '<w:ind w:right="1134"/>', "einzug_erste": '<w:ind w:firstLine="567"/>', "einzug_haengend": '<w:ind w:left="1134" w:hanging="567"/>',
    "einzug_beide": '<w:ind w:left="720" w:right="720" w:firstLine="360"/>', "einzug_negativ": '<w:ind w:left="-567"/>', "einzug_zeichen": '<w:ind w:leftChars="100" w:firstLineChars="200"/>', "einzug_start_ende": '<w:ind w:start="720" w:end="360"/>',
    "spiegel": '<w:mirrorIndents/>', "abstand_vor": '<w:spacing w:before="480"/>', "abstand_nach": '<w:spacing w:after="480"/>', "abstand_beide": '<w:spacing w:before="240" w:after="240"/>',
    "abstand_auto": '<w:spacing w:beforeAutospacing="1" w:afterAutospacing="1"/>', "abstand_lines": '<w:spacing w:beforeLines="100" w:afterLines="100"/>',
    "zeile_einfach": '<w:spacing w:line="240" w:lineRule="auto"/>', "zeile_15": '<w:spacing w:line="360" w:lineRule="auto"/>', "zeile_doppelt": '<w:spacing w:line="480" w:lineRule="auto"/>', "zeile_genau": '<w:spacing w:line="300" w:lineRule="exact"/>',
    "zeile_mind": '<w:spacing w:line="500" w:lineRule="atLeast"/>', "zeile_klein": '<w:spacing w:line="120" w:lineRule="exact"/>', "zeile_0_7": '<w:spacing w:line="168" w:lineRule="auto"/>',
    "kontextabstand": '<w:contextualSpacing/>', "mit_naechstem": '<w:keepNext/>', "zusammen": '<w:keepLines/>', "seite_vor": '<w:pageBreakBefore/>', "witwen_aus": '<w:widowControl w:val="0"/>', "witwen_ein": '<w:widowControl/>',
    "tabs_links": '<w:tabs><w:tab w:val="left" w:pos="1440"/><w:tab w:val="left" w:pos="2880"/></w:tabs>', "tabs_mitte_rechts": '<w:tabs><w:tab w:val="center" w:pos="4513"/><w:tab w:val="right" w:pos="9026"/></w:tabs>',
    "tabs_dezimal": '<w:tabs><w:tab w:val="decimal" w:pos="3000"/></w:tabs>', "tabs_fuell_punkt": '<w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9000"/></w:tabs>', "tabs_fuell_strich": '<w:tabs><w:tab w:val="left" w:leader="hyphen" w:pos="4000"/></w:tabs>',
    "tabs_fuell_linie": '<w:tabs><w:tab w:val="right" w:leader="underscore" w:pos="9000"/></w:tabs>', "tabs_fuell_mittel": '<w:tabs><w:tab w:val="left" w:leader="middleDot" w:pos="3000"/></w:tabs>', "tabs_bar": '<w:tabs><w:tab w:val="bar" w:pos="2000"/></w:tabs>',
    "tabs_loeschen": '<w:tabs><w:tab w:val="clear" w:pos="720"/></w:tabs>', "tabs_num": '<w:tabs><w:tab w:val="num" w:pos="720"/></w:tabs>',
    "rahmen_kasten": '<w:pBdr><w:top w:val="single" w:sz="8" w:space="4" w:color="000000"/><w:left w:val="single" w:sz="8" w:space="4" w:color="000000"/><w:bottom w:val="single" w:sz="8" w:space="4" w:color="000000"/><w:right w:val="single" w:sz="8" w:space="4" w:color="000000"/></w:pBdr>',
    "rahmen_unten": '<w:pBdr><w:bottom w:val="single" w:sz="12" w:space="1" w:color="C00000"/></w:pBdr>', "rahmen_oben_doppelt": '<w:pBdr><w:top w:val="double" w:sz="6" w:space="1" w:color="0000FF"/></w:pBdr>',
    "rahmen_zwischen": '<w:pBdr><w:between w:val="dashed" w:sz="6" w:space="1" w:color="808080"/></w:pBdr>', "rahmen_balken": '<w:pBdr><w:bar w:val="single" w:sz="18" w:space="4" w:color="FFC000"/></w:pBdr>',
    "rahmen_schatten": '<w:pBdr><w:top w:val="single" w:sz="4" w:space="1" w:color="auto" w:shadow="1"/><w:left w:val="single" w:sz="4" w:space="4" w:color="auto" w:shadow="1"/><w:bottom w:val="single" w:sz="4" w:space="1" w:color="auto" w:shadow="1"/><w:right w:val="single" w:sz="4" w:space="4" w:color="auto" w:shadow="1"/></w:pBdr>',
    "rahmen_welle": '<w:pBdr><w:bottom w:val="wave" w:sz="6" w:space="1" w:color="008000"/></w:pBdr>', "rahmen_kunst": '<w:pBdr><w:top w:val="apples" w:sz="12" w:space="1" w:color="auto"/></w:pBdr>',
    "hinten_gelb": '<w:shd w:val="clear" w:color="auto" w:fill="FFFF00"/>', "hinten_muster": '<w:shd w:val="pct50" w:color="FF0000" w:fill="FFFFFF"/>', "hinten_diag": '<w:shd w:val="diagStripe" w:color="000000" w:fill="DDDDDD"/>', "hinten_theme": '<w:shd w:val="clear" w:color="auto" w:fill="4472C4" w:themeFill="accent1"/>',
    "gliederung_1": '<w:outlineLvl w:val="0"/>', "gliederung_5": '<w:outlineLvl w:val="4"/>', "gliederung_9": '<w:outlineLvl w:val="9"/>', "rtl": '<w:bidi/>', "textrichtung_tb": '<w:textDirection w:val="tbRl"/>', "textrichtung_lr": '<w:textDirection w:val="lrTb"/>',
    "ausrichtung_text": '<w:textAlignment w:val="center"/>', "ohne_zeilennummer": '<w:suppressLineNumbers/>', "ohne_trennung": '<w:suppressAutoHyphens/>', "kein_umbruch_rand": '<w:wordWrap w:val="0"/>', "kinsoku_aus": '<w:kinsoku w:val="0"/>',
    "raster_aus": '<w:snapToGrid w:val="0"/>', "autospace_aus": '<w:autoSpaceDE w:val="0"/><w:autoSpaceDN w:val="0"/>', "hangend": '<w:overflowPunct w:val="0"/>',
    "initial": '<w:framePr w:dropCap="drop" w:lines="3" w:wrap="around" w:vAnchor="text" w:hAnchor="text"/>', "rahmen_abs": '<w:framePr w:w="2400" w:h="1200" w:hRule="exact" w:wrap="around" w:vAnchor="page" w:hAnchor="margin" w:x="1000" w:y="3000"/>',
    "rahmen_rechts": '<w:framePr w:w="3000" w:hSpace="180" w:wrap="around" w:vAnchor="text" w:hAnchor="margin" w:xAlign="right" w:y="1"/>',
}
PPR_NAMEN = list(PPR)


def k_absatz(i, rng):
    d = Dok(rng)
    haupt = pick(PPR_NAMEN, i)
    d.kern["beschreibung"] = f"Absatzformat: {haupt}"
    d.body.append(para(f"Absatzformat {haupt}", '<w:pStyle w:val="Heading1"/>'))
    for k in range(7):
        namen = [haupt] + (rng.sample(PPR_NAMEN, rng.randint(0, 2)) if k > 2 else [])
        ppr = ordne([PPR[n] for n in namen], PPR_ORDER)
        text = f"{haupt}\t{satz(rng, 2 + k % 3)}" if "tabs" in haupt else satz(rng, 2 + k % 3)
        d.body.append(para(text, ppr))
    d.body.append(para("Absatz ohne Besonderheit danach."))
    return d


# --------------------------------------------------------------------------------------------------------------------- Formatvorlagen
def k_vorlagen(i, rng):
    d = Dok(rng)
    art = i % 7
    d.defaults = {"schrift": pick(SCHRIFTEN, i), "groesse": rng.choice([16, 18, 20, 22, 24, 28]), "nach": rng.choice([0, 80, 160, 240]), "zeile": rng.choice([240, 259, 276, 360])}
    d.kern["beschreibung"] = f"Vorlagenart {art}"
    if art == 0:     # Vererbungskette
        tiefe = 2 + i % 6
        for n in range(1, tiefe + 1):
            basis = "Normal" if n == 1 else f"Kette{n - 1}"
            d.stile.append(f'<w:style w:type="paragraph" w:customStyle="1" w:styleId="Kette{n}"><w:name w:val="Kette {n}"/><w:basedOn w:val="{basis}"/><w:next w:val="Kette{min(n + 1, tiefe)}"/><w:qFormat/>'
                           f'<w:pPr><w:spacing w:before="{n * 40}"/><w:ind w:left="{n * 200}"/></w:pPr><w:rPr><w:color w:val="{pick(FARBEN, n + i)}"/><w:sz w:val="{18 + n * 2}"/></w:rPr></w:style>')
            d.body.append(para(f"Kettenstufe {n}: {satz(rng)}", f'<w:pStyle w:val="Kette{n}"/>'))
    elif art == 1:   # verknüpfte Zeichenvorlage
        d.stile.append('<w:style w:type="paragraph" w:customStyle="1" w:styleId="Betont"><w:name w:val="Betont Absatz"/><w:basedOn w:val="Normal"/><w:link w:val="BetontZchn"/><w:qFormat/><w:pPr><w:jc w:val="center"/></w:pPr><w:rPr><w:b/><w:color w:val="C00000"/></w:rPr></w:style>'
                       '<w:style w:type="character" w:customStyle="1" w:styleId="BetontZchn"><w:name w:val="Betont Zchn"/><w:basedOn w:val="DefaultParagraphFont"/><w:link w:val="Betont"/><w:rPr><w:b/><w:color w:val="C00000"/></w:rPr></w:style>'
                       '<w:style w:type="character" w:customStyle="1" w:styleId="Marker"><w:name w:val="Marker"/><w:basedOn w:val="DefaultParagraphFont"/><w:uiPriority w:val="1"/><w:qFormat/><w:rPr><w:shd w:val="clear" w:color="auto" w:fill="FFFF00"/><w:i/></w:rPr></w:style>')
        d.body.append(para(satz(rng), '<w:pStyle w:val="Betont"/>'))
        d.body.append(para(inhalt=run("Normal, ") + run("hervorgehoben", '<w:rStyle w:val="Marker"/>') + run(", wieder normal. ") + run("Verknüpft", '<w:rStyle w:val="BetontZchn"/>')))
    elif art == 2:   # Überschriften und Titel abgewandelt
        for n in range(1, 10):
            d.stile.append(f'<w:style w:type="paragraph" w:styleId="Heading{n}" w:customStyle="0"><w:name w:val="heading {n}"/><w:basedOn w:val="Normal"/><w:next w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:spacing w:before="{300 - n * 20}" w:after="60"/><w:ind w:left="{(n - 1) * 100}"/><w:outlineLvl w:val="{n - 1}"/></w:pPr><w:rPr><w:rFonts w:ascii="{pick(SCHRIFTEN, n + i)}" w:hAnsi="{pick(SCHRIFTEN, n + i)}"/><w:b/><w:sz w:val="{44 - n * 3}"/><w:color w:val="{pick(FARBEN, n)}"/></w:rPr></w:style>')
            d.body.append(heading(f"Überschrift Ebene {n}", n))
            d.body.append(para(satz(rng)))
    elif art == 3:   # Tabellenvorlage mit bedingter Formatierung
        d.stile.append('<w:style w:type="table" w:customStyle="1" w:styleId="Bunt"><w:name w:val="Bunt"/><w:basedOn w:val="TableNormal"/><w:uiPriority w:val="40"/><w:tblPr><w:tblStyleRowBandSize w:val="1"/><w:tblBorders><w:top w:val="single" w:sz="8" w:space="0" w:color="1F4E79"/><w:bottom w:val="single" w:sz="8" w:space="0" w:color="1F4E79"/><w:insideH w:val="single" w:sz="4" w:space="0" w:color="BDD7EE"/></w:tblBorders></w:tblPr>'
                       '<w:tblStylePr w:type="firstRow"><w:rPr><w:b/><w:color w:val="FFFFFF"/></w:rPr><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="1F4E79"/></w:tcPr></w:tblStylePr>'
                       '<w:tblStylePr w:type="lastRow"><w:rPr><w:b/></w:rPr><w:tcPr><w:tcBorders><w:top w:val="double" w:sz="6" w:space="0" w:color="auto"/></w:tcBorders></w:tcPr></w:tblStylePr>'
                       '<w:tblStylePr w:type="firstCol"><w:rPr><w:b/></w:rPr></w:tblStylePr><w:tblStylePr w:type="band1Horz"><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="DEEAF6"/></w:tcPr></w:tblStylePr>'
                       '<w:tblStylePr w:type="band2Horz"><w:tcPr><w:shd w:val="clear" w:color="auto" w:fill="FFFFFF"/></w:tcPr></w:tblStylePr></w:style>')
        look = pick(['<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>', '<w:tblLook w:val="0660" w:firstRow="1" w:lastRow="1" w:firstColumn="0" w:lastColumn="0" w:noHBand="1" w:noVBand="1"/>'], i)
        d.body.append(einfache_tabelle(rng, 5, 4, tblpr='<w:tblStyle w:val="Bunt"/>') .replace("</w:tblPr>", look + "</w:tblPr>", 1))
    elif art == 4:   # Nummerierung in der Vorlage, Verstecktes, Sperren
        d.num_abs.append('<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="multilevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:pStyle w:val="Gliederung1"/><w:lvlText w:val="%1."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="432" w:hanging="432"/></w:pPr></w:lvl><w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:pStyle w:val="Gliederung2"/><w:lvlText w:val="%1.%2"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="576" w:hanging="576"/></w:pPr></w:lvl></w:abstractNum>')
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        d.stile.append('<w:style w:type="paragraph" w:customStyle="1" w:styleId="Gliederung1"><w:name w:val="Gliederung 1"/><w:basedOn w:val="Normal"/><w:qFormat/><w:pPr><w:keepNext/><w:numPr><w:numId w:val="1"/></w:numPr></w:pPr><w:rPr><w:b/></w:rPr></w:style>'
                       '<w:style w:type="paragraph" w:customStyle="1" w:styleId="Gliederung2"><w:name w:val="Gliederung 2"/><w:basedOn w:val="Normal"/><w:pPr><w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr></w:pPr></w:style>'
                       '<w:style w:type="paragraph" w:customStyle="1" w:styleId="Intern"><w:name w:val="Intern"/><w:basedOn w:val="Normal"/><w:semiHidden/><w:hidden/><w:locked/><w:uiPriority w:val="99"/></w:style>')
        for n in range(4):
            d.body.append(para(f"Hauptpunkt {n + 1}", '<w:pStyle w:val="Gliederung1"/>'))
            d.body.append(para(satz(rng), '<w:pStyle w:val="Gliederung2"/>'))
        d.body.append(para("Absatz mit versteckter Vorlage", '<w:pStyle w:val="Intern"/>'))
    elif art == 5:   # Latente Stile, Standardvorlagen ersetzt
        d.stile.append('<w:latentStyles w:defLockedState="0" w:defUIPriority="99" w:defSemiHidden="0" w:defUnhideWhenUsed="0" w:defQFormat="0" w:count="376"><w:lsdException w:name="Normal" w:uiPriority="0" w:qFormat="1"/><w:lsdException w:name="heading 1" w:uiPriority="9" w:qFormat="1"/></w:latentStyles>')
        d.stile.append('<w:style w:type="paragraph" w:styleId="Normal2" w:customStyle="1"><w:name w:val="Normal 2"/><w:basedOn w:val="Normal"/><w:autoRedefine/><w:pPr><w:spacing w:after="0"/></w:pPr></w:style>')
        d.body.append(para(satz(rng, 3), '<w:pStyle w:val="Normal2"/>'))
        d.body.append(para("Titel", '<w:pStyle w:val="Title"/>'))
        d.body.append(para("Untertitel", '<w:pStyle w:val="Subtitle"/>'))
        d.body.append(para("Zitat im Zitat-Stil", '<w:pStyle w:val="Quote"/>'))
    else:            # unbekannte oder fehlende Vorlagen
        d.body.append(para("Verweis auf eine Vorlage, die nicht definiert ist", '<w:pStyle w:val="GibtEsNicht"/>'))
        d.body.append(para(inhalt=run("Zeichenvorlage fehlt", '<w:rStyle w:val="AuchNicht"/>')))
        d.body.append(para(satz(rng), '<w:pStyle w:val="Heading1"/>'))
    d.body.append(para(satz(rng)))
    return d


# --------------------------------------------------------------------------------------------------------------------- Listen
FORMATE = ["decimal", "lowerLetter", "upperLetter", "lowerRoman", "upperRoman", "ordinal", "cardinalText", "ordinalText", "decimalZero", "bullet", "none", "chicago", "decimalEnclosedCircle",
           "decimalEnclosedParen", "decimalEnclosedFullstop", "japaneseCounting", "chineseCounting", "ideographDigital", "koreanDigital", "hebrew1", "arabicAlpha", "thaiNumbers", "hindiNumbers", "russianLower", "russianUpper", "hex", "upperRoman"]
PUNKTE = [("\uf0b7", "Symbol"), ("o", "Courier New"), ("\uf0a7", "Wingdings"), ("\uf0d8", "Wingdings"), ("–", "Calibri"), ("•", "Arial"), ("★", "Segoe UI Symbol"), ("→", "Arial")]


def k_listen(i, rng):
    d = Dok(rng)
    art = i % 10
    d.kern["beschreibung"] = f"Listenart {art}"

    def ebenen(fmt_fun, text_fun, einzug=360, suff="tab", start=1):
        out = ""
        for n in range(9):
            f = fmt_fun(n)
            t = text_fun(n)
            font = f'<w:rPr><w:rFonts w:ascii="{t[1]}" w:hAnsi="{t[1]}" w:hint="default"/></w:rPr>' if isinstance(t, tuple) else ""
            txt = t[0] if isinstance(t, tuple) else t
            out += (f'<w:lvl w:ilvl="{n}"><w:start w:val="{start}"/><w:numFmt w:val="{f}"/><w:suff w:val="{suff}"/><w:lvlText w:val="{e(txt)}"/><w:lvlJc w:val="left"/>'
                    f'<w:pPr><w:ind w:left="{720 + n * einzug}" w:hanging="{360 if n < 8 else 400}"/></w:pPr>{font}</w:lvl>')
        return out

    def abs_(nid, mlt, lvls):
        d.num_abs.append(f'<w:abstractNum w:abstractNumId="{nid}"><w:multiLevelType w:val="{mlt}"/>{lvls}</w:abstractNum>')

    def liste(num, n_punkte=5, tiefe=1, text="Punkt"):
        for k in range(n_punkte):
            ebene = (k % tiefe) if tiefe > 1 else 0
            d.body.append(para(f"{text} {k + 1}: {rng.choice(SAETZE).split('.')[0]}", f'<w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="{ebene}"/><w:numId w:val="{num}"/></w:numPr>'))

    if art == 0:     # Aufzählung mit verschiedenen Zeichen
        sym = PUNKTE[i % len(PUNKTE)]
        abs_(0, "hybridMultilevel", ebenen(lambda n: "bullet", lambda n: PUNKTE[(i + n) % len(PUNKTE)]))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        liste(1, 6, 3)
    elif art == 1:   # nummeriert, Formate
        fmt = pick(FORMATE[:9] + FORMATE[10:], i // 10 + i)
        abs_(0, "hybridMultilevel", ebenen(lambda n: fmt, lambda n: f"%{n + 1}."))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        liste(1, 8)
        d.kern["beschreibung"] += f" {fmt}"
    elif art == 2:   # mehrstufig 1. 1.1 1.1.1
        abs_(0, "multilevel", ebenen(lambda n: "decimal", lambda n: ".".join(f"%{k + 1}" for k in range(n + 1)) + ("." if n == 0 else ""), 360))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        for k, n in enumerate([0, 1, 1, 2, 2, 2, 1, 0, 1, 2, 3, 4]):
            d.body.append(para(f"Gliederungspunkt {k + 1}", f'<w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="{n}"/><w:numId w:val="1"/></w:numPr>'))
    elif art == 3:   # Gesetzestext isLgl, Römisch, Buchstaben gemischt
        lv = ""
        for n, (f, t) in enumerate([("upperRoman", "%1."), ("upperLetter", "%2."), ("decimal", "%3."), ("lowerLetter", "%4)"), ("lowerRoman", "(%5)"), ("decimal", "%1.%2.%3.%4.%5.%6"), ("decimal", "%7"), ("decimal", "%8"), ("decimal", "%9")]):
            lv += f'<w:lvl w:ilvl="{n}"><w:start w:val="1"/><w:numFmt w:val="{f}"/>{"<w:isLgl/>" if n == 5 else ""}<w:lvlText w:val="{t}"/><w:lvlJc w:val="{"right" if n == 0 else "left"}"/><w:pPr><w:ind w:left="{720 + n * 360}" w:hanging="360"/></w:pPr></w:lvl>'
        abs_(0, "multilevel", lv)
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        for k, n in enumerate([0, 1, 2, 3, 4, 5, 4, 3, 2, 1, 0]):
            d.body.append(para(f"Abschnitt {k + 1}", f'<w:numPr><w:ilvl w:val="{n}"/><w:numId w:val="1"/></w:numPr>'))
    elif art == 4:   # Neustart und Startwert
        abs_(0, "hybridMultilevel", ebenen(lambda n: "decimal", lambda n: f"%{n + 1}."))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        d.num.append(f'<w:num w:numId="2"><w:abstractNumId w:val="0"/><w:lvlOverride w:ilvl="0"><w:startOverride w:val="{rng.randint(2, 20)}"/></w:lvlOverride></w:num>')
        d.num.append('<w:num w:numId="3"><w:abstractNumId w:val="0"/></w:num>')
        liste(1, 3, text="Liste A")
        d.body.append(para("Zwischentext."))
        liste(2, 3, text="Liste B (Startwert)")
        liste(1, 2, text="Liste A fortgesetzt")
        liste(3, 3, text="Liste C (eigene Zählung)")
    elif art == 5:   # Trennzeichen, Ausrichtung, Einzüge
        suff = pick(["tab", "space", "nothing"], i)
        abs_(0, "singleLevel", ebenen(lambda n: pick(["decimal", "bullet"], i), lambda n: "§ %1" if i % 2 == 0 else ("•", "Arial"), 0, suff))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        liste(1, 5)
    elif art == 6:   # Zeichenformat der Ziffer
        lv = ""
        for n in range(9):
            lv += f'<w:lvl w:ilvl="{n}"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="%{n + 1}."/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="{720 + n * 360}" w:hanging="360"/></w:pPr><w:rPr><w:b/><w:color w:val="{pick(FARBEN, n)}"/><w:sz w:val="{20 + n * 2}"/><w:u w:val="single"/></w:rPr></w:lvl>'
        abs_(0, "multilevel", lv)
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        liste(1, 6, 4)
    elif art == 7:   # Liste in Tabellenzelle und mehrere Absätze je Punkt
        abs_(0, "hybridMultilevel", ebenen(lambda n: "bullet", lambda n: PUNKTE[n % len(PUNKTE)]))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        inh = "".join(para(f"Zellpunkt {k}", '<w:pStyle w:val="ListParagraph"/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>') for k in range(4))
        d.body.append(tabelle([[zelle(inh, breite=4500), zelle(para("Daneben"), breite=4500)]], [4500, 4500], '<w:tblStyle w:val="TableGrid"/><w:tblW w:w="9000" w:type="dxa"/>'))
        d.body.append(para("Punkt mit Fortsetzung", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'))
        d.body.append(para("Fortsetzungsabsatz ohne Nummer", '<w:ind w:left="720"/>'))
    elif art == 8:   # numId 0 (Nummer entfernt), fehlende Definition, mehrere Listen verschränkt
        abs_(0, "hybridMultilevel", ebenen(lambda n: "decimal", lambda n: f"%{n + 1}."))
        abs_(1, "hybridMultilevel", ebenen(lambda n: "upperLetter", lambda n: f"%{n + 1})"))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num><w:num w:numId="2"><w:abstractNumId w:val="1"/></w:num>')
        for k in range(8):
            d.body.append(para(f"Verschränkt {k}", f'<w:numPr><w:ilvl w:val="0"/><w:numId w:val="{1 + k % 2}"/></w:numPr>'))
        d.body.append(para("Nummer entfernt (numId 0)", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="0"/></w:numPr>'))
        d.body.append(para("Verweis auf nicht vorhandene Liste 99", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="99"/></w:numPr>'))
    else:            # Bildpunkt-Aufzählung, Zeilenabstände in Listen, lange Listen
        abs_(0, "hybridMultilevel", ebenen(lambda n: "decimal", lambda n: f"%{n + 1}."))
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        liste(1, 60)
    return d


# --------------------------------------------------------------------------------------------------------------------- Tabellen
RAHMEN_ARTEN = ["single", "double", "dotted", "dashed", "dotDash", "dotDotDash", "triple", "thinThickSmallGap", "thickThinSmallGap", "thinThickThinSmallGap", "thinThickMediumGap", "wave", "doubleWave", "dashSmallGap", "threeDEmboss", "threeDEngrave", "outset", "inset", "nil", "none"]


def k_tabelle(i, rng):
    d = Dok(rng)
    art = i % 27
    d.kern["beschreibung"] = f"Tabellenart {art}"
    zl, sp = rng.randint(2, 6), rng.randint(2, 5)
    b = 9000 // sp
    raster = '<w:tblStyle w:val="TableGrid"/>'
    d.body.append(para(f"Tabelle Art {art}", '<w:pStyle w:val="Heading1"/>'))
    if art == 0:
        d.body.append(einfache_tabelle(rng, zl, sp))
    elif art == 1:   # gridSpan
        zeilen = [[zelle(para("Verbunden über alle"), f'<w:gridSpan w:val="{sp}"/>', 9000)]] + [[zelle(para(f"Z{r}S{c}"), breite=b) for c in range(sp)] for r in range(zl)]
        zeilen.append([zelle(para("Links"), f'<w:gridSpan w:val="2"/>', b * 2)] + [zelle(para(f"x{c}"), breite=b) for c in range(sp - 2)])
        d.body.append(tabelle(zeilen, [b] * sp, raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 2:   # vMerge
        zeilen = []
        for r in range(zl + 2):
            zeilen.append([zelle(para("Senkrecht verbunden") if r == 0 else para(), '<w:vMerge w:val="restart"/>' if r == 0 else "<w:vMerge/>", b)] + [zelle(para(f"Z{r}S{c}"), breite=b) for c in range(1, sp)])
        d.body.append(tabelle(zeilen, [b] * sp, raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 3:   # beides, unregelmäßig
        zeilen = [[zelle(para("A"), '<w:gridSpan w:val="2"/><w:vMerge w:val="restart"/>', 3000), zelle(para("B"), breite=1500), zelle(para("C"), '<w:vMerge w:val="restart"/>', 1500)],
                  [zelle(para(), '<w:gridSpan w:val="2"/><w:vMerge/>', 3000), zelle(para("D"), breite=1500), zelle(para(), "<w:vMerge/>", 1500)],
                  [zelle(para("E"), breite=1500), zelle(para("F"), '<w:gridSpan w:val="3"/>', 4500)]]
        d.body.append(tabelle(zeilen, [1500, 1500, 1500, 1500], raster + '<w:tblW w:w="6000" w:type="dxa"/>'))
    elif art == 4:   # Rahmenarten
        for n in range(3):
            rd = pick(RAHMEN_ARTEN, i + n * 3)
            rb = f'<w:tblBorders>' + "".join(f'<w:{s} w:val="{rd}" w:sz="{rng.choice([4, 8, 12, 24])}" w:space="0" w:color="{pick(FARBEN, n + i)}"/>' for s in ("top", "left", "bottom", "right", "insideH", "insideV")) + '</w:tblBorders>'
            d.body.append(para(f"Rahmenart {rd}"))
            d.body.append(einfache_tabelle(rng, 2, 3, tblpr=rb))
    elif art == 5:   # Zellhintergründe und Muster
        zeilen = []
        for r in range(zl):
            zeilen.append([zelle(para(f"{r}/{c}"), f'<w:shd w:val="{pick(["clear", "pct10", "pct50", "diagCross", "horzStripe", "solid"], r + c)}" w:color="{pick(FARBEN, r * 3 + c)}" w:fill="{pick(FARBEN, r + c * 5)}"/>', b) for c in range(sp)])
        d.body.append(tabelle(zeilen, [b] * sp, raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 6:   # Breite in Prozent / auto
        d.body.append(einfache_tabelle(rng, 3, 3, tblpr=raster).replace('<w:tblW w:w="9000" w:type="dxa"/>', f'<w:tblW w:w="{rng.choice([2500, 5000])}" w:type="pct"/>'))
        d.body.append(para())
        d.body.append(einfache_tabelle(rng, 3, 3, tblpr=raster).replace('<w:tblW w:w="9000" w:type="dxa"/>', '<w:tblW w:w="0" w:type="auto"/>'))
    elif art == 7:   # fest, ungleiche Spalten
        br = [rng.choice([1200, 2000, 3000, 800]) for _ in range(sp)]
        zeilen = [[zelle(para(f"{r}-{c}"), breite=br[c]) for c in range(sp)] for r in range(zl)]
        d.body.append(tabelle(zeilen, br, raster + f'<w:tblW w:w="{sum(br)}" w:type="dxa"/><w:tblLayout w:type="fixed"/>'))
    elif art == 8:   # Ausrichtung und Einzug
        d.body.append(einfache_tabelle(rng, 2, 2, 4000, tblpr=raster + f'<w:jc w:val="{pick(["left", "center", "right"], i)}"/>'))
        d.body.append(einfache_tabelle(rng, 2, 2, 4000, tblpr=raster + '<w:tblInd w:w="1134" w:type="dxa"/>'))
    elif art == 9:   # verschachtelt
        innen = einfache_tabelle(rng, 2, 2, 3000)
        d.body.append(tabelle([[zelle(para("Außen") + innen + para(), breite=4500), zelle(para("Daneben"), breite=4500)]], [4500, 4500], raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 10:  # lange Tabelle, Kopfzeile wiederholt
        d.body.append(einfache_tabelle(rng, 60, 3, kopf=True, tblpr=raster))
    elif art == 11:  # Höhen, nicht trennen
        zeilen = [[zelle(para(f"Zeile {r}"), breite=4500), zelle(para(satz(rng)), breite=4500)] for r in range(5)]
        d.body.append(tabelle(zeilen, [4500, 4500], raster + '<w:tblW w:w="9000" w:type="dxa"/>', {0: '<w:cantSplit/><w:trHeight w:val="800" w:hRule="exact"/>', 1: '<w:trHeight w:val="1000" w:hRule="atLeast"/>', 2: '<w:cantSplit/>', 3: '<w:trHeight w:val="300"/>', 4: '<w:jc w:val="center"/>'}))
    elif art == 12:  # vertikale Ausrichtung, Textrichtung
        zeilen = [[zelle(para(f"{va} {td}"), f'<w:textDirection w:val="{td}"/><w:vAlign w:val="{va}"/>', 2250) for td in ("lrTb", "tbRl", "btLr", "lrTbV")] for va in ("top", "center", "bottom")]
        d.body.append(tabelle(zeilen, [2250] * 4, raster + '<w:tblW w:w="9000" w:type="dxa"/>', {0: '<w:trHeight w:val="1500" w:hRule="atLeast"/>', 1: '<w:trHeight w:val="1500" w:hRule="atLeast"/>', 2: '<w:trHeight w:val="1500" w:hRule="atLeast"/>'}))
    elif art == 13:  # Zellränder
        zeilen = [[zelle(para("Rand"), '<w:tcMar><w:top w:w="200" w:type="dxa"/><w:left w:w="400" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/><w:right w:w="50" w:type="dxa"/></w:tcMar>', 4500), zelle(para("normal"), breite=4500)]]
        d.body.append(tabelle(zeilen, [4500, 4500], raster + '<w:tblW w:w="9000" w:type="dxa"/><w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="200" w:type="dxa"/><w:bottom w:w="60" w:type="dxa"/><w:right w:w="200" w:type="dxa"/></w:tblCellMar>'))
    elif art == 14:  # Zellabstand
        d.body.append(einfache_tabelle(rng, 3, 3, tblpr=raster + f'<w:tblCellSpacing w:w="{rng.choice([20, 60, 120])}" w:type="dxa"/>'))
    elif art == 15:  # umflossene Tabelle
        d.body.append(tabelle([[zelle(para("Schwebend"), breite=2500), zelle(para("Tabelle"), breite=2500)]], [2500, 2500], raster + '<w:tblpPr w:leftFromText="180" w:rightFromText="180" w:vertAnchor="text" w:horzAnchor="margin" w:tblpXSpec="right" w:tblpY="1"/><w:tblOverlap w:val="never"/><w:tblW w:w="5000" w:type="dxa"/>'))
        text_absaetze(d, 6)
    elif art == 16:  # alternativer Text
        d.body.append(einfache_tabelle(rng, 2, 2, tblpr=raster + '<w:tblCaption w:val="Titel der Tabelle"/><w:tblDescription w:val="Beschreibung für Screenreader"/>'))
    elif art == 17:  # Darstellungsoptionen
        look = pick(['<w:tblLook w:val="0000"/>', '<w:tblLook w:val="04A0" w:firstRow="1" w:lastRow="0" w:firstColumn="1" w:lastColumn="0" w:noHBand="0" w:noVBand="1"/>', '<w:tblLook w:val="0FFF" w:firstRow="1" w:lastRow="1" w:firstColumn="1" w:lastColumn="1" w:noHBand="1" w:noVBand="1"/>'], i)
        d.body.append(einfache_tabelle(rng, 4, 3, tblpr=raster + look))
    elif art == 18:  # mehrere Absätze, Format in Zellen
        zeilen = [[zelle(para("Fett", "", RPR["fett"]) + para("Rechts", '<w:jc w:val="right"/>') + para(satz(rng, 2)), breite=4500), zelle(para(satz(rng)) + para("Zwei"), breite=4500)]]
        d.body.append(tabelle(zeilen, [4500, 4500], raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 19:  # Bild in Zelle
        rid = d.bild(png(30, 20, (60, 120, 200), 1))
        d.body.append(tabelle([[zelle(para(inhalt=run("", "", inline_bild(d, rid, 30, 20, 45 * EMU_PX, 30 * EMU_PX))), breite=4500), zelle(para("Text"), breite=4500)]], [4500, 4500], raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 20:  # nicht umbrechen, einpassen
        d.body.append(tabelle([[zelle(para("Kein Umbruch in dieser Zelle mit langem Text"), '<w:noWrap/>', 2000), zelle(para("Einpassen"), '<w:tcFitText/>', 2000), zelle(para(satz(rng)), breite=5000)]], [2000, 2000, 5000], raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 21:  # diagonale Rahmen, einzelne Zellrahmen
        zeilen = [[zelle(para("diag"), '<w:tcBorders><w:tl2br w:val="single" w:sz="8" w:space="0" w:color="FF0000"/></w:tcBorders>', 3000), zelle(para("andere"), '<w:tcBorders><w:tr2bl w:val="single" w:sz="8" w:space="0" w:color="0000FF"/><w:bottom w:val="double" w:sz="6" w:space="0" w:color="000000"/></w:tcBorders>', 3000), zelle(para("ohne"), '<w:tcBorders><w:top w:val="nil"/><w:left w:val="nil"/></w:tcBorders>', 3000)]]
        d.body.append(tabelle(zeilen, [3000] * 3, raster + '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 22:  # eine Zelle, leere Zellen
        d.body.append(tabelle([[zelle(para("Einzige Zelle"), breite=9000)]], [9000], raster))
        d.body.append(para())
        d.body.append(tabelle([[zelle("", breite=3000), zelle("", breite=3000), zelle("", breite=3000)]], [3000] * 3, raster))
    elif art == 23:  # breit, 20 Spalten
        d.body.append(einfache_tabelle(rng, 3, 20, 10000, tblpr=raster))
    elif art == 24:  # gridBefore/gridAfter
        zeilen = [[zelle(para("a"), breite=3000), zelle(para("b"), breite=3000)]]
        d.body.append(tabelle(zeilen, [3000, 3000, 3000], raster + '<w:tblW w:w="9000" w:type="dxa"/>', {0: '<w:gridBefore w:val="1"/><w:wBefore w:w="3000" w:type="dxa"/>'}))
    elif art == 25:  # Tabellen unmittelbar hintereinander, Absatz dazwischen
        d.body.append(einfache_tabelle(rng, 2, 2, tblpr=raster))
        d.body.append(einfache_tabelle(rng, 2, 2, tblpr=raster))
        d.body.append(para("dazwischen"))
        d.body.append(einfache_tabelle(rng, 2, 2, tblpr=raster))
    else:            # Absatzvorlage und Schrift in Zeilen/Spalten, Tabelle mit Vorlage ohne Gitter
        d.body.append(einfache_tabelle(rng, 4, 3, tblpr='<w:tblStyle w:val="TableNormal"/>'))
    d.body.append(para(satz(rng)))
    return d


def inline_bild(d: Dok, rid: str, pxb, pxh, cx, cy, name="Bild", descr="", rot=0, srcrect="", geom="rect", ln="", titel="", svg_rid="") -> str:
    n = d.id()
    xf = f'<a:xfrm{f" rot={chr(34)}{rot}{chr(34)}" if rot else ""}><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
    blip = f'<a:blip r:embed="{rid}">' + (f'<a:extLst><a:ext uri="{{96DAC541-7B7A-43D3-8B79-37D633B846F1}}"><asvg:svgBlip r:embed="{svg_rid}"/></a:ext></a:extLst>' if svg_rid else "") + "</a:blip>"
    pic = (f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{n}" name="{e(name)}" descr="{e(descr)}"{f" title={chr(34)}{e(titel)}{chr(34)}" if titel else ""}/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill>{blip}{srcrect}<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
           f'<pic:spPr>{xf}<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>{ln}</pic:spPr></pic:pic>')
    return (f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{n}" name="{e(name)}" descr="{e(descr)}"{f" title={chr(34)}{e(titel)}{chr(34)}" if titel else ""}/>'
            f'<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/></wp:cNvGraphicFramePr><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">{pic}</a:graphicData></a:graphic></wp:inline></w:drawing>')


# --------------------------------------------------------------------------------------------------------------------- Seite und Abschnitte
SEITEN = {"A4": (11906, 16838), "A3": (16838, 23811), "A5": (8391, 11906), "A6": (5953, 8391), "Letter": (12240, 15840), "Legal": (12240, 20160), "B5": (10319, 14571), "Executive": (10440, 15120), "Tabloid": (15840, 24480), "Quadrat": (10000, 10000), "Klein": (4000, 5000)}


def sect_xml(b=11906, h=16838, quer=False, rand=(1417, 1417, 1134, 1417), kopf=708, fuss=708, rinne=0, spalten="", extra="", typ="", refs="", titel=False, seitenzahl="", pgbord="", zeilen="", valign="", textr="") -> str:
    o = ' w:orient="landscape"' if quer else ""
    if quer:
        b, h = max(b, h), min(b, h)
    teile = [refs, f'<w:type w:val="{typ}"/>' if typ else "", f'<w:pgSz w:w="{b}" w:h="{h}"{o}/>', f'<w:pgMar w:top="{rand[0]}" w:right="{rand[1]}" w:bottom="{rand[2]}" w:left="{rand[3]}" w:header="{kopf}" w:footer="{fuss}" w:gutter="{rinne}"/>',
             pgbord, zeilen, seitenzahl, spalten, "<w:titlePg/>" if titel else "", textr, valign, extra]
    return "".join(t for t in teile if t)


def k_seite(i, rng):
    d = Dok(rng)
    art = i % 14
    d.kern["beschreibung"] = f"Seitenart {art}"
    name = pick(list(SEITEN), i)
    b, h = SEITEN[name]
    if art == 0:
        d.sect = sect_xml(b, h, quer=i % 2 == 0)
        d.kern["beschreibung"] += f" {name}"
    elif art == 1:
        m = [rng.choice([360, 720, 1134, 1417, 2268]) for _ in range(4)]
        d.sect = sect_xml(rand=tuple(m), kopf=rng.choice([200, 500, 708]), fuss=rng.choice([200, 500, 708]), rinne=rng.choice([0, 567, 1134]))
    elif art == 2:
        n = rng.choice([2, 3, 4])
        d.sect = sect_xml(spalten=f'<w:cols w:num="{n}" w:space="{rng.choice([360, 708, 1000])}"{" w:sep=" + chr(34) + "1" + chr(34) if i % 2 else ""}/>')
    elif art == 3:
        d.sect = sect_xml(spalten='<w:cols w:num="3" w:space="360" w:equalWidth="0"><w:col w:w="2000" w:space="360"/><w:col w:w="4000" w:space="360"/><w:col w:w="1800"/></w:cols>')
    elif art == 4:   # mehrere Abschnitte
        arten = ["nextPage", "continuous", "evenPage", "oddPage", "nextColumn"]
        for n in range(3):
            d.body.append(heading(f"Abschnitt {n + 1}"))
            text_absaetze(d, 4)
            d.body.append(f'<w:p><w:pPr><w:sectPr>{sect_xml(quer=n == 1, typ=pick(arten, i + n), spalten=f"<w:cols w:num={chr(34)}{n + 1}{chr(34)} w:space={chr(34)}708{chr(34)}/>")}</w:sectPr></w:pPr></w:p>')
        d.sect = sect_xml(typ=pick(arten, i + 3))
    elif art == 5:
        d.sect = sect_xml(titel=True, refs="")
        d.settings.append("<w:evenAndOddHeaders/>")
    elif art == 6:   # Zeilennummern
        d.sect = sect_xml(zeilen=f'<w:lnNumType w:countBy="{rng.choice([1, 2, 5])}" w:start="{rng.choice([1, 10])}" w:distance="{rng.choice([360, 567])}" w:restart="{pick(["continuous", "newPage", "newSection"], i)}"/>')
    elif art == 7:   # Seitenrahmen
        k = pick(["single", "double", "thick", "dashed", "triple", "wave", "box"] if False else ["single", "double", "thickThinLargeGap", "dashed", "triple", "wave", "dotted", "stars", "hearts"], i)
        d.sect = sect_xml(pgbord=f'<w:pgBorders w:offsetFrom="{pick(["page", "text"], i)}"><w:top w:val="{k}" w:sz="12" w:space="24" w:color="1F4E79"/><w:left w:val="{k}" w:sz="12" w:space="24" w:color="1F4E79"/><w:bottom w:val="{k}" w:sz="12" w:space="24" w:color="1F4E79"/><w:right w:val="{k}" w:sz="12" w:space="24" w:color="1F4E79"/></w:pgBorders>')
    elif art == 8:   # Seitenzahlformat
        fmt = pick(["decimal", "lowerRoman", "upperRoman", "lowerLetter", "upperLetter", "decimalZero", "chicago"], i)
        d.sect = sect_xml(seitenzahl=f'<w:pgNumType w:fmt="{fmt}" w:start="{rng.choice([1, 5, 100])}"/>', refs=d.kopf_fuss("footer", para(inhalt=feld("PAGE", "1"), ppr='<w:jc w:val="center"/>')).join(['<w:footerReference w:type="default" r:id="', '"/>']))
    elif art == 9:   # vertikale Ausrichtung
        d.sect = sect_xml(valign=f'<w:vAlign w:val="{pick(["top", "center", "both", "bottom"], i)}"/>')
    elif art == 10:  # Textrichtung, Gitter
        d.sect = sect_xml(textr=f'<w:textDirection w:val="{pick(["lrTb", "tbRl", "btLr"], i)}"/>', zeilen=f'<w:docGrid w:type="{pick(["lines", "linesAndChars", "snapToChars"], i)}" w:linePitch="360" w:charSpace="0"/>')
    elif art == 11:  # Spiegelränder, Buchfalz
        d.sect = sect_xml(rinne=1134)
        d.settings.append("<w:mirrorMargins/>")
        d.settings.append(f'<w:gutterAtTop/>' if False else "<w:bookFoldPrinting/>" if i % 2 else "")
    elif art == 12:  # Seitenhintergrund
        d.hintergrund = f'w:color="{pick(FARBEN, i)}"'
        d.settings.append("<w:displayBackgroundShape/>")
        d.sect = sect_xml()
    else:            # Extreme Maße
        d.sect = sect_xml(*pick([(1000, 1000), (31680, 31680), (11906, 16838)], i), rand=pick([(0, 0, 0, 0), (5000, 5000, 5000, 5000), (1417, 1417, 1417, 1417)], i))
    if art != 4:
        d.body.append(heading(f"Seitenlayout {art}: {name}"))
        for n in range(24 if art in (2, 3, 5, 6) else 12):
            d.body.append(para(satz(rng, 3)))
            if art == 5 and n == 6:
                d.body.append(para(inhalt='<w:r><w:br w:type="page"/></w:r>'))
    return d


# --------------------------------------------------------------------------------------------------------------------- Kopf- und Fußzeilen
def k_kopffuss(i, rng):
    d = Dok(rng)
    art = i % 10
    d.kern["beschreibung"] = f"Kopf/Fuß Art {art}"
    kopf_t = para("Kopfzeile des Testdokuments", '<w:pStyle w:val="Header"/>')
    fuss_t = para(inhalt=run("Seite ") + feld("PAGE", "1") + run(" von ") + feld("NUMPAGES", "3"), ppr='<w:pStyle w:val="Footer"/><w:jc w:val="center"/>')
    refs = ""

    def hf(art_, inhalt, typ="default"):
        rid = d.kopf_fuss(art_, inhalt)
        return f'<w:{art_}Reference w:type="{typ}" r:id="{rid}"/>'
    titel = False
    if art == 0:
        refs = hf("header", kopf_t) + hf("footer", fuss_t)
    elif art == 1:   # erste Seite abweichend
        refs = hf("header", kopf_t) + hf("header", para("Kopf der ersten Seite", '<w:pStyle w:val="Header"/>'), "first") + hf("footer", fuss_t) + hf("footer", para("Fuß erste", '<w:pStyle w:val="Footer"/>'), "first")
        titel = True
    elif art == 2:   # gerade/ungerade
        d.settings.append("<w:evenAndOddHeaders/>")
        refs = hf("header", para("Ungerade Seite", '<w:pStyle w:val="Header"/><w:jc w:val="right"/>')) + hf("header", para("Gerade Seite", '<w:pStyle w:val="Header"/>'), "even") + hf("footer", fuss_t) + hf("footer", fuss_t, "even")
    elif art == 3:   # Tabulatoren und Felder
        refs = hf("header", para(inhalt=run("Links\tMitte\t") + feld("DATE \\@ \"dd.MM.yyyy\"", "01.02.2026"), ppr='<w:pStyle w:val="Header"/>')) + hf("footer", para(inhalt=feld("FILENAME", "test.docx") + run("\t\t") + feld("PAGE", "1"), ppr='<w:pStyle w:val="Footer"/>'))
    elif art == 4:   # Tabelle in der Kopfzeile
        tab = tabelle([[zelle(para("Firma GmbH"), breite=4500), zelle(para("Seite ", '<w:jc w:val="right"/>', inhalt=feld("PAGE", "1")), breite=4500)]], [4500, 4500], '<w:tblW w:w="9000" w:type="dxa"/>')
        refs = hf("header", tab + para("", '<w:pStyle w:val="Header"/>'))
    elif art == 5:   # Bild in der Kopfzeile
        rid = d.bild(png(40, 20, (200, 60, 60), 2))
        refs = hf("header", para(inhalt=run("", "", inline_bild(d, rid, 40, 20, 60 * EMU_PX, 30 * EMU_PX, "Logo", "Firmenlogo")) + run(" Firma"), ppr='<w:pStyle w:val="Header"/>'))
    elif art == 6:   # je Abschnitt andere
        for n in range(3):
            r = hf("header", para(f"Kopf Abschnitt {n + 1}", '<w:pStyle w:val="Header"/>'))
            d.body.append(heading(f"Abschnitt {n + 1}"))
            text_absaetze(d, 5)
            d.body.append(f'<w:p><w:pPr><w:sectPr>{sect_xml(refs=r, typ="nextPage")}</w:sectPr></w:pPr></w:p>')
        refs = hf("header", para("Kopf des letzten Abschnitts", '<w:pStyle w:val="Header"/>'))
    elif art == 7:   # leere Kopfzeile, nur Fuß
        refs = hf("header", "") + hf("footer", fuss_t)
    elif art == 8:   # Rahmenlinie, Formatierung
        refs = hf("header", para("Bericht", '<w:pStyle w:val="Header"/><w:pBdr><w:bottom w:val="single" w:sz="8" w:space="1" w:color="1F4E79"/></w:pBdr><w:jc w:val="right"/>', RPR["fett"] + RPR["farbe_theme"])) + hf("footer", para("Vertraulich", '<w:pStyle w:val="Footer"/><w:pBdr><w:top w:val="single" w:sz="4" w:space="1" w:color="auto"/></w:pBdr>', RPR["kapitaelchen"]))
    else:            # Fußnotentrenner, Verknüpfung, Textmarke in Kopf
        link = d.rel(RT + "hyperlink", "https://example.org/", True)
        refs = hf("header", para(inhalt=f'<w:hyperlink r:id="{link}">{run("Beispielseite", "<w:rStyle w:val=" + chr(34) + "Hyperlink" + chr(34) + "/>")}</w:hyperlink>', ppr='<w:pStyle w:val="Header"/>')) + hf("footer", fuss_t)
    if art != 6:
        d.sect = sect_xml(refs=refs, titel=titel)
        d.body.append(heading("Dokument mit Kopf- und Fußzeile"))
        for n in range(30):
            d.body.append(para(satz(rng, 3)))
            if n % 12 == 11:
                d.body.append(para(inhalt='<w:r><w:br w:type="page"/></w:r>'))
    else:
        d.sect = sect_xml(refs=refs)
    return d


# --------------------------------------------------------------------------------------------------------------------- Felder, Verweise, Textmarken
def k_felder(i, rng):
    d = Dok(rng)
    art = i % 12
    d.kern["beschreibung"] = f"Feldart {art}"
    d.body.append(heading("Felder und Verweise"))
    einfach = [("DATE \\@ \"dd.MM.yyyy\"", "20.02.2026"), ("TIME \\@ \"HH:mm\"", "16:30"), ("PAGE", "1"), ("NUMPAGES", "1"), ("SECTION", "1"), ("SECTIONPAGES", "1"), ("AUTHOR", "Lunivo Testbestand"), ("TITLE", "Testdokument"), ("SUBJECT", ""), ("FILENAME \\p", "test.docx"),
               ("NUMWORDS", "120"), ("NUMCHARS", "800"), ("CREATEDATE", "15.01.2026"), ("SAVEDATE", "20.02.2026"), ("PRINTDATE", ""), ("EDITTIME", "5"), ("USERNAME", "Tester"), ("DOCPROPERTY \"Company\"", "Firma"), ("= 2+3*4", "14"), ("= SUM(ABOVE)", "0"),
               ("SEQ Abbildung \\* ARABIC", "1"), ("SEQ Tabelle \\* ROMAN", "I"), ("SYMBOL 169 \\f \"Symbol\" \\s 12", "©"), ("QUOTE \"Zitat\"", "Zitat"), ("IF 1 = 1 \"wahr\" \"falsch\"", "wahr"), ("COMPARE 1 > 2", "0"), ("AUTONUM", "1."), ("INFO Author", "Tester")]
    if art == 0:     # fldSimple
        for n in range(8):
            a, r = einfach[(i * 3 + n) % len(einfach)]
            d.body.append(para(inhalt=run(f"{a}: ") + f'<w:fldSimple w:instr=" {e(a)} "><w:r><w:t>{e(r)}</w:t></w:r></w:fldSimple>'))
    elif art == 1:   # komplexe Felder
        for n in range(8):
            a, r = einfach[(i * 3 + n) % len(einfach)]
            d.body.append(para(inhalt=run(f"{a}: ") + feld(a, r, dirty=n % 4 == 3)))
    elif art == 2:   # Textmarken und Querverweise
        d.body.append(para(inhalt=f'<w:bookmarkStart w:id="1" w:name="Ziel_A"/>{run("Textmarke A")}<w:bookmarkEnd w:id="1"/>'))
        d.body.append(heading("Überschrift mit Marke"))
        d.body[-1] = d.body[-1].replace("<w:r>", '<w:bookmarkStart w:id="2" w:name="_Ref123456"/><w:r>', 1).replace("</w:p>", '<w:bookmarkEnd w:id="2"/></w:p>')
        d.body.append(para(inhalt=run("Siehe ") + feld("REF Ziel_A \\h", "Textmarke A") + run(", Seite ") + feld("PAGEREF Ziel_A \\h", "1") + run(", ") + feld("REF _Ref123456 \\r \\h", "1")))
        d.body.append(para(inhalt=f'<w:bookmarkStart w:id="3" w:name="Verborgen_x"/>{run("Marke über Absatzgrenze")}'))
        d.body.append(para(inhalt=f'{run("Ende der Marke")}<w:bookmarkEnd w:id="3"/>'))
        d.body.append(para(inhalt='<w:bookmarkStart w:id="4" w:name="Leer"/><w:bookmarkEnd w:id="4"/>' + run("Leere Marke davor")))
    elif art == 3:   # Hyperlinks
        ext = d.rel(RT + "hyperlink", "https://example.org/pfad?x=1&y=2#abschnitt", True)
        mail = d.rel(RT + "hyperlink", "mailto:test@example.org", True)
        d.body.append(para(inhalt=f'<w:bookmarkStart w:id="1" w:name="Ziel"/>{run("Ziel")}<w:bookmarkEnd w:id="1"/>'))
        d.body.append(para(inhalt=f'<w:hyperlink r:id="{ext}" w:tooltip="Hinweistext">{run("Externer Link", "<w:rStyle w:val=" + chr(34) + "Hyperlink" + chr(34) + "/>")}</w:hyperlink>' + run(" und ") + f'<w:hyperlink r:id="{mail}">{run("Mail", "<w:rStyle w:val=" + chr(34) + "Hyperlink" + chr(34) + "/>")}</w:hyperlink>' + run(" und ") + f'<w:hyperlink w:anchor="Ziel" w:history="1">{run("Interner Link", "<w:rStyle w:val=" + chr(34) + "Hyperlink" + chr(34) + "/>")}</w:hyperlink>'))
        d.body.append(para(inhalt=feld(f'HYPERLINK "https://example.org/feld"', "Link als Feld", "<w:rStyle w:val=" + chr(34) + "Hyperlink" + chr(34) + "/>")))
        d.body.append(para(inhalt=f'<w:hyperlink r:id="{ext}">{run("Link mit ")}{run("gemischter", RPR["fett"])}{run(" Formatierung")}</w:hyperlink>'))
    elif art == 4:   # Inhaltsverzeichnis
        titel = [("Einleitung", 1), ("Grundlagen", 1), ("Begriffe", 2), ("Methoden", 2), ("Ergebnisse", 1), ("Auswertung", 2), ("Fazit", 1)]
        d.body.append(para("Inhaltsverzeichnis", '<w:pStyle w:val="TOCHeading"/>'))
        opt = pick(['\\o "1-3" \\h \\z \\u', '\\o "1-2" \\n', '\\o "1-9" \\h \\p " "', '\\t "Heading 1,1,Heading 2,2"'], i)
        for n, (t, st) in enumerate(titel):
            kopf = feld_start(f"TOC {opt}") if n == 0 else ""
            ende = '<w:r><w:fldChar w:fldCharType="end"/></w:r>' if n == len(titel) - 1 else ""
            d.body.append(para(inhalt=kopf + f'<w:hyperlink w:anchor="_Toc{n}" w:history="1">{run(t)}{run(chr(9))}{feld("PAGEREF _Toc" + str(n) + " \\h", str(n + 1))}</w:hyperlink>' + ende, ppr=f'<w:pStyle w:val="TOC{st}"/>'))
        for n, (t, st) in enumerate(titel):
            d.body.append(para(inhalt=f'<w:bookmarkStart w:id="{n + 10}" w:name="_Toc{n}"/>{run(t)}<w:bookmarkEnd w:id="{n + 10}"/>', ppr=f'<w:pStyle w:val="Heading{st}"/>'))
            d.body.append(para(satz(rng, 2)))
    elif art == 5:   # Beschriftungen
        for n in range(4):
            d.body.append(para(inhalt=run("Abbildung ") + feld("SEQ Abbildung \\* ARABIC", str(n + 1)) + run(f": Beschreibung {n + 1}"), ppr='<w:pStyle w:val="Caption"/>'))
        for n in range(2):
            d.body.append(para(inhalt=run("Tabelle ") + feld("SEQ Tabelle \\* ARABIC", str(n + 1)), ppr='<w:pStyle w:val="Caption"/>'))
        d.body.append(para(inhalt=feld('TOC \\h \\z \\c "Abbildung"', "Abbildungsverzeichnis")))
    elif art == 6:   # Index
        d.body.append(para(inhalt=run("Stichwort") + feld('XE "Stichwort:Unterpunkt"', "", "<w:vanish/>") + run(" im Text.")))
        d.body.append(para(inhalt=feld('INDEX \\c "2" \\z "1031"', "Stichwort, 1")))
        d.body.append(para(inhalt=feld('TC "Eintrag" \\f C \\l 1', "", "<w:vanish/>") + run("Verzeichniseintrag")))
    elif art == 7:   # verschachtelte Felder
        inner = feld("PAGE", "1")
        d.body.append(para(inhalt='<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> IF </w:instrText></w:r>' + inner + '<w:r><w:instrText xml:space="preserve"> &gt; 0 "positiv" "leer" </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>' + run("positiv") + '<w:r><w:fldChar w:fldCharType="end"/></w:r>'))
        d.body.append(para(inhalt=feld("SYMBOL 252 \\f Wingdings", "ü", RPR["schrift_arial"])))
        d.body.append(para(inhalt=feld("= (2+3)*(4-1)", "15") + run(" und ") + feld("= 10 / 4 \\# 0,00", "2,50")))
    elif art == 8:   # Serienbrief
        d.settings.append('<w:mailMerge><w:mainDocumentType w:val="formLetters"/><w:dataType w:val="textFile"/></w:mailMerge>' if False else "")
        d.body.append(para(inhalt=run("Sehr geehrte(r) ") + feld("MERGEFIELD Anrede", "«Anrede»") + run(" ") + feld("MERGEFIELD Nachname \\* Upper", "«NACHNAME»") + run(",")))
        d.body.append(para(inhalt=feld("NEXT", "«Nächster Datensatz»") + feld("SKIPIF 1 = 2", "") + feld("MERGEREC", "1")))
    elif art == 9:   # Felder mit formatiertem Ergebnis
        d.body.append(para(inhalt=feld("TITLE \\* MERGEFORMAT", "Testdokument", RPR["fett"] + RPR["farbe_rot"]) + run(" – ") + feld("AUTHOR \\* Upper", "LUNIVO", RPR["kursiv"]) + run(" – ") + feld("DATE \\@ \"d. MMMM yyyy\" \\* MERGEFORMAT", "20. Februar 2026", RPR["u_einfach"])))
        d.body.append(para(inhalt=feld("STYLEREF \"Heading 1\"", "Felder und Verweise")))
    elif art == 10:  # Felder über mehrere Absätze, gesperrt, Formularfeld
        d.body.append(para(inhalt='<w:r><w:fldChar w:fldCharType="begin" w:fldLock="1"/></w:r><w:r><w:instrText xml:space="preserve"> AUTHOR </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>' + run("Gesperrtes Feld") + '<w:r><w:fldChar w:fldCharType="end"/></w:r>'))
        d.body.append(para(inhalt='<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> QUOTE "Feld über </w:instrText></w:r>'))
        d.body.append(para(inhalt='<w:r><w:instrText xml:space="preserve">zwei Absätze" </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>' + run("Ergebnis") + '<w:r><w:fldChar w:fldCharType="end"/></w:r>'))
    else:            # Zitate, Literatur, Gleichungsfelder
        d.body.append(para(inhalt=run("Zitat: ") + feld("CITATION Quelle1 \\l 1031", "(Muster, 2020)") + run(" Literatur: ") + feld("BIBLIOGRAPHY \\l 1031", "Literaturverzeichnis")))
        d.body.append(para(inhalt=feld("EQ \\f(1,2)", "½") + run(" ") + feld("EQ \\r(2)", "√2") + run(" ") + feld("EQ \\s\\up8(2)", "²")))
        d.body.append(para(inhalt=feld("LISTNUM LegalDefault", "1.") + feld("GOTOBUTTON Ziel Sprung", "Sprung") + feld("MACROBUTTON NoMacro Klick", "Klick")))
    d.body.append(para(satz(rng)))
    return d


def feld_start(anweisung: str) -> str:
    return f'<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> {e(anweisung)} </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>'


# --------------------------------------------------------------------------------------------------------------------- Bilder
UMFLUSS = ['<wp:wrapNone/>', '<wp:wrapSquare wrapText="bothSides"/>', '<wp:wrapSquare wrapText="left"/>', '<wp:wrapSquare wrapText="right"/>', '<wp:wrapSquare wrapText="largest"/>',
           '<wp:wrapTight wrapText="bothSides"><wp:wrapPolygon edited="0"><wp:start x="0" y="0"/><wp:lineTo x="0" y="21600"/><wp:lineTo x="21600" y="21600"/><wp:lineTo x="21600" y="0"/><wp:lineTo x="0" y="0"/></wp:wrapPolygon></wp:wrapTight>',
           '<wp:wrapThrough wrapText="bothSides"><wp:wrapPolygon edited="0"><wp:start x="0" y="0"/><wp:lineTo x="0" y="21600"/><wp:lineTo x="21600" y="21600"/><wp:lineTo x="21600" y="0"/><wp:lineTo x="0" y="0"/></wp:wrapPolygon></wp:wrapThrough>', '<wp:wrapTopAndBottom/>']


def anker_xml(d: Dok, grafik: str, cx, cy, wrap, h=("column", "offset", 0), v=("paragraph", "offset", 0), hinter=False, name="Objekt", descr="", abst=(0, 0, 114300, 114300), effekt=(0, 0, 0, 0), sperre=False, ueberlappen=True, gid=None) -> str:
    n = gid or d.id()
    def pos(tag, p):
        bezug, art, wert = p
        return f'<wp:{tag} relativeFrom="{bezug}">' + (f"<wp:align>{wert}</wp:align>" if art == "align" else f"<wp:posOffset>{wert}</wp:posOffset>") + f"</wp:{tag}>"
    return (f'<w:drawing><wp:anchor distT="{abst[0]}" distB="{abst[1]}" distL="{abst[2]}" distR="{abst[3]}" simplePos="0" relativeHeight="{251658240 + n}" behindDoc="{1 if hinter else 0}" locked="{1 if sperre else 0}" layoutInCell="1" allowOverlap="{1 if ueberlappen else 0}">'
            f'<wp:simplePos x="0" y="0"/>{pos("positionH", h)}{pos("positionV", v)}<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="{effekt[0]}" t="{effekt[1]}" r="{effekt[2]}" b="{effekt[3]}"/>{wrap}'
            f'<wp:docPr id="{n}" name="{e(name)} {n}" descr="{e(descr)}"/><wp:cNvGraphicFramePr/>{grafik}</wp:anchor></w:drawing>')


def grafik_bild(d: Dok, rid, cx, cy, geom="rect", rot=0, flip="", srcrect="", ln="", alpha=None, svg_rid="") -> str:
    n = d.id()
    af = f'<a:alphaModFix amt="{alpha}"/>' if alpha else ""
    blip = f'<a:blip r:embed="{rid}">{af}' + (f'<a:extLst><a:ext uri="{{96DAC541-7B7A-43D3-8B79-37D633B846F1}}"><asvg:svgBlip r:embed="{svg_rid}"/></a:ext></a:extLst>' if svg_rid else "") + "</a:blip>"
    return (f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{n}" name="Bild {n}"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill>{blip}{srcrect}<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm{f" rot={chr(34)}{rot}{chr(34)}" if rot else ""}{flip}><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>{ln}</pic:spPr></pic:pic></a:graphicData></a:graphic>')


def k_bilder(i, rng):
    d = Dok(rng)
    art = i % 15
    farbe = tuple(rng.randint(30, 220) for _ in range(3))
    pb, ph = rng.choice([(20, 20), (40, 24), (30, 50), (64, 36), (8, 8)])
    daten = png(pb, ph, farbe, i % 3)
    rid = d.bild(daten)
    cx, cy = int(rng.choice([20, 40, 60, 90]) * EMU_MM / 3.78 * 3.78 / 3.78 * 3.78 / 3.78), 0
    cx = int(rng.choice([25, 45, 70, 110]) * EMU_MM)
    cy = int(cx * ph / pb)
    d.kern["beschreibung"] = f"Bildart {art}"
    d.body.append(heading(f"Bilder Art {art}"))
    if art == 0:
        d.body.append(para(inhalt=run("Inline: ") + run("", "", inline_bild(d, rid, pb, ph, cx, cy, "Bild", f"Alternativtext {i}", titel="Titel")) + run(" im Text.")))
    elif art == 1:   # Umfluss
        for n, w in enumerate(UMFLUSS):
            d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, cx // 2, cy // 2), cx // 2, cy // 2, w, ("column", "align", pick(["left", "right", "center"], n)), ("paragraph", "offset", 0), name="Umfluss " + str(n))) + run(satz(rng, 3))))
    elif art == 2:   # Bezüge und Ausrichtung
        bez_h = ["page", "margin", "column", "character", "leftMargin", "rightMargin", "insideMargin", "outsideMargin"]
        bez_v = ["page", "margin", "paragraph", "line", "topMargin", "bottomMargin", "insideMargin", "outsideMargin"]
        a = ("align", pick(["left", "center", "right", "inside", "outside"], i))
        d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, cx, cy), cx, cy, UMFLUSS[1], (pick(bez_h, i), a[0], a[1] if a[0] == "align" else 0), (pick(bez_v, i + 3), "offset", rng.randint(-100000, 900000)))) + run(satz(rng, 4))))
    elif art == 3:   # hinter/vor dem Text
        d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, cx, cy, alpha=40000), cx, cy, UMFLUSS[0], ("page", "offset", 1500000), ("page", "offset", 2000000), hinter=True, name="Hinter")) + run(satz(rng, 4))))
        d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, cx, cy), cx, cy, UMFLUSS[0], ("page", "offset", 1700000), ("page", "offset", 2100000), name="Davor")) + run(satz(rng, 2))))
    elif art == 4:   # Zuschnitt
        s = f'<a:srcRect l="{rng.randint(0, 30000)}" t="{rng.randint(0, 30000)}" r="{rng.randint(0, 30000)}" b="{rng.randint(0, 30000)}"/>'
        d.body.append(para(inhalt=run("", "", inline_bild(d, rid, pb, ph, cx, cy, srcrect=s, descr="zugeschnitten"))))
    elif art == 5:   # Drehung, Spiegelung
        d.body.append(para(inhalt=run("", "", inline_bild(d, rid, pb, ph, cx, cy, rot=rng.choice([900000, 2700000, 5400000, 10800000, -1800000])))))
        d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, cx, cy, flip=pick([' flipH="1"', ' flipV="1"', ' flipH="1" flipV="1"'], i)), cx, cy, UMFLUSS[1], name="Gespiegelt"))))
    elif art == 6:   # Form und Rahmen
        ln = f'<a:ln w="{rng.choice([9525, 25400, 57150])}"><a:solidFill><a:srgbClr val="{pick(FARBEN, i)}"/></a:solidFill><a:prstDash val="{pick(["solid", "dash", "dot", "sysDash"], i)}"/></a:ln>'
        d.body.append(para(inhalt=run("", "", inline_bild(d, rid, pb, ph, cx, cy, geom=pick(["ellipse", "roundRect", "triangle", "diamond", "hexagon", "star5", "heart"], i), ln=ln))))
    elif art == 7:   # andere Bildformate
        fmt = pick([("bmp", bmp(16, 10, farbe)), ("gif", GIF), ("jpeg", JPG), ("svg", SVG)], i)
        if fmt[0] == "svg":
            r2 = d.bild(SVG, "svg")
            d.body.append(para(inhalt=run("", "", inline_bild(d, rid, 60, 40, 60 * EMU_PX, 40 * EMU_PX, svg_rid=r2))))
        else:
            r2 = d.bild(fmt[1], fmt[0])
            d.body.append(para(inhalt=run("", "", inline_bild(d, r2, 16, 10, 80 * EMU_PX, 50 * EMU_PX, f"Bild.{fmt[0]}"))))
    elif art == 8:   # mehrere Bilder in einer Zeile, verschiedene Größen
        d.body.append(para(inhalt="".join(run("", "", inline_bild(d, d.bild(png(20, 20, tuple(rng.randint(0, 255) for _ in range(3)))), 20, 20, s * EMU_PX, s * EMU_PX)) + run(" ") for s in (16, 32, 64, 96, 24))))
    elif art == 9:   # fehlendes Bild und beschädigte Daten
        d.body.append(para(inhalt=run("", "", inline_bild(d, "rId9999", 20, 20, 40 * EMU_PX, 40 * EMU_PX, descr="fehlende Beziehung"))))
        kaputt = d.bild(b"das ist kein Bild", "png")
        d.body.append(para(inhalt=run("", "", inline_bild(d, kaputt, 20, 20, 40 * EMU_PX, 40 * EMU_PX, descr="kaputte Bilddaten"))))
        link = d.rel(RT + "image", "file:///nicht/vorhanden.png", True)
        d.body.append(para(inhalt=run("", "", inline_bild(d, link, 20, 20, 40 * EMU_PX, 40 * EMU_PX, descr="verknüpft, nicht eingebettet"))))
    elif art == 10:  # Abstände zum Text, Effektrand
        d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, cx, cy), cx, cy, UMFLUSS[1], ("column", "align", "right"), abst=(rng.choice([0, 91440, 228600]),) * 2 + (rng.choice([0, 114300, 342900]),) * 2, effekt=(50800, 50800, 50800, 50800))) + run(satz(rng, 6))))
    elif art == 11:  # Bild im Absatz mit Zeilenabstand
        for ab in ('<w:spacing w:line="240" w:lineRule="exact"/>', '<w:spacing w:line="480" w:lineRule="auto"/>', '<w:spacing w:line="240" w:lineRule="atLeast"/>'):
            d.body.append(para(inhalt=run("Text ") + run("", "", inline_bild(d, rid, pb, ph, cx, cy)) + run(" Text"), ppr=ab))
    elif art == 12:  # Bild mit Beschriftung und Zentrierung
        d.body.append(para(inhalt=run("", "", inline_bild(d, rid, pb, ph, cx, cy)), ppr='<w:keepNext/><w:jc w:val="center"/>'))
        d.body.append(para(inhalt=run("Abbildung ") + feld("SEQ Abbildung \\* ARABIC", "1") + run(": Beispielbild"), ppr='<w:pStyle w:val="Caption"/><w:jc w:val="center"/>'))
    elif art == 13:  # sehr groß / sehr klein
        w = pick([(1, 1), (5000 * EMU_PX, 3500 * EMU_PX), (0, 0), (30 * EMU_MM, 10 * EMU_MM)], i)
        d.body.append(para(inhalt=run("", "", inline_bild(d, rid, pb, ph, w[0], w[1], descr="Extremmaß"))))
    else:            # Bild in Textfeld/Rahmen und gesperrter Anker
        d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, cx, cy), cx, cy, UMFLUSS[7], ("margin", "align", "center"), ("paragraph", "offset", 0), sperre=True, ueberlappen=False))))
        text_absaetze(d, 3)
    d.body.append(para(satz(rng)))
    return d


# --------------------------------------------------------------------------------------------------------------------- Formen
GEOMETRIEN = ["rect", "roundRect", "ellipse", "triangle", "rtTriangle", "parallelogram", "trapezoid", "diamond", "pentagon", "hexagon", "octagon", "star4", "star5", "star6", "star8", "star16", "plus", "cross" if False else "plus",
              "rightArrow", "leftArrow", "upArrow", "downArrow", "leftRightArrow", "bentArrow", "uturnArrow", "circularArrow", "chevron", "homePlate", "wedgeRectCallout", "wedgeEllipseCallout", "cloudCallout", "borderCallout1",
              "heart", "lightningBolt", "sun", "moon", "cloud", "smileyFace", "noSmoking", "donut", "blockArc", "arc", "bracePair", "bracketPair", "leftBrace", "line", "straightConnector1", "flowChartProcess", "flowChartDecision",
              "flowChartTerminator", "mathPlus", "mathEqual", "can", "cube", "bevel", "foldedCorner", "frame", "halfFrame", "ribbon", "wave", "doubleWave", "teardrop", "gear6", "funnel", "pie", "chord"]


def fuellung(art: str, i: int) -> str:
    f = pick(FARBEN, i)
    return {
        "voll": f'<a:solidFill><a:srgbClr val="{f}"/></a:solidFill>',
        "keine": "<a:noFill/>",
        "transparent": f'<a:solidFill><a:srgbClr val="{f}"><a:alpha val="40000"/></a:srgbClr></a:solidFill>',
        "theme": '<a:solidFill><a:schemeClr val="accent2"><a:lumMod val="60000"/><a:lumOff val="40000"/></a:schemeClr></a:solidFill>',
        "linear": f'<a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:srgbClr val="{f}"/></a:gs><a:gs pos="50000"><a:srgbClr val="FFFFFF"/></a:gs><a:gs pos="100000"><a:srgbClr val="{pick(FARBEN, i + 5)}"/></a:gs></a:gsLst><a:lin ang="{pick([0, 5400000, 2700000, 10800000], i)}" scaled="0"/></a:gradFill>',
        "pfad": f'<a:gradFill><a:gsLst><a:gs pos="0"><a:srgbClr val="{f}"/></a:gs><a:gs pos="100000"><a:srgbClr val="000000"/></a:gs></a:gsLst><a:path path="circle"><a:fillToRect l="50000" t="50000" r="50000" b="50000"/></a:path></a:gradFill>',
        "muster": f'<a:pattFill prst="{pick(["pct50", "ltDnDiag", "dkHorz", "smCheck", "weave", "zigZag"], i)}"><a:fgClr><a:srgbClr val="{f}"/></a:fgClr><a:bgClr><a:srgbClr val="FFFFFF"/></a:bgClr></a:pattFill>',
    }[art]


def kontur(i: int, art="voll") -> str:
    if art == "keine":
        return "<a:ln><a:noFill/></a:ln>"
    pfeil = '<a:headEnd type="triangle" w="med" len="med"/><a:tailEnd type="arrow" w="lg" len="lg"/>' if art == "pfeil" else ""
    dash = pick(["solid", "dash", "dot", "dashDot", "lgDash", "sysDot"], i)
    return f'<a:ln w="{pick([6350, 12700, 25400, 57150], i)}" cap="{pick(["flat", "rnd", "sq"], i)}"><a:solidFill><a:srgbClr val="{pick(FARBEN, i + 2)}"/></a:solidFill><a:prstDash val="{dash}"/><a:round/>{pfeil}</a:ln>'


EFFEKTE = ["", '<a:effectLst><a:outerShdw blurRad="50800" dist="38100" dir="2700000" algn="tl" rotWithShape="0"><a:srgbClr val="000000"><a:alpha val="40000"/></a:srgbClr></a:outerShdw></a:effectLst>',
           '<a:effectLst><a:glow rad="101600"><a:srgbClr val="FFC000"><a:alpha val="40000"/></a:srgbClr></a:glow></a:effectLst>', '<a:effectLst><a:softEdge rad="63500"/></a:effectLst>',
           '<a:effectLst><a:reflection blurRad="6350" stA="50000" endA="300" endPos="35000" dist="0" dir="5400000" sy="-100000" algn="bl" rotWithShape="0"/></a:effectLst>',
           '<a:effectLst><a:innerShdw blurRad="63500" dist="50800" dir="13500000"><a:srgbClr val="000000"><a:alpha val="50000"/></a:srgbClr></a:innerShdw></a:effectLst>']


def wps_form(d: Dok, cx, cy, geom="rect", fuell="voll", kont="voll", effekt="", text=None, rot=0, i=0, textfeld=False, adj="", ankerform=None, gruppe=False, xy=(0, 0), vert="horz", ankerpos="t", name="Form") -> str:
    n = d.id()
    xf = f'<a:xfrm{f" rot={chr(34)}{rot}{chr(34)}" if rot else ""}><a:off x="{xy[0]}" y="{xy[1]}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
    tb = f'<wps:txbx><w:txbxContent>{text}</w:txbxContent></wps:txbx>' if text else ""
    return (f'<wps:wsp><wps:cNvPr id="{n}" name="{name} {n}"/><wps:cNvSpPr{" txBox=" + chr(34) + "1" + chr(34) if textfeld else ""}/><wps:spPr>{xf}<a:prstGeom prst="{geom}"><a:avLst>{adj}</a:avLst></a:prstGeom>{fuellung(fuell, i)}{kontur(i, kont)}{effekt}</wps:spPr>{tb}'
            f'<wps:bodyPr rot="0" vert="{vert}" wrap="square" lIns="91440" tIns="45720" rIns="91440" bIns="45720" anchor="{ankerpos}" anchorCtr="0"><a:noAutofit/></wps:bodyPr></wps:wsp>')


def wps_huelle(d: Dok, wsp: str, cx, cy, wrap, h, v, hinter=False, name="Form", alternativ=True) -> str:
    gr = f'<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingShape">{wsp}</a:graphicData></a:graphic>'
    dr = anker_xml(d, gr, cx, cy, wrap, h, v, hinter=hinter, name=name)
    if not alternativ:
        return dr
    return f'<mc:AlternateContent><mc:Choice Requires="wps">{dr}</mc:Choice><mc:Fallback><w:pict><v:rect style="position:absolute;width:{cx // EMU_PX}px;height:{cy // EMU_PX}px" fillcolor="#c0c0c0"/></w:pict></mc:Fallback></mc:AlternateContent>'


def k_formen(i, rng):
    d = Dok(rng)
    art = i % 10
    cx, cy = rng.choice([(60, 40), (90, 30), (40, 40), (120, 60)])
    cx, cy = cx * EMU_MM, cy * EMU_MM
    d.kern["beschreibung"] = f"Formart {art}"
    d.body.append(heading(f"Formen Art {art}"))
    geom = pick(GEOMETRIEN, i)
    wrap = pick(UMFLUSS, i)
    h = ("column", "offset", rng.randint(0, 2000000))
    v = ("paragraph", "offset", 0)
    if art == 0:     # Geometrien
        for n in range(4):
            g = pick(GEOMETRIEN, i * 4 + n)
            d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx // 2, cy // 2, g, i=i + n), cx // 2, cy // 2, UMFLUSS[1], ("column", "align", pick(["left", "right"], n)), ("paragraph", "offset", 0))) + run(f"{g}: " + satz(rng, 2))))
    elif art == 1:   # Füllungen
        for n, fa in enumerate(["voll", "keine", "transparent", "theme", "linear", "pfad", "muster"]):
            d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx // 3, cy // 2, geom, fa, i=i + n), cx // 3, cy // 2, UMFLUSS[1], ("column", "align", "left"), ("paragraph", "offset", 0))) + run(f"Füllung {fa}. " + satz(rng))))
    elif art == 2:   # Linien und Pfeile
        for n, ka in enumerate(["voll", "keine", "pfeil"]):
            d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx, 0 if n == 2 else cy // 2, "line" if n == 2 else "rect", "keine", ka, i=i + n), cx, 1 if n == 2 else cy // 2, UMFLUSS[3], ("column", "offset", 0), ("paragraph", "offset", 0))) + run(f"Kontur {ka}")))
    elif art == 3:   # Effekte
        for n, ef in enumerate(EFFEKTE):
            d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx // 3, cy // 2, geom, "voll", "voll", ef, i=i + n), cx // 3, cy // 2, UMFLUSS[7], ("column", "align", "center"), ("paragraph", "offset", 0))) ))
    elif art == 4:   # Textfeld mit Inhalt
        inh = para("Titel im Textfeld", '<w:jc w:val="center"/>', RPR["fett"]) + para(satz(rng, 2)) + tabelle([[zelle(para("a"), breite=1000), zelle(para("b"), breite=1000)]], [1000, 1000], '<w:tblStyle w:val="TableGrid"/>') + para("Ende")
        d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx, cy * 2, "rect", pick(["keine", "voll"], i), "voll", "", inh, i=i, textfeld=True), cx, cy * 2, wrap, h, v)) + run(satz(rng, 4))))
    elif art == 5:   # Textrichtung, Verankerung
        for n, (vt, ap) in enumerate([("horz", "t"), ("horz", "ctr"), ("horz", "b"), ("vert", "t"), ("vert270", "ctr"), ("eaVert", "t")]):
            d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx // 2, cy, "rect", "keine", "voll", "", para(f"{vt} {ap}"), i=i, textfeld=True, vert=vt, ankerpos=ap), cx // 2, cy, UMFLUSS[1], ("column", "align", "right"), ("paragraph", "offset", 0))) + run(satz(rng))))
    elif art == 6:   # Gruppe
        a = wps_form(d, cx // 2, cy // 2, "ellipse", "voll", i=i, xy=(0, 0)) + wps_form(d, cx // 2, cy // 2, "rect", "linear", i=i + 1, xy=(cx // 2, cy // 2)) + wps_form(d, cx, cy // 4, "rect", "keine", "voll", "", para("Beschriftung"), textfeld=True, xy=(0, cy - cy // 4), i=i)
        grp = (f'<wpg:wgp><wpg:cNvGrpSpPr/><wpg:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/><a:chOff x="0" y="0"/><a:chExt cx="{cx}" cy="{cy}"/></a:xfrm></wpg:grpSpPr>{a}</wpg:wgp>')
        gr = f'<a:graphic><a:graphicData uri="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup">{grp}</a:graphicData></a:graphic>'
        d.body.append(para(inhalt=run("", "", f'<mc:AlternateContent><mc:Choice Requires="wpg">{anker_xml(d, gr, cx, cy, wrap, h, v, name="Gruppe")}</mc:Choice><mc:Fallback><w:pict/></mc:Fallback></mc:AlternateContent>') + run(satz(rng, 3))))
    elif art == 7:   # Drehung und Anpassungswerte
        for n in range(3):
            adj = f'<a:gd name="adj" fmla="val {rng.randint(0, 50000)}"/>' if geom in ("roundRect", "star5", "rightArrow") else ""
            d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx // 2, cy // 2, pick(["roundRect", "star5", "rightArrow"], n + i), "voll", rot=rng.choice([0, 1800000, 5400000, -2700000]), i=i + n, adj=adj), cx // 2, cy // 2, UMFLUSS[1], ("column", "align", "left"), ("paragraph", "offset", 0))) + run(satz(rng))))
    elif art == 8:   # alte VML-Objekte
        v = ["", ""]
        v[0] = f'<w:pict><v:rect style="position:absolute;margin-left:0;margin-top:0;width:120pt;height:40pt;z-index:1" fillcolor="#{pick(FARBEN, i)}" strokecolor="#000000" strokeweight="1pt"><v:textbox><w:txbxContent>{para("VML-Textfeld")}</w:txbxContent></v:textbox></v:rect></w:pict>'
        v[1] = f'<w:pict><v:oval style="position:absolute;width:60pt;height:40pt" fillcolor="#{pick(FARBEN, i + 3)}"/></w:pict>'
        wordart = ('<w:pict><v:shapetype id="_x0000_t136" coordsize="21600,21600" o:spt="136" adj="10800" path="m@7,l@8,m@5,21600l@6,21600e"><v:path textpathok="t" o:connecttype="custom"/><v:textpath on="t" fitshape="t"/><o:lock v:ext="edit" text="t" shapetype="t"/></v:shapetype>'
                   f'<v:shape id="WordArt1" type="#_x0000_t136" style="position:absolute;width:200pt;height:40pt" fillcolor="#{pick(FARBEN, i)}" stroked="f"><v:textpath style="font-family:&quot;Arial&quot;;font-size:24pt" string="WordArt Text"/></v:shape></w:pict>')
        d.body.append(para(inhalt=run("", "", v[0]) + run(" ") + run("", "", v[1])))
        d.body.append(para(inhalt=run("", "", wordart)))
        d.body.append(para(inhalt=run("", "", '<w:pict><v:line from="0,0" to="200pt,0" strokecolor="#FF0000" strokeweight="2pt"/></w:pict>')))
        d.body.append(para(inhalt=run("", "", '<w:pict><v:roundrect style="width:100pt;height:30pt" arcsize="0.2" fillcolor="#ffff99"><v:shadow on="t" color="gray" offset="3pt,3pt"/></v:roundrect></w:pict>')))
    else:            # Form ohne Alternativinhalt, Form im Absatz mit Tabelle
        w = wps_huelle(d, wps_form(d, cx, cy, geom, "voll", i=i, text=para("Text"), textfeld=True), cx, cy, UMFLUSS[2], h, v, alternativ=False)
        d.body.append(tabelle([[zelle(para(inhalt=run("", "", w) + run("In Tabellenzelle")), breite=4500), zelle(para("Rechts"), breite=4500)]], [4500, 4500], '<w:tblStyle w:val="TableGrid"/><w:tblW w:w="9000" w:type="dxa"/>'))
        d.body.append(para(inhalt=run("", "", wps_huelle(d, wps_form(d, cx, cy, "rect", "voll", i=i), cx, cy, UMFLUSS[0], ("page", "offset", 500000), ("page", "offset", 8000000), True, "Hinten")) + run(satz(rng))))
    d.body.append(para(satz(rng)))
    return d


# --------------------------------------------------------------------------------------------------------------------- Diagramme
def diagramm_xml(art: str, rng, titel: str, serien: int, legende: str, beschriftung: bool, achsentitel: bool) -> str:
    kat = ["Q1", "Q2", "Q3", "Q4", "Q5"][: rng.randint(3, 5)]
    n = len(kat)

    def cat():
        return (f'<c:cat><c:strRef><c:f>Tabelle1!$A$2:$A${n + 1}</c:f><c:strCache><c:ptCount val="{n}"/>' + "".join(f'<c:pt idx="{k}"><c:v>{t}</c:v></c:pt>' for k, t in enumerate(kat)) + "</c:strCache></c:strRef></c:cat>")

    def werte(s, tag="val"):
        sp = chr(ord("B") + s)
        return (f'<c:{tag}><c:numRef><c:f>Tabelle1!${sp}$2:${sp}${n + 1}</c:f><c:numCache><c:formatCode>General</c:formatCode><c:ptCount val="{n}"/>' + "".join(f'<c:pt idx="{k}"><c:v>{rng.randint(1, 100)}</c:v></c:pt>' for k in range(n)) + f"</c:numCache></c:numRef></c:{tag}>")

    def ser(s, kind):
        sp = chr(ord("B") + s)
        farbe = pick(FARBEN, s * 2 + 1)
        tx = f'<c:tx><c:strRef><c:f>Tabelle1!${sp}$1</c:f><c:strCache><c:ptCount val="1"/><c:pt idx="0"><c:v>Reihe {s + 1}</c:v></c:pt></c:strCache></c:strRef></c:tx>'
        sppr = f'<c:spPr><a:solidFill><a:srgbClr val="{farbe}"/></a:solidFill></c:spPr>' if kind != "line" else f'<c:spPr><a:ln w="28575"><a:solidFill><a:srgbClr val="{farbe}"/></a:solidFill></a:ln></c:spPr>'
        dl = '<c:dLbls><c:showLegendKey val="0"/><c:showVal val="1"/><c:showCatName val="0"/><c:showSerName val="0"/><c:showPercent val="0"/><c:showBubbleSize val="0"/></c:dLbls>' if beschriftung else ""
        if kind == "scatter":
            return f'<c:ser><c:idx val="{s}"/><c:order val="{s}"/>{tx}{sppr}<c:marker><c:symbol val="circle"/><c:size val="7"/></c:marker>{dl}{werte(s, "xVal")}{werte(s, "yVal")}<c:smooth val="0"/></c:ser>'
        extra = '<c:marker><c:symbol val="diamond"/><c:size val="6"/></c:marker>' if kind == "line" else ('<c:invertIfNegative val="0"/>' if kind == "bar" else "")
        glatt = '<c:smooth val="0"/>' if kind == "line" else ""
        return f'<c:ser><c:idx val="{s}"/><c:order val="{s}"/>{tx}{sppr}{extra}{dl}{cat()}{werte(s)}{glatt}</c:ser>'

    achsen_t = lambda t: f'<c:title><c:tx><c:rich><a:bodyPr/><a:p><a:r><a:t>{t}</a:t></a:r></a:p></c:rich></c:tx><c:overlay val="0"/></c:title>' if achsentitel else ""  # noqa: E731
    cat_ax = f'<c:catAx><c:axId val="111"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="b"/>{achsen_t("Kategorien")}<c:numFmt formatCode="General" sourceLinked="0"/><c:majorTickMark val="out"/><c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/><c:crossAx val="222"/><c:crosses val="autoZero"/><c:auto val="1"/><c:lblAlgn val="ctr"/><c:lblOffset val="100"/><c:noMultiLvlLbl val="0"/></c:catAx>'
    val_ax = f'<c:valAx><c:axId val="222"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="l"/><c:majorGridlines/>{achsen_t("Werte")}<c:numFmt formatCode="General" sourceLinked="0"/><c:majorTickMark val="out"/><c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/><c:crossAx val="111"/><c:crosses val="autoZero"/><c:crossBetween val="between"/></c:valAx>'
    xy_ax = ('<c:valAx><c:axId val="111"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="b"/><c:numFmt formatCode="General" sourceLinked="0"/><c:majorTickMark val="out"/><c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/><c:crossAx val="222"/><c:crosses val="autoZero"/><c:crossBetween val="midCat"/></c:valAx>'
             '<c:valAx><c:axId val="222"/><c:scaling><c:orientation val="minMax"/></c:scaling><c:delete val="0"/><c:axPos val="l"/><c:majorGridlines/><c:numFmt formatCode="General" sourceLinked="0"/><c:majorTickMark val="out"/><c:minorTickMark val="none"/><c:tickLblPos val="nextTo"/><c:crossAx val="111"/><c:crosses val="autoZero"/><c:crossBetween val="midCat"/></c:valAx>')
    ax = '<c:axId val="111"/><c:axId val="222"/>'
    reihen = lambda kind: "".join(ser(s, kind) for s in range(serien))  # noqa: E731
    v3 = '<c:view3D><c:rotX val="15"/><c:rotY val="20"/><c:rAngAx val="1"/></c:view3D>'
    if art in ("saeule", "balken", "gestapelt", "prozent"):
        grp = {"saeule": "clustered", "balken": "clustered", "gestapelt": "stacked", "prozent": "percentStacked"}[art]
        ueb = '<c:overlap val="100"/>' if grp != "clustered" else ""
        plot = f'<c:barChart><c:barDir val="{"bar" if art == "balken" else "col"}"/><c:grouping val="{grp}"/><c:varyColors val="0"/>{reihen("bar")}<c:gapWidth val="150"/>{ueb}{ax}</c:barChart>{cat_ax}{val_ax}'
        pre = ""
    elif art == "linie":
        plot = f'<c:lineChart><c:grouping val="standard"/><c:varyColors val="0"/>{reihen("line")}<c:marker val="1"/>{ax}</c:lineChart>{cat_ax}{val_ax}'
        pre = ""
    elif art == "flaeche":
        plot = f'<c:areaChart><c:grouping val="standard"/><c:varyColors val="0"/>{reihen("area")}{ax}</c:areaChart>{cat_ax}{val_ax}'
        pre = ""
    elif art == "kreis":
        plot = f'<c:pieChart><c:varyColors val="1"/>{ser(0, "pie")}<c:firstSliceAng val="0"/></c:pieChart>'
        pre = ""
    elif art == "ring":
        plot = f'<c:doughnutChart><c:varyColors val="1"/>{ser(0, "pie")}<c:firstSliceAng val="0"/><c:holeSize val="50"/></c:doughnutChart>'
        pre = ""
    elif art == "streu":
        plot = f'<c:scatterChart><c:scatterStyle val="lineMarker"/><c:varyColors val="0"/>{reihen("scatter")}{ax}</c:scatterChart>{xy_ax}'
        pre = ""
    elif art == "netz":
        plot = f'<c:radarChart><c:radarStyle val="marker"/><c:varyColors val="0"/>{reihen("line")}{ax}</c:radarChart>{cat_ax}{val_ax}'
        pre = ""
    elif art == "saeule3d":
        pre = v3
        plot = f'<c:bar3DChart><c:barDir val="col"/><c:grouping val="clustered"/><c:varyColors val="0"/>{reihen("bar")}<c:gapWidth val="150"/><c:shape val="box"/>{ax}<c:axId val="0"/></c:bar3DChart>{cat_ax}{val_ax}'
    else:            # kreis3d
        pre = v3
        plot = f'<c:pie3DChart><c:varyColors val="1"/>{ser(0, "pie")}</c:pie3DChart>'
    ti = f'<c:title><c:tx><c:rich><a:bodyPr/><a:p><a:pPr><a:defRPr/></a:pPr><a:r><a:rPr lang="de-DE"/><a:t>{e(titel)}</a:t></a:r></a:p></c:rich></c:tx><c:overlay val="0"/></c:title><c:autoTitleDeleted val="0"/>' if titel else '<c:autoTitleDeleted val="1"/>'
    leg = f'<c:legend><c:legendPos val="{legende}"/><c:overlay val="0"/></c:legend>' if legende else ""
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><c:chartSpace xmlns:c="{NS["c"]}" xmlns:a="{NS["a"]}" xmlns:r="{NS["r"]}"><c:roundedCorners val="0"/><c:chart>{ti}{pre}<c:plotArea><c:layout/>{plot}</c:plotArea>{leg}<c:plotVisOnly val="1"/><c:dispBlanksAs val="gap"/></c:chart></c:chartSpace>')


DIAGRAMMARTEN = ["saeule", "balken", "gestapelt", "prozent", "linie", "flaeche", "kreis", "ring", "streu", "netz", "saeule3d", "kreis3d"]


def k_diagramme(i, rng):
    d = Dok(rng)
    art = pick(DIAGRAMMARTEN, i)
    d.kern["beschreibung"] = f"Diagramm {art}"
    d.body.append(heading(f"Diagramm {art}"))
    n = d.diagramme = d.diagramme + 1
    pfad = f"charts/chart{n}.xml"
    d.teile["word/" + pfad] = (CT["chart"], diagramm_xml(art, rng, rng.choice(["", "Umsatz je Quartal", "Verteilung", "Messwerte"]), 1 if art in ("kreis", "ring", "kreis3d") else rng.randint(1, 3), pick(["", "r", "b", "t", "l"], i // 3), i % 2 == 0, i % 3 == 0 and art in ("saeule", "balken", "linie")).encode())
    rid = d.rel(RT + "chart", pfad)
    cx, cy = rng.choice([(120, 70), (90, 90), (150, 80)])
    cx, cy = cx * EMU_MM, cy * EMU_MM
    gr = f'<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart"><c:chart xmlns:c="{NS["c"]}" r:id="{rid}"/></a:graphicData></a:graphic>'
    if i % 2 == 0:
        dr = f'<w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{d.id()}" name="Diagramm" descr="{art}"/><wp:cNvGraphicFramePr/>{gr}</wp:inline></w:drawing>'
    else:
        dr = anker_xml(d, gr, cx, cy, UMFLUSS[7], ("column", "align", "center"), ("paragraph", "offset", 0), name="Diagramm")
    d.body.append(para(inhalt=run("", "", dr)))
    d.body.append(para(inhalt=run("Abbildung ") + feld("SEQ Abbildung \\* ARABIC", "1") + run(f": {art}"), ppr='<w:pStyle w:val="Caption"/>'))
    d.body.append(para(satz(rng, 2)))
    return d


# --------------------------------------------------------------------------------------------------------------------- Noten, Kommentare, Änderungen
def k_noten(i, rng):
    d = Dok(rng)
    art = i % 12
    d.kern["beschreibung"] = f"Notenart {art}"
    d.body.append(heading(f"Noten, Kommentare, Änderungen {art}"))
    aut = lambda n: f'w:id="{n}" w:author="{pick(["Anna", "Ben", "Cem"], n)}" w:date="2026-02-0{1 + n % 9}T10:{10 + n}:00Z"'  # noqa: E731
    if art == 0:     # Fußnoten
        for n in range(rng.randint(1, 6)):
            d.body.append(para(inhalt=run(satz(rng)) + d.fussnote(f"Fußnotentext {n + 1}. {satz(rng)}")))
    elif art == 1:   # Endnoten
        for n in range(rng.randint(1, 5)):
            d.body.append(para(inhalt=run(satz(rng)) + d.fussnote(f"Endnotentext {n + 1}.", endnote=True)))
    elif art == 2:   # beides, lange Fußnote, Format, mehrere Absätze
        inh = para("", '<w:pStyle w:val="FootnoteText"/>', inhalt='<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr><w:footnoteRef/></w:r>' + run(" Erster Absatz mit ") + run("Fett", RPR["fett"]) + run(" und ") + run("Kursiv", RPR["kursiv"])) + para(satz(rng, 6), '<w:pStyle w:val="FootnoteText"/>')
        d.body.append(para(inhalt=run("Lange Fußnote") + d.fussnote("", inhalt=inh)))
        d.body.append(para(inhalt=run("Endnote") + d.fussnote("Ende", endnote=True)))
        for n in range(15):
            d.body.append(para(inhalt=run(satz(rng, 3)) + (d.fussnote(f"Fußnote {n}") if n % 4 == 0 else "")))
    elif art == 3:   # eigene Marke, Nummernformat
        fmt = pick(["decimal", "lowerRoman", "upperLetter", "chicago", "decimalEnclosedCircle"], i)
        d.settings.append("")
        d.body.append(para(inhalt=run("Eigene Marke") + d.fussnote("mit Sternchen", marke="*")))
        d.body.append(para(inhalt=run("Normale Marke") + d.fussnote("normal")))
        d.sect = sect_xml(extra=f'<w:footnotePr><w:pos w:val="{pick(["pageBottom", "beneathText"], i)}"/><w:numFmt w:val="{fmt}"/><w:numRestart w:val="{pick(["continuous", "eachSect", "eachPage"], i)}"/></w:footnotePr><w:endnotePr><w:pos w:val="docEnd"/></w:endnotePr>')
    elif art == 4:   # Kommentare
        for n in range(rng.randint(1, 4)):
            nr, a, b, _ = d.kommentar(f"Kommentar {n + 1}: {satz(rng)}", pick(["Anna", "Ben", "Cem"], n))
            d.body.append(para(inhalt=run("Davor ") + a + run("kommentierter Text") + b + run(" danach.")))
    elif art == 5:   # Antworten, erledigt
        nr, a, b, pid = d.kommentar("Hauptkommentar", "Anna")
        d.kommentar("Antwort darauf", "Ben", antwort_auf=pid)
        d.kommentar("Zweite Antwort, erledigt", "Cem", antwort_auf=pid, erledigt=True)
        d.body.append(para(inhalt=run("Text ") + a + run("mit Diskussion") + b + '<w:commentRangeStart w:id="1"/><w:commentRangeEnd w:id="1"/><w:r><w:commentReference w:id="1"/></w:r><w:commentRangeStart w:id="2"/><w:commentRangeEnd w:id="2"/><w:r><w:commentReference w:id="2"/></w:r>'))
    elif art == 6:   # Kommentar über Absatz- und Tabellengrenzen
        nr, a, b, _ = d.kommentar("Über mehrere Absätze")
        d.body.append(para(inhalt=a + run(satz(rng))))
        d.body.append(einfache_tabelle(rng, 2, 2))
        d.body.append(para(inhalt=run(satz(rng)) + b))
    elif art == 7:   # Einfügungen/Löschungen
        d.settings.append("<w:trackRevisions/>")
        d.body.append(para(inhalt=run("Unverändert, ") + f'<w:ins {aut(1)}>{run("eingefügt, ", RPR["fett"])}</w:ins>' + f'<w:del {aut(2)}><w:r><w:delText xml:space="preserve">gelöscht, </w:delText></w:r></w:del>' + run("Ende.")))
        d.body.append(para(inhalt=f'<w:ins {aut(3)}>{run("Ganzer neuer Absatz")}</w:ins>', ppr=f'<w:rPr><w:ins {aut(4)}/></w:rPr>'))
        d.body.append(para(inhalt=f'<w:del {aut(5)}><w:r><w:delText>Ganzer gelöschter Absatz</w:delText></w:r></w:del>', ppr=f'<w:rPr><w:del {aut(6)}/></w:rPr>'))
    elif art == 8:   # Formatänderungen
        d.body.append(para(inhalt=f'<w:r><w:rPr><w:b/><w:rPrChange {aut(1)}><w:rPr/></w:rPrChange></w:rPr><w:t>Jetzt fett (vorher normal)</w:t></w:r>'))
        d.body.append(para("Absatz mit geänderter Ausrichtung", f'<w:jc w:val="center"/><w:pPrChange {aut(2)}><w:pPr/></w:pPrChange>'))
        d.body.append(tabelle([[zelle(para("Zelle"), breite=4500)]], [4500], f'<w:tblStyle w:val="TableGrid"/><w:tblPrChange {aut(3)}><w:tblPr/></w:tblPrChange>'))
        d.body.append(f'<w:p><w:pPr><w:sectPr>{sect_xml()}<w:sectPrChange {aut(4)}><w:sectPr/></w:sectPrChange></w:sectPr></w:pPr></w:p>')
    elif art == 9:   # Verschiebungen
        d.body.append(para(inhalt=f'<w:moveFromRangeStart w:id="1" w:name="move1" {aut(1).split(" ", 1)[1]}/><w:moveFrom {aut(2)}>{run("Verschobener Text")}</w:moveFrom><w:moveFromRangeEnd w:id="1"/>' + run(" Mitte ")))
        d.body.append(para(inhalt=f'<w:moveToRangeStart w:id="2" w:name="move1" {aut(3).split(" ", 1)[1]}/><w:moveTo {aut(4)}>{run("Verschobener Text")}</w:moveTo><w:moveToRangeEnd w:id="2"/>'))
    elif art == 10:  # Änderungen in Tabelle und Liste, eingefügte Zeile, gelöschte Zeile
        d.body.append(tabelle([[zelle(para(inhalt=f'<w:ins {aut(1)}>{run("neu")}</w:ins>'), breite=4500), zelle(para("alt"), breite=4500)], [zelle(para(inhalt=f'<w:del {aut(2)}><w:r><w:delText>weg</w:delText></w:r></w:del>'), breite=4500), zelle(para("alt"), breite=4500)]], [4500, 4500], '<w:tblStyle w:val="TableGrid"/>', {0: f'<w:ins {aut(3)}/>', 1: f'<w:del {aut(4)}/>'}))
    else:            # Bearbeitungsbereiche, Zeichenschutz
        d.body.append(para(inhalt=f'<w:permStart w:id="1" w:edGrp="everyone"/>{run("Bearbeitbarer Bereich")}<w:permEnd w:id="1"/>' + run(" geschützter Rest")))
        d.settings.append('<w:documentProtection w:edit="readOnly" w:enforcement="0"/>')
        d.body.append(para(inhalt='<w:proofErr w:type="spellStart"/>' + run("Rechtschreibfehlr") + '<w:proofErr w:type="spellEnd"/>' + '<w:smartTag w:uri="urn:schemas-microsoft-com:office:smarttags" w:element="place"><w:r><w:t>Berlin</w:t></w:r></w:smartTag>'))
    d.body.append(para(satz(rng)))
    return d


# --------------------------------------------------------------------------------------------------------------------- Inhaltssteuerelemente
def sdt(pr: str, inhalt: str, block=False, ende="") -> str:
    return f"<w:sdt><w:sdtPr>{pr}</w:sdtPr>{ende}<w:sdtContent>{inhalt}</w:sdtContent></w:sdt>"


def k_steuer(i, rng):
    d = Dok(rng)
    art = i % 12
    d.kern["beschreibung"] = f"Steuerelementart {art}"
    d.body.append(heading(f"Steuerelemente {art}"))
    pr = lambda t, a="Feld", extra="": f'<w:alias w:val="{a}"/><w:tag w:val="{t}"/><w:id w:val="{rng.randint(1000, 999999)}"/>{extra}'  # noqa: E731
    if art == 0:     # Text
        d.body.append(para(inhalt=run("Name: ") + sdt(pr("name", "Name", '<w:showingPlcHdr/><w:text/>'), run("Hier Namen eingeben", "<w:rStyle w:val=" + chr(34) + "PlaceholderText" + chr(34) + "/>" if False else "<w:color w:val=" + chr(34) + "808080" + chr(34) + "/>")), ))
        d.body.append(para(inhalt=sdt(pr("mehr", "Mehrzeilig", '<w:text w:multiLine="1"/>'), run("Zeile eins"))))
    elif art == 1:   # Auswahlliste
        d.body.append(para(inhalt=sdt(pr("land", "Land", '<w:dropDownList><w:listItem w:displayText="Deutschland" w:value="DE"/><w:listItem w:displayText="Österreich" w:value="AT"/><w:listItem w:displayText="Schweiz" w:value="CH"/></w:dropDownList>'), run("Österreich"))))
    elif art == 2:   # Kombinationsfeld
        d.body.append(para(inhalt=sdt(pr("farbe", "Farbe", '<w:comboBox><w:listItem w:displayText="Rot" w:value="r"/><w:listItem w:displayText="Grün" w:value="g"/></w:comboBox>'), run("Blau (frei eingegeben)"))))
    elif art == 3:   # Datum
        d.body.append(para(inhalt=sdt(pr("datum", "Datum", '<w:date w:fullDate="2026-02-20T00:00:00Z"><w:dateFormat w:val="dd.MM.yyyy"/><w:lid w:val="de-DE"/><w:storeMappedDataAs w:val="dateTime"/><w:calendar w:val="gregorian"/></w:date>'), run("20.02.2026"))))
    elif art == 4:   # Kontrollkästchen
        d.body.append(para(inhalt=sdt(pr("haken", "Haken", '<w14:checkbox><w14:checked w14:val="1"/><w14:checkedState w14:val="2612" w14:font="MS Gothic"/><w14:uncheckedState w14:val="2610" w14:font="MS Gothic"/></w14:checkbox>'), run("\u2612", '<w:rFonts w:ascii="MS Gothic" w:eastAsia="MS Gothic" w:hAnsi="MS Gothic" w:hint="eastAsia"/>')) + run(" Zugestimmt")))
        d.body.append(para(inhalt=sdt(pr("leer", "Leer", '<w14:checkbox><w14:checked w14:val="0"/><w14:checkedState w14:val="2612" w14:font="MS Gothic"/><w14:uncheckedState w14:val="2610" w14:font="MS Gothic"/></w14:checkbox>'), run("\u2610", '<w:rFonts w:ascii="MS Gothic" w:eastAsia="MS Gothic" w:hAnsi="MS Gothic" w:hint="eastAsia"/>')) + run(" Nicht angehakt")))
    elif art == 5:   # Block-Steuerelement mit Absätzen und Tabelle
        d.body.append(sdt(pr("block", "Block", "<w:richText/>"), para("Absatz im Block") + einfache_tabelle(rng, 2, 2) + para("Nach der Tabelle")))
    elif art == 6:   # Bild- und Bausteinauswahl
        rid = d.bild(png(20, 20, (100, 100, 200)))
        d.body.append(para(inhalt=sdt(pr("bild", "Bild", "<w:picture/>"), run("", "", inline_bild(d, rid, 20, 20, 40 * EMU_PX, 40 * EMU_PX)))))
        d.body.append(sdt(pr("baustein", "Baustein", '<w:docPartObj><w:docPartGallery w:val="Cover Pages"/><w:docPartUnique/></w:docPartObj>'), para("Deckblatt-Baustein", '<w:pStyle w:val="Title"/>') + para("Untertitel", '<w:pStyle w:val="Subtitle"/>')))
    elif art == 7:   # geschachtelt, gesperrt
        d.body.append(para(inhalt=sdt(pr("aussen", "Außen", '<w:lock w:val="sdtLocked"/>'), run("Außen: ") + sdt(pr("innen", "Innen", '<w:lock w:val="contentLocked"/><w:text/>'), run("Innen")))))
    elif art == 8:   # Datenbindung
        d.custom_xml = True
        d.body.append(para(inhalt=sdt(pr("bind", "Gebunden", '<w:dataBinding w:prefixMappings="xmlns:ns0=&quot;urn:lunivo:test&quot;" w:xpath="/ns0:daten/ns0:feld" w:storeItemID="{00000000-0000-0000-0000-000000000001}"/><w:text/>'), run("Wert"))))
    elif art == 9:   # Inhaltsverzeichnis als Baustein
        d.body.append(sdt(pr("vz", "Verzeichnis", '<w:docPartObj><w:docPartGallery w:val="Table of Contents"/><w:docPartUnique/></w:docPartObj>'), para("Inhalt", '<w:pStyle w:val="TOCHeading"/>') + para(inhalt=feld('TOC \\o "1-3" \\h \\z \\u', "Eintrag"), ppr='<w:pStyle w:val="TOC1"/>')))
    elif art == 10:  # Wiederholungsabschnitt
        d.body.append(sdt(pr("rep", "Wiederholung", '<w15:repeatingSection><w15:sectionTitle w15:val="Posten"/></w15:repeatingSection>'), sdt(pr("posten", "Posten", "<w15:repeatingSectionItem/>"), para("Posten 1") + para("Details"))))
    else:            # Formularfelder alter Art (ffData)
        ff_text = '<w:fldChar w:fldCharType="begin"><w:ffData><w:name w:val="Text1"/><w:enabled/><w:calcOnExit w:val="0"/><w:textInput><w:default w:val="Vorgabe"/><w:maxLength w:val="20"/></w:textInput></w:ffData></w:fldChar>'
        ff_box = '<w:fldChar w:fldCharType="begin"><w:ffData><w:name w:val="Kontroll1"/><w:enabled/><w:calcOnExit w:val="0"/><w:checkBox><w:sizeAuto/><w:default w:val="1"/></w:checkBox></w:ffData></w:fldChar>'
        ff_dd = '<w:fldChar w:fldCharType="begin"><w:ffData><w:name w:val="Auswahl1"/><w:enabled/><w:calcOnExit w:val="0"/><w:ddList><w:result w:val="1"/><w:listEntry w:val="Eins"/><w:listEntry w:val="Zwei"/></w:ddList></w:ffData></w:fldChar>'
        for kopf, inst, erg in ((ff_text, "FORMTEXT", "Vorgabe"), (ff_box, "FORMCHECKBOX", ""), (ff_dd, "FORMDROPDOWN", "")):
            d.body.append(para(inhalt=f'<w:r>{kopf}</w:r><w:r><w:instrText xml:space="preserve"> {inst} </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r>{run(erg) if erg else ""}<w:r><w:fldChar w:fldCharType="end"/></w:r>'))
    d.body.append(para(satz(rng)))
    return d


# --------------------------------------------------------------------------------------------------------------------- Sprachen, Schriften, Sonderzeichen
TEXTE = {
    "deutsch": "Größenwahnsinnige Übeltäter müssen äußerst überlegt handeln. Fußgängerübergang, Käse, Ölfässer.",
    "franzoesisch": "Où êtes-vous allé après l'été ? Ça m'étonne : œuvre, garçon, naïve, déjà vu.",
    "spanisch": "¿Cómo está usted? ¡Qué sorpresa! El niño comió piñas y añadió ñoquis.",
    "polnisch": "Zażółć gęślą jaźń. Łódź, ćma, śnieg, żółw.",
    "tschechisch": "Příliš žluťoučký kůň úpěl ďábelské ódy.",
    "ungarisch": "Árvíztűrő tükörfúrógép. Őszi műsor.",
    "tuerkisch": "Pijamalı hasta yağız şoföre çabucak güvendi. İstanbul, ığdır.",
    "griechisch": "Ξεσκεπάζω την ψυχοφθόρα βδελυγμία. Αθήνα, Ελλάδα.",
    "russisch": "Съешь же ещё этих мягких французских булок, да выпей чаю. Москва.",
    "bulgarisch": "Бъркотия, щъркел, жълтъци.",
    "arabisch": "نص عربي للاختبار: مرحبا بالعالم، هذا اختبار للكتابة من اليمين إلى اليسار 123.",
    "hebraeisch": "טקסט בעברית לבדיקה: שלום עולם, בדיקה מימין לשמאל 456.",
    "persisch": "این یک متن آزمایشی فارسی است: سلام دنیا.",
    "chinesisch": "快速的棕色狐狸跳过了懒狗。这是一个测试文档，包含中文字符和标点符号。",
    "japanisch": "いろはにほへと ちりぬるを。日本語のテスト文書です。カタカナもあります。漢字仮名交じり文。",
    "koreanisch": "다람쥐 헌 쳇바퀴에 타고파. 한국어 시험 문서입니다.",
    "thai": "เป็นมนุษย์สุดประเสริฐเลิศคุณค่า กว่าบรรดาฝูงสัตว์เดรัจฉาน",
    "hindi": "यह हिंदी में एक परीक्षण दस्तावेज़ है। नमस्ते दुनिया।",
    "tamil": "தமிழ் மொழி சோதனை ஆவணம்.",
    "vietnamesisch": "Tôi có thể ăn thủy tinh mà không hại gì. Việt Nam, Hà Nội.",
    "emoji": "Emoji: 😀 🎉 👍🏽 👨‍👩‍👧‍👦 🇩🇪 ❤️ ✅ 🚀 und Zeichen außerhalb der BMP: 𝔘𝔫𝔦𝔠𝔬𝔡𝔢 𠜎 🜂.",
    "mathe": "Symbole: ∑ ∏ ∫ ∂ ∇ ∞ ≈ ≠ ≤ ≥ ± × ÷ √ ∈ ∉ ⊂ ⊃ ∪ ∩ ℝ ℕ ℤ α β γ π Ω – — … ‰ € £ ¥ © ® ™ § ¶ † ‡ • ° µ",
    "kombiniert": "Kombinierende Zeichen: e\u0301 a\u0308 o\u0302 n\u0303 u\u030a und a\u0323\u0302; Hangul: 한글; Ligaturen: ﬁ ﬂ ﬃ; Bruchzahlen: ⅓ ⅔ ⅛; hochgestellt: x² y³ H₂O.",
    "unsichtbar": "Mit\u200bNullbreite\u200cTrenner\u200dVerbinder\u2060Wortverbinder\u00adWeichesTrennzeichen und \u00a0geschütztes\u00a0Leerzeichen sowie \u2003Geviert und \u2009Schmalraum.",
}


def k_sprachen(i, rng):
    d = Dok(rng)
    art = i % 10
    namen = list(TEXTE)
    n1 = pick(namen, i)
    d.kern["beschreibung"] = f"Sprachart {art} / {n1}"
    d.body.append(heading(f"Sprachen und Zeichen {art}: {n1}"))
    rtl = n1 in ("arabisch", "hebraeisch", "persisch")
    cjk = n1 in ("chinesisch", "japanisch", "koreanisch")
    lang = {"deutsch": "de-DE", "franzoesisch": "fr-FR", "spanisch": "es-ES", "russisch": "ru-RU", "arabisch": "ar-SA", "hebraeisch": "he-IL", "chinesisch": "zh-CN", "japanisch": "ja-JP", "koreanisch": "ko-KR", "thai": "th-TH", "hindi": "hi-IN"}.get(n1, "en-US")
    if art == 0:     # Absatz mit Sprache
        rpr = f'<w:lang w:val="{lang}" w:eastAsia="{lang}" w:bidi="{lang}"/>' + ("<w:rtl/>" if rtl else "")
        d.body.append(para(TEXTE[n1], ('<w:bidi/><w:jc w:val="left"/>' if rtl else ""), ordne([rpr, '<w:rFonts w:eastAsia="MS Mincho" w:cs="Arial"/>'], RPR_ORDER)))
    elif art == 1:   # Mischung in einem Absatz
        d.body.append(para(inhalt=run(TEXTE["deutsch"][:40] + " ") + run(TEXTE[pick(namen, i + 3)], '<w:rtl/>' if rtl else "") + run(" " + TEXTE["mathe"][:30]) + run(" " + TEXTE["emoji"][:20])))
    elif art == 2:   # Sonderelemente
        d.body.append(para(inhalt=run("A") + '<w:r><w:tab/></w:r>' + run("B") + '<w:r><w:br/></w:r>' + run("C") + '<w:r><w:br w:type="page"/></w:r>' + run("D") + '<w:r><w:br w:type="column"/></w:r>' + run("E") + '<w:r><w:br w:type="textWrapping" w:clear="all"/></w:r>' + run("F") + '<w:r><w:cr/></w:r>' + run("G")))
        d.body.append(para(inhalt=run("Trenn") + '<w:r><w:noBreakHyphen/></w:r>' + run("strich, weiches") + '<w:r><w:softHyphen/></w:r>' + run("Trennzeichen, Symbol ") + '<w:r><w:sym w:font="Wingdings" w:char="F04A"/></w:r>' + '<w:r><w:ptab w:relativeTo="margin" w:alignment="right" w:leader="none"/></w:r>' + run("rechts") + '<w:r><w:lastRenderedPageBreak/></w:r>' + run(" Ende")))
    elif art == 3:   # Ostasiatisch: Ruby, vertikal
        d.body.append(para(inhalt='<w:r><w:ruby><w:rubyPr><w:rubyAlign w:val="distributeSpace"/><w:hps w:val="10"/><w:hpsRaise w:val="18"/><w:hpsBaseText w:val="21"/><w:lid w:val="ja-JP"/></w:rubyPr><w:rt><w:r><w:t>かんじ</w:t></w:r></w:rt><w:rubyBase><w:r><w:t>漢字</w:t></w:r></w:rubyBase></w:ruby></w:r>' + run(" Ruby-Text ")))
        d.body.append(para(TEXTE["japanisch"], '<w:kinsoku w:val="1"/><w:wordWrap w:val="0"/><w:overflowPunct/><w:textDirection w:val="tbRlV"/>', '<w:rFonts w:eastAsia="MS Gothic"/><w:eastAsianLayout w:id="1" w:combine="1"/>'))
    elif art == 4:   # Schriftarten je Schriftart-Klasse
        d.body.append(para(inhalt="".join(run(f"{f}: Hamburgefonstiv 0123 ÄÖÜ ", f'<w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:cs="{f}" w:eastAsia="{f}"/>') for f in SCHRIFTEN)))
    elif art == 5:   # lange Wörter und Zeilen ohne Umbruchstelle
        d.body.append(para("Donaudampfschifffahrtsgesellschaftskapitänsmützenabzeichenhersteller" * 3))
        d.body.append(para("x" * 600))
        d.body.append(para("https://example.org/ein/sehr/langer/pfad/ohne/leerzeichen/" * 8))
        d.body.append(para(" ".join(["wort"] * 400)))
    elif art == 6:   # Rechts-nach-links-Absätze
        d.body.append(para(TEXTE["arabisch"], '<w:bidi/>', "<w:rtl/>"))
        d.body.append(para(TEXTE["hebraeisch"], '<w:bidi/><w:jc w:val="right"/>', "<w:rtl/>"))
        d.body.append(para(inhalt=run("Links ") + run(TEXTE["arabisch"][:20], "<w:rtl/>") + run(" 123 ") + run("wieder links"), ppr='<w:bidi/>'))
    elif art == 7:   # Zeichen in Tabelle und Liste
        d.body.append(tabelle([[zelle(para(TEXTE[n]), breite=4500) for n in (pick(namen, i + k), pick(namen, i + k + 5))] for k in range(3)], [4500, 4500], '<w:tblStyle w:val="TableGrid"/>'))
    elif art == 8:   # Steuerzeichen und Grenzfälle in w:t
        d.body.append(para(inhalt=f'<w:r><w:t xml:space="preserve">  führende und nachfolgende Leerzeichen  </w:t></w:r><w:r><w:t>   ohne Erhaltung   </w:t></w:r><w:r><w:t xml:space="preserve">&lt;&amp;&gt; &quot; &apos; &#9731; &#x1F600;</w:t></w:r>'))
        d.body.append(para("Tab\tin\tText und Zeilen\numbruch im Text"))
        d.body.append(para(""))
        d.body.append(para(" "))
    else:            # alle Sprachen nacheinander
        for n in namen:
            d.body.append(para(f"{n}: {TEXTE[n]}", '<w:bidi/>' if n in ("arabisch", "hebraeisch", "persisch") else ""))
    d.body.append(para(satz(rng)))
    return d


# --------------------------------------------------------------------------------------------------------------------- Metadaten und Einstellungen
def k_meta(i, rng):
    d = Dok(rng)
    art = i % 6
    d.kern.update({"titel": rng.choice(["Jahresbericht", "Protokoll", "Entwurf", "Ä-Ö-Ü Größe", ""]), "autor": rng.choice(["Anna Muster", "Test & Co <Autor>", "", "Ünïcödé Ñame"]), "betreff": "Thema", "stichwort": "a; b; c", "beschreibung": f"Metadatenart {art}"})
    d.body.append(para(d.kern["titel"] or "Ohne Titel", '<w:pStyle w:val="Title"/>'))
    text_absaetze(d, 3)
    if art == 0:
        d.app_extra = "<Template>Normal.dotm</Template><TotalTime>12</TotalTime><Pages>1</Pages><Words>100</Words><Characters>600</Characters><Company>Beispiel AG</Company><Lines>5</Lines><Paragraphs>3</Paragraphs>"
        d.eigene = [("Projekt", "lpwstr", "Lunivo"), ("Nummer", "i4", "42"), ("Betrag", "r8", "3.14"), ("Frei", "bool", "true")]
    elif art == 1:
        d.settings += [f'<w:zoom w:percent="{rng.choice([50, 75, 100, 150, 400])}"/>' if i % 2 else '<w:zoom w:val="bestFit" w:percent="100"/>', f'<w:defaultTabStop w:val="{rng.choice([360, 708, 1134])}"/>', "<w:autoHyphenation/>", '<w:consecutiveHyphenLimit w:val="2"/>', '<w:hyphenationZone w:val="425"/>', "<w:doNotHyphenateCaps/>"]
    elif art == 2:
        d.settings += [f'<w:compat><w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="{pick([11, 12, 14, 15], i)}"/><w:useFELayout/><w:doNotExpandShiftReturn/></w:compat>', '<w:characterSpacingControl w:val="compressPunctuation"/>']
    elif art == 3:
        d.docvars = ""
        d.settings += ['<w:docVars><w:docVar w:name="Projekt" w:val="Lunivo"/><w:docVar w:name="Stand" w:val="2026"/></w:docVars>', '<w:themeFontLang w:val="de-DE" w:eastAsia="ja-JP" w:bidi="ar-SA"/>', '<w:decimalSymbol w:val=","/>', '<w:listSeparator w:val=";"/>']
    elif art == 4:
        d.theme = False
        d.body.append(para("Ohne Theme-Teil, Schrift aus docDefaults"))
    else:
        d.settings.append('<w:documentProtection w:edit="forms" w:enforcement="0" w:cryptProviderType="rsaAES" w:cryptAlgorithmClass="hash" w:cryptAlgorithmType="typeAny" w:cryptAlgorithmSid="14" w:cryptSpinCount="100000" w:hash="AAAA" w:salt="BBBB"/>')
        d.settings.append('<w:writeProtection w:recommended="1"/>')
    return d


# --------------------------------------------------------------------------------------------------------------------- Grenzfälle
def k_grenz(i, rng):
    d = Dok(rng)
    art = i % 20
    d.kern["beschreibung"] = f"Grenzfall {art}"
    if art == 0:
        pass                                                   # leerer Textkörper (nur sectPr)
    elif art == 1:
        d.body.append(para())
    elif art == 2:
        for _ in range(3000):
            d.body.append(para(satz(rng)))
    elif art == 3:
        d.body.append(einfache_tabelle(rng, 400, 4, kopf=True))
        d.body.append(para())
    elif art == 4:   # verschachtelte Tabellen, 12 Ebenen
        inner = para("Innerste Zelle")
        for n in range(12):
            inner = tabelle([[zelle(inner + para(f"Ebene {12 - n}"), breite=9000 - n * 300)]], [9000 - n * 300], '<w:tblStyle w:val="TableGrid"/>')
        d.body.append(inner)
        d.body.append(para())
    elif art == 5:   # unbekannte Elemente und Namensräume
        d.body.append(para(inhalt=run("Text") + '<w:unbekannt w:x="1"><w:kind/></w:unbekannt>' + '<x:fremd xmlns:x="urn:fremd">Inhalt</x:fremd>' + run("weiter")))
        d.body.append(f'<w:p><w:pPr><w:unbekanntePr w:val="1"/></w:pPr>{run("Absatz mit unbekannter Eigenschaft")}</w:p>')
    elif art == 6:   # AlternateContent mit unbekannter Voraussetzung
        d.body.append(para(inhalt='<mc:AlternateContent><mc:Choice Requires="zzz" xmlns:zzz="urn:zukunft"><w:r><w:t>Zukunftsinhalt</w:t></w:r></mc:Choice><mc:Fallback><w:r><w:t>Rückfallinhalt</w:t></w:r></mc:Fallback></mc:AlternateContent>'))
    elif art == 7:
        d.ohne_stile = True
        d.body.append(para("Ohne styles.xml", '<w:pStyle w:val="Heading1"/>'))
    elif art == 8:
        d.ohne_nummerierung = True
        d.num_abs.append("<x/>")
        d.body.append(para("Nummer ohne numbering.xml", '<w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'))
    elif art == 9:   # sehr langer Absatz
        d.body.append(para(" ".join(rng.choice(SAETZE) for _ in range(1500))))
    elif art == 10:  # doppelte Kennungen
        d.body.append(para(inhalt=f'<w:bookmarkStart w:id="1" w:name="A"/>{run("a")}<w:bookmarkEnd w:id="1"/><w:bookmarkStart w:id="1" w:name="A"/>{run("doppelt")}<w:bookmarkEnd w:id="1"/>'))
        d.stile.append('<w:style w:type="paragraph" w:customStyle="1" w:styleId="Dopp"><w:name w:val="Dopp"/></w:style><w:style w:type="paragraph" w:customStyle="1" w:styleId="Dopp"><w:name w:val="Dopp"/><w:rPr><w:b/></w:rPr></w:style>')
        d.body.append(para("Doppelte Vorlage", '<w:pStyle w:val="Dopp"/>'))
    elif art == 11:  # Extrem­werte in Maßen
        d.body.append(para("Riesige Schrift und Einzüge", '<w:ind w:left="30000" w:right="-9000" w:firstLine="99999"/><w:spacing w:before="40000" w:after="40000"/>', '<w:sz w:val="1638"/>'))
        d.body.append(para("Winzige Schrift", "", '<w:sz w:val="2"/>'))
        d.body.append(para("Negative Zeichenbreite", "", '<w:w w:val="-50"/><w:spacing w:val="-3000"/>'))
    elif art == 12:  # Tabulatoren, Spalten und Absatzränder in großer Zahl
        d.body.append(para("a\tb\tc\td\te\tf", '<w:tabs>' + "".join(f'<w:tab w:val="left" w:pos="{300 * k}"/>' for k in range(1, 101)) + '</w:tabs>'))
        d.sect = sect_xml(spalten='<w:cols w:num="45" w:space="20"/>')
    elif art == 13:  # nur Tabelle, ohne Absatz danach; Tabelle ohne Zeilen
        d.body.append(einfache_tabelle(rng, 2, 2))
        d.sect = sect_xml()
    elif art == 14:  # Tabelle mit uneinheitlichen Zeilen (fehlende Zellen), Gitter stimmt nicht
        d.body.append(tabelle([[zelle(para("a"), breite=3000), zelle(para("b"), breite=3000), zelle(para("c"), breite=3000)], [zelle(para("nur eine"), breite=3000)], [zelle(para("a"), breite=1000), zelle(para("b"), breite=1000), zelle(para("c"), breite=1000), zelle(para("d"), breite=1000), zelle(para("e"), breite=1000)]], [3000, 3000], '<w:tblStyle w:val="TableGrid"/>'))
        d.body.append(para())
    elif art == 15:  # Zelle ohne Absatz, Tabelle in Textfeld in Tabelle
        d.body.append(tabelle([[ "<w:tc><w:tcPr><w:tcW w:w=\"4500\" w:type=\"dxa\"/></w:tcPr></w:tc>", zelle(para("ok"), breite=4500)]], [4500, 4500], '<w:tblStyle w:val="TableGrid"/>'))
        d.body.append(para())
    elif art == 16:  # altChunk (eingebettetes HTML)
        d.teile["word/afchunk1.html"] = ("text/html", "<html><body><h1>Eingebettet</h1><p>HTML-Inhalt</p></body></html>".encode())
        rid = d.rel(RT + "aFChunk", "afchunk1.html")
        d.body.append(para("Vor dem altChunk"))
        d.body.append(f'<w:altChunk r:id="{rid}"/>')
        d.body.append(para("Nach dem altChunk"))
    elif art == 17:  # Zähler gemischt: alle Elemente in einem Dokument
        d.body.append(heading("Alles in einem"))
        d.body.append(einfache_tabelle(rng, 2, 2))
        d.body.append(para(inhalt=run("Text") + d.fussnote("Note") + feld("PAGE", "1")))
        d.body.append(para(inhalt=run("", "", inline_bild(d, d.bild(png(10, 10, (255, 0, 0))), 10, 10, 30 * EMU_PX, 30 * EMU_PX))))
    elif art == 18:  # reine Abschnittsfolge ohne Text
        for n in range(5):
            d.body.append(f'<w:p><w:pPr><w:sectPr>{sect_xml(quer=n % 2 == 1, typ="nextPage")}</w:sectPr></w:pPr></w:p>')
    else:            # Änderungsverfolgung an + Kommentar + Feld in Kopfzeile gleichzeitig
        d.settings.append("<w:trackRevisions/>")
        nr, a, b, _ = d.kommentar("Kommentar")
        d.body.append(para(inhalt=a + f'<w:ins w:id="1" w:author="X" w:date="2026-01-01T00:00:00Z">{run("neu ")}</w:ins>' + run("alt") + b))
        d.sect = sect_xml(refs=d.kopf_fuss("footer", para(inhalt=feld("PAGE", "1"))).join(['<w:footerReference w:type="default" r:id="', '"/>']))
    return d


# --------------------------------------------------------------------------------------------------------------------- Praxisdokumente
def k_real(i, rng):
    d = Dok(rng)
    art = i % 10
    d.defaults["schrift"] = pick(["Calibri", "Arial", "Times New Roman", "Cambria"], i)
    d.defaults["groesse"] = pick([20, 22, 24], i)
    d.kern.update({"titel": f"Praxisdokument {art}", "beschreibung": f"Praxis {art}"})
    fuss = d.kopf_fuss("footer", para(inhalt=run("Seite ") + feld("PAGE", "1") + run(" von ") + feld("NUMPAGES", "2"), ppr='<w:pStyle w:val="Footer"/><w:jc w:val="center"/>'))
    refs = f'<w:footerReference w:type="default" r:id="{fuss}"/>'
    if art == 0:     # Geschäftsbrief
        d.body += [para("Beispiel GmbH · Musterstraße 1 · 12345 Musterstadt", "", "<w:sz w:val=\"16\"/>"), para("Frau\nMax Mustermann".replace("\n", " ")), para("Musterweg 5"), para("54321 Beispielort"), para("", '<w:spacing w:after="600"/>'),
                   para("Musterstadt, 20. Februar 2026", '<w:jc w:val="right"/>'), para("Betreff: Ihre Anfrage", "", RPR["fett"])]
        d.body += [para("Sehr geehrte Frau Mustermann,")] + [para(satz(rng, 3), '<w:jc w:val="both"/>') for _ in range(3)] + [para("Mit freundlichen Grüßen"), para("", '<w:spacing w:after="720"/>'), para("Erika Beispiel")]
    elif art == 1:   # Bericht mit Verzeichnis
        d.body.append(para("Jahresbericht", '<w:pStyle w:val="Title"/>'))
        d.body.append(para("Inhaltsverzeichnis", '<w:pStyle w:val="TOCHeading"/>'))
        d.body.append(para(inhalt=feld('TOC \\o "1-3" \\h \\z \\u', "Inhaltsverzeichnis (zu aktualisieren)")))
        for n in range(1, 5):
            d.body.append(para(inhalt='<w:r><w:br w:type="page"/></w:r>'))
            d.body.append(heading(f"Kapitel {n}"))
            for m in range(1, 3):
                d.body.append(heading(f"Abschnitt {n}.{m}", 2))
                d.body.append(para(satz(rng, 5), '<w:jc w:val="both"/>'))
                if m == 1:
                    d.body.append(para(inhalt=run(satz(rng)) + d.fussnote(satz(rng))))
    elif art == 2:   # Vertrag mit Klauseln
        d.num_abs.append('<w:abstractNum w:abstractNumId="0"><w:multiLevelType w:val="multilevel"/><w:lvl w:ilvl="0"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="§ %1"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="0" w:firstLine="0"/><w:jc w:val="center"/></w:pPr><w:rPr><w:b/></w:rPr></w:lvl><w:lvl w:ilvl="1"><w:start w:val="1"/><w:numFmt w:val="decimal"/><w:lvlText w:val="(%2)"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="567" w:hanging="567"/></w:pPr></w:lvl><w:lvl w:ilvl="2"><w:start w:val="1"/><w:numFmt w:val="lowerLetter"/><w:lvlText w:val="%3)"/><w:lvlJc w:val="left"/><w:pPr><w:ind w:left="1134" w:hanging="567"/></w:pPr></w:lvl></w:abstractNum>')
        d.num.append('<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num>')
        d.body.append(para("Dienstleistungsvertrag", '<w:pStyle w:val="Title"/><w:jc w:val="center"/>'))
        for n in range(4):
            d.body.append(para(["Gegenstand", "Vergütung", "Laufzeit", "Schlussbestimmungen"][n], '<w:keepNext/><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr>'))
            for m in range(3):
                d.body.append(para(satz(rng, 2), '<w:jc w:val="both"/><w:numPr><w:ilvl w:val="1"/><w:numId w:val="1"/></w:numPr>'))
                if m == 1:
                    d.body.append(para(satz(rng), '<w:numPr><w:ilvl w:val="2"/><w:numId w:val="1"/></w:numPr>'))
        d.body.append(tabelle([[zelle(para("\n\n______________\nAuftraggeber".replace("\n", " ")), breite=4500), zelle(para("______________ Auftragnehmer"), breite=4500)]], [4500, 4500], '<w:tblW w:w="9000" w:type="dxa"/>'))
    elif art == 3:   # Rechnung
        pos = [("Beratung", 10, 95.0), ("Entwicklung", 24, 110.0), ("Reisekosten", 1, 230.5)]
        zl = [[zelle(para(t, "", RPR["fett"]), '<w:shd w:val="clear" w:color="auto" w:fill="D9E2F3"/>', 3000 if k == 0 else 1500) for k, t in enumerate(["Leistung", "Menge", "Einzelpreis", "Summe"])]]
        for t, m, p in pos:
            zl.append([zelle(para(t), breite=3000), zelle(para(str(m), '<w:jc w:val="right"/>'), breite=1500), zelle(para(f"{p:.2f} €".replace(".", ","), '<w:jc w:val="right"/>'), breite=1500), zelle(para(f"{m * p:.2f} €".replace(".", ","), '<w:jc w:val="right"/>'), breite=1500)])
        d.body += [para("Rechnung Nr. 2026-0042", '<w:pStyle w:val="Heading1"/>'), tabelle(zl, [3000, 1500, 1500, 1500], '<w:tblStyle w:val="TableGrid"/><w:tblW w:w="7500" w:type="dxa"/>'), para("Gesamtbetrag: 4.063,50 €", '<w:jc w:val="right"/>', RPR["fett"])]
    elif art == 4:   # Lebenslauf zweispaltig
        d.sect = sect_xml(refs=refs, spalten='<w:cols w:num="2" w:space="567" w:sep="1"/>')
        d.body.append(para("Erika Beispiel", '<w:pStyle w:val="Title"/>'))
        for t in ("Berufserfahrung", "Ausbildung", "Kenntnisse"):
            d.body.append(heading(t, 2))
            for _ in range(3):
                d.body.append(para(satz(rng), '<w:ind w:left="284" w:hanging="284"/>'))
    elif art == 5:   # Protokoll mit Kommentaren und Änderungen
        d.body.append(heading("Protokoll der Sitzung"))
        for n in range(4):
            nr, a, b, _ = d.kommentar(f"Rückfrage {n + 1}")
            d.body.append(para(inhalt=run(f"TOP {n + 1}: ") + a + run(satz(rng)) + b + f'<w:ins w:id="{50 + n}" w:author="Ben" w:date="2026-02-1{n}T09:00:00Z">{run(" Nachtrag.")}</w:ins>'))
    elif art == 6:   # Abschlussarbeit mit Fußnoten und Abbildungen
        d.body.append(para("Abschlussarbeit", '<w:pStyle w:val="Title"/>'))
        for n in range(1, 4):
            d.body.append(heading(f"Kapitel {n}"))
            d.body.append(para(inhalt=run(satz(rng, 3)) + d.fussnote(f"Quelle {n}: Muster, 20{20 + n}.") + run(satz(rng))))
            rid = d.bild(png(40, 24, tuple(rng.randint(40, 200) for _ in range(3)), n % 3))
            d.body.append(para(inhalt=run("", "", inline_bild(d, rid, 40, 24, 80 * EMU_PX, 48 * EMU_PX, f"Abb {n}", "Beispielgrafik")), ppr='<w:keepNext/><w:jc w:val="center"/>'))
            d.body.append(para(inhalt=run("Abbildung ") + feld("SEQ Abbildung \\* ARABIC", str(n)) + run(": Beispiel"), ppr='<w:pStyle w:val="Caption"/><w:jc w:val="center"/>'))
        d.body.append(heading("Literatur"))
        for n in range(4):
            d.body.append(para(f"Muster, M. ({2018 + n}): Titel des Werks {n}. Verlag, Ort.", '<w:ind w:left="567" w:hanging="567"/>'))
    elif art == 7:   # Newsletter mit Spalten, Bild, Textfeld
        d.sect = sect_xml(refs=refs, spalten='<w:cols w:num="3" w:space="360"/>')
        d.body.append(para("Newsletter", '<w:pStyle w:val="Title"/>'))
        rid = d.bild(png(40, 30, (200, 120, 40), 2))
        d.body.append(para(inhalt=run("", "", anker_xml(d, grafik_bild(d, rid, 1400000, 1000000), 1400000, 1000000, UMFLUSS[1], ("column", "align", "left"), ("paragraph", "offset", 0))) + run(satz(rng, 6))))
        for _ in range(6):
            d.body.append(para(satz(rng, 4), '<w:jc w:val="both"/>'))
    elif art == 8:   # Formular
        d.body.append(heading("Antragsformular"))
        for n, t in enumerate(["Name", "Straße", "Ort"]):
            d.body.append(para(inhalt=run(f"{t}: ") + sdt(f'<w:alias w:val="{t}"/><w:tag w:val="{t.lower()}"/><w:id w:val="{4000 + n}"/><w:text/>', run(f"{t} eingeben", "<w:color w:val=\"808080\"/>"))))
        d.body.append(para(inhalt=sdt('<w:alias w:val="Art"/><w:tag w:val="art"/><w:id w:val="4100"/><w:dropDownList><w:listItem w:displayText="Neu" w:value="n"/><w:listItem w:displayText="Änderung" w:value="a"/></w:dropDownList>', run("Neu"))))
        d.body.append(para(inhalt=sdt('<w:alias w:val="Ok"/><w:tag w:val="ok"/><w:id w:val="4101"/><w14:checkbox><w14:checked w14:val="0"/><w14:checkedState w14:val="2612" w14:font="MS Gothic"/><w14:uncheckedState w14:val="2610" w14:font="MS Gothic"/></w14:checkbox>', run("\u2610", '<w:rFonts w:ascii="MS Gothic" w:eastAsia="MS Gothic" w:hAnsi="MS Gothic"/>')) + run(" Einverstanden")))
    else:            # Merkblatt mit Rahmen, Hintergrund, Symbolen
        d.body.append(para("Wichtig!", '<w:pBdr><w:top w:val="single" w:sz="12" w:space="4" w:color="C00000"/><w:left w:val="single" w:sz="12" w:space="4" w:color="C00000"/><w:bottom w:val="single" w:sz="12" w:space="4" w:color="C00000"/><w:right w:val="single" w:sz="12" w:space="4" w:color="C00000"/></w:pBdr><w:shd w:val="clear" w:color="auto" w:fill="FDE9E9"/><w:jc w:val="center"/>', RPR["fett"] + '<w:sz w:val="36"/>'))
        for n in range(5):
            d.body.append(para(satz(rng, 2), '<w:ind w:left="567" w:hanging="283"/>'))
    if art not in (4, 7):
        d.sect = sect_xml(refs=refs)
    return d


# --------------------------------------------------------------------------------------------------------------------- Sammlung
KATEGORIEN = [
    ("absatz", 90, k_absatz, "Absatzformat: Ausrichtung, Einzug, Abstand, Zeilenabstand, Tabulatoren, Rahmen, Schattierung, Gliederung, Rahmenabsätze"),
    ("zeichen", 80, k_zeichen, "Zeichenformat: Auszeichnungen, Unterstreichungen, Farben, Größen, Schriften, Effekte (w14), Sprache"),
    ("vorlagen", 70, k_vorlagen, "Formatvorlagen: Vererbung, verknüpfte Zeichenvorlagen, Überschriften, Tabellenvorlagen, Nummerierung, fehlende Vorlagen"),
    ("listen", 90, k_listen, "Aufzählungen und Nummerierung: Formate, Mehrebenen, Neustart, Überschreibung, Zeichenformate"),
    ("tabellen", 110, k_tabelle, "Tabellen: Verbünde, Rahmen, Schattierung, Breiten, Verschachtelung, Kopfzeilen, Umfluss, Sonderfälle"),
    ("seite", 70, k_seite, "Seite und Abschnitte: Papier, Ränder, Spalten, Abschnittsumbrüche, Zeilennummern, Seitenrahmen, Hintergrund"),
    ("kopffuss", 50, k_kopffuss, "Kopf- und Fußzeilen: Standard, erste, gerade/ungerade, Felder, Tabellen, Bilder, je Abschnitt"),
    ("felder", 60, k_felder, "Felder: einfach, komplex, verschachtelt, Verzeichnisse, Querverweise, Textmarken, Hyperlinks, Index, Serienbrief"),
    ("bilder", 60, k_bilder, "Bilder: inline und verankert, Umfluss, Bezüge, Zuschnitt, Drehung, Formate, fehlende Bilder"),
    ("formen", 50, k_formen, "Formen: Geometrien, Füllungen, Konturen, Effekte, Textfelder, Gruppen, VML, WordArt"),
    ("diagramme", 30, k_diagramme, "Diagramme: Säulen, Balken, Linien, Flächen, Kreis, Ring, Streu, Netz, 3D"),
    ("noten", 60, k_noten, "Fußnoten, Endnoten, Kommentare mit Antworten, Änderungsverfolgung, Verschiebungen, Bearbeitungsbereiche"),
    ("steuerelemente", 30, k_steuer, "Inhaltssteuerelemente und Formularfelder"),
    ("sprachen", 50, k_sprachen, "Sprachen, Schreibrichtungen, Sonderzeichen, Steuerzeichen, lange Wörter"),
    ("metadaten", 30, k_meta, "Dokumenteigenschaften, benutzerdefinierte Eigenschaften, Einstellungen, Kompatibilität"),
    ("grenzfaelle", 40, k_grenz, "Grenzfälle: leer, riesig, verschachtelt, unbekannt, beschädigt, fehlende Teile"),
    ("praxis", 30, k_real, "Praxisdokumente: Brief, Bericht, Vertrag, Rechnung, Lebenslauf, Protokoll, Abschlussarbeit, Newsletter, Formular"),
]


def zaehlen(pfad: str) -> dict:
    with zipfile.ZipFile(pfad) as z:
        x = z.read("word/document.xml").decode("utf-8")
        teile = z.namelist()
    return {"absaetze": len(re.findall(r"<w:p[ >]", x)), "tabellen": len(re.findall(r"<w:tbl>", x)), "zeilen": len(re.findall(r"<w:tr[ >]", x)), "zellen": len(re.findall(r"<w:tc>", x)),
            "bilder": len(re.findall(r"<pic:pic>", x)), "formen": len(re.findall(r"<wps:wsp>|<v:(?:rect|oval|roundrect|line|shape)[ >]", x)), "diagramme": len(re.findall(r"<c:chart ", x)),
            "felder": len(re.findall(r'w:fldCharType="begin"', x)) + len(re.findall(r"<w:fldSimple", x)), "steuerelemente": len(re.findall(r"<w:sdt>", x)),
            "abschnitte": len(re.findall(r"<w:sectPr[ >]", x)), "fussnoten": len(re.findall(r"<w:footnoteReference", x)), "endnoten": len(re.findall(r"<w:endnoteReference", x)),
            "kommentare": len(re.findall(r"<w:commentReference", x)), "aenderungen": len(re.findall(r"<w:(?:ins|del|moveFrom|moveTo) ", x)), "teile": len(teile)}


def pruefe_xml(pfad: str) -> list[str]:
    fehler = []
    with zipfile.ZipFile(pfad) as z:
        for n in z.namelist():
            if n.endswith((".xml", ".rels")):
                try:
                    minidom.parseString(z.read(n))
                except Exception as ex:  # noqa: BLE001
                    fehler.append(f"{n}: {ex}")
    return fehler


def main(argv: list[str]) -> int:
    ziel = os.path.expanduser("~/Lunivo-Testdateien/docx")
    nur = None
    args = argv[1:]
    while args:
        a = args.pop(0)
        if a == "--nur":
            nur = args.pop(0)
        else:
            ziel = os.path.expanduser(a)
    zeilen, schlecht, gesamt = [], [], 0
    for name, anzahl, fun, beschr in KATEGORIEN:
        if nur and name != nur:
            continue
        for i in range(anzahl):
            rng = random.Random(f"{name}-{i}")
            d = fun(i, rng)
            rel = f"{name}/{name}_{i + 1:04d}.docx"
            pfad = os.path.join(ziel, rel)
            d.speichern(pfad)
            fe = pruefe_xml(pfad)
            if fe:
                schlecht.append((rel, fe))
            z = zaehlen(pfad)
            zeilen.append({"datei": rel, "kategorie": name, "merkmal": d.kern["beschreibung"], **z, "bytes": os.path.getsize(pfad)})
            gesamt += 1
    if zeilen:
        with open(os.path.join(ziel, "manifest.csv" if not nur else f"manifest_{nur}.csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(zeilen[0]), delimiter=";")
            w.writeheader()
            w.writerows(zeilen)
        with open(os.path.join(ziel, "LIESMICH.md"), "w", encoding="utf-8") as f:
            f.write("# DOCX-Testbestand\n\nErzeugt von `werkzeuge/pruefungen/docx_testbestand.py` (deterministisch, nur Standardbibliothek, ohne Lunivo-Code).\n\n"
                    "Die Zählwerte in `manifest.csv` sind Rohzählungen im erzeugten XML und damit eine von Lunivo unabhängige Quelle.\n\n| Kategorie | Dateien | Inhalt |\n|---|---|---|\n"
                    + "".join(f"| {n} | {a} | {b} |\n" for n, a, fu, b in KATEGORIEN) + f"\nGesamt: {sum(a for _, a, _, _ in KATEGORIEN)} Dateien.\n")
    print(f"{gesamt} Dateien nach {ziel}")
    for rel, fe in schlecht:
        print("XML-FEHLER", rel, fe[:2])
    return 1 if schlecht else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
