"""Formate der Diagrammteile ohne Qt (``daten["teil_format"][teil]``): Füllung, Linie, Effekte, Text, Pfeile. Gezeichnet über das Rendering-Backend.

``fuell``   ``""`` keine · ``"#rrggbb"`` einfarbig · ``{"art": farbe|graduell|verlauf|textur|muster|bild|keine, "farbe", "dunkel", "hell", "winkel", "key", "grund", "bild_b64", "transparenz"}``
``linie``   ``{"keine": True}`` oder ``{"farbe", "breite" (pt), "art", "transparenz", "kombiniert" (einfach|doppelt|dick_duenn|duenn_dick|dreifach), "abschluss", "rund", "pfeil_anfang",
            "pfeil_ende", "pfeil_groesse_anfang", "pfeil_groesse_ende"}``
``schatten``, ``reflektion``, ``leuchten``, ``weich``, ``d3`` — Effekte des Teils (``True`` = Vorgabe); ``drehung`` wird nicht dargestellt (Bericht).
``text``    ``{"farbe", "groesse" (pt), "fett", "kursiv", "unter", "name", "effekt", "feld": {"vertikal", "richtung", "winkel", "raender"}}``"""
from __future__ import annotations

import base64
import dataclasses
import math

from core.geometrie import Point, Rect
from core.textsatz.engine import FontSpec
from core.layout.drucklayout.ausgabe.backend import LinearGradient, Style, rgba

PX = 96.0 / 72.0
VORGABEN = {"schatten": {"farbe": "#000000", "transparenz": 60, "groesse": 100, "weich": 4.0, "abstand": 4.0, "winkel": 45},
            "reflektion": {"groesse": 50, "transparenz": 50, "weich": 0.5, "abstand": 0.0}, "leuchten": {"farbe": "#4472c4", "groesse": 8.0, "transparenz": 60},
            "weich": {"radius": 6.0}, "d3": {"tiefe": 6.0, "tiefe_farbe": "#808080", "kontur": 0.0, "kontur_farbe": "#404040", "material": "matt", "beleuchtung": "neutral", "winkel": 0}}
FX_SCHLUESSEL = ("schatten", "reflektion", "leuchten", "weich", "d3")
_DASH = {"gestrichelt": "dash", "gepunktet": "dot", "strichpunkt": "dashdot", "strichpunktpunkt": "dashdotdot", "dash": "dash", "dot": "dot"}


def _farbe(text, standard=(0, 0, 0, 255)) -> tuple:
    try:
        return rgba(text)
    except (ValueError, IndexError, TypeError, AttributeError):
        return standard


def _mit_deckkraft(c: tuple, transparenz) -> tuple:
    return (c[0], c[1], c[2], int(c[3] * max(0.0, min(1.0, 1.0 - float(transparenz or 0) / 100.0))))


def fuell_dict(f) -> dict | None:
    if not f:
        return None
    return {"art": "farbe", "farbe": f} if isinstance(f, str) else f


def ist_keine(f) -> bool:
    return f == "" or (isinstance(f, dict) and f.get("art") == "keine")


def hauptfarbe(f) -> str | None:
    d = fuell_dict(f)
    if not d:
        return None
    return d.get("farbe") or d.get("hell") or d.get("dunkel")


def fuell_style(f, rect: Rect) -> Style | None:
    """Der Stil der Füllung eines Teils in ``rect``; ``None`` bei keiner Füllung oder wenn nichts gesetzt ist."""
    d = fuell_dict(f)
    if not d or d.get("art") == "keine":
        return None
    from core.objekte.anordnung.objekte_hilfen import FillStyle
    from core.layout.drucklayout.ausgabe.objekte.objekte import fuellstil
    bild = None
    if d.get("art") == "bild":
        try:
            bild = base64.b64decode(d.get("bild_b64", ""))
        except (ValueError, TypeError):
            bild = None
    st = fuellstil(FillStyle.aus_dict({k: v for k, v in d.items() if k != "transparenz"}), rect, bild)
    if st is None:
        return None
    t = d.get("transparenz") or 0
    if not t:
        return st
    fill = st.fill
    if isinstance(fill, LinearGradient):
        fill = dataclasses.replace(fill, stops=tuple((p, _mit_deckkraft(c, t)) for p, c in fill.stops))
    return dataclasses.replace(st, color=_mit_deckkraft(st.color, t), fill=fill)


