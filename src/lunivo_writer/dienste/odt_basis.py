"""Gemeinsame Bausteine zum Schreiben von ODT aus dem Dokumentmodell — ohne Qt: Namensräume, Maße, Textmaskierung, Vorlagen, Manifest, Metadaten, Bilder und
frei positionierte Rahmen. Bilder kommen als Bytes; ihr Format und ihre Größe werden am Dateikopf erkannt (``core.document.bildformat``)."""
from __future__ import annotations

from xml.sax.saxutils import escape

from lunivo_writer.kern.dokument.bildformat import FORMATE, format_erkennen, masse
from lunivo_writer.kern.dokument.bericht import IOReport

MIMETYPE = b"application/vnd.oasis.opendocument.text"
_NS = ('xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" '
       'xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" '
       'xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" '
       'xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" '
       'xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" '
       'xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" '
       'xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" '
       'xmlns:xlink="http://www.w3.org/1999/xlink" '
       'xmlns:dc="http://purl.org/dc/elements/1.1/" '
       'xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" '
       'xmlns:loext="urn:org:documentfoundation:names:experimental:office:xmlns:loext:1.0" '
       'xmlns:manifest="urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"')
ATTR_QUOTE = {chr(34): "&quot;"}
BILDTYPEN = {endung: typ for endung, typ in FORMATE.values()}                      # Dateiendung → Medientyp für das Manifest
BILDTYPEN["jpeg"] = "image/jpeg"
ODT_BILDFORMATE = frozenset({"png", "jpeg", "gif", "bmp", "tiff", "svg", "emf", "wmf"})       # bleiben im Original; anderes (WebP) lässt sich ohne Qt nicht umwandeln
STAND_TAB_STIL = ('<style:style style:name="Tab" style:family="table"><style:table-properties style:width="100%" '
                  'table:align="margins"/></style:style>')
STAND_ZELLE_STIL = ('<style:style style:name="Zelle" style:family="table-cell"><style:table-cell-properties '
                    'fo:padding="1mm" fo:border="0.5pt solid #000000"/></style:style>')
_TEXT_SONDER = {"\t": "<text:tab/>", " ": "<text:line-break/>", "\n": "<text:line-break/>", "￼": ""}   # Zeichen → ODF-Element

# Frei positionierte Bilder ↔ ODF-Rahmen am Absatz: Bezug und Ausrichtung je Achse.
BEZUG_H = {"seite": "page", "rand": "page-content", "spalte": "paragraph"}
BEZUG_V = {"seite": "page", "rand": "page-content", "absatz": "paragraph"}
AUSR_H = {"left": "left", "center": "center", "right": "right", "inside": "inside", "outside": "outside"}
AUSR_V = {"top": "top", "center": "middle", "bottom": "bottom"}


def _mm(wert: float) -> str:
    return f"{max(0.0, float(wert)):.2f}mm"


def _laenge(px: float) -> str:
    return f"{px * 25.4 / 96:.2f}mm"


def _odf(element: str, attr: dict | None = None, inhalt: str | None = None) -> str:
    """Ein Element des ODF-Tabellenmodells (Namensraum ``table:``) als XML-Text."""
    name = "table:" + element
    a = "".join(f' {k}="{escape(v, ATTR_QUOTE)}"' for k, v in (attr or {}).items())
    return f"<{name}{a}/>" if inhalt is None else f"<{name}{a}>{inhalt}</{name}>"


def manifest(namen: list[str]) -> str:
    eintraege = [f'<manifest:file-entry manifest:media-type="{MIMETYPE.decode()}" manifest:full-path="/"/>']
    for n in namen:
        if n in ("mimetype", "META-INF/manifest.xml") or n.endswith("/"):
            continue
        typ = "text/xml" if n.endswith(".xml") else BILDTYPEN.get(n.rsplit(".", 1)[-1].lower(), "application/octet-stream")
        eintraege.append(f'<manifest:file-entry manifest:media-type="{typ}" manifest:full-path="{escape(n)}"/>')
    return (f'<?xml version="1.0" encoding="UTF-8"?><manifest:manifest {_NS} manifest:version="1.3">'
            + "".join(eintraege) + "</manifest:manifest>")


def meta_xml(meta: dict) -> str:
    teile = []
    if meta.get("title"):
        teile.append(f"<dc:title>{escape(meta['title'])}</dc:title>")
    if meta.get("author"):
        teile.append(f"<meta:initial-creator>{escape(meta['author'])}</meta:initial-creator><dc:creator>{escape(meta['author'])}</dc:creator>")
    return ('<?xml version="1.0" encoding="UTF-8"?>'
            f'<office:document-meta {_NS} office:version="1.3"><office:meta><meta:generator>Lunivo Writer</meta:generator>'
            f'{"".join(teile)}</office:meta></office:document-meta>')


