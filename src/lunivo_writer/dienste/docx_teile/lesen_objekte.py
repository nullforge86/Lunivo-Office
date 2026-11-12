"""DOCX lesen: Bilder und schwebende Objekte (Textfelder: lesen_textfelder.py)."""
from __future__ import annotations

from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import (  # noqa: F401
    docx,
    qn,
    QUrl,
    QImage,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextImageFormat,
    Farbe,
    STYLE_PROP,
    P_OBJEKT,
    P_DEKORATIV,
    _NS,
    _xp,
    _emu_to_px,
)


# Strichart der Umrandung DOCX → Programm; Bezugspunkt der Lage DOCX → Programm (waagerecht/senkrecht)
_RAND_ART = {"sysDot": "gepunktet", "dot": "gepunktet", "sysDash": "fein_gestrichelt", "dash": "gestrichelt", "lgDash": "gestrichelt",
             "dashDot": "strichpunkt", "lgDashDot": "strichpunkt", "lgDashDotDot": "strichpunktpunkt",
             "sysDashDot": "strichpunkt", "sysDashDotDot": "strichpunktpunkt"}
_BEZUG_H = {"page": "seite", "margin": "rand", "leftMargin": "rand", "insideMargin": "rand", "outsideMargin": "rand", "rightMargin": "rand"}
_BEZUG_V = {"page": "seite", "margin": "rand", "topMargin": "rand", "insideMargin": "rand", "outsideMargin": "rand", "bottomMargin": "rand"}
_PT = 12700.0
_WPG = "{http://schemas.microsoft.com/office/word/2010/wordprocessingGroup}"  # Gruppen-Namensraum (nicht in python-docx enthalten)
_WPS = "{http://schemas.microsoft.com/office/word/2010/wordprocessingShape}"    # Formen-Namensraum (nicht in python-docx enthalten)


def _fx_farbe(el):
    """(Farbe, Transparenz in Prozent) eines Effekts."""
    from lunivo_writer.editor.objekte.freie_bilder import farbe_aus_element
    c = _xp(el, "a:srgbClr")
    if not c:
        return Farbe.SCHWARZ, 0
    al = _xp(c[0], "a:alpha/@val")
    return farbe_aus_element(c[0], _NS).name(), 100 - (int(al[0]) / 1000 if al else 100)


def _fx_leuchten(el) -> dict:
    f, t = _fx_farbe(el)
    return {"farbe": f, "groesse": int(el.get("rad") or 0) / _PT, "transparenz": t}


def _fx_schatten(el) -> dict:
    f, t = _fx_farbe(el)
    return {"farbe": f, "transparenz": t, "groesse": 100, "weich": int(el.get("blurRad") or 0) / _PT,
            "abstand": int(el.get("dist") or 0) / _PT, "winkel": int(el.get("dir") or 0) / 60000}


def _fx_reflektion(el) -> dict:
    return {"groesse": int(el.get("endPos") or 50000) / 1000, "transparenz": 100 - int(el.get("stA") or 50000) / 1000,
            "weich": int(el.get("blurRad") or 0) / _PT, "abstand": int(el.get("dist") or 0) / _PT}


def _fx_weich(el) -> dict:
    return {"radius": int(el.get("rad") or 0) / _PT}


# Effekt: (Schlüssel im Programm, Element in a:effectLst, Leser) — in dieser Reihenfolge
_EFFEKTE = (("leuchten", "glow", _fx_leuchten), ("schatten", "outerShdw", _fx_schatten),
            ("reflektion", "reflection", _fx_reflektion), ("weich", "softEdge", _fx_weich))


# Geometrie in DOCX (a:prstGeom/@prst) → Name im Formkatalog des Programms (editor/objekte/formen_katalog.py)
_FORM_AUS_DOCX = {"rect": "Rechteck", "roundRect": "Abgerundetes Rechteck", "ellipse": "Ellipse", "triangle": "Dreieck",
                  "rtTriangle": "Rechtwinkliges Dreieck", "parallelogram": "Parallelogramm", "trapezoid": "Trapez", "diamond": "Raute",
                  "pentagon": "Fünfeck", "hexagon": "Sechseck", "octagon": "Achteck", "decagon": "Zehneck", "dodecagon": "Zwölfeck",
                  "cross": "Kreuz", "heart": "Herz", "teardrop": "Tropfen", "moon": "Mond", "cloud": "Wolke", "lightningBolt": "Blitz", "star5": "Stern mit 5 Zacken",
                  "star6": "Stern mit 6 Zacken", "star8": "Stern mit 8 Zacken", "star10": "Stern mit 10 Zacken", "star12": "Stern mit 12 Zacken",
                  "star16": "Stern mit 16 Zacken", "star24": "Stern mit 24 Zacken", "star32": "Stern mit 32 Zacken", "rightArrow": "Pfeil nach rechts",
                  "leftArrow": "Pfeil nach links", "upArrow": "Pfeil nach oben", "downArrow": "Pfeil nach unten", "wave": "Welle",
                  "flowChartProcess": "Prozess", "flowChartDecision": "Verzweigung"}


