"""DOCX: Formen, Textfelder, Seitenrahmen, Absatzrahmen und Wasserzeichen zwischen XML und Dokumentmodell (ohne Qt).

Der native Leser und Schreiber (``docx_dokument_leser``, ``docx_modell_schreiber``) benutzen die Umwandlungen hier. Die Daten haben die Form, die der Renderer
(``core/rendering/objektrenderer.py``) schon liest:

* Form und Textfeld: ``FreiesObjekt``/``InlineObjekt`` mit ``daten`` = Angabe wie bei frei positionierten Bildern (``dreh``, ``flipH``, ``fuell``, ``rand``, ``alt`` …) und
  darin ``daten["daten"]`` mit den Parametern der Form (``form``, ``fuell``, ``linie``, ``strich``, ``text``) bzw. des Textfelds (``text``, ``schrift``, ``pt``, ``farbe``, ``innen``).
* Das Zeichnungselement der Datei bleibt zusätzlich als ``daten["docx_roh"]`` erhalten; der Schreiber setzt es mit Größe und Lage aus dem Modell wieder ein, so gehen
  Eigenschaften, die das Modell nicht kennt (Verläufe, Effekte, Textrichtung …), nicht verloren.
* Seitenrahmen: ``PageSettings.border``; Wasserzeichen: ``PageSettings.watermark``; Absatzrahmen: Absatzformat ``rahmen`` („Farbe|Breite pt|Art|Seiten|Abstände“)."""
from __future__ import annotations

from lxml import etree

from lunivo_writer.core.rendering.linien import STILE
from lunivo_writer.dienste.docx_erhalt import Beziehung, W, W_NS, als_text, hat_beziehung

NS = {
    "w": W_NS,
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "wps": "http://schemas.microsoft.com/office/word/2010/wordprocessingShape",
    "v": "urn:schemas-microsoft-com:vml",
    "o": "urn:schemas-microsoft-com:office:office",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
}
_WP, _A, _WPS = "{" + NS["wp"] + "}", "{" + NS["a"] + "}", "{" + NS["wps"] + "}"
EMU_JE_PX = 9525.0
FORM_URI = NS["wps"]
_VON_DOCX = {v[2]: k for k, v in STILE.items()}
_NACH_DOCX = {k: v[2] for k, v in STILE.items()}
_RAHMEN_SEITEN = (("top", "t"), ("bottom", "b"), ("left", "l"), ("right", "r"))

# Voreinstellung der Geometrie in DrawingML (``a:prstGeom``) ↔ Name der Form im Katalog des Programms (kleingeschrieben, wie der Renderer sie liest)
_GEOMETRIE = {"rect": "rechteck", "roundRect": "abgerundet", "ellipse": "ellipse", "line": "linie", "straightConnector1": "linie", "rightArrow": "pfeil",
              "triangle": "dreieck", "diamond": "raute", "hexagon": "sechseck", "pentagon": "fuenfeck", "octagon": "achteck", "star5": "stern", "heart": "herz",
              "parallelogram": "parallelogramm", "trapezoid": "trapez", "leftArrow": "pfeil_links", "upArrow": "pfeil_oben", "downArrow": "pfeil_unten", "cloud": "wolke"}
_GEOMETRIE_UMGEKEHRT = {v: k for k, v in _GEOMETRIE.items()}


