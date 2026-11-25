"""ODT direkt aus dem Dokumentmodell (``core.document.Dokument``) schreiben — ohne ``QTextDocument`` und ohne Umwandlung ins bisherige Modell.

Dateiaufteilung einer ODT-Datei: ``content.xml`` (Absätze, Überschriften, Zeichenformat samt Formatvorlagen, Listen mit Ebenen, Tabellen mit
verbundenen Zellen, Fuß- und Endnoten, Bilder im Text mit Alternativtext, frei positionierte Bilder und einfache Formen), ``styles.xml`` (Seite, Kopf-/Fußzeile) und
``meta.xml``. Die Bausteine für Namensräume, Maße, Bilder, freie Rahmen und ``styles.xml`` kommen aus ``odt_basis`` und ``odt_seite_schreiben``."""
from __future__ import annotations

import io
import zipfile
from xml.sax.saxutils import escape

from lunivo_writer.core.dokument.dokument import Absatz, Dokument, InlineObjekt, Rahmen, Tabelle
from lunivo_writer.core.dokument.formatvorlagen import ueberschriftsebene, wirksames_absatzformat, wirksames_zeichenformat
from lunivo_writer.core.dokument.listen import ZEICHEN_DER_AUFZAEHLUNG
from lunivo_writer.dienste.odt.odt_basis import ATTR_QUOTE as _ATTR_QUOTE, BILDTYPEN as _BILDTYPEN, MIMETYPE, InhaltBasis as _Inhalt, _NS, _laenge, _odf, bild_elemente, bild_stil as _bild_stil, frei_form as _frei_form, frei_rahmen as _frei_rahmen, frei_stil as _frei_stil, manifest as _manifest, meta_xml as _meta_xml, text_xml as _text_xml
from lunivo_writer.core.dokument.bildformat import masse
from lunivo_writer.dienste.odt.odt_formen_schreiben import FORMEN as _ZEICHENARTEN, FormenSchreiber
from lunivo_writer.dienste.odt.odt_seite_schreiben import _styles_xml
from lunivo_writer.dienste.rtf.rtf_basis import verluste_melden
from lunivo_writer.core.dokument.bericht import IOReport

_AUSRICHTUNG = {"mitte": "center", "rechts": "end", "block": "justify"}
_ZAHLENART = {"dezimal": "1", "klein": "a", "gross": "A", "roem_klein": "i", "roem_gross": "I"}
_LAGE = {"hoch": "super", "tief": "sub"}


