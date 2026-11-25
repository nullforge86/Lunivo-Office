"""Formen, Linien, Textrahmen und Gruppen aus ODT/FODT (``draw:custom-shape``, ``draw:rect``, ``draw:ellipse``, ``draw:line``, ``draw:frame`` mit Textfeld, ``draw:g``) in
das Dokumentmodell — Qt-frei, mit denselben Wörterbüchern wie der DOCX-Weg (``docx_formen``): ``{"art", "breite", "hoehe", "alt", "daten"}``.

Füllungen: einfarbig, Verlauf (``draw:gradient``, auch mit Stützstellen ``loext:gradient-stop``), Schraffur (``draw:hatch``) als Muster und Bild (``draw:fill-image``);
Konturen mit Farbe, Stärke und Strichart. Ein Verlauf mit ``draw:angle`` θ entspricht dem OOXML-Winkel 90° − θ; Schraffuren werden den Mustern des Modells zugeordnet
(Richtung nach ``draw:rotation``, ``double`` = Kreuzschraffur, dichte Linien = „hell“)."""
from __future__ import annotations

import base64
import math
import xml.etree.ElementTree as ET

from lunivo_writer.dienste.docx.docx_formen import _GEOMETRIE
from lunivo_writer.dienste.odt.odt_xml import _kurz, _px, _q

_LO_GEOMETRIE = {"rectangle": "rechteck", "round-rectangle": "abgerundet", "ellipse": "ellipse", "circle": "ellipse", "isosceles-triangle": "dreieck",
                 "right-triangle": "rechtwinkliges_dreieck", "diamond": "raute", "pentagon": "fuenfeck", "hexagon": "sechseck", "octagon": "achteck", "star4": "stern4",
                 "star5": "stern", "star6": "stern6", "star8": "stern8", "heart": "herz", "cloud": "wolke", "parallelogram": "parallelogramm", "trapezoid": "trapez",
                 "cross": "kreuz", "can": "zylinder", "right-arrow": "blockpfeil_rechts", "left-arrow": "blockpfeil_links", "up-arrow": "blockpfeil_oben",
                 "down-arrow": "blockpfeil_unten", "chevron": "chevron", "pentagon-right": "pfeil_fuenfeck", "mso-spt1": "rechteck", "mso-spt3": "ellipse"}
_SCHRAFFUR = {(0, "single"): "h", (900, "single"): "v", (450, "single"): "auf", (1350, "single"): "ab", (0, "double"): "raster", (900, "double"): "raster",
              (450, "double"): "karo", (1350, "double"): "karo"}
_FORMEN_TAGS = ("draw:custom-shape", "draw:rect", "draw:ellipse", "draw:line", "draw:g", "draw:frame", "draw:polygon", "draw:polyline", "draw:path", "draw:connector")


def ist_form(node: ET.Element) -> bool:
    return any(node.tag == _q(t) for t in _FORMEN_TAGS[:5])


def _werte(leser, node: ET.Element, familie: str = "graphic") -> dict:
    """Die Zeicheneigenschaften des Elements: Werte seines Stils (mit Eltern), darüber die Angaben am Element selbst."""
    w = dict(leser.stile.eigenschaften(familie, node.get(_q("draw:style-name")), "graphic"))
    w.update({_kurz(k): v for k, v in node.attrib.items()})
    return w


def _grad(winkel: str | None) -> float:
    try:
        return float(str(winkel or "0").replace("deg", "").replace("°", ""))
    except ValueError:
        return 0.0


def _hex(wert: str | None) -> str:
    return wert.lower() if wert and len(wert) == 7 and wert.startswith("#") else ""


def _benannt(leser, art: str, name: str | None):
    return leser.stile.zeichen.get((art, name)) if name else None


