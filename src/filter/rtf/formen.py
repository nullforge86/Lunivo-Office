"""RTF-Formen (``\\shp`` mit ``\\shpinst`` und den Eigenschaften ``\\sp{\\sn Name}{\\sv Wert}``): in das Wörterbuch des Modells übersetzen, Qt-frei.

Geometrie in Twips (``\\shpleft`` …), Farben als BGR-Ganzzahl (``fillColor``), Strichstärke in EMU (``lineWidth``), Winkel als 16.16-Festkomma (``rotation``, ``fillAngle``).
Ergebnis wie bei DOCX und ODT: ``{"art", "breite", "hoehe", "daten", "ressource"?, "lage"}``; ``lage`` beschreibt die Verankerung (Bezug, Versatz, Umbruch)."""
from __future__ import annotations

_FORM = {1: "rechteck", 2: "abgerundet", 3: "ellipse", 4: "raute", 5: "dreieck", 6: "rechtwinkliges_dreieck", 7: "parallelogramm", 8: "trapez", 9: "sechseck",
         10: "achteck", 11: "kreuz", 12: "stern", 13: "blockpfeil_rechts", 15: "pfeil_fuenfeck", 20: "linie", 22: "zylinder", 56: "fuenfeck", 74: "herz", 179: "wolke"}
_TWIP_JE_PX = 15.0


def _farbe(wert) -> str:
    """BGR-Ganzzahl (Word) → „#rrggbb“; leer bei ungültigem oder Systemfarbwert."""
    try:
        n = int(wert)
    except (TypeError, ValueError):
        return ""
    if n < 0 or n > 0xFFFFFF:
        return ""
    return "#%02x%02x%02x" % (n & 255, (n >> 8) & 255, (n >> 16) & 255)


def _zahl(wert, standard: float = 0.0) -> float:
    try:
        return float(wert)
    except (TypeError, ValueError):
        return standard


def _text_von(z, ziel) -> tuple[str, dict]:
    """Text und Zeichenformat des ersten Laufs aus dem gesammelten Ziel der Form (``\\shptxt``)."""
    from filter.rtf.modell import Absatz as RtfAbsatz
    zeilen, fmt = [], {}
    absaetze = [a for a in ziel.teile if isinstance(a, RtfAbsatz)] + ([RtfAbsatz({}, ziel.laeufe, None)] if ziel.laeufe else [])
    for a in absaetze:
        text = ""
        for lauf in a.laeufe:
            if lauf[0] != "t":
                continue
            text += lauf[1]
            if not fmt:
                d = dict(lauf[2])
                if d.get("f") in z.schriften:
                    fmt["schrift"] = z.schriften[d["f"]]
                if d.get("fs"):
                    fmt["pt"] = d["fs"] / 2
                if d.get("b"):
                    fmt["fett"] = True
                if d.get("i"):
                    fmt["kursiv"] = True
                cf = d.get("cf")
                if isinstance(cf, int) and 0 <= cf < len(z.farben) and z.farben[cf]:
                    fmt["farbe"] = z.farben[cf]
        zeilen.append(text.replace(" ", "\n"))
    return "\n".join(zeilen).strip("\n"), fmt


