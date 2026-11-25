"""Füllungen und Linien von DrawingML-Formen (``a:spPr``): Farbe, Verlauf, Muster und Bild — Qt-frei, für Lesen und Schreiben von DOCX.

Das Modell kennt eine Füllung als Wörterbuch ``{"art": "farbe" | "graduell" | "muster" | "textur" | "bild", "farbe": "#rrggbb", …}``:
* ``graduell``: ``stops`` = [[Stelle 0…1, "#rrggbb"], …] und ``winkel`` (Grad, 0 = von links nach rechts, 90 = von oben nach unten); ``hell``/``dunkel`` sind erster und letzter Farbwert;
* ``muster``: ``key`` (Schlüssel aus ``core/document/musterschluessel.py``), ``farbe`` = Musterfarbe, ``grund`` = Hintergrundfarbe;
* ``bild``: ``n`` = Name der Bildressource des Dokuments.
Farben aus dem Farbschema (``a:schemeClr``) werden mit den Werten des Dokumentdesigns (oder den Standardwerten von Office) in feste Farben umgerechnet.
"""
from __future__ import annotations

import colorsys

from lunivo_writer.core.document.musterschluessel import patt_von_schluessel, schluessel_von_patt

_A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
_R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
EMU_JE_PX = 9525.0

THEMA_STANDARD = {"dk1": "000000", "lt1": "FFFFFF", "dk2": "44546A", "lt2": "E7E6E6", "accent1": "4472C4", "accent2": "ED7D31", "accent3": "A5A5A5",
                  "accent4": "FFC000", "accent5": "5B9BD5", "accent6": "70AD47", "hlink": "0563C1", "folHlink": "954F72"}
_THEMA_ALIAS = {"tx1": "dk1", "bg1": "lt1", "tx2": "dk2", "bg2": "lt2", "dark1": "dk1", "light1": "lt1", "dark2": "dk2", "light2": "lt2"}
_VORGABEFARBEN = {"black": "000000", "white": "FFFFFF", "red": "FF0000", "green": "008000", "blue": "0000FF", "yellow": "FFFF00", "gray": "808080", "grey": "808080",
                  "orange": "FFA500", "purple": "800080", "cyan": "00FFFF", "magenta": "FF00FF", "lime": "00FF00", "navy": "000080", "silver": "C0C0C0", "maroon": "800000",
                  "teal": "008080", "olive": "808000", "brown": "A52A2A", "pink": "FFC0CB", "darkBlue": "00008B", "darkRed": "8B0000", "darkGreen": "006400",
                  "lightGray": "D3D3D3", "lightGrey": "D3D3D3", "darkGray": "A9A9A9", "darkGrey": "A9A9A9", "ltGray": "D3D3D3", "dkGray": "A9A9A9"}
_LINIENART = {"solid": "einfach", "dot": "gepunktet", "sysDot": "gepunktet", "sysDash": "fein_gestrichelt", "dash": "gestrichelt", "lgDash": "gestrichelt",
              "dashDot": "strichpunkt", "lgDashDot": "strichpunkt", "sysDashDot": "strichpunkt", "lgDashDotDot": "strichpunktpunkt", "sysDashDotDot": "strichpunktpunkt"}
_LINIENART_AUS = {"gepunktet": "sysDot", "fein_gestrichelt": "sysDash", "gestrichelt": "dash", "strichpunkt": "dashDot", "strichpunktpunkt": "lgDashDotDot"}


def thema_lesen(wurzel) -> dict:
    """Die Farben des Farbschemas (``a:clrScheme``) einer Designdatei (``theme1.xml``) als ``{"accent1": "4472C4", …}``; fehlt etwas, gelten die Office-Standardwerte."""
    farben = dict(THEMA_STANDARD)
    schema = wurzel.find(f".//{_A}clrScheme") if wurzel is not None else None
    if schema is not None:
        for e in schema:
            name = e.tag.rsplit("}", 1)[-1]
            c = e.find(f"{_A}srgbClr")
            if c is not None and c.get("val"):
                farben[name] = c.get("val").upper()
            else:
                s = e.find(f"{_A}sysClr")
                if s is not None and s.get("lastClr"):
                    farben[name] = s.get("lastClr").upper()
    return farben