def _verlauf(leser, name: str | None) -> dict | None:
    el = _benannt(leser, "gradient", name)
    if el is None:
        return None
    start, ende = _hex(el.get(_q("draw:start-color"))) or "#000000", _hex(el.get(_q("draw:end-color"))) or "#ffffff"
    stops = [[float((s.get(_q("svg:offset")) or "0").rstrip("%")) / (100.0 if str(s.get(_q("svg:offset"))).endswith("%") else 1.0), _hex(s.get(_q("svg:stop-color")))]
             for s in el if s.tag.endswith("gradient-stop") and _hex(s.get(_q("svg:stop-color")))]
    if len(stops) < 2:
        stops = [[0.0, start], [1.0, ende]]
        if el.get(_q("draw:style")) == "axial":                        # achsensymmetrisch: Endfarbe in der Mitte
            stops = [[0.0, ende], [0.5, start], [1.0, ende]]
    winkel = (90.0 - _grad(el.get(_q("draw:angle")))) % 360.0
    return {"art": "graduell", "farbe": stops[0][1], "hell": stops[0][1], "dunkel": stops[-1][1], "stops": stops, "winkel": winkel}


def _muster(leser, name: str | None, grund: str, deckend: bool) -> dict | None:
    el = _benannt(leser, "hatch", name)
    if el is None:
        return None
    try:
        drehung = int(float(el.get(_q("draw:rotation")) or 0)) % 1800
    except ValueError:
        drehung = 0
    richtung = _SCHRAFFUR.get((drehung if drehung in (0, 900, 450, 1350) else min((0, 450, 900, 1350), key=lambda r: abs(r - drehung)), el.get(_q("draw:style")) or "single"), "h")
    dicht = _px(el.get(_q("draw:distance")), 4.0) < 0.08 * 96 / 2.54
    key = ("hell_" if dicht else "dunkel_") + richtung
    return {"art": "muster", "farbe": _hex(el.get(_q("draw:color"))) or "#000000", "key": key, "grund": grund if deckend and grund else ""}


def _bild(leser, name: str | None) -> dict | None:
    el = _benannt(leser, "fill-image", name)
    if el is None:
        return None
    daten = leser._bytes(el)
    if not daten:
        return None
    return {"art": "bild", "farbe": "", "n": leser.ressource_neu(daten)}


def fuellung(leser, w: dict) -> dict | None:
    """Die Füllung aus den Eigenschaften; ``None`` = nicht angegeben, ``{}`` = keine Füllung."""
    art = w.get("draw:fill")
    farbe = _hex(w.get("draw:fill-color"))
    if art == "none":
        return {}
    if art == "solid":
        return {"art": "farbe", "farbe": farbe} if farbe else None
    if art == "gradient":
        return _verlauf(leser, w.get("draw:fill-gradient-name"))
    if art == "hatch":
        return _muster(leser, w.get("draw:fill-hatch-name"), farbe, w.get("draw:fill-hatch-solid") == "true")
    if art == "bitmap":
        return _bild(leser, w.get("draw:fill-image-name"))
    return None


def kontur(leser, w: dict, standard_sichtbar: bool) -> dict | None:
    art = w.get("draw:stroke", "solid" if standard_sichtbar else "none")
    if art == "none":
        return None
    farbe = _hex(w.get("svg:stroke-color")) or "#3465a4" if standard_sichtbar else _hex(w.get("svg:stroke-color")) or "#000000"
    strich = "einfach"
    if art == "dash":
        el = _benannt(leser, "stroke-dash", w.get("draw:stroke-dash"))
        punkt = _px(el.get(_q("draw:dots1-length")), 0.0) if el is not None else 0.0
        strich = "gepunktet" if el is not None and 0 < punkt < 0.06 * 96 / 2.54 else "gestrichelt"
    return {"farbe": farbe, "b": max(0.5, _px(w.get("svg:stroke-width"), 1.0)), "art": strich}