class ObjekteMixin:
    """DOCX lesen: Bilder und schwebende Objekte (Textfelder: lesen_textfelder.py)."""

    @staticmethod
    def _effekte_lesen(drawing) -> dict:
        """``a:effectLst`` am Bild → ``fx`` (Schatten, Leuchten, Spiegelung, weiche Kanten) in den Werten des Programms."""
        fx: dict = {}
        try:
            for schluessel, tag, bauer in _EFFEKTE:
                for el in _xp(drawing, f".//pic:spPr/a:effectLst/a:{tag}"):
                    fx[schluessel] = bauer(el)
        except Exception:                                              # noqa: BLE001 — ein ungewöhnlicher Effekt darf das Laden nicht verhindern
            return {}
        return fx

    def _frei(self, drawing, teil=None, inline_ok: bool = False):
        """Ein Bild, das frei auf dem Blatt liegt (wp:anchor ohne Textumbruch) → (Angabe, QImage); ``False``, wenn es nicht darstellbar ist
        (Vektorbild); ``None``, wenn es kein solches Bild ist (steht im Text oder umflossen). Siehe editor/objekte/freie_bilder.py."""
        a = self._frei_anker(drawing, inline_ok)
        textfeld = _xp(drawing, ".//wps:wsp[wps:txbx or wps:linkedTxbx]")             # Textfeld (auch verknüpft), kein Bild
        blips = drawing.xpath(".//a:blip")
        form = None if (blips or textfeld) else self._form_aus_docx(drawing)
        if a is None and (form is not None or textfeld) and drawing.xpath("wp:anchor"):
            a = drawing.xpath("wp:anchor")[0]           # Form oder Textfeld mit Textumbruch: frei auf dem Blatt, der Text umfließt sie nicht
        if a is None:
            return None
        if not blips and not textfeld and form is None:
            return None
        img = None
        if form is not None:
            from lunivo_writer.editor.objekte import frei_objekt as FO
            b, h = self._frei_groesse(a, None)
            angabe = {"b": b, "h": h, "hinter": (a.get("behindDoc") or "0").lower() in ("1", "true"), "bh": "spalte", "bv": "absatz",
                      "xh": 0.0, "yv": 0.0, "ah": "", "av": "", "ellipse": False}
            self._frei_lage(angabe, a)
            angabe["art"], angabe["daten"] = "form", form
            if self._dekorativ(drawing):                                   # Form als dekorativ markiert (Word: wp:docPr)
                angabe["dekor"] = True
            return angabe, FO.zeichnen("form", form, b, h)
        if not textfeld:
            img = self._frei_bild_laden(blips[0], teil)
            if img is None:
                return False
        img = self._duoton_anwenden(drawing, img)
        b, h = self._frei_groesse(a, img)
        tf_daten = None
        if textfeld:
            from lunivo_writer.editor.objekte import frei_objekt as FO
            tf_daten = self._textfeld_daten(drawing, textfeld[0])
            img = FO.textfeld_zeichnen(tf_daten, b, h)
        angabe = {"b": b, "h": h, "hinter": (a.get("behindDoc") or "0").lower() in ("1", "true"), "bh": "spalte", "bv": "absatz",
                  "xh": 0.0, "yv": 0.0, "ah": "", "av": "",
                  "ellipse": bool(_xp(drawing, ".//a:prstGeom[@prst='ellipse']"))}
        self._frei_darstellung(angabe, drawing, tf_daten)                  # Reihenfolge der Schlüssel bleibt wie im gespeicherten Absatz
        self._frei_zuschnitt(angabe, drawing)
        self._frei_helligkeit(angabe, drawing)
        self._frei_fuellung(angabe, drawing)
        self._frei_drehung(angabe, drawing)
        self._frei_lage(angabe, a)
        return angabe, img

    @staticmethod
    def _frei_anker(drawing, inline_ok: bool):
        """Anker des Bildes ohne Textumbruch (sonst None: das Bild steht im Text oder wird umflossen)."""
        anker = drawing.xpath("wp:anchor") or (drawing.xpath("wp:inline") if inline_ok else [])
        if not anker or _xp(anker[0], "wp:wrapSquare | wp:wrapTight | wp:wrapThrough | wp:wrapTopAndBottom"):
            return None
        return anker[0]

    def _frei_bild_laden(self, blip, teil):
        """Bilddaten des Verweises laden; None (mit Hinweis im Bericht), wenn sie fehlen oder nicht lesbar sind (zum Beispiel Vektorbild)."""
        rid = blip.get(qn("r:embed"))
        try:
            blob = (teil or self.d.part).related_parts[rid].blob
        except KeyError:
            self.report.warn("Ein Bild fehlt im Dokument; an seiner Stelle steht ein Platzhalter.")
            return self._bild_platzhalter(blip)
        from lunivo_writer.dienste.vektor_bilder import bild_lesen
        img = self._svg_ergaenzen(blip, teil, bild_lesen(blob), blob)
        if img.isNull():
            self.report.warn("Ein Bild hat ein nicht lesbares Format (zum Beispiel eine Vektorzeichnung); an seiner Stelle steht ein Platzhalter.")
            return self._bild_platzhalter(blip)
        return img

    @staticmethod
    def _bild_platzhalter(blip):
        """Platzhalterbild in der Größe, die das Dokument für das Bild vorsieht (``wp:extent``), sonst 100 × 50."""
        from lunivo_writer.editor.objekte import bilddaten as BD
        from lunivo_writer.editor.objekte.freie_bilder import emu_zu_px
        ext = blip.xpath("ancestor::wp:inline/wp:extent | ancestor::wp:anchor/wp:extent")
        b, h = (emu_zu_px(ext[0].get("cx")), emu_zu_px(ext[0].get("cy"))) if ext else (100.0, 50.0)
        return BD.platzhalter(b, h)

    def _svg_ergaenzen(self, blip, teil, img, png_blob: bytes):
        """Wie Word: hat das Bild ``a:blip/a:extLst/asvg:svgBlip``, ist das SVG die Quelle und die PNG-Ersatzgrafik nur die Rasterfassung."""
        from lunivo_writer.editor.objekte import bilddaten as BD
        for el in blip.iter("{%s}svgBlip" % BD.NS_SVG):
            try:
                svg = (teil or self.d.part).related_parts[el.get(qn("r:embed"))].blob
            except KeyError:
                break
            if BD.format_erkennen(svg) == "svg":
                neu = BD.bild_aus_svg(svg, png_blob)
                if not neu.isNull():
                    return neu
            break
        return img

    @staticmethod
    def _duoton_anwenden(drawing, img):
        """Zweifarbig umgefärbt (zum Beispiel grau statt grün)."""
        duo = _xp(drawing, ".//a:blip/a:duotone")
        if duo and len(duo[0]) >= 2:
            from lunivo_writer.editor.objekte.freie_bilder import duoton, farbe_aus_element
            try:
                img = duoton(img, farbe_aus_element(duo[0][0], _NS), farbe_aus_element(duo[0][1], _NS))
            except Exception:                                          # noqa: BLE001 — ein ungewöhnlicher Effekt darf das Laden nicht verhindern
                pass
        return img

    @staticmethod
    def _frei_groesse(anker, img) -> tuple[float, float]:
        """Breite und Höhe in Bildpunkten aus wp:extent, sonst aus dem Bild (oder 100 × 50)."""
        from lunivo_writer.editor.objekte.freie_bilder import emu_zu_px
        ext = _xp(anker, "wp:extent")
        b = emu_zu_px(ext[0].get("cx")) if ext else float(img.width() if img is not None else 100)
        h = emu_zu_px(ext[0].get("cy")) if ext else float(img.height() if img is not None else 50)
        return b, h

    @staticmethod
    def _frei_rand(drawing):
        """Umrandung der Form (der weiße Ring um ein Foto) → {b, farbe, art} oder None."""
        from lunivo_writer.editor.objekte.freie_bilder import emu_zu_px, farbe_aus_element
        for ln in _xp(drawing, ".//a:ln[a:solidFill]"):
            try:
                f = farbe_aus_element(_xp(ln, "a:solidFill/*")[0], _NS)
                dash = _xp(ln, "a:prstDash/@val")
                return {"b": max(0.5, emu_zu_px(ln.get("w") or 9525)), "farbe": f.name(), "art": _RAND_ART.get(dash[0] if dash else "", "einfach")}
            except Exception:                                              # noqa: BLE001
                return None
        return None

    def _frei_darstellung(self, angabe: dict, drawing, tf_daten) -> None:
        """Umrandung, Effekte, Beschreibung, Art (Textfeld, Form, Diagramm …) oder Zuschneideform ergänzen."""
        rand = self._frei_rand(drawing)
        if rand:
            angabe["rand"] = rand
        fx = self._effekte_lesen(drawing)
        if fx:
            angabe["fx"] = fx
        beschr = _xp(drawing, ".//wp:docPr/@descr")
        if beschr and beschr[0]:
            angabe["alt"] = beschr[0]
        if self._dekorativ(drawing):
            angabe["dekor"] = True
        if tf_daten is not None:
            angabe["art"], angabe["daten"] = "textfeld", tf_daten
            return
        obj = self._frei_objekt_daten(drawing)
        if obj:
            angabe["art"], angabe["daten"] = obj
        else:
            maske = self._frei_maske(drawing)
            if maske:
                angabe["maske"] = maske

    @staticmethod
    def _frei_zuschnitt(angabe: dict, drawing) -> None:
        """Zuschnitt (Tausendstel Prozent)."""
        sr = _xp(drawing, ".//pic:blipFill/a:srcRect")
        if not sr:
            return
        try:
            zu = [max(0.0, min(0.95, int(sr[0].get(k) or 0) / 100000.0)) for k in ("l", "t", "r", "b")]
        except ValueError:
            zu = []
        if any(zu):
            angabe["zu"] = zu

    @staticmethod
    def _frei_helligkeit(angabe: dict, drawing) -> None:
        """Helligkeit/Kontrast (Tausendstel Prozent)."""
        lum = _xp(drawing, ".//pic:blipFill/a:blip/a:lum")
        if not lum:
            return
        for schl, k in (("hell", "bright"), ("kontrast", "contrast")):
            try:
                w = int(lum[0].get(k) or 0) // 1000
            except ValueError:
                w = 0
            if w:
                angabe[schl] = max(-100, min(100, w))

    @staticmethod
    def _frei_fuellung(angabe: dict, drawing) -> None:
        """Füllung der Form hinter dem Bild."""
        fl = _xp(drawing, ".//pic:spPr/a:solidFill/* | .//wps:spPr/a:solidFill/*")
        if fl:
            try:
                from lunivo_writer.editor.objekte.freie_bilder import farbe_aus_element
                angabe["fuell"] = {"art": "farbe", "farbe": farbe_aus_element(fl[0], _NS).name()}
            except Exception:                                              # noqa: BLE001
                pass

    @staticmethod
    def _frei_drehung(angabe: dict, drawing) -> None:
        rot = _xp(drawing, ".//a:xfrm/@rot")
        if rot and rot[0].lstrip("-").isdigit() and int(rot[0]):
            angabe["dreh"] = int(rot[0]) / 60000.0

    @staticmethod
    def _frei_lage(angabe: dict, anker) -> None:
        """Bezug und Ausrichtung/Versatz je Achse (wp:positionH / wp:positionV)."""
        from lunivo_writer.editor.objekte.freie_bilder import emu_zu_px
        for waagerecht, el in ((True, _xp(anker, "wp:positionH")), (False, _xp(anker, "wp:positionV"))):
            if not el:
                continue
            bezug = el[0].get("relativeFrom", "")
            if waagerecht:
                angabe["bh"] = _BEZUG_H.get(bezug, "spalte")
            else:
                angabe["bv"] = _BEZUG_V.get(bezug, "absatz")
            al = _xp(el[0], "wp:align/text()")
            off = _xp(el[0], "wp:posOffset/text()")
            if al:
                angabe["ah" if waagerecht else "av"] = al[0]
            elif off:
                angabe["xh" if waagerecht else "yv"] = emu_zu_px(off[0])

    @staticmethod
    def _frei_maske(drawing) -> str:
        """Die Zuschneideform eines Bildes (``{"maske": …}`` im Titel, „lunivo:“), sonst leer."""
        import json
        titel = _xp(drawing, ".//wp:docPr/@title")
        if titel and titel[0].startswith("lunivo:"):
            try:
                return str(json.loads(titel[0][len("lunivo:"):]).get("maske") or "")
            except (ValueError, AttributeError):
                return ""
        return ""

    @staticmethod
    def _frei_objekt_daten(drawing) -> tuple[str, dict] | None:
        """(Art, Daten) eines freien Objekts Form, Diagramm oder SmartArt aus dem Titel („lunivo:“) des Bildes, sonst None."""
        import json
        titel = _xp(drawing, ".//wp:docPr/@title")
        if titel and titel[0].startswith("lunivo:"):
            try:
                o = json.loads(titel[0][len("lunivo:"):])
            except ValueError:
                return None
            if o.get("art") in ("form", "diagramm", "smartart", "piktogramm") and isinstance(o.get("daten"), dict):
                return o["art"], o["daten"]
        return None

    @staticmethod
    def _freiform_punkte(el):
        """Der Pfad einer frei gezeichneten Form (a:custGeom) als Punkte der Freiform: [Typ, x, y] mit x, y als Anteil 0..1 der Pfadgröße.
        None, wenn es keinen Pfad gibt. Bögen werden übersprungen; quadratische Kurven werden kubisch."""
        punkte: list[list] = []
        for pfad in _xp(el, ".//a:custGeom/a:pathLst/a:path"):
            pw = float(pfad.get("w") or 0) or 1.0
            ph = float(pfad.get("h") or 0) or 1.0
            aktuell = (0.0, 0.0)
            for e in pfad:
                tag = e.tag.rsplit("}", 1)[-1]
                pts = [(float(p.get("x", 0)) / pw, float(p.get("y", 0)) / ph) for p in _xp(e, "a:pt")]
                if tag == "moveTo" and pts:
                    punkte.append([0, *pts[0]]); aktuell = pts[0]
                elif tag == "lnTo" and pts:
                    punkte.append([1, *pts[0]]); aktuell = pts[0]
                elif tag == "cubicBezTo" and len(pts) == 3:
                    punkte += [[2, *pts[0]], [3, *pts[1]], [3, *pts[2]]]; aktuell = pts[2]
                elif tag == "quadBezTo" and len(pts) == 2:
                    (x0, y0), (qx, qy), (x1, y1) = aktuell, pts[0], pts[1]
                    c1 = (x0 + 2 / 3 * (qx - x0), y0 + 2 / 3 * (qy - y0)); c2 = (x1 + 2 / 3 * (qx - x1), y1 + 2 / 3 * (qy - y1))
                    punkte += [[2, *c1], [3, *c2], [3, x1, y1]]; aktuell = (x1, y1)
                elif tag == "close":
                    punkte.append([4, 0.0, 0.0])
        return punkte or None

    @staticmethod
    def _form_aus_docx(drawing):
        """Eine gezeichnete Form (wps:wsp mit Geometrie aus dem Formkatalog) als Form-Daten des Programms; None, wenn es keine solche
        Form ist oder die Geometrie hier nicht abgebildet wird (dann bleibt es beim Hinweis im Bericht)."""
        geo = _xp(drawing, ".//wps:spPr/a:prstGeom/@prst")
        punkte = None
        if not geo:
            punkte = ObjekteMixin._freiform_punkte(drawing)
            if punkte is None:
                return None
        elif geo[0] not in _FORM_AUS_DOCX:
            return None
        daten = {"form": "Freiform" if punkte else _FORM_AUS_DOCX[geo[0]], "fuell": "", "linie": "#00000000", "strich": 0.0, "text": ""}
        if punkte:
            daten["punkte"] = punkte
        fuell = _xp(drawing, ".//wps:spPr/a:solidFill/a:srgbClr/@val")
        if fuell:
            daten["fuell"] = "#" + fuell[0].lower()
        ln = _xp(drawing, ".//wps:spPr/a:ln")
        if ln:
            if ln[0].get("w"):
                daten["strich"] = round(int(ln[0].get("w")) / 12700, 2)            # EMU → Punkt
            farbe = _xp(ln[0], "a:solidFill/a:srgbClr/@val")
            if farbe:
                daten["linie"] = "#" + farbe[0].lower()
            elif _xp(ln[0], "a:noFill"):
                daten["strich"] = 0.0
        return daten

    def _gruppe_einfuegen(self, drawing, cursor: QTextCursor) -> None:
        """Eine Gruppe (wpg) als einzelne freie Objekte: jedes Teil an seiner Lage in der Gruppe, mit der Größe der Gruppe skaliert."""
        from lunivo_writer.editor.objekte import freie_bilder as FB
        base = (drawing.xpath("wp:anchor") or drawing.xpath("wp:inline"))[0]
        rahmen = {"bh": "spalte", "bv": "absatz", "xh": 0.0, "yv": 0.0, "ah": "", "av": ""}
        self._frei_lage(rahmen, base)
        oben = _xp(drawing, ".//wpg:wgp/wpg:grpSpPr/a:xfrm")
        if not oben:
            return
        if drawing.xpath("wp:inline"):
            self._gruppe_platz(drawing.xpath("wp:inline")[0], cursor)
            rahmen["xh"] += cursor.blockFormat().leftMargin()              # eine Gruppe in der Zeile beginnt am linken Einzug des Absatzes
        for leaf, lx, ly, bw, bh_ in self._gruppe_blaetter(oben[0], 0.0, 0.0):
            frei = self._gruppe_blatt(leaf, bw, bh_)
            if frei is None:
                continue
            angabe, img = frei
            if self._dekorativ(drawing):                                   # die Markierung der Gruppe gilt für alle ihre Teile
                angabe["dekor"] = True
            kx, ky = angabe.pop("_kx", 0.0), angabe.pop("_ky", 0.0)         # die Linie bleibt mittig auf ihrer Lage
            angabe.update({"bh": rahmen["bh"], "bv": rahmen["bv"], "xh": rahmen["xh"] + lx / 9525.0 - kx, "yv": rahmen["yv"] + ly / 9525.0 - ky,
                           "hinter": angabe.get("hinter", False)})
            self._frei_einfuegen((angabe, img), cursor)

    def _gruppe_platz(self, inline, cursor: QTextCursor) -> None:
        """Eine Gruppe im Text (wp:inline) steht wie ein Bild in der Zeile und nimmt ihre Höhe ein. Ihre Teile sind frei am Absatz verankert und
        brauchen deshalb einen durchsichtigen Platzhalter in der Zeile (als dekoratives Bild), sonst überdeckt der folgende Text sie."""
        ext = inline.xpath("wp:extent")
        if not ext:
            return
        b, h = _emu_to_px(ext[0].get("cx")), _emu_to_px(ext[0].get("cy"))
        if b < 1 or h < 1:
            return
        leer = QImage(1, 1, QImage.Format_ARGB32)
        leer.fill(0)
        self.img_n += 1
        name = f"docx-platz-{self.img_n}"
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), leer)
        imf = QTextImageFormat()
        imf.setName(name)
        imf.setWidth(b)
        imf.setHeight(h)
        imf.setProperty(P_DEKORATIV, 1)
        cursor.insertImage(imf)

    def _gruppe_blaetter(self, xfrm, o_x: float, o_y: float, skala_x: float = 1.0, skala_y: float = 1.0):
        """Alle Teile einer Gruppe als (Element, Lage x, Lage y, Breite, Höhe) in EMU, bezogen auf den Ursprung der obersten Gruppe.
        ``xfrm``: a:xfrm der Gruppe; ``o``: Ursprung der Gruppe; ``skala``: EMU je Einheit des Elternteils (1 für die oberste Gruppe).
        Verschachtelte Gruppen werden durchlaufen; jede Ebene hat ihr eigenes Koordinatensystem (chOff/chExt)."""
        def werte(el):
            off, ext = el.find(qn("a:off")), el.find(qn("a:ext"))
            if off is None or ext is None:
                return None
            return float(off.get("x", 0)), float(off.get("y", 0)), float(ext.get("cx", 0)), float(ext.get("cy", 0))
        g = werte(xfrm)
        chof, chext = xfrm.find(qn("a:chOff")), xfrm.find(qn("a:chExt"))
        if g is None or chof is None or chext is None:
            return
        cx0, cy0 = float(chof.get("x", 0)), float(chof.get("y", 0))
        cw = float(chext.get("cx", 1)) or 1.0
        ch = float(chext.get("cy", 1)) or 1.0
        sx, sy = (g[2] / cw) * skala_x, (g[3] / ch) * skala_y
        grp = xfrm.getparent().getparent()                          # wpg:wgp oder verschachtelte wpg:grpSp
        for kind in grp:
            if kind.tag in (_WPG + "grpSpPr", _WPG + "cNvGrpSpPr", _WPG + "cNvPr"):
                continue
            if kind.tag == _WPG + "grpSp":
                x_el = kind.find(_WPG + "grpSpPr" + "/" + qn("a:xfrm"))
                q = werte(x_el) if x_el is not None else None
                if q is None:
                    continue
                yield from self._gruppe_blaetter(x_el, o_x + (q[0] - cx0) * sx, o_y + (q[1] - cy0) * sy, sx, sy)
                continue
            teil = kind.find(".//" + qn("a:xfrm"))
            q = werte(teil) if teil is not None else None
            if q is None:
                continue
            yield kind, o_x + (q[0] - cx0) * sx, o_y + (q[1] - cy0) * sy, q[2] * sx, q[3] * sy

    def _gruppe_blatt(self, leaf, bw: float, bh_: float):
        """Ein Teil einer Gruppe → (Angabe, Bild) wie ``_frei``; None, wenn es nicht darstellbar ist (mit Hinweis)."""
        from lunivo_writer.editor.objekte import frei_objekt as FO
        b, h = bw / 9525.0, bh_ / 9525.0
        b2, h2 = max(b, 2.0), max(h, 2.0)               # eine Linie hat Breite oder Höhe 0: das Bild braucht Platz für den Strich (2 Bildpunkte), sonst sieht man sie nicht
        korr = ((b2 - b) / 2, (h2 - h) / 2)
        b, h = b2, h2
        angabe = {"b": b, "h": h, "_kx": korr[0], "_ky": korr[1], "hinter": False, "bh": "spalte", "bv": "absatz", "xh": 0.0, "yv": 0.0, "ah": "", "av": "", "ellipse": False}
        if leaf.tag == _WPS + "wsp":
            if _xp(leaf, "wps:txbx | wps:linkedTxbx"):
                tf = self._textfeld_daten(leaf, leaf)
                angabe["art"], angabe["daten"] = "textfeld", tf
                self._frei_fuellung(angabe, leaf)
                rand = self._frei_rand(leaf)
                if rand:
                    angabe["rand"] = rand
                return angabe, FO.textfeld_zeichnen(tf, b, h)
            form = self._form_aus_docx(leaf)
            if form is not None:
                angabe["art"], angabe["daten"] = "form", form
                return angabe, FO.zeichnen("form", form, b, h)
        if leaf.tag == "{http://schemas.openxmlformats.org/drawingml/2006/picture}pic":
            blips = _xp(leaf, ".//a:blip")
            if blips:
                img = self._frei_bild_laden(blips[0], self.d.part)
                if img is not None:
                    self._frei_fuellung(angabe, leaf)
                    return angabe, img
                return None
        self.report.warn("Formen und gezeichnete Objekte werden nicht dargestellt.")
        return None

    def _schwebend_setzen(self, cursor: QTextCursor, imf, seite: str, versatz: float) -> None:
        """Das umflossene Bild als Schwebeobjekt vor den Absatz des Cursors setzen; geschrieben wird danach am Ende dieses Absatzes weiter."""
        from lunivo_writer.editor.seite.umbruch import absatz_nach_rahmen, schwebend_einfuegen
        bild_pos = schwebend_einfuegen(self.doc, cursor.block().position(), imf, seite, versatz)
        text = absatz_nach_rahmen(self.doc, bild_pos)
        cursor.setPosition(text.position() + text.length() - 1)

    def _umbruch_form(self, drawing, cursor: QTextCursor) -> bool:
        """Gezeichnete Form, die den Text umfließt (wrapSquare/Tight/Through): wie ein umflossenes Bild als Schwebeobjekt am Absatz."""
        if drawing.xpath(".//a:blip") or _xp(drawing, ".//wps:wsp[wps:txbx or wps:linkedTxbx]"):
            return False
        anker = drawing.xpath("wp:anchor")
        form = self._form_aus_docx(drawing) if anker else None
        if form is None:
            return False
        b, h = self._frei_groesse(anker[0], None)
        seite = self._umbruch_seite(drawing, b)
        if not seite:
            return False
        from lunivo_writer.editor.objekte import frei_objekt as FO
        img = FO.zeichnen("form", form, b, h)
        if img is None or img.isNull():
            return False
        self.img_n += 1
        name = f"docx-form-{self.img_n}"
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
        imf = self._bildformat(drawing, name, b, h)
        self._schwebend_setzen(cursor, imf, seite, self._umbruch_versatz(drawing))
        return True

    def _add_image(self, drawing, cursor: QTextCursor, cfmt: QTextCharFormat):
        if _xp(drawing, ".//wpg:wgp"):                             # Gruppe: jedes Teil einzeln
            self._gruppe_einfuegen(drawing, cursor)
            return
        if self._umbruch_form(drawing, cursor):
            return
        if drawing.xpath("wp:inline") and not drawing.xpath(".//a:blip"):      # Textfeld oder Form in der Zeile: nimmt Platz ein, steht am Einzug
            frei = self._frei(drawing, inline_ok=True)
            if frei:
                self._gruppe_platz(drawing.xpath("wp:inline")[0], cursor)
                frei[0]["xh"] = frei[0].get("xh", 0.0) + cursor.blockFormat().leftMargin()
                self._frei_einfuegen(frei, cursor)
                return
        frei = self._frei(drawing)
        if frei is False:
            return
        if frei is not None:
            self._frei_einfuegen(frei, cursor)
            return
        img = self._bild_im_text_laden(drawing)
        if img is None:
            return
        extent = drawing.xpath(".//wp:extent")
        w, h = float(img.width()), float(img.height())
        if extent:
            w = _emu_to_px(extent[0].get("cx"))
            h = _emu_to_px(extent[0].get("cy"))
        self.img_n += 1
        name = f"docx-bild-{self.img_n}"
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
        imf = self._bildformat(drawing, name, w, h)
        seite = self._umbruch_seite(drawing, w)
        if seite:
            self._schwebend_setzen(cursor, imf, seite, self._umbruch_versatz(drawing))        # gehört zum Absatz: davor eingefügt
            return
        cursor.insertImage(imf)

    def _frei_einfuegen(self, frei, cursor: QTextCursor) -> None:
        """Frei positioniertes Bild als Ressource ablegen und am Absatz verankern."""
        from lunivo_writer.editor.objekte import freie_bilder as FB
        angabe, bild = frei
        name = FB.neuer_name(self.doc)
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), bild)
        angabe["n"] = name
        FB.an_absatz(cursor, angabe)

    def _bild_im_text_laden(self, drawing):
        """Bild eines Verweises im Text; None (mit Hinweis im Bericht), wenn keines da, die Daten fehlen oder nicht lesbar sind."""
        blips = drawing.xpath(".//a:blip")
        if not blips:
            return None
        rid = blips[0].get(qn("r:embed"))
        try:
            blob = self.d.part.related_parts[rid].blob
        except KeyError:
            self.report.warn("Ein Bild fehlt im Dokument; an seiner Stelle steht ein Platzhalter.")
            return self._bild_platzhalter(blips[0])
        from lunivo_writer.dienste.vektor_bilder import bild_lesen
        img = self._svg_ergaenzen(blips[0], None, bild_lesen(blob), blob)
        if img.isNull():
            self.report.warn("Ein Bild hat ein nicht lesbares Format; an seiner Stelle steht ein Platzhalter.")
            return self._bild_platzhalter(blips[0])
        return img

    @staticmethod
    def _dekorativ(drawing) -> bool:
        """Ist das Bild wie in Word als dekorativ markiert (``wp:docPr/a:extLst/a:ext/adec:decorative val="1"``)?"""
        for el in drawing.iter("{http://schemas.microsoft.com/office/drawing/2017/decorative}decorative"):
            return (el.get("val") or "1").lower() in ("1", "true")
        return False

    @staticmethod
    def _bildformat(drawing, name: str, w: float, h: float) -> QTextImageFormat:
        """Bildformat mit Größe, Beschreibung (Alternativtext) und den Daten eines eigenen Objekts („lunivo:“-Titel)."""
        imf = QTextImageFormat()
        imf.setName(name)
        imf.setWidth(w)
        imf.setHeight(h)
        alt = drawing.xpath(".//wp:docPr/@descr")
        if alt:
            imf.setProperty(STYLE_PROP + 1, alt[0])
        if ObjekteMixin._dekorativ(drawing):
            imf.setProperty(P_DEKORATIV, 1)
        titel = drawing.xpath(".//wp:docPr/@title")
        if titel and titel[0].startswith("lunivo:"):
            imf.setProperty(P_OBJEKT, titel[0][len("lunivo:"):])
        return imf
