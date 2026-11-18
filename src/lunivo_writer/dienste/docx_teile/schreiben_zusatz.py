"""DOCX schreiben: Kommentare, Quellenverzeichnis, Fuß- und Endnoten."""
from __future__ import annotations

from lunivo_writer.dienste.docx_teile.schreiben_gemeinsam import (  # noqa: F401
    WD_STYLE_TYPE,
    qn,
    Pt,
)

_BIB = "http://schemas.openxmlformats.org/officeDocument/2006/bibliography"
_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_QUELLENART = {"Buch": "Book", "Aufsatz": "JournalArticle", "Webseite": "InternetSite", "Bericht": "Report"}
# Fuß- und Endnoten: (Kürzel, Wurzel, Notenelement, Verweiselement, Beziehungsart, Inhaltstyp, Textvorlage, Verweisvorlage)
_NOTENARTEN = (
    ("f", "footnotes", "footnote", "footnoteRef", "footnotes",
     "application/vnd.openxmlformats-officedocument.wordprocessingml.footnotes+xml", "Footnote Text", "Footnote Reference"),
    ("e", "endnotes", "endnote", "endnoteRef", "endnotes",
     "application/vnd.openxmlformats-officedocument.wordprocessingml.endnotes+xml", "Endnote Text", "Endnote Reference"))