def _x(el, pfad: str):
    return el.xpath(pfad, namespaces=NS)


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
# Absatzrahmen (w:pBdr)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def absatzrahmen_aus_xml(bdr) -> str | None:
    """``w:pBdr`` → Rahmenangabe des Absatzes („Farbe|Breite pt|Art|Seiten|oben,unten,links,rechts“). ``None``, wenn nichts sichtbar ist oder die Seiten verschiedene
    Linien haben (dann bleibt das Element als erhaltene Eigenschaft im Absatz)."""
    if bdr is None:
        return None
    da = []
    for name, kurz in _RAHMEN_SEITEN:
        e = bdr.find(W + name)
        if e is not None and e.get(W + "val", "nil") not in ("nil", "none"):
            da.append((kurz, e))
    if not da or any(_name(k) in ("between", "bar") for k in bdr):
        return None
    erste = da[0][1]
    merkmale = {(e.get(W + "val"), e.get(W + "sz"), e.get(W + "color")) for _k, e in da}
    if len(merkmale) != 1:
        return None
    farbe = (erste.get(W + "color") or "000000").lower()
    farbe = "#" + ("000000" if farbe == "auto" else farbe)
    try:
        breite = int(erste.get(W + "sz") or 8) / 8.0
    except ValueError:
        breite = 1.0
    art = _VON_DOCX.get(erste.get(W + "val") or "", "einfach")
    abst = {k: e.get(W + "space") for k, e in da}
    abstand = ",".join(str(int(abst.get(k) or 4)) for k in "tblr") if any(v not in (None, "4") for v in abst.values()) else ""
    return f"{farbe}|{breite:g}|{art}|{''.join(k for k, _e in da)}|{abstand}"


def absatzrahmen_zu_xml(text: str):
    """Rahmenangabe des Absatzes → ``w:pBdr``; ``None``, wenn die Angabe nicht lesbar ist."""
    from lunivo_writer.core.rendering.linien import rahmen_aus_text
    a = rahmen_aus_text(text)
    if a is None:
        return None
    farbe, breite, art, seiten, abstand = a
    bdr = etree.Element(W + "pBdr", nsmap={"w": W_NS})
    for name, kurz in _RAHMEN_SEITEN:
        if kurz not in seiten:
            continue
        e = etree.SubElement(bdr, W + name)
        e.set(W + "val", _NACH_DOCX.get(art, "single"))
        e.set(W + "sz", str(max(2, int(round(breite * 8)))))
        e.set(W + "space", str(int(round(abstand[("top", "bottom", "left", "right").index(name)] if abstand else 4))))
        e.set(W + "color", farbe.lstrip("#").upper() or "000000")
    return bdr if len(bdr) else None


def _name(e) -> str:
    return etree.QName(e).localname


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
# Seitenrahmen (w:pgBorders)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def seitenrahmen_aus_xml(pb, einstellungen) -> dict | None:
    """``w:pgBorders`` (und die Angaben dazu in ``settings.xml``) → ``PageSettings.border``. Haben die Seiten verschiedene Linien, steht das Element zusätzlich als ``docx_roh`` im
    Rahmen (der Schreiber nimmt dann das Original)."""
    if pb is None:
        return None
    da = [(kurz, pb.find(W + name)) for name, kurz in (("top", "t"), ("bottom", "b"), ("left", "l"), ("right", "r"))]
    da = [(k, e) for k, e in da if e is not None and e.get(W + "val", "nil") not in ("nil", "none")]
    if not da:
        return None
    if any(hat_beziehung(e) for _k, e in da):
        raise Beziehung("pgBorders")
    e = da[0][1]
    farbe = (e.get(W + "color") or "000000").lower()
    try:
        breite = int(e.get(W + "sz") or 8) / 8.0
        raum = int(e.get(W + "space") or 24)
    except ValueError:
        breite, raum = 1.0, 24
    border = {"seiten": "".join(k for k, _e in da) or "tblr", "farbe": "#" + ("000000" if farbe == "auto" else farbe), "breite_pt": breite,
              "art": _VON_DOCX.get(e.get(W + "val") or "", "einfach"), "abstand_mm": raum / 72 * 25.4}
    if e.get(W + "val") in ("stars", "hearts", "triangles", "gems", "zigZag"):
        border["kunst"] = e.get(W + "val")
    if pb.get(W + "offsetFrom") == "text":
        border["messen"] = "text"
    border["abstand"] = ",".join(str(int((pb.find(W + n).get(W + "space") if pb.find(W + n) is not None else None) or 0)) for n in ("top", "bottom", "left", "right"))
    border["vordergrund"] = pb.get(W + "zOrder", "front") != "back"
    if einstellungen is not None:
        border["kopf"] = einstellungen.find(W + "bordersDoNotSurroundHeader") is None
        border["fuss"] = einstellungen.find(W + "bordersDoNotSurroundFooter") is None
        border["ausrichten"] = einstellungen.find(W + "alignBordersAndEdges") is not None
    if len({(k2.get(W + "val"), k2.get(W + "sz"), k2.get(W + "color")) for _k, k2 in da}) > 1:
        border["docx_roh"] = als_text(pb)
    return border


