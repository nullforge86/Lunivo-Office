"""Übergang für Dateileser und -schreiber: Das bisherige Modell (``core.document.Document`` mit Qt-Formatnamen, das die vorhandenen DOCX-, ODT-, RTF- und
Textleser und -schreiber noch erzeugen und lesen) wird beim Laden in das maßgebliche Modell (``core.document.Dokument``) übersetzt und beim Speichern
zurück. Es ist keine Spiegelung: Der Tab hält nur das neue Modell; die Umwandlung geschieht einmal je Datei und entfällt, sobald die Leser und Schreiber
das neue Modell selbst erzeugen und lesen.
"""
from __future__ import annotations

import base64
import json

from lunivo_writer.core.document import (
    Absatz, Abschnitt, Block, Brush, CharacterFormat, Color, Dokument, Document, Footnote, Formatvorlage, Frame, FreiesObjekt, Image, InlineObjekt, Kommentar,
    Lauf, Length, LineSpacing, ListenDefinition, ListenEbene, ListFormat, Note, Paragraph, ParagraphFormat, Rahmen, RowHeight, Section, Tabelle, Table,
    TableCell, TableRow, TabStop, TextRun, Zelle,
)
from lunivo_writer.core.document.dokument import LISTEN_EBENEN, normalisiere
from lunivo_writer.core.geometry import mm_to_px, px_to_mm

BASIS = 0x100000                                            # QTextFormat.UserProperty
ZEICHEN_USER = {20: "kommentar", 21: "note", 22: "aenderung", 23: "autor", 24: "datum", 26: "feld", 27: "index", 28: "zitat", 32: "versteckt",
                40: "effekt", 41: "font_asien", 42: "font_komplex", 43: "doppelt_durch", 44: "betonung", 45: "unter_art", 46: "raster",
                50: "umschlossen", 51: "ruby", 53: "index_opt"}
ABSATZ_USER = {1: "vorlage", 2: "toc", 3: "verzeichnis_art", 4: "beschriftung", 5: "rahmen", 6: "spaltenumbruch_vor", 7: "notenziel", 8: "hilfsabsatz",
               9: "muster", 36: "mehrstufig", 37: "tabfuell", 38: "optionen", 39: "autoumbruch", 47: "bildanker", 48: "abstand_vorher", 52: "toc_opt"}
P_OBJEKT = f"user:{BASIS + 33}"
P_BILD_ALT = f"user:{BASIS + 2}"                  # Alternativtext am Bild: ``STYLE_PROP + 1`` der alten Leser und Schreiber
_BUILTIN = {"Standard", "Überschrift 1", "Überschrift 2", "Überschrift 3", "Überschrift 4", "Überschrift 5", "Überschrift 6", "Überschrift 7",
            "Überschrift 8", "Überschrift 9", "Titel", "Untertitel", "Zitat", "Kein Abstand"}
BOOL_ZEICHEN = ("versteckt", "doppelt_durch", "raster")
BOOL_ABSATZ = ("spaltenumbruch_vor", "hilfsabsatz")
ZAHL_ZEICHEN = ("kommentar",)
ZAHL_ABSATZ = ("autoumbruch",)
LISTEN_STIL = {-1: "disc", -2: "circle", -3: "square", -4: "dezimal", -5: "klein", -6: "gross", -7: "roem_klein", -8: "roem_gross"}
LISTEN_STIL_UMGEKEHRT = {v: k for k, v in LISTEN_STIL.items()}
ABSCHNITT_BEGINN = {"next_page": "naechste", "continuous": "fortlaufend", "even_page": "gerade", "odd_page": "ungerade",
                    "naechste": "naechste", "fortlaufend": "fortlaufend", "gerade": "gerade", "ungerade": "ungerade"}
ABSCHNITT_BEGINN_ALT = {"naechste": "naechste", "fortlaufend": "fortlaufend", "gerade": "gerade", "ungerade": "ungerade"}
UNTER_ART = {2: "gestrichelt", 3: "gepunktet", 4: "strichpunkt", 5: "strichpunktpunkt"}
UNTER_ART_UMGEKEHRT = {v: k for k, v in UNTER_ART.items()}
KANTEN = (("Top", "oben"), ("Bottom", "unten"), ("Left", "links"), ("Right", "rechts"))
FRAME_BREITE = ("FrameWidth", "breite", "breite_art")


def _user(name: int) -> str:
    return f"user:{BASIS + name}"


def _hex(c: Color | None) -> str | None:
    if c is None:
        return None
    return f"#{c.r:02x}{c.g:02x}{c.b:02x}" + (f"{c.a:02x}" if c.a != 255 else "")


def _farbe_von(v) -> str | None:
    if isinstance(v, Color):
        return _hex(v)
    if isinstance(v, Brush) and v.style != 0:
        return _hex(v.color)
    return None


def _color(text) -> Color | None:
    if not isinstance(text, str) or not text.startswith("#") or len(text) not in (7, 9):
        return None
    try:
        return Color(int(text[1:3], 16), int(text[3:5], 16), int(text[5:7], 16), int(text[7:9], 16) if len(text) == 9 else 255)
    except ValueError:
        return None


def _zahl(v, standard=None):
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else standard


