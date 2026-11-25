"""3D-Format und 3D-Drehung von Bildern ohne Qt, als reine Pufferoperationen auf RGBA-Bytes (nicht vormultipliziert).

* ``extrusion``: die Tiefe des 3D-Formats (die Form nach hinten gestapelt, Material, Beleuchtung, Kontur an Vorder- und Rückseite, unterer Abschluss);
* ``nachbearbeitet``: oberer Abschluss (Fase, von links oben beleuchtet) und danach die Drehung im Raum mit Perspektive;
* ``gedreht``: nur die Drehung (Schatten, Leuchten und Tiefe gehören zur gedrehten Form).

Alle Maße in Pixeln des Puffers; ``sc`` rechnet Punkte (96 dpi) in Pufferpixel um. Rasterer und PDF-Ziel zeichnen die Ergebnisse wie jedes andere Bild."""
from __future__ import annotations

import colorsys
import math

from .bildeffekte import PX_PT, form_alpha, weichgezeichnet


# ---- Bausteine ---------------------------------------------------------------------------------------------------------------------
def _rgb(text, standard: str) -> tuple:
    from .backend import rgba
    try:
        return tuple(rgba(text or standard)[:3])
    except (ValueError, IndexError, TypeError):
        return tuple(rgba(standard)[:3])


def stufenfarbe(basis: tuple, material: str, licht: str, t: float) -> tuple:
    """Farbe der Tiefe in Stufe ``t`` (0 = vorn, 1 = hinten) nach Material und Beleuchtung (wie bei den Texteffekten)."""
    f = {"plastik": 1.25 - 0.5 * t, "metall": 1.0 + 0.45 * math.sin(t * math.pi * 2), "dunkel": 0.6 + 0.4 * (1 - t), "weich": 1.15 - 0.25 * t, "hell": 1.3}.get(material, 1.0)
    f *= {"weich": 1.08, "hart": 0.8 + 0.5 * (1 - t), "kontrast": 0.7 + 0.7 * t}.get(licht, 1.0)
    h, l, s = colorsys.rgb_to_hls(*(v / 255.0 for v in basis))
    r, g, b = (int(v * 255 + 0.5) for v in colorsys.hls_to_rgb(h, max(0.0, min(1.0, l * max(0.3, f))), s))
    if licht == "warm":
        r, b = min(255, r + 25), max(0, b - 20)
    elif licht == "kalt":
        r, b = max(0, r - 20), min(255, b + 25)
    return r, g, b


def tiefe_richtung(dreh: dict | None) -> tuple:
    """Einheitsvektor, in dem die Tiefe nach hinten läuft: schräg nach rechts unten, bei gedrehtem Objekt (3D-Drehung X/Y) entsprechend verschoben."""
    dx, dy = 0.7, 0.7
    if dreh:
        dx += math.sin(math.radians(float(dreh.get("y", 0.0)))) * 0.8
        dy -= math.sin(math.radians(float(dreh.get("x", 0.0)))) * 0.8
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def dreht(dreh: dict | None) -> bool:
    return bool(dreh) and any(abs(float(dreh.get(k, 0.0))) > 0.01 for k in ("x", "y", "z"))


def hat_abschluss(fx: dict | None) -> bool:
    return ((((fx or {}).get("d3") or {}).get("oben") or {}).get("art", "keine")) != "keine"


def braucht_nachbearbeitung(fx: dict | None) -> bool:
    """Ändert der Effekt das Bild selbst (oberer Abschluss oder Drehung im Raum)?"""
    return dreht((fx or {}).get("drehung")) or hat_abschluss(fx)


def hat_extrusion(fx: dict | None) -> bool:
    d3 = (fx or {}).get("d3") or {}
    return float(d3.get("tiefe", 0) or 0) > 0 or float(d3.get("kontur", 0) or 0) > 0


def _einbetten(alpha, w: int, h: int, pad: int) -> bytearray:
    """Die Alphaebene in die um ``pad`` Pixel größere Fläche setzen."""
    W, H = w + 2 * pad, h + 2 * pad
    aus = bytearray(W * H)
    for y in range(h):
        o = (y + pad) * W + pad
        aus[o:o + w] = alpha[y * w:(y + 1) * w]
    return aus


