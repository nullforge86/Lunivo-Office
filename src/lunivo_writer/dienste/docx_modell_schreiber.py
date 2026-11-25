"""DOCX direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben — ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

Umfang: Absätze mit Formatvorlage (Überschriften, Titel, Untertitel, Zitat), Ausrichtung, Einzügen, Abständen, Zeilenabstand, Seitenumbruch und Hintergrund; Textläufe
mit Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe, Marker, Kapitälchen, Großbuchstaben und Verweisen; Listen mit allen Ebenen (Zahlenart,
Aufzählungszeichen, Einzug, Neubeginn); Tabellen mit verbundenen Zellen, Spaltenbreiten, Zeilenhöhen, Kopfzeilen, Rahmen, Füllung und senkrechter Ausrichtung samt
verschachtelten Tabellen; Bilder im Text (Alternativtext, JPEG/PNG/GIF/BMP/TIFF im Original, sonst PNG); Seitengröße, Ränder, Kopf- und Fußzeile mit Seitenzahlfeldern;
Titel und Autor.

Dazu: Formen und Textfelder (im Text und frei verankert), Seitenrahmen, Wasserzeichen (Text), Absatzrahmen, Inhaltssteuerelemente (``w:sdt``), Zeichen- und Tabellenvorlagen
und alle Eigenschaften, die der Leser nicht selbst abbildet und als ``docx_roh`` im Modell erhalten hat (``docx_erhalt``).

Alles, was dieser Schreiber nicht abbildet (zum Beispiel Quellen, Bild-Wasserzeichen, Gruppen und verknüpfte Textfelder), meldet ``docx_dokument_daten`` mit ``None``: Der Aufrufer
nimmt dann den bisherigen Weg, damit nichts still verloren geht."""
from __future__ import annotations

import io
import re

from lunivo_writer.kern.dokument.bildformat import format_erkennen
from lunivo_writer.kern.dokument.dokument import Absatz, Dokument, InlineObjekt, Lauf, Rahmen, Tabelle
from lunivo_writer.kern.dokument.formatvorlagen import wirksames_absatzformat, wirksames_zeichenformat
from lunivo_writer.dienste import docx_erhalt as E, docx_formen as F
from lunivo_writer.kern.dokument.bericht import IOReport
from lunivo_writer.kern.dokument.seite import HeaderFooter, PageSettings

PT_JE_PX = 0.75
EMU_JE_PX = 9525
TWIP_JE_PX = 15

_STIL = {"Standard": "Normal", "Titel": "Title", "Untertitel": "Subtitle", "Zitat": "Quote", "Kein Abstand": "No Spacing",
         **{f"Überschrift {n}": f"Heading {n}" for n in range(1, 10)}}
_ZEICHEN = {"schrift", "groesse_pt", "fett", "kursiv", "unterstrichen", "durchgestrichen", "hoch_tief", "farbe", "marker", "link", "kapitaelchen",
            "grossbuchstaben", "sprache", "tooltip", "gewicht", "vorlage", "docx_roh", "docx_sdt"}
_ABSATZ = {"vorlage", "ausrichtung", "einzug_links", "einzug_rechts", "einzug_erste", "abstand_vor", "abstand_nach", "zeilenabstand_art", "zeilenabstand",
           "seitenumbruch_vor", "hintergrund", "gliederungsebene", "liste_start", "tabstopps", "tabfuell", "rahmen", "richtung", "optionen", "docx_roh", "docx_sdt"}
_ERWEITERT = {"effekt", "ruby", "umschlossen", "unter_art", "unter_farbe", "doppelt_durch", "zeichenabstand", "zeichenabstand_art", "skalierung", "versatz_pt", "unterschneidung", "versteckt", "raster",
              "font_asien", "font_komplex", "betonung"}                  # Zeichenformate, die ``_zeichen_erweitert`` schreibt
_UNTER_ART = {"doppelt": "double", "dick": "thick", "gepunktet": "dotted", "dick_gepunktet": "dottedHeavy", "gestrichelt": "dash", "dick_gestrichelt": "dashedHeavy",
              "lang": "dashLong", "dick_lang": "dashLongHeavy", "strichpunkt": "dotDash", "dick_strichpunkt": "dashDotHeavy", "strichpunktpunkt": "dotDotDash",
              "dick_strichpunktpunkt": "dashDotDotHeavy", "wellig": "wave", "dick_wellig": "wavyHeavy", "doppelwellig": "wavyDouble", "woerter": "words"}
_BETONUNG = {"punkt": "dot", "kreis": "circle", "komma": "comma", "unten": "underDot"}
_OBJEKT_DATEN = {"dekorativ", "original_format", "name", "fx"}
_SETTINGS_DANACH = ("w:compat", "w:docVars", "w:rsids", "w:mathPr", "w:themeFontLang", "w:clrSchemeMapping", "w:shapeDefaults", "w:decimalSymbol", "w:listSeparator")
_FORMEN = ("form", "textfeld")
_SEITE_ERLAUBT = {"border", "watermark", "docx_roh", "spalten", "spalten_abstand_mm", "spalten_linie", "spalten_raster_mm", "width_mm", "height_mm", "margin_top_mm", "margin_bottom_mm", "margin_left_mm", "margin_right_mm", "kopf_abstand_mm", "fuss_abstand_mm",
                  "header", "footer", "first_header", "first_footer", "diff_first", "bilder", "color", "zeilennummern", "zeilennummern_neu", "diff_even", "even_header",
                  "even_footer", "silbentrennung", "silben_sprache", "kopf_verknuepft", "fuss_verknuepft", "seiten_format", "seiten_start", "kapitel_ebene", "kapitel_trenner"}
_ZAHLENART = {"dezimal": "decimal", "klein": "lowerLetter", "gross": "upperLetter", "roem_klein": "lowerRoman", "roem_gross": "upperRoman"}
_PUNKT = {"disc": "•", "circle": "◦", "square": "▪"}
_PLATZHALTER = "①②③④⑤⑥⑦⑧⑨"
_RASTER = {"png", "jpeg", "gif", "bmp", "tiff"}
_ABSCHNITT_BEGINN = {"naechste": "NEW_PAGE", "fortlaufend": "CONTINUOUS", "gerade": "EVEN_PAGE", "ungerade": "ODD_PAGE"}


def _markenname(name: str) -> str:
    """Textmarken in Word: Buchstaben, Ziffern und Unterstrich, höchstens 40 Zeichen, nicht mit einer Ziffer beginnend."""
    s = re.sub(r"\W", "_", str(name))[:40] or "_"
    return s if not s[0].isdigit() else "_" + s[:39]


class _StilHuelle:
    """Ein Stil als Ziel für ``_absatzformat`` (das ``paragraph_format`` und das Element, an dem ``w:pPr`` hängt)."""

    def __init__(self, stil):
        self.paragraph_format, self._p = stil.paragraph_format, stil.element


class _Nicht(Exception):
    """Etwas, das dieser Schreiber nicht abbildet: der Aufrufer nimmt den bisherigen Weg."""


def _pruefen(dok: Dokument, page, meta: dict) -> None:
    if not isinstance(page, PageSettings):
        raise _Nicht("Seiteneinrichtung")
    if dok.quellen:
        raise _Nicht("Quellen")
    if meta.get("quellen") or meta.get("bilder_komprimieren") or meta.get("kompat"):
        raise _Nicht("Metadaten")
    standard = PageSettings()
    for ab in dok.abschnitte:
        for name in ab.seite.__dataclass_fields__:
            if name not in _SEITE_ERLAUBT and getattr(ab.seite, name) != getattr(standard, name):
                raise _Nicht(f"Seiteneinrichtung: {name}")
        for hf in (ab.seite.header, ab.seite.footer, ab.seite.first_header, ab.seite.first_footer):
            if hf.align in ("aussen", "innen") or hf.runs and "".join(r.get("text", "") for r in hf.runs) != hf.text:
                raise _Nicht("Kopf- und Fußzeile")
    if dok.eigenschaften.get("kennwort"):
        raise _Nicht("Kennwort")


_NACH_SHD = {
    "rPr": ("w:fitText", "w:vertAlign", "w:rtl", "w:cs", "w:em", "w:lang", "w:eastAsianLayout", "w:specVanish", "w:oMath", "w:rPrChange"),
    "pPr": ("w:tabs", "w:suppressAutoHyphens", "w:kinsoku", "w:wordWrap", "w:overflowPunct", "w:topLinePunct", "w:autoSpaceDE", "w:autoSpaceDN", "w:bidi",
            "w:adjustRightInd", "w:snapToGrid", "w:spacing", "w:ind", "w:contextualSpacing", "w:mirrorIndents", "w:suppressOverlap", "w:jc", "w:textDirection",
            "w:textAlignment", "w:textboxTightWrap", "w:outlineLvl", "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange"),
    "tcPr": ("w:noWrap", "w:tcMar", "w:textDirection", "w:tcFitText", "w:vAlign", "w:hideMark", "w:headers", "w:cellIns", "w:cellDel", "w:cellMerge", "w:tcPrChange"),
}
_NACH_TCBORDERS = ("w:shd",) + _NACH_SHD["tcPr"]
_NACH_TBLBORDERS = ("w:shd", "w:tblLayout", "w:tblCellMar", "w:tblLook", "w:tblCaption", "w:tblDescription", "w:tblPrChange")


def _einfuegen(eltern, element, nachfolger: tuple) -> None:
    """``element`` vor das erste vorhandene Nachfolgerelement setzen (Reihenfolge nach dem Schema), sonst ans Ende."""
    eltern.insert_element_before(element, *nachfolger)


def _themenschrift_entfernen(stil) -> None:
    """Die Schriftart eines Stils gilt nur, wenn keine Themenschrift (``asciiTheme`` …) darüber steht."""
    from docx.oxml.ns import qn
    rpr = stil.element.rPr
    fonts = rpr.rFonts if rpr is not None else None
    if fonts is not None:
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            fonts.attrib.pop(qn(a), None)


