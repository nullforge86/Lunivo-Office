"""DOCX schreiben: Bilder, schwebende Objekte und ihre Verankerung (Textfelder: schreiben_textfelder.py)."""
from __future__ import annotations

import json

from lunivo_writer.editor.dokument.zusatz import P_DEKORATIV
from lunivo_writer.editor.objekte import bilddaten as BD

from lunivo_writer.dienste.docx_teile.schreiben_gemeinsam import (  # noqa: F401
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


NS_SVG = BD.NS_SVG                                                             # Word: Erweiterung a:blip/a:extLst für SVG-Bilder
SVG_ERWEITERUNG = "{96DAC541-7B7A-43D3-8B79-37D633B846F1}"
NS_DEKORATIV = "http://schemas.microsoft.com/office/drawing/2017/decorative"       # Word: Bild als dekorativ markiert (wp:docPr/a:extLst)
DEKORATIV_ERWEITERUNG = "{C183D7F6-B498-43B3-948B-1728B52AA6E4}"
# Bezugspunkt der Lage (frei positionierte Bilder; waagerecht wie senkrecht) → wp:positionH/V relativeFrom; Strichart des Rahmens → a:prstDash
_BEZUG = {"seite": "page", "rand": "margin"}
_RAND_STRICH = {"gepunktet": "sysDot", "fein_gestrichelt": "sysDash", "gestrichelt": "dash", "strichpunkt": "dashDot", "strichpunktpunkt": "lgDashDotDot"}
# Füllart → Methode, die das DrawingML-Füllelement baut
_FUELL_ARTEN = {"farbe": "_fuell_farbe", "verlauf": "_fuell_verlauf", "graduell": "_fuell_verlauf", "muster": "_fuell_muster"}


def _eins(wert) -> str:
    """Wahrheitswert als OOXML-Attribut „1“/„0“."""
    return "1" if wert else "0"


class ObjekteSchreiber:
    """DOCX schreiben: Bilder, schwebende Objekte und ihre Verankerung (Textfelder: schreiben_textfelder.py)."""

    def _bild_laden(self, imf) -> QImage | None:
        """Bild aus den Dokumentressourcen oder von der Platte; bei Misserfolg Hinweis im Bericht. Große Bilder je nach Option verkleinert."""
        name = imf.name()
        img = self.q.resource(QTextDocument.ImageResource, QUrl(name))
        if not isinstance(img, QImage) or img.isNull():
            img = QImage(name)
        if img.isNull():
            self.report.warn(f"Bild „{os.path.basename(name)}“ nicht lesbar und nicht gespeichert.")
            return None
        if self.meta.get("bilder_komprimieren") and max(img.width(), img.height()) > 1600:        # „Bilder nicht komprimieren“ ist aus
            img = img.scaled(1600, 1600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        return img

    def _image(self, imf, para, seite: str | None = None):
        img = self._bild_laden(imf)
        if img is None:
            return
        w = imf.width() or img.width()
        h = imf.height() or img.height()
        run = para.add_run()
        run.add_picture(io.BytesIO(BD.fuer_schreiben(img, BD.ORIGINAL_DOCX)[0]), width=Emu(int(w * EMU_PER_PX)), height=Emu(int(h * EMU_PER_PX)))
        alt = imf.property(STYLE_PROP + 1) if imf.hasProperty(STYLE_PROP + 1) else ""
        if imf.hasProperty(P_DEKORATIV) and imf.property(P_DEKORATIV):
            self._dekorativ_setzen(run)
        elif alt:
            self._docpr_setzen(run, "descr", str(alt))
        if imf.hasProperty(P_OBJEKT):                       # Daten zum Wiederbearbeiten (Form, Diagramm, SmartArt …) im Titel des Bildes
            self._docpr_setzen(run, "title", "lunivo:" + str(imf.property(P_OBJEKT)))
        if seite:
            self._verankern(run, "right" if seite == "rechts" else "left")
        self._svg_anhaengen(run, img)
        self._metafile_anhaengen(run, img)

    def _bildquelle_beziehung(self, run, q, speicher: str, muster: str):
        """Die Originalquelle eines Bildes im passenden DOCX-Part verknüpfen (Dokument, Kopf- oder Fußzeile)."""
        from docx.opc.constants import RELATIONSHIP_TYPE as RT
        from docx.opc.packuri import PackURI
        from docx.opc.part import Part
        quelle = self.__dict__.setdefault(speicher, {})
        eintrag = quelle.get(id(q))
        if eintrag is None:
            teil = Part(PackURI(muster.format(n=len(quelle) + 1, endung=q.endung)), q.medientyp, q.daten, self.d.part.package)
            eintrag = quelle[id(q)] = (teil, {})
        teil, beziehungen = eintrag
        part = run.part
        rid = beziehungen.get(id(part))
        if rid is None:
            rid = beziehungen[id(part)] = part.relate_to(teil, RT.IMAGE)
        return rid

    def _metafile_anhaengen(self, run, img: QImage) -> None:
        """EMF/WMF wie in Word: das Bild zeigt unmittelbar auf das Original (eigener Bildteil in word/media); die PNG-Rasterfassung, mit der
        python-docx das Bild angelegt hat, entfällt wieder."""
        q = BD.quelle_zu(img)
        if q is None or q.format not in BD.ORIGINAL_DOCX_METAFILE:
            return
        blips = run._r.xpath(".//pic:blipFill/a:blip")
        if not blips:
            return
        rid = self._bildquelle_beziehung(run, q, "_metafile_teile", "/word/media/metafile{n}.{endung}")
        alt = blips[0].get(qn("r:embed"))
        blips[0].set(qn("r:embed"), rid)
        for pic in run._r.xpath(".//pic:cNvPr"):                  # Bildname mit Endung der Datei
            pic.set("name", f"metafile.{q.endung}")
        run.part.drop_rel(alt)

    def _svg_anhaengen(self, run, img: QImage) -> None:
        """Wie Word: das Bild zeigt auf die PNG-Ersatzgrafik, ``a:blip/a:extLst`` verweist auf das SVG (eigener Teil in word/media)."""
        q = BD.quelle_zu(img)
        if q is None or q.format != "svg":
            return
        from lxml import etree
        blips = run._r.xpath(".//pic:blipFill/a:blip")
        if not blips:
            return
        rid = self._bildquelle_beziehung(run, q, "_svg_teile", "/word/media/svg{n}.{endung}")
        liste = etree.SubElement(blips[0], qn("a:extLst"))
        ext = etree.SubElement(liste, qn("a:ext"))
        ext.set("uri", SVG_ERWEITERUNG)
        etree.SubElement(ext, "{%s}svgBlip" % NS_SVG, nsmap={"asvg": NS_SVG}).set(qn("r:embed"), rid)

    @staticmethod
    def _dekorativ_setzen(run) -> None:
        """Wie Word: ``wp:docPr/a:extLst/a:ext/adec:decorative val="1"``; ein dekoratives Bild hat keine Beschreibung."""
        from lxml import etree
        for dp in run._r.xpath(".//wp:docPr"):
            liste = etree.SubElement(dp, qn("a:extLst"))
            ext = etree.SubElement(liste, qn("a:ext"))
            ext.set("uri", DEKORATIV_ERWEITERUNG)
            etree.SubElement(ext, "{%s}decorative" % NS_DEKORATIV, nsmap={"adec": NS_DEKORATIV}).set("val", "1")

    @staticmethod
    def _docpr_setzen(run, name: str, wert: str) -> None:
        """Attribut (descr, title) an wp:docPr des Bildes setzen."""
        for dp in run._r.xpath(".//wp:docPr"):
            dp.set(name, wert)

    def _frei_bild(self, para, a: dict, img: QImage) -> None:
        """Ein frei positioniertes Bild (siehe editor/objekte/freie_bilder.py) als wp:anchor ohne Umbruch in den Absatz schreiben."""
        if img is None or img.isNull():
            return
        b, h = float(a.get("b") or img.width()), float(a.get("h") or img.height())
        run = para.add_run()
        run.add_picture(io.BytesIO(BD.fuer_schreiben(img, BD.ORIGINAL_DOCX)[0]), width=Emu(int(b * EMU_PER_PX)), height=Emu(int(h * EMU_PER_PX)))
        if a.get("dekor"):
            self._dekorativ_setzen(run)
        elif a.get("alt"):
            self._docpr_setzen(run, "descr", str(a["alt"]))
        for inline in run._r.xpath(".//wp:inline"):
            self._frei_verankern(inline, a)
        for schritt in (self._bild_ellipse, self._bild_zuschnitt, self._bild_helligkeit, self._bild_maske_titel, self._bild_drehung,
                        self._bild_fuellung, self._bild_rand, self._bild_effekte):             # Reihenfolge = Reihenfolge der Elemente im XML
            schritt(run, a)
        self._svg_anhaengen(run, img)
        self._metafile_anhaengen(run, img)
        if a.get("art") == "textfeld":
            self._textfeld_xml(run, a)
        elif a.get("art") in ("form", "diagramm", "smartart", "piktogramm"):          # Bild mit den Parametern im Titel („lunivo:“), damit Lunivo es wieder lesen kann
            self._objekt_titel(run, a)

    @staticmethod
    def _anker_lage(tag: str, bezug: str, ausr, versatz):
        """wp:positionH / wp:positionV: Ausrichtung (wp:align) oder Versatz in EMU (wp:posOffset)."""
        el = OxmlElement(tag); el.set("relativeFrom", bezug)
        if ausr:
            al = OxmlElement("wp:align"); al.text = ausr; el.append(al)
        else:
            po = OxmlElement("wp:posOffset"); po.text = str(int(round(float(versatz or 0) * EMU_PER_PX))); el.append(po)
        return el

    def _frei_verankern(self, inline, a: dict) -> None:
        """wp:inline → wp:anchor ohne Umbruch (wp:wrapNone), Lage nach Bezug und Ausrichtung/Versatz."""
        from lunivo_writer.core.document.objekte import ImageObject
        obj = ImageObject.aus_angabe(a)                         # Lage und Umfluss kommen aus dem Objektmodell (``core/document/objekte.py``)
        anker = OxmlElement("wp:anchor")
        for k, v in (("distT", "0"), ("distB", "0"), ("distL", "0"), ("distR", "0"), ("simplePos", "0"),
                     ("relativeHeight", "251658240" if obj.wrap.behind else "251659264"), ("behindDoc", _eins(obj.wrap.behind)),
                     ("locked", _eins(obj.wrap.lock_anchor)), ("layoutInCell", "1"), ("allowOverlap", _eins(obj.wrap.overlap))):
            anker.set(k, v)
        sp = OxmlElement("wp:simplePos"); sp.set("x", "0"); sp.set("y", "0")
        ph = self._anker_lage("wp:positionH", _BEZUG.get(a.get("bh"), "column"), obj.anchor.h_align or None, a.get("xh"))
        pv = self._anker_lage("wp:positionV", _BEZUG.get(a.get("bv"), "paragraph"), obj.anchor.v_align or None, a.get("yv"))
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

    @staticmethod
    def _bild_ellipse(run, a: dict) -> None:
        if a.get("ellipse") or a.get("maske") == "Ellipse":
            for geom in run._r.xpath(".//a:prstGeom"):
                geom.set("prst", "ellipse")

    @staticmethod
    def _bild_zuschnitt(run, a: dict) -> None:
        """Zuschnitt als a:srcRect (Tausendstel Prozent)."""
        zu = a.get("zu")
        if not (zu and len(zu) == 4 and any(zu)):
            return
        for bf in run._r.xpath(".//pic:blipFill"):
            sr = OxmlElement("a:srcRect")
            for k, v in zip(("l", "t", "r", "b"), zu):
                if v:
                    sr.set(k, str(int(round(float(v) * 100000))))
            blip = bf.find(qn("a:blip"))
            (blip.addnext(sr) if blip is not None else bf.insert(0, sr))

    @staticmethod
    def _bild_helligkeit(run, a: dict) -> None:
        """Helligkeit/Kontrast als a:lum (Tausendstel Prozent)."""
        if not ((a.get("hell") or a.get("kontrast")) and not a.get("art")):
            return
        for blip in run._r.xpath(".//pic:blipFill/a:blip"):
            lum = OxmlElement("a:lum")
            for k, schl in (("bright", "hell"), ("contrast", "kontrast")):
                if a.get(schl):
                    lum.set(k, str(int(a[schl]) * 1000))
            blip.append(lum)

    @classmethod
    def _bild_maske_titel(cls, run, a: dict) -> None:
        """Zuschneideform: nur in Lunivo, im Titel gemerkt."""
        if a.get("maske") and not a.get("art"):
            cls._docpr_setzen(run, "title", "lunivo:" + json.dumps({"maske": a["maske"]}, ensure_ascii=False, separators=(",", ":")))

    @staticmethod
    def _bild_drehung(run, a: dict) -> None:
        if a.get("dreh") or a.get("flipH") or a.get("flipV"):
            for xf in run._r.xpath(".//pic:spPr/a:xfrm"):
                if a.get("dreh"):
                    xf.set("rot", str(int(round(float(a["dreh"]) * 60000))))
                if a.get("flipH"):
                    xf.set("flipH", "1")
                if a.get("flipV"):
                    xf.set("flipV", "1")

    @classmethod
    def _bild_fuellung(cls, run, a: dict) -> None:
        """Füllung des Bildes (Farbe, Verlauf, Muster); Textur und Bild bleiben im Programm."""
        f = a.get("fuell")
        if not (f and f.get("art") in _FUELL_ARTEN):
            return
        bauer = getattr(cls, _FUELL_ARTEN[f["art"]])
        for sppr in run._r.xpath(".//pic:spPr"):
            el = bauer(f)
            geom = sppr.find(qn("a:prstGeom"))
            (geom.addnext(el) if geom is not None else sppr.append(el))

    @staticmethod
    def _srgb(hexwert):
        c = OxmlElement("a:srgbClr"); c.set("val", str(hexwert).lstrip("#").upper()); return c

    @classmethod
    def _fuell_farbe(cls, f: dict):
        el = OxmlElement("a:solidFill"); el.append(cls._srgb(f["farbe"]))
        return el

    @classmethod
    def _fuell_muster(cls, f: dict):
        from lunivo_writer.editor.text import muster as MU
        el = OxmlElement("a:pattFill"); el.set("prst", MU.ooxml_von(f.get("key", "rein")))
        fg, bg = OxmlElement("a:fgClr"), OxmlElement("a:bgClr")
        fg.append(cls._srgb(f.get("farbe", Farbe.SCHWARZ))); bg.append(cls._srgb(f.get("grund") or Farbe.WEISS))
        el.append(fg); el.append(bg)
        return el

    @classmethod
    def _fuell_verlauf(cls, f: dict):
        """Verlauf von hell nach dunkel, von oben nach unten."""
        dunkel = f.get("dunkel", f["farbe"]); hell = f.get("hell", Farbe.WEISS)
        el = OxmlElement("a:gradFill"); lst = OxmlElement("a:gsLst")
        for pos, c in ((0, hell), (100000, dunkel)):
            gs = OxmlElement("a:gs"); gs.set("pos", str(pos)); gs.append(cls._srgb(c)); lst.append(gs)
        lin = OxmlElement("a:lin"); lin.set("ang", "5400000"); el.append(lst); el.append(lin)
        return el

    @staticmethod
    def _bild_rand(run, a: dict) -> None:
        """Rahmenlinie des Bildes (a:ln) mit Breite, Farbe und Strichart."""
        if not a.get("rand"):
            return
        for sppr in run._r.xpath(".//pic:spPr"):
            ln = OxmlElement("a:ln"); ln.set("w", str(int(round(float(a["rand"].get("b", 1)) * EMU_PER_PX))))
            fill = OxmlElement("a:solidFill"); clr = OxmlElement("a:srgbClr"); clr.set("val", str(a["rand"].get("farbe", Farbe.WEISS)).lstrip("#").upper())
            fill.append(clr); ln.append(fill)
            dash = _RAND_STRICH.get(a["rand"].get("art", "einfach"))
            if dash:
                pd = OxmlElement("a:prstDash"); pd.set("val", dash); ln.append(pd)
            sppr.append(ln)

    @classmethod
    def _bild_effekte(cls, run, a: dict) -> None:
        if a.get("fx"):
            for sppr in run._r.xpath(".//pic:spPr"):
                lst = cls._effekte_element(a["fx"])
                if len(lst):
                    sppr.append(lst)

    @classmethod
    def _objekt_titel(cls, run, a: dict) -> None:
        """Form, Diagramm, SmartArt, Piktogramm: Parameter im Titel („lunivo:“) und bei Diagrammen die Beschreibung."""
        for dp in run._r.xpath(".//wp:docPr"):
            daten = {k: v for k, v in a.get("daten", {}).items() if k != "teil"}                      # die Auswahl eines Diagrammteils wird nicht gespeichert
            dp.set("title", "lunivo:" + json.dumps({"art": a["art"], "daten": daten}, ensure_ascii=False, separators=(",", ":")))
            if a["art"] == "diagramm" and daten.get("alt_beschreibung") and not a.get("dekor"):                # dekorativ: keine Beschreibung
                dp.set("descr", str(daten["alt_beschreibung"]))

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