# ================================================================ alt → neu ================================================================
def zeichenformat_neu(cf: CharacterFormat) -> dict:
    p, d = cf.properties, {}
    fam = cf.family or p.get("FontFamilies") or p.get("FontFamily")
    if isinstance(fam, (tuple, list)):
        fam = fam[0] if fam else None
    if fam:
        d["schrift"] = str(fam)
    pt = cf.size_pt if cf.size_pt else _zahl(p.get("FontPointSize"))
    if pt:
        d["groesse_pt"] = float(pt)
    gewicht = cf.weight if cf.weight is not None else _zahl(p.get("FontWeight"))
    if gewicht is not None and gewicht >= 600:
        d["fett"] = True
    if (cf.italic if cf.italic is not None else p.get("FontItalic")):
        d["kursiv"] = True
    farbe = _farbe_von(cf.foreground_color) or _farbe_von(p.get("ForegroundBrush"))
    if farbe:
        d["farbe"] = farbe
    stil = int(_zahl(p.get("TextUnderlineStyle"), 0))
    if cf.underline or p.get("FontUnderline") or stil > 0:
        d["unterstrichen"] = True
        if stil in UNTER_ART:
            d["unter_art"] = UNTER_ART[stil]
    if _farbe_von(p.get("TextUnderlineColor")):
        d["unter_farbe"] = _farbe_von(p.get("TextUnderlineColor"))
    if p.get("FontStrikeOut"):
        d["durchgestrichen"] = True
    if p.get("FontOverline"):
        d["ueberstrichen"] = True
    hoch = int(_zahl(p.get("TextVerticalAlignment"), 0))
    if hoch in (1, 2):
        d["hoch_tief"] = "hoch" if hoch == 1 else "tief"
    schreibweise = int(_zahl(p.get("FontCapitalization"), 0))
    if schreibweise == 1:
        d["grossbuchstaben"] = True
    elif schreibweise == 3:
        d["kapitaelchen"] = True
    weite = _zahl(p.get("FontLetterSpacing"))
    if weite:
        d["zeichenabstand"] = weite
        d["zeichenabstand_art"] = int(_zahl(p.get("FontLetterSpacingType"), 0))
    marker = _farbe_von(p.get("BackgroundBrush"))
    if marker:
        d["marker"] = marker
    if p.get("AnchorHref"):
        d["link"] = str(p["AnchorHref"])
    if p.get("AnchorNames"):
        d["anker"] = list(p["AnchorNames"]) if isinstance(p["AnchorNames"], (list, tuple)) else [str(p["AnchorNames"])]
    for nr, name in ZEICHEN_USER.items():
        v = p.get(_user(nr))
        if v is None:
            continue
        if name in BOOL_ZEICHEN:
            if name == "raster":
                d[name] = bool(v)
            elif v:
                d[name] = True
        elif name in ZAHL_ZEICHEN:
            d[name] = int(v)
        else:
            d[name] = v if isinstance(v, (str, dict)) else str(v)
    return d


def absatzformat_neu(pf: ParagraphFormat) -> dict:
    p, d = pf.properties, {}
    if pf.alignment in ("left", "center", "right", "justify"):
        d["ausrichtung"] = {"left": "links", "center": "mitte", "right": "rechts", "justify": "block"}[pf.alignment]
    else:
        bits = int(_zahl(p.get("BlockAlignment"), 0)) & 0xF
        if bits & 0x8:
            d["ausrichtung"] = "block"
        elif bits & 0x4:
            d["ausrichtung"] = "mitte"
        elif bits & 0x2:
            d["ausrichtung"] = "rechts"
    davor = pf.space_before_px if pf.space_before_px is not None else _zahl(p.get("BlockTopMargin"))
    danach = pf.space_after_px if pf.space_after_px is not None else _zahl(p.get("BlockBottomMargin"))
    links = pf.left_indent_px if pf.left_indent_px is not None else _zahl(p.get("BlockLeftMargin"))
    rechts = pf.right_indent_px if pf.right_indent_px is not None else _zahl(p.get("BlockRightMargin"))
    erste = pf.first_line_indent_px if pf.first_line_indent_px is not None else _zahl(p.get("TextIndent"))
    for name, wert in (("abstand_vor", davor), ("abstand_nach", danach), ("einzug_links", links), ("einzug_rechts", rechts), ("einzug_erste", erste)):
        if wert:
            d[name] = float(wert)
    ls = pf.line_spacing
    if isinstance(ls, LineSpacing):
        art = {"single": "einfach", "multiple": "vielfach", "proportional": "vielfach", "fixed": "genau", "minimum": "mindestens"}.get(ls.kind)
        if art and art != "einfach":
            d["zeilenabstand_art"] = art
            d["zeilenabstand"] = ls.value * 100.0 if ls.kind == "multiple" else ls.value
    policy = int(_zahl(p.get("PageBreakPolicy"), 0))
    if policy & 0x1:
        d["seitenumbruch_vor"] = True
    if policy & 0x10:
        d["seitenumbruch_nach"] = True
    if p.get("TabPositions"):
        d["tabstopps"] = [[t.position, t.kind, t.delimiter] for t in p["TabPositions"] if isinstance(t, TabStop)]
    fond = _farbe_von(p.get("BackgroundBrush"))
    if fond:
        d["hintergrund"] = fond
    for nr, name in ABSATZ_USER.items():
        v = p.get(_user(nr))
        if v is None or name in ("vorlage", "bildanker"):
            continue
        if name in BOOL_ABSATZ:
            if v:
                d[name] = True
        elif name in ZAHL_ABSATZ:
            d[name] = int(v)
        elif name == "abstand_vorher":
            d[name] = float(v)
        else:
            d[name] = v if isinstance(v, str) else str(v)
    return d


