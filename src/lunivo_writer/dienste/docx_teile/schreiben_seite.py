"""DOCX schreiben: Seite, Abschnitte, Kopf- und Fußzeilen."""
from __future__ import annotations

from docx.enum.section import WD_SECTION

from lunivo_writer.dienste.docx_teile.schreiben_gemeinsam import (  # noqa: F401
    docx,
    WD_ORIENT,
    WD_ALIGN_PARAGRAPH,
    OxmlElement,
    qn,
    Mm,
    Farbe,
    docx_wert,
)


_ABSCHNITT_TYP = {"naechste": WD_SECTION.NEW_PAGE, "fortlaufend": WD_SECTION.CONTINUOUS,
                  "gerade": WD_SECTION.EVEN_PAGE, "ungerade": WD_SECTION.ODD_PAGE}
_KOPF_AUSRICHTUNG = {"center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT}


def _zeichenformat_schreiben(run, fmt: dict) -> None:
    """Schlüssel aus ``HeaderFooter.fmt`` (Schrift, Größe, fett, kursiv, unterstrichen, Farbe) als Zeichenformat des Laufs."""
    from docx.shared import Pt, RGBColor
    if fmt.get("family"):
        run.font.name = fmt["family"]
    if fmt.get("size_pt"):
        run.font.size = Pt(float(fmt["size_pt"]))
    if "bold" in fmt:
        run.font.bold = bool(fmt["bold"])
    if "italic" in fmt:
        run.font.italic = bool(fmt["italic"])
    if "underline" in fmt:
        run.font.underline = bool(fmt["underline"])
    if fmt.get("color"):
        try:
            run.font.color.rgb = RGBColor.from_string(str(fmt["color"]).lstrip("#").upper())
        except ValueError:
            pass
# Kindelemente von w:settings, vor denen die Rahmen-Einstellungen eingefügt werden (Reihenfolge nach ECMA-376)
_SETTINGS_DANACH = ("w:compat", "w:docVars", "w:rsids", "w:mathPr", "w:themeFontLang", "w:clrSchemeMapping",
                    "w:shapeDefaults", "w:decimalSymbol", "w:listSeparator")


class SeiteSchreiber:
    """DOCX schreiben: Seite, Abschnitte, Kopf- und Fußzeilen."""

    # ---- Seite --------------------------------------------------------
    def write_page(self):
        """Dokumentweite Einstellungen (Hintergrund, Silbentrennung) und der letzte Abschnitt in der Schlusseinrichtung des Textes."""
        from lunivo_writer.editor.seite import abschnitte as AB
        self.abschnitte = AB.alle_einrichtungen(self.q, self.page)
        self._ab_nr = 0
        self._dokument_ebene(self.page)
        typ, letzte = self.abschnitte[-1]
        self.write_section(self.d.sections[0], letzte, typ if len(self.abschnitte) > 1 else None, len(self.abschnitte) - 1)

    def write_section(self, s, p, typ: str | None = None, nr: int = 0):
        """Einen Abschnitt (python-docx Section) nach Einrichtung p schreiben; nr = Nummer des Abschnitts (für verknüpfte Kopfzeilen)."""
        s.page_width, s.page_height = Mm(p.width_mm), Mm(p.height_mm)
        s.orientation = WD_ORIENT.LANDSCAPE if p.landscape else WD_ORIENT.PORTRAIT
        s.top_margin, s.bottom_margin = Mm(p.margin_top_mm), Mm(p.margin_bottom_mm)
        s.left_margin, s.right_margin = Mm(p.margin_left_mm), Mm(p.margin_right_mm)
        s.header_distance, s.footer_distance = Mm(p.kopf_abstand_mm), Mm(p.fuss_abstand_mm)
        if typ:
            s.start_type = _ABSCHNITT_TYP.get(typ, WD_SECTION.NEW_PAGE)
        self._seitenschmuck(s, p)
        for part, hf, verknuepft, ort, *seite in self._kopf_fuss_paare(s, p):
            if nr > 0 and verknuepft:
                continue                                            # bleibt „mit vorherigem verknüpft“
            self._kopf_fuss_schreiben(part, hf, ort, seite[0] if seite else 1, p, nr)
        self._seitenzahl_art(s, p)

    def _kopf_fuss_paare(self, s, p) -> list:
        """Alle Kopf-/Fußzeilen des Abschnitts als (Teil, Inhalt, verknüpft, Ort[, Seitenart]); Erstseite und gerade Seiten nur bei Bedarf."""
        paare = [(s.header, p.header, p.kopf_verknuepft, "kopf"), (s.footer, p.footer, p.fuss_verknuepft, "fuss")]
        if p.diff_first:
            s.different_first_page_header_footer = True
            paare += [(s.first_page_header, p.first_header, p.kopf_verknuepft, "kopf1"), (s.first_page_footer, p.first_footer, p.fuss_verknuepft, "fuss1")]
        if self._gerade_seiten_getrennt():
            self.d.settings.odd_and_even_pages_header_footer = True
            kopf_g, fuss_g = (p.even_header, p.even_footer) if p.diff_even else (p.header, p.footer)
            paare += [(s.even_page_header, kopf_g, p.kopf_verknuepft, "kopf", 2), (s.even_page_footer, fuss_g, p.fuss_verknuepft, "fuss", 2)]
        return paare

    def _gerade_seiten_getrennt(self) -> bool:
        """„außen“/„innen“ brauchen getrennte Kopf-/Fußzeilen für gerade Seiten (w:evenAndOddHeaders gilt für das ganze Dokument);
        „Gerade und ungerade Seiten unterschiedlich“ (diff_even) schreibt die eigenen Zeilen für gerade Seiten."""
        return any(h.align in ("aussen", "innen") for _t, ps in self.abschnitte for h in (ps.header, ps.footer)) \
            or any(ps.diff_even for _t, ps in self.abschnitte)

    def _kopf_fuss_schreiben(self, part, hf, ort: str, seite: int, p, nr: int) -> None:
        """Text (mit Feldern) und freie Bilder einer Kopf- oder Fußzeile; leere Zeilen im ersten Abschnitt bleiben ungeschrieben."""
        bilder = [a for a in (getattr(p, "bilder", None) or []) if a.get("ort") == ort and a.get("bild") is not None]
        if hf.is_empty() and nr == 0 and not bilder:
            return
        part.is_linked_to_previous = False
        self._kopf_fuss_text(part, hf, seite)
        for a in bilder:
            self._frei_bild(part.paragraphs[0], a, a["bild"])

    def _kopf_fuss_text(self, part, hf, seite: int) -> None:
        from lunivo_writer.editor.seite import seitenzahl as SZ
        ausr = SZ.ausrichtung(hf.align, seite)
        absatz = part.paragraphs[0]
        absatz.alignment = _KOPF_AUSRICHTUNG.get(ausr, WD_ALIGN_PARAGRAPH.LEFT)
        for text, fmt in hf.laeufe():
            for k, stueck in enumerate(text.split("\n")):
                if k:                                                  # Zeilenende: neuer Absatz mit gleicher Ausrichtung
                    absatz = part.add_paragraph()
                    absatz.alignment = _KOPF_AUSRICHTUNG.get(ausr, WD_ALIGN_PARAGRAPH.LEFT)
                if stueck:
                    self._lauf_mit_format(absatz, stueck, fmt)

    def _lauf_mit_format(self, para, text: str, fmt: dict) -> None:
        """Text mit Seitenzahlfeldern in den Absatz schreiben; die Textstücke bekommen das Zeichenformat ``fmt``."""
        import re
        for tok in re.split(r"(\{PAGE\}|\{PAGES\})", text):
            if tok in ("{PAGE}", "{PAGES}"):
                self._field(para, "PAGE" if tok == "{PAGE}" else "NUMPAGES")
            elif tok:
                run = para.add_run(tok)
                _zeichenformat_schreiben(run, fmt or {})

    def _seitenzahl_art(self, s, p) -> None:
        """Zahlenart, „Beginnen mit“ und Kapitelnummer der Seitenzahl als w:pgNumType."""
        from lunivo_writer.editor.seite import seitenzahl as SZ
        sp = s._sectPr
        for alt in sp.findall(qn("w:pgNumType")):
            sp.remove(alt)
        if p.seiten_format == "dezimal" and not p.seiten_start and not p.kapitel_ebene:
            return
        e = OxmlElement("w:pgNumType")
        if p.seiten_format != "dezimal":
            e.set(qn("w:fmt"), SZ.DOCX_FORMAT.get(p.seiten_format, "decimal"))
        if p.seiten_start:
            e.set(qn("w:start"), str(int(p.seiten_start)))
        if p.kapitel_ebene:
            e.set(qn("w:chapStyle"), str(int(p.kapitel_ebene)))
            e.set(qn("w:chapSep"), next((d for z, _t, d in SZ.TRENNER if z == p.kapitel_trenner), "hyphen"))
        sp.insert_element_before(e, "w:cols", "w:formProt", "w:vAlign", "w:noEndnote", "w:titlePg", "w:textDirection", "w:bidi", "w:rtlGutter",
                                 "w:docGrid", "w:printerSettings", "w:sectPrChange")

    def _abschnitt_ende(self, para) -> None:
        """Am Ende des Absatzes, der einen Abschnitt beschließt: dessen Einrichtung als w:sectPr in den Absatz schreiben."""
        from docx.section import Section
        k = self._ab_nr
        self._ab_nr += 1
        typ, ps = self.abschnitte[k]
        sp = OxmlElement("w:sectPr")
        ppr = para._p.get_or_add_pPr()
        nach = ppr.find(qn("w:pPrChange"))
        (nach.addprevious(sp) if nach is not None else ppr.append(sp))
        self.write_section(Section(sp, self.d.part), ps, typ if k > 0 else None, k)

    def _seitenschmuck(self, sect, p) -> None:
        """Seitenrahmen, Spalten, Zeilennummern (je als Element in w:sectPr) und Hinweis zum Wasserzeichen."""
        sp = sect._sectPr
        self._seitenrahmen(sp, p)
        self._spalten(sp, p)
        self._zeilennummern(sp, p)
        if p.watermark and p.watermark.get("text") and not getattr(self, "_wasserzeichen_gemeldet", False):
            self._wasserzeichen_gemeldet = True
            self.report.warn("Das Wasserzeichen wird in der DOCX-Datei nicht gespeichert (nur Anzeige, PDF und Druck).")

    @staticmethod
    def _alte_entfernen(sp, tag: str) -> None:
        for alt in sp.findall(qn(tag)):
            sp.remove(alt)

    @staticmethod
    def _nach_anker_einfuegen(sp, el, *tags: str) -> None:
        """Element hinter das erste vorhandene der Ankerelemente setzen, sonst ans Ende."""
        anker = next((x for x in (sp.find(qn(t)) for t in tags) if x is not None), None)
        (anker.addnext(el) if anker is not None else sp.append(el))

    def _seitenrahmen(self, sp, p) -> None:
        """Seitenrahmen als w:pgBorders und die zugehörigen Einstellungen des Dokuments."""
        self._alte_entfernen(sp, "w:pgBorders")
        if not p.border:
            return
        b = p.border
        from lunivo_writer.editor.seite.seitenrahmen import abstaende_pt
        pb = OxmlElement("w:pgBorders")
        pb.set(qn("w:offsetFrom"), "text" if b.get("messen") == "text" else "page")
        pb.set(qn("w:zOrder"), "front" if b.get("vordergrund", True) else "back")
        ab = dict(zip(("top", "bottom", "left", "right"), abstaende_pt(b)))
        for seite, kurz in (("top", "t"), ("left", "l"), ("bottom", "b"), ("right", "r")):
            if kurz not in b.get("seiten", "tblr"):
                continue
            e = OxmlElement(f"w:{seite}")
            e.set(qn("w:val"), b["kunst"] if b.get("kunst") else docx_wert(b.get("art", "einfach")))
            e.set(qn("w:sz"), str(max(2, int(round(b.get("breite_pt", 1.0) * 8)))))
            e.set(qn("w:space"), str(min(31, int(round(ab[seite])))))
            e.set(qn("w:color"), b.get("farbe", Farbe.SCHWARZ).lstrip("#").upper())
            pb.append(e)
        self._rahmen_einstellungen(b)
        self._nach_anker_einfuegen(sp, pb, "w:pgMar")

    def _rahmen_einstellungen(self, b: dict) -> None:
        """Kopf-/Fußzeile umgeben, am Seitenrand ausrichten (Einstellungen des Dokuments)."""
        st = self.d.settings.element
        for tag, an in (("w:bordersDoNotSurroundHeader", not b.get("kopf")), ("w:bordersDoNotSurroundFooter", not b.get("fuss")),
                        ("w:alignBordersAndEdges", bool(b.get("ausrichten")))):
            self._alte_entfernen(st, tag)
            if an:
                st.insert_element_before(OxmlElement(tag), *_SETTINGS_DANACH)

    def _spalten(self, sp, p) -> None:
        self._alte_entfernen(sp, "w:cols")
        if p.spalten > 1:
            co = OxmlElement("w:cols")
            co.set(qn("w:num"), str(int(p.spalten)))
            co.set(qn("w:space"), str(int(round(p.spalten_abstand_mm / 25.4 * 1440))))
            if p.spalten_linie:
                co.set(qn("w:sep"), "1")
            raster = p.spalten_raster_mm
            if raster and len(raster) == int(p.spalten):                  # ungleich breite Spalten: je Spalte Breite und Abstand danach
                co.set(qn("w:equalWidth"), "0")
                for i, (b, a) in enumerate(raster):
                    c = OxmlElement("w:col")
                    c.set(qn("w:w"), str(int(round(float(b) / 25.4 * 1440))))
                    if i < len(raster) - 1:
                        c.set(qn("w:space"), str(int(round(float(a) / 25.4 * 1440))))
                    co.append(c)
            self._nach_anker_einfuegen(sp, co, "w:pgMar")

    def _zeilennummern(self, sp, p) -> None:
        self._alte_entfernen(sp, "w:lnNumType")
        if p.zeilennummern:
            ln = OxmlElement("w:lnNumType")
            ln.set(qn("w:countBy"), "1"); ln.set(qn("w:restart"), "newPage" if p.zeilennummern_neu == "seite" else "continuous")
            self._nach_anker_einfuegen(sp, ln, "w:pgBorders", "w:pgMar")
