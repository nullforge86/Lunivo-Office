"""Texteffekte in DOCX (Erweiterung ``w14``: ``textOutline``, ``textFill``, ``glow``, ``shadow``, ``reflection``, ``props3d``), Qt-frei.

Ein Effekt ist ein Wörterbuch wie ``texteffekt.EFFEKT`` (Füllung, Kontur) mit den Teilen aus ``textfx`` (Schatten, Spiegelung, Leuchten, 3D). ``in_rpr`` schreibt ihn an ein
``w:rPr``, ``aus_rpr`` liest ihn von dort."""
from __future__ import annotations

SCHWARZ, WEISS = "#000000", "#ffffff"
EFFEKT = {"fuell": "farbe", "farbe": "", "transparenz": 0, "kontur": False, "kontur_farbe": SCHWARZ, "kontur_breite": 0.75, "kontur_art": "einfach"}
KONTUR_DASH = {"einfach": "solid", "gepunktet": "sysDot", "fein": "sysDash", "gestrichelt": "dash", "lang": "lgDash", "strichpunkt": "dashDot",
               "lang_strichpunkt": "lgDashDot", "strichpunktpunkt": "lgDashDotDot"}


# ---- DOCX (DOCX-2010-Erweiterung w14:textOutline und w14:textFill) ----------------------------------------------------------
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
_DASH = KONTUR_DASH


def _q(name: str) -> str:
    return f"{{{W14}}}{name}"


_MATERIAL = {"matt": "matte", "plastik": "plastic", "metall": "metal", "dunkel": "dkEdge", "weich": "softEdge", "hell": "flat"}
_FORM = {"doppelt": "dbl", "dick_duenn": "thickThin", "duenn_dick": "thinThick", "dreifach": "tri"}
_EMU_PT = 12700


def _farbelement(eltern, hexwert: str, alpha_pct: float | None = None):
    from lxml import etree
    c = etree.SubElement(eltern, _q("srgbClr")); c.set(_q("val"), (hexwert or SCHWARZ)[1:].upper())
    if alpha_pct is not None and alpha_pct < 100:
        etree.SubElement(c, _q("alpha")).set(_q("val"), str(int(round(alpha_pct * 1000))))
    return c


def _verlauf_element(eltern, v: dict) -> None:
    from lxml import etree
    g = etree.SubElement(eltern, _q("gradFill"))
    lst = etree.SubElement(g, _q("gsLst"))
    for pos, farbe in ((0, v.get("farbe1", SCHWARZ)), (100000, v.get("farbe2", WEISS))):
        gs = etree.SubElement(lst, _q("gs")); gs.set(_q("pos"), str(pos)); _farbelement(gs, farbe)
    lin = etree.SubElement(g, _q("lin")); lin.set(_q("ang"), str(int(round(v.get("winkel", 90) * 60000)))); lin.set(_q("scaled"), "0")


def _rpr_leuchten(rpr, g: dict | None) -> None:
    from lxml import etree
    if g and g.get("groesse", 0) > 0:
        e = etree.SubElement(rpr, _q("glow")); e.set(_q("rad"), str(int(g["groesse"] * _EMU_PT)))
        _farbelement(e, g.get("farbe", Farbe.BLAU), 100 - g.get("transparenz", 60))


def _rpr_schatten(rpr, s: dict | None) -> None:
    from lxml import etree
    if not s or s.get("art") == "innen":                                    # Innenschatten kennt DOCX nicht
        return
    e = etree.SubElement(rpr, _q("shadow"))
    e.set(_q("blurRad"), str(int(s.get("weich", 0) * _EMU_PT))); e.set(_q("dist"), str(int(s.get("abstand", 0) * _EMU_PT)))
    e.set(_q("dir"), str(int(round(s.get("winkel", 45) * 60000)))); e.set(_q("sx"), str(int(s.get("groesse", 100) * 1000)))
    persp = s.get("art") == "persp"
    e.set(_q("sy"), str(int(s.get("groesse", 100) * 1000 * (-0.4 if persp else 1)))); e.set(_q("kx"), "0"); e.set(_q("ky"), "0")
    e.set(_q("algn"), "b" if persp else "ctr")
    _farbelement(e, s.get("farbe", SCHWARZ), 100 - s.get("transparenz", 50))


