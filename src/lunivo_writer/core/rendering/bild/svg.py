"""SVG ohne Qt: ein häufig gebrauchter Teil des Formats wird auf eine ``RenderTarget`` des Kerns gezeichnet.

Unterstützt: ``svg`` mit ``viewBox``/Größe, ``g``, ``defs``, ``use``, ``rect`` (auch ``rx``/``ry``), ``circle``, ``ellipse``, ``line``, ``polyline``, ``polygon``, ``path`` (alle Befehle
M L H V C S Q T A Z, absolut und relativ), ``text`` (einfache Zeilen), Transformationen (``matrix``, ``translate``, ``scale``, ``rotate``, ``skewX``, ``skewY``), Füllung und Strich
(Farben als Name, ``#rgb``, ``#rrggbb``, ``rgb()``; ``fill-rule``, Strichstärke, -enden, -ecken, -muster, Deckkraft), ``style``-Attribute, lineare und runde Verläufe (auch über ``href``).
Nicht gezeichnet werden Filter, Masken, Beschneidungspfade und eingebettete fremde Dokumente; solche Elemente stehen im Bericht der Fläche (``hinweise``)."""
from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

from lunivo_writer.core.geometrie import Point, Rect
from lunivo_writer.core.textsatz.engine import FontSpec
from lunivo_writer.core.rendering.ausgabe.backend import LinearGradient, RadialGradient, Style

_FARBEN = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff", "yellow": "#ffff00", "gray": "#808080", "grey": "#808080",
           "orange": "#ffa500", "purple": "#800080", "pink": "#ffc0cb", "brown": "#a52a2a", "cyan": "#00ffff", "magenta": "#ff00ff", "lime": "#00ff00", "navy": "#000080",
           "teal": "#008080", "silver": "#c0c0c0", "maroon": "#800000", "olive": "#808000", "aqua": "#00ffff", "fuchsia": "#ff00ff", "lightgray": "#d3d3d3", "darkgray": "#a9a9a9",
           "darkblue": "#00008b", "lightblue": "#add8e6", "gold": "#ffd700", "transparent": "#00000000"}
_KAPPA = 0.5522847498
_EINS = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
MAX_BYTES = 8_000_000


def _mal(m, a):
    return (m[0] * a[0] + m[2] * a[1], m[1] * a[0] + m[3] * a[1], m[0] * a[2] + m[2] * a[3], m[1] * a[2] + m[3] * a[3],
            m[0] * a[4] + m[2] * a[5] + m[4], m[1] * a[4] + m[3] * a[5] + m[5])


def _pt(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def _name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _zahl(text, standard: float = 0.0) -> float:
    if text is None:
        return standard
    m = re.match(r"\s*([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)\s*(px|pt|mm|cm|in|pc|%|em)?", str(text))
    if not m:
        return standard
    v, einheit = float(m.group(1)), m.group(2)
    return v * {"pt": 96 / 72, "mm": 96 / 25.4, "cm": 96 / 2.54, "in": 96.0, "pc": 16.0, "em": 16.0}.get(einheit or "", 1.0)


def _farbe(text, deckkraft: float = 1.0):
    if text is None:
        return None
    t = str(text).strip().lower()
    if t in ("none", ""):
        return None
    t = _FARBEN.get(t, t)
    try:
        if t.startswith("#"):
            h = t[1:]
            if len(h) in (3, 4):
                h = "".join(c * 2 for c in h)
            a = int(h[6:8], 16) / 255 if len(h) >= 8 else 1.0
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(255 * a * deckkraft))
        m = re.match(r"rgba?\(([^)]*)\)", t)
        if m:
            teile = [x.strip() for x in m.group(1).replace("/", ",").split(",")]
            werte = [float(x[:-1]) * 2.55 if x.endswith("%") else float(x) for x in teile[:3]]
            a = float(teile[3]) if len(teile) > 3 else 1.0
            return (int(werte[0]), int(werte[1]), int(werte[2]), int(255 * a * deckkraft))
    except (ValueError, IndexError):
        return None
    return None