def seitenrahmen_zu_xml(b: dict):
    """``PageSettings.border`` → ``w:pgBorders``."""
    from lunivo_writer.core.rendering.seitenrahmen import abstaende_pt
    if b.get("docx_roh"):
        from docx.oxml import parse_xml
        return parse_xml(b["docx_roh"])
    pb = etree.Element(W + "pgBorders", nsmap={"w": W_NS})
    pb.set(W + "offsetFrom", "text" if b.get("messen") == "text" else "page")
    pb.set(W + "zOrder", "front" if b.get("vordergrund", True) else "back")
    ab = dict(zip(("top", "bottom", "left", "right"), abstaende_pt(b)))
    for name, kurz in (("top", "t"), ("left", "l"), ("bottom", "b"), ("right", "r")):
        if kurz not in b.get("seiten", "tblr"):
            continue
        e = etree.SubElement(pb, W + name)
        e.set(W + "val", b.get("kunst") or _NACH_DOCX.get(b.get("art", "einfach"), "single"))
        e.set(W + "sz", str(max(2, int(round(float(b.get("breite_pt", 1.0)) * 8)))))
        e.set(W + "space", str(min(31, int(round(ab[name])))))
        e.set(W + "color", (b.get("farbe") or "#000000").lstrip("#").upper())
    return pb if len(pb) else None


def seitenrahmen_einstellungen(b: dict) -> dict:
    """Welche Elemente in ``settings.xml`` zum Seitenrahmen gehören: Name → an/aus."""
    return {"bordersDoNotSurroundHeader": not b.get("kopf", True), "bordersDoNotSurroundFooter": not b.get("fuss", True), "alignBordersAndEdges": bool(b.get("ausrichten"))}


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
# Wasserzeichen (VML-Textform „PowerPlusWaterMarkObject“ in der Kopfzeile)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
_VML_FARBEN = {"silver": "#c0c0c0", "gray": "#808080", "grey": "#808080", "black": "#000000", "white": "#ffffff", "red": "#ff0000", "blue": "#0000ff", "green": "#008000",
               "yellow": "#ffff00", "lightgray": "#d3d3d3", "lightgrey": "#d3d3d3"}


def ist_wasserzeichen(pict) -> bool:
    return any((s.get("id") or "").startswith("PowerPlusWaterMarkObject") for s in _x(pict, ".//v:shape"))