def _rand_fo(w: dict) -> dict | None:
    """Der Rand eines Rahmens (``fo:border`` „0.5pt solid #000000“) als Kontur."""
    for k in ("fo:border", "fo:border-top", "fo:border-left"):
        wert = w.get(k)
        if wert and wert != "none":
            teile = wert.split()
            farbe = next((t for t in teile if t.startswith("#")), "#000000")
            return {"farbe": farbe.lower(), "b": max(0.5, _px(teile[0], 1.0)), "art": "einfach"}
    return None


def _zahlen_pfad(d: str) -> list:
    """Pfaddaten (``svg:d``) in Anweisungen ``["M", x, y] …`` mit absoluten Koordinaten (M, L, H, V, C, Q, Z, auch klein geschrieben als relativ)."""
    import re
    teile = re.findall(r"[MmLlCcQqZzHhVv]|-?\d*\.?\d+(?:[eE][-+]?\d+)?", d or "")
    ops: list = []
    i, x, y, anfang = 0, 0.0, 0.0, (0.0, 0.0)
    kdo = ""
    zahlen = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "Q": 4}

    def zahl(k):
        return [float(t) for t in teile[i:i + k]]
    while i < len(teile):
        if teile[i].isalpha():
            kdo = teile[i]
            i += 1
            if kdo in "Zz":
                ops.append(["Z"])
                x, y = anfang
                continue
        rel, gross = kdo.islower(), kdo.upper()
        n = zahlen.get(gross)
        if n is None or i + n > len(teile):
            break
        w = zahl(n)
        i += n
        if gross == "H":
            x = x + w[0] if rel else w[0]
            ops.append(["L", x, y])
        elif gross == "V":
            y = y + w[0] if rel else w[0]
            ops.append(["L", x, y])
        else:
            if rel:
                w = [v + (x if k % 2 == 0 else y) for k, v in enumerate(w)]
            x, y = w[-2], w[-1]
            ops.append(["M" if gross == "M" else gross, *w])
            if gross == "M":
                anfang = (x, y)
                kdo = "l" if rel else "L"                          # weitere Zahlenpaare nach M sind Linien
    return ops


def _pfad_aus_odt(node: ET.Element) -> tuple:
    """Vieleck, Linienzug oder Pfad als normalisierte Anweisungen (Koordinaten 0…1 der ``svg:viewBox``) und Kennzeichen „offen“."""
    breite, hoehe = _px(node.get(_q("svg:width")), 1.0), _px(node.get(_q("svg:height")), 1.0)
    try:
        vx, vy, vw, vh = (float(v) for v in (node.get(_q("svg:viewBox")) or "").split())
    except ValueError:
        vx = vy = 0.0
        vw, vh = breite, hoehe
    if node.tag in (_q("draw:polygon"), _q("draw:polyline")):
        punkte = [tuple(float(c) for c in p.split(",")) for p in (node.get(_q("draw:points")) or "").split() if "," in p]
        if len(punkte) < 2:
            return [], False
        ops = [["M", *punkte[0]]] + [["L", *p] for p in punkte[1:]]
        if node.tag == _q("draw:polygon"):
            ops.append(["Z"])
    else:
        ops = _zahlen_pfad(node.get(_q("svg:d")))
    vw, vh = vw or 1.0, vh or 1.0
    norm = [[o[0]] + [((v - vx) / vw) if k % 2 == 0 else ((v - vy) / vh) for k, v in enumerate(o[1:])] for o in ops]
    return norm, not any(o[0] == "Z" for o in norm)


def _text(node: ET.Element) -> str:
    absaetze = [p for p in node.iter() if p.tag in (_q("text:p"), _q("text:h"))]
    return "\n".join("".join(p.itertext()) for p in absaetze).strip("\n")