def _rpr_reflektion(rpr, r: dict | None) -> None:
    from lxml import etree
    if not r:
        return
    e = etree.SubElement(rpr, _q("reflection"))
    e.set(_q("blurRad"), str(int(r.get("weich", 0) * _EMU_PT))); e.set(_q("stA"), str(int((100 - r.get("transparenz", 50)) * 1000)))
    e.set(_q("stPos"), "0"); e.set(_q("endA"), "300"); e.set(_q("endPos"), str(int(r.get("groesse", 50) * 1000)))
    e.set(_q("dist"), str(int(r.get("abstand", 0) * _EMU_PT))); e.set(_q("dir"), "5400000"); e.set(_q("fadeDir"), "5400000")
    e.set(_q("sx"), "100000"); e.set(_q("sy"), "-100000"); e.set(_q("kx"), "0"); e.set(_q("ky"), "0"); e.set(_q("algn"), "bl")


def _rpr_kontur(rpr, w: dict) -> None:
    from lxml import etree
    if not w["kontur"]:
        return
    o = etree.SubElement(rpr, _q("textOutline"))
    o.set(_q("w"), str(int(round(w["kontur_breite"] * _EMU_PT)))); o.set(_q("cap"), "flat"); o.set(_q("cmpd"), _FORM.get(w.get("kontur_form"), "sng")); o.set(_q("algn"), "ctr")
    if "kontur_verlauf" in w:
        _verlauf_element(o, w["kontur_verlauf"])
    else:
        _farbelement(etree.SubElement(o, _q("solidFill")), w["kontur_farbe"])
    etree.SubElement(o, _q("prstDash")).set(_q("val"), _DASH.get(w["kontur_art"], "solid"))
    etree.SubElement(o, _q("round"))


def _rpr_fuellung(rpr, w: dict) -> None:
    """Textfüllung: keine, Verlauf oder (bei Transparenz) einfarbig mit Deckkraft."""
    from lxml import etree
    if w["fuell"] == "keine":
        etree.SubElement(etree.SubElement(rpr, _q("textFill")), _q("noFill"))
    elif w["fuell"] == "verlauf" and "verlauf" in w:
        _verlauf_element(etree.SubElement(rpr, _q("textFill")), w["verlauf"])
    elif w["transparenz"]:
        c = _farbelement(etree.SubElement(etree.SubElement(rpr, _q("textFill")), _q("solidFill")), w["farbe"] or SCHWARZ)
        etree.SubElement(c, _q("alpha")).set(_q("val"), str(int(round((100 - w["transparenz"]) * 1000))))


def _rpr_3d(rpr, d: dict | None) -> None:
    from lxml import etree
    if d and d.get("tiefe", 0) > 0:
        e = etree.SubElement(rpr, _q("props3d")); e.set(_q("extrusionH"), str(int(d["tiefe"] * _EMU_PT)))
        e.set(_q("contourW"), str(int(d.get("kontur", 0) * _EMU_PT))); e.set(_q("prstMaterial"), _MATERIAL.get(d.get("material", "matt"), "matte"))
        _farbelement(etree.SubElement(e, _q("extrusionClr")), d.get("tiefe_farbe", Farbe.GRAU))
        _farbelement(etree.SubElement(e, _q("contourClr")), d.get("kontur_farbe", Farbe.TINTE))


def in_rpr(rpr, w: dict) -> None:
    """Die Texteffekte ``w`` (siehe ``aus_zeichen``) als w14-Elemente an ``w:rPr`` schreiben, in der Reihenfolge des Schemas (nichts, wenn es keinen Effekt gibt)."""
    _rpr_leuchten(rpr, w.get("leuchten"))
    _rpr_schatten(rpr, w.get("schatten"))
    _rpr_reflektion(rpr, w.get("reflektion"))
    _rpr_kontur(rpr, w)
    _rpr_fuellung(rpr, w)
    _rpr_3d(rpr, w.get("d3"))


def _wert(e, name: str, vorgabe: float = 0.0) -> float:
    try:
        return float(e.get(_q(name)))
    except (TypeError, ValueError):
        return vorgabe


def _farbe_aus(e) -> tuple[str, float]:
    """(Farbe, Transparenz in %) eines Elements mit w14:srgbClr darunter."""
    c = e.find(_q("srgbClr")) if e is not None else None
    if c is None:
        return SCHWARZ, 0.0
    a = c.find(_q("alpha"))
    return "#" + (c.get(_q("val")) or "000000"), (100 - _wert(a, "val", 100000) / 1000) if a is not None else 0.0