def _farbe(wert) -> str | None:
    return wert[1:].upper() if isinstance(wert, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", wert) else None


class _Schreiber:
    def __init__(self, dok: Dokument, page: PageSettings, meta: dict):
        import docx
        self.dok, self.page, self.meta = dok, page, meta
        self.d = docx.Document()
        self.report = IOReport()
        self.listen_num: dict[int, int] = {}              # Listen-Id → numId
        self.abstrakt: dict[int, int] = {}
        self.bilder = 0
        self._numbering = None
        self._eigene_stile: set[str] = set()
        self.kommentar_laeufe: dict[int, list] = {}       # Kommentar-Id → Läufe, über die er reicht
        self.noten_ids: dict[str, dict[int, int]] = {"f": {}, "e": {}}      # Art → (Noten-Id im Modell → Nummer in der Datei)
        self.marken_offen: dict[str, int] = {}             # Textmarke → Nummer, solange sie im Absatz offen ist
        self.marken_fertig: set[str] = set()               # jede Textmarke gibt es in einer Datei nur einmal
        self.marken_zaehler = 0
        self.aend_zaehler = 0
        self.wz_zaehler = 0
        self.nicht_gespeichert: set[str] = set()
        self.frei_nach_anker: dict[int, list] = {}
        for o in dok.objekte.values():
            self.frei_nach_anker.setdefault(o.anker, []).append(o)

    # ---- Formate ----
    def _zeichen(self, run, f: dict) -> None:
        from docx.shared import Pt, RGBColor
        for k in f:
            if k not in _ZEICHEN and k not in _ERWEITERT and k not in self.nicht_gespeichert:
                self.nicht_gespeichert.add(k)                              # nicht still verwerfen: der Bericht nennt, was die DOCX-Datei nicht enthält
                self.report.warn(f"Die Zeichenformatierung „{k}“ wird in der DOCX-Datei nicht gespeichert.")
        name = f.get("schrift")
        if isinstance(name, (list, tuple)):
            name = name[0] if name else None
        if name:
            run.font.name = str(name)
            rpr = run._r.get_or_add_rPr()
            fonts = rpr.rFonts
            if fonts is not None:
                from docx.oxml.ns import qn
                for attr in ("w:eastAsia", "w:cs"):
                    fonts.set(qn(attr), str(name))
        if f.get("groesse_pt"):
            run.font.size = Pt(float(f["groesse_pt"]))
        if f.get("fett") or (f.get("gewicht") or 0) >= 600:
            run.font.bold = True
        if f.get("kursiv"):
            run.font.italic = True
        if f.get("unterstrichen"):
            run.font.underline = True
        if f.get("durchgestrichen"):
            run.font.strike = True
        if f.get("hoch_tief") == "hoch":
            run.font.superscript = True
        elif f.get("hoch_tief") == "tief":
            run.font.subscript = True
        if f.get("kapitaelchen"):
            run.font.small_caps = True
        if f.get("grossbuchstaben"):
            run.font.all_caps = True
        if _farbe(f.get("farbe")):
            run.font.color.rgb = RGBColor.from_string(_farbe(f["farbe"]))
        if _farbe(f.get("marker")):
            self._schattierung(run._r.get_or_add_rPr(), _farbe(f["marker"]))
        if f.get("sprache"):
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            lang = OxmlElement("w:lang")
            lang.set(qn("w:val"), str(f["sprache"]))
            run._r.get_or_add_rPr().append(lang)
        vorlage = self.dok.vorlagen.get(f.get("vorlage") or "")
        if vorlage is not None and vorlage.art == "zeichen":
            self._zeichenstil(vorlage.name)
            run.style = self.d.styles[vorlage.name]
        self._zeichen_erweitert(run, f)
        if f.get(E.ROH):
            E.einsetzen(run._r.get_or_add_rPr(), f[E.ROH], "rPr")

    def _zeichen_erweitert(self, run, f: dict) -> None:
        """Unterstreichungsart und -farbe, doppelt Durchgestrichen, Zeichenabstand, Skalierung, Position, Unterschneidung, Verstecktes, Raster, asiatische und komplexe
        Schrift, Betonungszeichen."""
        if not any(k in f for k in _ERWEITERT):
            return
        from docx.oxml.ns import qn
        W = E.W_NS
        rpr = run._r.get_or_add_rPr()
        if f.get("doppelt_durch"):
            run.font.double_strike = True
        if f.get("versteckt"):
            run.font.hidden = True
        if f.get("raster") is False:
            run.font.snap_to_grid = False
        u = rpr.find(qn("w:u"))
        if f.get("unterstrichen") and u is not None:
            if f.get("unter_art") in _UNTER_ART:
                u.set(qn("w:val"), _UNTER_ART[f["unter_art"]])
            if _farbe(f.get("unter_farbe")):
                u.set(qn("w:color"), _farbe(f["unter_farbe"]))
        neu: list[str] = []
        if f.get("zeichenabstand"):
            neu.append(f'<w:spacing xmlns:w="{W}" w:val="{round(float(f["zeichenabstand"]) * (15 if f.get("zeichenabstand_art") == 1 else 20))}"/>')
        if f.get("skalierung"):
            neu.append(f'<w:w xmlns:w="{W}" w:val="{round(float(f["skalierung"]))}"/>')
        if f.get("versatz_pt"):
            neu.append(f'<w:position xmlns:w="{W}" w:val="{round(float(f["versatz_pt"]) * 2)}"/>')
        if f.get("unterschneidung") is False:
            neu.append(f'<w:kern xmlns:w="{W}" w:val="0"/>')
        if f.get("betonung") in _BETONUNG:
            neu.append(f'<w:em xmlns:w="{W}" w:val="{_BETONUNG[f["betonung"]]}"/>')
        for schluessel, attr in (("font_asien", "w:eastAsia"), ("font_komplex", "w:cs")):
            familie = str(f.get(schluessel) or "").split("|")[0]
            if familie:
                if rpr.rFonts is None:
                    run.font.name = str(f.get("schrift") if isinstance(f.get("schrift"), str) and f.get("schrift") else "Liberation Sans")
                rpr.rFonts.set(qn(attr), familie)
        E.einsetzen(rpr, neu, "rPr")
        effekt = f.get("effekt")
        if effekt:
            from lunivo_writer.dienste import docx_effekte
            if isinstance(effekt, str):
                effekt = {}
            docx_effekte.in_rpr(rpr, {**docx_effekte.EFFEKT, **effekt})

    def _stil_xml_einsetzen(self, v) -> bool:
        """Die Stile (Basisstile zuerst), die der Leser als XML erhalten hat, in ``styles.xml`` setzen, soweit es ihre Kennung dort noch nicht gibt."""
        from docx.oxml import parse_xml
        from docx.oxml.ns import qn
        liste = v.zusatz.get("docx_stil_xml") or []
        if not liste:
            return False
        wurzel = self.d.styles.element
        vorhanden = {e.get(qn("w:styleId")) for e in wurzel.findall(qn("w:style"))}
        for xml in liste:
            e = parse_xml(xml)
            if e.get(qn("w:styleId")) not in vorhanden:
                wurzel.append(e)
                vorhanden.add(e.get(qn("w:styleId")))
        return True

    def _zeichenstil(self, name: str) -> None:
        """Eine Zeichenvorlage des Modells als Zeichenstil der Datei anlegen (einmal)."""
        if name in self._eigene_stile:
            return
        self._eigene_stile.add(name)
        v = self.dok.vorlagen[name]
        if self._stil_xml_einsetzen(v):
            return
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt, RGBColor
        try:
            stil = self.d.styles.add_style(name, WD_STYLE_TYPE.CHARACTER)
        except ValueError:
            return
        z = v.zeichen
        if z.get("schrift"):
            stil.font.name = str(z["schrift"] if isinstance(z["schrift"], str) else z["schrift"][0])
        if z.get("groesse_pt"):
            stil.font.size = Pt(float(z["groesse_pt"]))
        for name_z, ziel in (("fett", "bold"), ("kursiv", "italic"), ("unterstrichen", "underline"), ("durchgestrichen", "strike")):
            if z.get(name_z):
                setattr(stil.font, ziel, True)
        if _farbe(z.get("farbe")):
            stil.font.color.rgb = RGBColor.from_string(_farbe(z["farbe"]))

    def _tabellenstil(self, name: str) -> bool:
        """Eine Tabellenvorlage des Modells als Tabellenstil der Datei anlegen (einmal); ``True``, wenn es sie jetzt gibt."""
        if name in self._eigene_stile:
            return True
        v = self.dok.vorlagen.get(name)
        if v is None or v.art != "tabelle" or not self._stil_xml_einsetzen(v):
            return False
        self._eigene_stile.add(name)
        return True

    @staticmethod
    def _schattierung(eltern, fuell: str) -> None:
        """``w:shd`` an die schemagerechte Stelle von ``w:rPr``, ``w:pPr`` oder ``w:tcPr`` setzen."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        for alt in eltern.findall(qn("w:shd")):
            eltern.remove(alt)
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), fuell)
        art = eltern.tag.rsplit("}", 1)[-1]
        _einfuegen(eltern, shd, _NACH_SHD[art])

    def _absatzformat(self, para, f: dict) -> None:
        from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
        from docx.shared import Pt
        for k in f:
            if k not in _ABSATZ:
                raise _Nicht(f"Absatzformat {k}")
        pf = para.paragraph_format
        ausr = {"links": WD_ALIGN_PARAGRAPH.LEFT, "mitte": WD_ALIGN_PARAGRAPH.CENTER, "rechts": WD_ALIGN_PARAGRAPH.RIGHT, "block": WD_ALIGN_PARAGRAPH.JUSTIFY}
        if f.get("ausrichtung") in ausr:
            pf.alignment = ausr[f["ausrichtung"]]
        for name, ziel in (("einzug_links", "left_indent"), ("einzug_rechts", "right_indent"), ("einzug_erste", "first_line_indent"),
                           ("abstand_vor", "space_before"), ("abstand_nach", "space_after")):
            if f.get(name):
                setattr(pf, ziel, Pt(float(f[name]) * PT_JE_PX))
        art, wert = f.get("zeilenabstand_art"), f.get("zeilenabstand")
        if art in ("vielfach", "vielfaches") and wert:
            pf.line_spacing = float(wert) if float(wert) <= 10 else float(wert) / 100.0
        elif art == "genau" and wert:
            pf.line_spacing, pf.line_spacing_rule = Pt(float(wert) * PT_JE_PX), WD_LINE_SPACING.EXACTLY
        elif art == "mindestens" and wert:
            pf.line_spacing, pf.line_spacing_rule = Pt(float(wert) * PT_JE_PX), WD_LINE_SPACING.AT_LEAST
        if f.get("seitenumbruch_vor"):
            pf.page_break_before = True
        if f.get("tabstopps"):
            from docx.enum.text import WD_TAB_ALIGNMENT, WD_TAB_LEADER
            art = {0: WD_TAB_ALIGNMENT.LEFT, 1: WD_TAB_ALIGNMENT.RIGHT, 2: WD_TAB_ALIGNMENT.CENTER, 3: WD_TAB_ALIGNMENT.DECIMAL}
            fuell = {".": WD_TAB_LEADER.DOTS, "-": WD_TAB_LEADER.DASHES, "_": WD_TAB_LEADER.LINES, "·": WD_TAB_LEADER.MIDDLE_DOT}.get(f.get("tabfuell", ""), WD_TAB_LEADER.SPACES)
            for stopp in f["tabstopps"]:
                kind = stopp[1] if len(stopp) > 1 and not isinstance(stopp[1], str) else 0
                pf.tab_stops.add_tab_stop(Pt(float(stopp[0]) * PT_JE_PX), art.get(int(kind), WD_TAB_ALIGNMENT.LEFT), fuell)
        if _farbe(f.get("hintergrund")):
            self._schattierung(para._p.get_or_add_pPr(), _farbe(f["hintergrund"]))
        if f.get("rahmen"):
            bdr = F.absatzrahmen_zu_xml(str(f["rahmen"]))
            if bdr is not None:
                ppr = para._p.get_or_add_pPr()
                E.einsetzen(ppr, [E.als_text(bdr)], "pPr")
        if f.get("gliederungsebene"):                                     # Gliederungsebene (Navigation, Inhaltsverzeichnis): ``w:outlineLvl`` (0 = Ebene 1)
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            ppr = para._p.get_or_add_pPr()
            if ppr.find(qn("w:outlineLvl")) is None:
                ol = OxmlElement("w:outlineLvl")
                ol.set(qn("w:val"), str(max(0, min(8, int(f["gliederungsebene"]) - 1))))
                ppr.insert_element_before(ol, "w:divId", "w:cnfStyle", "w:rPr", "w:sectPr", "w:pPrChange")
        if f.get("richtung") == "rtl":                                    # Schreibrichtung von rechts nach links: ``w:bidi``
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            from lunivo_writer.kern.dokument import absatzoptionen as absatzopt
            ppr = para._p.get_or_add_pPr()
            if ppr.find(qn("w:bidi")) is None:
                folge = tuple(absatzopt._FOLGE[absatzopt._FOLGE.index("w:bidi") + 1:])
                ppr.insert_element_before(OxmlElement("w:bidi"), *folge)
        if f.get("optionen"):                                              # Absatzoptionen (Umbruchregeln, Raster …) als die zugehörigen Elemente
            from lunivo_writer.kern.dokument import absatzoptionen as absatzopt
            absatzopt.in_ppr(para._p.get_or_add_pPr(), absatzopt.aus_text(f["optionen"] if isinstance(f["optionen"], str) else ""))
        if f.get(E.ROH):
            E.einsetzen(para._p.get_or_add_pPr(), f[E.ROH], "pPr")

    # ---- Listen ----
    def _numbering_teil(self):
        if self._numbering is None:
            self._numbering = self.d.part.numbering_part.element
        return self._numbering

    def _abstrakte_liste(self, lid: int) -> int:
        from lxml import etree
        from docx.oxml.ns import qn
        if lid in self.abstrakt:
            return self.abstrakt[lid]
        wurzel = self._numbering_teil()
        belegt = [int(e.get(qn("w:abstractNumId"))) for e in wurzel.findall(qn("w:abstractNum"))]
        nr = max(belegt + [-1]) + 1
        definition = self.dok.listen[lid]
        ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        ebenen = []
        for n in range(9):
            e = definition.ebenen[min(n, len(definition.ebenen) - 1)] if definition.ebenen else None
            stil = e.stil if e is not None else "disc"
            links = round((e.einzug if e is not None and e.einzug else 6.35 * (n + 1)) * 1440 / 25.4)
            haengend = round(((e.einzug - e.ausr) if e is not None and e.einzug and e.einzug > e.ausr else 6.35) * 1440 / 25.4)
            if stil in _ZAHLENART:
                text = e.format.translate({ord(c): f"%{i + 1}" for i, c in enumerate(_PLATZHALTER)}) if e is not None and e.format else f"%{n + 1}."
                art, start = _ZAHLENART[stil], e.start if e is not None else 1
            else:
                text = (e.zeichen if e is not None and e.zeichen else None) or _PUNKT.get(stil, "•")
                art, start = "bullet", 1
            ebenen.append(f'<w:lvl w:ilvl="{n}"><w:start w:val="{start}"/><w:numFmt w:val="{art}"/><w:lvlText w:val="{_xml(text)}"/><w:lvlJc w:val="left"/>'
                          f'<w:pPr><w:ind w:left="{links}" w:hanging="{haengend}"/></w:pPr></w:lvl>')
        xml = f'<w:abstractNum {ns} w:abstractNumId="{nr}"><w:multiLevelType w:val="multilevel"/>{"".join(ebenen)}</w:abstractNum>'
        element = etree.fromstring(xml)
        erste_num = wurzel.find(qn("w:num"))
        (erste_num.addprevious(element) if erste_num is not None else wurzel.append(element))
        self.abstrakt[lid] = nr
        return nr

    def _num(self, lid: int, neu_bei: int | None = None) -> int:
        from lxml import etree
        from docx.oxml.ns import qn
        if lid in self.listen_num and neu_bei is None:
            return self.listen_num[lid]
        wurzel = self._numbering_teil()
        belegt = [int(e.get(qn("w:numId"))) for e in wurzel.findall(qn("w:num"))]
        num_id = max(belegt + [0]) + 1
        ns = 'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"'
        ueberschreiben = f'<w:lvlOverride w:ilvl="0"><w:startOverride w:val="{neu_bei}"/></w:lvlOverride>' if neu_bei is not None else ""
        wurzel.append(etree.fromstring(f'<w:num {ns} w:numId="{num_id}"><w:abstractNumId w:val="{self._abstrakte_liste(lid)}"/>{ueberschreiben}</w:num>'))
        self.listen_num[lid] = num_id
        return num_id

    # ---- Absätze ----
    _UMSCHLIESSER = {"kreis": "○", "quadrat": "□", "dreieck": "△", "raute": "◇"}

    def _umschlossen(self, para, text: str, f: dict) -> bool:
        """Umschlossene Zeichen (``umschlossen``: „Form|Vorlage“) als Feld ``EQ \\o\\ac(Form,Zeichen)``, wie Word sie schreibt; das Feldergebnis ist das Zeichen."""
        roh = f.get("umschlossen")
        form = str(roh).split("|")[0] if isinstance(roh, str) else ""
        if form not in self._UMSCHLIESSER or not text.strip():
            return False
        from xml.sax.saxutils import escape
        from docx.oxml import parse_xml
        W = E.W_NS
        text = escape(text)
        rpr_run = para.add_run("")
        self._zeichen(rpr_run, {k: v for k, v in f.items() if k not in ("link", "umschlossen")})
        rpr = rpr_run._r.find("{%s}rPr" % W)
        rpr_xml = E.als_text(rpr) if rpr is not None else ""
        para._p.remove(rpr_run._r)
        kopf = f'xmlns:w="{W}"'

        def lauf(inhalt: str):
            return parse_xml(f'<w:r {kopf}>{rpr_xml}{inhalt}</w:r>')
        anweisung = f' EQ \\o\\ac({self._UMSCHLIESSER[form]},{text}) '
        for inhalt in ('<w:fldChar w:fldCharType="begin"/>', f'<w:instrText xml:space="preserve">{anweisung}</w:instrText>', '<w:fldChar w:fldCharType="separate"/>',
                       f'<w:t xml:space="preserve">{text}</w:t>', '<w:fldChar w:fldCharType="end"/>'):
            para._p.append(lauf(inhalt))
        return True

    def _ruby(self, run, f: dict) -> None:
        """Phonetisches Leitzeichen (``ruby``: „Leittext|Ausrichtung|Abstand|Größe“) als ``w:ruby``: der Text des Laufs ist der Grundtext, der Leittext steht darüber."""
        roh = f.get("ruby")
        if not isinstance(roh, str) or roh.count("|") != 3:
            return
        import copy
        from xml.sax.saxutils import escape
        from docx.oxml import parse_xml
        leit, ausr, abstand, groesse = roh.split("|")
        try:
            abstand_pt, groesse_pt = float(abstand), float(groesse)
        except ValueError:
            return
        W = E.W_NS
        grund_pt = float(f.get("groesse_pt") or 11.0)
        ausrichtung = {"zentriert": "center", "links": "left", "rechts": "right"}.get(ausr, "center")
        ruby = parse_xml(
            f'<w:ruby xmlns:w="{W}"><w:rubyPr><w:rubyAlign w:val="{ausrichtung}"/><w:hps w:val="{round(groesse_pt * 2)}"/>'
            f'<w:hpsRaise w:val="{round((grund_pt * 0.8 + abstand_pt) * 2)}"/><w:hpsBaseText w:val="{round(grund_pt * 2)}"/><w:lid w:val="ja-JP"/></w:rubyPr>'
            f'<w:rt><w:r><w:rPr><w:sz w:val="{round(groesse_pt * 2)}"/></w:rPr><w:t xml:space="preserve">{escape(leit)}</w:t></w:r></w:rt><w:rubyBase/></w:ruby>')
        ruby.find(f"{{{W}}}rubyBase").append(copy.deepcopy(run._r))
        for kind in list(run._r):
            run._r.remove(kind)
        run._r.append(ruby)

    def _lauf(self, para, x: Lauf, a: Absatz) -> None:
        f = wirksames_zeichenformat(self.dok, a, x.format)
        marke, kommentar, anker = f.pop("note", None), f.pop("kommentar", None), f.pop("anker", None)
        aenderung, autor, datum = f.pop("aenderung", None), f.pop("autor", None), f.pop("datum", None)
        f.pop("feld", None)                                           # das Feld umschließt ``absatz`` selbst
        f.pop("docx_sdt", None)                                       # das Inhaltssteuerelement umschließt ``absatz`` selbst
        umbruch = f.pop("umbruch", None)
        if umbruch in ("seite", "spalte") and not x.text.replace(" ", "").replace("\n", "").replace(" ", ""):   # Seiten-/Spaltenumbruch mitten im Absatz: ein eigener Lauf mit ``w:br``
            from docx.enum.text import WD_BREAK
            run = para.add_run()
            run.add_break(WD_BREAK.PAGE if umbruch == "seite" else WD_BREAK.COLUMN)
            self._zeichen(run, {k: v for k, v in f.items() if k != "link"})
            return
        if marke:
            self._notenreferenz(para, str(marke), f)
            return
        text = x.text.replace(" ", "\n").replace("￼", "")
        if not text:
            return
        ziel = f.get("link")
        self._marken(para, anker)
        if self._umschlossen(para, text, f):
            return
        run = para.add_run(text)
        self._zeichen(run, {k: v for k, v in f.items() if k != "link"})
        self._ruby(run, f)
        if kommentar is not None:
            self.kommentar_laeufe.setdefault(int(kommentar), []).append(run)
        aussen = run._r
        if aenderung in ("ins", "del"):
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            self.aend_zaehler += 1
            huelle = OxmlElement(f"w:{aenderung}")
            huelle.set(qn("w:id"), str(self.aend_zaehler))
            huelle.set(qn("w:author"), str(autor or "Lunivo Writer"))
            if isinstance(datum, str) and re.match(r"\d{4}-\d{2}-\d{2}T", datum):
                huelle.set(qn("w:date"), datum)
            if aenderung == "del":
                for t_ in run._r.findall(qn("w:t")):
                    t_.tag = qn("w:delText")
            run._r.addprevious(huelle)
            huelle.append(run._r)
            aussen = huelle
        if ziel:
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            from docx.opc.constants import RELATIONSHIP_TYPE as RT
            hl = OxmlElement("w:hyperlink")
            if str(ziel).startswith("#"):
                hl.set(qn("w:anchor"), _markenname(str(ziel)[1:]))
            else:
                hl.set(qn("r:id"), self.d.part.relate_to(str(ziel), RT.HYPERLINK, is_external=True))
            aussen.addprevious(hl)
            hl.append(aussen)

    def _frei(self, para, o) -> None:
        """Ein frei verankertes Bild als ``wp:anchor`` (Lage, Größe, Textumbruch) im Absatz."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Emu
        if o.art in _FORMEN or (o.art == "wordart" and o.daten.get("docx_roh")):
            self._form_frei(para, o)
            return
        if o.art == "gruppe" and o.daten.get("xml"):
            self._roh_lauf(para, o, o)
            return
        if o.art != "bild" or o.daten.get("dekorativ"):
            raise _Nicht("freies Objekt")
        self._ohne_effekte(o.daten)
        original = self.dok.ressourcen.get(o.ressource)
        roh = self._bildbytes(original, o.breite) if original else None
        if not roh:
            fmt = format_erkennen(original) if original else None
            self.report.warn(f"Ein frei positioniertes Bild im Format {fmt.upper()} wird in der DOCX-Datei nicht gespeichert (nur als Bild im Text möglich)."
                             if fmt else "Ein Bild war nicht lesbar und fehlt in der DOCX-Datei.")
            return
        form = para.add_run().add_picture(io.BytesIO(roh), width=Emu(int(o.breite * EMU_JE_PX)), height=Emu(int(o.hoehe * EMU_JE_PX)))
        inline = form._inline
        self._bildeffekte(inline, o.daten)
        self.bilder += 1
        docpr = inline.docPr
        docpr.set("id", str(self.bilder))
        docpr.set("name", f"Bild {self.bilder}")
        if o.alt_text:
            docpr.set("descr", o.alt_text)
        anker = OxmlElement("wp:anchor")
        for name, wert in (("distT", "0"), ("distB", "0"), ("distL", "114300"), ("distR", "114300"), ("simplePos", "0"), ("relativeHeight", str(251658240 + self.bilder)),
                           ("behindDoc", "1" if o.umbruch == "hinter" else "0"), ("locked", "0"), ("layoutInCell", "1"), ("allowOverlap", "1")):
            anker.set(name, wert)
        einfach = OxmlElement("wp:simplePos")
        einfach.set("x", "0")
        einfach.set("y", "0")
        anker.append(einfach)
        for tag, bezug, bezuege, ausr, versatz in (("wp:positionH", o.bezug_h, {"seite": "page", "rand": "margin", "spalte": "column"}, o.ausr_h, o.x),
                                                   ("wp:positionV", o.bezug_v, {"seite": "page", "rand": "margin", "absatz": "paragraph"}, o.ausr_v, o.y)):
            pos = OxmlElement(tag)
            pos.set("relativeFrom", bezuege.get(bezug, "column" if tag.endswith("H") else "paragraph"))
            if ausr:
                kind = OxmlElement("wp:align")
                kind.text = ausr
            else:
                kind = OxmlElement("wp:posOffset")
                kind.text = str(int(float(versatz) * EMU_JE_PX))
            pos.append(kind)
            anker.append(pos)
        anker.append(inline.extent)
        rand = OxmlElement("wp:effectExtent")
        for name in ("l", "t", "r", "b"):
            rand.set(name, "0")
        anker.append(rand)
        polygon = ('<wp:wrapPolygon xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" edited="0"><wp:start x="0" y="0"/>'
                   '<wp:lineTo x="0" y="21600"/><wp:lineTo x="21600" y="21600"/><wp:lineTo x="21600" y="0"/><wp:lineTo x="0" y="0"/></wp:wrapPolygon>')
        from docx.oxml import parse_xml
        if o.umbruch == "quadrat":
            umbruch = OxmlElement("wp:wrapSquare")
            umbruch.set("wrapText", "bothSides")
        elif o.umbruch in ("eng", "durch"):
            umbruch = OxmlElement("wp:wrapTight" if o.umbruch == "eng" else "wp:wrapThrough")
            umbruch.set("wrapText", "bothSides")
            umbruch.append(parse_xml(polygon))
        elif o.umbruch == "oben_unten":
            umbruch = OxmlElement("wp:wrapTopAndBottom")
        else:
            umbruch = OxmlElement("wp:wrapNone")
        anker.append(umbruch)
        anker.append(docpr)
        rahmen = inline.find("{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}cNvGraphicFramePr")
        if rahmen is not None:                                                        # in der Datei optional; python-docx bietet es nicht als Eigenschaft an
            anker.append(rahmen)
        anker.append(inline.graphic)
        inline.getparent().replace(inline, anker)

    def _form_lauf(self, para, art: str, breite: float, hoehe: float, daten: dict, lage) -> None:
        """Form oder Textfeld als Lauf mit ``w:drawing``: das erhaltene Original (mit Größe aus dem Modell) oder, ohne Original, eine neu erzeugte Zeichnung."""
        from docx.oxml import parse_xml
        self.bilder += 1
        roh = daten.get("docx_roh")
        if roh:
            zeichnung = parse_xml(roh)
            if zeichnung.tag.endswith("}pict"):                                  # Textfeld in VML: das erhaltene Original unverändert zurückschreiben
                para.add_run()._r.append(zeichnung)
                return
            F.groesse_setzen(zeichnung, breite, hoehe, self.bilder)
        else:
            zeichnung = parse_xml(F.zeichnung_neu(art, breite, hoehe, daten, self.bilder, bild_rid=self._fuellbild_rid))
        if lage is not None:
            self._verankern(zeichnung, lage)
        para.add_run()._r.append(zeichnung)

    def _fuellbild_rid(self, name):
        """Die Beziehung (``rId``) zu einem Füllbild der Form; das Bild kommt aus den Ressourcen des Dokuments. ``None``, wenn es fehlt oder kein Rasterbild ist."""
        import io
        roh = self.dok.ressourcen.get(str(name or ""))
        if not roh or format_erkennen(roh) not in _RASTER:
            self.report.warn("Eine Bildfüllung konnte nicht in die DOCX-Datei geschrieben werden (Format oder Daten fehlen); die Form bleibt ohne Füllung.")
            return None
        rid, _bild = self.d.part.get_or_add_image(io.BytesIO(roh))
        return rid

    def _form_frei(self, para, o) -> None:
        self._form_lauf(para, o.art, o.breite, o.hoehe, {**o.daten, "alt": o.alt_text or o.daten.get("alt", "")}, o)

    def _verankern(self, zeichnung, o) -> None:
        """Die Verankerung der Zeichnung (``wp:anchor``) mit Lage und Umbruch des Modells: Ein erhaltenes ``wp:anchor`` bekommt nur die Lage, ein ``wp:inline`` wird zum Anker."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        wp = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
        huelle = zeichnung[0]

        def lage(tag, bezug, bezuege, ausr, versatz):
            pos = OxmlElement(tag)
            pos.set("relativeFrom", bezuege.get(bezug, "column" if tag.endswith("H") else "paragraph"))
            if ausr:
                kind = OxmlElement("wp:align")
                kind.text = ausr
            else:
                kind = OxmlElement("wp:posOffset")
                kind.text = str(int(float(versatz) * EMU_JE_PX))
            pos.append(kind)
            return pos

        h = lage("wp:positionH", o.bezug_h, {"seite": "page", "rand": "margin", "spalte": "column"}, o.ausr_h, o.x)
        v = lage("wp:positionV", o.bezug_v, {"seite": "page", "rand": "margin", "absatz": "paragraph"}, o.ausr_v, o.y)
        if huelle.tag == wp + "anchor":
            for tag, neu in (("positionH", h), ("positionV", v)):
                alt = huelle.find(wp + tag)
                if alt is not None:
                    huelle.replace(alt, neu)
                else:
                    huelle.find(wp + "extent").addprevious(neu)
            return
        anker = OxmlElement("wp:anchor")
        for name, wert in (("distT", "0"), ("distB", "0"), ("distL", "114300"), ("distR", "114300"), ("simplePos", "0"), ("relativeHeight", str(251658240 + self.bilder)),
                           ("behindDoc", "1" if o.umbruch == "hinter" else "0"), ("locked", "0"), ("layoutInCell", "1"), ("allowOverlap", "1")):
            anker.set(name, wert)
        einfach = OxmlElement("wp:simplePos")
        einfach.set("x", "0")
        einfach.set("y", "0")
        anker.append(einfach)
        anker.append(h)
        anker.append(v)
        anker.append(huelle.find(wp + "extent"))
        rand = OxmlElement("wp:effectExtent")
        for name in ("l", "t", "r", "b"):
            rand.set(name, "0")
        anker.append(rand)
        if o.umbruch in ("quadrat", "eng", "durch"):
            umbruch = OxmlElement("wp:wrapSquare")
            umbruch.set("wrapText", "bothSides")
        elif o.umbruch == "oben_unten":
            umbruch = OxmlElement("wp:wrapTopAndBottom")
        else:
            umbruch = OxmlElement("wp:wrapNone")
        anker.append(umbruch)
        anker.append(huelle.find(wp + "docPr"))
        anker.append(huelle.find(wp + "cNvGraphicFramePr") if huelle.find(wp + "cNvGraphicFramePr") is not None else OxmlElement("wp:cNvGraphicFramePr"))
        anker.append(huelle.find("{http://schemas.openxmlformats.org/drawingml/2006/main}graphic"))
        zeichnung.replace(huelle, anker)

    def _marken(self, para, namen) -> None:
        """Textmarken öffnen und schließen, damit genau die Läufe von ``namen`` in ihnen stehen."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        gewuenscht = {_markenname(n) for n in (namen or ())} - self.marken_fertig
        for name in [n for n in self.marken_offen if n not in gewuenscht]:
            self._marke_ende(para, name)
        for name in sorted(gewuenscht - set(self.marken_offen)):
            self.marken_zaehler += 1
            start = OxmlElement("w:bookmarkStart")
            start.set(qn("w:id"), str(self.marken_zaehler))
            start.set(qn("w:name"), name)
            para._p.append(start)
            self.marken_offen[name] = self.marken_zaehler

    def _marke_ende(self, para, name: str) -> None:
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        ende = OxmlElement("w:bookmarkEnd")
        ende.set(qn("w:id"), str(self.marken_offen.pop(name)))
        para._p.append(ende)
        self.marken_fertig.add(name)

    def _feld(self, para, anweisung: str, laeufe: list, a: Absatz) -> None:
        """Ein Feld: Anfang, Anweisung, Trenner, das Ergebnis (die Läufe des Modells) und Ende."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn

        def zeichen(art: str) -> None:
            e = OxmlElement("w:fldChar")
            e.set(qn("w:fldCharType"), art)
            para.add_run()._r.append(e)

        zeichen("begin")
        instr = OxmlElement("w:instrText")
        instr.set(qn("xml:space"), "preserve")
        instr.text = f" {anweisung} "
        para.add_run()._r.append(instr)
        zeichen("separate")
        for x in laeufe:
            self._lauf(para, x, a)
        zeichen("end")

    def _notenreferenz(self, para, marke: str, f: dict) -> None:
        """Das Notenzeichen im Text als Verweis auf die Fuß- oder Endnote (Text der Note steht in ``footnotes.xml`` bzw. ``endnotes.xml``)."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        art, _, nummer = marke.partition(":")
        if art not in ("f", "e") or not nummer.isdigit() or int(nummer) not in self.dok.noten.get(art, {}):
            raise _Nicht("Notenverweis ohne Note")
        ids = self.noten_ids[art]
        n = ids.setdefault(int(nummer), len(ids) + 1)
        run = para.add_run()
        run.font.superscript = True
        ref = OxmlElement("w:footnoteReference" if art == "f" else "w:endnoteReference")
        ref.set(qn("w:id"), str(n))
        run._r.append(ref)

    def _noten_teile(self) -> None:
        """``footnotes.xml`` und ``endnotes.xml`` mit den Texten der Noten; Trennlinien haben die Nummern −1 und 0, die Noten zählen ab 1."""
        from xml.sax.saxutils import escape
        from docx.opc.constants import CONTENT_TYPE as CT, RELATIONSHIP_TYPE as RT
        from docx.opc.packuri import PackURI
        from docx.opc.part import Part
        w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        for art, wurzel, kind, ref, ct, rt, datei in (("f", "footnotes", "footnote", "footnoteRef", CT.WML_FOOTNOTES, RT.FOOTNOTES, "footnotes.xml"),
                                                       ("e", "endnotes", "endnote", "endnoteRef", CT.WML_ENDNOTES, RT.ENDNOTES, "endnotes.xml")):
            if not self.noten_ids[art]:
                continue
            teile = [f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:{wurzel} xmlns:w="{w}">',
                     f'<w:{kind} w:type="separator" w:id="-1"><w:p><w:r><w:separator/></w:r></w:p></w:{kind}>',
                     f'<w:{kind} w:type="continuationSeparator" w:id="0"><w:p><w:r><w:continuationSeparator/></w:r></w:p></w:{kind}>']
            for modell_id, n in sorted(self.noten_ids[art].items(), key=lambda kv: kv[1]):
                text = self.dok.noten[art][modell_id].text
                absaetze = []
                for i, zeile in enumerate(text.split("\n")):
                    marke = f'<w:r><w:rPr><w:vertAlign w:val="superscript"/></w:rPr><w:{ref}/></w:r>' if i == 0 else ""
                    absaetze.append(f'<w:p>{marke}<w:r><w:t xml:space="preserve">{" " if i == 0 else ""}{escape(zeile)}</w:t></w:r></w:p>')
                teile.append(f'<w:{kind} w:id="{n}">{"".join(absaetze)}</w:{kind}>')
            teile.append(f"</w:{wurzel}>")
            teil = Part(PackURI(f"/word/{datei}"), ct, "".join(teile).encode("utf-8"), self.d.part.package)
            self.d.part.relate_to(teil, rt)

    def _kommentare(self) -> None:
        geloest: list = []
        for kid, laeufe in self.kommentar_laeufe.items():
            k = self.dok.kommentare.get(kid)
            if k is None or not laeufe:
                continue
            c = self.d.add_comment(runs=laeufe[0] if len(laeufe) == 1 else (laeufe[0], laeufe[-1]), text=k.text, author=k.autor or "Lunivo Writer", initials=k.initialen or "")
            if k.geloest:
                geloest.append(c)
        if geloest:
            self._kommentare_erweitert(geloest)

    def _kommentare_erweitert(self, kommentare: list) -> None:
        """Gelöste Kommentare als ``word/commentsExtended.xml`` (``w15:done``), verknüpft über die ``w14:paraId`` des letzten Absatzes des Kommentars."""
        from docx.opc.packuri import PackURI
        from docx.opc.part import Part
        w, w14, w15 = E.W_NS, "http://schemas.microsoft.com/office/word/2010/wordml", "http://schemas.microsoft.com/office/word/2012/wordml"
        eintraege = []
        for n, c in enumerate(kommentare, 1):
            absaetze = c._comment_elm.findall("{%s}p" % w)
            if not absaetze:
                continue
            pid = f"{0x20000000 + n:08X}"
            absaetze[-1].set("{%s}paraId" % w14, pid)
            eintraege.append(f'<w15:commentEx w15:paraId="{pid}" w15:done="1"/>')
        if not eintraege:
            return
        xml = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w15:commentsEx xmlns:w15="{w15}">{"".join(eintraege)}</w15:commentsEx>'
        teil = Part(PackURI("/word/commentsExtended.xml"), "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml",
                    xml.encode("utf-8"), self.d.part.package)
        self.d.part.relate_to(teil, "http://schemas.microsoft.com/office/2011/relationships/commentsExtended")

    def _bildbytes(self, roh: bytes, breite: float) -> bytes | None:
        """Die Bytes eines Rasterbildes für python-docx (JPEG, PNG, GIF, BMP, TIFF im Original). Andere Formate (SVG, WebP, Metafile) schreibt ``_bild_roh`` im
        Originalformat: ``None``."""
        return roh if format_erkennen(roh) in _RASTER else None

    def _bild_roh(self, para, roh: bytes, x: InlineObjekt) -> bool:
        """Ein Bild, das python-docx nicht kennt (EMF, WMF, SVG, WebP), unverändert als Bildteil schreiben — nichts geht verloren, nichts wird umgerechnet.
        Word zeigt EMF und WMF immer; SVG und WebP je nach Version (ältere Fassungen zeigen einen Platzhalter): darauf weist der Bericht hin."""
        from lunivo_writer.kern.dokument.bildformat import FORMATE
        fmt = format_erkennen(roh)
        if fmt not in FORMATE:
            return False
        try:
            from docx.opc.packuri import PackURI
            from docx.opc.part import Part
            from docx.oxml import parse_xml
            endung, medientyp = FORMATE[fmt]
            self.bilder += 1
            teil = Part(PackURI(f"/word/media/lunivo{self.bilder}.{endung}"), medientyp, roh, self.d.part.package)
            rid = self.d.part.relate_to(teil, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
            alt = (x.alt_text or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
            lauf = parse_xml(
                '<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:drawing>'
                f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{int(x.breite * EMU_JE_PX)}" cy="{int(x.hoehe * EMU_JE_PX)}"/>'
                f'<wp:docPr id="{self.bilder}" name="Bild {self.bilder}" descr="{alt}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{self.bilder}" name="Bild {self.bilder}"/><pic:cNvPicPr/></pic:nvPicPr>'
                f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{int(x.breite * EMU_JE_PX)}" cy="{int(x.hoehe * EMU_JE_PX)}"/></a:xfrm>'
                '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
            para._p.append(lauf)
            if fmt in ("svg", "webp"):
                self.report.warn(f"Ein Bild im Format {fmt.upper()} wurde unverändert in die DOCX-Datei geschrieben; ältere Word-Versionen zeigen es eventuell nicht an.")
            return True
        except Exception:                                                        # noqa: BLE001 — dann bleibt der Hinweis „nicht lesbar“
            return False

    def _diagramm_lauf(self, para, x: InlineObjekt) -> bool:
        """Ein beim Lesen erkanntes Word-Diagramm wieder als echtes Diagramm schreiben (Diagrammteil in ``word/charts``); ohne Erfolg bleibt es ein Bild."""
        try:
            from docx.opc.packuri import PackURI
            from docx.opc.part import Part
            from docx.oxml import parse_xml
            self.diagramme = getattr(self, "diagramme", 0) + 1
            teil = Part(PackURI(f"/word/charts/chart{self.diagramme}.xml"), "application/vnd.openxmlformats-officedocument.drawingml.chart+xml",
                        x.daten["diagramm_xml"].encode("utf-8"), self.d.part.package)
            rid = self.d.part.relate_to(teil, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/chart")
            self.bilder += 1
            alt = (x.alt_text or "").replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
            lauf = parse_xml(
                '<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
                'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:c="http://schemas.openxmlformats.org/drawingml/2006/chart" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:drawing>'
                f'<wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{int(x.breite * EMU_JE_PX)}" cy="{int(x.hoehe * EMU_JE_PX)}"/>'
                f'<wp:docPr id="{self.bilder}" name="Diagramm {self.bilder}" descr="{alt}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/chart">'
                f'<c:chart r:id="{rid}"/></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')
            para._p.append(lauf)
            return True
        except Exception:                                                        # noqa: BLE001 — dann bleibt das Bild
            return False

    @staticmethod
    def _bildeffekte(huelle, daten: dict) -> None:
        """Schatten, Leuchten, Spiegelung und weiche Kanten des Bildes als ``a:effectLst`` in ``pic:spPr``."""
        from docx.oxml import parse_xml
        from lunivo_writer.dienste.docx_bildeffekte import effekte_zu_xml
        xml = effekte_zu_xml(daten.get("fx"))
        sp = huelle.find(".//{http://schemas.openxmlformats.org/drawingml/2006/picture}spPr") if xml else None
        if sp is not None:
            sp.append(parse_xml(xml))

    def _ohne_effekte(self, daten: dict) -> None:
        """Angaben eines Bildes, die DOCX hier nicht trägt (Effekte wie Schatten, Leuchten, Spiegelung, Zuschnitt), nicht still verwerfen: Der Bericht nennt sie."""
        for k in daten:
            if k not in _OBJEKT_DATEN and k not in self.nicht_gespeichert:
                self.nicht_gespeichert.add(k)
                self.report.warn(f"Die Bildangabe „{k}“ (zum Beispiel Effekte) wird in der DOCX-Datei nicht gespeichert; das Bild selbst ist enthalten.")

    def _roh_lauf(self, para, x: InlineObjekt, lage=None) -> None:
        """Ein beim Lesen aufbewahrtes Objekt (``roh``: Gruppe, SmartArt, VML …) mit seinen Datenteilen unverändert zurückschreiben."""
        from docx.opc.packuri import PackURI
        from docx.opc.part import Part
        from docx.oxml import parse_xml
        r_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
        try:
            element = parse_xml(x.daten["xml"])
            neu: dict = {}
            for rid, t in (x.daten.get("teile") or {}).items():
                blob = self.dok.ressourcen.get(t.get("ressource", ""))
                if blob is None:
                    raise ValueError("Datenteil fehlt")
                self.roh_teile = getattr(self, "roh_teile", 0) + 1
                name = str(t["name"])
                stamm, punkt, endung = name.rpartition(".")
                teil = Part(PackURI(f"{stamm}-lunivo{self.roh_teile}{punkt}{endung}" if punkt else f"{name}-lunivo{self.roh_teile}"), t["typ"], bytes(blob), self.d.part.package)
                neu[rid] = self.d.part.relate_to(teil, t["beziehung"])
            for e in element.iter():
                for k, v in list(e.attrib.items()):
                    if k.startswith(r_ns) and v in neu:
                        e.set(k, neu[v])
            if lage is not None:                                                     # frei verankert: Lage und Umbruch des Modells
                self._verankern(element, lage)
            lauf = parse_xml('<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"/>')
            lauf.append(element)
            para._p.append(lauf)
        except Exception:                                                        # noqa: BLE001
            self.report.warn("Ein aufbewahrtes Objekt (" + str(x.daten.get("grund", "")) + ") konnte nicht in die DOCX-Datei geschrieben werden.")


    def _bild(self, para, x: InlineObjekt) -> None:
        from docx.shared import Emu
        if x.art == "roh" or (x.art == "gruppe" and x.daten.get("xml")):
            self._roh_lauf(para, x)
            return
        if x.art in _FORMEN or (x.art == "wordart" and x.daten.get("docx_roh")):
            self._form_lauf(para, x.art, x.breite, x.hoehe, x.daten, None)
            return
        if x.art == "diagramm" and x.daten.get("diagramm_xml"):
            if not self._diagramm_lauf(para, x):
                self.report.warn("Ein Diagramm konnte nicht in die DOCX-Datei geschrieben werden.")
            return
        if x.art != "bild" or x.daten.get("dekorativ") or x.format:
            raise _Nicht("Objekt im Text")
        self._ohne_effekte(x.daten)
        original = self.dok.ressourcen.get(x.ressource)
        roh = self._bildbytes(original, x.breite) if original else None
        if not roh:
            if original and self._bild_roh(para, original, x):
                return
            self.report.warn("Ein Bild war nicht lesbar und fehlt in der DOCX-Datei.")
            return
        form = para.add_run().add_picture(io.BytesIO(roh), width=Emu(int(x.breite * EMU_JE_PX)), height=Emu(int(x.hoehe * EMU_JE_PX)))
        self._bildeffekte(form._inline, x.daten)
        if x.alt_text:
            form._inline.docPr.set("descr", x.alt_text)
        self.bilder += 1
        form._inline.docPr.set("id", str(self.bilder))
        form._inline.docPr.set("name", f"Bild {self.bilder}")

    def absatz(self, container, a: Absatz) -> None:
        para = container.add_paragraph()
        f = a.format
        vorlage = f.get("vorlage")
        if vorlage and vorlage != "Standard":
            para.style = self.d.styles[_STIL[vorlage]] if vorlage in _STIL else self.d.styles[self._eigener_stil(vorlage)]
        self._absatzformat(para, wirksames_absatzformat(self.dok, a))
        if a.liste_id is not None and a.liste_id in self.dok.listen:
            num = self._num(a.liste_id, f.get("liste_start"))
            ppr = para._p.get_or_add_pPr()
            numpr = ppr.get_or_add_numPr()
            numpr.get_or_add_ilvl().val = max(0, min(8, a.ebene))
            numpr.get_or_add_numId().val = num
            para.paragraph_format.left_indent = None                    # Einzug und Hängen kommen aus der Liste
            para.paragraph_format.first_line_indent = None
        if a.zeichenformat.get(E.ROH):                                   # erhaltene Eigenschaften der Absatzmarke
            from docx.oxml import OxmlElement
            from docx.oxml.ns import qn
            ppr = para._p.get_or_add_pPr()
            rpr = ppr.find(qn("w:rPr"))
            if rpr is None:
                rpr = OxmlElement("w:rPr")
                ppr.append(rpr)
            E.einsetzen(rpr, a.zeichenformat[E.ROH], "rPr")
            E.ordnen(ppr, "pPr")
        inhalte = a.inhalte
        i = 0
        while i < len(inhalte):
            gruppe = self._sdt_gruppe(inhalte[i])
            if gruppe is None:
                self._inhalte_schreiben(para, inhalte[i:i + 1], a)
                i += 1
                continue
            j = i
            while j < len(inhalte) and self._sdt_gruppe(inhalte[j]) == gruppe:
                j += 1
            vorher = list(para._p)
            self._inhalte_schreiben(para, inhalte[i:j], a)
            self._sdt_umhuellen(para._p, vorher, inhalte[i].format["docx_sdt"])
            i = j
        for name in list(self.marken_offen):
            self._marke_ende(para, name)
        for o in self.frei_nach_anker.get(a.id, ()):
            self._frei(para, o)

    @staticmethod
    def _sdt_gruppe(x):
        """Die Gruppe des Inhaltssteuerelements, in dem der Lauf oder das Objekt steht (``None``: in keinem)."""
        sdt = (x.format or {}).get("docx_sdt")
        return sdt.get("gruppe") if isinstance(sdt, dict) else None

    def _inhalte_schreiben(self, para, inhalte: list, a: Absatz) -> None:
        """Läufe, Objekte und Felder eines Stücks des Absatzes."""
        i = 0
        while i < len(inhalte):
            x = inhalte[i]
            if isinstance(x, InlineObjekt):
                self._bild(para, x)
                i += 1
                continue
            feld = wirksames_zeichenformat(self.dok, a, x.format).get("feld")
            if not feld:
                self._lauf(para, x, a)
                i += 1
                continue
            j = i
            while j < len(inhalte) and isinstance(inhalte[j], Lauf) and wirksames_zeichenformat(self.dok, a, inhalte[j].format).get("feld") == feld:
                j += 1
            self._feld(para, str(feld), inhalte[i:j], a)
            i = j

    @staticmethod
    def _sdt_umhuellen(eltern, vorher: list, marke: dict) -> None:
        """Alles, was seit ``vorher`` in ``eltern`` hinzugekommen ist, in ein ``w:sdt`` mit den erhaltenen Angaben (``w:sdtPr``, ggf. ``w:sdtEndPr``) setzen."""
        from docx.oxml import OxmlElement, parse_xml
        neu = [k for k in eltern if k not in vorher and isinstance(k.tag, str) and not k.tag.endswith("}sectPr")]
        if not neu:
            return
        sdt = OxmlElement("w:sdt")
        if marke.get("pr"):
            sdt.append(parse_xml(marke["pr"]))
        if marke.get("ende"):
            sdt.append(parse_xml(marke["ende"]))
        inhalt = OxmlElement("w:sdtContent")
        sdt.append(inhalt)
        neu[0].addprevious(sdt)
        for k in neu:
            inhalt.append(k)

    # ---- Tabellen ----
    @staticmethod
    def _kante(angabe: str) -> tuple[str, str, str]:
        t = str(angabe).split("|")
        farbe = _farbe(t[0]) or "000000"
        try:
            breite = max(2, round(float(t[1]) * 8)) if len(t) > 1 else 6
        except ValueError:
            breite = 6
        art = {"gepunktet": "dotted", "gestrichelt": "dashed", "doppelt": "double"}.get(t[2] if len(t) > 2 else "einfach", "single")
        return art, str(breite), farbe

    def tabelle(self, container, t: Tabelle) -> None:
        from docx.enum.table import WD_ROW_HEIGHT_RULE, WD_CELL_VERTICAL_ALIGNMENT
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        from docx.shared import Emu, Pt
        zeilen, spalten = len(t.zellen), (len(t.zellen[0]) if t.zellen else 0)
        if not zeilen or not spalten:
            return
        tab = container.add_table(rows=zeilen, cols=spalten)
        tab.autofit = False
        f = t.format
        for k in f:
            if k not in {"rahmen_breite", "rahmen_farbe", "rahmen_art", "kopfzeilen", "zeilenhoehe_exakt", "zellabstand", "zellpolster", "breite", "breite_art", "alt_text", "alt_titel", "vorlage",
                         "docx_roh", "docx_roh_zeilen"}:
                raise _Nicht(f"Tabellenformat {k}")
        tpr = tab._tbl.tblPr
        if f.get("vorlage") and self._tabellenstil(str(f["vorlage"])):
            tab.style = self.d.styles[str(f["vorlage"])]
        if f.get("rahmen_breite"):
            raender = OxmlElement("w:tblBorders")
            for kante in ("top", "left", "bottom", "right", "insideH", "insideV"):
                e = OxmlElement(f"w:{kante}")
                e.set(qn("w:val"), "single")
                e.set(qn("w:sz"), str(max(2, round(float(f["rahmen_breite"]) * PT_JE_PX * 8))))
                e.set(qn("w:space"), "0")
                e.set(qn("w:color"), _farbe(f.get("rahmen_farbe")) or "000000")
                raender.append(e)
            _einfuegen(tpr, raender, _NACH_TBLBORDERS)
        if f.get("alt_text"):
            beschr = OxmlElement("w:tblDescription")
            beschr.set(qn("w:val"), str(f["alt_text"]))
            _einfuegen(tpr, beschr, ("w:tblPrChange",))
        if f.get(E.ROH):
            E.einsetzen(tpr, f[E.ROH], "tblPr")
        if t.spaltenbreiten and len(t.spaltenbreiten) == spalten and all(b > 0 for b in t.spaltenbreiten):
            breiten = [float(b) for b in t.spaltenbreiten]
        else:
            text_px = (self.page.width_mm - self.page.margin_left_mm - self.page.margin_right_mm) * 96 / 25.4
            breiten = [text_px / spalten] * spalten
        for c in range(spalten):
            tab.columns[c].width = Emu(int(breiten[c] * EMU_JE_PX))
        for r, zeile in enumerate(t.zellen):
            if r < len(t.zeilenhoehen) and t.zeilenhoehen[r]:
                tab.rows[r].height = Pt(float(t.zeilenhoehen[r]) * PT_JE_PX)
                tab.rows[r].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY if r in (f.get("zeilenhoehe_exakt") or ()) else WD_ROW_HEIGHT_RULE.AT_LEAST
            if r < int(f.get("kopfzeilen") or 0):
                tab.rows[r]._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))
            if (f.get("docx_roh_zeilen") or {}).get(str(r)):
                trpr = tab.rows[r]._tr.get_or_add_trPr()
                E.einsetzen(trpr, f["docx_roh_zeilen"][str(r)], "trPr")
            for c, z in enumerate(zeile):
                if z.verdeckt_von is not None:
                    continue
                zelle = tab.cell(r, c)
                tcpr = zelle._tc.get_or_add_tcPr()
                for k in z.format:
                    if k not in {"hintergrund", "vertikal", "rahmen_oben", "rahmen_unten", "rahmen_links", "rahmen_rechts", "docx_roh"}:
                        raise _Nicht(f"Zellformat {k}")
                zelle.width = Emu(int(sum(breiten[c:c + z.spaltenspanne]) * EMU_JE_PX))
                kanten = [(name, z.format.get(f"rahmen_{ort}")) for name, ort in (("top", "oben"), ("left", "links"), ("bottom", "unten"), ("right", "rechts"))]
                if any(k for _n, k in kanten):
                    raender = OxmlElement("w:tcBorders")
                    for name, angabe in kanten:
                        e = OxmlElement(f"w:{name}")
                        if angabe == "keine" or not angabe:
                            e.set(qn("w:val"), "nil")
                        else:
                            art, breite, farbe = self._kante(angabe)
                            e.set(qn("w:val"), art)
                            e.set(qn("w:sz"), breite)
                            e.set(qn("w:space"), "0")
                            e.set(qn("w:color"), farbe)
                        raender.append(e)
                    _einfuegen(tcpr, raender, _NACH_TCBORDERS)
                if _farbe(z.format.get("hintergrund")):
                    self._schattierung(tcpr, _farbe(z.format["hintergrund"]))
                if z.format.get("vertikal") in ("mitte", "unten"):
                    zelle.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER if z.format["vertikal"] == "mitte" else WD_CELL_VERTICAL_ALIGNMENT.BOTTOM
                if z.format.get(E.ROH):
                    E.einsetzen(tcpr, z.format[E.ROH], "tcPr")
                self.bloecke(zelle, z.bloecke, erste_leer=True)
        for r, zeile in enumerate(t.zellen):
            for c, z in enumerate(zeile):
                if z.verdeckt_von is None and (z.zeilenspanne > 1 or z.spaltenspanne > 1):
                    tab.cell(r, c).merge(tab.cell(r + z.zeilenspanne - 1, c + z.spaltenspanne - 1))

    @staticmethod
    def _block_sdt(b):
        sdt = b.format.get("docx_sdt") if isinstance(b, Absatz) else None
        return sdt.get("gruppe") if isinstance(sdt, dict) else None

    def _block(self, container, b) -> None:
        if isinstance(b, Absatz):
            self.absatz(container, b)
        elif isinstance(b, Tabelle):
            self.tabelle(container, b)
        elif isinstance(b, Rahmen):
            raise _Nicht("Rahmen")

    # ---- Blöcke ----
    def bloecke(self, container, bloecke: list, erste_leer: bool = False) -> None:
        """Blöcke schreiben; in Zellen gehört der vorhandene leere Absatz dem ersten Block."""
        vorhanden = len(container.paragraphs) if erste_leer else 0
        i = 0
        while i < len(bloecke):
            gruppe = self._block_sdt(bloecke[i])
            if gruppe is None:
                self._block(container, bloecke[i])
                i += 1
                continue
            j = i
            while j < len(bloecke) and self._block_sdt(bloecke[j]) == gruppe:
                j += 1
            wurzel = container._tc if hasattr(container, "_tc") else container.element.body
            vorher = list(wurzel)
            for b in bloecke[i:j]:
                self._block(container, b)
            self._sdt_umhuellen(wurzel, vorher, bloecke[i].format["docx_sdt"])
            i = j
        if erste_leer and vorhanden:
            leer = container.paragraphs[0]
            if not leer.text and not leer._p.xpath(".//w:drawing") and len(container.paragraphs) > 1:
                leer._p.getparent().remove(leer._p)
        if erste_leer and not container.paragraphs:
            container.add_paragraph()
        if erste_leer and container._tc.xpath("./*[last()]")[0].tag.endswith("}tbl"):
            container.add_paragraph()                                  # eine Zelle endet immer mit einem Absatz

    # ---- Seite ----
    def seite_einrichten(self, s, p: PageSettings, beginn: str, k: int, vorher: PageSettings | None) -> None:
        """Seiteneinrichtung des Abschnitts ``k`` (``s``: ``Section``); Kopf- und Fußzeilen, die denen des Abschnitts davor gleichen, bleiben mit ihnen verknüpft."""
        from docx.enum.section import WD_ORIENT, WD_SECTION
        from docx.shared import Mm
        s.page_width, s.page_height = Mm(p.width_mm), Mm(p.height_mm)
        s.orientation = WD_ORIENT.LANDSCAPE if p.landscape else WD_ORIENT.PORTRAIT
        s.top_margin, s.bottom_margin, s.left_margin, s.right_margin = Mm(p.margin_top_mm), Mm(p.margin_bottom_mm), Mm(p.margin_left_mm), Mm(p.margin_right_mm)
        s.header_distance, s.footer_distance = Mm(p.kopf_abstand_mm), Mm(p.fuss_abstand_mm)
        if k > 0:
            s.start_type = getattr(WD_SECTION, _ABSCHNITT_BEGINN.get(beginn, "NEW_PAGE"))
        self._spalten(s, p)
        self._seitenschmuck(s, p)
        self._seitenzaehlung(s, p)
        if k == 0:
            self._dokumentweit(p)
        paare = [(s.header, p.header, vorher.header if vorher else None), (s.footer, p.footer, vorher.footer if vorher else None)]
        if p.diff_first:
            s.different_first_page_header_footer = True
            paare += [(s.first_page_header, p.first_header, vorher.first_header if vorher and vorher.diff_first else None),
                      (s.first_page_footer, p.first_footer, vorher.first_footer if vorher and vorher.diff_first else None)]
        if p.diff_even:
            paare += [(s.even_page_header, p.even_header, vorher.even_header if vorher and vorher.diff_even else None),
                      (s.even_page_footer, p.even_footer, vorher.even_footer if vorher and vorher.diff_even else None)]
        for teil, hf, davor in paare:
            self.kopf_fuss(teil, hf, davor)
        self._seitenbilder(s, p, k, vorher)
        self._wasserzeichen(s, p, k)

    def _seitenbilder(self, s, p: PageSettings, k: int, vorher: PageSettings | None) -> None:
        """Bilder der Kopf- und Fußzeilen (``PageSettings.bilder``) als verankerte Bilder in den Kopf- und Fußteilen des Abschnitts; gleichen sie denen des
        Abschnitts davor und ist der Teil verknüpft, gelten die davor."""
        import io
        from docx.oxml import parse_xml
        from lunivo_writer.kern.dokument.bildformat import FORMATE
        teile = {"kopf": s.header, "fuss": s.footer, "kopf1": s.first_page_header if p.diff_first else None, "fuss1": s.first_page_footer if p.diff_first else None,
                 "kopf2": s.even_page_header if p.diff_even else None, "fuss2": s.even_page_footer if p.diff_even else None}
        for ort, teil in teile.items():
            eigene = [a for a in p.bilder if isinstance(a, dict) and a.get("ort") == ort]
            davor = [a for a in (vorher.bilder if vorher else []) if isinstance(a, dict) and a.get("ort") == ort]
            if teil is None or not eigene or (k > 0 and eigene == davor and teil.is_linked_to_previous):
                continue
            teil.is_linked_to_previous = False
            for a in eigene:
                roh = self.dok.ressourcen.get(str(a.get("ressource", ""))) or (bytes(a["bild"]) if isinstance(a.get("bild"), (bytes, bytearray)) else None)
                fmt = format_erkennen(roh) if roh else None
                if not roh or fmt not in FORMATE:
                    self.report.warn("Ein Bild in der Kopf- oder Fußzeile war nicht lesbar und fehlt in der DOCX-Datei.")
                    continue
                if fmt in _RASTER:
                    rid, _bild = teil.part.get_or_add_image(io.BytesIO(roh))
                else:
                    from docx.opc.packuri import PackURI
                    from docx.opc.part import Part
                    self.bilder += 1
                    endung, medientyp = FORMATE[fmt]
                    rid = teil.part.relate_to(Part(PackURI(f"/word/media/lunivo{self.bilder}.{endung}"), medientyp, roh, self.d.part.package),
                                              "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image")
                    if fmt in ("svg", "webp"):
                        self.report.warn(f"Ein Bild im Format {fmt.upper()} wurde unverändert in die DOCX-Datei geschrieben; ältere Word-Versionen zeigen es eventuell nicht an.")
                self.bilder += 1
                cx, cy = int(float(a.get("b", 0)) * EMU_JE_PX), int(float(a.get("h", 0)) * EMU_JE_PX)
                bezug_h = {"seite": "page", "rand": "margin", "spalte": "column"}.get(a.get("bh"), "page")
                bezug_v = {"seite": "page", "rand": "margin"}.get(a.get("bv"), "page")

                def lage(ausr: str, versatz, erlaubt: tuple) -> str:
                    return f"<wp:align>{ausr}</wp:align>" if ausr in erlaubt else f"<wp:posOffset>{int(float(versatz or 0) * EMU_JE_PX)}</wp:posOffset>"
                alt = str(a.get("alt", "")).replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
                lauf = parse_xml(
                    '<w:r xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
                    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
                    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:drawing>'
                    f'<wp:anchor distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="251658240" behindDoc="{1 if a.get("hinter") else 0}" locked="0" '
                    'layoutInCell="1" allowOverlap="1"><wp:simplePos x="0" y="0"/>'
                    f'<wp:positionH relativeFrom="{bezug_h}">{lage(a.get("ah") or "", a.get("xh"), ("left", "center", "right", "inside", "outside"))}</wp:positionH>'
                    f'<wp:positionV relativeFrom="{bezug_v}">{lage(a.get("av") or "", a.get("yv"), ("top", "center", "bottom"))}</wp:positionV>'
                    f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:wrapNone/>'
                    f'<wp:docPr id="{self.bilder}" name="Bild {self.bilder}" descr="{alt}"/><wp:cNvGraphicFramePr/>'
                    '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
                    f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{self.bilder}" name="Bild {self.bilder}"/><pic:cNvPicPr/></pic:nvPicPr>'
                    f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
                    f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
                    '</pic:pic></a:graphicData></a:graphic></wp:anchor></w:drawing></w:r>')
                teil.paragraphs[0]._p.append(lauf)

    def _seitenschmuck(self, s, p: PageSettings) -> None:
        """Seitenrahmen (``w:pgBorders`` samt Einstellungen des Dokuments) und die erhaltenen Eigenschaften des Abschnitts."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        sp = s._sectPr
        for alt in sp.findall(qn("w:pgBorders")):
            sp.remove(alt)
        if p.border:
            pb = F.seitenrahmen_zu_xml(p.border)
            if pb is not None:
                sp.append(pb)
                st = self.d.settings.element
                for name, an in F.seitenrahmen_einstellungen(p.border).items():
                    for alt in st.findall(qn(f"w:{name}")):
                        st.remove(alt)
                    if an:
                        st.insert_element_before(OxmlElement(f"w:{name}"), *_SETTINGS_DANACH)
        E.einsetzen(sp, p.docx_roh, "sectPr")
        E.ordnen(sp, "sectPr")

    def _seitenzaehlung(self, s, p: PageSettings) -> None:
        """Zeilennummern (``w:lnNumType``) und Seitenzahlformat (``w:pgNumType``) des Abschnitts; die Kapitelnummer vor der Seitenzahl kennt DOCX hier nicht."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        sp = s._sectPr
        for name in ("w:lnNumType", "w:pgNumType"):
            for alt in sp.findall(qn(name)):
                sp.remove(alt)
        if p.zeilennummern:
            ln = OxmlElement("w:lnNumType")
            ln.set(qn("w:countBy"), "1")
            ln.set(qn("w:restart"), "newPage" if p.zeilennummern_neu == "seite" else "continuous")
            sp.append(ln)
        if p.seiten_format != "dezimal" or p.seiten_start:
            pg = OxmlElement("w:pgNumType")
            if p.seiten_format != "dezimal":
                pg.set(qn("w:fmt"), _ZAHLENART.get(p.seiten_format, "decimal"))
            if p.seiten_start:
                pg.set(qn("w:start"), str(int(p.seiten_start)))
            sp.append(pg)
        if p.kapitel_ebene:
            self.report.warn("Die Kapitelnummer vor der Seitenzahl wird in der DOCX-Datei nicht gespeichert.")
        E.ordnen(sp, "sectPr")

    def _dokumentweit(self, p: PageSettings) -> None:
        """Einstellungen, die in DOCX für das ganze Dokument gelten (Seitenfarbe, Silbentrennung, gerade/ungerade Kopfzeilen); sie kommen vom ersten Abschnitt."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        st = self.d.settings.element
        for alt in self.d.element.findall(qn("w:background")):
            self.d.element.remove(alt)
        for name in ("w:displayBackgroundShape", "w:autoHyphenation"):
            for alt in st.findall(qn(name)):
                st.remove(alt)
        if p.color:
            hg = OxmlElement("w:background")
            hg.set(qn("w:color"), p.color.lstrip("#").upper())
            self.d.element.insert(0, hg)
            st.insert_element_before(OxmlElement("w:displayBackgroundShape"), *_SETTINGS_DANACH)
        if p.silbentrennung:
            st.insert_element_before(OxmlElement("w:autoHyphenation"), *_SETTINGS_DANACH)
        self.d.settings.odd_and_even_pages_header_footer = bool(p.diff_even)

    def _wasserzeichen(self, s, p: PageSettings, k: int) -> None:
        """Wasserzeichen mit Text als VML-Textform in der Kopfzeile (und der Kopfzeile der ersten Seite); Bild-Wasserzeichen bleiben außen vor und werden gemeldet."""
        w = p.watermark
        if not w or not (w.get("text") or "").strip():
            if w and w.get("bild"):
                self.report.warn("Ein Bild-Wasserzeichen wird in der DOCX-Datei nicht gespeichert.")
            return
        for teil in [s.header] + ([s.first_page_header] if p.diff_first else []):
            if teil.is_linked_to_previous and k > 0:
                continue                                                   # die Kopfzeile des Abschnitts davor gilt auch hier
            teil.is_linked_to_previous = False
            para = teil.paragraphs[0]
            if any(F.ist_wasserzeichen(x) for x in para._p.iter("{" + E.W_NS + "}pict")):
                continue
            self.wz_zaehler += 1
            lauf = F.wasserzeichen_zu_xml(w, self.wz_zaehler)
            if lauf is not None:
                para._p.append(lauf)

    @staticmethod
    def _spalten(s, p: PageSettings) -> None:
        """Textspalten als ``w:cols`` (gleich breit oder mit eigenen Breiten)."""
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        sp = s._sectPr
        for alt in sp.findall(qn("w:cols")):
            sp.remove(alt)
        if int(p.spalten or 1) <= 1:
            return
        cols = OxmlElement("w:cols")
        cols.set(qn("w:num"), str(int(p.spalten)))
        cols.set(qn("w:space"), str(round(float(p.spalten_abstand_mm) * 1440 / 25.4)))
        if p.spalten_linie:
            cols.set(qn("w:sep"), "1")
        if p.spalten_raster_mm:
            cols.set(qn("w:equalWidth"), "0")
            for breite, abstand in p.spalten_raster_mm:
                c = OxmlElement("w:col")
                c.set(qn("w:w"), str(round(float(breite) * 1440 / 25.4)))
                c.set(qn("w:space"), str(round(float(abstand) * 1440 / 25.4)))
                cols.append(c)
        sp.insert_element_before(cols, "w:formProt", "w:vAlign", "w:noEndnote", "w:titlePg", "w:textDirection", "w:bidi", "w:rtlGutter", "w:docGrid",
                                 "w:printerSettings", "w:sectPrChange")

    def _abschnittsende(self, ab, k: int, vorher: PageSettings | None) -> None:
        """Der Abschnitt ``k`` endet: seine Einrichtung kommt als ``w:sectPr`` in den letzten Absatz."""
        from docx.oxml import OxmlElement
        from docx.section import Section
        d = self.d
        kinder = [e for e in d.element.body if not e.tag.endswith("}sectPr")]
        letzte = d.paragraphs[-1] if kinder and kinder[-1].tag.endswith("}p") else d.add_paragraph()
        sectpr = OxmlElement("w:sectPr")
        letzte._p.get_or_add_pPr().insert_element_before(sectpr, "w:pPrChange")
        self.seite_einrichten(Section(sectpr, d.part), ab.seite, ab.beginn, k, vorher)

    def kopf_fuss(self, teil, hf: HeaderFooter, davor: HeaderFooter | None = None) -> None:
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.oxml import OxmlElement
        from docx.oxml.ns import qn
        if hf.is_empty():
            if davor is not None and not davor.is_empty():
                teil.is_linked_to_previous = False                     # die eigene Zeile des Abschnitts bleibt leer
            return
        if davor is not None and hf == davor:
            return                                                     # gleich wie davor: verknüpft lassen
        teil.is_linked_to_previous = False
        ausr = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER, "right": WD_ALIGN_PARAGRAPH.RIGHT, "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}.get(hf.align, WD_ALIGN_PARAGRAPH.CENTER)
        para = teil.paragraphs[0]
        para.alignment = ausr
        for text, fmt in hf.laeufe():
            for k, stueck in enumerate(text.split("\n")):
                if k:
                    para = teil.add_paragraph()
                    para.alignment = ausr
                for tok in re.split(r"(\{PAGE\}|\{PAGES\})", stueck):
                    if tok in ("{PAGE}", "{PAGES}"):
                        feld = OxmlElement("w:fldSimple")
                        feld.set(qn("w:instr"), "PAGE" if tok == "{PAGE}" else "NUMPAGES")
                        lauf = OxmlElement("w:r")
                        t = OxmlElement("w:t")
                        t.text = "1"
                        lauf.append(t)
                        feld.append(lauf)
                        para._p.append(feld)
                    elif tok:
                        run = para.add_run(tok)
                        self._kopf_format(run, fmt or {})

    @staticmethod
    def _kopf_format(run, fmt: dict) -> None:
        from docx.shared import Pt, RGBColor
        if fmt.get("family"):
            run.font.name = fmt["family"]
        if fmt.get("size_pt"):
            run.font.size = Pt(float(fmt["size_pt"]))
        for name, ziel in (("bold", "bold"), ("italic", "italic"), ("underline", "underline")):
            if fmt.get(name):
                setattr(run.font, ziel, True)
        if _farbe(fmt.get("color")):
            run.font.color.rgb = RGBColor.from_string(_farbe(fmt["color"]))

    # ---- Dokument ----
    def stile(self) -> None:
        """Die Eigenschaften der benutzten eingebauten Vorlagen aus dem Modell auf die Word-Stile übertragen."""
        from docx.shared import Pt, RGBColor
        std = self.dok.standardformat
        normal = self.d.styles["Normal"]
        if std.get("schrift"):
            normal.font.name = str(std["schrift"])
            _themenschrift_entfernen(normal)
        if std.get("groesse_pt"):
            normal.font.size = Pt(float(std["groesse_pt"]))
        for name, v in self.dok.vorlagen.items():
            if name not in _STIL or name == "Standard":
                continue
            try:
                stil = self.d.styles[_STIL[name]]
            except KeyError:
                continue
            z, a = v.zeichen, v.absatz
            if z.get("schrift"):
                stil.font.name = str(z["schrift"] if isinstance(z["schrift"], str) else z["schrift"][0])
            elif std.get("schrift"):
                stil.font.name = str(std["schrift"])
            _themenschrift_entfernen(stil)
            if z.get("groesse_pt"):
                stil.font.size = Pt(float(z["groesse_pt"]))
            stil.font.bold = bool(z.get("fett"))
            stil.font.italic = bool(z.get("kursiv"))
            if _farbe(z.get("farbe")):
                stil.font.color.rgb = RGBColor.from_string(_farbe(z["farbe"]))
            else:
                stil.font.color.rgb = RGBColor(0, 0, 0)
            if a.get("abstand_vor") is not None:
                stil.paragraph_format.space_before = Pt(float(a["abstand_vor"]) * PT_JE_PX)
            if a.get("abstand_nach") is not None:
                stil.paragraph_format.space_after = Pt(float(a["abstand_nach"]) * PT_JE_PX)

    def _eigener_stil(self, name: str) -> str:
        """Eine eigene Absatzvorlage des Modells als Word-Stil anlegen (einmal) und ihren Namen geben."""
        if name in self._eigene_stile:
            return name
        from docx.enum.style import WD_STYLE_TYPE
        from docx.shared import Pt, RGBColor
        v = self.dok.vorlagen.get(name)
        if v is None or v.art != "absatz":
            raise _Nicht("Formatvorlage fehlt")
        try:
            stil = self.d.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        except ValueError:                                              # der Name gehört schon einem Stil der Vorlage
            stil = self.d.styles[name]
        self._eigene_stile.add(name)
        basis = v.basis or "Standard"
        stil.base_style = self.d.styles["Normal" if basis == "Standard" else (_STIL[basis] if basis in _STIL else self._eigener_stil(basis))]
        z = v.zeichen
        for k in z:
            if k not in _ZEICHEN:
                raise _Nicht(f"Zeichenformat {k} einer Vorlage")
        if z.get("schrift"):
            stil.font.name = str(z["schrift"] if isinstance(z["schrift"], str) else z["schrift"][0])
            _themenschrift_entfernen(stil)
        if z.get("groesse_pt"):
            stil.font.size = Pt(float(z["groesse_pt"]))
        for name_z, ziel in (("fett", "bold"), ("kursiv", "italic"), ("unterstrichen", "underline"), ("durchgestrichen", "strike")):
            if z.get(name_z):
                setattr(stil.font, ziel, True)
        if _farbe(z.get("farbe")):
            stil.font.color.rgb = RGBColor.from_string(_farbe(z["farbe"]))
        self._absatzformat(_StilHuelle(stil), {k: x for k, x in v.absatz.items() if k != "vorlage"})
        if v.zusatz.get("docx_roh_ppr"):
            E.einsetzen(stil.element.get_or_add_pPr(), v.zusatz["docx_roh_ppr"], "pPr")
        if v.zusatz.get("docx_roh_rpr"):
            E.einsetzen(stil.element.get_or_add_rPr(), v.zusatz["docx_roh_rpr"], "rPr")
        return name

    def schreiben(self) -> bytes:
        d = self.d
        body = d.element.body
        for kind in list(body):
            if kind.tag.endswith("}p") or kind.tag.endswith("}tbl"):
                body.remove(kind)
        self.stile()
        abschnitte = self.dok.abschnitte
        for k, ab in enumerate(abschnitte):
            self.page = ab.seite                                        # Tabellenbreiten richten sich nach der Seite des Abschnitts
            self.bloecke(d, ab.bloecke)
            vorher = abschnitte[k - 1].seite if k else None
            if k < len(abschnitte) - 1:
                self._abschnittsende(ab, k, vorher)
            else:
                self.seite_einrichten(d.sections[-1], ab.seite, ab.beginn, k, vorher)
        self._noten_teile()
        self._kommentare()
        if not d.paragraphs or body.xpath("./*[not(self::w:sectPr)][last()]")[-1].tag.endswith("}tbl"):
            d.add_paragraph()
        d.core_properties.title = self.meta.get("title", "") or ""
        d.core_properties.author = self.meta.get("author", "") or "Lunivo Writer"
        sprache = self.meta.get("sprache") or str(getattr(self.page, "silben_sprache", "") or "").replace("_", "-")
        if sprache:
            from docx.oxml.ns import qn
            rpr = d.styles.element.find(qn("w:docDefaults") + "/" + qn("w:rPrDefault") + "/" + qn("w:rPr"))
            if rpr is not None:
                lang = rpr.find(qn("w:lang"))
                if lang is None:
                    from docx.oxml import OxmlElement
                    lang = OxmlElement("w:lang")
                    rpr.append(lang)
                lang.set(qn("w:val"), sprache)
        aus = io.BytesIO()
        d.save(aus)
        return aus.getvalue()


def _xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def docx_dokument_daten(dok: Dokument, page, meta: dict | None = None) -> tuple[bytes, IOReport]:
    """Baut die DOCX-Datei im Speicher. Wirft ``DocumentIOError``, wenn das Dokument etwas enthält, das dieser Schreiber nicht abbildet (kein Rückfallweg)."""
    from lunivo_writer.kern.dokument.bericht import DocumentIOError
    meta = meta or {}
    try:
        _pruefen(dok, page, meta)
        s = _Schreiber(dok, page, meta)
        daten = s.schreiben()
    except _Nicht as e:
        raise DocumentIOError(f"Das Dokument enthält etwas, das Lunivo noch nicht als DOCX schreiben kann: {e}.") from e
    return daten, s.report