def _anpassen(hexfarbe: str, kind) -> str:
    """Farbänderungen (``lumMod``, ``lumOff``, ``tint``, ``shade``) auf eine Farbe anwenden."""
    r, g, b = (int(hexfarbe[i:i + 2], 16) / 255 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    for m in kind:
        n = m.tag.rsplit("}", 1)[-1]
        try:
            w = int(m.get("val") or 0) / 100000.0
        except ValueError:
            continue
        if n == "lumMod":
            l = min(1.0, l * w)
        elif n == "lumOff":
            l = min(1.0, l + w)
        elif n == "satMod":
            s = min(1.0, s * w)
        elif n == "tint":
            l = l * w + (1 - w)
        elif n == "shade":
            l = l * w
    r, g, b = colorsys.hls_to_rgb(h, max(0.0, min(1.0, l)), s)
    return "{:02X}{:02X}{:02X}".format(round(r * 255), round(g * 255), round(b * 255))


def farbe_aus(el, thema: dict | None = None) -> str:
    """Die Farbe eines Farbelements (``a:srgbClr``, ``a:schemeClr``, ``a:sysClr``, ``a:prstClr``) als „#rrggbb“; leer, wenn sie sich nicht bestimmen lässt."""
    if el is None:
        return ""
    thema = thema or THEMA_STANDARD
    for kind in el:
        n = kind.tag.rsplit("}", 1)[-1]
        wert = ""
        if n == "srgbClr":
            wert = (kind.get("val") or "").upper()
        elif n == "schemeClr":
            name = kind.get("val") or ""
            wert = thema.get(_THEMA_ALIAS.get(name, name), "")
        elif n == "sysClr":
            wert = (kind.get("lastClr") or {"windowText": "000000", "window": "FFFFFF"}.get(kind.get("val") or "", "")).upper()
        elif n == "prstClr":
            wert = _VORGABEFARBEN.get(kind.get("val") or "", "")
        if len(wert) == 6:
            try:
                rgb = "#" + _anpassen(wert, kind).lower()
            except ValueError:
                rgb = "#" + wert.lower()
            alpha = kind.find(f"{_A}alpha")                                        # Deckkraft in Hunderttausendstel: unter 100 % als Alphawert („#rrggbbaa“)
            if alpha is not None and alpha.get("val"):
                try:
                    anteil = max(0.0, min(1.0, int(alpha.get("val")) / 100000.0))
                except ValueError:
                    anteil = 1.0
                if anteil < 1.0:
                    rgb += "%02x" % round(anteil * 255)
            return rgb
    return ""


def fuellung_lesen(sp, thema: dict | None = None, bild_holen=None) -> dict | None:
    """Die Füllung von ``a:spPr`` als Wörterbuch; ``None`` ohne Füllungsangabe, ``{}`` bei ausdrücklich keiner Füllung. ``bild_holen(rId)`` → Name der Ressource oder ``None``."""
    if sp is None:
        return None
    if sp.find(f"{_A}noFill") is not None:
        return {}
    solid = sp.find(f"{_A}solidFill")
    if solid is not None:
        farbe = farbe_aus(solid, thema)
        return {"art": "farbe", "farbe": farbe} if farbe else None
    grad = sp.find(f"{_A}gradFill")
    if grad is not None:
        stops = []
        for gs in grad.findall(f"{_A}gsLst/{_A}gs"):
            farbe = farbe_aus(gs, thema)
            if farbe:
                stops.append([int(gs.get("pos") or 0) / 100000.0, farbe])
        if len(stops) < 2:
            return {"art": "farbe", "farbe": stops[0][1]} if stops else None
        stops.sort(key=lambda s: s[0])
        lin = grad.find(f"{_A}lin")
        winkel = int(lin.get("ang") or 0) / 60000.0 if lin is not None else 90.0
        return {"art": "graduell", "farbe": stops[0][1], "hell": stops[0][1], "dunkel": stops[-1][1], "stops": stops, "winkel": winkel}
    patt = sp.find(f"{_A}pattFill")
    if patt is not None:
        vorn, hinten = farbe_aus(patt.find(f"{_A}fgClr"), thema) or "#000000", farbe_aus(patt.find(f"{_A}bgClr"), thema) or "#ffffff"
        return {"art": "muster", "farbe": vorn, "key": schluessel_von_patt(patt.get("prst")), "grund": hinten}
    blip = sp.find(f"{_A}blipFill") if sp.find(f"{_A}blipFill") is not None else sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}blipFill")
    if blip is not None:
        b = blip.find(f"{_A}blip")
        rid = b.get(_R + "embed") if b is not None else None
        name = bild_holen(rid) if rid and bild_holen else None
        return {"art": "bild", "farbe": "", "n": name} if name else None
    return None


