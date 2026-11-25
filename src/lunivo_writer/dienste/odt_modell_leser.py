"""Gemeinsame Hilfen der ODT-Leser, ohne Qt: Stile (``_Stile``), Seiteneinrichtung samt Kopf-/Fußzeile (``_Leser._seite``), Farbwerte und sicheres XML.

Gelesen wird ODT in das Dokumentenmodell von ``odt_dokument_leser``; dieses Modul hält nur, was dieser Leser von hier nimmt."""
from __future__ import annotations

import base64
import xml.etree.ElementTree as ET

from lunivo_writer.core.document.values import Brush, Color, Length
from lunivo_writer.dienste.odt_xml import GRENZE_BYTES, MAX_WIEDERHOLUNG, NS, _kurz, _px, _pt, _q, _text_von
from lunivo_writer.modelle.bericht import DocumentIOError, IOReport
from lunivo_writer.modelle.seite import HeaderFooter, PageSettings, px_to_mm

class NichtImModell(Exception):
    """ODT-Inhalt, der noch nicht ohne Qt vollständig übernommen wird."""


class _Stile:
    def __init__(self):
        self.stile: dict[tuple[str, str], ET.Element] = {}
        self.standard: dict[str, ET.Element] = {}
        self.listen: dict[str, ET.Element] = {}
        self.schriften: dict[str, str] = {}
        self.seiten: dict[str, ET.Element] = {}
        self.cache: dict[tuple[str, str | None, str], dict[str, str]] = {}
        self.zeichen: dict[tuple[str, str], ET.Element] = {}                       # benannte Zeichenvorlagen: ("gradient" | "hatch" | "fill-image" | "stroke-dash", Name)

    def lesen(self, wurzel: ET.Element | None) -> None:
        if wurzel is None:
            return
        for element in wurzel.iter(_q("style:font-face")):
            name = element.get(_q("style:name"), "")
            self.schriften[name] = (element.get(_q("svg:font-family")) or name).strip("'\"")
        for bereich in ("office:styles", "office:automatic-styles"):
            container = wurzel.find(_q(bereich))
            if container is None:
                continue
            for element in container:
                name, familie = element.get(_q("style:name"), ""), element.get(_q("style:family"), "")
                lokal = element.tag.rsplit("}", 1)[-1]
                if element.tag.startswith("{" + NS["draw"] + "}") and lokal in ("gradient", "hatch", "fill-image", "stroke-dash"):
                    self.zeichen[lokal, element.get(_q("draw:name"), "")] = element
                elif element.tag == _q("style:style"):
                    self.stile[familie, name] = element
                elif element.tag == _q("style:default-style"):
                    self.standard[familie] = element
                elif element.tag == _q("text:list-style"):
                    self.listen[name] = element
                elif element.tag == _q("style:page-layout"):
                    self.seiten[name] = element

    def eigenschaften(self, familie: str, name: str | None, art: str) -> dict[str, str]:
        key = (familie, name, art)
        if key in self.cache:
            return self.cache[key]
        kette, gesehen = [], set()
        while name and (familie, name) in self.stile and name not in gesehen:
            gesehen.add(name)
            element = self.stile[familie, name]
            kette.append(element)
            name = element.get(_q("style:parent-style-name"))
        if familie in self.standard:
            kette.append(self.standard[familie])
        werte = {}
        for element in reversed(kette):
            child = element.find(_q(f"style:{art}-properties"))
            if child is not None:
                werte.update({_kurz(k): v for k, v in child.attrib.items()})
        self.cache[key] = werte
        return werte

    def liste_von(self, absatzstil: str | None) -> str | None:
        gesehen = set()
        while absatzstil and absatzstil not in gesehen and ("paragraph", absatzstil) in self.stile:
            gesehen.add(absatzstil)
            style = self.stile["paragraph", absatzstil]
            name = style.get(_q("style:list-style-name"))
            if name:
                return name
            absatzstil = style.get(_q("style:parent-style-name"))
        return None


def _farbe(wert: str | None) -> Color | None:
    if not wert or wert == "transparent" or len(wert) != 7 or wert[0] != "#":
        return None
    try:
        return Color(int(wert[1:3], 16), int(wert[3:5], 16), int(wert[5:7], 16))
    except ValueError:
        return None