def _transform(text) -> tuple:
    m = _EINS
    for name, args in re.findall(r"(\w+)\s*\(([^)]*)\)", text or ""):
        a = [float(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        if name == "matrix" and len(a) == 6:
            n = tuple(a)
        elif name == "translate":
            n = (1.0, 0.0, 0.0, 1.0, a[0], a[1] if len(a) > 1 else 0.0)
        elif name == "scale":
            n = (a[0], 0.0, 0.0, a[1] if len(a) > 1 else a[0], 0.0, 0.0)
        elif name == "rotate":
            w = math.radians(a[0])
            n = (math.cos(w), math.sin(w), -math.sin(w), math.cos(w), 0.0, 0.0)
            if len(a) >= 3:
                n = _mal(_mal((1.0, 0.0, 0.0, 1.0, a[1], a[2]), n), (1.0, 0.0, 0.0, 1.0, -a[1], -a[2]))
        elif name == "skewx":
            n = (1.0, 0.0, math.tan(math.radians(a[0])), 1.0, 0.0, 0.0)
        elif name == "skewy":
            n = (1.0, math.tan(math.radians(a[0])), 0.0, 1.0, 0.0, 0.0)
        else:
            continue
        m = _mal(m, n)
    return m


def _stil_attribute(e: ET.Element) -> dict:
    d = dict(e.attrib)
    for teil in (e.get("style") or "").split(";"):
        if ":" in teil:
            k, v = teil.split(":", 1)
            d[k.strip()] = v.strip()
    return d


_SCHRITT_BEFEHLE = re.compile(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)")


def pfad_ops(d: str) -> list:
    """Die Pfaddaten (``d``) als Anweisungen (M, L, C, Z; Bögen als Kubikkurven)."""
    ops, cx, cy, sx, sy, letzte_c, letzte_q, letzter = [], 0.0, 0.0, 0.0, 0.0, None, None, ""
    for b, args in _SCHRITT_BEFEHLE.findall(d or ""):
        z = [float(x) for x in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", args)]
        rel = b.islower()
        B = b.upper()
        i = 0
        while True:
            if B == "Z":
                ops.append(("Z",))
                cx, cy = sx, sy
                letzte_c = letzte_q = None
                break
            n = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7}[B]
            if i + n > len(z):
                break
            a = z[i:i + n]
            i += n
            ox, oy = (cx, cy) if rel else (0.0, 0.0)
            if B == "M":
                cx, cy = a[0] + ox, a[1] + oy
                sx, sy = cx, cy
                ops.append(("M", cx, cy))
                B = "L"
                letzte_c = letzte_q = None
            elif B == "L":
                cx, cy = a[0] + ox, a[1] + oy
                ops.append(("L", cx, cy))
                letzte_c = letzte_q = None
            elif B == "H":
                cx = a[0] + (cx if rel else 0.0)
                ops.append(("L", cx, cy))
                letzte_c = letzte_q = None
            elif B == "V":
                cy = a[0] + (cy if rel else 0.0)
                ops.append(("L", cx, cy))
                letzte_c = letzte_q = None
            elif B in ("C", "S"):
                if B == "C":
                    x1, y1, x2, y2, x, y = a[0] + ox, a[1] + oy, a[2] + ox, a[3] + oy, a[4] + ox, a[5] + oy
                else:
                    x1, y1 = (2 * cx - letzte_c[0], 2 * cy - letzte_c[1]) if letzte_c else (cx, cy)
                    x2, y2, x, y = a[0] + ox, a[1] + oy, a[2] + ox, a[3] + oy
                ops.append(("C", x1, y1, x2, y2, x, y))
                letzte_c, letzte_q = (x2, y2), None
                cx, cy = x, y
            elif B in ("Q", "T"):
                if B == "Q":
                    x1, y1, x, y = a[0] + ox, a[1] + oy, a[2] + ox, a[3] + oy
                else:
                    x1, y1 = (2 * cx - letzte_q[0], 2 * cy - letzte_q[1]) if letzte_q else (cx, cy)
                    x, y = a[0] + ox, a[1] + oy
                ops.append(("Q", x1, y1, x, y))
                letzte_q, letzte_c = (x1, y1), None
                cx, cy = x, y
            elif B == "A":
                x, y = a[5] + ox, a[6] + oy
                ops += _bogen(cx, cy, a[0], a[1], a[2], bool(a[3]), bool(a[4]), x, y)
                cx, cy = x, y
                letzte_c = letzte_q = None
            if i >= len(z):
                break
        letzter = b
    return ops


def _bogen(x1, y1, rx, ry, winkel, gross, links, x2, y2) -> list:
    """Elliptischer Bogen (SVG-Endpunktform) als Kubikkurven."""
    if (x1, y1) == (x2, y2) or not rx or not ry:
        return [("L", x2, y2)]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(winkel)
    c, s = math.cos(phi), math.sin(phi)
    dx, dy = (x1 - x2) / 2, (y1 - y2) / 2
    x1s, y1s = c * dx + s * dy, -s * dx + c * dy
    lam = x1s ** 2 / rx ** 2 + y1s ** 2 / ry ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    zaehler = rx ** 2 * ry ** 2 - rx ** 2 * y1s ** 2 - ry ** 2 * x1s ** 2
    nenner = rx ** 2 * y1s ** 2 + ry ** 2 * x1s ** 2
    k = math.sqrt(max(0.0, zaehler / nenner)) * (-1 if gross == links else 1)
    cxs, cys = k * rx * y1s / ry, -k * ry * x1s / rx
    cx, cy = c * cxs - s * cys + (x1 + x2) / 2, s * cxs + c * cys + (y1 + y2) / 2

    def winkel_(ux, uy, vx, vy):
        w = math.atan2(ux * vy - uy * vx, ux * vx + uy * vy)
        return w
    t1 = winkel_(1, 0, (x1s - cxs) / rx, (y1s - cys) / ry)
    dt = winkel_((x1s - cxs) / rx, (y1s - cys) / ry, (-x1s - cxs) / rx, (-y1s - cys) / ry)
    if not links and dt > 0:
        dt -= 2 * math.pi
    elif links and dt < 0:
        dt += 2 * math.pi
    n = max(1, int(math.ceil(abs(dt) / (math.pi / 2))))
    schritt = dt / n
    ops = []
    for i in range(n):
        a0, a1 = t1 + i * schritt, t1 + (i + 1) * schritt
        t = 4 / 3 * math.tan((a1 - a0) / 4)

        def punkt(w, dxw=0.0, dyw=0.0):
            px, py = rx * (math.cos(w) + dxw), ry * (math.sin(w) + dyw)
            return c * px - s * py + cx, s * px + c * py + cy
        p1 = punkt(a0, -t * math.sin(a0), t * math.cos(a0))
        p2 = punkt(a1, t * math.sin(a1), -t * math.cos(a1))
        p3 = punkt(a1)
        ops.append(("C", *p1, *p2, *p3))
    return ops


class _Svg:
    def __init__(self, wurzel: ET.Element, b, engine):
        self.b, self.engine, self.ids = b, engine, {}
        for e in wurzel.iter():
            if e.get("id"):
                self.ids[e.get("id")] = e

    def verlauf(self, ref: str, bbox, m, deckkraft: float):
        e = self.ids.get(ref.strip()[5:-1].strip("'\"#")) if ref.strip().startswith("url(") else None
        if e is None:
            return None
        tag = _name(e.tag)
        basis = e
        stops = [s for s in e if _name(s.tag) == "stop"]
        h = (e.get("{http://www.w3.org/1999/xlink}href") or e.get("href") or "").lstrip("#")
        if not stops and h in self.ids:
            stops = [s for s in self.ids[h] if _name(s.tag) == "stop"]
        if not stops:
            return None
        farben = []
        for s in stops:
            st = _stil_attribute(s)
            pos = st.get("offset", "0")
            p = float(pos[:-1]) / 100 if pos.endswith("%") else _zahl(pos)
            c = _farbe(st.get("stop-color", "#000000"), float(st.get("stop-opacity", 1)) * deckkraft) or (0, 0, 0, 0)
            farben.append((max(0.0, min(1.0, p)), c))
        bb = (e.get("gradientUnits") or "objectBoundingBox") == "objectBoundingBox"
        gm = _transform(e.get("gradientTransform"))
        x0, y0, bw, bh = bbox

        def pkt(x, y, prozent_von=None):
            if bb:
                x, y = x0 + x * bw, y0 + y * bh
            return _pt(m, *_pt(gm, x, y))

        def wert(name, standard, achse):
            t = e.get(name)
            if t is None:
                return standard
            if bb:
                return float(t[:-1]) / 100 if t.endswith("%") else float(t)
            return float(t[:-1]) / 100 * (bw if achse == "x" else bh) if t.endswith("%") else _zahl(t)
        if tag == "linearGradient":
            a, c = pkt(wert("x1", 0.0, "x"), wert("y1", 0.0, "y")), pkt(wert("x2", 1.0 if bb else bw, "x"), wert("y2", 0.0, "y"))
            return LinearGradient(Point(*a), Point(*c), tuple(farben))
        if tag == "radialGradient":
            mx, my = pkt(wert("cx", 0.5, "x"), wert("cy", 0.5, "y"))
            r = wert("r", 0.5 if bb else min(bw, bh) / 2, "x") * (bw if bb else 1.0)
            return RadialGradient(Point(mx, my), abs(r) * math.sqrt(abs(m[0] * m[3] - m[1] * m[2])), tuple(farben))
        return None

    def zeichne(self, e: ET.Element, m, erbe: dict) -> None:
        tag = _name(e.tag)
        if tag in ("defs", "title", "desc", "metadata", "style", "linearGradient", "radialGradient", "clipPath", "mask", "filter", "symbol"):
            if tag in ("filter", "mask", "clipPath") and hasattr(self.b, "hinweise"):
                self.b.hinweise.append("SVG-Filter, -Masken und -Beschneidungspfade werden nicht dargestellt.")
            return
        st = {**erbe, **{k: v for k, v in _stil_attribute(e).items() if k in _VERERBT or k in _EIGEN}}
        if st.get("display") == "none" or st.get("visibility") == "hidden":
            return
        m = _mal(m, _transform(e.get("transform")))
        deckkraft = float(st.get("opacity", 1)) if "opacity" in st else 1.0
        vererbt = {k: v for k, v in st.items() if k in _VERERBT}
        if tag in ("svg", "g", "a"):
            self.b.push_state(opacity=deckkraft)
            for k in e:
                self.zeichne(k, m, vererbt)
            self.b.pop_state()
            return
        if tag == "use":
            ziel = self.ids.get((e.get("{http://www.w3.org/1999/xlink}href") or e.get("href") or "").lstrip("#"))
            if ziel is not None:
                m2 = _mal(m, (1.0, 0.0, 0.0, 1.0, _zahl(e.get("x")), _zahl(e.get("y"))))
                self.b.push_state(opacity=deckkraft)
                self.zeichne(ziel, m2, vererbt)
                self.b.pop_state()
            return
        ops = self.ops(e, tag, st)
        if tag == "text":
            self.text(e, m, st)
            return
        if not ops:
            return
        self.b.push_state(opacity=deckkraft)
        self.malen(ops, m, st)
        self.b.pop_state()

    def ops(self, e, tag, st):
        if tag == "rect":
            x, y, w, h = _zahl(e.get("x")), _zahl(e.get("y")), _zahl(e.get("width")), _zahl(e.get("height"))
            rx, ry = _zahl(e.get("rx"), -1), _zahl(e.get("ry"), -1)
            if w <= 0 or h <= 0:
                return []
            if rx < 0 and ry < 0:
                return [("M", x, y), ("L", x + w, y), ("L", x + w, y + h), ("L", x, y + h), ("Z",)]
            rx, ry = (ry if rx < 0 else rx), (rx if ry < 0 else ry)
            rx, ry = min(rx, w / 2), min(ry, h / 2)
            kx, ky, r, b = rx * _KAPPA, ry * _KAPPA, x + w, y + h
            return [("M", x + rx, y), ("L", r - rx, y), ("C", r - rx + kx, y, r, y + ry - ky, r, y + ry), ("L", r, b - ry), ("C", r, b - ry + ky, r - rx + kx, b, r - rx, b),
                    ("L", x + rx, b), ("C", x + rx - kx, b, x, b - ry + ky, x, b - ry), ("L", x, y + ry), ("C", x, y + ry - ky, x + rx - kx, y, x + rx, y), ("Z",)]
        if tag in ("circle", "ellipse"):
            cx, cy = _zahl(e.get("cx")), _zahl(e.get("cy"))
            rx = ry = _zahl(e.get("r")) if tag == "circle" else 0.0
            if tag == "ellipse":
                rx, ry = _zahl(e.get("rx")), _zahl(e.get("ry"))
            if rx <= 0 or ry <= 0:
                return []
            kx, ky = rx * _KAPPA, ry * _KAPPA
            return [("M", cx + rx, cy), ("C", cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry), ("C", cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy),
                    ("C", cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry), ("C", cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy), ("Z",)]
        if tag == "line":
            return [("M", _zahl(e.get("x1")), _zahl(e.get("y1"))), ("L", _zahl(e.get("x2")), _zahl(e.get("y2")))]
        if tag in ("polyline", "polygon"):
            z = [float(x) for x in re.findall(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?", e.get("points") or "")]
            pts = list(zip(z[0::2], z[1::2]))
            return ([("M", *pts[0])] + [("L", *q) for q in pts[1:]] + ([("Z",)] if tag == "polygon" else [])) if pts else []
        if tag == "path":
            return pfad_ops(e.get("d") or "")
        return []

    def malen(self, ops: list, m, st: dict) -> None:
        xs = [op[i] for op in ops if op[0] != "Z" for i in range(1, len(op), 2)]
        ys = [op[i] for op in ops if op[0] != "Z" for i in range(2, len(op), 2)]
        bbox = (min(xs), min(ys), (max(xs) - min(xs)) or 1.0, (max(ys) - min(ys)) or 1.0) if xs else (0, 0, 1, 1)
        geom = []
        for op in ops:
            if op[0] == "Z":
                geom.append(op)
            else:
                p = []
                for i in range(1, len(op), 2):
                    p += list(_pt(m, op[i], op[i + 1]))
                geom.append((op[0],) + tuple(p))
        massstab = math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1.0
        fa = float(st.get("fill-opacity", 1))
        fuelltext = st.get("fill", "#000000")
        gerade = st.get("fill-rule", "nonzero") == "evenodd"
        if str(fuelltext).strip().startswith("url("):
            v = self.verlauf(fuelltext, bbox, m, fa)
            if v is not None:
                self.b.draw_path(geom, Style(color=(0, 0, 0, 255), width=0, filled=True, fill=v), True, not gerade)
        else:
            fc = _farbe(fuelltext, fa)
            if fc is not None and fc[3] > 0:
                self.b.draw_path(geom, Style(color=fc, width=0, filled=True), True, not gerade)
        sc = _farbe(st.get("stroke"), float(st.get("stroke-opacity", 1)))
        breite = _zahl(st.get("stroke-width"), 1.0) * massstab
        if sc is not None and sc[3] > 0 and breite > 0:
            muster = None
            da = st.get("stroke-dasharray")
            if da and da != "none":
                z = [_zahl(x) / max(0.01, _zahl(st.get("stroke-width"), 1.0)) for x in re.split(r"[\s,]+", da.strip()) if x]
                muster = tuple(z) if z and any(z) else None
            self.b.draw_path(geom, Style(color=sc, width=breite, filled=False, dash=muster, cap={"round": "round", "square": "square"}.get(st.get("stroke-linecap"), "flat"),
                                         join={"round": "round", "bevel": "bevel"}.get(st.get("stroke-linejoin"), "miter")), True, True)

    def text(self, e, m, st) -> None:
        inhalt = "".join(e.itertext()).strip()
        if not inhalt:
            return
        px = _zahl(st.get("font-size"), 16.0)
        massstab = math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1.0
        fam = (st.get("font-family") or "Liberation Sans").split(",")[0].strip().strip("'\"")
        font = FontSpec(fam, px * massstab * 72 / 96, 700 if st.get("font-weight") in ("bold", "700", "800", "900") else 400, st.get("font-style") == "italic")
        x, y = _zahl(e.get("x")), _zahl(e.get("y"))
        breite = self.engine.measure_text(inhalt, font)
        anker = st.get("text-anchor", "start")
        ax, ay = _pt(m, x, y)
        ax -= breite / 2 if anker == "middle" else breite if anker == "end" else 0.0
        fc = _farbe(st.get("fill", "#000000"), float(st.get("fill-opacity", 1))) or (0, 0, 0, 255)
        self.b.draw_text(inhalt, Point(ax, ay), font, Style(color=fc))


_VERERBT = {"fill", "fill-opacity", "fill-rule", "stroke", "stroke-width", "stroke-opacity", "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "font-size", "font-family",
            "font-weight", "font-style", "text-anchor", "visibility"}
_EIGEN = {"opacity", "display"}


def _parsen(daten: bytes):
    if len(daten) > MAX_BYTES or b"<!ENTITY" in daten:                          # keine Entitäten (Entitätsexplosion) und keine übergroßen Dateien
        return None
    try:
        return ET.fromstring(daten)
    except ET.ParseError:
        return None


def ist_svg(daten: bytes) -> bool:
    kopf = daten[:2048].lstrip(b"\xef\xbb\xbf \t\r\n")
    return b"<svg" in daten[:4096] or (kopf.startswith(b"<?xml") and b"<svg" in daten[:8192])


def svg_masse(daten: bytes):
    """Die natürliche Größe in Bildpunkten (Breite, Höhe) aus ``width``/``height`` oder ``viewBox``; ``None``, wenn keine Größe gefunden wird."""
    w = _parsen(daten)
    if w is None or _name(w.tag) != "svg":
        return None
    vb = [float(x) for x in re.split(r"[\s,]+", (w.get("viewBox") or "").strip()) if x]
    b, h = _zahl(w.get("width"), 0.0), _zahl(w.get("height"), 0.0)
    if str(w.get("width", "")).endswith("%"):
        b = 0.0
    if str(w.get("height", "")).endswith("%"):
        h = 0.0
    if (not b or not h) and len(vb) == 4 and vb[2] > 0 and vb[3] > 0:
        b, h = (b or vb[2], h or vb[3]) if not (b or h) else ((b, b * vb[3] / vb[2]) if b else (h * vb[2] / vb[3], h))
    return (b, h) if b > 0 and h > 0 else None


def svg_zeichnen(daten: bytes, b, ziel: Rect, engine=None) -> bool:
    """Das SVG in ``ziel`` auf ``b`` zeichnen (Seitenverhältnis bleibt, zentriert, nichts außerhalb). ``False``, wenn es kein lesbares SVG ist."""
    wurzel = _parsen(daten)
    if wurzel is None or _name(wurzel.tag) != "svg":
        return False
    if engine is None:
        from lunivo_writer.core.rendering.text.textpfad import gemeinsame_engine
        engine = gemeinsame_engine()
    vb = [float(x) for x in re.split(r"[\s,]+", (wurzel.get("viewBox") or "").strip()) if x]
    masse = svg_masse(daten)
    if len(vb) == 4 and vb[2] > 0 and vb[3] > 0:
        x0, y0, w, h = vb
    elif masse:
        x0, y0, w, h = 0.0, 0.0, masse[0], masse[1]
    else:
        x0, y0, w, h = 0.0, 0.0, ziel.width, ziel.height
    f = min(ziel.width / w, ziel.height / h)
    m = (f, 0.0, 0.0, f, ziel.x + (ziel.width - w * f) / 2 - x0 * f, ziel.y + (ziel.height - h * f) / 2 - y0 * f)
    b.push_state(clip=ziel)
    try:
        _Svg(wurzel, b, engine).zeichne(wurzel, m, {})
    finally:
        b.pop_state()
    return True


def svg_rgba(daten: bytes, breite_px: int = 0, engine=None):
    """Das SVG gerastert: ``(breite, hoehe, RGBA)``; Größe aus ``width``/``height``/``viewBox`` (mindestens doppelt so fein wie 96 dpi, höchstens 3000 Pixel); sonst ``None``."""
    from lunivo_writer.core.rendering.ausgabe.rasterziel import RasterZiel
    masse = svg_masse(daten) or (300.0, 150.0)
    f = max(2.0, breite_px / masse[0]) if breite_px else 2.0
    b, h = max(1, round(masse[0] * f)), max(1, round(masse[1] * f))
    k = min(1.0, 3000 / max(b, h))
    b, h = max(1, round(b * k)), max(1, round(h * k))
    if engine is None:
        from lunivo_writer.core.rendering.text.textpfad import gemeinsame_engine
        engine = gemeinsame_engine()
    ziel = RasterZiel(engine, b, h, 1.0, (255, 255, 255, 0))
    if not svg_zeichnen(daten, ziel, Rect(0, 0, b, h), engine):
        return None
    bb, hh, roh = ziel.als_rgba()
    return bb, hh, bytearray(roh)