class _AltNeu:
    def __init__(self, alt: Document, meta: dict | None = None):
        self.alt = alt
        self.meta = meta or {}
        self.neu = Dokument()
        self.listen: dict = {}
        self.medien: dict = {}
        self.listen_ids: dict = {}                           # Liste der ersten Ebene → Definition
        self.gruppe: int | None = None                       # Definition der Liste, deren Absätze gerade aufeinanderfolgen

    def laufen(self) -> Dokument:
        alt, neu = self.alt, self.neu
        grund = zeichenformat_neu(alt.default_format)
        neu.standardformat = {k: v for k, v in grund.items() if k in ("schrift", "groesse_pt")}
        if alt.document_margin:
            neu.standardformat["rand"] = alt.document_margin
        for abschnitt in alt.sections:
            beginn = ABSCHNITT_BEGINN.get(abschnitt.kind, "naechste")
            seite = abschnitt.page.copy() if hasattr(abschnitt.page, "copy") else abschnitt.page
            neu.abschnitte.append(Abschnitt(neu.neue_id(), self.bloecke(abschnitt.content), seite, beginn))
        for f in alt.notes:
            neu.noten.setdefault(f.kind, {})[f.id] = Note(f.id, f.kind, f.text)
        neu.naechste_id = max(neu.naechste_id, max((f.id for f in alt.notes), default=0) + 1)
        if not neu.abschnitte:
            neu.abschnitte.append(Abschnitt(neu.neue_id(), [Absatz(neu.neue_id())]))
        for a in neu.abschnitte:
            self.ordnen(a.bloecke, True)
        self.zusatzdaten()
        self.vorlagen()
        return neu

    def vorlagen(self) -> None:
        """Die Formatvorlagen des Katalogs (eingebaute mit den Änderungen des Benutzers und die aus der Datei mitgebrachten eigenen) als Vorlagen des Dokuments."""
        from lunivo_writer.editor.text import stile
        for name in stile.namen():
            d = stile.definition(name)
            zeichen = {k: v for k, v in (("groesse_pt", float(d["groesse"]) if d.get("groesse") else None), ("fett", True if d.get("fett") else None),
                                         ("kursiv", True if d.get("kursiv") else None), ("farbe", d.get("farbe") or None), ("schrift", d.get("schrift") or None),
                                         ("durchgestrichen", True if d.get("durch") else None)) if v is not None}
            absatz = {k: v for k, v in (("abstand_vor", d["vor"] / 0.75 if d.get("vor") else None), ("abstand_nach", d["nach"] / 0.75 if d.get("nach") else None),
                                        ("ausrichtung", {"links": "links", "mitte": "mitte", "rechts": "rechts", "block": "block"}.get(d.get("ausr"))),
                                        ("zeilenabstand_art", "vielfach" if d.get("zeilen") else None), ("zeilenabstand", d["zeilen"] * 100.0 if d.get("zeilen") else None),
                                        ("einzug_links", mm_to_px(d["einzug"]) if d.get("einzug") else None)) if v is not None}
            self.neu.vorlagen[name] = Formatvorlage(name, "absatz", d.get("basis") or ("" if name == "Standard" else "Standard"),
                                                    d.get("folge") or ("Standard" if d.get("ebene") else ""), int(d.get("ebene") or 0), zeichen, absatz)
        for a in self.neu.absaetze():
            name = a.format.get("vorlage")
            if name and name not in self.neu.vorlagen:
                del a.format["vorlage"]

    def zusatzdaten(self) -> None:
        """Kommentare, Notentexte, Quellen und Eigenschaften aus dem Meta-Wörterbuch des bisherigen Editors."""
        neu, meta = self.neu, self.meta
        for kid, k in (meta.get("kommentare") or {}).items():
            kid = int(kid)
            neu.kommentare[kid] = Kommentar(kid, str(k.get("autor", "")), str(k.get("initialen", "")), str(k.get("datum", "")), str(k.get("text", "")),
                                            bool(k.get("geloest", False)), k.get("antwort_auf"))
        for art, eintraege in (meta.get("noten") or {}).items():
            if art in ("f", "e"):
                for nid, text in eintraege.items():
                    neu.noten.setdefault(art, {})[int(nid)] = Note(int(nid), art, str(text))
        neu.quellen = [dict(q) for q in (meta.get("quellen") or [])]
        for k, v in meta.items():
            if k not in ("kommentare", "noten", "quellen") and isinstance(v, (str, int, float, bool)):
                neu.eigenschaften[k] = v
        neu.naechste_id = max([neu.naechste_id] + [k + 1 for k in neu.kommentare] + [n + 1 for art in neu.noten.values() for n in art])

    # ---- Blöcke ----
    def ordnen(self, bloecke: list, haupttext: bool = False) -> None:
        """Vor jeder Tabelle und jedem Rahmen und am Ende steht ein Absatz."""
        i = 0
        while i < len(bloecke):
            if isinstance(bloecke[i], (Tabelle, Rahmen)) and (i == 0 or not isinstance(bloecke[i - 1], Absatz)):
                bloecke.insert(i, Absatz(self.neu.neue_id()))
                i += 1
            i += 1
        if not bloecke or not isinstance(bloecke[-1], Absatz):
            bloecke.append(Absatz(self.neu.neue_id()))

    def bloecke(self, inhalt: list) -> list:
        aus: list = []
        self.gruppe = None
        for b in inhalt:
            if isinstance(b, Paragraph):
                if b.format.list_id is None:
                    self.gruppe = None
                a = self.absatz(b)
                if a is not None:
                    aus.append(a)
            elif isinstance(b, Table):
                self.gruppe = None
                aus.append(self.tabelle(b))
                self.gruppe = None
            elif isinstance(b, Frame):
                self.gruppe = None
                r = Rahmen(self.neu.neue_id(), self.bloecke(b.content), self.rahmenformat(b.properties))
                self.ordnen(r.bloecke)
                aus.append(r)
        # Hilfsabsätze, die nur ein frei positioniertes Bild ankern, fallen weg; die Bilder wandern an den nächsten Absatz
        ergebnis: list = []
        offen: list = []
        for b in aus:
            if isinstance(b, Absatz) and b.format.get("hilfsabsatz") and not b.laenge:
                offen.extend(o for o in self.neu.objekte.values() if o.anker == b.id)
                continue
            if offen and isinstance(b, Absatz):
                for o in offen:
                    o.anker = b.id
                offen = []
            ergebnis.append(b)
        if offen:
            letzter = Absatz(self.neu.neue_id())
            for o in offen:
                o.anker = letzter.id
            ergebnis.append(letzter)
        return ergebnis

    def absatz(self, p: Paragraph) -> Absatz:
        neu = self.neu
        a = Absatz(neu.neue_id(), [], absatzformat_neu(p.format), zeichenformat_neu(p.format.char_format), None, 0, True)
        vorlage = p.format.properties.get(_user(1))
        if isinstance(vorlage, str) and vorlage:
            a.format["vorlage"] = vorlage[2:] if vorlage.startswith("x:") else vorlage
        if p.format.list_id is not None:
            a.liste_id, a.ebene, indent = self.liste(p.format.list_id)
            if indent:                                       # die Einrückung der Liste gehört zum linken Rand des Absatzes
                a.format["einzug_links"] = float(a.format.get("einzug_links", 0.0)) + indent
        inhalte: list = []
        for r in p.runs:
            if isinstance(r, TextRun):
                if r.text:
                    inhalte.append(Lauf(r.text, zeichenformat_neu(r.format)))
            elif isinstance(r, Image):
                inhalte.append(self.bild(r))
        a.inhalte = normalisiere(inhalte)
        roh = p.format.properties.get(_user(47))
        if isinstance(roh, str):
            self.freie_bilder(a, roh)
        return a

    def bild(self, r: Image) -> InlineObjekt:
        neu = self.neu
        art, daten = "bild", {}
        roh = r.format.properties.get(P_OBJEKT)
        if isinstance(roh, str):
            try:
                angabe = json.loads(roh)
                art, daten = str(angabe.get("art") or "bild"), {"daten": dict(angabe.get("daten") or {})}
            except ValueError:
                pass
        oid = neu.neue_id()
        schluessel = f"bild-{oid}"
        neu.ressourcen[schluessel] = bytes(r.original if r.original and r.original_format == "svg" else r.raster_png)
        if r.original and r.original_format and r.original_format != "svg":
            daten.setdefault("original_format", r.original_format)
        breite = _zahl(r.format.properties.get("ImageWidth"), 0.0)
        hoehe = _zahl(r.format.properties.get("ImageHeight"), 0.0)
        fmt = zeichenformat_neu(r.format)
        if r.format.properties.get("ImageName"):
            daten.setdefault("name", str(r.format.properties["ImageName"]))
        if art not in ("bild", "form", "textfeld", "wordart", "diagramm", "smartart", "formel", "piktogramm", "zeichenbereich"):
            art = "bild"
        return InlineObjekt(oid, art, breite, hoehe, schluessel, daten, str(r.format.properties.get(P_BILD_ALT, "")), fmt)

    def freie_bilder(self, a: Absatz, roh: str) -> None:
        neu = self.neu
        try:
            angaben = json.loads(roh)
        except ValueError:
            return
        for z, ang in enumerate(angaben if isinstance(angaben, list) else []):
            bild = self.alt.media.get(ang.get("n"))
            oid = neu.neue_id()
            schluessel = ""
            if bild is not None:
                schluessel = f"objekt-{oid}"
                neu.ressourcen[schluessel] = bytes(bild.original if bild.original and bild.original_format == "svg" else bild.raster_png)
            art = str(ang.get("art") or "bild")
            if art not in ("bild", "form", "textfeld", "wordart", "diagramm", "smartart", "formel", "piktogramm", "zeichenbereich"):
                art = "bild"
            daten = {k: v for k, v in ang.items() if k not in ("b", "h", "bh", "xh", "ah", "bv", "yv", "av", "hinter", "art", "n")}
            if ang.get("n"):
                daten["name"] = ang["n"]
            neu.objekte[oid] = FreiesObjekt(oid, a.id, art, float(ang.get("b", 0)), float(ang.get("h", 0)), str(ang.get("bh", "spalte")), float(ang.get("xh", 0)),
                                           str(ang.get("ah") or ""), str(ang.get("bv", "absatz")), float(ang.get("yv", 0)), str(ang.get("av") or ""),
                                           "hinter" if ang.get("hinter") else "vor", z, schluessel, daten, str(ang.get("alt", "")))

    def liste(self, alt_id: int) -> tuple:
        """(Definition, Ebene, Einrückung in Bildpunkten) einer Liste des bisherigen Modells. Aufeinanderfolgende Listenabsätze teilen sich
        eine Definition: die Einrückung der bisherigen Liste (``ListIndent``) wird zur Ebene, so zählt jede Ebene für sich weiter."""
        lf = self.alt.lists.get(alt_id)
        p = lf.properties if lf is not None else {}
        stil = LISTEN_STIL.get(int(_zahl(p.get("ListStyle"), -4)), "dezimal")
        stufe = max(1, int(_zahl(p.get("ListIndent"), 1.0)))
        ebene = min(stufe - 1, LISTEN_EBENEN - 1)
        if stufe == 1 and alt_id in self.listen_ids:             # dieselbe Liste wie zuvor: ihre Zählung läuft weiter
            self.gruppe = self.listen_ids[alt_id]
        elif stufe == 1 or self.gruppe is None:                 # jede Liste der ersten Ebene beginnt eine eigene Zählung
            nid = self.neu.neue_id()
            aufzaehlung = stil in ("disc", "circle", "square")
            vorgabe = ("disc", "circle", "square") if aufzaehlung else ("dezimal", "klein", "roem_klein")
            ebenen = []
            for i in range(LISTEN_EBENEN):
                text = px_to_mm((i + 1) * self.alt.indent_width)
                art = vorgabe[i % 3]
                ebenen.append(ListenEbene(stil=art, format="" if aufzaehlung else "①.", ausr=max(0.0, text - px_to_mm(20.0)), einzug=text))
            self.neu.listen[nid] = ListenDefinition(nid, ebenen, "")
            self.gruppe = nid
            if stufe == 1:
                self.listen_ids[alt_id] = nid
        d = self.neu.listen[self.gruppe]
        vor, nach = str(p.get("ListNumberPrefix") or ""), str(p.get("ListNumberSuffix", "."))
        text = px_to_mm(stufe * self.alt.indent_width)
        d.ebenen[ebene] = ListenEbene(stil=stil, format=f"{vor}①{nach}" if stil not in ("disc", "circle", "square") else "",
                                      ausr=max(0.0, text - px_to_mm(20.0)), einzug=text)
        return self.gruppe, ebene, stufe * self.alt.indent_width

    # ---- Rahmen und Tabellen ----
    def rahmenformat(self, p: dict) -> dict:
        d = {}
        if int(_zahl(p.get("CssFloat"), 0)) in (1, 2):
            d["umfluss"] = int(p["CssFloat"])
        for alt, neu in (("FrameMargin", "rand"), ("FramePadding", "polster"), ("FrameBorder", "rahmen_breite")):
            if _zahl(p.get(alt)):
                d[neu] = float(p[alt])
        if _farbe_von(p.get("FrameBorderBrush")):
            d["rahmen_farbe"] = _farbe_von(p["FrameBorderBrush"])
        fond = _farbe_von(p.get("BackgroundBrush"))
        if fond:
            d["hintergrund"] = fond
        for alt, name in (("FrameWidth", "breite"), ("FrameHeight", "hoehe")):
            v = p.get(alt)
            if isinstance(v, Length) and v.kind in ("fixed", "percentage"):
                d[name] = v.value
                d[name + "_art"] = "fest" if v.kind == "fixed" else "prozent"
        return d

    def tabelle(self, t: Table) -> Tabelle:
        neu = self.neu
        gitter = [[None] * t.columns for _ in range(t.rows)]
        for ri, zeile in enumerate(t.table_rows):
            for c in zeile.cells:
                if not (0 <= c.row < t.rows and 0 <= c.column < t.columns):
                    continue
                z = Zelle(self.bloecke(c.content), self.zellformat(c.properties), max(1, c.row_span), max(1, c.column_span))
                self.ordnen(z.bloecke)
                gitter[c.row][c.column] = z
        for r in range(t.rows):
            for s in range(t.columns):
                z = gitter[r][s]
                if z is None:
                    continue
                for dz in range(z.zeilenspanne):
                    for ds in range(z.spaltenspanne):
                        if (dz or ds) and r + dz < t.rows and s + ds < t.columns:
                            gitter[r + dz][s + ds] = Zelle([], {}, 1, 1, (r, s))
        for r in range(t.rows):
            for s in range(t.columns):
                if gitter[r][s] is None:
                    gitter[r][s] = Zelle([Absatz(neu.neue_id())])
        breiten = [0.0] * t.columns
        for i, v in enumerate(list(t.properties.get("TableColumnWidthConstraints") or ())[:t.columns]):
            if isinstance(v, Length) and v.kind == "fixed":
                breiten[i] = v.value
        hoehen = []
        for zeile in t.table_rows[:t.rows]:
            if zeile.row_height is not None:
                hoehen.append(float(zeile.row_height.value_px))
            else:
                hoehen.append(float(zeile.minimum_height_px or 0.0))
        hoehen += [0.0] * (t.rows - len(hoehen))
        return Tabelle(neu.neue_id(), gitter, breiten, hoehen, self.tabellenformat(t.properties))

    def tabellenformat(self, p: dict) -> dict:
        d = {}
        if _zahl(p.get("FrameBorder")):
            d["rahmen_breite"] = float(p["FrameBorder"])
        if _farbe_von(p.get("FrameBorderBrush")):
            d["rahmen_farbe"] = _farbe_von(p["FrameBorderBrush"])
        if _zahl(p.get("TableCellSpacing")) is not None and "TableCellSpacing" in p:
            d["zellabstand"] = float(p["TableCellSpacing"])
        if "TableCellPadding" in p and _zahl(p["TableCellPadding"]) is not None:
            d["zellpolster"] = float(p["TableCellPadding"])
        if _zahl(p.get("TableHeaderRowCount")):
            d["kopfzeilen"] = int(p["TableHeaderRowCount"])
        bits = int(_zahl(p.get("BlockAlignment"), 0)) & 0xF
        if bits & 0x4:
            d["ausrichtung"] = "mitte"
        elif bits & 0x2:
            d["ausrichtung"] = "rechts"
        w = p.get("FrameWidth", p.get("TableWidth"))
        if isinstance(w, Length) and w.kind in ("fixed", "percentage"):
            d["breite"] = w.value
            d["breite_art"] = "fest" if w.kind == "fixed" else "prozent"
        return d

    def zellformat(self, p: dict) -> dict:
        d = {}
        fond = _farbe_von(p.get("BackgroundBrush"))
        if fond:
            d["hintergrund"] = fond
        senkrecht = int(_zahl(p.get("TextVerticalAlignment"), 0))
        if senkrecht == 3:
            d["vertikal"] = "mitte"
        elif senkrecht == 5:
            d["vertikal"] = "unten"
        for alt, neu in KANTEN:
            breite = _zahl(p.get(f"TableCell{alt}Border"))
            if breite is not None:
                farbe = _farbe_von(p.get(f"TableCell{alt}BorderBrush")) or "#000000"
                stil = int(_zahl(p.get(f"TableCell{alt}BorderStyle"), 10))
                d[f"rahmen_{neu}"] = "keine" if breite <= 0 or stil == 0 else f"{farbe}|{breite * 72.0 / 96.0:.3f}|{'gepunktet' if stil == 1 else 'gestrichelt' if stil == 2 else 'einfach'}"
            pad = _zahl(p.get(f"TableCell{alt}Padding"))
            if pad is not None:
                d[f"polster_{neu}"] = pad
        return d