def _textformat(leser, node: ET.Element) -> dict:
    """Schrift, Größe, Farbe und Fettdruck des ersten Textstücks (Zeichenstil oder Absatzstil)."""
    from lunivo_writer.dienste.odt.odt_dokument_leser import _zeichen
    p = next((p for p in node.iter() if p.tag in (_q("text:p"), _q("text:h"))), None)
    if p is None:
        return {}
    stile = [p.get(_q("text:style-name"))] + [s.get(_q("text:style-name")) for s in p.iter(_q("text:span"))]
    werte: dict = {}
    for name in stile:
        werte.update(leser.stile.eigenschaften("paragraph", name, "text"))
        werte.update(leser.stile.eigenschaften("text", name, "text"))
    z = _zeichen(werte, leser.stile)
    aus = {}
    if z.get("schrift"):
        aus["schrift"] = z["schrift"]
    if z.get("groesse_pt"):
        aus["pt"] = z["groesse_pt"]
    if z.get("farbe"):
        aus["farbe"] = z["farbe"]
    for k in ("fett", "kursiv"):
        if z.get(k):
            aus[k] = True
    return aus


def _geometrie(leser, node: ET.Element) -> str:
    eg = node.find(_q("draw:enhanced-geometry"))
    typ = (eg.get(_q("draw:type")) if eg is not None else "") or ""
    art = _GEOMETRIE.get(typ[6:]) if typ.startswith("ooxml-") else _LO_GEOMETRIE.get(typ)
    if art is None and typ:
        leser.report.warn(f"Die Form „{typ}“ wird als Rechteck dargestellt.")
    return art or "rechteck"


def _einfach(leser, node: ET.Element, art_form: str | None = None) -> dict | None:
    """Eine einzelne Form (Rechteck, Ellipse, Standardform, Linie) oder ein Textrahmen als Wörterbuch des Modells; ``None``, wenn sie sich nicht abbilden lässt."""
    t = node.tag
    w = _werte(leser, node)
    freiform = None
    breite, hoehe = _px(node.get(_q("svg:width")), 0.0), _px(node.get(_q("svg:height")), 0.0)
    alt_el = node.find(_q("svg:desc"))
    alt = (alt_el.text or "").strip() if alt_el is not None else ""
    flips: dict = {}
    if t == _q("draw:line"):
        x1, y1, x2, y2 = (_px(node.get(_q(f"svg:{k}")), 0.0) for k in ("x1", "y1", "x2", "y2"))
        breite, hoehe = abs(x2 - x1), abs(y2 - y1)
        if (x2 - x1) * (y2 - y1) < 0:
            flips["flipV"] = True
        form, text, fmt = "linie", "", {}
    elif t == _q("draw:frame") and node.find(_q("draw:text-box")) is not None:
        form, text, fmt = None, _text(node.find(_q("draw:text-box"))), _textformat(leser, node)
    elif t in (_q("draw:polygon"), _q("draw:polyline"), _q("draw:path")):
        ops, offen = _pfad_aus_odt(node)
        if not ops:
            return None
        freiform = (ops, offen)
        form, text, fmt = "freiform", _text(node), _textformat(leser, node)
    elif t in (_q("draw:custom-shape"), _q("draw:rect"), _q("draw:ellipse")):
        form = "ellipse" if t == _q("draw:ellipse") else "rechteck" if t == _q("draw:rect") else _geometrie(leser, node)
        text, fmt = _text(node), _textformat(leser, node)
    else:
        return None
    voll = fuellung(leser, w)
    linie = kontur(leser, w, form is not None) or (_rand_fo(w) if form is None else None)
    if form == "linie":
        linie = linie or {"farbe": "#000000", "b": 1.0, "art": "einfach"}
        voll = None
    angabe: dict = dict(flips)
    if voll is not None:
        angabe["fuell"] = voll
    if linie:
        angabe["rand"] = linie
    if alt:
        angabe["alt"] = alt
    farbe = (voll or {}).get("farbe", "") if voll else ""
    if form is None:                                                        # Textfeld
        innen = {"text": text, "schrift": fmt.get("schrift", "Liberation Sans"), "pt": fmt.get("pt", 11), "farbe": fmt.get("farbe", "#1f1f1f")}
        for k in ("fett", "kursiv"):
            if fmt.get(k):
                innen[k] = True
        pad = [round(_px(w.get(f"fo:padding-{s}") or w.get("fo:padding"), 0.0), 2) for s in ("left", "top", "right", "bottom")]
        if any(pad):
            innen["innen"] = pad
        angabe["daten"] = innen
        art = "textfeld"
    else:
        innen = {"form": form, "fuell": farbe, "linie": (linie or {}).get("farbe", ""), "strich": (linie or {}).get("b", 0.0), "text": text}
        if text:
            innen.update({k: v for k, v in fmt.items() if k in ("schrift", "pt", "farbe", "fett", "kursiv")})
        if freiform:
            innen["pfad_norm"] = freiform[0]
            if freiform[1]:
                innen["offen"] = True
        marke = ("beide" if w.get("draw:marker-start") and w.get("draw:marker-end") else "anfang" if w.get("draw:marker-start") else "ende" if w.get("draw:marker-end") else "")
        if marke and form in ("linie", "freiform"):
            innen["pfeil"] = marke
        angabe["daten"] = innen
        art = "form"
    return {"art": art, "breite": breite, "hoehe": hoehe, "alt": alt, "daten": angabe}


