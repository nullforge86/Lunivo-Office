"""DOCX lesen: Seitengröße, Ränder, Abschnitte, Kopf- und Fußzeilen."""
from __future__ import annotations

from docx.oxml import OxmlElement

from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import (  # noqa: F401
    qn,
    HeaderFooter,
    PageSettings,
    mm_to_px,
    art_aus_docx,
    Qt,
    _xp,
)


# Kanten des Seitenrahmens (DOCX-Name, Kürzel)
_KANTEN = (("top", "t"), ("bottom", "b"), ("left", "l"), ("right", "r"))


def _kante_sichtbar(x) -> bool:
    """Hat die Rahmenkante (w:top …) eine sichtbare Linie?"""
    return x is not None and x.get(qn("w:val"), "none") not in ("none", "nil")


# Seitenmaße: (Feld der Seiteneinrichtung, Angabe im Abschnitt, Ersatzwert in mm). Fehlt eine Angabe, gilt der Wert des Dateiformats:
# Papier „Letter“ (8,5 × 11 Zoll) mit 1 Zoll Rand — so setzen es auch andere Textprogramme.
_SEITENMASSE = (("width_mm", "page_width", 215.9), ("height_mm", "page_height", 279.4), ("margin_top_mm", "top_margin", 25.4),
                ("margin_bottom_mm", "bottom_margin", 25.4), ("margin_left_mm", "left_margin", 25.4), ("margin_right_mm", "right_margin", 25.4))


# Wo jedes Seitenmaß in w:sectPr steht: (Element, Attribut)
_MASS_ORT = {"page_width": ("w:pgSz", "w:w"), "page_height": ("w:pgSz", "w:h"), "top_margin": ("w:pgMar", "w:top"),
             "bottom_margin": ("w:pgMar", "w:bottom"), "left_margin": ("w:pgMar", "w:left"), "right_margin": ("w:pgMar", "w:right")}


