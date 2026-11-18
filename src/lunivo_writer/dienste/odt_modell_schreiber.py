"""ODT direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben — ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

Gleiche Dateiaufteilung wie ``odt_schreiber``: ``content.xml`` (Absätze, Überschriften, Zeichenformat samt Formatvorlagen, Listen mit Ebenen, Tabellen mit
verbundenen Zellen, Fuß- und Endnoten, Bilder im Text mit Alternativtext, frei positionierte Bilder und einfache Formen), ``styles.xml`` (Seite, Kopf-/Fußzeile) und
``meta.xml``. Die Bausteine für Namensräume, Maße, Bilder, freie Rahmen und ``styles.xml`` kommen aus ``odt_schreiben_basis`` und ``odt_seite_schreiben``."""
from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

from PySide6.QtGui import QFont, QImage, QTextDocument

from lunivo_writer.core.document.dokument import Absatz, Dokument, InlineObjekt, Rahmen, Tabelle
from lunivo_writer.core.document.formatvorlagen import ueberschriftsebene, wirksames_absatzformat, wirksames_zeichenformat
from lunivo_writer.core.document.listen import ZEICHEN_DER_AUFZAEHLUNG
from lunivo_writer.dienste.odt_schreiben_basis import MIMETYPE, _NS, _bild_elemente, _bild_stil, _frei_form, _frei_rahmen, _frei_stil, _laenge, _odf
from lunivo_writer.dienste.odt_schreiber import (_ATTR_QUOTE, _BILDTYPEN, _Inhalt, _STAND_TAB_STIL, _STAND_ZELLE_STIL, _absatz_vorlage_xml, _manifest, _meta_xml,
                                                _text_eigenschaften, _text_xml, _verluste_melden)
from lunivo_writer.dienste.odt_seite_schreiben import _styles_xml
from lunivo_writer.editor.objekte import bilddaten as BD
from lunivo_writer.modelle.bericht import IOReport

_AUSRICHTUNG = {"mitte": "center", "rechts": "end", "block": "justify"}
_ZAHLENART = {"dezimal": "1", "klein": "a", "gross": "A", "roem_klein": "i", "roem_gross": "I"}
_LAGE = {"hoch": "super", "tief": "sub"}


def _bild(roh: bytes) -> QImage | None:
    """Das Bild hinter den Bytes; das Original (JPEG, SVG, Metafile …) bleibt für das Schreiben erhalten."""
    art = None
    try:
        from lunivo_writer.core.document.bildformat import format_erkennen
        art = format_erkennen(roh)
    except Exception:                                                              # noqa: BLE001
        pass
    if art == "svg":
        img = BD.bild_aus_svg(roh)
    else:
        img = QImage.fromData(roh)
        if img.isNull():
            from lunivo_writer.dienste.vektor_bilder import bild_lesen
            img = bild_lesen(roh)
    if img is None or img.isNull():
        return None
    if art != "png":
        BD.merken(img, roh)
    return img