def wasserzeichen_aus_xml(pict) -> dict | None:
    """``w:pict`` mit einer Textform „PowerPlusWaterMarkObject“ → ``PageSettings.watermark``; ``None`` für Bild-Wasserzeichen und andere Formen."""
    for s in _x(pict, ".//v:shape"):
        if not (s.get("id") or "").startswith("PowerPlusWaterMarkObject"):
            continue
        tp = _x(s, "v:textpath")
        if not tp or tp[0].get("string") is None:
            return None
        stil = {}
        for teil in (s.get("style") or "").split(";"):
            if ":" in teil:
                k, v = teil.split(":", 1)
                stil[k.strip().lower()] = v.strip()
        farbe = (s.get("fillcolor") or "silver").strip().lower()
        farbe = _VML_FARBEN.get(farbe, farbe if farbe.startswith("#") and len(farbe) == 7 else "#c0c0c0")
        try:
            winkel = float(stil.get("rotation", "0"))
        except ValueError:
            winkel = 0.0
        winkel = winkel - 360 if winkel > 180 else winkel
        w = {"text": tp[0].get("string"), "farbe": farbe, "winkel": winkel}
        schrift = (tp[0].get("style") or "").replace("&quot;", '"')
        for teil in schrift.split(";"):
            if teil.strip().lower().startswith("font-family:"):
                w["schrift"] = teil.split(":", 1)[1].strip().strip('"')
        fill = _x(s, "v:fill")
        if fill and fill[0].get("opacity"):
            roh = fill[0].get("opacity")
            try:
                deck = float(roh[:-1]) / 65536 if roh.endswith("f") else float(roh)
                w["transparenz"] = int(round((1 - max(0.0, min(1.0, deck))) * 100))
            except ValueError:
                pass
        return w
    return None


_SHAPETYPE = ('<v:shapetype xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" id="_x0000_t136" coordsize="21600,21600" o:spt="136" adj="10800" '
              'path="m@7,l@8,m@5,21600l@6,21600e"><v:formulas><v:f eqn="sum #0 0 10800"/><v:f eqn="prod #0 2 1"/><v:f eqn="sum 21600 0 @1"/><v:f eqn="sum 0 0 @2"/>'
              '<v:f eqn="sum 21600 0 @3"/><v:f eqn="if @0 @3 0"/><v:f eqn="if @0 21600 @1"/><v:f eqn="if @0 0 @2"/><v:f eqn="if @0 @4 21600"/><v:f eqn="mid @5 @6"/>'
              '<v:f eqn="mid @8 @5"/><v:f eqn="mid @7 @8"/><v:f eqn="mid @6 @7"/><v:f eqn="sum @6 0 @5"/></v:formulas><v:path textpathok="t" o:connecttype="custom" '
              'o:connectlocs="@9,0;@10,10800;@11,21600;@12,10800" o:connectangles="270,180,90,0"/><v:textpath on="t" fitshape="t"/><v:handles><v:h position="#0,bottomRight" '
              'xrange="6629,14971"/></v:handles><o:lock v:ext="edit" text="t" shapetype="t"/></v:shapetype>')


def wasserzeichen_zu_xml(w: dict, nummer: int):
    """``PageSettings.watermark`` (Text) → ``w:r`` mit ``w:pict`` für die Kopfzeile; ``None`` ohne Text."""
    from xml.sax.saxutils import quoteattr
    text = (w.get("text") or "").strip()
    if not text:
        return None
    winkel = float(w.get("winkel", -45) or 0)
    drehung = winkel + 360 if winkel < 0 else winkel
    breite = max(120.0, min(560.0, len(text) * 52.0))
    hoehe = breite / max(1, len(text)) * 1.9
    farbe = (w.get("farbe") or "#c0c0c0")
    deck = 1 - max(0, min(100, int(w.get("transparenz", 50) or 0))) / 100
    schrift = str(w.get("schrift") or "Calibri").replace('"', "")
    xml = (f'<w:r xmlns:w="{W_NS}" xmlns:v="{NS["v"]}" xmlns:o="{NS["o"]}"><w:rPr><w:noProof/></w:rPr><w:pict>{_SHAPETYPE}'
           f'<v:shape id="PowerPlusWaterMarkObject{nummer}" o:spid="_x0000_s{2048 + nummer}" type="#_x0000_t136" style="position:absolute;margin-left:0;margin-top:0;'
           f'width:{breite:.0f}pt;height:{hoehe:.0f}pt;rotation:{drehung:g};z-index:-251658752;mso-position-horizontal:center;mso-position-horizontal-relative:margin;'
           f'mso-position-vertical:center;mso-position-vertical-relative:margin" o:allowincell="f" fillcolor={quoteattr(farbe)} stroked="f">'
           f'<v:fill opacity="{deck:.2f}"/><v:textpath style="font-family:&quot;{schrift}&quot;;font-size:1pt" string={quoteattr(text)}/></v:shape></w:pict></w:r>')
    from docx.oxml import parse_xml
    return parse_xml(xml)


