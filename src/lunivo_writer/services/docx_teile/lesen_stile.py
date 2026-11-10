"""DOCX lesen: Formatvorlagen, Schrift und Zeichenformat (Vererbung, Standardwerte, Hervorhebung)."""
from __future__ import annotations

from docx.enum.text import WD_UNDERLINE as U

from lunivo_writer.services.docx_teile.lesen_gemeinsam import (  # noqa: F401
    Optional,
    docx,
    qn,
    Paragraph,
    QBrush,
    QColor,
    QFont,
    QTextCharFormat,
    Farbe,
    P_VERSTECKT,
    HEADING_DEFAULT_PT,
    NAMED_STYLE_DEFAULT,
    Qt,
)


# Unterstreichung Word → eigene Art; Betonungszeichen Word → Lunivo
_UNTER_ART = {U.WORDS: "woerter", U.DOUBLE: "doppelt", U.THICK: "dick", U.DOTTED: "gepunktet", U.DOTTED_HEAVY: "dick_gepunktet", U.DASH: "gestrichelt",
              U.DASH_HEAVY: "dick_gestrichelt", U.DASH_LONG: "lang", U.DASH_LONG_HEAVY: "dick_lang", U.DOT_DASH: "strichpunkt",
              U.DOT_DASH_HEAVY: "dick_strichpunkt", U.DOT_DOT_DASH: "strichpunktpunkt", U.DOT_DOT_DASH_HEAVY: "dick_strichpunktpunkt",
              U.WAVY: "wellig", U.WAVY_HEAVY: "dick_wellig", U.WAVY_DOUBLE: "doppelwellig"}
_BETONUNG = {"dot": "punkt", "circle": "kreis", "comma": "komma", "underDot": "unten"}