class _InhaltModell(_Inhalt):
    """``content.xml`` aus dem Modell: überschreibt die Teile von ``_Inhalt``, die am QTextDocument hängen."""

    def __init__(self, dok: Dokument, rep: IOReport):
        super().__init__(rep)
        self.dok = dok
        self.liste_stile: dict[int, str] = {}
        self.formen = FormenSchreiber(self.rahmen_stile, self.bilder, rep, dok.ressourcen)       # Formen, Textfelder, Gruppen und ihre Füllungen

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
        if x.art in _ZEICHENARTEN and not self.dok.ressourcen.get(x.ressource):
            return self.formen.element(x.art, x.breite, x.hoehe, x.daten, x.alt_text, None, len(self.rahmen_stile) + 1)
        if x.art == "roh":
            self.rep.warn(f"Ein Objekt ({x.daten.get('grund', 'unbekannte Art')}) lässt sich nur in DOCX erhalten und fehlt in der ODT-Datei.")
            return ""
        roh = self.dok.ressourcen.get(x.ressource)
        bild = bild_elemente(roh, f"bild{len(self.bilder) + 1}", self.bilder) if roh else None
        if bild is None:
            from lunivo_writer.core.dokument.bildformat import format_erkennen as _fe
            self.rep.warn(f"Ein Bild im Format {(_fe(roh) or 'unbekannt').upper()} lässt sich nicht nach ODT schreiben und fehlt in der ODT-Datei." if roh else "Ein Bild war nicht lesbar und fehlt in der ODT-Datei.")
            return ""
        groesse = masse(roh) or (64.0, 64.0)
        b, h = x.breite or groesse[0], x.hoehe or groesse[1]
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
            if o.art in _ZEICHENARTEN and not self.dok.ressourcen.get(o.ressource):
                lage = {"ah": o.ausr_h, "av": o.ausr_v, "bh": o.bezug_h, "bv": o.bezug_v}
                out.append(self.formen.element(o.art, o.breite, o.hoehe, o.daten, o.alt_text, lage, nr, o.x, o.y, o.umbruch == "hinter"))
                continue
            roh = self.dok.ressourcen.get(o.ressource)
            rahmen = _frei_rahmen(ang, roh, nr, stil, self.bilder) if roh else ""
            if not rahmen:
                self.rep.warn("Ein Bild war nicht lesbar oder hat ein Format, das ohne Qt nicht nach ODT geschrieben werden kann, und fehlt in der ODT-Datei.")
                continue
            self.rahmen_stile.append(_frei_stil(stil, ang))
            out.append(rahmen)
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

    @staticmethod
    def _kommentar_modell(k) -> str:
        absaetze = "".join(f"<text:p>{_text_xml(z)}</text:p>" for z in (k.text or "").split("\n"))
        autor = f"<dc:creator>{_text_xml(k.autor)}</dc:creator>" if k.autor else ""
        datum = f"<dc:date>{_text_xml(k.datum)}</dc:date>" if k.datum else ""
        return f'<office:annotation office:name="k{k.id}">{autor}{datum}{absaetze}</office:annotation>'

    def absatz_modell(self, a: Absatz) -> str:
        inhalt = self._freie_objekte(a)
        teile: list = []                                                          # Inhalte der Absätze, in die ein Absatz mit Seitenumbruch mitten im Text zerfällt
        offen = None                                                              # Id des gerade offenen Kommentarbereichs
        for x in a.inhalte:
            kid = x.format.get("kommentar") if not isinstance(x, InlineObjekt) else None
            if kid != offen:
                if offen is not None:
                    inhalt.append(f'<office:annotation-end office:name="k{offen}"/>')
                k = self.dok.kommentare.get(int(kid)) if kid is not None else None
                if k is not None:
                    inhalt.append(self._kommentar_modell(k))
                    offen = kid
                else:
                    offen = None
            if isinstance(x, InlineObjekt):
                inhalt.append(self._bild_modell(x))
                continue
            f = wirksames_zeichenformat(self.dok, a, x.format)
            if x.format.get("umbruch") in ("seite", "spalte"):                    # ODF kennt Seiten-/Spaltenumbrüche nur vor einem Absatz: hier beginnt ein neuer Absatz mit Umbruch davor
                if x.format["umbruch"] == "spalte":
                    self.rep.warn("Ein Spaltenumbruch mitten in einem Absatz wird in ODT als Seitenumbruch vor einem neuen Absatz geschrieben.")
                teile.append(inhalt)
                inhalt = []
                continue
            if x.format.get("note"):
                note = self._note_modell(x.text, str(x.format["note"]), f)
                if note is not None:
                    inhalt.append(note)
                    continue
            t = _text_xml(x.text)
            stil = self._text_stil_modell(f)
            inhalt.append(f'<text:span text:style-name="{stil}">{t}</text:span>' if stil and t else t)
        if offen is not None:
            inhalt.append(f'<office:annotation-end office:name="k{offen}"/>')
        teile.append(inhalt)
        format = wirksames_absatzformat(self.dok, a)
        stufe = ueberschriftsebene(self.dok, a)
        aus = []
        for n, teil in enumerate(teile):
            stil = self._absatz_stil_modell(format if n == 0 else {**format, "seitenumbruch_vor": True})
            if 1 <= stufe <= 10 and n == 0:
                aus.append(f'<text:h text:style-name="{stil}" text:outline-level="{stufe}">{"".join(teil)}</text:h>')
            else:
                aus.append(f'<text:p text:style-name="{stil}">{"".join(teil)}</text:p>')
        return "".join(aus)

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
        if len(self.dok.abschnitte) > 1:                              # mehrere Abschnitte: je ein ``text:section``, damit sie beim Lesen erhalten bleiben
            koerper = "".join(f'<text:section text:name="Abschnitt{n}">{self.bloecke_modell(ab.bloecke)}</text:section>'
                              for n, ab in enumerate(self.dok.abschnitte, 1))
        else:
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
    schrift = dok.standardformat.get("schrift") or "Liberation Sans"                     # Standardschrift für ``styles.xml``
    groesse = float(dok.standardformat.get("groesse_pt") or 11.0)
    teile = {"content.xml": inhalt.xml_modell().encode("utf-8"),
             "styles.xml": _styles_xml(page, schrift, groesse, kf_bilder, "".join(inhalt.formen.zeichen_vorlagen)).encode("utf-8"),
             "meta.xml": _meta_xml(meta or {}).encode("utf-8")}
    teile.update(inhalt.bilder)
    teile.update(kf_bilder)
    aus = io.BytesIO()
    with zipfile.ZipFile(aus, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), MIMETYPE, compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/manifest.xml", _manifest(list(teile)), compress_type=zipfile.ZIP_DEFLATED)
        for n, daten in teile.items():
            z.writestr(n, daten, compress_type=zipfile.ZIP_STORED if n.rsplit(".", 1)[-1].lower() in _BILDTYPEN else zipfile.ZIP_DEFLATED)
    verluste_melden(rep, page, "ODT")
    return aus.getvalue(), rep
