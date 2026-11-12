"""DOCX lesen: ältere Zeichnungsobjekte in VML (``w:pict``) — Textfelder, Formen und Bilder aus Versionen vor 2010.

Die VML-Objekte werden in dasselbe Format gebracht wie die DrawingML-Objekte (``lesen_objekte``): frei auf dem Blatt, Lage und Größe aus
dem ``style`` des Objekts, Füllung und Rahmen aus ``fillcolor`` und ``v:stroke``. Formen werden über ihren Namen erkannt (Word vergibt
„Teardrop 1“, „Oval 2“ …); unbekannte Namen bleiben mit Hinweis im Bericht."""
from __future__ import annotations

import re

from lunivo_writer.dienste.docx_teile.lesen_gemeinsam import _xp, qn, QTextCursor

_PT_PX = 96 / 72                                                       # Punkt → Bildpunkt

# Name, den Word einer VML-Form gibt (ohne Nummer) → Name im Formkatalog des Programms
_VML_FORMEN = {"Rectangle": "Rechteck", "Rounded Rectangle": "Abgerundetes Rechteck", "Oval": "Ellipse", "Diamond": "Raute",
               "Triangle": "Dreieck", "Right Triangle": "Rechtwinkliges Dreieck", "Parallelogram": "Parallelogramm",
               "Trapezoid": "Trapez", "Pentagon": "Fünfeck", "Hexagon": "Sechseck", "Octagon": "Achteck", "Heart": "Herz",
               "Cloud": "Wolke", "Teardrop": "Tropfen", "Moon": "Mond", "Lightning Bolt": "Blitz", "Cross": "Kreuz",
               "5-Point Star": "Stern mit 5 Zacken", "Right Arrow": "Pfeil nach rechts", "Left Arrow": "Pfeil nach links",
               "Up Arrow": "Pfeil nach oben", "Down Arrow": "Pfeil nach unten"}

_BEZUG_H = {"page": "seite", "margin": "rand", "text": "spalte", "char": "spalte", "column": "spalte"}
_BEZUG_V = {"page": "seite", "margin": "rand", "text": "absatz", "line": "absatz", "paragraph": "absatz"}


def _stil(el) -> dict:
    """Das Attribut ``style`` als Verzeichnis, z. B. {"margin-left": "12pt", …}."""
    aus = {}
    for teil in (el.get("style") or "").split(";"):
        if ":" in teil:
            k, v = teil.split(":", 1)
            aus[k.strip().lower()] = v.strip()
    return aus


def _pt(wert: str | None) -> float | None:
    """„12.5pt“ → 12.5; Zahlen ohne Einheit gelten als Punkt; sonst None."""
    if not wert:
        return None
    m = re.match(r"^\s*(-?[\d.]+)\s*(pt|px|in|cm|mm)?\s*$", wert)
    if not m:
        return None
    zahl, einheit = float(m.group(1)), m.group(2) or "pt"
    return {"pt": zahl, "px": zahl * 0.75, "in": zahl * 72, "cm": zahl * 72 / 2.54, "mm": zahl * 72 / 25.4}[einheit]


def _hex(wert: str | None) -> str | None:
    """Farbe als „#rrggbb“, wenn VML sie so angibt; benannte Farben bleiben ungelesen."""
    if wert and re.match(r"^#[0-9a-fA-F]{6}$", wert.strip()):
        return wert.strip().lower()
    return None