class StilMixin:
    """DOCX lesen: Formatvorlagen, Schrift und Zeichenformat (Vererbung, Standardwerte, Hervorhebung)."""

    # ---- Auflösung der Vererbung -------------------------------------
    def _standard_stil(self, art):
        try:
            return self.d.styles.default(art)
        except Exception:
            return None

    def _ps(self, para):
        """Absatzvorlage (mit Zwischenspeicher)."""
        ppr = para._p.pPr
        sid = ppr.pStyle.val if ppr is not None and ppr.pStyle is not None else None
        return self._stile_id.get(sid) or self._standard_absatz

    def _rs(self, run):
        rpr = run._r.rPr
        sid = rpr.rStyle.val if rpr is not None and rpr.rStyle is not None else None
        return self._stile_id.get(sid) if sid else None

    def _kette(self, style):
        k = self._ketten.get(id(style.element))
        if k is None:
            k, gesehen, s = [], set(), style
            while s is not None and id(s.element) not in gesehen:
                gesehen.add(id(s.element)); k.append(s)
                b = self._basis.get(id(s.element), False)
                if b is False:
                    b = s.base_style
                    self._basis[id(s.element)] = b
                s = b
            self._ketten[id(style.element)] = k
        return k

    def _style_attr(self, style, getter):
        for s in self._kette(style):
            v = getter(s)
            if v is not None:
                return v
        return None

    def _stil_font(self, style, attr):
        key = (id(style.element), attr)
        if key not in self._attr_cache:
            self._attr_cache[key] = self._style_attr(style, lambda s: getattr(s.font, attr) if attr != "name" else s.font.name)
        return self._attr_cache[key]

    def _font_name(self, run, para) -> str:
        v = run.font.name
        rs = self._rs(run) if hasattr(run, "_r") else None
        if v is None and rs is not None:
            v = self._stil_font(rs, "name")
        if v is None and para is not None:
            v = self._stil_font(self._ps(para), "name")
        if v is None and self.normal is not None:
            v = self.normal.font.name
        return v or self.def_font or "Calibri"

    def _font_size_pt(self, run, para) -> float:
        v = self._font_size_gesetzt(run, para)
        if v is not None:
            return v.pt
        ersatz = self._font_size_ersatz(para)
        if ersatz:
            return ersatz
        if self.normal is not None and self.normal.font.size is not None:
            return self.normal.font.size.pt
        return self.def_size or 11.0

    def _font_size_gesetzt(self, run, para):
        """Größe am Lauf, sonst aus dessen Zeichenvorlage, sonst aus der Absatzvorlage; sonst None."""
        v = run.font.size
        rs = self._rs(run) if hasattr(run, "_r") else None
        if v is None and rs is not None:
            v = self._stil_font(rs, "size")
        if v is None and para is not None:
            v = self._stil_font(self._ps(para), "size")
        return v

    def _font_size_ersatz(self, para):
        """Standardgröße einer Überschrift oder benannten Vorlage, wenn nirgends eine Größe steht; sonst None."""
        if para is None:
            return None
        lvl = self._heading_level(para)
        if lvl:
            return HEADING_DEFAULT_PT[lvl]
        nm = NAMED_STYLE_DEFAULT.get(self._ps(para).name)
        return nm[0] if nm and nm[0] else None

    def _flag(self, run, para, attr):
        v = getattr(run.font, attr)
        rs = self._rs(run) if hasattr(run, "_r") else None
        if v is None and rs is not None:
            v = self._stil_font(rs, attr)
        if v is None and para is not None:
            v = self._stil_font(self._ps(para), attr)
        return v

    def _heading_level(self, para) -> int:
        st = self._ps(para)
        n = st.name if st is not None else ""
        if n.startswith("Heading ") and n[8:].isdigit():
            return max(1, min(9, int(n[8:])))
        return 0

    # ---- Zeichenformat -----------------------------------------------
    def _char_format(self, run, para) -> QTextCharFormat:
        """Zeichenformat eines Textlaufs. Es hängt nur von dessen Eigenschaften (rPr) und den Vorlagen von Lauf und Absatz ab; Läufe mit gleichem
        Schlüssel (in langen Dokumenten fast alle) teilen sich das Ergebnis, statt die Vorlagenkette jedes Mal neu aufzulösen."""
        try:
            from lxml import etree
            rpr = run._r.rPr
            schluessel = (etree.tostring(rpr) if rpr is not None else b"", id(self._rs(run).element) if self._rs(run) is not None else 0,
                          id(self._ps(para).element) if para is not None and self._ps(para) is not None else 0, para is None)
        except Exception:
            return self._char_format_roh(run, para)
        zw = self.__dict__.setdefault("_cf_zw", {})
        f = zw.get(schluessel)
        if f is None:
            f = zw[schluessel] = self._char_format_roh(run, para)
        return QTextCharFormat(f)

    def _char_format_roh(self, run, para) -> QTextCharFormat:
        f = QTextCharFormat()
        f.setFontFamilies([self._font_name(run, para)])
        f.setFontPointSize(self._font_size_pt(run, para))
        self._cf_stil(run, para, f)
        self._cf_unterstreichung(run, f)
        self._cf_kontur_abstand(run, f)
        self._cf_hochtief_farben(run, para, f)
        self._schrift_zusatz(run._r.rPr, f)
        from lunivo_writer.editor.text import texteffekt
        texteffekt.aus_rpr(run._r.rPr, f)
        return f

    def _cf_stil(self, run, para, f: QTextCharFormat) -> None:
        """Fett, Kursiv (auch aus Überschrift und Standardvorlage) und das Unterstreichungs-Kennzeichen."""
        lvl = self._heading_level(para) if para is not None else 0
        named = NAMED_STYLE_DEFAULT.get(self._ps(para).name) if para is not None else None
        bold = self._flag(run, para, "bold")
        if bold is None and lvl:
            bold = True
        f.setFontWeight(QFont.Bold if bold else QFont.Normal)
        ital = self._flag(run, para, "italic")
        if ital is None and named:
            ital = named[2]
        f.setFontItalic(bool(ital))
        f.setFontUnderline(bool(self._flag(run, para, "underline")))

    @staticmethod
    def _cf_unterstreichung(run, f: QTextCharFormat) -> None:
        """Besondere Unterstreichungsarten (doppelt, gestrichelt, wellig …) als eigenes Zeichenformat."""
        raw = run.font.underline
        if raw not in (None, True, False):
            from lunivo_writer.editor.text.unterstreichung import unter_format
            art = _UNTER_ART.get(raw)
            if art:
                f.merge(unter_format(art))

    @staticmethod
    def _cf_kontur_abstand(run, f: QTextCharFormat) -> None:
        """Kontur, verborgener Text, Zeichenabstand."""
        if run.font.outline:
            from PySide6.QtGui import QPen
            f.setTextOutline(QPen(QColor(Farbe.SCHWARZ)))
        if run.font.hidden:
            f.setProperty(P_VERSTECKT, 1)
        rpr = run._r.rPr
        sp = rpr.find(qn("w:spacing")) if rpr is not None else None
        if sp is not None and sp.get(qn("w:val")):
            f.setFontLetterSpacingType(QFont.AbsoluteSpacing)
            f.setFontLetterSpacing(int(sp.get(qn("w:val"))) / 20 / 0.75)

    def _cf_hochtief_farben(self, run, para, f: QTextCharFormat) -> None:
        """Durchgestrichen, Hoch-/Tiefstellung, Schriftfarbe, Hervorhebung, Versalien."""
        f.setFontStrikeOut(bool(self._flag(run, para, "strike")))
        if self._flag(run, para, "superscript"):
            f.setVerticalAlignment(QTextCharFormat.AlignSuperScript)
        elif self._flag(run, para, "subscript"):
            f.setVerticalAlignment(QTextCharFormat.AlignSubScript)
        col = run.font.color
        if col is not None and col.rgb is not None:
            f.setForeground(QBrush(QColor("#" + str(col.rgb))))
        hl = self._highlight(run)
        if hl:
            f.setBackground(QBrush(QColor(hl)))
        if self._flag(run, para, "all_caps"):
            f.setFontCapitalization(QFont.AllUppercase)
        elif self._flag(run, para, "small_caps"):
            f.setFontCapitalization(QFont.SmallCaps)

    def _schrift_zusatz(self, rpr, f: QTextCharFormat) -> None:
        """Schrift für asiatische und komplexe Zeichen, Betonungszeichen und doppeltes Durchstreichen (Fenster „Schriftart“)."""
        if rpr is None:
            return
        self._zs_schriften(rpr, f)
        self._zs_skalieren_position(rpr, f)
        self._zs_raster_durchstreichung_betonung(rpr, f)

    @staticmethod
    def _zs_schriften(rpr, f: QTextCharFormat) -> None:
        """Schrift für asiatische (eastAsia) und komplexe (cs) Zeichen; weitere Familien kommen hinter die Hauptschrift."""
        from lunivo_writer.editor.dokument.zusatz import P_FONT_ASIEN, P_FONT_KOMPLEX
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            return
        haupt = f.fontFamilies()[0] if f.fontFamilies() else ""
        fam = [haupt]
        for attr, prop in (("w:eastAsia", P_FONT_ASIEN), ("w:cs", P_FONT_KOMPLEX)):
            n = rf.get(qn(attr))
            if n and n != haupt:
                schnitt, gr = StilMixin._zs_komplex_schnitt(rpr) if attr == "w:cs" else ("", "")
                f.setProperty(prop, f"{n}|{schnitt.strip()}|{gr}")
                fam.append(n)
        if len(fam) > 1:
            f.setFontFamilies(list(dict.fromkeys(fam)))

    @staticmethod
    def _zs_komplex_schnitt(rpr):
        """Schnitt („Fett Kursiv“) und Größe der komplexen Schrift → (Schnitt, Größe in pt als Text)."""
        bcs, ics = rpr.find(qn("w:bCs")), rpr.find(qn("w:iCs"))
        schnitt = ("Fett " if bcs is not None and bcs.get(qn("w:val")) not in ("0", "false") else "") + \
                  ("Kursiv" if ics is not None and ics.get(qn("w:val")) not in ("0", "false") else "")
        sz = rpr.find(qn("w:szCs"))
        return schnitt, (f"{int(sz.get(qn('w:val'))) / 2:g}" if sz is not None and sz.get(qn("w:val")) else "")

    @staticmethod
    def _zs_skalieren_position(rpr, f: QTextCharFormat) -> None:
        w_ = rpr.find(qn("w:w"))
        if w_ is not None and w_.get(qn("w:val")) and w_.get(qn("w:val")).isdigit():
            f.setFontStretch(int(w_.get(qn("w:val"))))                                    # Skalieren
        pos = rpr.find(qn("w:position"))
        if pos is not None and pos.get(qn("w:val")) not in (None, "0"):
            try:                                                                          # Position in Halbpunkten → Prozent der Schriftgröße
                gr = f.fontPointSize() or 11.0
                f.setBaselineOffset(int(pos.get(qn("w:val"))) / 2 / gr * 100)
            except ValueError:
                pass

    @staticmethod
    def _zs_raster_durchstreichung_betonung(rpr, f: QTextCharFormat) -> None:
        from lunivo_writer.editor.dokument.zusatz import P_BETONUNG, P_DOPPELT, P_RASTER
        sg = rpr.find(qn("w:snapToGrid"))
        if sg is not None and sg.get(qn("w:val")) in ("0", "false", "off"):
            f.setProperty(P_RASTER, 0)
        if rpr.find(qn("w:dstrike")) is not None and rpr.find(qn("w:dstrike")).get(qn("w:val")) not in ("0", "false"):
            f.setProperty(P_DOPPELT, 1); f.setFontStrikeOut(True)
        em = rpr.find(qn("w:em"))
        if em is not None and em.get(qn("w:val")) not in (None, "none"):
            f.setProperty(P_BETONUNG, _BETONUNG.get(em.get(qn("w:val")), "punkt"))

    def _highlight(self, run) -> Optional[str]:
        rpr = run._r.rPr
        if rpr is None:
            return None
        h = rpr.find(qn("w:highlight"))
        if h is not None:
            return self._HL.get(h.get(qn("w:val")))
        shd = rpr.find(qn("w:shd"))
        if shd is not None:
            fill = shd.get(qn("w:fill"))
            if fill and fill.lower() not in ("auto", "ffffff"):
                return "#" + fill
        return None

    def _ausrichtung(self, para: Paragraph, st):
        """w:jc roh lesen — python-docx kennt „start“/„end“ nicht und bricht sonst ab."""
        def roh(ppr):
            if ppr is None:
                return None
            jc = ppr.find(qn("w:jc"))
            return jc.get(qn("w:val")) if jc is not None else None
        v = roh(para._p.pPr)
        s = st
        while v is None and s is not None:
            v = roh(s.element.pPr)
            s = s.base_style
        return self._JC.get(v, Qt.AlignLeft)