def linie_lesen(sp, thema: dict | None = None) -> dict | None:
    """Die Kontur von ``a:spPr`` als ``{"farbe", "b" (Bildpunkte), "art"}``; ``None``, wenn keine Kontur angegeben ist oder sie fehlt."""
    ln = sp.find(f"{_A}ln") if sp is not None else None
    if ln is None or ln.find(f"{_A}noFill") is not None:
        return None
    farbe = farbe_aus(ln.find(f"{_A}solidFill"), thema) or "#000000"
    dash = ln.find(f"{_A}prstDash")
    return {"farbe": farbe, "b": int(ln.get("w") or 9525) / EMU_JE_PX, "art": _LINIENART.get(dash.get("val") if dash is not None else "solid", "einfach")}


def _hex(farbe: str) -> str | None:
    return farbe[1:7].upper() if isinstance(farbe, str) and len(farbe) in (7, 9) and farbe.startswith("#") else None


def _clr(farbe) -> str:
    """Das Farbelement für „#rrggbb“ oder „#rrggbbaa“ (mit ``a:alpha``); leer bei ungültiger Farbe."""
    h = _hex(farbe)
    if not h:
        return ""
    if len(farbe) == 9:
        try:
            return f'<a:srgbClr val="{h}"><a:alpha val="{round(int(farbe[7:9], 16) / 255 * 100000)}"/></a:srgbClr>'
        except ValueError:
            pass
    return f'<a:srgbClr val="{h}"/>'


def fuellung_xml(fuell, bild_rid=None) -> str:
    """Das Füllungselement (``a:solidFill`` …) für ``a:spPr``; ``fuell`` = Wörterbuch oder „#rrggbb“; ``bild_rid(name)`` → ``rId`` des Bildes im Dokument oder ``None``."""
    if isinstance(fuell, str):
        fuell = {"art": "farbe", "farbe": fuell} if fuell else {}
    if not fuell:
        return "<a:noFill/>"
    art = fuell.get("art", "farbe")
    farbe = fuell.get("farbe", "")
    einfach = f"<a:solidFill>{_clr(farbe)}</a:solidFill>" if _clr(farbe) else "<a:noFill/>"
    if art in ("farbe", "verlauf"):
        return einfach
    if art == "graduell":
        stops = fuell.get("stops") or [[0.0, fuell.get("hell", farbe)], [1.0, fuell.get("dunkel", "#ffffff")]]
        gs = "".join(f'<a:gs pos="{int(round(float(p) * 100000))}">{_clr(c)}</a:gs>' for p, c in stops if _clr(c))
        if gs.count("<a:gs ") < 2:
            return einfach
        return f'<a:gradFill rotWithShape="1"><a:gsLst>{gs}</a:gsLst><a:lin ang="{int(round(float(fuell.get("winkel", 90)) * 60000)) % 21600000}" scaled="0"/></a:gradFill>'
    if art == "muster":
        key = str(fuell.get("key") or "rein")
        if key == "rein":
            return einfach
        return (f'<a:pattFill prst="{patt_von_schluessel(key)}"><a:fgClr>{_clr(farbe) or _clr("#000000")}</a:fgClr>'
                f'<a:bgClr>{_clr(fuell.get("grund") or "#ffffff") or _clr("#ffffff")}</a:bgClr></a:pattFill>')
    if art == "bild" and bild_rid is not None:
        rid = bild_rid(fuell.get("n"))
        if rid:
            return f'<a:blipFill rotWithShape="1"><a:blip xmlns:r="{_R[1:-1]}" r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></a:blipFill>'
    return einfach


def linie_xml(linie: str, strich: float, art: str = "einfach", pfeil: str = "") -> str:
    if not _clr(linie):
        return "<a:ln><a:noFill/></a:ln>"
    dash = f'<a:prstDash val="{_LINIENART_AUS[art]}"/>' if art in _LINIENART_AUS else ""
    kopf = '<a:headEnd type="triangle"/>' if pfeil in ("anfang", "beide") else ""
    ende = '<a:tailEnd type="triangle"/>' if pfeil in ("ende", "beide") else ""
    return f'<a:ln w="{int(round(float(strich or 1.0) * EMU_JE_PX))}"><a:solidFill>{_clr(linie)}</a:solidFill>{dash}{kopf}{ende}</a:ln>'


def pfeil_lesen(sp) -> str:
    """Pfeilspitzen an den Enden der Linie: ``"anfang"``, ``"ende"``, ``"beide"`` oder leer."""
    ln = sp.find(f"{_A}ln") if sp is not None else None
    if ln is None:
        return ""
    kopf = ln.find(f"{_A}headEnd")
    ende = ln.find(f"{_A}tailEnd")
    a = kopf is not None and kopf.get("type") not in (None, "none")
    e = ende is not None and ende.get("type") not in (None, "none")
    return "beide" if a and e else "anfang" if a else "ende" if e else ""


