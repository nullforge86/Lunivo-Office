"""Bildeffekte (Schatten, Leuchten, Spiegelung, weiche Kanten) als DrawingML ``a:effectLst`` — lesen und schreiben, ohne Qt.

Die Effekte eines Bildes stehen im Modell als ``daten["fx"]``: ``schatten`` (farbe, transparenz %, groesse %, weich pt, abstand pt, winkel Grad), ``leuchten`` (farbe, groesse pt,
transparenz %), ``reflektion`` (groesse %, transparenz %, weich pt, abstand pt) und ``weich`` (radius pt)."""
from __future__ import annotations

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
EMU_PT = 12700


def _farbe(hexwert: str, transparenz: float = 0.0) -> str:
    wert = (hexwert or "#000000").lstrip("#").upper()[:6]
    alpha = round((100.0 - float(transparenz)) * 1000)
    return f'<a:srgbClr val="{wert}">' + (f'<a:alpha val="{alpha}"/>' if alpha < 100000 else "") + "</a:srgbClr>"


def effekte_zu_xml(fx: dict | None) -> str | None:
    """Das ``a:effectLst``-Element (als XML-Text mit Namensraum) für die Effekte; ``None``, wenn es keine gibt. Die Reihenfolge folgt dem Schema (glow, outerShdw, reflection, softEdge)."""
    if not isinstance(fx, dict) or not any(k in fx for k in ("schatten", "leuchten", "reflektion", "weich")):
        return None
    teile: list[str] = []
    g = fx.get("leuchten")
    if isinstance(g, dict):
        teile.append(f'<a:glow rad="{round(float(g.get("groesse", 5.0)) * EMU_PT)}">{_farbe(g.get("farbe", "#ffc000"), g.get("transparenz", 60.0))}</a:glow>')
    s = fx.get("schatten")
    if isinstance(s, dict):
        gr = round(float(s.get("groesse", 100.0)) * 1000)
        teile.append(f'<a:outerShdw blurRad="{round(float(s.get("weich", 4.0)) * EMU_PT)}" dist="{round(float(s.get("abstand", 3.0)) * EMU_PT)}" '
                     f'dir="{round(float(s.get("winkel", 45.0)) * 60000)}" sx="{gr}" sy="{gr}" algn="ctr" rotWithShape="0">{_farbe(s.get("farbe", "#000000"), s.get("transparenz", 60.0))}</a:outerShdw>')
    r = fx.get("reflektion")
    if isinstance(r, dict):
        teile.append(f'<a:reflection blurRad="{round(float(r.get("weich", 0.5)) * EMU_PT)}" stA="{round((100.0 - float(r.get("transparenz", 50.0))) * 1000)}" endA="0" '
                     f'endPos="{round(float(r.get("groesse", 50.0)) * 1000)}" dist="{round(float(r.get("abstand", 0.0)) * EMU_PT)}" dir="5400000" sy="-100000" algn="bl" rotWithShape="0"/>')
    w = fx.get("weich")
    if isinstance(w, dict):
        teile.append(f'<a:softEdge rad="{round(float(w.get("radius", 5.0)) * EMU_PT)}"/>')
    return f'<a:effectLst xmlns:a="{A}">' + "".join(teile) + "</a:effectLst>"


def _alpha_prozent(elem) -> float:
    a = elem.find(f"{{{A}}}srgbClr/{{{A}}}alpha")
    return 0.0 if a is None else 100.0 - float(a.get("val", "100000")) / 1000.0


def _wert(elem, name: str, vorgabe: float = 0.0) -> float:
    try:
        return float(elem.get(name))
    except (TypeError, ValueError):
        return vorgabe


def effekte_aus_element(liste) -> dict:
    """Die Effekte eines ``a:effectLst``-Elements als ``fx`` (nur, was darin steht)."""
    fx: dict = {}
    for kind in liste:
        name = kind.tag.rpartition("}")[2]
        farbe = kind.find(f"{{{A}}}srgbClr")
        hexfarbe = "#" + farbe.get("val").lower() if farbe is not None and farbe.get("val") else "#000000"
        if name == "glow":
            fx["leuchten"] = {"farbe": hexfarbe, "groesse": _wert(kind, "rad") / EMU_PT, "transparenz": _alpha_prozent(kind)}
        elif name == "outerShdw":
            fx["schatten"] = {"farbe": hexfarbe, "transparenz": _alpha_prozent(kind), "groesse": _wert(kind, "sx", 100000.0) / 1000.0, "weich": _wert(kind, "blurRad") / EMU_PT,
                              "abstand": _wert(kind, "dist") / EMU_PT, "winkel": _wert(kind, "dir") / 60000.0}
        elif name == "reflection":
            fx["reflektion"] = {"groesse": _wert(kind, "endPos", 50000.0) / 1000.0, "transparenz": 100.0 - _wert(kind, "stA", 50000.0) / 1000.0,
                                "weich": _wert(kind, "blurRad") / EMU_PT, "abstand": _wert(kind, "dist") / EMU_PT}
        elif name == "softEdge":
            fx["weich"] = {"radius": _wert(kind, "rad") / EMU_PT}
    return fx