def _verschoben_zeile(zeile: bytes, sx: int) -> bytes:
    n = len(zeile)
    if sx == 0:
        return zeile
    if abs(sx) >= n:
        return bytes(n)
    return (bytes(sx) + zeile[:n - sx]) if sx > 0 else (zeile[-sx:] + bytes(-sx))


def _kombiniert(alpha, W: int, H: int, rad: float, funktion) -> bytearray:
    """Die Alphaebene mit sich selbst in acht um ``rad`` verschobenen Lagen kombiniert (Maximum: aufgeweitet, Minimum: verkleinert)."""
    r = max(1, int(round(rad)))
    aus = bytearray(alpha)
    zeilen = [bytes(alpha[y * W:(y + 1) * W]) for y in range(H)]
    leer = bytes(W)
    for k in range(8):
        a = k * math.pi / 4
        sx, sy = int(round(math.cos(a) * r)), int(round(math.sin(a) * r))
        for y in range(H):
            qy = y - sy
            zeile = _verschoben_zeile(zeilen[qy] if 0 <= qy < H else leer, sx)
            alt = aus[y * W:(y + 1) * W]
            aus[y * W:(y + 1) * W] = bytes(map(funktion, alt, zeile))
    return aus


def _laeufe(alpha, W: int, H: int) -> tuple:
    """Die Form als Läufe voller Deckkraft ``(y, x0, x1)`` und Einzelpunkte ``(y, x, a)`` (Ränder): so lässt sich die Form schnell stempeln."""
    laeufe, punkte = [], []
    for y in range(H):
        zeile = alpha[y * W:(y + 1) * W]
        x = 0
        while x < W:
            a = zeile[x]
            if a == 0:
                x += 1
            elif a == 255:
                x0 = x
                while x < W and zeile[x] == 255:
                    x += 1
                laeufe.append((y, x0, x))
            else:
                punkte.append((y, x, a))
                x += 1
    return laeufe, punkte


def _stempeln(ziel: bytearray, W: int, H: int, form: tuple, ox: int, oy: int, farbe: tuple) -> None:
    """Die Form in ``farbe`` (r, g, b) um ``(ox, oy)`` verschoben „über“ den Puffer legen."""
    laeufe, punkte = form
    px = bytes((farbe[0], farbe[1], farbe[2], 255))
    for y, x0, x1 in laeufe:
        dy = y + oy
        if 0 <= dy < H:
            a0, a1 = max(0, x0 + ox), min(W, x1 + ox)
            if a1 > a0:
                o = (dy * W + a0) * 4
                ziel[o:o + (a1 - a0) * 4] = px * (a1 - a0)
    for y, x, a in punkte:
        dy, dx = y + oy, x + ox
        if 0 <= dy < H and 0 <= dx < W:
            o = (dy * W + dx) * 4
            oa = a / 255.0
            da = ziel[o + 3] / 255.0
            na = oa + da * (1 - oa)
            if na > 0:
                for i in range(3):
                    ziel[o + i] = int((farbe[i] * oa + ziel[o + i] * da * (1 - oa)) / na + 0.5)
                ziel[o + 3] = min(255, int(na * 255 + 0.5))


