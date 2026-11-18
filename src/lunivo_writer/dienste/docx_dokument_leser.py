"""DOCX direkt in das Dokumentmodell (``core.document.Dokument``) lesen — ohne ``QTextDocument`` und ohne das bisherige Modell als Zwischenschritt.

Gelesen werden: Absätze mit ihrem wirksamen Format (Docdefaults, Formatvorlagenkette, direkte Angaben: Ausrichtung, Einzüge, Abstände, Zeilenabstand, Seitenumbruch,
Hintergrund) und der Überschriftenvorlage; Textläufe mit wirksamem Zeichenformat (Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen, hoch/tief, Farbe,
Marker, Kapitälchen, Großbuchstaben) und Verweisen; Listen aus ``numbering.xml`` mit allen Ebenen; Tabellen mit verbundenen Zellen (Spalten und Zeilen), Spaltenbreiten,
Zeilenhöhen, Kopfzeilen, Rahmen, Füllung und senkrechter Ausrichtung samt verschachtelten Tabellen; Bilder im Text mit Alternativtext; Seitengröße, Ränder, Kopf- und
Fußzeile mit Seitenzahlfeldern; Titel und Autor.

Dazu: Formen und Textfelder (im Text und frei verankert), Seitenrahmen, Wasserzeichen (Text), Absatzrahmen, Inhaltssteuerelemente (``w:sdt``), Zeichen- und Tabellenvorlagen;
alles, was der Leser nicht selbst abbildet (unbekannte Eigenschaften an Läufen, Absätzen, Tabellen, Zellen, Zeilen und Abschnitten), bleibt als ``docx_roh`` im Modell erhalten
(``docx_erhalt``); die Regeln dafür stehen in ``core/document/kompatibilitaet.py``.

Trifft der Leser auf etwas, das er weder abbildet noch erhalten kann (Gruppen und verknüpfte Textfelder, Bild-Wasserzeichen und andere VML-Objekte, Elemente mit Verweisen auf
andere Teile der Datei, Tabellen in Steuerelementen, Textmarken ohne Inhalt, Abschnitte in Absätzen …), gibt ``lese_docx_dokument`` ``None`` zurück und der Aufrufer liest mit
dem bisherigen Weg: Es wird nie ein Dokument unvollständig gelesen."""
from __future__ import annotations

import re

from lunivo_writer.core.document.bildformat import format_erkennen
from lunivo_writer.dienste.docx_bildeffekte import effekte_aus_element
from lunivo_writer.core.document.dokument import (Abschnitt, Absatz, Formatvorlage, FreiesObjekt, InlineObjekt, Kommentar, Lauf, ListenDefinition, ListenEbene, Note, Tabelle, Zelle, neues_dokument,
                                                  normalisiere)
from lunivo_writer.core.document.formatvorlagen import eingebaute_vorlagen
from lunivo_writer.dienste import docx_erhalt as E, docx_formen as F
from lunivo_writer.modelle.bericht import IOReport
from lunivo_writer.modelle.seite import HeaderFooter, PageSettings

PX_JE_TWIP = 1.0 / 15.0
_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_NS = {"w": _W[1:-1], "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing", "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
       "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture", "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships"}
_R = "{" + _NS["r"] + "}"
_STIL_VORLAGE = {"heading1": "Überschrift 1", "heading2": "Überschrift 2", "heading3": "Überschrift 3", "heading4": "Überschrift 4", "heading5": "Überschrift 5",
                 "heading6": "Überschrift 6", "heading7": "Überschrift 7", "heading8": "Überschrift 8", "heading9": "Überschrift 9", "title": "Titel",
                 "subtitle": "Untertitel", "quote": "Zitat"}
_RPR_BEKANNT = {"rStyle", "rFonts", "sz", "szCs", "b", "bCs", "i", "iCs", "u", "strike", "dstrike", "caps", "smallCaps", "vertAlign", "color", "highlight", "shd", "lang",
                "noProof", "kern", "webHidden", "eastAsianLayout", "ins", "del"}
_PPR_BEKANNT = {"pStyle", "jc", "ind", "spacing", "pageBreakBefore", "shd", "numPr", "outlineLvl", "keepNext", "keepLines", "widowControl", "contextualSpacing", "rPr",
                "suppressAutoHyphens", "snapToGrid", "adjustRightInd", "autoSpaceDE", "autoSpaceDN", "wordWrap", "overflowPunct", "topLinePunct", "kinsoku", "tabs"}
_TAB_ART = {"left": 0, "start": 0, "num": 0, "right": 1, "end": 1, "center": 2, "decimal": 3}
_TAB_FUELL = {"dot": ".", "hyphen": "-", "underscore": "_", "middleDot": "·"}
_ABSCHNITT_ART = {"nextPage": "naechste", "continuous": "fortlaufend", "evenPage": "gerade", "oddPage": "ungerade"}
_HIGHLIGHT = {"yellow": "#ffff00", "green": "#00ff00", "cyan": "#00ffff", "magenta": "#ff00ff", "blue": "#0000ff", "red": "#ff0000", "darkBlue": "#000080",
              "darkCyan": "#008080", "darkGreen": "#008000", "darkMagenta": "#800080", "darkRed": "#800000", "darkYellow": "#808000", "darkGray": "#808080",
              "lightGray": "#c0c0c0", "black": "#000000", "white": "#ffffff"}
_ZAHLENART = {"decimal": "dezimal", "lowerLetter": "klein", "upperLetter": "gross", "lowerRoman": "roem_klein", "upperRoman": "roem_gross"}
_PUNKT = {"•": "disc", "·": "disc", "◦": "circle", "o": "circle", "○": "circle", "▪": "square", "■": "square", "§": "square", "": "disc", "": "disc"}
_PLATZHALTER = "①②③④⑤⑥⑦⑧⑨"
_BILDER = {"png", "jpeg", "gif", "bmp", "tiff", "emf", "wmf", "svg", "webp"}


class _Nicht(Exception):
    """Etwas, das dieser Leser nicht abbildet: der Aufrufer nimmt den bisherigen Weg."""


def _name(e) -> str:
    return e.tag.rsplit("}", 1)[-1] if isinstance(e.tag, str) else ""


def _val(e, attr: str = "val"):
    return None if e is None else e.get(_W + attr)


def _an(e, attr: str = "val") -> bool:
    """Ein- und Ausschalter wie ``w:b``: vorhanden und nicht ausdrücklich aus."""
    return e is not None and e.get(_W + attr) not in ("0", "false", "off")


def _zahl(wert, standard=None):
    try:
        return float(wert)
    except (TypeError, ValueError):
        return standard


def _farbe(wert: str | None) -> str | None:
    return "#" + wert.lower() if wert and re.fullmatch(r"[0-9a-fA-F]{6}", wert) else None


class _Stile:
    """Docdefaults und Formatvorlagen (mit ``basedOn``-Kette) aus ``styles.xml``."""

    def __init__(self, wurzel):
        self.nach_id = {s.get(_W + "styleId"): s for s in wurzel.findall(_W + "style")}
        d = wurzel.find(_W + "docDefaults")
        self.rpr0 = d.find(f"{_W}rPrDefault/{_W}rPr") if d is not None else None
        self.ppr0 = d.find(f"{_W}pPrDefault/{_W}pPr") if d is not None else None
        self.standard = next((s.get(_W + "styleId") for s in wurzel.findall(_W + "style") if s.get(_W + "type") == "paragraph" and s.get(_W + "default") in ("1", "true")), None)

    def kette(self, stil_id: str | None) -> list:
        aus, gesehen = [], set()
        while stil_id and stil_id in self.nach_id and stil_id not in gesehen:
            gesehen.add(stil_id)
            e = self.nach_id[stil_id]
            aus.append(e)
            stil_id = _val(e.find(_W + "basedOn"))
        return aus[::-1]


def _rpr_dict(rpr) -> dict:
    f: dict = {}
    if rpr is None:
        return f
    for kind in rpr:
        n = _name(kind)
        if n not in E.ABGEBILDET["rPr"]:
            continue                                                  # Unbekanntes bleibt als ``docx_roh`` erhalten (``_Leser._roh``), solange es direkt am Lauf steht
        if n == "rFonts":
            familie = kind.get(_W + "ascii") or kind.get(_W + "hAnsi")
            if familie:
                f["schrift"] = familie
        elif n == "sz":
            if _zahl(_val(kind)):
                f["groesse_pt"] = _zahl(_val(kind)) / 2
        elif n == "b":
            f["fett"] = _an(kind)
        elif n == "i":
            f["kursiv"] = _an(kind)
        elif n in ("strike", "dstrike"):
            f["durchgestrichen"] = _an(kind)
        elif n == "caps":
            f["grossbuchstaben"] = _an(kind)
        elif n == "smallCaps":
            f["kapitaelchen"] = _an(kind)
        elif n == "u":
            f["unterstrichen"] = _val(kind) not in (None, "none")
        elif n == "vertAlign":
            f["hoch_tief"] = {"superscript": "hoch", "subscript": "tief"}.get(_val(kind), "")
        elif n == "color":
            f["farbe"] = _farbe(_val(kind)) or ""
        elif n == "highlight":
            f["marker"] = _HIGHLIGHT.get(_val(kind), "")
        elif n == "shd":
            f["marker"] = _farbe(kind.get(_W + "fill")) or ""
    return f


