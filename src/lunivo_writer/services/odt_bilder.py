"""Bildimport und Rahmenbehandlung für den ODT-Reader."""
from __future__ import annotations

import base64
import re
import xml.etree.ElementTree as ET

from PySide6.QtCore import QUrl
from PySide6.QtGui import QImage, QTextCursor, QTextDocument, QTextImageFormat

from lunivo_writer.services.odt_xml import _q, _px, _text_von


class _ODTBilder:
    def _bild_laden(self, bild: ET.Element) -> QImage:
        daten = None
        href = bild.get(_q("xlink:href"), "")
        binaer = bild.find(_q("office:binary-data"))
        if binaer is not None and binaer.text:
            try:
                daten = base64.b64decode(binaer.text)
            except ValueError:
                daten = None
        elif href and not re.match(r"^[a-z]+:", href):
            daten = self.bilder(href.lstrip("./"))
        img = QImage()
        if not daten or not img.loadFromData(daten):
            from lunivo_writer.editor.freie_bilder import bild_aus_daten
            img = bild_aus_daten(daten) if daten else QImage()
        return img

    def _frei_angabe(self, frame: ET.Element) -> dict | None:
        """Ein Rahmen am Absatz oder an der Seite, den kein Text umfließt → Angabe wie in editor/freie_bilder.py, sonst None."""
        from lunivo_writer.services.odt_writer import AUSR_H, AUSR_V, BEZUG_H, BEZUG_V
        anker = frame.get(_q("text:anchor-type"), "as-char")
        if anker not in ("paragraph", "char", "page"):
            return None
        g = self.stile.eigenschaften("graphic", frame.get(_q("draw:style-name")), "graphic")
        if g.get("style:wrap") != "run-through":                # umflossene Bilder bleiben Bilder im Text
            return None
        zurueck = lambda tab, wert, standard: next((k for k, v in tab.items() if v == wert), standard)   # noqa: E731
        hpos, vpos = g.get("style:horizontal-pos", "from-left"), g.get("style:vertical-pos", "from-top")
        return {"b": _px(frame.get(_q("svg:width")), 0.0) or None, "h": _px(frame.get(_q("svg:height")), 0.0) or None,
                "hinter": g.get("style:run-through") == "background",
                "bh": "seite" if anker == "page" else zurueck(BEZUG_H, g.get("style:horizontal-rel", "paragraph"), "spalte"),
                "bv": "seite" if anker == "page" else zurueck(BEZUG_V, g.get("style:vertical-rel", "paragraph"), "absatz"),
                "ah": zurueck(AUSR_H, hpos, ""), "av": zurueck(AUSR_V, vpos, ""),
                "xh": _px(frame.get(_q("svg:x")), 0.0), "yv": _px(frame.get(_q("svg:y")), 0.0), "ellipse": False}

    def rahmen(self, frame: ET.Element, cur: QTextCursor) -> None:
        bild = frame.find(_q("draw:image"))
        if bild is None:
            if frame.find(_q("draw:text-box")) is not None:
                self.report.warn("Textrahmen aus der ODT-Datei wurden als Text übernommen.")
                for k in frame.find(_q("draw:text-box")).iter():
                    if k.tag in (_q("text:p"), _q("text:h")):
                        cur.insertText(_text_von(k) + " ")
            else:
                self.report.warn("Zeichnungen und Formen aus der ODT-Datei wurden nicht übernommen.")
            return
        img = self._bild_laden(bild)
        if img.isNull():
            self.report.warn("Ein Bild aus der ODT-Datei war nicht lesbar und wurde übersprungen.")
            return
        angabe = self._frei_angabe(frame)
        if angabe is not None:                                 # frei auf dem Blatt (am Absatz): als Bildanker des Absatzes
            from lunivo_writer.editor import freie_bilder as FB
            name = FB.neuer_name(self.doc)
            self.doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
            angabe.update(n=name, b=angabe["b"] or img.width(), h=angabe["h"] or img.height())
            FB.an_absatz(cur, angabe)
            return
        self.bild_n += 1
        name = f"odt-bild-{self.bild_n}"
        self.doc.addResource(QTextDocument.ImageResource, QUrl(name), img)
        f = QTextImageFormat()
        f.setName(name)
        f.setWidth(_px(frame.get(_q("svg:width")), img.width()))
        f.setHeight(_px(frame.get(_q("svg:height")), img.height()))
        cur.insertImage(f)