class _Leser:
    def __init__(self, inhalt: ET.Element, stilelement: ET.Element | None, metaelement: ET.Element | None, bild_laden=None):
        self.inhalt, self.stilelement, self.metaelement = inhalt, stilelement, metaelement
        self.bild_laden = bild_laden or (lambda _name: None)
        self.stile = _Stile()
        self.stile.lesen(stilelement)
        if inhalt is not stilelement:
            self.stile.lesen(inhalt)
        self.report = IOReport()

    @staticmethod
    def _repeat(node: ET.Element, key: str) -> int:
        try:
            return max(1, min(MAX_WIEDERHOLUNG, int(node.get(_q(key), "1"))))
        except ValueError:
            return 1

    def _seite(self) -> PageSettings:
        page = PageSettings()
        masters = self.stilelement.find(_q("office:master-styles")) if self.stilelement is not None else None
        if masters is None:
            return page
        master = next(iter(masters.findall(_q("style:master-page"))), None)
        if master is None:
            return page
        layout = self.stile.seiten.get(master.get(_q("style:page-layout-name"), ""))
        properties = layout.find(_q("style:page-layout-properties")) if layout is not None else None
        if properties is not None:
            attrs = {_kurz(k): v for k, v in properties.attrib.items()}
            for field, key in (("width_mm", "fo:page-width"), ("height_mm", "fo:page-height"), ("margin_left_mm", "fo:margin-left"),
                               ("margin_right_mm", "fo:margin-right"), ("margin_top_mm", "fo:margin-top"), ("margin_bottom_mm", "fo:margin-bottom")):
                if key in attrs:
                    setattr(page, field, px_to_mm(_px(attrs[key])))
            bgcolor = attrs.get("fo:background-color")
            if bgcolor and bgcolor != "transparent":
                page.color = bgcolor
            page.seiten_format = {"a": "klein", "A": "gross", "i": "roem_klein", "I": "roem_gross"}.get(attrs.get("style:num-format", "1"), "dezimal")
            for element_name, margin_attr, distance_attr, edge in (("header", "margin_top_mm", "kopf_abstand_mm", "bottom"),
                                                                    ("footer", "margin_bottom_mm", "fuss_abstand_mm", "top")):
                style = layout.find(f"{_q(f'style:{element_name}-style')}/{_q('style:header-footer-properties')}") if layout is not None else None
                if style is None or master.find(_q("style:" + element_name)) is None:
                    continue
                values = {_kurz(k): v for k, v in style.attrib.items()}
                margin = getattr(page, margin_attr)
                extra = px_to_mm(_px(values.get("fo:min-height") or values.get("svg:height"), 0)
                                 + _px(values.get(f"fo:margin-{edge}"), 0))
                setattr(page, distance_attr, margin)
                setattr(page, margin_attr, margin + max(extra, 5.0))
        for attr, tag in (("header", "header"), ("footer", "footer"), ("first_header", "header-first"), ("first_footer", "footer-first")):
            el = master.find(_q("style:" + tag))
            if el is not None:
                text = "\n".join(_text_von(p) for p in el.iter() if p.tag in (_q("text:p"), _q("text:h"))).strip("\n")
                para = next((p for p in el.iter() if p.tag in (_q("text:p"), _q("text:h"))), None)
                align = self.stile.eigenschaften("paragraph", para.get(_q("text:style-name")) if para is not None else None, "paragraph").get("fo:text-align")
                setattr(page, attr, HeaderFooter(text, {"start": "left", "left": "left", "center": "center", "end": "right", "right": "right", "justify": "justify"}.get(align, "center")))
        page.diff_first = master.find(_q("style:header-first")) is not None or master.find(_q("style:footer-first")) is not None
        for tag, ort in (("header", "kopf"), ("footer", "fuss"), ("header-first", "kopf1"), ("footer-first", "fuss1")):
            parent = master.find(_q("style:" + tag))
            if parent is None:
                continue
            for frame in parent.iter(_q("draw:frame")):
                image = frame.find(_q("draw:image"))
                if image is None:
                    continue
                href = image.get(_q("xlink:href"), "")
                embedded = image.find(_q("office:binary-data"))
                data = None
                if embedded is not None and embedded.text:
                    try:
                        data = base64.b64decode(embedded.text)
                    except ValueError:
                        data = None
                elif href and not ":" in href:
                    data = self.bild_laden(href.lstrip("./"))
                if not data:
                    self.report.warn("Ein Bild in der Kopf- oder Fußzeile der ODT-Datei wurde nicht übernommen.")
                    continue
                g = self.stile.eigenschaften("graphic", frame.get(_q("draw:style-name")), "graphic")
                hpos, vpos = g.get("style:horizontal-pos"), g.get("style:vertical-pos")
                page.bilder.append({"ort": ort, "bild": data, "b": _px(frame.get(_q("svg:width")), 64.0),
                                    "h": _px(frame.get(_q("svg:height")), 64.0), "bh": "seite", "bv": "seite",
                                    "ah": hpos if hpos in ("left", "center", "right", "inside", "outside") else "",
                                    "av": {"top": "top", "middle": "center", "bottom": "bottom"}.get(vpos, ""), "xh": _px(frame.get(_q("svg:x")), 0.0),
                                    "yv": _px(frame.get(_q("svg:y")), 0.0)})
        return page


def _xml(data: bytes) -> ET.Element:
    from lunivo_writer.dienste.import_grenzen import sicheres_xml
    return sicheres_xml(data)