def _sammeln(leser, knoten: ET.Element, aus: list) -> None:
    """Die Teile einer Gruppe (flach, auch aus verschachtelten Gruppen) mit Lage und Größe in Bildpunkten, wie sie im Dokument stehen."""
    for kind in knoten:
        if kind.tag == _q("draw:g"):
            _sammeln(leser, kind, aus)
            continue
        if kind.tag == _q("draw:frame") and kind.find(_q("draw:image")) is not None:
            daten = leser._bytes(kind.find(_q("draw:image")))
            if daten:
                aus.append({"art": "bild", "x": _px(kind.get(_q("svg:x")), 0.0), "y": _px(kind.get(_q("svg:y")), 0.0), "b": _px(kind.get(_q("svg:width")), 0.0),
                            "h": _px(kind.get(_q("svg:height")), 0.0), "ressource": leser.ressource_neu(daten), "angabe": {}})
            continue
        d = _einfach(leser, kind)
        if d is None:
            continue
        if kind.tag == _q("draw:line"):
            x = min(_px(kind.get(_q("svg:x1")), 0.0), _px(kind.get(_q("svg:x2")), 0.0))
            y = min(_px(kind.get(_q("svg:y1")), 0.0), _px(kind.get(_q("svg:y2")), 0.0))
        else:
            x, y = _px(kind.get(_q("svg:x")), 0.0), _px(kind.get(_q("svg:y")), 0.0)
        aus.append({"art": d["art"], "x": x, "y": y, "b": d["breite"], "h": d["hoehe"], "ressource": "", "angabe": d["daten"]})


def objekt_aus_odt(leser, node: ET.Element) -> dict | None:
    """Das Zeichenobjekt als ``{"art", "breite", "hoehe", "alt", "daten"[, "x", "y"]}``. Gruppen werden zur Art ``gruppe`` mit ihren Teilen (``elemente``); ``x``/``y`` ist dann die
    linke obere Ecke der Gruppe."""
    if node.tag == _q("draw:g"):
        teile: list = []
        _sammeln(leser, node, teile)
        if not teile:
            return None
        x0, y0 = min(t["x"] for t in teile), min(t["y"] for t in teile)
        x1, y1 = max(t["x"] + t["b"] for t in teile), max(t["y"] + t["h"] for t in teile)
        for t in teile:
            t["x"], t["y"] = t["x"] - x0, t["y"] - y0
        return {"art": "gruppe", "breite": x1 - x0, "hoehe": y1 - y0, "alt": "", "daten": {"elemente": teile}, "x": x0, "y": y0}
    return _einfach(leser, node)