# --------------------------------------------------------------------------------------------------------------------------------------------------------------
# Formen und Textfelder (wps:wsp in w:drawing)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
def ist_form(drawing) -> bool:
    gd = drawing.find(f".//{_A}graphicData")
    return gd is not None and gd.get("uri", "") == FORM_URI


def _farbe_von(fill) -> str:
    """Farbe einer ``a:solidFill`` als „#rrggbb“; leer, wenn es keine einfache RGB-Farbe ist."""
    if fill is None:
        return ""
    c = fill.find(_A + "srgbClr")
    return "#" + c.get("val").lower() if c is not None and c.get("val") else ""


def _absaetze_text(txbx) -> tuple[str, dict]:
    """Text eines Textfelds (``w:txbxContent``) mit Schrift, Größe, Farbe und Fettdruck des ersten Laufs."""
    zeilen, fmt = [], {}
    for p in txbx.iter(W + "p"):
        text = ""
        for r in p.iter(W + "r"):
            text += "".join(t.text or "" for t in r.iter(W + "t"))
            rpr = r.find(W + "rPr")
            if rpr is not None and not fmt:
                fonts = rpr.find(W + "rFonts")
                if fonts is not None and (fonts.get(W + "ascii") or fonts.get(W + "hAnsi")):
                    fmt["schrift"] = fonts.get(W + "ascii") or fonts.get(W + "hAnsi")
                sz = rpr.find(W + "sz")
                if sz is not None and (sz.get(W + "val") or "").isdigit():
                    fmt["pt"] = int(sz.get(W + "val")) / 2
                farbe = rpr.find(W + "color")
                if farbe is not None and (farbe.get(W + "val") or "") not in ("", "auto"):
                    fmt["farbe"] = "#" + farbe.get(W + "val").lower()
                for k, n in (("fett", "b"), ("kursiv", "i")):
                    e = rpr.find(W + n)
                    if e is not None and e.get(W + "val") not in ("0", "false", "off"):
                        fmt[k] = True
        zeilen.append(text)
    return "\n".join(zeilen), fmt