def alt_zu_neu(alt: Document, meta: dict | None = None) -> Dokument:
    """Das bisherige Modell (samt Meta-Wörterbuch des Editors: Kommentare, Noten, Quellen, Eigenschaften) als ``Dokument``."""
    return _AltNeu(alt, meta).laufen()


def meta_aus_dokument(neu: Dokument, meta: dict | None = None) -> dict:
    """Das Meta-Wörterbuch der Schreiber aus den Zusatzdaten des Dokuments; Einträge, die das Dokument nicht kennt, bleiben aus ``meta`` erhalten."""
    aus = dict(meta or {})
    aus["kommentare"] = {k.id: {"autor": k.autor, "initialen": k.initialen, "datum": k.datum, "text": k.text, "geloest": k.geloest,
                                **({"antwort_auf": k.antwort_auf} if k.antwort_auf is not None else {})} for k in neu.kommentare.values()}
    aus["noten"] = {art: {n.id: n.text for n in noten.values()} for art, noten in neu.noten.items()}
    aus["quellen"] = [dict(q) for q in neu.quellen]
    aus.update(neu.eigenschaften)
    return aus


# ================================================================ neu → alt ================================================================
def zeichenformat_alt(d: dict) -> CharacterFormat:
    p: dict = {}
    fam = d.get("schrift")
    if isinstance(fam, (list, tuple)):
        fam = fam[0] if fam else None
    if fam:
        p["FontFamilies"] = (str(fam),)
    if d.get("groesse_pt"):
        p["FontPointSize"] = float(d["groesse_pt"])
    gewicht = d.get("gewicht") if isinstance(d.get("gewicht"), int) else (700 if d.get("fett") else None)
    if gewicht is not None:
        p["FontWeight"] = gewicht
    if d.get("kursiv"):
        p["FontItalic"] = True
    if _color(d.get("farbe")):
        p["ForegroundBrush"] = Brush(1, _color(d["farbe"]))
    if d.get("unterstrichen"):
        p["FontUnderline"] = True
        p["TextUnderlineStyle"] = UNTER_ART_UMGEKEHRT.get(d.get("unter_art"), 1)
    if _color(d.get("unter_farbe")):
        p["TextUnderlineColor"] = _color(d["unter_farbe"])
    if d.get("durchgestrichen"):
        p["FontStrikeOut"] = True
    if d.get("ueberstrichen"):
        p["FontOverline"] = True
    if d.get("hoch_tief") in ("hoch", "tief"):
        p["TextVerticalAlignment"] = 1 if d["hoch_tief"] == "hoch" else 2
    if d.get("grossbuchstaben"):
        p["FontCapitalization"] = 1
    elif d.get("kapitaelchen"):
        p["FontCapitalization"] = 3
    if d.get("zeichenabstand"):
        p["FontLetterSpacing"] = float(d["zeichenabstand"])
        p["FontLetterSpacingType"] = int(d.get("zeichenabstand_art", 0))
    if _color(d.get("marker")):
        p["BackgroundBrush"] = Brush(1, _color(d["marker"]))
    if d.get("link"):
        p["AnchorHref"] = d["link"]
    if d.get("anker"):
        p["AnchorNames"] = tuple(d["anker"])
    for nr, name in ZEICHEN_USER.items():
        if name in d:
            v = d[name]
            p[_user(nr)] = (1 if v else 0) if name in BOOL_ZEICHEN else v
    cf = CharacterFormat(p)
    cf.family = fam if fam else None
    cf.size_pt = float(d["groesse_pt"]) if d.get("groesse_pt") else None
    cf.weight = gewicht
    cf.italic = True if d.get("kursiv") else None
    cf.foreground_color = _color(d.get("farbe"))
    cf.underline = True if d.get("unterstrichen") else None
    return cf