def _ppr_dict(ppr) -> dict:
    f: dict = {}
    if ppr is None:
        return f
    for kind in ppr:
        n = _name(kind)
        if n == "pBdr":
            rahmen = F.absatzrahmen_aus_xml(kind)
            if rahmen:
                f["rahmen"] = rahmen
            continue
        if n not in E.ABGEBILDET["pPr"]:
            continue                                                  # Unbekanntes bleibt als ``docx_roh`` erhalten (``_Leser._roh``)
        if n == "jc":
            f["ausrichtung"] = {"center": "mitte", "right": "rechts", "end": "rechts", "both": "block", "distribute": "block"}.get(_val(kind), "links")
        elif n == "ind":
            for quelle, name in (("left", "einzug_links"), ("start", "einzug_links"), ("right", "einzug_rechts"), ("end", "einzug_rechts")):
                if _zahl(kind.get(_W + quelle)) is not None:
                    f[name] = _zahl(kind.get(_W + quelle)) * PX_JE_TWIP
            if _zahl(kind.get(_W + "firstLine")):
                f["einzug_erste"] = _zahl(kind.get(_W + "firstLine")) * PX_JE_TWIP
            if _zahl(kind.get(_W + "hanging")):
                f["einzug_erste"] = -_zahl(kind.get(_W + "hanging")) * PX_JE_TWIP
        elif n == "spacing":
            for quelle, name in (("before", "abstand_vor"), ("after", "abstand_nach")):
                if _zahl(kind.get(_W + quelle)) is not None:
                    f[name] = _zahl(kind.get(_W + quelle)) * PX_JE_TWIP
            linie, regel = _zahl(kind.get(_W + "line")), kind.get(_W + "lineRule") or "auto"
            if linie:
                if regel == "auto":
                    f["zeilenabstand_art"], f["zeilenabstand"] = "vielfach", linie / 240.0
                else:
                    f["zeilenabstand_art"], f["zeilenabstand"] = ("genau" if regel == "exact" else "mindestens"), linie * PX_JE_TWIP
        elif n == "pageBreakBefore":
            f["seitenumbruch_vor"] = _an(kind)
        elif n == "outlineLvl":
            ebene = _zahl(_val(kind))
            if ebene is not None and 0 <= ebene < 9:
                f["gliederungsebene"] = int(ebene) + 1
        elif n == "bidi":
            f["richtung"] = "rtl" if _an(kind) else "ltr"
        elif n == "shd":
            f["hintergrund"] = _farbe(kind.get(_W + "fill")) or ""
        elif n == "numPr":
            f["_num"] = (_val(kind.find(_W + "numId")), _val(kind.find(_W + "ilvl")))
        elif n == "tabs":
            f["_tabs"] = [(_zahl(k.get(_W + "pos"), 0.0), k.get(_W + "val"), k.get(_W + "leader")) for k in kind.findall(_W + "tab")]
    return f


def _bereinigt(f: dict) -> dict:
    return {k: v for k, v in f.items() if v not in (False, "", None) or k in ("einzug_links", "einzug_rechts", "abstand_vor", "abstand_nach", "einzug_erste")}