def form_aus_zeichnung(drawing, huelle) -> dict:
    """Form oder Textfeld (``w:drawing`` mit ``wps:wsp``) → {"art", "breite", "hoehe", "alt", "daten"}; ``Beziehung`` bei Verweisen auf andere Teile (Bildfüllung …),
    ``ValueError`` bei Gruppen, verknüpften Textfeldern und anderem, das sich nicht abbilden lässt."""
    gd = drawing.find(f".//{_A}graphicData")
    wsp = gd.find(_WPS + "wsp") if gd is not None else None
    if wsp is None:
        raise ValueError("Gruppe oder anderes Zeichnungsobjekt")
    if hat_beziehung(drawing):
        raise Beziehung("Zeichnung")
    if wsp.find(_WPS + "linkedTxbx") is not None:
        raise ValueError("verknüpftes Textfeld")
    ext = huelle.find(_WP + "extent")
    breite, hoehe = float(ext.get("cx")) / EMU_JE_PX, float(ext.get("cy")) / EMU_JE_PX
    docpr = huelle.find(_WP + "docPr")
    alt = (docpr.get("descr") or "") if docpr is not None else ""
    sp = wsp.find(_WPS + "spPr")
    txbx = wsp.find(_WPS + "txbx")
    cnv = wsp.find(_WPS + "cNvSpPr")
    textfeld = cnv is not None and cnv.get("txBox") in ("1", "true")
    angabe: dict = {}
    fuell, linie, strich = "", "", 0.0
    prst = "rect"
    if sp is not None:
        xf = sp.find(_A + "xfrm")
        if xf is not None:
            if xf.get("rot"):
                grad = int(xf.get("rot")) / 60000.0
                angabe["dreh"] = grad - 360 if grad > 180 else grad
            if xf.get("flipH") in ("1", "true"):
                angabe["flipH"] = True
            if xf.get("flipV") in ("1", "true"):
                angabe["flipV"] = True
        geo = sp.find(_A + "prstGeom")
        prst = geo.get("prst") if geo is not None else "custom"
        fuell = _farbe_von(sp.find(_A + "solidFill"))
        ln = sp.find(_A + "ln")
        if ln is not None:
            if ln.find(_A + "noFill") is None:
                linie = _farbe_von(ln.find(_A + "solidFill")) or "#000000"
                strich = int(ln.get("w") or 9525) / EMU_JE_PX
        elif sp.find(_A + "noFill") is None and not fuell:
            linie = ""
    text, fmt = _absaetze_text(txbx) if txbx is not None else ("", {})
    if fuell:
        angabe["fuell"] = {"art": "farbe", "farbe": fuell}
    if linie:
        angabe["rand"] = {"farbe": linie, "b": strich or 1.0, "art": "einfach"}
    if alt:
        angabe["alt"] = alt
    if textfeld or (txbx is not None and prst == "rect" and not fuell and not linie):
        art = "textfeld"
        innen = {"text": text, "schrift": fmt.get("schrift", "Liberation Sans"), "pt": fmt.get("pt", 11), "farbe": fmt.get("farbe", "#1f1f1f")}
        for k in ("fett", "kursiv"):
            if fmt.get(k):
                innen[k] = True
        bp = wsp.find(_WPS + "bodyPr")
        if bp is not None:
            standard = {"lIns": 91440, "tIns": 45720, "rIns": 91440, "bIns": 45720}
            try:
                innen["innen"] = [round(float(bp.get(k) or standard[k]) / EMU_JE_PX, 2) for k in ("lIns", "tIns", "rIns", "bIns")]
            except ValueError:
                pass
    else:
        art = "form"
        innen = {"form": _GEOMETRIE.get(prst, "rechteck"), "fuell": fuell, "linie": linie or "", "strich": strich if linie else 0.0, "text": text}
        if prst not in _GEOMETRIE:
            innen["docx_geometrie"] = prst
    angabe["daten"] = innen
    angabe["docx_roh"] = als_text(drawing)
    return {"art": art, "breite": breite, "hoehe": hoehe, "alt": alt, "daten": angabe}


_V = "{urn:schemas-microsoft-com:vml}"
_VML_EINHEIT_PX = {"pt": 96 / 72, "in": 96.0, "cm": 96 / 2.54, "mm": 96 / 25.4, "px": 1.0}


def _vml_stil(el) -> dict:
    """Das Attribut ``style`` eines VML-Elements als Verzeichnis."""
    aus = {}
    for teil in (el.get("style") or "").split(";"):
        if ":" in teil:
            k, v = teil.split(":", 1)
            aus[k.strip().lower()] = v.strip()
    return aus


def _vml_px(wert) -> float | None:
    """Maß wie ``380pt`` oder ``2in`` in Bildpunkten (96 dpi); ``None`` ohne gültige Angabe."""
    t = (wert or "").strip().lower()
    for einheit, faktor in _VML_EINHEIT_PX.items():
        if t.endswith(einheit):
            try:
                return float(t[:-len(einheit)]) * faktor
            except ValueError:
                return None
    try:
        return float(t) if t else None
    except ValueError:
        return None