class VmlMixin:
    """DOCX lesen: VML-Textfelder, -Formen und -Bilder (``w:pict``)."""

    def _run_vml(self, child, cursor: QTextCursor, cfmt) -> bool:
        """Alle VML-Objekte eines ``w:pict`` als freie Objekte einfügen. → True, wenn etwas eingefügt wurde."""
        added = False
        for shape in _xp(child, ".//v:shape | .//v:rect | .//v:oval | .//v:roundrect"):
            frei = self._vml_frei(shape)
            if frei is None:
                continue
            self._frei_einfuegen(frei, cursor)
            added = True
        return added

    def _vml_frei(self, shape):
        """(Angabe, Bild) eines VML-Objekts wie ``_frei`` in lesen_objekte; None, wenn es nicht darstellbar ist (mit Hinweis)."""
        from lunivo_writer.editor.objekte import frei_objekt as FO
        from lunivo_writer.dienste.vektor_bilder import bild_lesen
        stil = _stil(shape)
        b = (_pt(stil.get("width")) or 100) * _PT_PX
        h = (_pt(stil.get("height")) or 50) * _PT_PX
        angabe = {"b": b, "h": h, "hinter": (stil.get("z-index") or "0").startswith("-"), "bh": "spalte", "bv": "absatz",
                  "xh": 0.0, "yv": 0.0, "ah": "", "av": ""}
        self._vml_lage(angabe, stil)
        fuell, linie, strich = self._vml_farben(angabe, shape)
        textbox = _xp(shape, "v:textbox/w:txbxContent")
        if textbox:
            daten = self._vml_textfeld(textbox[0])
            angabe["art"], angabe["daten"] = "textfeld", daten
            return angabe, FO.textfeld_zeichnen(daten, b, h)
        bild = _xp(shape, "v:imagedata/@r:id")
        if bild:
            try:
                blob = self.d.part.related_parts[bild[0]].blob
            except KeyError:
                self.report.warn("Ein Bild fehlt im Dokument und wurde übersprungen.")
                return None
            img = bild_lesen(blob)
            if img.isNull():
                self.report.warn("Ein Bild hat ein nicht lesbares Format (zum Beispiel eine Vektorzeichnung) und wird nicht angezeigt.")
                return None
            return angabe, img
        name = _VML_FORMEN.get(re.sub(r"\s*\d+$", "", shape.get("id") or ""))
        if name is None:
            self.report.warn("Formen und gezeichnete Objekte werden nicht dargestellt.")
            return None
        daten = {"form": name, "fuell": fuell or "", "linie": linie, "strich": strich, "text": ""}
        angabe["art"], angabe["daten"] = "form", daten
        return angabe, FO.zeichnen("form", daten, b, h)

    @staticmethod
    def _vml_lage(angabe: dict, stil: dict) -> None:
        """Absolute Lage (``margin-left``/``margin-top``) und Bezug (``mso-position-…-relative``) oder Ausrichtung."""
        for waagerecht, rel, ausr, rand_k, bezug in ((True, "mso-position-horizontal-relative", "mso-position-horizontal", "margin-left", _BEZUG_H),
                                                    (False, "mso-position-vertical-relative", "mso-position-vertical", "margin-top", _BEZUG_V)):
            angabe["bh" if waagerecht else "bv"] = bezug.get(stil.get(rel, ""), "spalte" if waagerecht else "absatz")
            if stil.get(ausr) in ("center", "left", "right", "inside", "outside", "top", "bottom"):
                angabe["ah" if waagerecht else "av"] = stil[ausr]
            else:
                px = _pt(stil.get(rand_k))
                if px is not None:
                    angabe["xh" if waagerecht else "yv"] = px * _PT_PX

    @staticmethod
    def _vml_farben(angabe: dict, shape) -> tuple[str | None, str, float]:
        """Füllung (``fillcolor``) und Rahmen (``v:stroke``) des Objekts an die Angabe; → (Füllfarbe, Linienfarbe, Strichstärke) für Formen."""
        fuell = _hex(shape.get("fillcolor")) if shape.get("filled", "t") != "f" else None
        if fuell:
            angabe["fuell"] = {"art": "farbe", "farbe": fuell}
        linie, strich_pt = "#00000000", 0.0
        strich = _xp(shape, "v:stroke")
        if strich and strich[0].get("on", "t") != "f":
            s = strich[0]
            strich_pt = _pt(s.get("weight")) or 0.75
            linie = _hex(s.get("color")) or "#000000"
            angabe["rand"] = {"b": max(0.5, strich_pt * _PT_PX), "farbe": linie, "art": "einfach"}
        return fuell, linie, strich_pt

    def _vml_textfeld(self, inhalt) -> dict:
        """Die Parameter eines Textfelds aus den Absätzen des VML-Kastens (wie ``_textfeld_daten``)."""
        from lunivo_writer.dienste.docx_teile.lesen_textfelder import _STANDARD
        daten: dict = dict(_STANDARD)
        laeufe: list[dict] = []
        for i, p in enumerate(_xp(inhalt, "w:p")):
            if i:
                laeufe.append({"t": "\n"})
            for r in _xp(p, "w:r"):
                t = "".join(_xp(r, "w:t/text()"))
                if t:
                    laeufe.append(self._textfeld_lauf(r, t))
        for r in laeufe:
            if r.get("pt") == daten["pt"]:
                r.pop("pt")
            if r.get("fuell") == daten["farbe"]:
                r.pop("fuell")
        daten["text"] = "".join(r["t"] for r in laeufe)
        if any(len(r) > 1 for r in laeufe):
            daten["laeufe"] = laeufe
        return daten