def schatten_lesen(sp, thema: dict | None = None) -> dict | None:
    """Der äußere Schatten von ``a:effectLst`` als ``{"farbe", "blur", "dx", "dy", "deckkraft"}`` (Bildpunkte); ``None`` ohne Schatten."""
    sh = sp.find(f"{_A}effectLst/{_A}outerShdw") if sp is not None else None
    if sh is None:
        return None
    import math
    farbe = farbe_aus(sh, thema) or "#000000"
    deckkraft = int(farbe[7:9], 16) / 255 if len(farbe) == 9 else 1.0
    blur = int(sh.get("blurRad") or 0) / EMU_JE_PX
    abstand = int(sh.get("dist") or 0) / EMU_JE_PX
    winkel = math.radians(int(sh.get("dir") or 0) / 60000.0)
    return {"farbe": farbe[:7], "blur": blur, "dx": abstand * math.cos(winkel), "dy": abstand * math.sin(winkel), "deckkraft": deckkraft}


def schatten_xml(s: dict) -> str:
    import math
    farbe = _hex(s.get("farbe", "#000000")) or "000000"
    abstand = math.hypot(float(s.get("dx", 0)), float(s.get("dy", 0))) * EMU_JE_PX
    winkel = int(round(math.degrees(math.atan2(float(s.get("dy", 0)), float(s.get("dx", 0)))) * 60000)) % 21600000
    return (f'<a:effectLst><a:outerShdw blurRad="{int(float(s.get("blur", 0)) * EMU_JE_PX)}" dist="{int(abstand)}" dir="{winkel}" algn="ctr" rotWithShape="0">'
            f'<a:srgbClr val="{farbe}"><a:alpha val="{int(float(s.get("deckkraft", 0.4)) * 100000)}"/></a:srgbClr></a:outerShdw></a:effectLst>')


def custgeom_lesen(sp) -> dict | None:
    """Freie Geometrie (``a:custGeom``) als normalisierte Pfadanweisungen (0…1 der Zeichnungsgröße): ``{"ops": [...], "offen": bool}``; ``None``, wenn keine vorhanden ist."""
    cg = sp.find(f"{_A}custGeom") if sp is not None else None
    if cg is None:
        return None
    ops: list = []
    geschlossen = False
    for pfad in cg.findall(f"{_A}pathLst/{_A}path"):
        w, h = float(pfad.get("w") or 0), float(pfad.get("h") or 0)
        punkte = [(float(p.get("x")), float(p.get("y"))) for p in pfad.iter(f"{_A}pt") if p.get("x") is not None]
        if not w:
            w = max((x for x, _y in punkte), default=1.0) or 1.0
        if not h:
            h = max((y for _x, y in punkte), default=1.0) or 1.0

        def pt(e):
            return float(e.get("x")) / w, float(e.get("y")) / h
        for k in pfad:
            n = k.tag.rsplit("}", 1)[-1]
            pts = [pt(p) for p in k.findall(f"{_A}pt")]
            if n == "moveTo" and pts:
                ops.append(["M", *pts[0]])
            elif n == "lnTo" and pts:
                ops.append(["L", *pts[0]])
            elif n == "cubicBezTo" and len(pts) == 3:
                ops.append(["C", *pts[0], *pts[1], *pts[2]])
            elif n == "quadBezTo" and len(pts) == 2:
                ops.append(["Q", *pts[0], *pts[1]])
            elif n == "close":
                ops.append(["Z"])
                geschlossen = True
    return {"ops": ops, "offen": not geschlossen} if ops else None


def custgeom_xml(ops: list) -> str:
    """Normalisierte Pfadanweisungen als ``a:custGeom`` (Pfad im 100000er-Raster)."""
    def z(v):
        return str(int(round(float(v) * 100000)))
    teile = []
    for o in ops:
        if o[0] in ("M", "L"):
            teile.append(f'<a:{"moveTo" if o[0] == "M" else "lnTo"}><a:pt x="{z(o[1])}" y="{z(o[2])}"/></a:{"moveTo" if o[0] == "M" else "lnTo"}>')
        elif o[0] == "C":
            teile.append("<a:cubicBezTo>" + "".join(f'<a:pt x="{z(o[i])}" y="{z(o[i + 1])}"/>' for i in (1, 3, 5)) + "</a:cubicBezTo>")
        elif o[0] == "Q":
            teile.append("<a:quadBezTo>" + "".join(f'<a:pt x="{z(o[i])}" y="{z(o[i + 1])}"/>' for i in (1, 3)) + "</a:quadBezTo>")
        elif o[0] == "Z":
            teile.append("<a:close/>")
    return ('<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/>'
            f'<a:pathLst><a:path w="100000" h="100000">{"".join(teile)}</a:path></a:pathLst></a:custGeom>')