# ---- 3D-Format: Tiefe --------------------------------------------------------------------------------------------------------------
def extrusion(daten, w: int, h: int, ellipse: bool, d3: dict, dreh: dict | None, sc: float) -> tuple:
    """Die Tiefe des 3D-Formats hinter dem Bild → ``(W, H, RGBA, pad)``; das Bild liegt in dem Puffer um ``pad`` Pixel eingerückt und wird danach vorn darübergezeichnet."""
    tiefe = max(0.0, float(d3.get("tiefe", 0) or 0)) * PX_PT * sc
    unten = d3.get("unten") if (d3.get("unten") or {}).get("art", "keine") != "keine" else None
    if unten and tiefe > 0:
        tiefe += max(0.0, float(unten.get("hoehe", 0.0))) * PX_PT * sc * 0.5       # unterer Abschluss: die Rückseite wird um seine Höhe tiefer
    kontur = max(0.0, float(d3.get("kontur", 0) or 0)) * PX_PT * sc
    rad_unten = max(1.0, float(unten.get("breite", 4.0)) * PX_PT * sc) if unten else 0.0
    dx, dy = tiefe_richtung(dreh)
    pad = int(math.ceil(tiefe + kontur + rad_unten)) + 3
    W, H = w + 2 * pad, h + 2 * pad
    flaeche = _einbetten(form_alpha(daten, w, h, ellipse), w, h, pad)
    ziel = bytearray(W * H * 4)
    basis = _rgb(d3.get("tiefe_farbe"), "#808080")
    material, licht = d3.get("material", "matt"), d3.get("beleuchtung", "neutral")
    ox, oy = int(round(dx * tiefe)), int(round(dy * tiefe))
    koerper = _laeufe(flaeche, W, H)
    if unten and tiefe > 0:                                                              # unterer Abschluss: ein dunkler Rand um das hintere Ende
        dunkel = tuple(int(v / 1.5) for v in stufenfarbe(basis, material, licht, 1.0))
        _stempeln(ziel, W, H, _laeufe(_kombiniert(flaeche, W, H, rad_unten, max), W, H), ox, oy, dunkel)
    if kontur > 0:                                                                       # Kontur am hinteren und am vorderen Ende
        ring = _laeufe(_kombiniert(flaeche, W, H, kontur, max), W, H)
        farbe = _rgb(d3.get("kontur_farbe"), "#202124")
        _stempeln(ziel, W, H, ring, ox, oy, farbe)
        _stempeln(ziel, W, H, ring, 0, 0, farbe)
    n = int(min(90, max(1, tiefe))) if tiefe > 0 else 0
    stufen = 8
    for k in range(n, 0, -1):
        t = k / n
        band = min(stufen - 1, int(t * stufen))
        _stempeln(ziel, W, H, koerper, int(round(dx * tiefe * t)), int(round(dy * tiefe * t)), stufenfarbe(basis, material, licht, (band + 0.5) / stufen))
    return W, H, ziel, pad


# ---- Oberer Abschluss ---------------------------------------------------------------------------------------------------------------
def _gradient(stops: list, t: float) -> tuple:
    t = max(0.0, min(1.0, t))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if t <= p1:
            u = 0.0 if p1 <= p0 else (t - p0) / (p1 - p0)
            return tuple(c0[i] + (c1[i] - c0[i]) * max(0.0, min(1.0, u)) for i in range(4))
    return stops[-1][1]


def _licht(band, w: int, h: int, art: str, st: float, umgekehrt: bool = False) -> list:
    """Das Band mit Licht von links oben (``st`` = Stärke 0…1) als Überlagerung ``[(r, g, b, a)]`` je Pixel (nur dort gesetzt, wo das Band liegt)."""
    hell, dunkel = (255, 255, 255, 255 * st), (0, 0, 0, 255 * st)
    if umgekehrt:
        hell, dunkel = dunkel, hell
    if art == "rahmen":
        stops = [(0.0, (0, 0, 0, 255 * st * 0.7)), (1.0, (0, 0, 0, 255 * st * 0.7))]
    elif art in ("winkel", "kreuz"):
        stops = [(0.0, hell), (0.499, hell), (0.501, dunkel), (1.0, dunkel)]
    elif art == "weich":
        stops = [(0.0, (255, 255, 255, 255 * st * 0.8)), (0.6, (255, 255, 255, 0)), (1.0, (0, 0, 0, 255 * st * 0.3))]
    else:
        stops = [(0.0, hell), (0.5, (128, 128, 128, 0)), (1.0, dunkel)]
    nenner = float(w * w + h * h) or 1.0
    aus = [None] * (w * h)
    for y in range(h):
        for x in range(w):
            b = band[y * w + x]
            if b:
                c = _gradient(stops, ((x + 0.5) * w + (y + 0.5) * h) / nenner)
                aus[y * w + x] = (c[0], c[1], c[2], c[3] * b / 255.0)
    return aus


def _aufgelegt(puffer: bytearray, ueber: list, w: int, h: int) -> None:
    """Die Überlagerung auf den Puffer legen, ohne die Deckkraft des Puffers zu ändern (Quelle über Ziel, nur wo das Ziel liegt)."""
    for i, c in enumerate(ueber):
        if c is None:
            continue
        o = i * 4
        oa = c[3] / 255.0
        for k in range(3):
            puffer[o + k] = int(puffer[o + k] * (1 - oa) + c[k] * oa + 0.5)