def form_aus_shp(z, shp: dict) -> dict | None:
    """Die gesammelten Angaben einer ``\\shp``-Gruppe als Objekt des Modells; ``None``, wenn die Form nichts Darstellbares enthält."""
    g, e = shp.get("geom", {}), shp.get("eig", {})
    breite = (_zahl(g.get("shpright")) - _zahl(g.get("shpleft"))) / _TWIP_JE_PX
    hoehe = (_zahl(g.get("shpbottom")) - _zahl(g.get("shptop"))) / _TWIP_JE_PX
    typ = int(_zahl(e.get("shapeType"), 1))
    text, fmt = _text_von(z, shp["txt"]) if shp.get("txt") is not None else ("", {})
    angabe: dict = {}
    drehung = _zahl(e.get("rotation")) / 65536.0
    if drehung:
        angabe["dreh"] = drehung - 360 if drehung > 180 else drehung
    if e.get("fFlipH") == "1":
        angabe["flipH"] = True
    if e.get("fFlipV") == "1":
        angabe["flipV"] = True
    gefuellt = e.get("fFilled", "1") != "0"
    voll = None
    if not gefuellt:
        voll = {}
    else:
        farbe = _farbe(e.get("fillColor", 0xFFFFFF if typ != 20 else 0)) or "#ffffff"
        art = int(_zahl(e.get("fillType"), 0))
        hinten = _farbe(e.get("fillBackColor", 0xFFFFFF)) or "#ffffff"
        if art in (4, 5, 6, 7):                                       # Verlauf
            winkel = (90.0 - _zahl(e.get("fillAngle")) / 65536.0) % 360.0
            voll = {"art": "graduell", "farbe": farbe, "hell": farbe, "dunkel": hinten, "stops": [[0.0, farbe], [1.0, hinten]], "winkel": winkel}
        elif art == 1:                                                # Muster: ohne Mustertabelle ein mittleres Raster in den beiden Farben
            voll = {"art": "muster", "farbe": farbe, "key": "pct50", "grund": hinten}
        elif art in (3, 9) and shp.get("bild") is not None:           # Bildfüllung
            voll = {"art": "bild", "farbe": "", "n": None}
        else:
            voll = {"art": "farbe", "farbe": farbe}
    linie = None
    if e.get("fLine", "1") != "0":
        b = max(0.5, _zahl(e.get("lineWidth"), 9525) / 9525.0)
        stil = int(_zahl(e.get("lineDashing"), 0))
        linie = {"farbe": _farbe(e.get("lineColor", 0)) or "#000000", "b": b,
                 "art": {1: "gestrichelt", 2: "gepunktet", 3: "gestrichelt", 4: "strichpunkt", 5: "strichpunktpunkt", 6: "gestrichelt", 7: "gestrichelt"}.get(stil, "einfach")}
    if voll is not None:
        angabe["fuell"] = voll
    if linie:
        angabe["rand"] = linie
    # Verankerung: Bezug nach \shpbx…/\shpby…, Umbruch nach \shpwr und \shpfblwtxt
    bezug_h = "seite" if "shpbxpage" in g else "rand" if "shpbxmargin" in g else "spalte"
    bezug_v = "seite" if "shpbypage" in g else "rand" if "shpbymargin" in g else "absatz"
    if "shpbxignore" in g:                                             # die \shpbx…-Angaben gelten nicht: ``posrelh`` bestimmt den Bezug (0 Rand, 1 Seite, 2 Spalte, 3 Zeichen)
        bezug_h = {0: "rand", 1: "seite", 2: "spalte", 3: "spalte"}.get(int(_zahl(e.get("posrelh"), 3)), "spalte")
    if "shpbyignore" in g:                                             # ``posrelv``: 0 Rand, 1 Seite, 2 Absatz, 3 Zeile
        bezug_v = {0: "rand", 1: "seite", 2: "absatz", 3: "absatz"}.get(int(_zahl(e.get("posrelv"), 2)), "absatz")
    umbruch = {1: "oben_unten", 2: "quadrat", 3: "vor", 4: "eng", 5: "eng"}.get(int(_zahl(g.get("shpwr"), 2)), "quadrat")
    if umbruch == "vor" and (g.get("shpfblwtxt") == 1 or e.get("fBehindDocument") == "1"):
        umbruch = "hinter"
    lage = {"bezug_h": bezug_h, "bezug_v": bezug_v, "x": _zahl(g.get("shpleft")) / _TWIP_JE_PX, "y": _zahl(g.get("shptop")) / _TWIP_JE_PX, "umbruch": umbruch,
            "ebene": int(_zahl(g.get("shpz")))}
    ergebnis = {"breite": breite, "hoehe": hoehe, "lage": lage, "alt": e.get("wzDescription", "")}
    if shp.get("roh_bild") is not None:                                # Bild, das kein Decoder kennt (zum Beispiel Musterkachel): unverändert für das Speichern aufbewahren
        ergebnis["roh_bild"] = shp["roh_bild"]
    if shp.get("bild") is not None and typ == 75:                      # Bildrahmen
        ergebnis.update(art="bild", daten={k: v for k, v in angabe.items() if k in ("dreh", "flipH", "flipV", "rand")}, bild=shp["bild"])
        return ergebnis
    if shp.get("bild") is not None and voll is not None and voll.get("art") == "bild":
        ergebnis["fuellbild"] = shp["bild"]
    if typ == 136 or e.get("gtextUNICODE"):                           # WordArt (Fontwork)
        wa = e.get("gtextUNICODE") or text
        if not wa:
            return None
        farbe = _farbe(e.get("fillColor", 0)) or "#000000"
        ergebnis.update(art="wordart", daten={"daten": {"text": wa, "schrift": e.get("gtextFont") or fmt.get("schrift", "Liberation Sans"), "pt": fmt.get("pt", 36), "fett": True,
                                                       "fuell": {"art": "farbe", "farbe": farbe},
                                                       **({"kontur": {"farbe": linie["farbe"], "b": linie["b"]}} if linie else {})}})
        return ergebnis
    if typ == 202 or (typ == 1 and text and (voll == {} or voll is None) and not linie):
        innen = {"text": text, "schrift": fmt.get("schrift", "Liberation Sans"), "pt": fmt.get("pt", 12), "farbe": fmt.get("farbe", "#1f1f1f")}
        for k in ("fett", "kursiv"):
            if fmt.get(k):
                innen[k] = True
        ins = [_zahl(e.get(k), d) / 9525.0 for k, d in (("dxTextLeft", 91440), ("dyTextTop", 45720), ("dxTextRight", 91440), ("dyTextBottom", 45720))]
        innen["innen"] = [round(v, 2) for v in ins]
        ergebnis.update(art="textfeld", daten={**angabe, "daten": innen})
        return ergebnis
    kind = _FORM.get(typ)
    if kind is None:
        z.report.warn(f"Die RTF-Form vom Typ {typ} wird als Rechteck dargestellt.")
        kind = "rechteck"
    innen = {"form": kind, "fuell": (voll or {}).get("farbe", ""), "linie": (linie or {}).get("farbe", ""), "strich": (linie or {}).get("b", 0.0), "text": text}
    if text:
        innen.update({k: v for k, v in fmt.items() if k in ("schrift", "pt", "farbe", "fett", "kursiv")})
    ergebnis.update(art="form", daten={**angabe, "daten": innen})
    return ergebnis