def _text_zeichen(ch: str) -> str:
    """Ein Zeichen des Dokumenttexts als ODF-Text (Sonderzeichen → Elemente, Steuerzeichen entfallen)."""
    if ch in _TEXT_SONDER:
        return _TEXT_SONDER[ch]
    return "" if ord(ch) < 32 else escape(ch)


def _leerzeichen_lauf(s: str, i: int) -> tuple[str, int]:
    """Mehrere Leerzeichen ab ``i`` → (ODF-Text, Länge des Laufs): ein echtes Leerzeichen plus ``text:s`` für den Rest."""
    n = 1
    while i + n < len(s) and s[i + n] == " ":
        n += 1
    return " " + (f'<text:s text:c="{n - 1}"/>' if n > 1 else ""), n


def text_xml(s: str) -> str:
    teile, i = [], 0
    while i < len(s):
        if s[i] == " " and s[i + 1:i + 2] == " ":
            xml, n = _leerzeichen_lauf(s, i)
            teile.append(xml)
            i += n
            continue
        teile.append(_text_zeichen(s[i]))
        i += 1
    return "".join(teile)


def text_eigenschaften(name, groesse, fett, kursiv, unter, durch, lage, farbe, hg) -> str:
    """Die Attribute einer Textvorlage; nur gesetzte Eigenschaften erscheinen."""
    paare = ((name, f'style:font-name="{escape(name, ATTR_QUOTE)}"'), (groesse, f'fo:font-size="{groesse:g}pt"'),
             (fett, 'fo:font-weight="bold"'), (kursiv, 'fo:font-style="italic"'),
             (unter, 'style:text-underline-style="solid" style:text-underline-width="auto" style:text-underline-color="font-color"'),
             (durch, 'style:text-line-through-style="solid"'), (lage, f'style:text-position="{lage} 58%"'),
             (farbe, f'fo:color="{farbe}"'), (hg, f'fo:background-color="{hg}"'))
    return " ".join(s for gesetzt, s in paare if gesetzt)


def absatz_vorlage_xml(name: str, schl: tuple) -> str:
    """Eine Absatz- oder Spaltenvorlage (``schl`` wie in ``InhaltBasis`` bzw. ``("spalte", Prozent)``)."""
    if schl[0] == "spalte":
        return (f'<style:style style:name="{name}" style:family="table-column"><style:table-column-properties '
                f'style:rel-column-width="{schl[1] * 100}*"/></style:style>')
    ausr, links, rechts, oben, unten, einzug, umbruch = schl
    return (f'<style:style style:name="{name}" style:family="paragraph" style:parent-style-name="Standard">'
            f'<style:paragraph-properties fo:text-align="{ausr}" fo:margin-left="{_laenge(links)}" '
            f'fo:margin-right="{_laenge(rechts)}" fo:margin-top="{_laenge(oben)}" fo:margin-bottom="{_laenge(unten)}" '
            f'fo:text-indent="{_laenge(einzug)}"' + (' fo:break-before="page"' if umbruch else "") + "/></style:style>")


def _dekorativ(a_oder_bool) -> str:
    """Das Attribut „Als dekorativ markiert“ für ``style:graphic-properties`` (so schreibt es LibreOffice: ``loext:decorative="true"``)."""
    return ' loext:decorative="true"' if a_oder_bool else ""


def bild_stil(name: str) -> str:
    """Rahmenvorlage eines dekorativen Bildes im Text (sonst hat der Rahmen keine eigene)."""
    return f'<style:style style:name="{name}" style:family="graphic"><style:graphic-properties{_dekorativ(True)}/></style:style>'


def frei_stil(name: str, a: dict) -> str:
    """Rahmenvorlage (Familie „graphic“) für ein frei positioniertes Bild: ohne Textumfluss, vor oder hinter dem Text."""
    daten = a.get("daten") if a.get("art") == "form" and isinstance(a.get("daten"), dict) else {}
    fuell = daten.get("fuell", "")
    linie = daten.get("linie", "")
    fuell_xml = (f' draw:fill="solid" draw:fill-color="{escape(str(fuell), ATTR_QUOTE)}"' if fuell else ' draw:fill="none"' if daten else "")
    strich_xml = (f' draw:stroke="solid" svg:stroke-color="{escape(str(linie), ATTR_QUOTE)}" '
                  f'svg:stroke-width="{_laenge(float(daten.get("strich") or 1.0))}"' if linie else ' draw:stroke="none"' if daten else "")
    return (f'<style:style style:name="{name}" style:family="graphic"><style:graphic-properties style:wrap="run-through" '
            f'style:run-through="{"background" if a.get("hinter") else "foreground"}" '
            f'style:horizontal-pos="{AUSR_H.get(a.get("ah") or "", "from-left")}" '
            f'style:horizontal-rel="{BEZUG_H.get(a.get("bh"), "paragraph")}" '
            f'style:vertical-pos="{AUSR_V.get(a.get("av") or "", "from-top")}" '
            f'style:vertical-rel="{BEZUG_V.get(a.get("bv"), "paragraph")}"{fuell_xml}{strich_xml}{_dekorativ(a.get("dekor"))}/></style:style>')