def textfeld_aus_vml(pict) -> dict | None:
    """Textfeld in VML (``w:pict`` mit ``v:rect``/``v:shape`` und ``v:textbox``), das in der Zeile steht → wie ``form_aus_zeichnung``
    {"art", "breite", "hoehe", "alt", "daten"}; ``None``, wenn es nicht abbildbar ist (mehrere Objekte, kein Textfeld, frei positioniert)."""
    formen = [e for e in pict if e.tag in (_V + "rect", _V + "shape", _V + "roundrect")]
    if len(formen) != 1:
        return None
    form = formen[0]
    box = form.find(_V + "textbox")
    inhalt = box.find(W + "txbxContent") if box is not None else None
    if inhalt is None:
        return None
    stil = _vml_stil(form)
    if (stil.get("position") or "static") != "static" or "margin-left" in stil or "margin-top" in stil or "mso-position-horizontal" in stil:
        return None                                                          # frei auf dem Blatt: bleibt dem Rückfall überlassen
    breite, hoehe = _vml_px(stil.get("width")), _vml_px(stil.get("height"))
    if not breite or not hoehe:
        return None
    text, fmt = _absaetze_text(inhalt)
    angabe: dict = {}
    fuell = (form.get("fillcolor") or "").lower()
    if form.get("filled") != "f" and len(fuell) == 7 and fuell.startswith("#"):
        angabe["fuell"] = {"art": "farbe", "farbe": fuell}
    if form.get("stroked") != "f":
        linie = (form.get("strokecolor") or "").lower()
        angabe["rand"] = {"farbe": linie if len(linie) == 7 and linie.startswith("#") else "#000000", "b": 1.0, "art": "einfach"}
    innen = {"text": text, "schrift": fmt.get("schrift", "Liberation Sans"), "pt": fmt.get("pt", 11), "farbe": fmt.get("farbe", "#1f1f1f")}
    for k in ("fett", "kursiv"):
        if fmt.get(k):
            innen[k] = True
    angabe["daten"] = innen
    angabe["docx_roh"] = als_text(pict)
    return {"art": "textfeld", "breite": breite, "hoehe": hoehe, "alt": "", "daten": angabe, "_vorlage_absatz": inhalt.find(W + "p")}


def _emu(px) -> int:
    return int(round(float(px) * EMU_JE_PX))


def _absatz_xml(zeile: str, innen: dict) -> str:
    from xml.sax.saxutils import escape
    rpr = ""
    if innen.get("schrift"):
        s = escape(str(innen["schrift"]), {'"': "&quot;"})
        rpr += f'<w:rFonts w:ascii="{s}" w:hAnsi="{s}" w:cs="{s}"/>'
    if innen.get("fett"):
        rpr += "<w:b/>"
    if innen.get("kursiv"):
        rpr += "<w:i/>"
    farbe = str(innen.get("farbe") or "")
    if len(farbe) == 7 and farbe.startswith("#"):
        rpr += f'<w:color w:val="{farbe[1:].upper()}"/>'
    if innen.get("pt"):
        rpr += f'<w:sz w:val="{int(round(float(innen["pt"]) * 2))}"/>'
    return f'<w:p><w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{escape(zeile)}</w:t></w:r></w:p>'


def _fuellung_xml(fuell: str) -> str:
    return f'<a:solidFill><a:srgbClr val="{fuell[1:].upper()}"/></a:solidFill>' if len(fuell) == 7 and fuell.startswith("#") else "<a:noFill/>"


def _linie_xml(linie: str, strich: float) -> str:
    if len(linie) == 7 and linie.startswith("#"):
        return f'<a:ln w="{_emu(strich or 1.0)}"><a:solidFill><a:srgbClr val="{linie[1:].upper()}"/></a:solidFill></a:ln>'
    return "<a:ln><a:noFill/></a:ln>"