def absatzformat_alt(d: dict, zeichen: dict, liste_alt: int | None) -> ParagraphFormat:
    p: dict = {}
    pf = ParagraphFormat(p, zeichenformat_alt(zeichen), liste_alt)
    pf.alignment = {"links": "left", "mitte": "center", "rechts": "right", "block": "justify"}.get(d.get("ausrichtung", ""))
    for neu, attr in (("abstand_vor", "space_before_px"), ("abstand_nach", "space_after_px"), ("einzug_links", "left_indent_px"),
                      ("einzug_rechts", "right_indent_px"), ("einzug_erste", "first_line_indent_px")):
        if neu in d:
            setattr(pf, attr, float(d[neu]))
    art = d.get("zeilenabstand_art")
    if art in ("vielfach", "genau", "mindestens"):
        wert = float(d.get("zeilenabstand", 100.0 if art == "vielfach" else 0.0))
        pf.line_spacing = (LineSpacing("proportional", wert) if wert > 10 else LineSpacing("multiple", wert)) if art == "vielfach" \
            else LineSpacing("fixed" if art == "genau" else "minimum", wert)
    policy = (1 if d.get("seitenumbruch_vor") else 0) | (0x10 if d.get("seitenumbruch_nach") else 0)
    if policy:
        p["PageBreakPolicy"] = policy
    if d.get("tabstopps"):
        p["TabPositions"] = tuple(TabStop(float(t[0]), int(t[1]) if len(t) > 1 and not isinstance(t[1], str) else 0, str(t[2]) if len(t) > 2 and t[2] else "")
                                  for t in d["tabstopps"])
    if _color(d.get("hintergrund")):
        p["BackgroundBrush"] = Brush(1, _color(d["hintergrund"]))
    for nr, name in ABSATZ_USER.items():
        if name in d and name not in ("vorlage", "bildanker"):
            v = d[name]
            p[_user(nr)] = (1 if v else 0) if name in BOOL_ABSATZ else v
    return pf


