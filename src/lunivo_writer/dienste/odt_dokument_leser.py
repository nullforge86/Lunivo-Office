"""ODT/FODT direkt in das Dokumentmodell (``core.document.Dokument``) lesen — ohne das bisherige Modell und ohne ``QTextDocument`` als Zwischenschritt.

Gelesen werden: Absätze und Überschriften (Ausrichtung, Einzüge, Abstände, Seitenumbruch), Textläufe mit Schrift, Größe, fett, kursiv, unterstrichen, durchgestrichen,
hoch/tief, Farbe, Hintergrund und Verweisen, Tabulatoren und Zeilenwechsel, Listen mit Ebenen und Zahlenarten, Tabellen mit verbundenen Zellen und Spaltenbreiten,
Fuß- und Endnoten, Bilder im Text (mit Alternativtext und „dekorativ“), frei positionierte Bilder und einfache Formen, Seiteneinrichtung samt Kopf- und Fußzeile und die
Metadaten. Stile, Seitenlogik und Paketprüfung teilt der Leser mit ``odt_modell_leser``."""
from __future__ import annotations

import base64
import xml.etree.ElementTree as ET
import zipfile

from lunivo_writer.core.document.dokument import (Absatz, FreiesObjekt, InlineObjekt, Lauf, ListenDefinition, ListenEbene, Note, Tabelle, Zelle, neues_dokument,
                                                  normalisiere)
from lunivo_writer.core.document.formatvorlagen import eingebaute_vorlagen
from lunivo_writer.dienste.odt_modell_leser import _Leser, _farbe, _xml
from lunivo_writer.dienste.odt_xml import GRENZE_BYTES, _kurz, _px, _pt, _q
from lunivo_writer.modelle.bericht import DocumentIOError

_ZAHLENART = {"1": "dezimal", "a": "klein", "A": "gross", "i": "roem_klein", "I": "roem_gross"}
_PUNKT = {"◦": "circle", "○": "circle", "▪": "square", "■": "square"}
_AUSRICHTUNG = {"center": "mitte", "end": "rechts", "right": "rechts", "justify": "block"}
_BEZUG_H = {"page": "seite", "page-content": "rand", "paragraph": "spalte"}
_BEZUG_V = {"page": "seite", "page-content": "rand", "paragraph": "absatz"}


def _zeichen(p: dict, stile) -> dict:
    f: dict = {}
    familie = stile.schriften.get(p.get("style:font-name", ""), "") or p.get("fo:font-family", "").strip("'\"")
    if familie:
        f["schrift"] = familie
    groesse = _pt(p.get("fo:font-size"))
    if groesse:
        f["groesse_pt"] = groesse
    if p.get("fo:font-weight") in {"bold", "600", "700", "800", "900"}:
        f["fett"] = True
    if p.get("fo:font-style") in ("italic", "oblique"):
        f["kursiv"] = True
    if p.get("style:text-underline-style") not in (None, "none"):
        f["unterstrichen"] = True
    if p.get("style:text-line-through-style") not in (None, "none"):
        f["durchgestrichen"] = True
    for quelle, name in (("fo:color", "farbe"), ("fo:background-color", "marker")):
        if _farbe(p.get(quelle)):
            f[name] = p[quelle]
    lage = p.get("style:text-position", "").split()
    if lage and lage[0] in ("super", "sub"):
        f["hoch_tief"] = "hoch" if lage[0] == "super" else "tief"
    return f


def _absatz(p: dict) -> dict:
    f: dict = {}
    if p.get("fo:text-align") in _AUSRICHTUNG:
        f["ausrichtung"] = _AUSRICHTUNG[p["fo:text-align"]]
    for quelle, name in (("fo:margin-left", "einzug_links"), ("fo:margin-right", "einzug_rechts"), ("fo:margin-top", "abstand_vor"),
                         ("fo:margin-bottom", "abstand_nach"), ("fo:text-indent", "einzug_erste")):
        if quelle in p and not p[quelle].endswith("%") and _px(p[quelle]):
            f[name] = _px(p[quelle])
    if p.get("fo:break-before") == "page":
        f["seitenumbruch_vor"] = True
    return f


