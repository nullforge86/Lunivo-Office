"""DOCX schreiben: Bilder, schwebende Objekte, Textfelder und ihre Verankerung."""
from __future__ import annotations

from lunivo_writer.services.docx_teile.schreiben_gemeinsam import (  # noqa: F401
    io,
    os,
    OxmlElement,
    qn,
    Emu,
    QBuffer,
    QIODevice,
    QUrl,
    Qt,
    QImage,
    QTextDocument,
    STYLE_PROP,
    Farbe,
    EMU_PER_PX,
    P_OBJEKT,
    muster,
)


class ObjekteSchreiber:
    """DOCX schreiben: Bilder, schwebende Objekte, Textfelder und ihre Verankerung."""

    def _image(self, imf, para, seite: str | None = None):
        name = imf.name()
        img = self.q.resource(QTextDocument.ImageResource, QUrl(name))
        if not isinstance(img, QImage) or img.isNull():
            img = QImage(name)
        if img.isNull():
            self.report.warn(f"Bild „{os.path.basename(name)}“ nicht lesbar und nicht gespeichert.")
            return
        if self.meta.get("bilder_komprimieren") and max(img.width(), img.height()) > 1600:        # „Bilder nicht komprimieren“ ist aus
            img = img.scaled(1600, 1600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        buf = QBuffer()
        buf.open(QIODevice.WriteOnly)
        img.save(buf, "PNG")
        data = bytes(buf.data())
        w = imf.width() or img.width()
        h = imf.height() or img.height()
        run = para.add_run()
        run.add_picture(io.BytesIO(data), width=Emu(int(w * EMU_PER_PX)), height=Emu(int(h * EMU_PER_PX)))
        alt = imf.property(STYLE_PROP + 1) if imf.hasProperty(STYLE_PROP + 1) else ""
        if alt:
            for dp in run._r.xpath(".//wp:docPr"):
                dp.set("descr", str(alt))
        if imf.hasProperty(P_OBJEKT):                       # Daten zum Wiederbearbeiten (Form, Diagramm, SmartArt …) im Titel des Bildes
            for dp in run._r.xpath(".//wp:docPr"):
                dp.set("title", "lunivo:" + str(imf.property(P_OBJEKT)))
        if seite:
            self._verankern(run, "right" if seite == "rechts" else "left")

    def _frei_bild(self, para, a: dict, img: QImage) -> None:
        """Ein frei positioniertes Bild (siehe editor/objekte/freie_bilder.py) als wp:anchor ohne Umbruch in den Absatz schreiben."""
        if img is None or img.isNull():
            return
        buf = QBuffer()
        buf.open(QIODevice.WriteOnly)
        img.save(buf, "PNG")
        b, h = float(a.get("b") or img.width()), float(a.get("h") or img.height())
        run = para.add_run()
        run.add_picture(io.BytesIO(bytes(buf.data())), width=Emu(int(b * EMU_PER_PX)), height=Emu(int(h * EMU_PER_PX)))
        if a.get("alt"):
            for dp in run._r.xpath(".//wp:docPr"):
                dp.set("descr", str(a["alt"]))
        for inline in run._r.xpath(".//wp:inline"):
            anker = OxmlElement("wp:anchor")
            for k, v in (("distT", "0"), ("distB", "0"), ("distL", "0"), ("distR", "0"), ("simplePos", "0"),
                         ("relativeHeight", "251658240" if a.get("hinter") else "251659264"), ("behindDoc", "1" if a.get("hinter") else "0"),
                         ("locked", "1" if a.get("verankern") else "0"), ("layoutInCell", "1"), ("allowOverlap", "1" if a.get("ueberlappen", True) else "0")):
                anker.set(k, v)
            sp = OxmlElement("wp:simplePos"); sp.set("x", "0"); sp.set("y", "0")

            def lage(tag, bezug, ausr, versatz):
                el = OxmlElement(tag); el.set("relativeFrom", bezug)
                if ausr:
                    al = OxmlElement("wp:align"); al.text = ausr; el.append(al)
                else:
                    po = OxmlElement("wp:posOffset"); po.text = str(int(round(float(versatz or 0) * EMU_PER_PX))); el.append(po)
                return el
            ph = lage("wp:positionH", {"seite": "page", "rand": "margin"}.get(a.get("bh"), "column"), a.get("ah"), a.get("xh"))
            pv = lage("wp:positionV", {"seite": "page", "rand": "margin"}.get(a.get("bv"), "paragraph"), a.get("av"), a.get("yv"))
            extent = inline.find(qn("wp:extent"))
            ee = OxmlElement("wp:effectExtent")
            for k in ("l", "t", "r", "b"):
                ee.set(k, "0")
            for e in [sp, ph, pv] + ([extent] if extent is not None else []) + [ee, OxmlElement("wp:wrapNone")]:
                anker.append(e)
            for k in list(inline):
                if k is not extent and k.tag != qn("wp:effectExtent"):
                    anker.append(k)
            inline.getparent().replace(inline, anker)
        if a.get("ellipse") or a.get("maske") == "Ellipse":
            for geom in run._r.xpath(".//a:prstGeom"):
                geom.set("prst", "ellipse")
        zu = a.get("zu")
        if zu and len(zu) == 4 and any(zu):                                                   # Zuschnitt als a:srcRect (Tausendstel Prozent)
            for bf in run._r.xpath(".//pic:blipFill"):
                sr = OxmlElement("a:srcRect")
                for k, v in zip(("l", "t", "r", "b"), zu):
                    if v:
                        sr.set(k, str(int(round(float(v) * 100000))))
                blip = bf.find(qn("a:blip"))
                (blip.addnext(sr) if blip is not None else bf.insert(0, sr))
        if (a.get("hell") or a.get("kontrast")) and not a.get("art"):                          # Helligkeit/Kontrast als a:lum (Tausendstel Prozent)
            for blip in run._r.xpath(".//pic:blipFill/a:blip"):
                lum = OxmlElement("a:lum")
                for k, schl in (("bright", "hell"), ("contrast", "kontrast")):
                    if a.get(schl):
                        lum.set(k, str(int(a[schl]) * 1000))
                blip.append(lum)
        if a.get("maske") and not a.get("art"):                                              # Zuschneideform: nur in Lunivo, im Titel gemerkt
            import json
            for dp in run._r.xpath(".//wp:docPr"):
                dp.set("title", "lunivo:" + json.dumps({"maske": a["maske"]}, ensure_ascii=False, separators=(",", ":")))
        if a.get("dreh"):
            for xf in run._r.xpath(".//pic:spPr/a:xfrm"):
                xf.set("rot", str(int(round(float(a["dreh"]) * 60000))))
        f = a.get("fuell")
        if f and f.get("art") in ("farbe", "verlauf", "graduell", "muster"):                     # Textur und Bild bleiben im Programm
            from lunivo_writer.editor.text import muster as MU
            for sppr in run._r.xpath(".//pic:spPr"):
                def farbe(hexwert):
                    c = OxmlElement("a:srgbClr"); c.set("val", str(hexwert).lstrip("#").upper()); return c
                if f["art"] == "farbe":
                    el = OxmlElement("a:solidFill"); el.append(farbe(f["farbe"]))
                elif f["art"] == "muster":
                    el = OxmlElement("a:pattFill"); el.set("prst", MU.ooxml_von(f.get("key", "rein")))
                    fg, bg = OxmlElement("a:fgClr"), OxmlElement("a:bgClr"); fg.append(farbe(f.get("farbe", Farbe.SCHWARZ))); bg.append(farbe(f.get("grund") or Farbe.WEISS))
                    el.append(fg); el.append(bg)
                else:                                                                           # Verlauf von hell nach dunkel, von oben nach unten
                    dunkel = f.get("dunkel", f["farbe"]); hell = f.get("hell", Farbe.WEISS)
                    el = OxmlElement("a:gradFill"); lst = OxmlElement("a:gsLst")
                    for pos, c in ((0, hell), (100000, dunkel)):
                        gs = OxmlElement("a:gs"); gs.set("pos", str(pos)); gs.append(farbe(c)); lst.append(gs)
                    lin = OxmlElement("a:lin"); lin.set("ang", "5400000"); el.append(lst); el.append(lin)
                geom = sppr.find(qn("a:prstGeom"))
                (geom.addnext(el) if geom is not None else sppr.append(el))
        if a.get("rand"):
            for sppr in run._r.xpath(".//pic:spPr"):
                ln = OxmlElement("a:ln"); ln.set("w", str(int(round(float(a["rand"].get("b", 1)) * EMU_PER_PX))))
                fill = OxmlElement("a:solidFill"); clr = OxmlElement("a:srgbClr"); clr.set("val", str(a["rand"].get("farbe", Farbe.WEISS)).lstrip("#").upper())
                fill.append(clr); ln.append(fill)
                dash = {"gepunktet": "sysDot", "fein_gestrichelt": "sysDash", "gestrichelt": "dash", "strichpunkt": "dashDot", "strichpunktpunkt": "lgDashDotDot"}.get(a["rand"].get("art", "einfach"))
                if dash:
                    pd = OxmlElement("a:prstDash"); pd.set("val", dash); ln.append(pd)
                sppr.append(ln)
        if a.get("fx"):
            for sppr in run._r.xpath(".//pic:spPr"):
                lst = self._effekte_element(a["fx"])
                if len(lst):
                    sppr.append(lst)
        if a.get("art") == "textfeld":
            self._textfeld_xml(run, a)
        elif a.get("art") in ("form", "diagramm", "smartart", "piktogramm"):          # Bild mit den Parametern im Titel („lunivo:“), damit Lunivo es wieder lesen kann
            import json
            for dp in run._r.xpath(".//wp:docPr"):
                daten = {k: v for k, v in a.get("daten", {}).items() if k != "teil"}                      # die Auswahl eines Diagrammteils wird nicht gespeichert
                dp.set("title", "lunivo:" + json.dumps({"art": a["art"], "daten": daten}, ensure_ascii=False, separators=(",", ":")))
                if a["art"] == "diagramm" and daten.get("alt_beschreibung"):
                    dp.set("descr", str(daten["alt_beschreibung"]))

    def _textfeld_ketten(self) -> dict:
        """{id des Textfelds: (Kettennummer, Stelle in der Kette)} — die Verknüpfungen aller Textfelder des Dokuments (``wps:linkedTxbx``)."""
        if getattr(self, "_tf_ketten", None) is None:
            from lunivo_writer.editor.objekte import freie_bilder as FB
            felder = {}
            b = self.q.firstBlock()
            while b.isValid():
                for a in FB.aus_absatz(b.blockFormat()):
                    d = a.get("daten") if a.get("art") == "textfeld" else None
                    if d and d.get("id"):
                        felder[d["id"]] = d
                b = b.next()
            self._tf_ketten, n = {}, 0
            for i, d in felder.items():
                if d.get("von") or not d.get("weiter"):
                    continue
                n += 1
                seq, cur = 0, d
                while cur is not None and seq < 1000:
                    self._tf_ketten[cur["id"]] = (n, seq)
                    cur = felder.get(cur.get("weiter")); seq += 1
        return self._tf_ketten

    def _textfeld_xml(self, run, a: dict) -> None:
        """Das Bild des Textfelds wird zur Form mit Text (``wps:wsp`` mit ``wps:txbx``/``w:txbxContent``), in „Alternativer Inhalt“.
        Verknüpfte Felder tragen ``wps:linkedTxbx`` (``id`` = Kette, ``seq`` = Stelle); das erste Feld hält den ganzen Text. Die genauen Werte
        des Programms stehen im Titel des Objekts („lunivo:“), damit Lunivo es unverändert wieder lesen kann."""
        import json
        from lxml import etree
        W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        A = "http://schemas.openxmlformats.org/drawingml/2006/main"
        d = a.get("daten", {})
        for drawing in run._r.xpath(".//w:drawing"):
            gd = drawing.xpath(".//a:graphicData")[0]
            sppr_pic = gd.xpath(".//pic:spPr")[0]
            wsp = etree.Element(f"{{{self._WPS}}}wsp", nsmap={"wps": self._WPS})
            etree.SubElement(wsp, f"{{{self._WPS}}}cNvSpPr").set("txBox", "1")
            sppr = etree.SubElement(wsp, f"{{{self._WPS}}}spPr")
            for k in list(sppr_pic):
                sppr.append(k)
            if sppr.find(f"{{{A}}}prstGeom") is None:
                geom = etree.SubElement(sppr, f"{{{A}}}prstGeom"); geom.set("prst", "rect"); etree.SubElement(geom, f"{{{A}}}avLst")
            kette = self._textfeld_ketten().get(d.get("id"))
            if kette and (d.get("von") or d.get("weiter")) and d.get("von"):
                lt = etree.SubElement(wsp, f"{{{self._WPS}}}linkedTxbx"); lt.set("id", str(kette[0])); lt.set("seq", str(kette[1]))
            else:
                tb = etree.SubElement(wsp, f"{{{self._WPS}}}txbx")
                if kette:
                    tb.set("id", str(kette[0]))
                self._txbx_inhalt(etree.SubElement(tb, f"{{{W}}}txbxContent"), d)
            bp = etree.SubElement(wsp, f"{{{self._WPS}}}bodyPr")
            for k, v in (("lIns", "76200"), ("tIns", "76200"), ("rIns", "76200"), ("bIns", "76200")):
                bp.set(k, v)
            gd.set("uri", self._WPS)
            for k in list(gd):
                gd.remove(k)
            gd.append(wsp)
            for dp in drawing.xpath(".//wp:docPr"):
                dp.set("title", "lunivo:" + json.dumps({"art": "textfeld", "daten": d}, ensure_ascii=False, separators=(",", ":")))
            ac = etree.Element(f"{{{self._MC}}}AlternateContent", nsmap={"mc": self._MC, "wps": self._WPS})
            ch = etree.SubElement(ac, f"{{{self._MC}}}Choice"); ch.set("Requires", "wps")
            drawing.getparent().replace(drawing, ac)
            ch.append(drawing)

    def _txbx_inhalt(self, inhalt, d: dict) -> None:
        """Absätze und Läufe des Textfelds (Text mit Zeichenformaten) als ``w:p``/``w:r`` in ``w:txbxContent``."""
        from lxml import etree
        from lunivo_writer.editor.objekte import frei_objekt as FO
        W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

        def el(eltern, name, **at):
            e = etree.SubElement(eltern, f"{{{W}}}{name}")
            for k, v in at.items():
                e.set(f"{{{W}}}{k}", str(v))
            return e
        laeufe = d.get("laeufe") or [{"t": d.get("text", "")}]
        for zeile in FO._zeilen_laeufe(laeufe) or [[]]:
            p = el(inhalt, "p")
            ppr = el(p, "pPr")
            if d.get("ausr") in ("mitte", "rechts", "block", "verteilt"):
                el(ppr, "jc", val={"mitte": "center", "rechts": "right", "block": "both", "verteilt": "distribute"}[d["ausr"]])
            if d.get("einzug"):
                el(ppr, "ind", left=int(d["einzug"]) * 360)
            if d.get("zeilenabstand"):
                el(ppr, "spacing", line=int(float(d["zeilenabstand"]) * 240), lineRule="auto")
            for r in zeile:
                e = {k: r.get(k, d.get(k)) for k in FO.ZEICHEN_SCHLUESSEL}
                wr = el(p, "r"); rpr = el(wr, "rPr")
                if e["schrift"]:
                    el(rpr, "rFonts", ascii=e["schrift"], hAnsi=e["schrift"])
                if e["fett"]:
                    el(rpr, "b")
                if e["kursiv"]:
                    el(rpr, "i")
                if e["durch"]:
                    el(rpr, "strike")
                col = e["fuell"] or d.get("farbe")
                if col and len(col.lstrip("#")) in (6, 8):
                    el(rpr, "color", val=col.lstrip("#")[-6:].upper())
                if e["pt"]:
                    el(rpr, "sz", val=int(float(e["pt"]) * 2))
                if e["hervor"]:
                    el(rpr, "shd", val="clear", color="auto", fill=e["hervor"].lstrip("#")[-6:].upper())
                if e["unter"]:
                    el(rpr, "u", val="single")
                if e["hoch"] or e["tief"]:
                    el(rpr, "vertAlign", val="superscript" if e["hoch"] else "subscript")
                t = el(wr, "t"); t.text = r["t"]; t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")

    @staticmethod
    def _effekte_element(fx: dict):
        """Schatten, Leuchten, Spiegelung und weiche Kanten als ``a:effectLst`` (Längen in Punkt → EMU, Winkel in 1/60000 Grad)."""
        pt = 12700

        def farbe(el, hexfarbe: str, transparenz) -> None:
            c = OxmlElement("a:srgbClr"); c.set("val", str(hexfarbe or Farbe.SCHWARZ).lstrip("#").upper())
            al = OxmlElement("a:alpha"); al.set("val", str(int(round((100 - float(transparenz)) * 1000)))); c.append(al); el.append(c)
        lst = OxmlElement("a:effectLst")
        if fx.get("leuchten"):
            g = fx["leuchten"]; el = OxmlElement("a:glow"); el.set("rad", str(int(float(g.get("groesse", 8)) * pt)))
            farbe(el, g.get("farbe", Farbe.BLAU), g.get("transparenz", 60)); lst.append(el)
        if fx.get("schatten"):
            sc = fx["schatten"]; el = OxmlElement("a:outerShdw")
            el.set("blurRad", str(int(float(sc.get("weich", 4)) * pt))); el.set("dist", str(int(float(sc.get("abstand", 4)) * pt)))
            el.set("dir", str(int(float(sc.get("winkel", 45)) * 60000))); el.set("algn", "ctr"); el.set("rotWithShape", "0")
            farbe(el, sc.get("farbe", Farbe.SCHWARZ), sc.get("transparenz", 60)); lst.append(el)
        if fx.get("reflektion"):
            r = fx["reflektion"]; el = OxmlElement("a:reflection")
            el.set("blurRad", str(int(float(r.get("weich", 0.5)) * pt))); el.set("stA", str(int(round((100 - float(r.get("transparenz", 50))) * 1000))))
            el.set("endA", "0"); el.set("endPos", str(int(float(r.get("groesse", 50)) * 1000))); el.set("dist", str(int(float(r.get("abstand", 0)) * pt)))
            el.set("dir", "5400000"); el.set("sy", "-100000"); el.set("algn", "bl"); el.set("rotWithShape", "0"); lst.append(el)
        if fx.get("weich"):
            el = OxmlElement("a:softEdge"); el.set("rad", str(int(float(fx["weich"].get("radius", 6)) * pt))); lst.append(el)
        return lst

    def _verankern(self, run, ausrichtung: str) -> None:
        """Macht aus dem Bild im Text (wp:inline) ein umflossenes Bild (wp:anchor, Umbruch „Quadrat“, links/rechts)."""
        for inline in run._r.xpath(".//wp:inline"):
            anker = OxmlElement("wp:anchor")
            for k, v in (("distT", "0"), ("distB", "0"), ("distL", "114300"), ("distR", "114300"), ("simplePos", "0"),
                         ("relativeHeight", "251658240"), ("behindDoc", "0"), ("locked", "0"), ("layoutInCell", "1"),
                         ("allowOverlap", "0")):
                anker.set(k, v)
            sp = OxmlElement("wp:simplePos"); sp.set("x", "0"); sp.set("y", "0")
            ph = OxmlElement("wp:positionH"); ph.set("relativeFrom", "margin")
            al = OxmlElement("wp:align"); al.text = ausrichtung; ph.append(al)
            pv = OxmlElement("wp:positionV"); pv.set("relativeFrom", "paragraph")
            po = OxmlElement("wp:posOffset"); po.text = "0"; pv.append(po)
            ee = OxmlElement("wp:effectExtent")
            for k in ("l", "t", "r", "b"):
                ee.set(k, "0")
            wr = OxmlElement("wp:wrapSquare"); wr.set("wrapText", "bothSides")
            extent = inline.find(qn("wp:extent"))
            vorn = [sp, ph, pv] + ([extent] if extent is not None else [])
            for e in vorn + [ee, wr]:
                anker.append(e)
            for k in list(inline):
                if k is not extent and k.tag != qn("wp:effectExtent"):
                    anker.append(k)
            inline.getparent().replace(inline, anker)