class _NeuAlt:
    def __init__(self, neu: Dokument):
        self.neu = neu
        self.alt = Document()
        self.listen: dict = {}
        self.freie: dict = {}
        for o in neu.objekte.values():
            self.freie.setdefault(o.anker, []).append(o)

    def laufen(self) -> Document:
        neu, alt = self.neu, self.alt
        gf = dict(neu.standardformat)
        alt.default_format = zeichenformat_alt({"schrift": gf.get("schrift"), "groesse_pt": gf.get("groesse_pt")})
        alt.document_margin = float(gf.get("rand", 0.0) or 0.0)
        for a in neu.abschnitte:
            alt.sections.append(Section(ABSCHNITT_BEGINN_ALT.get(a.beginn, "naechste"), a.seite, self.bloecke(a.bloecke)))
        for art, noten in neu.noten.items():
            for n in noten.values():
                alt.notes.append(Footnote(n.id, art, n.text))
        return alt

    def bloecke(self, bloecke: list) -> list:
        aus: list = []
        for b in bloecke:
            if isinstance(b, Absatz):
                aus.append(self.absatz(b))
            elif isinstance(b, Tabelle):
                aus.append(self.tabelle(b))
            elif isinstance(b, Rahmen):
                aus.append(Frame(self.rahmenformat(b.format), self.bloecke(b.bloecke)))
        return aus

    def liste(self, nid: int, ebene: int) -> int:
        """Die Liste des bisherigen Modells für eine Definition und Ebene (Einrückung ``ListIndent`` = Ebene + 1)."""
        schluessel = (nid, ebene)
        if schluessel in self.listen:
            return self.listen[schluessel]
        d = self.neu.listen.get(nid)
        e = d.ebenen[min(ebene, len(d.ebenen) - 1)] if d is not None and d.ebenen else ListenEbene()
        p = {"ListStyle": LISTEN_STIL_UMGEKEHRT.get(e.stil, -4), "ListIndent": float(ebene + 1)}
        if e.format:
            vor, _s, nach = e.format.partition("①")
            p["ListNumberPrefix"], p["ListNumberSuffix"] = vor, nach
        alt_id = len(self.alt.lists) + 1
        self.alt.lists[alt_id] = ListFormat(p)
        self.listen[schluessel] = alt_id
        return alt_id

    def absatz(self, a: Absatz) -> Paragraph:
        liste = self.liste(a.liste_id, a.ebene) if a.liste_id is not None and a.liste_id in self.neu.listen else None
        fmt = dict(a.format)
        if liste is not None and "einzug_links" in fmt:                  # die Einrückung der Liste gehört im bisherigen Modell nicht zum Rand
            fmt["einzug_links"] = max(0.0, float(fmt["einzug_links"]) - (a.ebene + 1) * self.alt.indent_width) or None
            fmt = {k: v for k, v in fmt.items() if v is not None}
        pf = absatzformat_alt(fmt, a.zeichenformat, liste)
        if a.format.get("vorlage"):
            pf.properties[_user(1)] = a.format["vorlage"] if a.format["vorlage"] in _BUILTIN else "x:" + a.format["vorlage"]
        runs: list = []
        for x in a.inhalte:
            if isinstance(x, Lauf):
                runs.append(TextRun(x.text, zeichenformat_alt(x.format)))
            else:
                runs.append(self.bild(x))
        frei = self.freie.get(a.id)
        if frei:
            pf.properties[_user(47)] = json.dumps([self.freies_bild(o) for o in sorted(frei, key=lambda o: o.ebene)], ensure_ascii=False)
        return Paragraph(pf, runs)

    def bild(self, x: InlineObjekt) -> Image:
        roh = self.neu.ressourcen.get(x.ressource, b"")
        daten = dict(x.daten)
        fmt = zeichenformat_alt(x.format)
        fmt.properties["ImageWidth"] = x.breite
        fmt.properties["ImageHeight"] = x.hoehe
        if x.alt_text:
            fmt.properties[P_BILD_ALT] = x.alt_text
        if x.art != "bild" or daten.get("daten"):
            fmt.properties[P_OBJEKT] = json.dumps({"art": x.art, "daten": daten.get("daten") or {}}, ensure_ascii=False)
        if daten.get("name"):
            fmt.properties["ImageName"] = daten["name"]
        svg = roh[:5].lstrip().startswith(b"<") if roh else False
        return Image(roh, fmt, roh if svg else None, "svg" if svg else None)

    def freies_bild(self, o: FreiesObjekt) -> dict:
        name = o.daten.get("name") or f"objekt-{o.id}"
        roh = self.neu.ressourcen.get(o.ressource)
        if roh is not None:
            svg = roh[:5].lstrip().startswith(b"<")
            self.alt.media[name] = Image(roh, CharacterFormat(), roh if svg else None, "svg" if svg else None)
        ang = {k: v for k, v in o.daten.items() if k != "name"}
        ang.update({"n": name, "b": o.breite, "h": o.hoehe, "bh": o.bezug_h, "xh": o.x, "bv": o.bezug_v, "yv": o.y, "art": o.art})
        if o.ausr_h:
            ang["ah"] = o.ausr_h
        if o.ausr_v:
            ang["av"] = o.ausr_v
        if o.umbruch == "hinter":
            ang["hinter"] = True
        if o.alt_text:
            ang["alt"] = o.alt_text
        return ang

    def rahmenformat(self, d: dict) -> dict:
        p: dict = {}
        if d.get("umfluss"):
            p["CssFloat"] = int(d["umfluss"])
        for neu, alt in (("rand", "FrameMargin"), ("polster", "FramePadding"), ("rahmen_breite", "FrameBorder")):
            if d.get(neu):
                p[alt] = float(d[neu])
        if _color(d.get("rahmen_farbe")):
            p["FrameBorderBrush"] = Brush(1, _color(d["rahmen_farbe"]))
        if _color(d.get("hintergrund")):
            p["BackgroundBrush"] = Brush(1, _color(d["hintergrund"]))
        for neu, alt in (("breite", "FrameWidth"), ("hoehe", "FrameHeight")):
            if d.get(neu):
                p[alt] = Length("fixed" if d.get(neu + "_art", "fest") == "fest" else "percentage", float(d[neu]))
        return p

    def tabelle(self, t: Tabelle) -> Table:
        p: dict = {}
        f = t.format
        if f.get("rahmen_breite"):
            p["FrameBorder"] = float(f["rahmen_breite"])
        if _color(f.get("rahmen_farbe")):
            p["FrameBorderBrush"] = Brush(1, _color(f["rahmen_farbe"]))
        if "zellabstand" in f:
            p["TableCellSpacing"] = float(f["zellabstand"])
        if "zellpolster" in f:
            p["TableCellPadding"] = float(f["zellpolster"])
        if f.get("kopfzeilen"):
            p["TableHeaderRowCount"] = int(f["kopfzeilen"])
        if f.get("ausrichtung") in ("mitte", "rechts"):
            p["BlockAlignment"] = 0x4 if f["ausrichtung"] == "mitte" else 0x2
        if f.get("breite"):
            p["FrameWidth"] = Length("fixed" if f.get("breite_art", "fest") == "fest" else "percentage", float(f["breite"]))
        if any(b > 0 for b in t.spaltenbreiten):
            p["TableColumnWidthConstraints"] = tuple(Length("fixed", b) if b > 0 else Length("variable", 0.0) for b in t.spaltenbreiten)
        zeilen: list = []
        for r, zeile in enumerate(t.zellen):
            tz = TableRow([], t.zeilenhoehen[r] or None if r < len(t.zeilenhoehen) else None)
            for s, z in enumerate(zeile):
                if z.verdeckt_von is not None:
                    continue
                tz.cells.append(TableCell(r, s, z.zeilenspanne, z.spaltenspanne, self.zellformat(z.format), self.bloecke(z.bloecke)))
            zeilen.append(tz)
        return Table(t.zeilen, t.spalten, p, zeilen)

    def zellformat(self, d: dict) -> dict:
        p: dict = {}
        if _color(d.get("hintergrund")):
            p["BackgroundBrush"] = Brush(1, _color(d["hintergrund"]))
        if d.get("vertikal") in ("mitte", "unten"):
            p["TextVerticalAlignment"] = 3 if d["vertikal"] == "mitte" else 5
        for alt, neu in KANTEN:
            angabe = d.get(f"rahmen_{neu}")
            if isinstance(angabe, str):
                if angabe == "keine":
                    p[f"TableCell{alt}Border"] = 0.0
                    p[f"TableCell{alt}BorderStyle"] = 0
                else:
                    t = angabe.split("|")
                    try:
                        p[f"TableCell{alt}Border"] = float(t[1]) * 96.0 / 72.0 if len(t) > 1 else 1.0
                    except ValueError:
                        p[f"TableCell{alt}Border"] = 1.0
                    if _color(t[0]):
                        p[f"TableCell{alt}BorderBrush"] = Brush(1, _color(t[0]))
                    art = t[2] if len(t) > 2 else "einfach"
                    p[f"TableCell{alt}BorderStyle"] = 1 if art == "gepunktet" else 2 if art == "gestrichelt" else 10
            if d.get(f"polster_{neu}") is not None:
                p[f"TableCell{alt}Padding"] = float(d[f"polster_{neu}"])
        return p


def neu_zu_alt(neu: Dokument) -> Document:
    """Das maßgebliche Modell als bisheriges Modell, für die vorhandenen Schreiber."""
    return _NeuAlt(neu).laufen()