class ZusatzSchreiber:
    """DOCX schreiben: Kommentare, Quellenverzeichnis, Fuß- und Endnoten."""

    def _kommentare_schreiben(self) -> None:
        daten = self.meta.get("kommentare", {}) or {}
        gelost: list[str] = []                                   # Kennungen der als gelöst markierten Kommentare (für commentsExtended)
        for kid in sorted(self._komm_runs):
            runs = self._komm_runs[kid]
            k = daten.get(kid) or daten.get(str(kid)) or {}
            try:
                self._kommentar_schreiben(runs, k, gelost)
            except Exception as ex:
                self.report.warn(f"Ein Kommentar konnte nicht gespeichert werden: {ex}")
        if gelost:
            self._komm_erweitert(gelost)

    def _kommentar_schreiben(self, runs: list, k: dict, gelost: list) -> None:
        """Einen Kommentar über dem Bereich von erstem bis letztem Lauf anlegen; gelöste bekommen eine Absatzkennung (→ ``gelost``)."""
        c = self.d.add_comment(runs=[runs[0], runs[-1]] if len(runs) > 1 else runs[0], text=k.get("text", ""),
                               author=k.get("autor", "") or "Unbekannt", initials=k.get("initialen", "") or "")
        if k.get("datum"):
            c._comment_elm.set(qn("w:date"), k["datum"])
        if k.get("geloest"):
            pid = f"{0x20000000 + len(gelost) * 0x111:08X}"
            c.paragraphs[0]._p.set("{http://schemas.microsoft.com/office/word/2010/wordml}paraId", pid)
            gelost.append(pid)

    def _komm_erweitert(self, kennungen: list[str]) -> None:
        """Teil word/commentsExtended.xml: Die Kommentare mit diesen Absatzkennungen sind gelöst (w15:done)."""
        from docx.opc.packuri import PackURI
        from docx.opc.part import Part
        from lxml import etree
        W15 = "http://schemas.microsoft.com/office/word/2012/wordml"
        wurzel = etree.Element(f"{{{W15}}}commentsEx", nsmap={"w15": W15})
        for pid in kennungen:
            etree.SubElement(wurzel, f"{{{W15}}}commentEx", {f"{{{W15}}}paraId": pid, f"{{{W15}}}done": "1"})
        blob = etree.tostring(wurzel, xml_declaration=True, encoding="UTF-8", standalone=True)
        pkg = self.d.part.package
        teil = Part(PackURI("/word/commentsExtended.xml"), "application/vnd.openxmlformats-officedocument.wordprocessingml.commentsExtended+xml", blob, pkg)
        self.d.part.relate_to(teil, "http://schemas.microsoft.com/office/2011/relationships/commentsExtended")

    def _quellen_schreiben(self) -> None:
        quellen = self.meta.get("quellen") or []
        if not quellen:
            return
        import uuid
        from docx.opc.packuri import PackURI
        from docx.opc.part import Part
        from lxml import etree
        B = _BIB
        w = etree.Element(f"{{{B}}}Sources", nsmap={"b": B, None: B},
                          SelectedStyle="\\APA.XSL", StyleName=self.meta.get("zitierweise", "APA"), Version="6")
        for q in quellen:
            self._quelle_schreiben(w, q)
        blob = etree.tostring(w, xml_declaration=True, encoding="UTF-8", standalone=True)
        pkg = self.d.part.package
        vorhanden = {str(x.partname) for x in pkg.iter_parts()}
        n = 1
        while f"/customXml/item{n}.xml" in vorhanden or f"/customXml/itemProps{n}.xml" in vorhanden:
            n += 1
        item = Part(PackURI(f"/customXml/item{n}.xml"), "application/xml", blob, pkg)
        guid = "{" + str(uuid.uuid4()).upper() + "}"
        props = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                 f'<ds:datastoreItem ds:itemID="{guid}" xmlns:ds="http://schemas.openxmlformats.org/officeDocument/2006/customXml">'
                 f'<ds:schemaRefs><ds:schemaRef ds:uri="{B}"/></ds:schemaRefs></ds:datastoreItem>').encode("utf-8")
        pp = Part(PackURI(f"/customXml/itemProps{n}.xml"),
                  "application/vnd.openxmlformats-officedocument.customXmlProperties+xml", props, pkg)
        item.relate_to(pp, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXmlProps")
        self.d.part.relate_to(item, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/customXml")

    @staticmethod
    def _quelle_schreiben(w, q: dict) -> None:
        """Eine Quelle als b:Source (Tag, Art, Autorenliste, Titel, Jahr, Ort, Verlag, URL) an b:Sources hängen."""
        from lxml import etree
        B = _BIB
        e = etree.SubElement(w, f"{{{B}}}Source")

        def sub(n, v, parent=e):
            x = etree.SubElement(parent, f"{{{B}}}{n}")
            x.text = v or ""
            return x
        sub("Tag", q.get("tag", ""))
        sub("SourceType", _QUELLENART.get(q.get("typ"), "Misc"))
        a1 = etree.SubElement(etree.SubElement(e, f"{{{B}}}Author"), f"{{{B}}}Author")
        nl = etree.SubElement(a1, f"{{{B}}}NameList")
        for person in [x.strip() for x in (q.get("autor") or "").split(";") if x.strip()]:
            pe = etree.SubElement(nl, f"{{{B}}}Person")
            last, _, first = person.partition(",")
            sub("Last", last.strip(), pe)
            if first.strip():
                sub("First", first.strip(), pe)
        sub("Title", q.get("titel", "")); sub("Year", q.get("jahr", "")); sub("City", q.get("ort", ""))
        sub("Publisher", q.get("verlag", "")); sub("URL", q.get("url", ""))

    def _noten_schreiben(self) -> None:
        from docx.opc.packuri import PackURI
        from docx.opc.part import Part
        from lxml import etree
        for art, wurzel, tag, ref, rel, ct, stil_t, stil_r in _NOTENARTEN:
            if not self._noten[art]:
                continue
            self._notenstile(stil_t, stil_r)
            root = self._noten_xml(art, wurzel, tag, ref, stil_t, stil_r)
            blob = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            part = Part(PackURI(f"/word/{wurzel}.xml"), ct, blob, self.d.part.package)
            self.d.part.relate_to(part, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/" + rel)

    def _notenstile(self, stil_t: str, stil_r: str) -> None:
        """Absatzvorlage der Notentexte und Zeichenvorlage der Notenverweise anlegen, falls sie fehlen."""
        names = [s.name for s in self.d.styles]
        if stil_t not in names:
            st = self.d.styles.add_style(stil_t, WD_STYLE_TYPE.PARAGRAPH)
            st.base_style = self.d.styles["Normal"]
            st.font.size = Pt(10)
        if stil_r not in names:
            st = self.d.styles.add_style(stil_r, WD_STYLE_TYPE.CHARACTER)
            st.font.superscript = True

    def _noten_xml(self, art: str, wurzel: str, tag: str, ref: str, stil_t: str, stil_r: str):
        """Wurzel des Notenteils: zwei Trenner, danach jede Note mit Verweiszeichen in der ersten Zeile."""
        from lxml import etree
        root = etree.Element(f"{{{_W}}}{wurzel}", nsmap={"w": _W})
        for typ, nid in (("separator", -1), ("continuationSeparator", 0)):
            n = etree.SubElement(root, f"{{{_W}}}{tag}", {f"{{{_W}}}type": typ, f"{{{_W}}}id": str(nid)})
            r = etree.SubElement(etree.SubElement(n, f"{{{_W}}}p"), f"{{{_W}}}r")
            etree.SubElement(r, f"{{{_W}}}{typ}")
        for nid, text in self._noten[art]:
            n = etree.SubElement(root, f"{{{_W}}}{tag}", {f"{{{_W}}}id": str(nid)})
            for i, zeile in enumerate((text or "").split("\n")):
                self._noten_absatz(n, i, zeile, ref, stil_t, stil_r)
        return root

    @staticmethod
    def _noten_absatz(note, i: int, zeile: str, ref: str, stil_t: str, stil_r: str) -> None:
        """Eine Zeile der Note als Absatz; die erste beginnt mit dem Verweiszeichen (Zeichenvorlage ``stil_r``)."""
        from lxml import etree
        p = etree.SubElement(note, f"{{{_W}}}p")
        ppr = etree.SubElement(p, f"{{{_W}}}pPr")
        etree.SubElement(ppr, f"{{{_W}}}pStyle", {f"{{{_W}}}val": stil_t.replace(" ", "")})
        if i == 0:
            r = etree.SubElement(p, f"{{{_W}}}r")
            rpr = etree.SubElement(r, f"{{{_W}}}rPr")
            etree.SubElement(rpr, f"{{{_W}}}rStyle", {f"{{{_W}}}val": stil_r.replace(" ", "")})
            etree.SubElement(r, f"{{{_W}}}{ref}")
        r2 = etree.SubElement(p, f"{{{_W}}}r")
        t = etree.SubElement(r2, f"{{{_W}}}t")
        t.text = (" " if i == 0 else "") + zeile
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