class _InhaltModell(_Inhalt):
    """``content.xml`` aus dem Modell: überschreibt die Teile von ``_Inhalt``, die am QTextDocument hängen."""

    def __init__(self, dok: Dokument, rep: IOReport):
        super().__init__(None, rep, {})
        self.dok = dok
        self.liste_stile: dict[int, str] = {}

    # ---- Formate ----
    def _absatz_stil_modell(self, f: dict) -> str:
        ausr = _AUSRICHTUNG.get(f.get("ausrichtung", ""), "start")
        schl = (ausr, round(float(f.get("einzug_links") or 0.0), 2), round(float(f.get("einzug_rechts") or 0.0), 2),
                round(float(f.get("abstand_vor") or 0.0), 2), round(float(f.get("abstand_nach") or 0.0), 2), round(float(f.get("einzug_erste") or 0.0), 2),
                bool(f.get("seitenumbruch_vor")))
        if schl not in self.absatz_stile:
            self.absatz_stile[schl] = f"P{len(self.absatz_stile) + 1}"
        return self.absatz_stile[schl]

    def _text_stil_modell(self, f: dict) -> str | None:
        name = f.get("schrift")
        if isinstance(name, (list, tuple)):
            name = name[0] if name else ""
        schl = (name or "", round(float(f.get("groesse_pt") or 0.0), 2), bool(f.get("fett") or (f.get("gewicht") or 0) >= 600), bool(f.get("kursiv")),
                bool(f.get("unterstrichen")), bool(f.get("durchgestrichen") or f.get("doppelt_durch")), _LAGE.get(f.get("hoch_tief", ""), ""),
                f.get("farbe", "") or "", f.get("marker", "") or "")
        if not any(schl):
            return None
        if schl[0]:
            self.schriften.add(schl[0])
        if schl not in self.text_stile:
            self.text_stile[schl] = f"T{len(self.text_stile) + 1}"
        return self.text_stile[schl]

    def _listen_stil_modell(self, lid: int) -> str:
        if lid not in self.liste_stile:
            name = f"L{len(self.liste_stile) + 1}"
            definition = self.dok.listen.get(lid)
            ebenen = []
            for n in range(1, 11):
                e = definition.ebenen[min(n - 1, len(definition.ebenen) - 1)] if definition and definition.ebenen else None
                ausr, einzug = (e.ausr, e.einzug) if e is not None else (0.0, 0.0)
                links = einzug or 6.35 * n
                einrueck = f'<style:list-level-properties text:list-level-position-and-space-mode="label-alignment"><style:list-level-label-alignment text:label-followed-by="listtab" fo:text-indent="{-(links - ausr) if einzug else -6.35:.2f}mm" fo:margin-left="{links:.2f}mm"/></style:list-level-properties>'
                if e is not None and e.stil in _ZAHLENART:
                    ebenen.append(f'<text:list-level-style-number text:level="{n}" style:num-suffix="." style:num-format="{_ZAHLENART[e.stil]}" text:start-value="{e.start}">{einrueck}</text:list-level-style-number>')
                else:
                    zeichen = (e.zeichen if e is not None and e.zeichen else None) or ZEICHEN_DER_AUFZAEHLUNG.get(e.stil if e is not None else "disc", "•")
                    ebenen.append(f'<text:list-level-style-bullet text:level="{n}" text:bullet-char="{escape(zeichen)}">{einrueck}</text:list-level-style-bullet>')
            self.liste_stile[lid] = name
            self.listen_stile[lid] = (name, f'<text:list-style style:name="{name}">{"".join(ebenen)}</text:list-style>')
        return self.liste_stile[lid]

    # ---- Inhalt ----
    def _bild_modell(self, x: InlineObjekt) -> str:
        roh = self.dok.ressourcen.get(x.ressource)
        img = _bild(roh) if roh else None
        if img is None:
            self.rep.warn("Ein Bild war nicht lesbar und fehlt in der ODT-Datei.")
            return ""
        bild = _bild_elemente(img, f"bild{len(self.bilder) + 1}", self.bilder)
        b, h = x.breite or img.width(), x.hoehe or img.height()
        stil = ""
        dekorativ = bool(x.daten.get("dekorativ"))
        if dekorativ:
            nr = len(self.rahmen_stile) + 1
            self.rahmen_stile.append(_bild_stil(f"Fr{nr}"))
            stil = f' draw:style-name="Fr{nr}"'
        beschr = f"<svg:desc>{escape(x.alt_text)}</svg:desc>" if x.alt_text and not dekorativ else ""
        return (f'<draw:frame{stil} draw:name="Bild{len(self.bilder)}" text:anchor-type="as-char" svg:width="{_laenge(b)}" '
                f'svg:height="{_laenge(h)}">{bild}{beschr}</draw:frame>')

    def _freie_objekte(self, a: Absatz) -> list[str]:
        out = []
        for o in self.dok.objekte.values():
            if o.anker != a.id:
                continue
            ang = {k: v for k, v in o.daten.items() if k != "name"}
            ang.update({"b": o.breite, "h": o.hoehe, "bh": o.bezug_h, "xh": o.x, "bv": o.bezug_v, "yv": o.y, "art": o.art})
            if o.ausr_h:
                ang["ah"] = o.ausr_h
            if o.ausr_v:
                ang["av"] = o.ausr_v
            if o.umbruch == "hinter":
                ang["hinter"] = True
            nr = len(self.rahmen_stile) + 1
            stil = f"Fr{nr}"
            if o.art == "form":
                self.rahmen_stile.append(_frei_stil(stil, ang))
                form = _frei_form(ang, nr, stil)
                if form:
                    out.append(form)
                else:
                    self.rep.warn("Eine freie Form wurde nicht in die ODT-Datei übernommen.")
                continue
            roh = self.dok.ressourcen.get(o.ressource)
            img = _bild(roh) if roh else None
            if img is None:
                self.rep.warn("Ein Bild war nicht lesbar und fehlt in der ODT-Datei.")
                continue
            self.rahmen_stile.append(_frei_stil(stil, ang))
            out.append(_frei_rahmen(ang, img, nr, stil, self.bilder))
        return out

    def _note_modell(self, text: str, marke: str, f: dict) -> str | None:
        art, _, nummer = marke.partition(":")
        if art not in ("f", "e") or not nummer.isdigit():
            return None
        n = self.dok.noten.get(art, {}).get(int(nummer))
        if n is None:
            return None
        klass, ident = ("endnote", "etn") if art == "e" else ("footnote", "ftn")
        stil = self._text_stil_modell(f)
        zitat = _text_xml(text)
        zitat = f'<text:span text:style-name="{stil}">{zitat}</text:span>' if stil else zitat
        return (f'<text:note text:id="{ident}{nummer}" text:note-class="{klass}"><text:note-citation>{zitat}</text:note-citation>'
                f"<text:note-body><text:p>{_text_xml(n.text)}</text:p></text:note-body></text:note>")

    def absatz_modell(self, a: Absatz) -> str:
        inhalt = self._freie_objekte(a)
        for x in a.inhalte:
            if isinstance(x, InlineObjekt):
                inhalt.append(self._bild_modell(x))
                continue
            f = wirksames_zeichenformat(self.dok, a, x.format)
            if x.format.get("note"):
                note = self._note_modell(x.text, str(x.format["note"]), f)
                if note is not None:
                    inhalt.append(note)
                    continue
            t = _text_xml(x.text)
            stil = self._text_stil_modell(f)
            inhalt.append(f'<text:span text:style-name="{stil}">{t}</text:span>' if stil and t else t)
        stil = self._absatz_stil_modell(wirksames_absatzformat(self.dok, a))
        stufe = ueberschriftsebene(self.dok, a)
        if 1 <= stufe <= 10:
            return f'<text:h text:style-name="{stil}" text:outline-level="{stufe}">{"".join(inhalt)}</text:h>'
        return f'<text:p text:style-name="{stil}">{"".join(inhalt)}</text:p>'

    # ---- Tabellen ----
    def tabelle_modell(self, t: Tabelle) -> str:
        self.tabellen += 1
        spalten = len(t.zellen[0]) if t.zellen else 0
        gesamt = sum(t.spaltenbreiten) if t.spaltenbreiten and sum(t.spaltenbreiten) > 0 else 0.0
        kopf = []
        for c in range(spalten):
            anteil = (t.spaltenbreiten[c] / gesamt * 100) if gesamt and t.spaltenbreiten[c] > 0 else 100 / max(1, spalten)
            prozent = max(1, round(anteil))
            kopf.append(_odf("table-column", {"table:style-name": f"Sp{prozent}"}))
            self.absatz_stile.setdefault(("spalte", prozent), f"Sp{prozent}")
        zeilen = []
        for zeile in t.zellen:
            zellen = []
            for z in zeile:
                if z.verdeckt_von is not None:
                    zellen.append(_odf("covered-table-cell"))
                    continue
                attr = {"office:value-type": "string", "table:style-name": "Zelle"}
                if z.spaltenspanne > 1:
                    attr["table:number-columns-spanned"] = str(z.spaltenspanne)
                if z.zeilenspanne > 1:
                    attr["table:number-rows-spanned"] = str(z.zeilenspanne)
                zellen.append(_odf("table-cell", attr, self.bloecke_modell(z.bloecke) or "<text:p/>"))
            zeilen.append(_odf("table-row", {}, "".join(zellen)))
        return _odf("table", {"table:name": f"Tabelle{self.tabellen}", "table:style-name": "Tab"}, "".join(kopf + zeilen))

    # ---- Blöcke, Listen ----
    def bloecke_modell(self, bloecke: list) -> str:
        teile: list[str] = []
        offen: list[int] = []                                       # Listen-Id je offener Ebene, außen zuerst

        def schliessen(bis: int) -> None:
            while len(offen) > bis:
                offen.pop()
                teile.append("</text:list-item></text:list>")

        for b in bloecke:
            if isinstance(b, Absatz) and b.liste_id is not None and b.liste_id in self.dok.listen:
                tiefe = b.ebene + 1
                schliessen(min(len(offen), tiefe))
                if len(offen) == tiefe and offen[-1] != b.liste_id:
                    schliessen(tiefe - 1)
                if len(offen) == tiefe:
                    teile.append("</text:list-item><text:list-item>")
                while len(offen) < tiefe:
                    stil = f' text:style-name="{self._listen_stil_modell(b.liste_id)}"' if not offen else ""
                    teile.append(f"<text:list{stil}><text:list-item>")
                    offen.append(b.liste_id)
                teile.append(self.absatz_modell(b))
                continue
            schliessen(0)
            if isinstance(b, Tabelle):
                teile.append(self.tabelle_modell(b))
            elif isinstance(b, Rahmen):
                teile.append(self.bloecke_modell(b.bloecke))
            else:
                teile.append(self.absatz_modell(b))
        schliessen(0)
        return "".join(teile)

    def xml_modell(self) -> str:
        koerper = "".join(self.bloecke_modell(ab.bloecke) for ab in self.dok.abschnitte)
        return ('<?xml version="1.0" encoding="UTF-8"?>'
                f'<office:document-content {_NS} office:version="1.3">'
                f"<office:font-face-decls>{self._schriften_xml()}</office:font-face-decls>"
                f'<office:automatic-styles>{self._vorlagen_xml()}</office:automatic-styles>'
                f"<office:body><office:text>{koerper}</office:text></office:body></office:document-content>")