def abschluss_oben(daten, w: int, h: int, ellipse: bool, ab: dict, sc: float) -> bytearray:
    """Oberer Abschluss: ein Rand der Breite ``breite`` rundum, von links oben beleuchtet; ``hoehe`` bestimmt die Stärke von Licht und Schatten.
    Arten: rund, winkel, weich, kreuz (äußere Hälfte so, innere umgekehrt), rahmen (gleichmäßig dunkel). Ergebnis: das Bild in seiner Form (Alpha)."""
    art = ab.get("art", "keine")
    out = bytearray(daten)
    out[3::4] = form_alpha(daten, w, h, ellipse)
    if art == "keine":
        return out
    rad = max(1.0, min(float(ab.get("breite", 4.0)) * PX_PT * sc, min(w, h) / 2 - 1))
    st = max(0.1, min(0.9, 0.15 + float(ab.get("hoehe", 6.0)) / 20.0 * 0.55))
    maske = bytearray(out[3::4])

    def band(aussen, innen):
        return bytearray(max(0, a - i) for a, i in zip(aussen, innen))
    voll = _kombiniert(maske, w, h, rad, min)
    if art == "kreuz":
        halb = _kombiniert(maske, w, h, rad / 2, min)
        _aufgelegt(out, _licht(band(maske, halb), w, h, art, st), w, h)
        _aufgelegt(out, _licht(band(halb, voll), w, h, art, st, True), w, h)
    else:
        b = band(maske, voll)
        if art in ("rund", "weich"):
            b = weichgezeichnet(b, w, h, rad * 0.5)
        _aufgelegt(out, _licht(b, w, h, art, st), w, h)
    return out


# ---- Drehung im Raum ------------------------------------------------------------------------------------------------------------------
def _projektion(w: int, h: int, dreh: dict) -> tuple:
    """(Zielviereck, Breite, Höhe) der gedrehten Fläche: Drehung um X, Y, Z und Perspektive (Sichtwinkel ``persp``, 0 = parallel), eingepasst in ``w`` × ``h``."""
    x, y, z, pers = (float(dreh.get(k, 0.0)) for k in ("x", "y", "z", "persp"))
    a, b, c = math.radians(x), math.radians(y), math.radians(z)
    punkte = []
    for px, py in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)):
        X, Y, Z = px, py, 0.0
        Y, Z = Y * math.cos(a) - Z * math.sin(a), Y * math.sin(a) + Z * math.cos(a)
        X, Z = X * math.cos(b) + Z * math.sin(b), -X * math.sin(b) + Z * math.cos(b)
        X, Y = X * math.cos(c) - Y * math.sin(c), X * math.sin(c) + Y * math.cos(c)
        punkte.append((X, Y, Z))
    if pers > 1:
        d = max(w, h) / (2 * math.tan(math.radians(min(pers, 150.0)) / 2))
        punkte = [(X * d / max(d * 0.1, d - Z), Y * d / max(d * 0.1, d - Z), Z) for X, Y, Z in punkte]
    xs, ys = [q[0] for q in punkte], [q[1] for q in punkte]
    f = min(1.0, w / max(1.0, max(xs) - min(xs)), h / max(1.0, max(ys) - min(ys)))
    mx, my = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
    return [(w / 2 + (q[0] - mx) * f, h / 2 + (q[1] - my) * f) for q in punkte], (max(xs) - min(xs)) * f, (max(ys) - min(ys)) * f


def _homographie(von: list, nach: list) -> list | None:
    """Die 3×3-Abbildung, die die vier Punkte ``von`` auf ``nach`` legt (Gauß-Verfahren); ``None``, wenn entartet."""
    m = []
    for (x, y), (u, v) in zip(von, nach):
        m.append([x, y, 1, 0, 0, 0, -u * x, -u * y, u])
        m.append([0, 0, 0, x, y, 1, -v * x, -v * y, v])
    for i in range(8):
        p = max(range(i, 8), key=lambda r: abs(m[r][i]))
        if abs(m[p][i]) < 1e-12:
            return None
        m[i], m[p] = m[p], m[i]
        for r in range(8):
            if r != i:
                f = m[r][i] / m[i][i]
                m[r] = [a - f * b for a, b in zip(m[r], m[i])]
    k = [m[i][8] / m[i][i] for i in range(8)]
    return [[k[0], k[1], k[2]], [k[3], k[4], k[5]], [k[6], k[7], 1.0]]