def zeichnung_neu(art: str, breite: float, hoehe: float, daten: dict, nummer: int, hinter: bool | None = None) -> str:
    """XML-Text einer neuen ``w:drawing`` (Form oder Textfeld) ohne Verankerung: das Ergebnis enthält ``wp:inline``; ``zu_anker`` macht daraus die Verankerung."""
    from xml.sax.saxutils import escape
    innen = daten.get("daten") if isinstance(daten.get("daten"), dict) else {}
    rot = int(round(float(daten.get("dreh", 0) or 0) * 60000)) % 21600000
    transform = f' rot="{rot}"' if rot else ""
    transform += ' flipH="1"' if daten.get("flipH") else ""
    transform += ' flipV="1"' if daten.get("flipV") else ""
    rand = daten.get("rand") if isinstance(daten.get("rand"), dict) else {}
    fuell = (daten.get("fuell") or {}).get("farbe", "") if isinstance(daten.get("fuell"), dict) else ""
    if art == "form":
        prst = innen.get("docx_geometrie") or _GEOMETRIE_UMGEKEHRT.get(str(innen.get("form", "rechteck")).casefold(), "rect")
        fuell = fuell or str(innen.get("fuell") or "")
        linie, strich = rand.get("farbe") or str(innen.get("linie") or ""), float(rand.get("b") or innen.get("strich") or 0)
        text = str(innen.get("text") or "")
        kasten = ""
    else:
        prst = "rect"
        linie, strich = rand.get("farbe", ""), float(rand.get("b") or 0)
        text = str(innen.get("text") or "")
        kasten = ' txBox="1"'
    absaetze = "".join(_absatz_xml(z, innen) for z in (text.split("\n") if text else [""]))
    ins = innen.get("innen")
    insets = ""
    if isinstance(ins, (list, tuple)) and len(ins) == 4:
        insets = " " + " ".join(f'{k}="{_emu(v)}"' for k, v in zip(("lIns", "tIns", "rIns", "bIns"), ins))
    txbx = f"<wps:txbx><w:txbxContent>{absaetze}</w:txbxContent></wps:txbx>" if (text or art == "textfeld") else ""
    alt = escape(str(daten.get("alt") or ""), {'"': "&quot;"})
    cx, cy = _emu(breite), _emu(hoehe)
    return (f'<w:drawing xmlns:w="{W_NS}" xmlns:wp="{NS["wp"]}" xmlns:a="{NS["a"]}" xmlns:wps="{NS["wps"]}"><wp:inline distT="0" distB="0" distL="0" distR="0">'
            f'<wp:extent cx="{cx}" cy="{cy}"/><wp:effectExtent l="0" t="0" r="0" b="0"/><wp:docPr id="{nummer}" name="{"Textfeld" if art == "textfeld" else "Form"} {nummer}" descr="{alt}"/>'
            f'<wp:cNvGraphicFramePr/><a:graphic><a:graphicData uri="{FORM_URI}"><wps:wsp><wps:cNvSpPr{kasten}/><wps:spPr><a:xfrm{transform}><a:off x="0" y="0"/>'
            f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="{prst}"><a:avLst/></a:prstGeom>{_fuellung_xml(fuell)}{_linie_xml(linie, strich)}</wps:spPr>'
            f'{txbx}<wps:bodyPr rot="0" vert="horz" wrap="square"{insets} anchor="t" anchorCtr="0"><a:noAutofit/></wps:bodyPr></wps:wsp></a:graphicData></a:graphic></wp:inline></w:drawing>')


def groesse_setzen(drawing, breite: float, hoehe: float, nummer: int) -> None:
    """Größe (``wp:extent`` und ``a:ext``) und Kennung (``wp:docPr/@id``) einer erhaltenen Zeichnung auf die Werte des Modells setzen."""
    cx, cy = str(_emu(breite)), str(_emu(hoehe))
    for huelle in drawing:
        ext = huelle.find(_WP + "extent")
        if ext is not None:
            ext.set("cx", cx)
            ext.set("cy", cy)
        docpr = huelle.find(_WP + "docPr")
        if docpr is not None:
            docpr.set("id", str(nummer))
    for e in drawing.iter(_A + "ext"):
        if e.get("cx") is not None:
            e.set("cx", cx)
            e.set("cy", cy)