def odt_modell_daten(dok: Dokument, page, meta: dict | None = None) -> tuple[bytes, IOReport]:
    """Baut die ODT-Datei im Speicher. → (Inhalt, Bericht über nicht Übernommenes)."""
    rep = IOReport()
    inhalt = _InhaltModell(dok, rep)
    kf_bilder: dict[str, bytes] = {}
    stand = QTextDocument()                                            # trägt nur die Standardschrift für ``styles.xml``
    schrift = QFont(dok.standardformat.get("schrift") or "Liberation Sans")
    schrift.setPointSizeF(float(dok.standardformat.get("groesse_pt") or 11.0))
    stand.setDefaultFont(schrift)
    teile = {"content.xml": inhalt.xml_modell().encode("utf-8"), "styles.xml": _styles_xml(page, stand, kf_bilder).encode("utf-8"),
             "meta.xml": _meta_xml(meta or {}).encode("utf-8")}
    teile.update(inhalt.bilder)
    teile.update(kf_bilder)
    aus = io.BytesIO()
    with zipfile.ZipFile(aus, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), MIMETYPE, compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/manifest.xml", _manifest(list(teile)), compress_type=zipfile.ZIP_DEFLATED)
        for n, daten in teile.items():
            z.writestr(n, daten, compress_type=zipfile.ZIP_STORED if n.rsplit(".", 1)[-1].lower() in _BILDTYPEN else zipfile.ZIP_DEFLATED)
    _verluste_melden(rep, page, {"kommentare": bool(dok.kommentare)}, "ODT")
    return aus.getvalue(), rep
