"""DOCX schreiben: Textfelder (``wps:wsp`` mit ``wps:txbx``/``w:txbxContent``), ihre Verknüpfungsketten und der Text darin.

Nutzt die Namensräume ``_WPS`` und ``_MC`` der Klasse ``_Writer`` (docx_schreiber.py); das Bild des Textfelds legt ``schreiben_objekte`` an."""
from __future__ import annotations

import json

from lxml import etree

_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
_XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"
_RAND_INNEN = {"lIns": "76200", "tIns": "76200", "rIns": "76200", "bIns": "76200"}              # Textrand im Feld (EMU)
_AUSRICHTUNG = {"mitte": "center", "rechts": "right", "block": "both", "verteilt": "distribute"}
_ZEICHEN_FLAGS = (("fett", "b"), ("kursiv", "i"), ("durch", "strike"))                         # Zeichenformat-Schlüssel → w:rPr-Element


def _w(eltern, name: str, **at):
    """Kindelement im DOCX-Namensraum anlegen, Attribute ebenfalls in diesem Namensraum."""
    e = etree.SubElement(eltern, f"{{{_W}}}{name}")
    for k, v in at.items():
        e.set(f"{{{_W}}}{k}", str(v))
    return e


class TextfeldSchreiber:
    """Fachliche Teilverantwortung des DOCX-Writers: Textfelder und verknüpfte Textfeldketten."""

    def _textfeld_ketten(self) -> dict:
        """{id des Textfelds: (Kettennummer, Stelle in der Kette)} — die Verknüpfungen aller Textfelder des Dokuments (``wps:linkedTxbx``)."""
        if getattr(self, "_tf_ketten", None) is None:
            self._tf_ketten = self._ketten_nummerieren(self._textfelder_sammeln())
        return self._tf_ketten

    def _textfelder_sammeln(self) -> dict:
        """Daten aller Textfelder des Dokuments nach ihrer id."""
        from lunivo_writer.editor.objekte import freie_bilder as FB
        felder = {}
        b = self.q.firstBlock()
        while b.isValid():
            for a in FB.aus_absatz(b.blockFormat()):
                d = a.get("daten") if a.get("art") == "textfeld" else None
                if d and d.get("id"):
                    felder[d["id"]] = d
            b = b.next()
        return felder

    @staticmethod
    def _ketten_nummerieren(felder: dict) -> dict:
        """Jede Kette (erstes Feld ohne Vorgänger, mit Nachfolger) bekommt eine Nummer; jedes Feld seine Stelle darin."""
        ketten, n = {}, 0
        for d in felder.values():
            if d.get("von") or not d.get("weiter"):
                continue
            n += 1
            seq, cur = 0, d
            while cur is not None and seq < 1000:
                ketten[cur["id"]] = (n, seq)
                cur = felder.get(cur.get("weiter")); seq += 1
        return ketten

    def _textfeld_xml(self, run, a: dict) -> None:
        """Das Bild des Textfelds wird zur Form mit Text (``wps:wsp`` mit ``wps:txbx``/``w:txbxContent``), in „Alternativer Inhalt“.
        Verknüpfte Felder tragen ``wps:linkedTxbx`` (``id`` = Kette, ``seq`` = Stelle); das erste Feld hält den ganzen Text. Die genauen Werte
        des Programms stehen im Titel des Objekts („lunivo:“), damit Lunivo es unverändert wieder lesen kann."""
        d = a.get("daten", {})
        for drawing in run._r.xpath(".//w:drawing"):
            self._textfeld_zeichnung(drawing, d)

    def _textfeld_zeichnung(self, drawing, d: dict) -> None:
        gd = drawing.xpath(".//a:graphicData")[0]
        sppr_pic = gd.xpath(".//pic:spPr")[0]
        wsp = etree.Element(f"{{{self._WPS}}}wsp", nsmap={"wps": self._WPS})
        etree.SubElement(wsp, f"{{{self._WPS}}}cNvSpPr").set("txBox", "1")
        sppr = etree.SubElement(wsp, f"{{{self._WPS}}}spPr")
        for k in list(sppr_pic):
            sppr.append(k)
        if sppr.find(f"{{{_A}}}prstGeom") is None:
            geom = etree.SubElement(sppr, f"{{{_A}}}prstGeom"); geom.set("prst", "rect"); etree.SubElement(geom, f"{{{_A}}}avLst")
        self._textfeld_text_oder_verknuepfung(wsp, d)
        bp = etree.SubElement(wsp, f"{{{self._WPS}}}bodyPr")
        innen = d.get("innen")
        for i, (k, v) in enumerate(_RAND_INNEN.items()):                  # eigener Innenabstand (Bildpunkte → EMU), sonst der Standard
            bp.set(k, str(int(round(float(innen[i]) * 9525))) if isinstance(innen, (list, tuple)) and len(innen) == 4 else v)
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

    def _textfeld_text_oder_verknuepfung(self, wsp, d: dict) -> None:
        """Folgefelder einer Kette verweisen nur (``wps:linkedTxbx``); alle anderen tragen den Text (``wps:txbx``)."""
        kette = self._textfeld_ketten().get(d.get("id"))
        if kette and d.get("von"):
            lt = etree.SubElement(wsp, f"{{{self._WPS}}}linkedTxbx"); lt.set("id", str(kette[0])); lt.set("seq", str(kette[1]))
            return
        tb = etree.SubElement(wsp, f"{{{self._WPS}}}txbx")
        if kette:
            tb.set("id", str(kette[0]))
        self._txbx_inhalt(etree.SubElement(tb, f"{{{_W}}}txbxContent"), d)

    def _txbx_inhalt(self, inhalt, d: dict) -> None:
        """Absätze und Läufe des Textfelds (Text mit Zeichenformaten) als ``w:p``/``w:r`` in ``w:txbxContent``."""
        from lunivo_writer.editor.objekte import frei_objekt as FO
        laeufe = d.get("laeufe") or [{"t": d.get("text", "")}]
        for zeile in FO._zeilen_laeufe(laeufe) or [[]]:
            p = _w(inhalt, "p")
            self._txbx_absatzformat(_w(p, "pPr"), d)
            for r in zeile:
                self._txbx_lauf(p, r, d, FO.ZEICHEN_SCHLUESSEL)

    @staticmethod
    def _txbx_absatzformat(ppr, d: dict) -> None:
        """Ausrichtung, Einzug und Zeilenabstand des Textfeld-Absatzes."""
        if d.get("ausr") in _AUSRICHTUNG:
            _w(ppr, "jc", val=_AUSRICHTUNG[d["ausr"]])
        if d.get("einzug"):
            _w(ppr, "ind", left=int(d["einzug"]) * 360)
        if d.get("zeilenabstand"):
            _w(ppr, "spacing", line=int(float(d["zeilenabstand"]) * 240), lineRule="auto")

    @classmethod
    def _txbx_lauf(cls, p, r: dict, d: dict, schluessel) -> None:
        """Ein Lauf mit Zeichenformat; fehlende Werte kommen aus den Daten des Textfelds."""
        e = {k: r.get(k, d.get(k)) for k in schluessel}
        wr = _w(p, "r")
        rpr = _w(wr, "rPr")
        cls._txbx_schrift(rpr, e, d)
        cls._txbx_hervorhebung(rpr, e)
        t = _w(wr, "t"); t.text = r["t"]; t.set(_XML_SPACE, "preserve")

    @staticmethod
    def _txbx_schrift(rpr, e: dict, d: dict) -> None:
        """Schriftart, Fett/Kursiv/Durchgestrichen, Farbe und Größe."""
        if e["schrift"]:
            _w(rpr, "rFonts", ascii=e["schrift"], hAnsi=e["schrift"])
        for key, tag in _ZEICHEN_FLAGS:
            if e[key]:
                _w(rpr, tag)
        col = e["fuell"] or d.get("farbe")
        if col and len(col.lstrip("#")) in (6, 8):
            _w(rpr, "color", val=col.lstrip("#")[-6:].upper())
        if e["pt"]:
            _w(rpr, "sz", val=int(float(e["pt"]) * 2))

    @staticmethod
    def _txbx_hervorhebung(rpr, e: dict) -> None:
        """Hervorhebung (Hintergrund), Unterstreichung, Hoch-/Tiefstellung."""
        if e["hervor"]:
            _w(rpr, "shd", val="clear", color="auto", fill=e["hervor"].lstrip("#")[-6:].upper())
        if e["unter"]:
            _w(rpr, "u", val="single")
        if e["hoch"] or e["tief"]:
            _w(rpr, "vertAlign", val="superscript" if e["hoch"] else "subscript")
