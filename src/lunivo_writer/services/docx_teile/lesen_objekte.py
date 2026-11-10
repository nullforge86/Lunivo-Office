"""DOCX lesen: Bilder und schwebende Objekte (Textfelder: lesen_textfelder.py)."""
from __future__ import annotations

from lunivo_writer.services.docx_teile.lesen_gemeinsam import (  # noqa: F401
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
    _NS,
    _xp,
    _emu_to_px,
)


# Strichart der Umrandung Word → Programm; Bezugspunkt der Lage Word → Programm (waagerecht/senkrecht)
_RAND_ART = {"sysDot": "gepunktet", "dot": "gepunktet", "sysDash": "fein_gestrichelt", "dash": "gestrichelt", "lgDash": "gestrichelt",
             "dashDot": "strichpunkt", "lgDashDot": "strichpunkt", "lgDashDotDot": "strichpunktpunkt",
             "sysDashDot": "strichpunkt", "sysDashDotDot": "strichpunktpunkt"}
_BEZUG_H = {"page": "seite", "margin": "rand", "leftMargin": "rand", "insideMargin": "rand", "outsideMargin": "rand", "rightMargin": "rand"}
_BEZUG_V = {"page": "seite", "margin": "rand", "topMargin": "rand", "insideMargin": "rand", "outsideMargin": "rand", "bottomMargin": "rand"}
_PT = 12700.0                                                      # EMU je Punkt


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
        if a is None:
            return None
        textfeld = _xp(drawing, ".//wps:wsp[wps:txbx or wps:linkedTxbx]")             # Textfeld (auch verknüpft), kein Bild
        blips = drawing.xpath(".//a:blip")
        if not blips and not textfeld:
            return None
        img = None
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
            self.report.warn("Ein Bild fehlt im Dokument und wurde übersprungen.")
            return None
        from lunivo_writer.editor.objekte.freie_bilder import bild_aus_daten
        img = bild_aus_daten(blob)
        if img.isNull():
            self.report.warn("Ein Bild hat ein nicht lesbares Format (zum Beispiel eine Vektorzeichnung) und wird nicht angezeigt.")
            return None
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

    def _add_image(self, drawing, cursor: QTextCursor, cfmt: QTextCharFormat):
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
            from lunivo_writer.editor.seite.umbruch import absatz_nach_rahmen, schwebend_einfuegen
            bild_pos = schwebend_einfuegen(self.doc, cursor.block().position(), imf, seite)   # gehört zum Absatz: davor eingefügt
            text = absatz_nach_rahmen(self.doc, bild_pos)
            cursor.setPosition(text.position() + text.length() - 1)                          # weiter am Ende dieses Absatzes schreiben
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
            self.report.warn("Ein Bild fehlt im Dokument und wurde übersprungen.")
            return None
        from lunivo_writer.editor.objekte.freie_bilder import bild_aus_daten
        img = bild_aus_daten(blob)
        if img.isNull():
            self.report.warn("Ein Bild hat ein nicht lesbares Format und wurde übersprungen.")
            return None
        return img

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
        titel = drawing.xpath(".//wp:docPr/@title")
        if titel and titel[0].startswith("lunivo:"):
            imf.setProperty(P_OBJEKT, titel[0][len("lunivo:"):])
        return imf