class _Leser:
    def __init__(self, pfad: str):
        import docx
        self.d = docx.Document(pfad)
        self._bezugsteil = self.d.part                    # der Teil, dessen Beziehungen gerade gelten (Dokument, Kopf- oder Fußzeile)
        self.hf_bilder: list = []
        self.stile = _Stile(self.d.styles.element)
        self.dok = neues_dokument()
        self.dok.abschnitte[0].bloecke = []
        self.report = IOReport()
        self.nummern = self._nummerierung()
        self.listen: dict = {}
        self.vorlagen = False
        self.umbruch_stelle = None                      # Textstelle eines Seitenumbruchs im gerade gelesenen Absatz
        self.umbruch_naechster = False                  # Seitenumbruch am Ende eines Absatzes: der nächste beginnt auf neuer Seite
        self.bilder = 0
        self.standard_stil = self.stile.standard
        self.noten_text = {"f": self._noten_lesen("footnotes"), "e": self._noten_lesen("endnotes")}
        self.kommentar_quelle = self._kommentare_lesen()
        self.kommentar_modell: dict[str, int] = {}          # Kommentar-Nummer der Datei → Id im Modell
        self.offene_kommentare: list[str] = []
        self.frei: list = []                                  # frei verankerte Objekte des Absatzes in Arbeit
        self.in_tabelle = 0
        self.marken: dict[str, list] = {}                    # offene Textmarken: Nummer → [Name, hat Inhalt]
        self.feld: dict | None = None                        # offenes Feld: {"instr", "phase"}
        self.vorlagen_eigen: dict[str, str] = {}             # Stil-Id → Name der Vorlage im Modell
        self.sdt_zaehler = 0                                 # Inhaltssteuerelemente: laufende Nummer (Gruppe)
        self.wasserzeichen: dict | None = None               # Wasserzeichen aus der Kopfzeile des Abschnitts in Arbeit

    # ---- Noten und Kommentare ----
    def _teil(self, endung: str):
        """Der Dokumentteil zu einer Beziehung (``footnotes``, ``endnotes``, ``comments``) als XML-Wurzel, sonst ``None``."""
        from lxml import etree
        for rel in self.d.part.rels.values():
            if rel.reltype.endswith("/" + endung) and not rel.is_external:
                return etree.fromstring(rel.target_part.blob)
        return None

    def _noten_lesen(self, endung: str) -> dict:
        wurzel = self._teil(endung)
        if wurzel is None:
            return {}
        kind = "footnote" if endung == "footnotes" else "endnote"
        aus = {}
        for n in wurzel.findall(_W + kind):
            if n.get(_W + "type") in ("separator", "continuationSeparator", "continuationNotice"):
                continue
            absaetze = ["".join(t.text or "" for t in p.iter(_W + "t")).strip() for p in n.findall(_W + "p")]
            aus[n.get(_W + "id")] = "\n".join(a for a in absaetze if a)
        return aus

    def _kommentare_lesen(self) -> dict:
        wurzel = self._teil("comments")
        if wurzel is None:
            return {}
        aus = {}
        for c in wurzel.findall(_W + "comment"):
            absaetze = ["".join(t.text or "" for t in p.iter(_W + "t")) for p in c.findall(_W + "p")]
            aus[c.get(_W + "id")] = (c.get(_W + "author") or "", c.get(_W + "initials") or "", c.get(_W + "date") or "", "\n".join(absaetze))
        return aus

    def _kommentar_id(self, nummer: str) -> int:
        if nummer not in self.kommentar_quelle:
            raise _Nicht("Kommentar ohne Text")
        if nummer not in self.kommentar_modell:
            autor, initialen, datum, text = self.kommentar_quelle[nummer]
            kid = self.dok.neue_id()
            self.dok.kommentare[kid] = Kommentar(kid, autor, initialen, datum, text)
            self.kommentar_modell[nummer] = kid
        return self.kommentar_modell[nummer]

    def _note(self, kind, art: str, f: dict, aus: list) -> None:
        text = self.noten_text[art].get(kind.get(_W + "id"))
        if text is None:
            raise _Nicht("Notenverweis ohne Note")
        nid = self.dok.neue_id()
        self.dok.noten.setdefault(art, {})[nid] = Note(nid, art, text)
        aus.append(Lauf("?", {**f, "note": f"{art}:{nid}", "hoch_tief": "hoch"}))

    # ---- Formate ----
    def _zeichenformat(self, stil_id: str | None, run_stil: str | None, rpr) -> dict:
        f = dict(_rpr_dict(self.stile.rpr0))
        for s in self.stile.kette(stil_id) + self.stile.kette(run_stil):
            f.update(_rpr_dict(s.find(_W + "rPr")))
        f.update(_rpr_dict(rpr))
        if run_stil:
            vorlage = self._zeichenvorlage(run_stil)
            if vorlage:
                f["vorlage"] = vorlage
        roh = self._roh(rpr, "rPr")
        if roh:
            f[E.ROH] = roh
        return _bereinigt(f)

    def _roh(self, eltern, art: str, extra=(), ausser=()) -> list:
        """Die Kinder von ``eltern``, die der Leser nicht abbildet, als XML-Texte (siehe ``docx_erhalt``)."""
        try:
            return E.sammeln(eltern, art, extra, ausser)
        except E.Beziehung as ex:
            raise _Nicht(f"Eigenschaft mit Verweis {ex}") from ex

    def _stilkette_xml(self, stil_id: str) -> list:
        """Der Stil und seine Basisstile (der allgemeinste zuerst) als XML-Texte."""
        return [E.als_text(e) for e in self.stile.kette(stil_id)]

    def _zeichenvorlage(self, stil_id: str) -> str | None:
        """Ein Zeichenstil der Datei als ``Formatvorlage`` der Art ``zeichen`` (einmal je Stil); ``None`` für den Standard-Absatzstil und unbekannte Stile."""
        if stil_id in self.vorlagen_eigen:
            return self.vorlagen_eigen[stil_id]
        e = self.stile.nach_id.get(stil_id)
        if e is None or e.get(_W + "type") != "character" or e.get(_W + "default") in ("1", "true"):
            return None
        name = _val(e.find(_W + "name")) or stil_id
        basis_id = _val(e.find(_W + "basedOn"))
        basis = (self._zeichenvorlage(basis_id) or "") if basis_id else ""
        self.dok.vorlagen[name] = Formatvorlage(name, "zeichen", basis, "", 0, _bereinigt(_rpr_dict(e.find(_W + "rPr"))), {},
                                                {"docx_stil_id": stil_id, "docx_stil_xml": self._stilkette_xml(stil_id)})
        self.vorlagen_eigen[stil_id] = name
        return name

    def _tabellenvorlage(self, stil_id: str | None) -> str | None:
        """Ein Tabellenstil der Datei als ``Formatvorlage`` der Art ``tabelle`` (einmal je Stil); der Standardtabellenstil gilt als keiner."""
        if not stil_id:
            return None
        if stil_id in self.vorlagen_eigen:
            return self.vorlagen_eigen[stil_id]
        e = self.stile.nach_id.get(stil_id)
        if e is None or e.get(_W + "type") != "table" or e.get(_W + "default") in ("1", "true"):
            return None
        name = _val(e.find(_W + "name")) or stil_id
        basis_id = _val(e.find(_W + "basedOn"))
        basis = (self._tabellenvorlage(basis_id) or "") if basis_id else ""
        self.dok.vorlagen[name] = Formatvorlage(name, "tabelle", basis, "", 0, _bereinigt(_rpr_dict(e.find(_W + "rPr"))), {},
                                                {"docx_stil_id": stil_id, "docx_stil_xml": self._stilkette_xml(stil_id)})
        self.vorlagen_eigen[stil_id] = name
        return name

    def _absatzformat(self, stil_id: str | None, ppr) -> tuple[dict, dict]:
        """Wirksames Absatzformat (Docdefaults, Stilkette, direkte Angaben) und die direkten Angaben allein. Tabulatoren der Stufen werden vereinigt, ``clear`` entfernt einen."""
        tabs: dict = {}

        def aufnehmen(d: dict) -> None:
            for pos, art, fuell in d.pop("_tabs", ()):
                if art == "clear":
                    tabs.pop(pos, None)
                elif art in _TAB_ART:
                    tabs[pos] = (_TAB_ART[art], _TAB_FUELL.get(fuell or "", ""))

        f = _ppr_dict(self.stile.ppr0)
        aufnehmen(f)
        for s in self.stile.kette(stil_id):
            d = _ppr_dict(s.find(_W + "pPr"))
            aufnehmen(d)
            f.update(d)
        direkt = _ppr_dict(ppr)
        aufnehmen(direkt)
        f.update(direkt)
        if tabs:
            f["tabstopps"] = [[pos * PX_JE_TWIP, art, ""] for pos, (art, _fuell) in sorted(tabs.items())]
            fuell = next((fu for _a, fu in (v for _p, v in sorted(tabs.items())) if fu), "")
            if fuell:
                f["tabfuell"] = fuell
        return f, direkt

    # ---- Listen ----
    def _nummerierung(self) -> dict:
        try:
            teil = self.d.part.numbering_part
        except Exception:                                                          # noqa: BLE001 — kein numbering.xml
            return {}
        wurzel = teil.element
        abstrakt = {a.get(_W + "abstractNumId"): a for a in wurzel.findall(_W + "abstractNum")}
        aus = {}
        for n in wurzel.findall(_W + "num"):
            a = abstrakt.get(_val(n.find(_W + "abstractNumId")))
            if a is not None:
                aus[n.get(_W + "numId")] = (a, {o.get(_W + "ilvl"): _zahl(_val(o.find(_W + "startOverride")))
                                                for o in n.findall(_W + "lvlOverride") if o.find(_W + "startOverride") is not None})
        return aus

    def _liste(self, num_id: str) -> int:
        if num_id not in self.nummern:
            raise _Nicht("Liste ohne Definition")
        a, ueberschreibt = self.nummern[num_id]
        schluessel = (a.get(_W + "abstractNumId"), tuple(sorted((k, v) for k, v in ueberschreibt.items() if v is not None)))
        if schluessel in self.listen:
            return self.listen[schluessel]
        lid = self.dok.neue_id()
        stufen = {l.get(_W + "ilvl"): l for l in a.findall(_W + "lvl")}
        ebenen = []
        for n in range(9):
            l = stufen.get(str(n))
            if l is None:
                ebenen.append(ListenEbene("disc"))
                continue
            art = _val(l.find(_W + "numFmt")) or "decimal"
            text = _val(l.find(_W + "lvlText")) or ""
            start = int(_zahl(_val(l.find(_W + "start")), 1) or 1)
            if str(n) in ueberschreibt and ueberschreibt[str(n)] is not None:
                start = int(ueberschreibt[str(n)])
            ind = l.find(f"{_W}pPr/{_W}ind")
            links = (_zahl(ind.get(_W + "left") or ind.get(_W + "start"), 0.0) if ind is not None else 0.0) * 25.4 / 1440
            haengend = (_zahl(ind.get(_W + "hanging"), 0.0) if ind is not None else 0.0) * 25.4 / 1440
            if art in _ZAHLENART:
                format = re.sub(r"%([1-9])", lambda m: _PLATZHALTER[int(m.group(1)) - 1], text)
                ebenen.append(ListenEbene(_ZAHLENART[art], format, start, links - haengend, links))
            elif art == "bullet":
                ebenen.append(ListenEbene(_PUNKT.get(text, "zeichen"), "", 1, links - haengend, links, text if text not in _PUNKT else ""))
            elif art == "none":                                                   # Ebene ohne Nummer und Zeichen
                ebenen.append(ListenEbene("zeichen", "", 1, links - haengend, links, ""))
            else:                                                                 # andere Zahlenarten (ordinal, Zahlwörter, fremde Schriften …): als Dezimalzahl, mit Meldung
                format = re.sub(r"%([1-9])", lambda m: _PLATZHALTER[int(m.group(1)) - 1], text)
                ebenen.append(ListenEbene("dezimal", format, start, links - haengend, links))
                self.report.warn(f"Die Zahlenart „{art}“ einer Liste wird als gewöhnliche Nummerierung dargestellt.")
        self.dok.listen[lid] = ListenDefinition(lid, ebenen)
        self.listen[schluessel] = lid
        return lid

    # ---- Läufe ----
    def _bild(self, drawing, inline) -> InlineObjekt:
        daten = drawing.find(f".//{{{_NS['a']}}}graphicData")
        if daten is not None and daten.get("uri", "").endswith("/chart"):
            return self._diagramm(daten, inline)
        if daten is None or not daten.get("uri", "").endswith("/picture"):
            raise _Nicht("zusammengesetztes Objekt")
        blip = drawing.find(f".//{{{_NS['a']}}}blip")
        if blip is None or blip.find(f".//{{{_NS['a']}}}ext") is not None or blip.get(_R + "embed") is None:
            raise _Nicht("Bild ohne Datenteil oder mit Erweiterung")
        teil = self._bezugsteil.related_parts.get(blip.get(_R + "embed"))
        roh = teil.blob if teil is not None else None
        if not roh or format_erkennen(roh) not in _BILDER:
            raise _Nicht("Bildformat")
        ext = inline.find(f"{{{_NS['wp']}}}extent")
        breite, hoehe = float(ext.get("cx")) / 9525.0, float(ext.get("cy")) / 9525.0
        docpr = inline.find(f"{{{_NS['wp']}}}docPr")
        alt = (docpr.get("descr") or "") if docpr is not None else ""
        if docpr is not None and docpr.find(f".//{{http://schemas.microsoft.com/office/drawing/2017/decorative}}decorative") is not None:
            raise _Nicht("dekoratives Bild")
        self.bilder += 1
        schluessel = f"docx-bild-{self.bilder}"
        self.dok.ressourcen[schluessel] = roh
        liste = drawing.find(f".//{{{_NS['pic']}}}spPr/{{{_NS['a']}}}effectLst")
        fx = effekte_aus_element(liste) if liste is not None else {}
        return InlineObjekt(self.dok.neue_id(), "bild", breite, hoehe, schluessel, {"fx": fx} if fx else {}, alt)

    def _diagramm(self, daten, inline) -> InlineObjekt:
        """Natives Word-Diagramm als Objekt der Art „diagramm“: Rubriken, Reihen und Werte im Modell, gezeichnet vom Kern; der Diagrammteil bleibt zum Zurückschreiben erhalten."""
        from lunivo_writer.dienste import docx_diagramm
        chart = next((e for e in daten.iter() if isinstance(e.tag, str) and e.tag.endswith("}chart")), None)
        rid = chart.get(_R + "id") if chart is not None else None
        teil = self.d.part.related_parts.get(rid) if rid else None
        ext = inline.find(f"{{{_NS['wp']}}}extent")
        if teil is None or ext is None:
            raise _Nicht("Diagramm ohne Datenteil")
        d = docx_diagramm.diagramm_daten(teil.blob)
        if d is None:
            raise _Nicht("Diagrammart")
        breite, hoehe = float(ext.get("cx")) / 9525.0, float(ext.get("cy")) / 9525.0
        docpr = inline.find(f"{{{_NS['wp']}}}docPr")
        alt = ((docpr.get("descr") or docpr.get("name") or "") if docpr is not None else "") or d.get("titel") or "Diagramm"
        return InlineObjekt(self.dok.neue_id(), "diagramm", breite, hoehe, "", {"diagramm": d, "diagramm_xml": docx_diagramm.ohne_datenquelle(teil.blob)}, alt)

    def _vml_textfeld(self, pict) -> InlineObjekt:
        """Textfeld in VML, das in der Zeile steht, als Objekt der Art „textfeld“ (wie ein Textfeld in DrawingML); Schrift, Größe und Fettdruck aus der Absatzvorlage,
        wenn der Lauf sie nicht selbst angibt. Anderes VML bleibt beim bisherigen Weg."""
        d = F.textfeld_aus_vml(pict)
        if d is None:
            raise _Nicht("VML-Objekt")
        innen = d["daten"]["daten"]
        absatz = d.pop("_vorlage_absatz", None)
        ppr = absatz.find(_W + "pPr") if absatz is not None else None
        stil_id = (_val(ppr.find(_W + "pStyle")) if ppr is not None else None) or self.standard_stil
        z = self._zeichenformat(stil_id, None, None)
        for ziel, quelle in (("schrift", "schrift"), ("pt", "groesse_pt")):
            if z.get(quelle) and (ziel == "schrift" and innen.get("schrift") == "Liberation Sans" or ziel == "pt" and innen.get("pt") == 11):
                innen[ziel] = z[quelle]
        if z.get("fett"):
            innen["fett"] = True
        return InlineObjekt(self.dok.neue_id(), d["art"], d["breite"], d["hoehe"], "", d["daten"], d["alt"])

    def _zeichnung(self, drawing, aus: list) -> None:
        """Eine Zeichnung im Lauf: im Text (``wp:inline``) oder frei verankert (``wp:anchor``)."""
        inline = drawing.find(f"{{{_NS['wp']}}}inline")
        if inline is not None:
            aus.append(self._objekt(drawing, inline))
            return
        anker = drawing.find(f"{{{_NS['wp']}}}anchor")
        if anker is None:
            raise _Nicht("Objekt ohne Verankerung")
        self._frei_objekt(drawing, anker)

    def _objekt(self, drawing, huelle) -> InlineObjekt:
        """Bild, Form oder Textfeld der Zeichnung als Objekt des Modells (``huelle``: ``wp:inline`` oder ``wp:anchor``)."""
        if not F.ist_form(drawing):
            return self._bild(drawing, huelle)
        try:
            d = F.form_aus_zeichnung(drawing, huelle)
        except (E.Beziehung, ValueError) as ex:
            raise _Nicht(f"Form oder Textfeld: {ex}") from ex
        return InlineObjekt(self.dok.neue_id(), d["art"], d["breite"], d["hoehe"], "", d["daten"], d["alt"])

    def _frei_objekt(self, drawing, anker) -> None:
        """Ein am Absatz oder an der Seite verankertes Bild als ``FreiesObjekt`` (Lage, Größe, Textumbruch)."""
        if self.in_tabelle:
            raise _Nicht("verankertes Objekt in einer Tabelle")
        wp = "{" + _NS["wp"] + "}"
        bild = self._objekt(drawing, anker)
        h, v = anker.find(wp + "positionH"), anker.find(wp + "positionV")
        if h is None or v is None:
            raise _Nicht("Lage des Objekts")
        bezug_h = {"page": "seite", "margin": "rand", "column": "spalte"}.get(h.get("relativeFrom"))
        bezug_v = {"page": "seite", "margin": "rand", "paragraph": "absatz", "line": "absatz"}.get(v.get("relativeFrom"))
        if bezug_h is None or bezug_v is None:
            raise _Nicht("Bezug des Objekts")
        werte = []
        for pos, erlaubt in ((h, ("left", "center", "right", "inside", "outside")), (v, ("top", "center", "bottom"))):
            ausr, versatz = "", 0.0
            al, off = pos.find(wp + "align"), pos.find(wp + "posOffset")
            if al is not None:
                if (al.text or "") not in erlaubt:
                    raise _Nicht("Ausrichtung des Objekts")
                ausr = al.text
            elif off is not None:
                versatz = float(off.text or 0) / 9525.0
            werte.append((ausr, versatz))
        if anker.find(wp + "wrapNone") is not None:
            umbruch = "hinter" if anker.get("behindDoc") in ("1", "true") else "vor"
        elif anker.find(wp + "wrapSquare") is not None:
            umbruch = "quadrat"
        elif anker.find(wp + "wrapTight") is not None or anker.find(wp + "wrapThrough") is not None:
            umbruch = "eng"
        elif anker.find(wp + "wrapTopAndBottom") is not None:
            umbruch = "oben_unten"
        else:
            raise _Nicht("Textumbruch des Objekts")
        self.frei.append(FreiesObjekt(self.dok.neue_id(), 0, bild.art, bild.breite, bild.hoehe, bezug_h, werte[0][1], werte[0][0], bezug_v, werte[1][1], werte[1][0],
                                      umbruch, 0, bild.ressource, bild.daten, bild.alt_text))

    def _laeufe(self, absatz_el, stil_id: str | None, aus: list) -> None:
        for kind in absatz_el:
            n = _name(kind)
            if n == "pPr" or n == "proofErr":
                continue
            if n == "sdt":
                self._sdt_laeufe(kind, stil_id, aus)
                continue
            if n == "commentRangeStart":
                self.offene_kommentare.append(kind.get(_W + "id"))
                continue
            if n == "commentRangeEnd":
                if kind.get(_W + "id") in self.offene_kommentare:
                    self.offene_kommentare.remove(kind.get(_W + "id"))
                continue
            if n == "bookmarkStart":
                name = kind.get(_W + "name") or ""
                if not name.startswith("_"):                     # versteckte Textmarken (``_GoBack``, ``_Toc…``) bleiben außen vor
                    self.marken[kind.get(_W + "id")] = [name, False]
                continue
            if n == "bookmarkEnd":
                m = self.marken.pop(kind.get(_W + "id"), None)
                if m is not None and not m[1]:
                    raise _Nicht("Textmarke ohne Inhalt")
                continue
            if n in ("ins", "del"):
                marke = {"aenderung": n, "autor": kind.get(_W + "author") or "", "datum": kind.get(_W + "date") or ""}
                for r in kind:
                    if _name(r) == "r":
                        self._lauf(r, stil_id, aus, None, marke)
                    elif _name(r) != "proofErr":
                        raise _Nicht(f"Inhalt einer Änderung {_name(r)}")
                continue
            if n == "fldSimple":
                if self.feld is not None:
                    raise _Nicht("verschachteltes Feld")
                self.feld = {"instr": (kind.get(_W + "instr") or "").strip(), "phase": "ergebnis"}
                for r in kind:
                    if _name(r) == "r":
                        self._lauf(r, stil_id, aus, None)
                    elif _name(r) not in ("proofErr",):
                        raise _Nicht(f"Feldinhalt {_name(r)}")
                self.feld = None
                continue
            if n == "r":
                self._lauf(kind, stil_id, aus, None)
            elif n == "hyperlink":
                ziel = kind.get(_R + "id")
                if kind.get(_W + "anchor"):
                    link = "#" + kind.get(_W + "anchor")
                else:
                    link = self.d.part.rels[ziel].target_ref if ziel in self.d.part.rels else None
                if not link:
                    raise _Nicht("Verweis ohne Ziel")
                for r in kind:
                    if _name(r) == "r":
                        self._lauf(r, stil_id, aus, link)
                    elif _name(r) not in ("proofErr", "bookmarkStart", "bookmarkEnd"):
                        raise _Nicht(f"Verweisinhalt {_name(r)}")
            else:
                raise _Nicht(f"Absatzinhalt {n}")

    def _sdt_laeufe(self, sdt, stil_id: str | None, aus: list) -> None:
        """Ein Inhaltssteuerelement im Text: die Läufe darin tragen ``docx_sdt`` (Gruppe und ``w:sdtPr``); der Schreiber fasst gleiche Gruppen wieder zusammen."""
        pr, inhalt = sdt.find(_W + "sdtPr"), sdt.find(_W + "sdtContent")
        if inhalt is None or (pr is not None and E.hat_beziehung(pr)):
            raise _Nicht("Inhaltssteuerelement im Text")
        innen: list = []
        self._laeufe(inhalt, stil_id, innen)
        if not innen:
            raise _Nicht("leeres Inhaltssteuerelement im Text")
        self.sdt_zaehler += 1
        marke = {"gruppe": self.sdt_zaehler, "pr": E.als_text(pr) if pr is not None else ""}
        for x in innen:
            if "docx_sdt" in x.format:
                raise _Nicht("verschachteltes Inhaltssteuerelement")
            x.format = {**x.format, "docx_sdt": marke}
        aus.extend(innen)

    def _sdt_bloecke(self, sdt) -> list:
        """Ein Inhaltssteuerelement zwischen Absätzen (Block): die Absätze darin, jeder mit ``docx_sdt`` (Gruppe, ``w:sdtPr``, ``w:sdtEndPr``)."""
        pr, ende, inhalt = sdt.find(_W + "sdtPr"), sdt.find(_W + "sdtEndPr"), sdt.find(_W + "sdtContent")
        if inhalt is None or any(E.hat_beziehung(x) for x in (pr, ende) if x is not None):
            raise _Nicht("Inhaltssteuerelement")
        bl = self.bloecke(inhalt)
        if not bl or any(not isinstance(b, Absatz) or "docx_sdt" in b.format for b in bl):
            raise _Nicht("Inhaltssteuerelement mit Tabelle oder verschachtelt")
        self.sdt_zaehler += 1
        marke = {"gruppe": self.sdt_zaehler, "pr": E.als_text(pr) if pr is not None else "", "ende": E.als_text(ende) if ende is not None else ""}
        for b in bl:
            b.format["docx_sdt"] = marke
        return bl

    def _lauf(self, r, stil_id: str | None, aus: list, link: str | None, marke: dict | None = None) -> None:
        rpr = r.find(_W + "rPr")
        f = self._zeichenformat(stil_id, _val(rpr.find(_W + "rStyle")) if rpr is not None else None, rpr)
        if marke:
            f.update(marke)
        if link:
            f["link"] = link
        if self.offene_kommentare:
            f["kommentar"] = self._kommentar_id(self.offene_kommentare[-1])
        if self.marken:
            f["anker"] = tuple(sorted(m[0] for m in self.marken.values()))
        vorher = self._laenge(aus)
        for kind in r:
            n = _name(kind)
            if n == "rPr" or n in ("lastRenderedPageBreak", "softHyphen", "commentReference"):
                continue
            if n == "fldChar":
                art = _val(kind, "fldCharType")
                if art == "begin":
                    if kind.find(_W + "ffData") is not None:
                        raise _Nicht("Formularfeld (w:ffData)")                  # Textfeld, Kontrollkästchen und Liste der älteren Formulare: der bisherige Weg
                    if self.feld is not None:
                        raise _Nicht("verschachteltes Feld")
                    self.feld = {"instr": "", "phase": "instr"}
                elif art == "separate":
                    if self.feld is None:
                        raise _Nicht("Feldtrenner ohne Anfang")
                    self.feld["phase"], self.feld["instr"] = "ergebnis", self.feld["instr"].strip()
                elif art == "end":
                    if self.feld is None or self.feld["phase"] != "ergebnis":
                        raise _Nicht("Feld ohne Ergebnis")
                    self.feld = None
                else:
                    raise _Nicht("Feldzeichen")
                continue
            if n == "instrText":
                if self.feld is None or self.feld["phase"] != "instr":
                    raise _Nicht("Feldanweisung außerhalb eines Feldes")
                self.feld["instr"] += kind.text or ""
                continue
            if self.feld is not None and self.feld["phase"] == "instr":
                continue                                        # zwischen Anfang und Trenner steht nur die Anweisung
            if self.feld is not None and n in ("t", "delText", "tab", "br", "cr"):
                f = {**f, "feld": self.feld["instr"]}
            if n == "footnoteReference":
                self._note(kind, "f", {k: v for k, v in f.items() if k != "kommentar"}, aus)
                continue
            if n == "endnoteReference":
                self._note(kind, "e", {k: v for k, v in f.items() if k != "kommentar"}, aus)
                continue
            if n in ("footnoteRef", "endnoteRef"):
                continue
            if n in ("t", "delText"):
                self._text(kind.text or "", f, aus)
            elif n == "tab":
                self._text("\t", f, aus)
            elif n == "br":
                if _val(kind, "type") in (None, "textWrapping"):
                    self._text(" ", f, aus)
                elif _val(kind, "type") == "page" and self.umbruch_stelle is None:
                    self.umbruch_stelle = self._laenge(aus)     # Absatz bleibt erhalten; die Wirkung des Umbruchs setzt ``absatz``
                else:
                    raise _Nicht("Seiten- oder Spaltenumbruch im Absatz")
            elif n == "cr":
                self._text(" ", f, aus)
            elif n == "noBreakHyphen":
                self._text("‑", f, aus)
            elif n == "drawing":
                self._oder_roh(kind, aus, lambda kind=kind: self._zeichnung(kind, aus))
            elif n == "AlternateContent":
                self._oder_roh(kind, aus, lambda kind=kind: self._alternativinhalt(kind, aus))
            elif n == "pict":
                self._oder_roh(kind, aus, lambda kind=kind: aus.append(self._vml_textfeld(kind)))
            else:
                raise _Nicht(f"Laufinhalt {n}")
        if self._laenge(aus) > vorher:
            for m in self.marken.values():
                m[1] = True

    def _alternativinhalt(self, kind, aus: list) -> None:
        wahl = kind.find("{http://schemas.openxmlformats.org/markup-compatibility/2006}Choice")
        zeichnung = wahl.find(_W + "drawing") if wahl is not None else None
        if zeichnung is None:
            raise _Nicht("Alternativinhalt")
        self._zeichnung(zeichnung, aus)                 # die Ausweichfassung (VML) bleibt unbeachtet

    def _oder_roh(self, element, aus: list, versuch) -> None:
        """Das Objekt abbilden; gelingt das nicht (Gruppen, SmartArt, VML außerhalb der Zeile, Formen mit besonderer Lage …), bleibt es als ``roh``-Objekt erhalten."""
        try:
            versuch()
        except _Nicht as ex:
            aus.append(self._roh_objekt(element, str(ex)))

    def _roh_objekt(self, element, grund: str) -> InlineObjekt:
        """Ein Objekt, das das Modell nicht abbildet, unverändert aufbewahren: der Quelltext (XML) und die Datenteile, auf die er verweist (Bilder, SmartArt-Daten …).
        Es steht als Platzhalter im Text und wird beim Speichern als DOCX wieder so geschrieben, wie es war. Verweise nach außen (verknüpfte Dateien) lassen sich nicht
        aufbewahren: dann bleibt es bei der Meldung, dass die Datei nicht geöffnet wird."""
        from lxml import etree
        r_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
        teile: dict = {}
        for e in element.iter():
            for k, v in e.attrib.items():
                if not k.startswith(r_ns) or v in teile:
                    continue
                teil = self._bezugsteil.related_parts.get(v)
                if teil is None:
                    raise _Nicht(f"{grund} (Verweis {v} nicht aufbewahrbar)")
                schluessel = f"docx-roh-{self.dok.neue_id()}"
                self.dok.ressourcen[schluessel] = bytes(teil.blob)
                teile[v] = {"ressource": schluessel, "name": str(teil.partname), "typ": teil.content_type, "beziehung": self._bezugsteil.rels[v].reltype}
        ext = element.find(f".//{{{_NS['wp']}}}extent")
        docpr = element.find(f".//{{{_NS['wp']}}}docPr")
        try:
            breite, hoehe = float(ext.get("cx")) / 9525.0, float(ext.get("cy")) / 9525.0
        except (AttributeError, TypeError, ValueError):
            breite, hoehe = 96.0, 48.0
        alt = (docpr.get("descr") or docpr.get("name") or "") if docpr is not None else ""
        self.report.warn(f"Ein Objekt ({grund}) wird nicht dargestellt, aber unverändert erhalten und beim Speichern als DOCX wieder geschrieben.")
        return InlineObjekt(self.dok.neue_id(), "roh", breite, hoehe, "", {"xml": etree.tostring(element, encoding="unicode"), "teile": teile, "grund": grund}, alt)

    @staticmethod
    def _laenge(aus: list) -> int:
        return sum(len(x.text) if isinstance(x, Lauf) else 1 for x in aus)

    @staticmethod
    def _text(text: str, f: dict, aus: list) -> None:
        if not text:
            return
        if aus and isinstance(aus[-1], Lauf) and aus[-1].format == f:
            aus[-1].text += text
        else:
            aus.append(Lauf(text, dict(f)))

    # ---- Absätze ----
    def _vorlage(self, stil_id: str) -> str | None:
        """Eine eigene Formatvorlage der Datei als ``Formatvorlage`` des Modells (einmal je Stil); ``None`` bei Zeichen- und Tabellenstilen."""
        if stil_id in self.vorlagen_eigen:
            return self.vorlagen_eigen[stil_id]
        e = self.stile.nach_id.get(stil_id)
        if e is None or e.get(_W + "type") != "paragraph":
            return None
        name = _val(e.find(_W + "name")) or stil_id
        if name in self.dok.vorlagen or name.lower() in ("normal", "standard"):
            return None
        basis_id = _val(e.find(_W + "basedOn"))
        basis = "Standard"
        if basis_id and basis_id != self.standard_stil:
            basis = _STIL_VORLAGE.get(basis_id.lower()) or self._vorlage(basis_id) or "Standard"
        absatz = _ppr_dict(e.find(_W + "pPr"))
        absatz.pop("_num", None)
        absatz.pop("_tabs", None)
        ppr_stil = e.find(_W + "pPr")
        zusatz = {}
        roh_p = self._roh(ppr_stil, "pPr", {"pBdr"} if absatz.get("rahmen") else ())
        roh_r = self._roh(e.find(_W + "rPr"), "rPr")
        if roh_p:
            zusatz["docx_roh_ppr"] = roh_p
        if roh_r:
            zusatz["docx_roh_rpr"] = roh_r
        self.dok.vorlagen[name] = Formatvorlage(name, "absatz", basis, "", 0, _bereinigt(_rpr_dict(e.find(_W + "rPr"))), _bereinigt(absatz), zusatz)
        self.vorlagen_eigen[stil_id] = name
        self.vorlagen = True
        return name

    def absatz(self, p, ende_ok: bool = False) -> Absatz:
        ppr = p.find(_W + "pPr")
        if ppr is not None and ppr.find(_W + "sectPr") is not None and not ende_ok:
            raise _Nicht("Abschnittswechsel")
        stil_id = _val(ppr.find(_W + "pStyle")) if ppr is not None else None
        stil_id = stil_id or self.standard_stil
        format, direkt = self._absatzformat(stil_id, ppr)
        num = format.pop("_num", None)
        direkt.pop("_num", None)
        inhalte: list = []
        self.frei = []
        neue_seite, self.umbruch_naechster = self.umbruch_naechster, False
        self.umbruch_stelle = None
        self._laeufe(p, stil_id, inhalte)
        if self.umbruch_stelle is not None:
            if self.umbruch_stelle == 0 and self._laenge(inhalte) > 0:
                neue_seite = True                                   # Umbruch vor dem Inhalt: der Absatz beginnt auf neuer Seite
            elif self.umbruch_stelle == self._laenge(inhalte):
                self.umbruch_naechster = True                       # Umbruch am Ende oder allein im Absatz: der leere Absatz bleibt, der nächste beginnt auf neuer Seite (wie in der Referenzdarstellung)
            else:
                raise _Nicht("Seitenumbruch mitten im Absatz")
            self.umbruch_stelle = None
        if neue_seite:
            format["seitenumbruch_vor"] = True
        if self.feld is not None:
            raise _Nicht("Feld über mehrere Absätze")
        liste_id, ebene = None, 0
        if num and num[0] not in (None, "0"):
            liste_id, ebene = self._liste(num[0]), int(_zahl(num[1], 0) or 0)
            for k in ("einzug_links", "einzug_erste"):                      # Einzug und Hängen kommen aus der Liste, sofern der Absatz sie nicht selbst setzt
                if k not in direkt:
                    format.pop(k, None)
        format = _bereinigt(format)
        bdr = ppr.find(_W + "pBdr") if ppr is not None else None
        roh = self._roh(ppr, "pPr", {"pBdr"} if bdr is not None and F.absatzrahmen_aus_xml(bdr) else ())
        if roh:
            format[E.ROH] = roh
        if stil_id and stil_id.lower() in _STIL_VORLAGE:
            format["vorlage"] = _STIL_VORLAGE[stil_id.lower()]
            self.vorlagen = True
        elif stil_id and stil_id != self.standard_stil and self._vorlage(stil_id):
            format["vorlage"] = self._vorlage(stil_id)
        rpr_marke = ppr.find(_W + "rPr") if ppr is not None else None
        a = Absatz(self.dok.neue_id(), normalisiere(inhalte), format, self._zeichenformat(stil_id, None, rpr_marke), liste_id, max(0, min(8, ebene)))
        for o in self.frei:
            o.anker = a.id
            self.dok.objekte[o.id] = o
        self.frei = []
        return a

    # ---- Tabellen ----
    def _rahmen(self, tblpr, stil_id: str | None) -> dict:
        quellen = [s.find(f"{_W}tblPr/{_W}tblBorders") for s in self.stile.kette(stil_id)] + [tblpr.find(_W + "tblBorders") if tblpr is not None else None]
        raender = None
        for q in quellen:
            if q is not None:
                raender = q
        if raender is None:
            return {}
        sichtbar = [k for k in raender if _val(k) not in (None, "nil", "none")]
        if not sichtbar:
            return {}
        k = sichtbar[0]
        pt = (_zahl(k.get(_W + "sz"), 4) or 4) / 8.0
        return {"rahmen_breite": pt / 0.75, "rahmen_farbe": _farbe(k.get(_W + "color")) or "#000000"}

    @staticmethod
    def _sechs_gleich(bd) -> bool:
        """Ob ``w:tblBorders`` alle sechs Kanten mit derselben Linie nennt (nur dann fasst das Modell sie vollständig)."""
        werte = set()
        for n in ("top", "left", "bottom", "right", "insideH", "insideV"):
            e = bd.find(_W + n)
            if e is None:
                return False
            werte.add((e.get(_W + "val"), e.get(_W + "sz"), e.get(_W + "color")))
        return len(werte) == 1

    def tabelle(self, tbl) -> Tabelle:
        tblpr = tbl.find(_W + "tblPr")
        stil_id = _val(tblpr.find(_W + "tblStyle")) if tblpr is not None else None
        bd = tblpr.find(_W + "tblBorders") if tblpr is not None else None
        format = self._rahmen(tblpr, stil_id)
        abst = tblpr.find(_W + "tblCellSpacing") if tblpr is not None else None            # Word setzt Zellen ohne Zwischenraum, sofern die Tabelle keinen verlangt
        format["zellabstand"] = (_zahl(abst.get(_W + "w"), 0.0) or 0.0) * PX_JE_TWIP if abst is not None else 0.0
        mar = tblpr.find(_W + "tblCellMar") if tblpr is not None else None
        if mar is not None:                                          # Zellrand oben/unten bestimmt die Zeilenhöhe; die Datei behält ihre Angabe in ``docx_roh``
            oben = mar.find(_W + "top")
            if oben is not None and _zahl(oben.get(_W + "w")) is not None:
                format["zellpolster"] = _zahl(oben.get(_W + "w")) * PX_JE_TWIP
        roh = self._roh(tblpr, "tblPr", {"tblW", "tblLayout"}, set() if bd is None or self._sechs_gleich(bd) else {"tblBorders"})
        if roh:
            format[E.ROH] = roh
        vorlage = self._tabellenvorlage(stil_id)
        if vorlage:
            format["vorlage"] = vorlage
        zeilen_roh: dict = {}
        if tblpr is not None and tblpr.find(_W + "tblDescription") is not None:
            format["alt_text"] = _val(tblpr.find(_W + "tblDescription")) or ""
        gitter = tbl.find(_W + "tblGrid")
        spalten_breiten = [(_zahl(g.get(_W + "w"), 0.0) or 0.0) * PX_JE_TWIP for g in gitter.findall(_W + "gridCol")] if gitter is not None else []
        zeilen_el = tbl.findall(_W + "tr")
        reihen: list[list] = []
        hoehen: list[float] = []
        exakt: list[int] = []
        kopf = 0
        for r, tr in enumerate(zeilen_el):
            trpr = tr.find(_W + "trPr")
            hoehe = 0.0
            if trpr is not None:
                for k in trpr:
                    if _name(k) == "trHeight":
                        hoehe = (_zahl(_val(k), 0.0) or 0.0) * PX_JE_TWIP
                        if k.get(_W + "hRule") == "exact":
                            exakt.append(r)
                    elif _name(k) == "tblHeader":
                        kopf = max(kopf, r + 1)
                roh_zeile = self._roh(trpr, "trPr")
                if roh_zeile:
                    zeilen_roh[str(r)] = roh_zeile
            hoehen.append(hoehe)
            zeile = []
            for tc in tr.findall(_W + "tc"):
                zeile.append(tc)
            reihen.append(zeile)
        if not reihen:
            raise _Nicht("leere Tabelle")
        # Gitter aufbauen: je Zelle (Zeile, Spalte, Spaltenspanne, vMerge)
        belegt: list[list] = []
        for r, zeile in enumerate(reihen):
            c = 0
            ausgabe: list = []
            for tc in zeile:
                tcpr = tc.find(_W + "tcPr")
                spanne = int(_zahl(_val(tcpr.find(_W + "gridSpan")) if tcpr is not None else None, 1) or 1)
                vm = tcpr.find(_W + "vMerge") if tcpr is not None else None
                ausgabe.append((c, spanne, tc, None if vm is None else (_val(vm) or "continue")))
                c += spanne
            belegt.append(ausgabe)
        spalten = max(max((c + s for c, s, _t, _v in zeile), default=0) for zeile in belegt) or 1
        gitter_zellen: list[list] = [[None] * spalten for _ in belegt]
        ursprung: dict = {}
        for r, zeile in enumerate(belegt):
            for c, spanne, tc, vm in zeile:
                if vm == "continue" and (r - 1, c) in ursprung:
                    o = ursprung[(r - 1, c)]
                    ursprung[(r, c)] = o
                    z0 = gitter_zellen[o[0]][o[1]]
                    z0.zeilenspanne = r - o[0] + 1
                    for dc in range(spanne):
                        gitter_zellen[r][c + dc] = Zelle([Absatz(self.dok.neue_id())], {}, 1, 1, o)
                    continue
                z = self._zelle(tc)
                z.spaltenspanne = spanne
                gitter_zellen[r][c] = z
                ursprung[(r, c)] = (r, c)
                for dc in range(1, spanne):
                    gitter_zellen[r][c + dc] = Zelle([Absatz(self.dok.neue_id())], {}, 1, 1, (r, c))
        for zeile in gitter_zellen:
            for c in range(spalten):
                if zeile[c] is None:
                    zeile[c] = Zelle([Absatz(self.dok.neue_id())])
        breiten = spalten_breiten if len(spalten_breiten) == spalten and all(b > 0 for b in spalten_breiten) else [0.0] * spalten
        if kopf:
            format["kopfzeilen"] = kopf
        if zeilen_roh:
            format["docx_roh_zeilen"] = zeilen_roh
        if exakt:
            format["zeilenhoehe_exakt"] = exakt
        return Tabelle(self.dok.neue_id(), gitter_zellen, breiten, hoehen, format)

    def _zelle(self, tc) -> Zelle:
        tcpr = tc.find(_W + "tcPr")
        format: dict = {}
        original: set = set()                                        # Eigenschaften, die das Modell nicht ganz fasst und die deshalb im Original bleiben
        for k in (tcpr if tcpr is not None else ()):
            n = _name(k)
            if n in ("tcW", "gridSpan", "vMerge"):
                continue
            if n == "shd":
                if _farbe(k.get(_W + "fill")):
                    format["hintergrund"] = _farbe(k.get(_W + "fill"))
            elif n == "vAlign":
                if _val(k) in ("center", "bottom"):
                    format["vertikal"] = "mitte" if _val(k) == "center" else "unten"
            elif n == "tcBorders":
                if any(_name(kante) not in ("top", "bottom", "left", "start", "right", "end") for kante in k):
                    original.add("tcBorders")                                     # Diagonalen und innere Linien: das Original bleibt erhalten
                    continue
                for kante in k:
                    ort = {"top": "oben", "bottom": "unten", "left": "links", "start": "links", "right": "rechts", "end": "rechts"}.get(_name(kante))
                    if _val(kante) in (None, "nil", "none"):
                        format[f"rahmen_{ort}"] = "keine"
                    else:
                        pt = (_zahl(kante.get(_W + "sz"), 4) or 4) / 8.0
                        format[f"rahmen_{ort}"] = f"{_farbe(kante.get(_W + 'color')) or '#000000'}|{pt:.3f}|einfach"
        roh = self._roh(tcpr, "tcPr", (), original)
        if roh:
            format[E.ROH] = roh
        self.in_tabelle += 1
        try:
            bloecke = self.bloecke(tc)
        finally:
            self.in_tabelle -= 1
        if not bloecke or not isinstance(bloecke[-1], Absatz):
            bloecke.append(Absatz(self.dok.neue_id()))
        return Zelle(bloecke, format)

    # ---- Blöcke ----
    def _textmarke_auf_blockebene(self, kind, n: str) -> None:
        """Textmarke zwischen Absätzen (Anfang vor, Ende nach einem Absatz): wie im Absatz verfolgt; sie umschließt dann den Absatzinhalt. Versteckte (``_…``) bleiben außen vor."""
        if n == "bookmarkStart":
            name = kind.get(_W + "name") or ""
            if not name.startswith("_"):
                self.marken[kind.get(_W + "id")] = [name, False]
        elif n == "bookmarkEnd":
            m = self.marken.pop(kind.get(_W + "id"), None)
            if m is not None and not m[1]:
                raise _Nicht("Textmarke ohne Inhalt")

    def bloecke(self, eltern) -> list:
        aus: list = []
        for kind in eltern:
            n = _name(kind)
            if n == "p":
                aus.append(self.absatz(kind))
            elif n == "tbl":
                aus.append(self.tabelle(kind))
            elif n == "sdt":
                aus.extend(self._sdt_bloecke(kind))
            elif n in ("tcPr", "sectPr", "bookmarkStart", "bookmarkEnd", "proofErr"):
                self._textmarke_auf_blockebene(kind, n)
                continue
            else:
                raise _Nicht(f"Blockinhalt {n}")
        return aus

    # ---- Seite ----
    def _text_hf(self, teil, vorher: HeaderFooter | None = None, ort: str = "") -> HeaderFooter:
        if teil.is_linked_to_previous:
            return vorher.kopie() if vorher is not None else HeaderFooter()          # verknüpft: dieselbe Zeile wie im Abschnitt davor
        self._bezugsteil = teil.part
        try:
            return self._text_hf_lesen(teil, ort)
        finally:
            self._bezugsteil = self.d.part

    def _text_hf_lesen(self, teil, ort: str) -> HeaderFooter:
        zeilen: list[str] = []
        ausr = "center"
        fmt: dict = {}
        erste = True
        for kind in teil._element:
            n = _name(kind)
            if n != "p":
                raise _Nicht("Kopf-/Fußzeile mit Tabelle oder Objekt")
            text, feld = "", None
            ppr = kind.find(_W + "pPr")
            stil_id = _val(ppr.find(_W + "pStyle")) if ppr is not None else None
            if erste:
                j = _ppr_dict(ppr).get("ausrichtung")
                ausr = {"mitte": "center", "rechts": "right", "block": "justify", "links": "left"}.get(j or "", "center") if j else "left"
            for r in kind.iter(_W + "r", _W + "fldSimple"):
                if _name(r) == "fldSimple":
                    anw = (r.get(_W + "instr") or "").split()
                    text += {"PAGE": "{PAGE}", "NUMPAGES": "{PAGES}"}.get(anw[0] if anw else "", None) or self._raise("Feld in Kopf-/Fußzeile")
                    continue
                if r.getparent() is not None and _name(r.getparent()) == "fldSimple":
                    continue
                for k in r:
                    kn = _name(k)
                    if kn == "t":
                        if feld is None:
                            text += k.text or ""
                    elif kn == "tab":
                        text += "\t"
                    elif kn == "fldChar":
                        t = _val(k, "fldCharType")
                        if t == "begin":
                            feld = ""
                        elif t == "end":
                            anw = (feld or "").split()
                            text += {"PAGE": "{PAGE}", "NUMPAGES": "{PAGES}"}.get(anw[0] if anw else "", None) or self._raise("Feld in Kopf-/Fußzeile")
                            feld = None
                    elif kn == "instrText":
                        feld = (feld or "") + (k.text or "")
                    elif kn == "drawing" and ort:
                        self._hf_bild(k, ort, ausr)
                    elif kn == "pict" and F.ist_wasserzeichen(k):
                        self.wasserzeichen = F.wasserzeichen_aus_xml(k) or self._raise("Wasserzeichen")
                    elif kn not in ("rPr", "lastRenderedPageBreak"):
                        raise _Nicht(f"Kopf-/Fußzeileninhalt {kn}")
                if erste and not fmt and (text.strip("{}PAGES") or True):
                    pass
            if erste:
                rpr = kind.find(f"{_W}r/{_W}rPr")
                z = self._zeichenformat(stil_id, None, rpr)
                fmt = {k: v for k, v in (("family", z.get("schrift")), ("size_pt", z.get("groesse_pt")), ("bold", z.get("fett")), ("italic", z.get("kursiv")),
                                         ("underline", z.get("unterstrichen")), ("color", z.get("farbe"))) if v}
            zeilen.append(text)
            erste = False
        text = "\n".join(zeilen).strip("\n")
        return HeaderFooter(text, ausr, fmt, []) if text else HeaderFooter()

    @staticmethod
    def _verknuepft(s, ort: str) -> bool:
        """Gilt der Kopf-/Fußteil ``ort`` des Abschnitts als verknüpft (dann gelten die Bilder des Abschnitts davor)?"""
        teil = {"kopf": s.header, "fuss": s.footer, "kopf1": s.first_page_header, "fuss1": s.first_page_footer,
                "kopf2": s.even_page_header, "fuss2": s.even_page_footer}.get(ort)
        return teil is not None and teil.is_linked_to_previous

    def _hf_bild(self, drawing, ort: str, ausrichtung: str) -> None:
        """Ein Bild in einer Kopf- oder Fußzeile als Seitenbild (``PageSettings.bilder``): im Text steht es oben bzw. unten am Rand der Zeile, verankert mit seiner Lage."""
        wp = "{" + _NS["wp"] + "}"
        inline = drawing.find(wp + "inline")
        anker = drawing.find(wp + "anchor")
        huelle = inline if inline is not None else anker
        if huelle is None:
            raise _Nicht("Objekt in Kopf-/Fußzeile")
        bild = self._objekt(drawing, huelle)
        if bild.art != "bild":
            raise _Nicht(f"{bild.art} in Kopf-/Fußzeile")
        a = {"ort": ort, "ressource": bild.ressource, "b": bild.breite, "h": bild.hoehe, "alt": bild.alt_text, "hinter": False}
        if anker is not None:
            h, v = anker.find(wp + "positionH"), anker.find(wp + "positionV")
            if h is None or v is None:
                raise _Nicht("Lage des Bildes in Kopf-/Fußzeile")
            a["bh"] = {"page": "seite", "margin": "rand", "column": "rand"}.get(h.get("relativeFrom"), "seite")
            a["bv"] = {"page": "seite", "margin": "rand", "paragraph": "seite", "line": "seite"}.get(v.get("relativeFrom"), "seite")
            for pos, (schl_a, schl_x), erlaubt in ((h, ("ah", "xh"), ("left", "center", "right", "inside", "outside")), (v, ("av", "yv"), ("top", "center", "bottom"))):
                al, off = pos.find(wp + "align"), pos.find(wp + "posOffset")
                if al is not None and (al.text or "") in erlaubt:
                    a[schl_a], a[schl_x] = al.text, 0.0
                else:
                    a[schl_a], a[schl_x] = "", float(off.text or 0) / 9525.0 if off is not None else 0.0
            a["hinter"] = anker.get("behindDoc") in ("1", "true")
        else:                                                      # im Text der Zeile: am Seitenrand der Zeile, so ausgerichtet wie der Absatz
            a.update({"bh": "rand", "bv": "seite", "xh": 0.0, "ah": {"right": "right", "center": "center"}.get(ausrichtung, "left"),
                      "yv": 0.0, "av": "", "zeile": True})
        self.hf_bilder.append(a)

    @staticmethod
    def _raise(grund: str):
        raise _Nicht(grund)

    def seite(self, index: int, vorher: PageSettings | None = None) -> tuple[PageSettings, str]:
        """Seiteneinrichtung und Beginn des Abschnitts ``index`` (``w:sectPr`` in Dokumentreihenfolge)."""
        d = self.d
        s = d.sections[index]
        sp = s._sectPr
        cols = sp.find(_W + "cols")
        gerade = d.settings.element.find(_W + "evenAndOddHeaders") is not None
        art = _val(sp.find(_W + "type")) or "nextPage"
        if art not in _ABSCHNITT_ART:
            raise _Nicht("Beginn des Abschnitts")
        p = PageSettings()
        mm = 25.4 / 1440
        sz, mar = sp.find(_W + "pgSz"), sp.find(_W + "pgMar")
        if sz is not None and _zahl(sz.get(_W + "w")) and _zahl(sz.get(_W + "h")):
            p.width_mm, p.height_mm = _zahl(sz.get(_W + "w")) * mm, _zahl(sz.get(_W + "h")) * mm
        if mar is not None:
            for quelle, name in (("top", "margin_top_mm"), ("bottom", "margin_bottom_mm"), ("left", "margin_left_mm"), ("right", "margin_right_mm"),
                                 ("header", "kopf_abstand_mm"), ("footer", "fuss_abstand_mm")):
                if _zahl(mar.get(_W + quelle)) is not None:
                    setattr(p, name, _zahl(mar.get(_W + quelle)) * mm)
        if cols is not None and int(_zahl(cols.get(_W + "num"), 1) or 1) > 1:
            p.spalten = int(_zahl(cols.get(_W + "num"), 1))
            p.spalten_abstand_mm = (_zahl(cols.get(_W + "space"), 720.0) or 0.0) * mm
            p.spalten_linie = cols.get(_W + "sep") in ("1", "true", "on")
            einzeln = cols.findall(_W + "col")
            if cols.get(_W + "equalWidth") in ("0", "false") and einzeln:
                p.spalten_raster_mm = [[(_zahl(c.get(_W + "w"), 0.0) or 0.0) * mm, (_zahl(c.get(_W + "space"), 0.0) or 0.0) * mm] for c in einzeln]
        self.wasserzeichen = None
        p.docx_roh = self._roh(sp, "sectPr")
        hintergrund = d.element.find(_W + "background")
        farbe = hintergrund.get(_W + "color") if hintergrund is not None else None
        if farbe and farbe.lower() != "auto" and re.fullmatch(r"[0-9a-fA-F]{6}", farbe):
            p.color = "#" + farbe.lower()
        zeilen = sp.find(_W + "lnNumType")
        if zeilen is not None:
            p.zeilennummern = True
            p.zeilennummern_neu = "seite" if zeilen.get(_W + "restart") == "newPage" else ""
        nummer = sp.find(_W + "pgNumType")
        if nummer is not None:
            p.seiten_format = _ZAHLENART.get(nummer.get(_W + "fmt") or "decimal", "dezimal")
            p.seiten_start = int(_zahl(nummer.get(_W + "start"), 0) or 0)
        trennung = d.settings.element.find(_W + "autoHyphenation")
        p.silbentrennung = trennung is not None and trennung.get(_W + "val") not in ("0", "false", "off")
        if index > 0:
            p.kopf_verknuepft, p.fuss_verknuepft = bool(s.header.is_linked_to_previous), bool(s.footer.is_linked_to_previous)
        if sp.find(_W + "pgBorders") is not None:
            try:
                p.border = F.seitenrahmen_aus_xml(sp.find(_W + "pgBorders"), self.d.settings.element)
            except E.Beziehung as ex:
                raise _Nicht("Seitenrahmen mit Verweis") from ex
        self.hf_bilder = []
        p.header = self._text_hf(s.header, vorher.header if vorher else None, "kopf")
        p.footer = self._text_hf(s.footer, vorher.footer if vorher else None, "fuss")
        p.diff_first = bool(s.different_first_page_header_footer)
        if p.diff_first:
            p.first_header = self._text_hf(s.first_page_header, vorher.first_header if vorher and vorher.diff_first else None, "kopf1")
            p.first_footer = self._text_hf(s.first_page_footer, vorher.first_footer if vorher and vorher.diff_first else None, "fuss1")
        p.diff_even = gerade
        if gerade:
            p.even_header = self._text_hf(s.even_page_header, vorher.even_header if vorher and vorher.diff_even else None, "kopf2")
            p.even_footer = self._text_hf(s.even_page_footer, vorher.even_footer if vorher and vorher.diff_even else None, "fuss2")
        for a in self.hf_bilder:                                    # Bilder in der Zeile: unter dem Kopfabstand bzw. über dem Fußabstand
            if a.pop("zeile", False):
                a["yv"] = p.kopf_abstand_mm * 96 / 25.4 if a["ort"].startswith("kopf") else max(0.0, (p.height_mm - p.fuss_abstand_mm) * 96 / 25.4 - a["h"])
        geerbt = [dict(a) for a in (vorher.bilder if vorher is not None else []) if isinstance(a, dict)]
        p.bilder = self.hf_bilder + [a for a in geerbt if self._verknuepft(s, a.get("ort", "")) and not any(n.get("ort") == a.get("ort") for n in self.hf_bilder)]
        p.watermark = self.wasserzeichen or (dict(vorher.watermark) if vorher is not None and vorher.watermark and s.header.is_linked_to_previous else None)
        return p, _ABSCHNITT_ART[art]

    def _ordnen(self, bloecke: list) -> list:
        """Vor jeder Tabelle und am Ende eines Abschnitts steht ein Absatz."""
        ordnung: list = []
        for b in bloecke:
            if isinstance(b, Tabelle) and (not ordnung or isinstance(ordnung[-1], Tabelle)):
                ordnung.append(Absatz(self.dok.neue_id()))
            ordnung.append(b)
        if not ordnung or isinstance(ordnung[-1], Tabelle):
            ordnung.append(Absatz(self.dok.neue_id()))
        return ordnung

    def lesen(self):
        body = self.d.element.body
        teile: list[list] = []
        aktuell: list = []
        for kind in body:
            n = _name(kind)
            if n == "p":
                aktuell.append(self.absatz(kind, ende_ok=True))
                if kind.find(f"{_W}pPr/{_W}sectPr") is not None:        # der Absatz beschließt einen Abschnitt
                    teile.append(aktuell)
                    aktuell = []
            elif n == "tbl":
                aktuell.append(self.tabelle(kind))
            elif n == "sdt":
                aktuell.extend(self._sdt_bloecke(kind))
            elif n in ("sectPr", "proofErr", "bookmarkStart", "bookmarkEnd"):
                self._textmarke_auf_blockebene(kind, n)
                continue
            else:
                raise _Nicht(f"Blockinhalt {n}")
        teile.append(aktuell)
        if len(teile) != len(self.d.sections):
            raise _Nicht("Abschnitte")
        dok = self.dok
        seiten: list[PageSettings] = []
        for i, bloecke in enumerate(teile):
            page, beginn = self.seite(i, seiten[-1] if seiten else None)
            seiten.append(page)
            ordnung = self._ordnen(bloecke)
            if i == 0:
                dok.abschnitte[0].bloecke, dok.abschnitte[0].seite = ordnung, page
            else:
                dok.abschnitte.append(Abschnitt(dok.neue_id(), ordnung, page, beginn))
        page = seiten[0]
        if self.vorlagen:
            dok.vorlagen.update(eingebaute_vorlagen())
        z = self._zeichenformat(self.standard_stil, None, None)
        dok.standardformat = {"schrift": z.get("schrift") or "Liberation Sans", "groesse_pt": z.get("groesse_pt") or 11.0}
        grund_absatz, _direkt = self._absatzformat(self.standard_stil, None)           # Absatzabstände der Grundvorlage: gelten auch für Kopf- und Fußzeile
        kopffuss = {k: grund_absatz[k] for k in ("abstand_nach", "zeilenabstand_art", "zeilenabstand") if k in grund_absatz}
        if kopffuss:
            dok.standardformat["kopffuss"] = kopffuss
        kern = self.d.core_properties
        meta = {"title": kern.title or "", "author": kern.author or ""}
        dok.eigenschaften.update({k: v for k, v in meta.items() if v})
        from lunivo_writer.core.document.kompatibilitaet import hinweis_erhalten
        hinweis = hinweis_erhalten(dok)
        if hinweis:
            self.report.warn(hinweis)
        return dok, page, meta, self.report


def lese_docx_dokument(path: str):
    """→ ``(Dokument, PageSettings, meta, IOReport)``. Wirft ``DocumentIOError``, auch wenn die Datei etwas enthält, das dieser Leser noch nicht abbildet
    (es gibt keinen Rückfallweg; die Meldung nennt die Stelle, damit sie hier ergänzt werden kann)."""
    from lunivo_writer.dienste.import_grenzen import pruefe_paket
    from lunivo_writer.modelle.bericht import DocumentIOError
    pruefe_paket(path, "DOCX")
    try:
        return _Leser(path).lesen()
    except _Nicht as e:
        raise DocumentIOError(f"Die DOCX-Datei enthält etwas, das Lunivo noch nicht abbilden kann: {e}.") from e
