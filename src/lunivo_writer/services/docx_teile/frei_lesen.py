"""Teil von docx_reader: frei lesen (Methoden einer Mixin-Klasse)."""
from __future__ import annotations

from lunivo_writer.services.docx_teile.basis_lesen import (
    P_OBJEKT,
    QTextCharFormat,
    QTextCursor,
    QTextDocument,
    QTextImageFormat,
    QUrl,
    STYLE_PROP,
    _NS,
    _emu_to_px,
    _xp,
    qn,
)  # noqa: F401


class FreiLesen:
    def _frei(self, drawing, teil=None, inline_ok: bool = False):
        """Ein Bild, das frei auf dem Blatt liegt (wp:anchor ohne Textumbruch) → (Angabe, QImage); ``False``, wenn es nicht darstellbar ist
        (Vektorbild); ``None``, wenn es kein solches Bild ist (steht im Text oder umflossen). Siehe editor/freie_bilder.py."""
        from lunivo_writer.editor.freie_bilder import emu_zu_px
        anker = drawing.xpath("wp:anchor") or (drawing.xpath("wp:inline") if inline_ok else [])
        if not anker or _xp(anker[0], "wp:wrapSquare | wp:wrapTight | wp:wrapThrough | wp:wrapTopAndBottom"):
            return None
        a = anker[0]
        textfeld = _xp(drawing, ".//wps:wsp[wps:txbx or wps:linkedTxbx]")             # Textfeld (auch verknüpft), kein Bild
        blips = drawing.xpath(".//a:blip")
        if not blips and not textfeld:
            return None
        img = None
        if not textfeld:
            rid = blips[0].get(qn("r:embed"))
            try:
                blob = (teil or self.d.part).related_parts[rid].blob
            except KeyError:
                self.report.warn("Ein Bild fehlt im Dokument und wurde übersprungen.")
                return False
            from lunivo_writer.editor.freie_bilder import bild_aus_daten
            img = bild_aus_daten(blob)
            if img.isNull():
                self.report.warn("Ein Bild hat ein nicht lesbares Format (zum Beispiel eine Vektorzeichnung) und wird nicht angezeigt.")
                return False
        duo = _xp(drawing, ".//a:blip/a:duotone")
        if duo and len(duo[0]) >= 2:                                   # zweifarbig umgefärbt (zum Beispiel grau statt grün)
            from lunivo_writer.editor.freie_bilder import duoton, farbe_aus_element
            try:
                img = duoton(img, farbe_aus_element(duo[0][0], _NS), farbe_aus_element(duo[0][1], _NS))
            except Exception:                                          # noqa: BLE001 — ein ungewöhnlicher Effekt darf das Laden nicht verhindern
                pass
        ext = _xp(a, "wp:extent")
        b = emu_zu_px(ext[0].get("cx")) if ext else float(img.width() if img is not None else 100)
        h = emu_zu_px(ext[0].get("cy")) if ext else float(img.height() if img is not None else 50)
        tf_daten = None
        if textfeld:
            from lunivo_writer.editor import frei_objekt as FO
            tf_daten = self._textfeld_daten(drawing, textfeld[0])
            img = FO.textfeld_zeichnen(tf_daten, b, h)
        rand = None
        for ln in _xp(drawing, ".//a:ln[a:solidFill]"):                  # Umrandung der Form (der weiße Ring um ein Foto)
            try:
                from lunivo_writer.editor.freie_bilder import farbe_aus_element
                f = farbe_aus_element(_xp(ln, "a:solidFill/*")[0], _NS)
                rand = {"b": max(0.5, emu_zu_px(ln.get("w") or 9525)), "farbe": f.name()}
                dash = _xp(ln, "a:prstDash/@val")
                rand["art"] = {"sysDot": "gepunktet", "dot": "gepunktet", "sysDash": "fein_gestrichelt", "dash": "gestrichelt", "lgDash": "gestrichelt",
                               "dashDot": "strichpunkt", "lgDashDot": "strichpunkt", "lgDashDotDot": "strichpunktpunkt",
                               "sysDashDot": "strichpunkt", "sysDashDotDot": "strichpunktpunkt"}.get(dash[0] if dash else "", "einfach")
            except Exception:                                              # noqa: BLE001
                rand = None
            break
        angabe = {"b": b, "h": h, "hinter": (a.get("behindDoc") or "0").lower() in ("1", "true"), "bh": "spalte", "bv": "absatz",
                  "xh": 0.0, "yv": 0.0, "ah": "", "av": "",
                  "ellipse": bool(_xp(drawing, ".//a:prstGeom[@prst='ellipse']"))}
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
        else:
            obj = self._frei_objekt_daten(drawing)
            if obj:
                angabe["art"], angabe["daten"] = obj
            else:
                maske = self._frei_maske(drawing)
                if maske:
                    angabe["maske"] = maske
        sr = _xp(drawing, ".//pic:blipFill/a:srcRect")                  # Zuschnitt (Tausendstel Prozent)
        if sr:
            try:
                zu = [max(0.0, min(0.95, int(sr[0].get(k) or 0) / 100000.0)) for k in ("l", "t", "r", "b")]
            except ValueError:
                zu = []
            if any(zu):
                angabe["zu"] = zu
        lum = _xp(drawing, ".//pic:blipFill/a:blip/a:lum")                  # Helligkeit/Kontrast (Tausendstel Prozent)
        if lum:
            for schl, k in (("hell", "bright"), ("kontrast", "contrast")):
                try:
                    w = int(lum[0].get(k) or 0) // 1000
                except ValueError:
                    w = 0
                if w:
                    angabe[schl] = max(-100, min(100, w))
        fl = _xp(drawing, ".//pic:spPr/a:solidFill/* | .//wps:spPr/a:solidFill/*")  # Füllung der Form hinter dem Bild
        if fl:
            try:
                from lunivo_writer.editor.freie_bilder import farbe_aus_element
                angabe["fuell"] = {"art": "farbe", "farbe": farbe_aus_element(fl[0], _NS).name()}
            except Exception:                                              # noqa: BLE001
                pass
        rot = _xp(drawing, ".//a:xfrm/@rot")
        if rot and rot[0].lstrip("-").isdigit() and int(rot[0]):
            angabe["dreh"] = int(rot[0]) / 60000.0
        for achse, el in (("h", _xp(a, "wp:positionH")), ("v", _xp(a, "wp:positionV"))):
            if not el:
                continue
            bezug = el[0].get("relativeFrom", "")
            if achse == "h":
                angabe["bh"] = {"page": "seite", "margin": "rand", "leftMargin": "rand", "insideMargin": "rand", "outsideMargin": "rand",
                                "rightMargin": "rand"}.get(bezug, "spalte")
            else:
                angabe["bv"] = {"page": "seite", "margin": "rand", "topMargin": "rand", "insideMargin": "rand", "outsideMargin": "rand",
                                "bottomMargin": "rand"}.get(bezug, "absatz")
            al = _xp(el[0], "wp:align/text()")
            off = _xp(el[0], "wp:posOffset/text()")
            if al:
                angabe["ah" if achse == "h" else "av"] = al[0]
            elif off:
                angabe["xh" if achse == "h" else "yv"] = emu_zu_px(off[0])
        return angabe, img

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
    def _textfeld_daten(drawing, wsp) -> dict:
        """Die Parameter eines Textfelds (``editor/frei_objekt.py``): genau die gespeicherten aus dem Titel („lunivo:“), sonst aus dem Text des
        Kastens (``w:txbxContent``) und seiner Verknüpfung (``wps:linkedTxbx`` mit ``id`` und ``seq``, wie in Word)."""
        import json
        titel = _xp(drawing, ".//wp:docPr/@title")
        if titel and titel[0].startswith("lunivo:"):
            try:
                o = json.loads(titel[0][len("lunivo:"):])
                if o.get("art") == "textfeld" and isinstance(o.get("daten"), dict):
                    return o["daten"]
            except ValueError:
                pass
        daten: dict = {"text": "", "schrift": "Liberation Sans", "pt": 11, "farbe": "#1f1f1f"}
        absaetze = _xp(wsp, "wps:txbx/w:txbxContent/w:p")
        laeufe: list[dict] = []
        for i, p in enumerate(absaetze):
            if i:
                laeufe.append({"t": "\n"})
            for r in _xp(p, "w:r"):
                t = "".join(_xp(r, "w:t/text()"))
                if not t:
                    continue
                lauf = {"t": t}
                rpr = _xp(r, "w:rPr")
                if rpr:
                    rp = rpr[0]
                    for k, ausdruck in (("fett", "w:b"), ("kursiv", "w:i"), ("durch", "w:strike")):
                        el = _xp(rp, ausdruck)
                        if el and el[0].get(qn("w:val")) not in ("0", "false"):
                            lauf[k] = True
                    u = _xp(rp, "w:u/@w:val")
                    if u and u[0] != "none":
                        lauf["unter"] = True
                    va = _xp(rp, "w:vertAlign/@w:val")
                    if va and va[0] in ("superscript", "subscript"):
                        lauf["hoch" if va[0] == "superscript" else "tief"] = True
                    c = _xp(rp, "w:color/@w:val")
                    if c and c[0] not in ("auto", ""):
                        lauf["fuell"] = "#" + c[0].lower()
                    shd = _xp(rp, "w:shd/@w:fill")
                    if shd and shd[0] not in ("auto", ""):
                        lauf["hervor"] = "#" + shd[0].lower()
                    sz = _xp(rp, "w:sz/@w:val")
                    if sz and sz[0].isdigit():
                        lauf["pt"] = int(sz[0]) / 2
                laeufe.append(lauf)
        for r in laeufe:                                           # was dem Standard des Textfelds entspricht, ist keine eigene Angabe
            if r.get("pt") == daten["pt"]:
                r.pop("pt")
            if r.get("fuell") == daten["farbe"]:
                r.pop("fuell")
        text = "".join(r["t"] for r in laeufe)
        daten["text"] = text
        if any(len(r) > 1 for r in laeufe):
            daten["laeufe"] = laeufe
        ver = _xp(wsp, "wps:linkedTxbx")
        kopf = _xp(wsp, "wps:txbx/@id")
        kette, seq = (ver[0].get("id"), int(ver[0].get("seq") or 0)) if ver else (kopf[0] if kopf else None, 0)
        if ver and kette is not None:
            daten["id"] = f"k{kette}_{seq}"
            if seq > 0:
                daten["von"] = f"k{kette}_{seq - 1}"
            daten["weiter"] = f"k{kette}_{seq + 1}"                # unbekannte Folgefelder entfernt ``_ketten_bereinigen``
        return daten

    def _ketten_bereinigen(self) -> None:
        """Nach dem Lesen: Verweise auf Folgefelder, die es nicht gibt, entfernen."""
        import json
        from lunivo_writer.editor import freie_bilder as FB
        from lunivo_writer.editor.zusatz import B_BILDANKER
        ids = set()
        b = self.doc.firstBlock()
        while b.isValid():
            for a in FB.aus_absatz(b.blockFormat()):
                if a.get("art") == "textfeld" and a.get("daten", {}).get("id"):
                    ids.add(a["daten"]["id"])
            b = b.next()
        b = self.doc.firstBlock()
        while b.isValid():
            liste = FB.aus_absatz(b.blockFormat())
            geaendert = False
            for a in liste:
                d = a.get("daten") if a.get("art") == "textfeld" else None
                if d and d.get("weiter") and d["weiter"] not in ids:
                    d.pop("weiter"); geaendert = True
                if d and d.get("von") and d["von"] not in ids:
                    d.pop("von"); geaendert = True
            if geaendert:
                bf = b.blockFormat(); bf.setProperty(B_BILDANKER, json.dumps(liste, separators=(",", ":")))
                QTextCursor(b).setBlockFormat(bf)
            b = b.next()

    def _add_image(self, drawing, cursor: QTextCursor, cfmt: QTextCharFormat):
        frei = self._frei(drawing)
        if frei is False:
            return
        if frei is not None:
            from lunivo_writer.editor import freie_bilder as FB
            angabe, bild = frei
            name = FB.neuer_name(self.doc)
            self.doc.addResource(QTextDocument.ImageResource, QUrl(name), bild)
            angabe["n"] = name
            FB.an_absatz(cursor, angabe)
            return
        blips = drawing.xpath(".//a:blip")
        if not blips:
            return
        rid = blips[0].get(qn("r:embed"))
        try:
            blob = self.d.part.related_parts[rid].blob
        except KeyError:
            self.report.warn("Ein Bild fehlt im Dokument und wurde übersprungen.")
            return
        from lunivo_writer.editor.freie_bilder import bild_aus_daten
        img = bild_aus_daten(blob)
        if img.isNull():
            self.report.warn("Ein Bild hat ein nicht lesbares Format und wurde übersprungen.")
            return
        extent = drawing.xpath(".//wp:extent")
        w, h = float(img.width()), float(img.height())
        if extent:
            w = _emu_to_px(extent[0].get("cx"))
            h = _emu_to_px(extent[0].get("cy"))
        self.img_n += 1
        name = f"docx-bild-{self.img_n}"
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
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
        seite = self._umbruch_seite(drawing, w)
        if seite:
            from lunivo_writer.editor.umbruch import absatz_nach_rahmen, schwebend_einfuegen
            bild_pos = schwebend_einfuegen(self.doc, cursor.block().position(), imf, seite)   # gehört zum Absatz: davor eingefügt
            text = absatz_nach_rahmen(self.doc, bild_pos)
            cursor.setPosition(text.position() + text.length() - 1)                          # weiter am Ende dieses Absatzes schreiben
            return
        cursor.insertImage(imf)
