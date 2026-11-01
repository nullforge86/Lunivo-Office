"""Teil von docx_reader: seite lesen (Methoden einer Mixin-Klasse)."""
from __future__ import annotations

from lunivo_writer.services.docx_teile.basis_lesen import (
    HeaderFooter,
    PageSettings,
    Qt,
    _xp,
    art_aus_docx,
    qn,
)  # noqa: F401


class SeiteLesen:
    def read_page(self) -> PageSettings:
        """Einrichtung des ERSTEN Abschnitts; weitere Abschnitte stehen als Umbrüche im Text (siehe editor/abschnitte.py)."""
        return self._section_page(self.d.sections[0], erster=True)

    def _section_page(self, s, erster: bool = False, basis: PageSettings | None = None) -> PageSettings:
        ps = PageSettings()
        try:
            ps.width_mm = s.page_width.mm
            ps.height_mm = s.page_height.mm
            ps.margin_top_mm = s.top_margin.mm
            ps.margin_bottom_mm = s.bottom_margin.mm
            ps.margin_left_mm = s.left_margin.mm
            ps.margin_right_mm = s.right_margin.mm
        except Exception:
            self.report.warn("Seitengröße oder Ränder fehlen; es gilt A4 mit 2,5 cm Rand.")
        try:
            ps.kopf_abstand_mm, ps.fuss_abstand_mm = s.header_distance.mm, s.footer_distance.mm
        except Exception:                                                  # noqa: BLE001
            pass
        self._seitenschmuck(ps, s)
        if basis is not None:                                    # Hintergrund, Silbentrennung und Wasserzeichen gelten für das ganze Dokument
            ps.color, ps.silbentrennung, ps.watermark = basis.color, basis.silbentrennung, basis.watermark
        ps.kopf_verknuepft = (not erster) and s.header.is_linked_to_previous
        ps.fuss_verknuepft = (not erster) and s.footer.is_linked_to_previous
        ps.header = self._hf(s.header)
        ps.footer = self._hf(s.footer)
        self._aussen_innen(s, ps)
        self._seitenzahl_art(s, ps)
        ps.bilder = self._hf_bilder(s.header, "kopf", s, ps) + self._hf_bilder(s.footer, "fuss", s, ps)
        if s.different_first_page_header_footer:
            ps.diff_first = True
            ps.first_header = self._hf(s.first_page_header)
            ps.first_footer = self._hf(s.first_page_footer)
            ps.bilder += self._hf_bilder(s.first_page_header, "kopf1", s, ps) + self._hf_bilder(s.first_page_footer, "fuss1", s, ps)
        return ps

    def _hf_bilder(self, teil, ort: str, s, ps: PageSettings) -> list[dict]:
        """Frei positionierte Bilder einer Kopf- oder Fußzeile (zum Beispiel ein Band über dem Briefkopf). „Am Absatz“ wird auf das Blatt
        umgerechnet: der Absatz steht im Abstand der Kopfzeile vom oberen Rand, der der Fußzeile über dem unteren."""
        from lunivo_writer.models.page import mm_to_px
        if teil.is_linked_to_previous:
            return []
        out = []
        for dr in teil._element.iter(qn("w:drawing")):
            frei = self._frei(dr, teil.part, inline_ok=True)
            if not frei:
                continue
            angabe, bild = frei
            angabe["ort"], angabe["bild"] = ort, bild
            if dr.xpath("wp:inline"):                                  # Bild im Text der Kopf-/Fußzeile (Zierleiste): am Rand, am Absatz eingerückt
                ind = _xp(dr, "ancestor::w:p[1]/w:pPr/w:ind/@w:left")
                try:
                    angabe["xh"] = float(ind[0]) / 15.0 if ind else 0.0                      # Twips → px
                except ValueError:
                    angabe["xh"] = 0.0
                angabe["bh"] = "rand"
                try:
                    abstand = (s.header_distance if ort.startswith("kopf") else s.footer_distance).mm
                except Exception:                                                  # noqa: BLE001
                    abstand = 12.7
                angabe["bv"] = "seite"
                angabe["yv"] = mm_to_px(abstand) if ort.startswith("kopf") else mm_to_px(ps.height_mm - abstand) - angabe["h"]
                angabe["hinter"] = False
                out.append(angabe)
                continue
            if angabe["bv"] == "absatz":
                try:
                    abstand = (s.header_distance if ort.startswith("kopf") else s.footer_distance).mm
                except Exception:                                                  # noqa: BLE001
                    abstand = 12.7
                if ort.startswith("kopf"):
                    angabe["yv"] = mm_to_px(abstand) + angabe["yv"]
                else:
                    angabe["yv"] = mm_to_px(ps.height_mm - abstand) - 20 + angabe["yv"]
                angabe["bv"] = "seite"
            out.append(angabe)
        return out

    def _abschnitt_beginn(self, s) -> str:
        from lunivo_writer.editor.abschnitte import VOM_DOCX
        t = s._sectPr.find(qn("w:type"))
        return VOM_DOCX.get(t.get(qn("w:val")) if t is not None else "nextPage", "naechste")

    def _seitenschmuck(self, ps: PageSettings, sect) -> None:
        bg = self.d.element.find(qn("w:background"))
        if bg is not None:
            c = bg.get(qn("w:color"))
            if c and c.lower() not in ("auto", "ffffff"):
                ps.color = "#" + c.lower()
        ln = sect._sectPr.find(qn("w:lnNumType"))
        if ln is not None:
            ps.zeilennummern = True
            ps.zeilennummern_neu = "seite" if ln.get(qn("w:restart")) == "newPage" else ""
        co = sect._sectPr.find(qn("w:cols"))
        if co is not None:
            try:
                n = int(co.get(qn("w:num"), "1"))
            except ValueError:
                n = 1
            if n > 1:
                ps.spalten = min(n, 4)
                ps.spalten_abstand_mm = int(co.get(qn("w:space"), "720")) / 1440 * 25.4
                ps.spalten_linie = co.get(qn("w:sep"), "0").lower() in ("1", "true", "on")
        dt = self.d.settings.element.find(qn("w:defaultTabStop"))                      # Standardtabstopps des Dokuments (Twips)
        if dt is not None and dt.get(qn("w:val"), "").isdigit() and int(dt.get(qn("w:val"))) > 0:
            from PySide6.QtGui import QTextOption
            from lunivo_writer.models.page import mm_to_px
            opt = self.doc.defaultTextOption()
            opt.setTabStopDistance(mm_to_px(int(dt.get(qn("w:val"))) / 1440 * 25.4))
            self.doc.setDefaultTextOption(opt)
        ah = self.d.settings.element.find(qn("w:autoHyphenation"))
        if ah is not None and ah.get(qn("w:val"), "true").lower() not in ("false", "0", "off"):
            ps.silbentrennung = True
        pb = sect._sectPr.find(qn("w:pgBorders"))
        if pb is not None:
            e = next((x for x in (pb.find(qn("w:top")), pb.find(qn("w:left")), pb.find(qn("w:bottom")), pb.find(qn("w:right")))
                      if x is not None and x.get(qn("w:val"), "none") not in ("none", "nil")), None)
            if e is not None:
                col = (e.get(qn("w:color")) or "000000")
                da = "".join(k for x, k in (("top", "t"), ("bottom", "b"), ("left", "l"), ("right", "r"))
                             if pb.find(qn(f"w:{x}")) is not None and pb.find(qn(f"w:{x}")).get(qn("w:val"), "none") not in ("none", "nil"))
                ps.border = {"seiten": da or "tblr", "farbe": "#" + (col if col.lower() != "auto" else "000000").lower(),
                             "breite_pt": int(e.get(qn("w:sz")) or 8) / 8.0,
                             "art": art_aus_docx(e.get(qn("w:val"))),
                             "abstand_mm": int(e.get(qn("w:space")) or 24) / 72 * 25.4}
                from lunivo_writer.editor.seitenrahmen import KUNST
                wert = e.get(qn("w:val"))
                if wert in [k for k, _n in KUNST if k]:                              # Kunstrahmen
                    ps.border["kunst"] = wert
                if pb.get(qn("w:offsetFrom")) == "text":                              # Abstand vom Text, je Seite (pt)
                    ps.border["messen"] = "text"
                ab = [int((pb.find(qn(f"w:{x}")).get(qn("w:space")) if pb.find(qn(f"w:{x}")) is not None else None) or 0) for x in ("top", "bottom", "left", "right")]
                ps.border["abstand"] = ",".join(str(x) for x in ab)
                ps.border["vordergrund"] = pb.get(qn("w:zOrder"), "front") != "back"
                st = self.d.settings.element
                ps.border["kopf"] = st.find(qn("w:bordersDoNotSurroundHeader")) is None
                ps.border["fuss"] = st.find(qn("w:bordersDoNotSurroundFooter")) is None
                ps.border["ausrichten"] = st.find(qn("w:alignBordersAndEdges")) is not None

    def _aussen_innen(self, s, ps: PageSettings) -> None:
        """Gerade Seiten mit gespiegelter Ausrichtung bei gleichem Text: das ist „außen“ (ungerade rechts) bzw. „innen“ (ungerade links)."""
        try:
            if not self.d.settings.odd_and_even_pages_header_footer:
                return
            for attr, teil in (("header", s.even_page_header), ("footer", s.even_page_footer)):
                hf, gerade = getattr(ps, attr), self._hf(teil)
                if hf.text and gerade.text == hf.text and {hf.align, gerade.align} == {"left", "right"}:
                    hf.align = "aussen" if hf.align == "right" else "innen"
                elif not teil.is_linked_to_previous and (gerade.text != hf.text or gerade.align != hf.align):
                    ps.diff_even = True                          # eigene Zeilen für gerade Seiten
                    setattr(ps, "even_" + attr, gerade)
        except Exception:                                                  # noqa: BLE001
            pass

    def _seitenzahl_art(self, s, ps: PageSettings) -> None:
        """w:pgNumType: Zahlenart, „Beginnen mit“, Kapitelnummer."""
        from lunivo_writer.editor import seitenzahl as SZ
        e = s._sectPr.find(qn("w:pgNumType"))
        if e is None:
            return
        ps.seiten_format = {v: k for k, v in SZ.DOCX_FORMAT.items()}.get(e.get(qn("w:fmt")) or "decimal", "dezimal")
        try:
            ps.seiten_start = max(0, int(e.get(qn("w:start")) or 0))
            ps.kapitel_ebene = max(0, min(9, int(e.get(qn("w:chapStyle")) or 0)))
        except ValueError:
            pass
        ps.kapitel_trenner = next((z for z, _t, d in SZ.TRENNER if d == e.get(qn("w:chapSep"))), "-")

    def _hf(self, part) -> HeaderFooter:
        if part.is_linked_to_previous or not part.paragraphs:
            return HeaderFooter()
        lines, align = [], "left"
        for i, p in enumerate(part.paragraphs):
            txt = ""
            seite_feld = ueberspringen = False                       # der zwischengespeicherte Wert eines Seitenzahlfeldes ist kein Text
            for el in p._p.iter():
                if el.tag == qn("w:fldChar"):
                    art = el.get(qn("w:fldCharType"))
                    if art == "begin":
                        seite_feld = ueberspringen = False
                    elif art == "separate":
                        ueberspringen = seite_feld
                    elif art == "end":
                        seite_feld = ueberspringen = False
                elif el.tag == qn("w:instrText") and "PAGE" in (el.text or "").upper():
                    seite_feld = True
                if el.tag == qn("w:t"):
                    if not ueberspringen:
                        txt += el.text or ""
                elif el.tag == qn("w:tab"):
                    txt += "\t"
                elif el.tag == qn("w:instrText") and "PAGE" in (el.text or "").upper() \
                        and "NUMPAGES" not in (el.text or "").upper():
                    txt += "{PAGE}"
                elif el.tag == qn("w:instrText") and "NUMPAGES" in (el.text or "").upper():
                    txt += "{PAGES}"
                elif el.tag == qn("w:fldSimple"):
                    instr = (el.get(qn("w:instr")) or "").upper()
                    txt += "{PAGES}" if "NUMPAGES" in instr else "{PAGE}" if "PAGE" in instr else ""
            if i == 0:
                a = self._ausrichtung(p, p.style)
                align = {Qt.AlignHCenter: "center", Qt.AlignRight: "right"}.get(a, "left")
            lines.append(txt)
        text = "\n".join(lines).rstrip("\n")
        return HeaderFooter(text, align)

    # ---- Hauptlauf ---------------------------------------------------