class SeiteMixin:
    """DOCX lesen: Seitengröße, Ränder, Abschnitte, Kopf- und Fußzeilen."""

    # ---- Seite -------------------------------------------------------
    def read_page(self) -> PageSettings:
        """Einrichtung des ERSTEN Abschnitts; weitere Abschnitte stehen als Umbrüche im Text (siehe editor/seite/abschnitte.py)."""
        self._abschnitt_sichern()
        return self._section_page(self.d.sections[0], erster=True)

    @staticmethod
    def _mass_roh(s, quelle: str):
        """Ein Seitenmaß, das als Kommazahl in der Datei steht (im Format nicht erlaubt, kommt aber vor): gerundet lesen."""
        from docx.shared import Twips
        el, attr = _MASS_ORT[quelle]
        knoten = s._sectPr.find(qn(el))
        try:
            return Twips(round(float(knoten.get(qn(attr))))) if knoten is not None else None
        except (ValueError, TypeError):
            return None

    def _abschnitt_sichern(self) -> None:
        """Ein Dokument ohne Abschnittsangabe (w:sectPr fehlt, im Dateiformat erlaubt) bekommt eine leere: alles Weitere liest dann die
        Ersatzwerte statt abzubrechen. Nur im Speicher, die Datei bleibt unberührt."""
        body = self.d.element.body
        if body.find(qn("w:sectPr")) is None and not self.d.sections:
            body.append(OxmlElement("w:sectPr"))

    def _section_page(self, s, erster: bool = False, basis: PageSettings | None = None) -> PageSettings:
        ps = PageSettings()
        fehlt = False
        for feld, quelle, ersatz_mm in _SEITENMASSE:
            try:
                wert = getattr(s, quelle, None)
            except (ValueError, TypeError):                      # Maß in der Datei ist keine ganze Zahl: wie fehlend behandeln
                wert = self._mass_roh(s, quelle)
            fehlt |= wert is None
            setattr(ps, feld, wert.mm if wert is not None else ersatz_mm)
        if fehlt:
            self.report.warn("Seitengröße oder Ränder fehlen; es gilt das Format „Letter“ mit 2,54 cm Rand wie im Dateiformat vorgesehen.")
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
                self._hf_bild_im_text(angabe, dr, ort, s, ps)
            elif angabe["bv"] == "absatz":
                self._hf_bild_am_absatz(angabe, ort, s, ps)
            out.append(angabe)
        for shape in _xp(teil._element, ".//w:pict//v:shape"):                 # ältere Textfelder und Formen (VML) in Kopf-/Fußzeilen
            frei = self._vml_frei(shape)
            if not frei:
                continue
            angabe, bild = frei
            angabe["ort"], angabe["bild"] = ort, bild
            if angabe["bv"] == "absatz":
                self._hf_bild_am_absatz(angabe, ort, s, ps)
            out.append(angabe)
        return out

    @staticmethod
    def _hf_abstand_mm(s, ort: str) -> float:
        """Abstand der Kopf- bzw. Fußzeile vom Seitenrand in mm (ersatzweise 12,7)."""
        try:
            return (s.header_distance if ort.startswith("kopf") else s.footer_distance).mm
        except Exception:                                                  # noqa: BLE001
            return 12.7

    def _hf_bild_im_text(self, angabe: dict, dr, ort: str, s, ps: PageSettings) -> None:
        ind = _xp(dr, "ancestor::w:p[1]/w:pPr/w:ind/@w:left")
        try:
            angabe["xh"] = float(ind[0]) / 15.0 if ind else 0.0                      # Twips → px
        except ValueError:
            angabe["xh"] = 0.0
        angabe["bh"] = "rand"
        abstand = self._hf_abstand_mm(s, ort)
        angabe["bv"] = "seite"
        angabe["yv"] = mm_to_px(abstand) if ort.startswith("kopf") else mm_to_px(ps.height_mm - abstand) - angabe["h"]
        angabe["hinter"] = False

    def _hf_bild_am_absatz(self, angabe: dict, ort: str, s, ps: PageSettings) -> None:
        abstand = self._hf_abstand_mm(s, ort)
        if ort.startswith("kopf"):
            angabe["yv"] = mm_to_px(abstand) + angabe["yv"]
        else:
            angabe["yv"] = mm_to_px(ps.height_mm - abstand) - 20 + angabe["yv"]
        angabe["bv"] = "seite"

    def _abschnitt_beginn(self, s) -> str:
        from lunivo_writer.editor.seite.abschnitte import VOM_DOCX
        t = s._sectPr.find(qn("w:type"))
        return VOM_DOCX.get(t.get(qn("w:val")) if t is not None else "nextPage", "naechste")

    def _seitenschmuck(self, ps: PageSettings, sect) -> None:
        """Seitenfarbe, Zeilennummern, Spalten, Standardtabstopp, Silbentrennung und Seitenrahmen."""
        bg = self.d.element.find(qn("w:background"))
        if bg is not None:
            c = bg.get(qn("w:color"))
            if c and c.lower() not in ("auto", "ffffff"):
                ps.color = "#" + c.lower()
        ln = sect._sectPr.find(qn("w:lnNumType"))
        if ln is not None:
            ps.zeilennummern = True
            ps.zeilennummern_neu = "seite" if ln.get(qn("w:restart")) == "newPage" else ""
        self._spalten_lesen(ps, sect._sectPr.find(qn("w:cols")))
        self._standardtabstopp(self.d.settings.element.find(qn("w:defaultTabStop")))
        ah = self.d.settings.element.find(qn("w:autoHyphenation"))
        if ah is not None and ah.get(qn("w:val"), "true").lower() not in ("false", "0", "off"):
            ps.silbentrennung = True
        pb = sect._sectPr.find(qn("w:pgBorders"))
        if pb is not None:
            self._seitenrahmen_lesen(ps, pb)

    @staticmethod
    def _spalten_lesen(ps: PageSettings, co) -> None:
        if co is None:
            return
        try:
            n = int(co.get(qn("w:num"), "1"))
        except ValueError:
            n = 1
        if n > 1:
            ps.spalten = min(n, 4)
            ps.spalten_abstand_mm = int(co.get(qn("w:space"), "720")) / 1440 * 25.4
            ps.spalten_linie = co.get(qn("w:sep"), "0").lower() in ("1", "true", "on")
            ps.spalten_raster_mm = SeiteMixin._spaltenraster(co, ps.spalten)

    @staticmethod
    def _spaltenraster(co, n: int):
        """Ungleich breite Spalten (``w:equalWidth="0"`` mit ``w:col`` je Spalte: Breite und Abstand danach in Zwanzigstelpunkt) → [[Breite, Abstand]] in mm,
        sonst None (gleich breit). Stimmt die Zahl der Spalten nicht, gilt gleich breit."""
        if (co.get(qn("w:equalWidth"), "1") or "1").lower() in ("1", "true", "on"):
            return None
        cols = co.findall(qn("w:col"))
        if len(cols) < 2:
            return None
        try:
            roh = [(int(c.get(qn("w:w"), "0")), int(c.get(qn("w:space"), "0"))) for c in cols[:n]]
        except ValueError:
            return None
        if len(roh) != n or min(b for b, _a in roh) <= 0:
            return None
        return [[b / 1440 * 25.4, a / 1440 * 25.4] for b, a in roh]

    def _standardtabstopp(self, dt) -> None:
        """Standardtabstopps des Dokuments (Twips) in die Textoptionen übernehmen."""
        if dt is not None and dt.get(qn("w:val"), "").isdigit() and int(dt.get(qn("w:val"))) > 0:
            opt = self.doc.defaultTextOption()
            opt.setTabStopDistance(mm_to_px(int(dt.get(qn("w:val"))) / 1440 * 25.4))
            self.doc.setDefaultTextOption(opt)

    def _seitenrahmen_lesen(self, ps: PageSettings, pb) -> None:
        """Seitenrahmen (w:pgBorders): Linie der ersten sichtbaren Kante, Seiten, Kunstrahmen, Abstände und Einstellungen des Dokuments."""
        e = next((x for x in (pb.find(qn("w:top")), pb.find(qn("w:left")), pb.find(qn("w:bottom")), pb.find(qn("w:right")))
                  if _kante_sichtbar(x)), None)
        if e is None:
            return
        ps.border = self._seitenrahmen_linie(pb, e)
        self._seitenrahmen_zusatz(ps.border, pb, e.get(qn("w:val")))

    @staticmethod
    def _seitenrahmen_linie(pb, e) -> dict:
        """Seiten mit Linie, Farbe, Stärke, Art und Abstand zum Seitenrand aus der ersten sichtbaren Kante ``e``."""
        col = (e.get(qn("w:color")) or "000000")
        da = "".join(k for x, k in _KANTEN if _kante_sichtbar(pb.find(qn(f"w:{x}"))))
        return {"seiten": da or "tblr", "farbe": "#" + (col if col.lower() != "auto" else "000000").lower(),
                "breite_pt": int(e.get(qn("w:sz")) or 8) / 8.0,
                "art": art_aus_docx(e.get(qn("w:val"))),
                "abstand_mm": int(e.get(qn("w:space")) or 24) / 72 * 25.4}

    def _seitenrahmen_zusatz(self, border: dict, pb, wert) -> None:
        """Kunstrahmen, Messung vom Text, Abstände je Seite, Vordergrund und die Einstellungen des Dokuments (Kopf-/Fußzeile, Ausrichtung)."""
        from lunivo_writer.editor.seite.seitenrahmen import KUNST
        if wert in [k for k, _n in KUNST if k]:                              # Kunstrahmen
            border["kunst"] = wert
        if pb.get(qn("w:offsetFrom")) == "text":                              # Abstand vom Text, je Seite (pt)
            border["messen"] = "text"
        ab = [int((pb.find(qn(f"w:{x}")).get(qn("w:space")) if pb.find(qn(f"w:{x}")) is not None else None) or 0) for x in ("top", "bottom", "left", "right")]
        border["abstand"] = ",".join(str(x) for x in ab)
        border["vordergrund"] = pb.get(qn("w:zOrder"), "front") != "back"
        st = self.d.settings.element
        border["kopf"] = st.find(qn("w:bordersDoNotSurroundHeader")) is None
        border["fuss"] = st.find(qn("w:bordersDoNotSurroundFooter")) is None
        border["ausrichten"] = st.find(qn("w:alignBordersAndEdges")) is not None

    def _aussen_innen(self, s, ps: PageSettings) -> None:
        """Gerade Seiten mit gespiegelter Ausrichtung bei gleichem Text: das ist „außen“ (ungerade rechts) bzw. „innen“ (ungerade links)."""
        try:
            if not self.d.settings.odd_and_even_pages_header_footer:
                return
            for attr, teil in (("header", s.even_page_header), ("footer", s.even_page_footer)):
                self._gerade_zeile(ps, attr, teil)
        except Exception:                                                  # noqa: BLE001
            pass

    def _gerade_zeile(self, ps: PageSettings, attr: str, teil) -> None:
        """Kopf- bzw. Fußzeile der geraden Seiten: gespiegelt (außen/innen) oder eigene Zeilen."""
        hf, gerade = getattr(ps, attr), self._hf(teil)
        if hf.text and gerade.text == hf.text and {hf.align, gerade.align} == {"left", "right"}:
            hf.align = "aussen" if hf.align == "right" else "innen"
        elif not teil.is_linked_to_previous and (gerade.text != hf.text or gerade.align != hf.align):
            ps.diff_even = True                          # eigene Zeilen für gerade Seiten
            setattr(ps, "even_" + attr, gerade)

    def _seitenzahl_art(self, s, ps: PageSettings) -> None:
        """w:pgNumType: Zahlenart, „Beginnen mit“, Kapitelnummer."""
        from lunivo_writer.editor.seite import seitenzahl as SZ
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
            if i == 0:
                a = self._ausrichtung(p, p.style)
                align = {Qt.AlignHCenter: "center", Qt.AlignRight: "right"}.get(a, "left")
            lines.append(self._hf_absatztext(p))
        text = "\n".join(lines).rstrip("\n")
        return HeaderFooter(text, align, self._hf_format(part), self._hf_laeufe(part, text))

    def _hf_laeufe(self, part, text: str) -> list:
        """Textstücke der Kopf-/Fußzeile mit ihrem eigenen Format (Zeilen durch „\\n“ getrennt). Leer, wenn Felder im Spiel sind
        oder die Stücke nicht genau den Text ergeben: dann gilt das eine Format der Zeile."""
        from docx.text.run import Run
        laeufe: list = []
        for i, p in enumerate(part.paragraphs):
            if i:
                laeufe.append({"text": "\n", "fmt": {}})
            if p._p.xpath(".//w:fldChar | .//w:instrText | .//w:fldSimple"):
                return []
            for el in p._p.iter(qn("w:r")):
                stueck = "".join(self._hf_elementtext(c, False) for c in el if c.tag in (qn("w:t"), qn("w:tab")))
                if stueck:
                    laeufe.append({"text": stueck, "fmt": self._hf_zeichenformat(Run(el, p), p)})
        while laeufe and laeufe[-1]["text"] == "\n":
            laeufe.pop()
        if "".join(r["text"] for r in laeufe) != text:
            return []
        return laeufe

    def _hf_format(self, part) -> dict:
        """Zeichenformat der Kopf-/Fußzeile (Schrift, Größe, fett, kursiv, unterstrichen, Farbe) aus dem ersten Textlauf mit Text.
        Die Zeile hat ein einheitliches Format; wechselt das Format innerhalb der Zeile, gilt das des ersten Laufs."""
        from docx.text.run import Run
        for p in part.paragraphs:
            for el in p._p.iter(qn("w:r")):
                if not "".join(el.xpath(".//w:t/text()")).strip():
                    continue
                return self._hf_zeichenformat(Run(el, p), p)
        return {}

    def _hf_zeichenformat(self, run, p) -> dict:
        """Zeichenformat eines Laufs als Schlüssel für ``HeaderFooter.fmt`` (Schrift, Größe, fett, kursiv, unterstrichen, Farbe)."""
        cf = self._char_format(run, p)
        fmt: dict = {}
        fam = cf.fontFamilies()
        if fam:
            fmt["family"] = fam[0]
        if cf.fontPointSize() > 0:
            fmt["size_pt"] = round(cf.fontPointSize(), 1)
        fmt["bold"] = bool(cf.font().bold())
        fmt["italic"] = bool(cf.fontItalic())
        fmt["underline"] = bool(cf.fontUnderline())
        if cf.foreground().style():
            fmt["color"] = cf.foreground().color().name()
        return fmt

    @classmethod
    def _hf_absatztext(cls, p) -> str:
        """Text eines Kopf-/Fußzeilenabsatzes; Seitenzahlfelder werden zu {PAGE} / {PAGES}, ihr zwischengespeicherter Wert entfällt."""
        txt = ""
        seite_feld = ueberspringen = False                       # der zwischengespeicherte Wert eines Seitenzahlfeldes ist kein Text
        for el in p._p.iter():
            if el.tag == qn("w:fldChar"):
                art = el.get(qn("w:fldCharType"))
                if art == "separate":
                    ueberspringen = seite_feld
                elif art in ("begin", "end"):
                    seite_feld = ueberspringen = False
            elif el.tag == qn("w:instrText") and "PAGE" in (el.text or "").upper():
                seite_feld = True
            txt += cls._hf_elementtext(el, ueberspringen)
        return txt

    @staticmethod
    def _hf_elementtext(el, ueberspringen: bool) -> str:
        """Beitrag eines Elements zum Text: Text, Tabulator oder Platzhalter für Seitenzahl bzw. Seitenanzahl."""
        if el.tag == qn("w:t"):
            return "" if ueberspringen else (el.text or "")
        if el.tag == qn("w:tab"):
            return "\t"
        if el.tag == qn("w:instrText"):
            return SeiteMixin._hf_platzhalter(el.text or "")
        if el.tag == qn("w:fldSimple"):
            return SeiteMixin._hf_platzhalter(el.get(qn("w:instr")) or "")
        return ""

    @staticmethod
    def _hf_platzhalter(anweisung: str) -> str:
        """Feldanweisung → {PAGES} (NUMPAGES), {PAGE} (PAGE) oder leer."""
        text = anweisung.upper()
        if "NUMPAGES" in text:
            return "{PAGES}"
        return "{PAGE}" if "PAGE" in text else ""