def gedreht(daten, w: int, h: int, ellipse: bool, dreh: dict, gerade: bool = False) -> bytearray:
    """Das Bild im Raum gedreht (``x``, ``y``, ``z`` Grad, ``persp``); gleiche Größe, die Fläche passt vollständig hinein. ``gerade``: der Inhalt bleibt aufrecht
    und wird nur so verkleinert, dass er in die gedrehte Fläche passt."""
    quelle = bytearray(daten)
    quelle[3::4] = form_alpha(daten, w, h, ellipse)
    ziel, bw, bh = _projektion(w, h, dreh)
    out = bytearray(w * h * 4)
    if gerade:
        f = min(1.0, bw / w, bh / h) * 0.9
        abbildung = [[1 / f, 0, w / 2 - w / (2 * f)], [0, 1 / f, h / 2 - h / (2 * f)], [0, 0, 1]]
    else:
        abbildung = _homographie(ziel, [(0, 0), (w, 0), (w, h), (0, h)])
        if abbildung is None:
            return quelle
    xs, ys = [p[0] for p in ziel], [p[1] for p in ziel]
    x0, x1 = max(0, int(min(xs)) - 1), min(w, int(max(xs)) + 2)
    y0, y1 = max(0, int(min(ys)) - 1), min(h, int(max(ys)) + 2)
    (a, b, c), (d, e, f_), (g, hh, i) = abbildung
    for y in range(y0, y1):
        py = y + 0.5
        for x in range(x0, x1):
            px = x + 0.5
            n = g * px + hh * py + i
            if abs(n) < 1e-9:
                continue
            u, v = (a * px + b * py + c) / n, (d * px + e * py + f_) / n
            rand = min(u, w - u, v, h - v) + 0.5                                      # Randabdeckung: weicher Rand der gedrehten Fläche
            if rand <= 0:
                continue
            fu, fv = u - 0.5, v - 0.5
            iu, iv = int(math.floor(fu)), int(math.floor(fv))
            wu, wv = fu - iu, fv - iv
            iu0, iu1 = min(w - 1, max(0, iu)), min(w - 1, max(0, iu + 1))
            iv0, iv1 = min(h - 1, max(0, iv)), min(h - 1, max(0, iv + 1))
            r = gr = bl = al = 0.0
            for qx, qy, wt in ((iu0, iv0, (1 - wu) * (1 - wv)), (iu1, iv0, wu * (1 - wv)), (iu0, iv1, (1 - wu) * wv), (iu1, iv1, wu * wv)):
                o = (qy * w + qx) * 4
                pa = quelle[o + 3] * wt
                r += quelle[o] * pa
                gr += quelle[o + 1] * pa
                bl += quelle[o + 2] * pa
                al += pa
            if al > 0:
                o = (y * w + x) * 4
                out[o], out[o + 1], out[o + 2] = int(r / al + 0.5), int(gr / al + 0.5), int(bl / al + 0.5)
                out[o + 3] = min(255, int(al * min(1.0, rand) + 0.5))
    return out


def nachbearbeitet(daten, w: int, h: int, ellipse: bool, fx: dict, sc: float) -> bytearray:
    """Das Bild für das Zeichnen vorbereiten: oberer Abschluss des 3D-Formats eingearbeitet, dann im Raum gedreht. Die Form ist danach schon ausgeschnitten
    (die Ellipse gilt nicht mehr)."""
    puffer = daten
    if hat_abschluss(fx):
        puffer = abschluss_oben(puffer, w, h, ellipse, fx["d3"]["oben"], sc)
        ellipse = False
    d = fx.get("drehung")
    if dreht(d):
        puffer = gedreht(puffer, w, h, ellipse, d, bool(d.get("text_gerade")))
    return puffer
