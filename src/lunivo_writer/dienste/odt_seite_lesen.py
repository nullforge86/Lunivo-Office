"""ODT lesen: Seitenvorlage (Größe, Ränder, Hintergrund, Seitenzahlart), Kopf- und Fußzeile samt Bildern → ``PageSettings``.

Als Baustein ``_ODTSeite`` in ``odt_reader._Leser`` eingemischt; braucht dessen ``stile``, ``stil_wurzel``, ``report`` und die Bildhilfen
aus ``odt_bilder._ODTBilder``.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from PySide6.QtGui import QImage

from lunivo_writer.modelle.seite import HeaderFooter, PageSettings, px_to_mm
from lunivo_writer.dienste.odt_xml import _kurz, _px, _q, _text_von

_SEITENZAHL_ART = {"a": "klein", "A": "gross", "i": "roem_klein", "I": "roem_gross"}
_AUSRICHTUNG = {"start": "left", "left": "left", "end": "right", "right": "right", "justify": "justify"}
# Kopf und Fuß: (ODF-Name, Seite des Abstands zum Text, Seitenattribut des Abstands, Seitenattribut des Randes)
_KOPF_FUSS = (("header", "bottom", "kopf_abstand_mm", "margin_top_mm"),
              ("footer", "top", "fuss_abstand_mm", "margin_bottom_mm"))
_GROESSEN = (("width_mm", "fo:page-width"), ("height_mm", "fo:page-height"),
             ("margin_left_mm", "fo:margin-left"), ("margin_right_mm", "fo:margin-right"))
_BILD_ORTE = (("header", "kopf"), ("footer", "fuss"), ("header-first", "kopf1"), ("footer-first", "fuss1"))
_MIN_ABSTAND_MM = 5.0


def _mm(wert: str | None, standard: float) -> float:
    """ODF-Länge → Millimeter; ohne Angabe ``standard``."""
    return px_to_mm(_px(wert, standard * 96 / 25.4)) if wert else standard


def _hauptvorlage(wurzel: ET.Element | None) -> ET.Element | None:
    """Die Seitenvorlage „Standard“ (sonst die erste) aus ``office:master-styles``."""
    ms = wurzel.find(_q("office:master-styles")) if wurzel is not None else None
    if ms is None:
        return None
    alle = ms.findall(_q("style:master-page"))
    return next((m for m in alle if m.get(_q("style:name")) == "Standard"), alle[0] if alle else None)


def _bereich_da(master: ET.Element, teil: str) -> bool:
    """Hat die Vorlage diesen Kopf bzw. Fuß (normal, erste Seite oder linke Seiten)?"""
    return any(master.find(_q(f"style:{teil}{ende}")) is not None for ende in ("", "-first", "-left"))


def _bereich_abstand(page: PageSettings, master: ET.Element, layout: ET.Element, art: tuple) -> None:
    """ODF misst den Rand bis zur Kopfzeile; Lunivo bis zum Text: Höhe und Abstand der Kopf-/Fußzeile kommen zum Rand dazu."""
    teil, kante, abstand_attr, rand_attr = art
    hp = layout.find(f"{_q('style:' + teil + '-style')}/{_q('style:header-footer-properties')}")
    if not _bereich_da(master, teil) or hp is None:
        return
    h = {_kurz(k): v for k, v in hp.attrib.items()}
    extra = px_to_mm(_px(h.get("fo:min-height") or h.get("svg:height"), 0) + _px(h.get(f"fo:margin-{kante}"), 0))
    rand = getattr(page, rand_attr)
    setattr(page, abstand_attr, rand)
    setattr(page, rand_attr, rand + max(extra, _MIN_ABSTAND_MM))


def _layout_anwenden(page: PageSettings, master: ET.Element, layout: ET.Element) -> None:
    p = layout.find(_q("style:page-layout-properties"))
    a = {_kurz(k): v for k, v in (p.attrib.items() if p is not None else [])}
    for attr, schluessel in _GROESSEN:
        setattr(page, attr, _mm(a.get(schluessel), getattr(page, attr)))
    page.seiten_format = _SEITENZAHL_ART.get(a.get("style:num-format", "1"), "dezimal")
    oben = _mm(a.get("fo:margin-top"), page.margin_top_mm)
    unten = _mm(a.get("fo:margin-bottom"), page.margin_bottom_mm)
    hg = a.get("fo:background-color")
    if hg and hg != "transparent":
        page.color = hg
    page.margin_top_mm, page.margin_bottom_mm = oben, unten
    for art in _KOPF_FUSS:
        _bereich_abstand(page, master, layout, art)


class _ODTSeite:
    def seite(self) -> PageSettings:
        page = PageSettings()
        master = _hauptvorlage(self.stil_wurzel)
        if master is None:
            return page
        layout = self.stile.seiten.get(master.get(_q("style:page-layout-name"), ""))
        if layout is not None:
            _layout_anwenden(page, master, layout)
        page.header = self._kopf_fuss(master.find(_q("style:header")))
        page.footer = self._kopf_fuss(master.find(_q("style:footer")))
        self._linke_seiten(page, master)
        self._erste_seite(page, master)
        self._seiten_bilder(page, master)
        return page

    def _linke_seiten(self, page: PageSettings, master: ET.Element) -> None:
        for attr, tag in (("header", "header-left"), ("footer", "footer-left")):          # gespiegelt auf linken Seiten: „außen“/„innen“
            hf, links = getattr(page, attr), self._kopf_fuss(master.find(_q("style:" + tag)))
            if hf.text and links.text == hf.text and {hf.align, links.align} == {"left", "right"}:
                hf.align = "aussen" if hf.align == "right" else "innen"
            elif links.text and (links.text != hf.text or links.align != hf.align):
                page.diff_even = True                                  # eigene Zeilen für gerade Seiten
                setattr(page, "even_" + attr, links)

    def _erste_seite(self, page: PageSettings, master: ET.Element) -> None:
        erste_kopf, erste_fuss = master.find(_q("style:header-first")), master.find(_q("style:footer-first"))
        if erste_kopf is not None or erste_fuss is not None:
            page.diff_first = True
            page.first_header = self._kopf_fuss(erste_kopf)
            page.first_footer = self._kopf_fuss(erste_fuss)

    def _seiten_bilder(self, page: PageSettings, master: ET.Element) -> None:
        for tag, ort in _BILD_ORTE:
            teil = master.find(_q("style:" + tag))
            if teil is None:
                continue
            for fr in teil.iter(_q("draw:frame")):
                bild = fr.find(_q("draw:image"))
                img = self._bild_laden(bild) if bild is not None else QImage()
                angabe = self._frei_angabe(fr) if not img.isNull() else None
                if angabe is None:
                    self.report.warn("Ein Bild in der Kopf- oder Fußzeile der ODT-Datei wurde nicht übernommen.")
                    continue
                angabe.update(ort=ort, bild=img, b=angabe["b"] or img.width(), h=angabe["h"] or img.height())
                page.bilder.append(angabe)

    def _kopf_fuss(self, el: ET.Element | None) -> HeaderFooter:
        if el is None or el.get(_q("style:display")) == "false":
            return HeaderFooter()
        absaetze = [p for p in el.iter() if p.tag in (_q("text:p"), _q("text:h"))]
        text = "\n".join(_text_von(p) for p in absaetze).strip("\n")
        ausr = "center"
        if absaetze:
            a = self.stile.eigenschaften("paragraph", absaetze[0].get(_q("text:style-name")), "paragraph").get("fo:text-align")
            ausr = _AUSRICHTUNG.get(a or "", "center")
        return HeaderFooter(text, ausr)