def linie_stile(linie, standard_farbe: tuple, standard_breite: float) -> list:
    """Die Linienstile eines Teils (mehrere bei ``kombiniert``: doppelt, dick-dünn …); leer bei „keine Linie“."""
    if linie is None:
        return [Style(color=standard_farbe, width=standard_breite)] if standard_breite > 0 else []
    if linie.get("keine"):
        return []
    farbe = _mit_deckkraft(_farbe(linie.get("farbe"), standard_farbe), linie.get("transparenz"))
    breite = float(linie.get("breite", standard_breite / PX if standard_breite else 0.75)) * PX
    dash = _DASH.get(str(linie.get("art") or ""), None)
    cap = {"rund": "round", "quadrat": "square"}.get(str(linie.get("abschluss") or ""), "flat")
    join = "round" if linie.get("rund") else {"schraeg": "bevel", "rund": "round"}.get(str(linie.get("verknuepfung") or ""), "miter")
    stil = Style(color=farbe, width=breite, dash=dash, cap=cap, join=join)
    k = str(linie.get("kombiniert") or "einfach")
    if k == "einfach":
        return [stil]
    teile = {"doppelt": [(0.34, -0.33), (0.34, 0.33)], "dick_duenn": [(0.5, -0.25), (0.22, 0.4)], "duenn_dick": [(0.22, -0.4), (0.5, 0.25)],
             "dreifach": [(0.22, -0.39), (0.22, 0.0), (0.22, 0.39)]}.get(k)
    return [dataclasses.replace(stil, width=max(0.5, breite * a)) for a, _o in teile] if teile else [stil]


def _versatz(linie) -> list:
    k = str((linie or {}).get("kombiniert") or "einfach")
    return {"doppelt": [-0.33, 0.33], "dick_duenn": [-0.25, 0.4], "duenn_dick": [-0.4, 0.25], "dreifach": [-0.39, 0.0, 0.39]}.get(k, [0.0])


def rahmen_zeichnen(b, rect: Rect, linie, standard_farbe: tuple = (0, 0, 0, 255), standard_breite: float = 0.0) -> None:
    stile = linie_stile(linie, standard_farbe, standard_breite)
    gesamt = float((linie or {}).get("breite", 0.75)) * PX
    for st, off in zip(stile, _versatz(linie)):
        d = off * gesamt
        b.draw_rect(Rect(rect.x - d, rect.y - d, rect.width + 2 * d, rect.height + 2 * d), st)


# ---- Effekte -------------------------------------------------------------------------------------------------------------------
def effekt(fmt: dict, name: str) -> dict | None:
    w = (fmt or {}).get(name)
    if not w:
        return None
    return dict(VORGABEN[name]) if w is True else {**VORGABEN[name], **w}


def hat_effekte(fmt: dict) -> bool:
    return any((fmt or {}).get(k) for k in FX_SCHLUESSEL)


def _rect_ops(r: Rect) -> list:
    return [("R", r.x, r.y, r.width, r.height)]


def effekte_hinter(b, rect: Rect, fmt: dict, farbe: tuple) -> None:
    """Was hinter einem Teil liegt: 3D-Tiefe, Schatten, Leuchten und Spiegelung."""
    d3 = effekt(fmt, "d3")
    if d3 and float(d3.get("tiefe", 0)) > 0:
        tiefe = float(d3["tiefe"]) * PX
        w = math.radians(float(d3.get("winkel", 0)) + 45)
        basis = _farbe(d3.get("tiefe_farbe", "#808080"))
        n = max(2, int(tiefe))
        for k in range(n, 0, -1):
            t = k / n
            f = {"plastik": 1.25 - 0.5 * t, "metall": 1.0 + 0.45 * math.sin(t * math.pi * 2), "dunkel": 0.6 + 0.4 * (1 - t), "weich": 1.15 - 0.25 * t, "hell": 1.3}.get(d3.get("material", "matt"), 1.0)
            c = tuple(max(0, min(255, int(basis[i] * f))) for i in range(3)) + (255,)
            b.draw_rect(Rect(rect.x + math.cos(w) * tiefe * t, rect.y + math.sin(w) * tiefe * t, rect.width, rect.height), Style(color=c, width=0, filled=True))
    s = effekt(fmt, "schatten")
    if s:
        sk = float(s.get("groesse", 100)) / 100.0
        a = math.radians(float(s.get("winkel", 45)))
        abst = float(s.get("abstand", 4)) * PX
        cx, cy = rect.x + rect.width / 2, rect.y + rect.height / 2
        ops = _rect_ops(Rect(cx - rect.width * sk / 2, cy - rect.height * sk / 2, rect.width * sk, rect.height * sk))
        b.draw_shadow(ops, _mit_deckkraft(_farbe(s.get("farbe"), (0, 0, 0, 255)), s.get("transparenz", 60)), float(s.get("weich", 4)) * PX * 0.6, math.cos(a) * abst, math.sin(a) * abst)
    g = effekt(fmt, "leuchten")
    if g and float(g.get("groesse", 0)) > 0:
        b.draw_shadow(_rect_ops(rect), _mit_deckkraft(_farbe(g.get("farbe")), g.get("transparenz", 60)), float(g["groesse"]) * PX, 0.0, 0.0)
    r = effekt(fmt, "reflektion")
    if r:
        hoch = rect.height * float(r.get("groesse", 50)) / 100.0
        y0 = rect.bottom + float(r.get("abstand", 0)) * PX
        c = _mit_deckkraft(farbe, r.get("transparenz", 50))
        b.draw_rect(Rect(rect.x, y0, rect.width, hoch), Style(color=c, width=0, filled=True, fill=LinearGradient(Point(0, y0), Point(0, y0 + hoch), ((0.0, c), (1.0, (c[0], c[1], c[2], 0))))))