class _DokLeser(_Leser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dok = neues_dokument()
        self.dok.abschnitte[0].bloecke = []
        self.dok.vorlagen.update(eingebaute_vorlagen())
        self.listen_nach_name: dict[str, int] = {}
        self.bilder_n = 0
        self.frei: list = []                         # (Absatz-Id kommt später) freie Objekte des Absatzes in Arbeit

    # ---- Bilder und Rahmen ----
    def _bytes(self, element: ET.Element) -> bytes | None:
        href = element.get(_q("xlink:href"), "")
        binaer = element.find(_q("office:binary-data"))
        if binaer is not None and binaer.text:
            try:
                return base64.b64decode(binaer.text)
            except ValueError:
                return None
        if href and ":" not in href:
            return self.bild_laden(href.lstrip("./"))
        return None

    def _ressource(self, frame: ET.Element) -> str | None:
        """Der Bildschlüssel im Dokument; bei SVG mit PNG-Ersatz zählt das SVG (wie bei LibreOffice)."""
        daten = [d for d in (self._bytes(b) for b in frame.findall(_q("draw:image"))) if d]
        if not daten:
            return None
        roh = next((d for d in daten if d[:5].lstrip().startswith(b"<")), daten[0])
        self.bilder_n += 1
        schluessel = f"odt-bild-{self.bilder_n}"
        self.dok.ressourcen[schluessel] = roh
        return schluessel

    def _frei_lage(self, frame: ET.Element, form: bool) -> dict | None:
        anker = frame.get(_q("text:anchor-type"), "as-char")
        if anker not in ("paragraph", "char", "page"):
            return None
        g = self.stile.eigenschaften("graphic", frame.get(_q("draw:style-name")), "graphic")
        if not form and g.get("style:wrap") != "run-through":           # umflossene Bilder bleiben Bilder im Text
            return None
        hpos, vpos = g.get("style:horizontal-pos", "from-left"), g.get("style:vertical-pos", "from-top")
        return {"bezug_h": "seite" if anker == "page" else _BEZUG_H.get(g.get("style:horizontal-rel", "paragraph"), "spalte"),
                "bezug_v": "seite" if anker == "page" else _BEZUG_V.get(g.get("style:vertical-rel", "paragraph"), "absatz"),
                "ausr_h": hpos if hpos in ("left", "center", "right", "inside", "outside") else "",
                "ausr_v": vpos if vpos in ("top", "center", "bottom") else "",
                "x": _px(frame.get(_q("svg:x")), 0.0), "y": _px(frame.get(_q("svg:y")), 0.0),
                "umbruch": "hinter" if g.get("style:run-through") == "background" else "vor"}

    def _rahmen(self, frame: ET.Element, aus: list) -> None:
        if frame.find(_q("draw:text-box")) is not None:
            self.report.warn("Textrahmen aus der ODT-Datei wurden als Text übernommen.")
            for k in frame.find(_q("draw:text-box")).iter():
                if k.tag in (_q("text:p"), _q("text:h")):
                    aus.append(Lauf("".join(k.itertext()) + " ", {}))
            return
        bild = frame.find(_q("draw:image"))
        if bild is None:
            self.report.warn("Zeichnungen und Formen aus der ODT-Datei wurden nicht übernommen.")
            return
        schluessel = self._ressource(frame)
        if schluessel is None:
            self.report.warn("Ein Bild aus der ODT-Datei war nicht lesbar und wurde übersprungen.")
            return
        breite, hoehe = _px(frame.get(_q("svg:width")), 64.0), _px(frame.get(_q("svg:height")), 64.0)
        beschr = frame.find(_q("svg:desc"))
        alt = (beschr.text or "").strip() if beschr is not None else ""
        dekorativ = self.stile.eigenschaften("graphic", frame.get(_q("draw:style-name")), "graphic").get("loext:decorative") == "true"
        lage = self._frei_lage(frame, False)
        if lage is not None:
            o = FreiesObjekt(self.dok.neue_id(), 0, "bild", breite, hoehe, ressource=schluessel, alt_text="" if dekorativ else alt, **lage)
            if dekorativ:
                o.daten["dekorativ"] = True
            self.frei.append(o)
            return
        daten = {"dekorativ": True} if dekorativ else {}
        aus.append(InlineObjekt(self.dok.neue_id(), "bild", breite, hoehe, schluessel, daten, "" if dekorativ else alt))

    def _form(self, node: ET.Element) -> None:
        art = {_q("draw:rect"): "rechteck", _q("draw:ellipse"): "ellipse"}.get(node.tag)
        lage = self._frei_lage(node, True) if art else None
        if lage is None:
            self.report.warn("Diese Zeichnung aus der ODT-Datei wurde nicht übernommen.")
            return
        eig = self.stile.eigenschaften("graphic", node.get(_q("draw:style-name")), "graphic")
        fuell_art = node.get(_q("draw:fill"), eig.get("draw:fill", "solid"))
        fuell = node.get(_q("draw:fill-color"), eig.get("draw:fill-color", "")) if fuell_art != "none" else ""
        strich_art = node.get(_q("draw:stroke"), eig.get("draw:stroke", "solid"))
        strich = node.get(_q("svg:stroke-color"), eig.get("svg:stroke-color", "#000000")) if strich_art != "none" else ""
        breite, hoehe = _px(node.get(_q("svg:width")), 1.0), _px(node.get(_q("svg:height")), 1.0)
        daten = {"form": art, "breite": breite, "hoehe": hoehe, "fuell": fuell, "linie": strich,
                 "strich": _px(node.get(_q("svg:stroke-width"), eig.get("svg:stroke-width")), 1.0)}
        self.frei.append(FreiesObjekt(self.dok.neue_id(), 0, "form", breite, hoehe, daten=daten, **lage))

    # ---- Läufe ----
    def _lauf(self, text: str, props: dict, aus: list, extra: dict | None = None) -> None:
        if not text:
            return
        f = _zeichen(props, self.stile)
        if extra:
            f.update(extra)
        if aus and isinstance(aus[-1], Lauf) and aus[-1].format == f:
            aus[-1].text += text
        else:
            aus.append(Lauf(text, f))

    def _note(self, node: ET.Element, props: dict, aus: list) -> None:
        art = "e" if node.get(_q("text:note-class")) == "endnote" else "f"
        nid = self.dok.neue_id()
        koerper = node.find(_q("text:note-body"))
        text = " ".join("".join(p.itertext()) for p in (koerper.iter(_q("text:p")) if koerper is not None else ()))
        self.dok.noten.setdefault(art, {})[nid] = Note(nid, art, text.strip())
        aus.append(Lauf("?", {**_zeichen(props, self.stile), "note": f"{art}:{nid}", "hoch_tief": "hoch"}))

    def _laeufe(self, node: ET.Element, props: dict, aus: list, extra: dict | None = None) -> None:
        self._lauf(node.text or "", props, aus, extra)
        for kind in node:
            t = kind.tag
            if t == _q("text:span"):
                p = dict(props)
                p.update(self.stile.eigenschaften("text", kind.get(_q("text:style-name")), "text"))
                self._laeufe(kind, p, aus, extra)
            elif t == _q("text:a"):
                ziel = kind.get(_q("xlink:href"), "")
                self._laeufe(kind, props, aus, {**(extra or {}), **({"link": ziel} if ziel else {})})
            elif t == _q("text:s"):
                try:
                    n = max(1, min(1000, int(kind.get(_q("text:c"), "1"))))
                except ValueError:
                    n = 1
                self._lauf(" " * n, props, aus, extra)
            elif t == _q("text:tab"):
                self._lauf("\t", props, aus, extra)
            elif t == _q("text:line-break"):
                self._lauf(" ", props, aus, extra)
            elif t == _q("text:note"):
                self._note(kind, props, aus)
            elif t == _q("office:annotation"):
                self.report.warn("Kommentare aus der ODT-Datei wurden nicht übernommen.")
            elif t in (_q("text:bookmark"), _q("text:bookmark-start"), _q("text:bookmark-end"), _q("text:reference-mark"),
                       _q("text:reference-mark-start"), _q("text:reference-mark-end"), _q("office:annotation-end")):
                pass
            elif t == _q("draw:frame"):
                self._rahmen(kind, aus)
            elif t in (_q("draw:rect"), _q("draw:ellipse")):
                self._form(kind)
            else:
                self._laeufe(kind, props, aus, extra)
            if kind.tail:
                self._lauf(kind.tail, props, aus, extra)

    # ---- Absätze, Listen ----
    def _liste_id(self, name: str | None) -> int:
        schluessel = name or ""
        if schluessel not in self.listen_nach_name:
            lid = self.dok.neue_id()
            stil = self.stile.listen.get(schluessel)
            ebenen = []
            for n in range(1, 10):
                e = next((k for k in stil if k.get(_q("text:level")) == str(n)), None) if stil is not None else None
                ausr = einzug = 0.0
                if e is not None:
                    pos = e.find(f"{_q('style:list-level-properties')}/{_q('style:list-level-label-alignment')}")
                    if pos is not None:
                        links = _px(pos.get(_q("fo:margin-left")), 0.0) * 25.4 / 96
                        einzug = links
                        ausr = links + _px(pos.get(_q("fo:text-indent")), 0.0) * 25.4 / 96
                if e is not None and e.tag == _q("text:list-level-style-number"):
                    try:
                        start = int(e.get(_q("text:start-value"), "1"))
                    except ValueError:
                        start = 1
                    ebenen.append(ListenEbene(_ZAHLENART.get(e.get(_q("style:num-format"), "1"), "dezimal"), "", start, ausr, einzug))
                else:
                    zeichen = e.get(_q("text:bullet-char"), "•") if e is not None else "•"
                    ebenen.append(ListenEbene(_PUNKT.get(zeichen, "disc"), "", 1, ausr, einzug))
            self.dok.listen[lid] = ListenDefinition(lid, ebenen)
            self.listen_nach_name[schluessel] = lid
        return self.listen_nach_name[schluessel]

    def _paragraph(self, node: ET.Element, listen: tuple | None = None) -> Absatz:
        stil = node.get(_q("text:style-name"))
        pp = self.stile.eigenschaften("paragraph", stil, "paragraph")
        tp = self.stile.eigenschaften("paragraph", stil, "text")
        self.frei = []
        inhalte: list = []
        self._laeufe(node, tp, inhalte)
        inhalte = normalisiere(inhalte)
        format = _absatz(pp)
        if node.tag == _q("text:h"):
            try:
                stufe = max(1, min(9, int(node.get(_q("text:outline-level"), "1"))))
            except ValueError:
                stufe = 1
            format["vorlage"] = f"Überschrift {stufe}"
        liste_id, ebene = None, 0
        if listen is not None:
            name, tiefe = listen
            liste_id, ebene = self._liste_id(name or self.stile.liste_von(stil)), max(0, min(8, tiefe - 1))
        a = Absatz(self.dok.neue_id(), inhalte, format, _zeichen(tp, self.stile), liste_id, ebene)
        for o in self.frei:
            o.anker = a.id
            self.dok.objekte[o.id] = o
        self.frei = []
        return a

    def _inhalte(self, nodes) -> list:
        aus: list = []
        for node in nodes:
            if node.tag in (_q("text:p"), _q("text:h")):
                aus.append(self._paragraph(node))
            elif node.tag == _q("text:list"):
                self._liste(node, aus)
            elif node.tag == _q("table:table"):
                aus.append(self._tabelle(node))
            elif node.tag in (_q("text:section"), _q("text:index-body"), _q("text:table-of-content"), _q("text:alphabetical-index"), _q("text:illustration-index"),
                              _q("text:table-index"), _q("text:bibliography"), _q("text:user-index"), _q("text:object-index")):
                aus.extend(self._inhalte(list(node)))
        return aus

    def _liste(self, node: ET.Element, aus: list, stil: str | None = None, ebene: int = 1) -> None:
        stil = node.get(_q("text:style-name")) or stil
        for item in node:
            if item.tag not in (_q("text:list-item"), _q("text:list-header")):
                continue
            for kind in item:
                if kind.tag in (_q("text:p"), _q("text:h")):
                    aus.append(self._paragraph(kind, (stil, ebene) if item.tag == _q("text:list-item") else None))
                elif kind.tag == _q("text:list"):
                    self._liste(kind, aus, stil, ebene + 1)
                else:
                    aus.extend(self._inhalte([kind]))

    # ---- Tabellen ----
    def _tabelle(self, node: ET.Element) -> Tabelle:
        zeilen_tags = {_q("table:table-row")}
        zeilen_gruppen = {_q("table:table-rows"), _q("table:table-header-rows"), _q("table:table-row-group")}
        spalten_gruppen = {_q("table:table-columns"), _q("table:table-header-columns"), _q("table:table-column-group")}
        zeilen: list[ET.Element] = []
        breiten: list[float] = []

        def sammeln(element: ET.Element) -> None:
            for kind in element:
                if kind.tag in zeilen_tags:
                    zeilen.extend([kind] * self._repeat(kind, "table:number-rows-repeated"))
                elif kind.tag in zeilen_gruppen or kind.tag in spalten_gruppen:
                    sammeln(kind)
                elif kind.tag == _q("table:table-column"):
                    stil = self.stile.eigenschaften("table-column", kind.get(_q("table:style-name")), "table-column")
                    breiten.extend([_px(stil.get("style:column-width"), 0.0)] * self._repeat(kind, "table:number-columns-repeated"))

        sammeln(node)
        reihen = []
        for z in zeilen:
            zellen: list = []
            for kind in z:
                if kind.tag in (_q("table:table-cell"), _q("table:covered-table-cell")):
                    zellen.extend([kind] * self._repeat(kind, "table:number-columns-repeated"))
            reihen.append(zellen)
        spalten = max([len(r) for r in reihen] + [len(breiten), 1])
        gitter: list[list] = [[None] * spalten for _ in reihen]
        besetzt: dict = {}
        raster = False
        for r, zellen in enumerate(reihen):
            for c, el in enumerate(zellen[:spalten]):
                if el.tag == _q("table:covered-table-cell"):
                    gitter[r][c] = Zelle([], {}, 1, 1, besetzt.get((r, c), (r, max(0, c - 1))))
                    continue
                try:
                    zs = max(1, int(el.get(_q("table:number-rows-spanned"), "1")))
                    ss = max(1, min(int(el.get(_q("table:number-columns-spanned"), "1")), spalten - c))
                except ValueError:
                    zs = ss = 1
                for dr in range(zs):
                    for dc in range(ss):
                        if dr or dc:
                            besetzt[(r + dr, c + dc)] = (r, c)
                stil = self.stile.eigenschaften("table-cell", el.get(_q("table:style-name")), "table-cell")
                fmt = {}
                if _farbe(stil.get("fo:background-color")):
                    fmt["hintergrund"] = stil["fo:background-color"]
                if stil.get("fo:border") not in (None, "none"):
                    raster = True
                gitter[r][c] = Zelle(self._inhalte(list(el)) or [Absatz(self.dok.neue_id())], fmt, zs, ss)
        for r in range(len(gitter)):
            for c in range(spalten):
                if gitter[r][c] is None:
                    gitter[r][c] = Zelle([Absatz(self.dok.neue_id())])
        for zeile in gitter:                                       # verdeckte Zellen brauchen einen Absatz, damit jede Gitterstelle gültig bleibt
            for z in zeile:
                if z.verdeckt_von is not None and not z.bloecke:
                    z.bloecke = [Absatz(self.dok.neue_id())]
        spaltenbreiten = breiten if len(breiten) == spalten and sum(breiten) > 0 else [0.0] * spalten
        format = {"rahmen_breite": 1.0, "rahmen_farbe": "#000000"} if raster else {}
        return Tabelle(self.dok.neue_id(), gitter, spaltenbreiten, [0.0] * len(gitter), format)

    def dokument(self):
        body = self.inhalt.find(f"{_q('office:body')}/{_q('office:text')}")
        if body is None:
            raise DocumentIOError("Die Datei ist kein OpenDocument-Text (ODT) oder beschädigt.")
        bloecke = self._inhalte(list(body))
        ordnung: list = []
        for b in bloecke:
            if isinstance(b, Tabelle) and (not ordnung or isinstance(ordnung[-1], Tabelle)):
                ordnung.append(Absatz(self.dok.neue_id()))
            ordnung.append(b)
        if not ordnung or isinstance(ordnung[-1], Tabelle):
            ordnung.append(Absatz(self.dok.neue_id()))
        page = self._seite()
        dok = self.dok
        dok.abschnitte[0].bloecke, dok.abschnitte[0].seite = ordnung, page
        standard = self.stile.eigenschaften("paragraph", "Standard", "text")
        dok.standardformat = {"schrift": _zeichen(standard, self.stile).get("schrift", "Liberation Serif"), "groesse_pt": _pt(standard.get("fo:font-size")) or 12.0}
        titel = self.metaelement.find(f".//{_q('dc:title')}") if self.metaelement is not None else None
        autor = self.metaelement.find(f".//{_q('meta:initial-creator')}") if self.metaelement is not None else None
        if autor is None and self.metaelement is not None:
            autor = self.metaelement.find(f".//{_q('dc:creator')}")
        meta = {"title": (titel.text or "") if titel is not None else "", "author": (autor.text or "") if autor is not None else ""}
        dok.eigenschaften.update({k: v for k, v in meta.items() if v})
        dok.naechste_id = max([dok.naechste_id] + [n + 1 for art in dok.noten.values() for n in art])
        return dok, page, meta, self.report


def lese_odt_dokument(path: str, flach: bool = False):
    """→ ``(Dokument, PageSettings, meta, IOReport)``."""
    from lunivo_writer.dienste.import_grenzen import pruefe_paket
    if flach:
        try:
            with open(path, "rb") as f:
                daten = f.read(GRENZE_BYTES + 1)
        except OSError as ex:
            raise DocumentIOError(f"Datei nicht lesbar: {ex.strerror or ex}") from ex
        if len(daten) > GRENZE_BYTES:
            raise DocumentIOError("Die Datei ist zu groß, um sie sicher zu öffnen.")
        wurzel = _xml(daten)
        return _DokLeser(wurzel, wurzel, wurzel.find(_q("office:meta"))).dokument()
    pruefe_paket(path, "ODT")
    try:
        with zipfile.ZipFile(path) as archiv:
            if sum(i.file_size for i in archiv.infolist()) > GRENZE_BYTES:
                raise DocumentIOError("Die ODT-Datei ist entpackt zu groß, um sie sicher zu öffnen.")
            namen = set(archiv.namelist())
            if "content.xml" not in namen:
                raise DocumentIOError("Die Datei ist kein gültiges ODT-Dokument oder beschädigt (content.xml fehlt).")
            inhalt = _xml(archiv.read("content.xml"))
            stile = _xml(archiv.read("styles.xml")) if "styles.xml" in namen else None
            meta = _xml(archiv.read("meta.xml")) if "meta.xml" in namen else None
            bilder = {n: archiv.read(n) for n in namen if n.startswith("Pictures/") or n.lower().endswith((".png", ".jpg", ".jpeg", ".svg", ".gif", ".bmp", ".emf", ".wmf", ".tif", ".tiff", ".webp"))}
    except (zipfile.BadZipFile, KeyError, OSError) as ex:
        raise DocumentIOError("Die Datei ist kein gültiges ODT-Dokument oder beschädigt.") from ex
    return _DokLeser(inhalt, stile, meta, bilder.get).dokument()