def _verlauf_aus(g) -> dict:
    stopps = [(_wert(gs, "pos"), "#" + ((gs.find(_q("srgbClr")).get(_q("val"))) if gs.find(_q("srgbClr")) is not None else "000000")) for gs in g.iter(_q("gs"))]
    stopps.sort()
    lin = g.find(_q("lin"))
    return {"farbe1": stopps[0][1] if stopps else SCHWARZ, "farbe2": stopps[-1][1] if stopps else WEISS,
            "winkel": round(_wert(lin, "ang", 5400000) / 60000) % 360 if lin is not None else 90}


def _kontur_aus(rpr, w: dict) -> None:
    o = rpr.find(_q("textOutline"))
    if o is None:
        return
    w["kontur"] = True
    g = o.find(_q("gradFill"))
    farbe = o.find(f"{_q('solidFill')}/{_q('srgbClr')}")
    dash = o.find(_q("prstDash"))
    w["kontur_art"] = next((k for k, v in _DASH.items() if dash is not None and v == dash.get(_q("val"))), "einfach")
    w["kontur_breite"] = max(0.1, _wert(o, "w", 9525) / _EMU_PT)
    w["kontur_farbe"] = "#" + (farbe.get(_q("val")) if farbe is not None else "000000")
    if g is not None:
        w["kontur_verlauf"] = _verlauf_aus(g)
    form = next((k for k, v in _FORM.items() if v == o.get(_q("cmpd"))), None)
    if form:
        w["kontur_form"] = form


def _fuellung_aus(rpr, w: dict) -> None:
    f = rpr.find(_q("textFill"))
    if f is None:
        return
    if f.find(_q("noFill")) is not None:
        w["fuell"] = "keine"
    elif f.find(_q("gradFill")) is not None:
        w["fuell"] = "verlauf"; w["verlauf"] = _verlauf_aus(f.find(_q("gradFill")))
    else:
        farbe, trans = _farbe_aus(f.find(_q("solidFill")))
        w["farbe"] = farbe; w["transparenz"] = int(round(trans))


def _leuchten_schatten_aus(rpr, w: dict) -> None:
    g = rpr.find(_q("glow"))
    if g is not None:
        farbe, trans = _farbe_aus(g)
        w["leuchten"] = {"farbe": farbe, "groesse": _wert(g, "rad") / _EMU_PT, "transparenz": trans}
    s = rpr.find(_q("shadow"))
    if s is not None:
        farbe, trans = _farbe_aus(s)
        w["schatten"] = {"art": "persp" if _wert(s, "sy", 100000) < 0 else "aussen", "farbe": farbe, "transparenz": trans,
                         "groesse": abs(_wert(s, "sx", 100000)) / 1000, "weich": _wert(s, "blurRad") / _EMU_PT, "abstand": _wert(s, "dist") / _EMU_PT,
                         "winkel": round(_wert(s, "dir") / 60000) % 360}


def _reflektion_3d_aus(rpr, w: dict) -> None:
    r = rpr.find(_q("reflection"))
    if r is not None:
        w["reflektion"] = {"groesse": _wert(r, "endPos", 50000) / 1000, "transparenz": 100 - _wert(r, "stA", 50000) / 1000, "weich": _wert(r, "blurRad") / _EMU_PT,
                           "abstand": _wert(r, "dist") / _EMU_PT}
    d = rpr.find(_q("props3d"))
    if d is not None and _wert(d, "extrusionH") > 0:
        tf, _t = _farbe_aus(d.find(_q("extrusionClr"))); kf, _t = _farbe_aus(d.find(_q("contourClr")))
        w["d3"] = {"tiefe": _wert(d, "extrusionH") / _EMU_PT, "tiefe_farbe": tf, "kontur": _wert(d, "contourW") / _EMU_PT, "kontur_farbe": kf,
                   "material": next((k for k, v in _MATERIAL.items() if v == d.get(_q("prstMaterial"))), "matt"), "beleuchtung": "neutral", "winkel": 0}


def aus_rpr(rpr) -> dict | None:
    """Das Gegenstück zu ``in_rpr``: die w14-Elemente von ``w:rPr`` als Effekt lesen; ``None``, wenn es keinen Effekt gibt."""
    if rpr is None:
        return None
    w: dict = dict(EFFEKT)
    _kontur_aus(rpr, w)
    _fuellung_aus(rpr, w)
    _leuchten_schatten_aus(rpr, w)
    _reflektion_3d_aus(rpr, w)
    return None if w == dict(EFFEKT) else w