def teil_zeichnen(b, engine, rect: Rect, fmt: dict, grund: tuple = (255, 255, 255, 255), standard_fuell: tuple | None = None, standard_linie: tuple | None = None, hinweise=None) -> None:
    """Ein Teil als Fläche: Effekte dahinter, Füllung, Linie; ``weich`` rechnet das Teil in einem eigenen Bild und blendet den Rand aus."""
    fmt = fmt or {}
    st = fuell_style(fmt.get("fuell"), rect) if "fuell" in fmt else (Style(color=standard_fuell, width=0, filled=True) if standard_fuell else None)
    farbe = st.color if st is not None else (standard_fuell or (128, 128, 128, 255))
    effekte_hinter(b, rect, fmt, farbe)
    if hinweise is not None and (fmt.get("drehung") or effekt(fmt, "d3") and float((effekt(fmt, "d3") or {}).get("kontur", 0)) > 0 and False):
        hinweise.append("Die 3D-Drehung eines Diagrammteils wird in dieser Ausgabe nicht dargestellt.")
    w = effekt(fmt, "weich")
    if w:
        from core.layout.drucklayout.ausgabe.bild.bildeffekte import PX_PT, png_bytes, weiche_kanten
        from core.layout.drucklayout.ausgabe.rasterziel import RasterZiel
        sc = 2.0
        pw, ph = max(1, int(round(rect.width * sc))), max(1, int(round(rect.height * sc)))
        if pw * ph < 4_000_000:
            z = RasterZiel(engine, rect.width, rect.height, sc, (255, 255, 255, 0))
            if st is not None:
                z.draw_rect(Rect(0, 0, rect.width, rect.height), st)
            for ls in linie_stile(fmt.get("linie"), (0, 0, 0, 0), 0.0):
                z.draw_rect(Rect(0.5, 0.5, rect.width - 1, rect.height - 1), ls)
            _w, _h, roh = z.als_rgba()
            png = png_bytes(_w, _h, weiche_kanten(bytearray(roh), _w, _h, False, float(w.get("radius", 6)) * PX_PT * sc))
            b.draw_image(png, rect, smooth=True)
            return
    if st is not None:
        b.draw_rect(rect, st)
    if "linie" in fmt:
        rahmen_zeichnen(b, rect, fmt.get("linie"), standard_linie or (0, 0, 0, 255), 0.0)


# ---- Text ----------------------------------------------------------------------------------------------------------------------
def textwinkel(text_fmt: dict | None) -> float:
    """Der Drehwinkel des Textes aus ``feld``: ``winkel`` plus die Richtung (dreh90 +90, dreh270 −90, senkrecht wie dreh90)."""
    feld = (text_fmt or {}).get("feld") or {}
    w = float(feld.get("winkel", 0.0) or 0.0)
    r = feld.get("richtung")
    if r in ("dreh90", "senkrecht_rl", "vertikal", "asiatisch270"):
        w += 90
    elif r in ("dreh270", "senkrecht_lr"):
        w -= 90
    return w


def schrift(text_fmt: dict | None, standard: FontSpec, standard_farbe: tuple) -> tuple:
    """(FontSpec, Farbe, Effekt) aus dem Textformat eines Teils."""
    t = text_fmt or {}
    pt = float(t.get("groesse") or standard.size_pt)
    f = FontSpec(str(t.get("name") or standard.family), pt, 700 if t.get("fett", standard.weight >= 600) else 400, bool(t.get("kursiv", standard.italic)))
    return f, _farbe(t.get("farbe"), standard_farbe) if t.get("farbe") else standard_farbe, t.get("effekt")