def bild_elemente(roh: bytes, stamm: str, bilder: dict[str, bytes]) -> str | None:
    """Das ``draw:image``-Element eines Bildes im Original; die Bilddaten kommen nach ``bilder`` (Pictures/…). ``None``, wenn das Format nicht
    unverändert in ODT gehört (und ohne Qt nicht umzuwandeln ist)."""
    art = format_erkennen(roh)
    if art not in ODT_BILDFORMATE:
        return None
    name = f"Pictures/{stamm}.{FORMATE[art][0]}"
    bilder[name] = roh
    return f'<draw:image xlink:href="{name}" xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad"/>'


def frei_rahmen(a: dict, roh: bytes, nr: int, stil: str, bilder: dict[str, bytes]) -> str:
    """Ein frei positioniertes Bild als draw:frame am Absatz; die Bilddaten kommen nach ``bilder``. Leer, wenn das Format nicht geschrieben werden kann."""
    bild = bild_elemente(roh, f"frei{nr}", bilder)
    if bild is None:
        return ""
    groesse = masse(roh) or (64.0, 64.0)
    b, h = float(a.get("b") or groesse[0]), float(a.get("h") or groesse[1])
    lage = ""
    if not AUSR_H.get(a.get("ah") or ""):
        lage += f' svg:x="{_laenge(float(a.get("xh") or 0))}"'
    if not AUSR_V.get(a.get("av") or ""):
        lage += f' svg:y="{_laenge(float(a.get("yv") or 0))}"'
    return (f'<draw:frame draw:style-name="{stil}" draw:name="Frei{nr}" text:anchor-type="paragraph"{lage} '
            f'svg:width="{_laenge(b)}" svg:height="{_laenge(h)}" draw:z-index="{0 if a.get("hinter") else nr}">'
            f'{bild}</draw:frame>')


def frei_form(a: dict, nr: int, stil: str) -> str:
    """Einfache freie ODT-Form (Rechteck/Ellipse) ohne Rasterbild."""
    daten = a.get("daten") or {}
    element = {"rechteck": "rect", "ellipse": "ellipse"}.get(str(daten.get("form", "")).casefold())
    if element is None:
        return ""
    lage = ""
    if not AUSR_H.get(a.get("ah") or ""):
        lage += f' svg:x="{_laenge(float(a.get("xh") or 0))}"'
    if not AUSR_V.get(a.get("av") or ""):
        lage += f' svg:y="{_laenge(float(a.get("yv") or 0))}"'
    breite = float(a.get("b") or daten.get("breite") or 1)
    hoehe = float(a.get("h") or daten.get("hoehe") or 1)
    return (f'<draw:{element} draw:style-name="{stil}" draw:name="Form{nr}" text:anchor-type="paragraph"{lage} '
            f'svg:width="{_laenge(breite)}" svg:height="{_laenge(hoehe)}" draw:z-index="{0 if a.get("hinter") else nr}"/>')


class InhaltBasis:
    """Zustand von ``content.xml``: Vorlagen (Absatz, Text, Liste), Schriften, Bilder, Rahmenvorlagen; baut den Vorlagen- und Schriftenteil."""

    def __init__(self, rep: IOReport):
        self.rep = rep
        self.absatz_stile: dict[tuple, str] = {}
        self.text_stile: dict[tuple, str] = {}
        self.listen_stile: dict[int, tuple[str, str]] = {}
        self.schriften: set[str] = set()
        self.bilder: dict[str, bytes] = {}
        self.tabellen = 0
        self.rahmen_stile: list[str] = []

    def _vorlagen_xml(self) -> str:
        stile = [absatz_vorlage_xml(name, schl) for schl, name in self.absatz_stile.items()]
        stile.extend(f'<style:style style:name="{stil}" style:family="text"><style:text-properties '
                     f'{text_eigenschaften(*schl)}/></style:style>' for schl, stil in self.text_stile.items())
        stile.extend((STAND_TAB_STIL, STAND_ZELLE_STIL))
        stile.extend(x for _n, x in self.listen_stile.values())
        stile.extend(self.rahmen_stile)
        return "".join(stile)

    def _schriften_xml(self) -> str:
        return "".join(f'<style:font-face style:name="{escape(n, ATTR_QUOTE)}" svg:font-family="{escape(n, ATTR_QUOTE)}"/>' for n in sorted(self.schriften))