def text_zeichnen(b, engine, text: str, rect: Rect, text_fmt: dict | None, standard: FontSpec, standard_farbe: tuple, ausr: str = "center", valign: str = "center",
                  raender_standard: dict | None = None, box: dict | None = None, objekt_dreh: float = 0.0) -> Rect:
    """Text in ``rect`` nach dem Textformat (Größe, Winkel, Ränder, Ausrichtung im Feld, Effekte). → das Feld um den Text (mit Rändern)."""
    from core.layout.drucklayout.ausgabe.text.texteffekte import zeichne_text_mit_effekt
    f, farbe, fx = schrift(text_fmt, standard, standard_farbe)
    feld = (text_fmt or {}).get("feld") or {}
    rd = {**{"l": 0.0, "o": 0.0, "r": 0.0, "u": 0.0}, **(raender_standard or {}), **(feld.get("raender") or {})}
    l_, o_, r_, u_ = (float(rd[k]) * PX for k in ("l", "o", "r", "u"))
    breite = engine.measure_text(text, f)
    m = engine.font_metrics(f)
    bw, bh = breite + l_ + r_, m.line_spacing + o_ + u_
    vert = str(feld.get("vertikal") or "")
    if vert:
        links = vert.endswith("_links")
        senk = vert.split("_")[0]
        x = rect.x if links else rect.x + (rect.width - bw) / 2
        y = {"oben": rect.y, "unten": rect.bottom - bh}.get(senk, rect.y + (rect.height - bh) / 2)
    else:
        x = rect.x if ausr == "left" else rect.right - bw if ausr == "right" else rect.x + (rect.width - bw) / 2
        y = rect.y if valign == "top" else rect.bottom - bh if valign == "bottom" else rect.y + (rect.height - bh) / 2
    feldrect = Rect(x, y, bw, bh)
    if box:                                                                       # Füllung, Linie und Effekte des Feldes hinter dem Text
        teil_zeichnen(b, engine, feldrect, box)
    winkel = textwinkel(text_fmt) - (objekt_dreh if feld.get("gerade") else 0.0)        # „Text nicht drehen“: gegen die Drehung des Objekts drehen
    px, py = x + l_, y + o_ + m.ascent
    if winkel:
        cx, cy = feldrect.x + bw / 2, feldrect.y + bh / 2
        b.push_state(translate=Point(cx, cy), rotate=winkel)
        px, py = -bw / 2 + l_, -bh / 2 + o_ + m.ascent
    if fx:
        zeichne_text_mit_effekt(b, engine, text, Point(px, py), f, farbe, fx)
    else:
        b.draw_text(text, Point(px, py), f, Style(color=farbe))
    if winkel:
        b.pop_state()
    return feldrect


# ---- Pfeile --------------------------------------------------------------------------------------------------------------------
def pfeil_zeichnen(b, spitze: tuple, von: tuple, art: str, groesse: float, farbe: tuple, breite: float) -> None:
    """Pfeilspitze (``pfeil``, ``offen``, ``oval``, ``raute``) an ``spitze``, Richtung von ``von`` nach ``spitze``."""
    if art in ("", "keiner", None):
        return
    dx, dy = spitze[0] - von[0], spitze[1] - von[1]
    l = math.hypot(dx, dy) or 1.0
    dx, dy = dx / l, dy / l
    nx, ny = -dy, dx
    s = max(5.0, breite * 3.0) * float(groesse or 1.0)
    st = Style(color=farbe, width=0, filled=True)
    if art == "pfeil":
        b.draw_path([("M", *spitze), ("L", spitze[0] - dx * s + nx * s * 0.5, spitze[1] - dy * s + ny * s * 0.5), ("L", spitze[0] - dx * s - nx * s * 0.5, spitze[1] - dy * s - ny * s * 0.5), ("Z",)], st, True, True)
    elif art == "offen":
        o = Style(color=farbe, width=max(1.0, breite), cap="round", join="round")
        b.draw_path([("M", spitze[0] - dx * s + nx * s * 0.5, spitze[1] - dy * s + ny * s * 0.5), ("L", *spitze), ("L", spitze[0] - dx * s - nx * s * 0.5, spitze[1] - dy * s - ny * s * 0.5)], o, True, True)
    elif art == "oval":
        b.draw_ellipse(Point(spitze[0] - dx * s * 0.4, spitze[1] - dy * s * 0.4), s * 0.45, s * 0.45, st)
    elif art == "raute":
        c = (spitze[0] - dx * s * 0.5, spitze[1] - dy * s * 0.5)
        b.draw_path([("M", *spitze), ("L", c[0] + nx * s * 0.4, c[1] + ny * s * 0.4), ("L", spitze[0] - dx * s, spitze[1] - dy * s), ("L", c[0] - nx * s * 0.4, c[1] - ny * s * 0.4), ("Z",)], st, True, True)
