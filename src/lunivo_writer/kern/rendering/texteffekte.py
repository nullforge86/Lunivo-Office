"""Texteffekte im Kern, ohne Qt: Farbverlauf, Muster-/Textur-/Bildfüllung, Kontur, Schatten, Leuchten, Spiegelung und 3D-Tiefe über den Glyphenpfaden des Textes.

Ein Effekt (``fx``) ist ein Wörterbuch (Schlüssel wie im Zeichenformat ``effekt``): ``verlauf``, ``kontur_verlauf``, ``kontur_form``, ``schatten``, ``reflektion``, ``leuchten``,
``fuell_pinsel``, ``d3``; Längen in Punkt, Prozentwerte 0…100. Gezeichnet wird mit den Pfadmitteln jeder Zeichenfläche (``draw_path``, ``draw_shadow``)."""
from __future__ import annotations

import base64
import json
import math

from lunivo_writer.kern.geometrie import Point
from .backend import ImageFill, LinearGradient, PatternFill, Style, TextureFill, rgba

PX = 96.0 / 72.0


def effekt_lesen(wert) -> dict:
    """Der Effekt aus dem Zeichenformat (Wörterbuch oder JSON-Text); sonst leer."""
    if isinstance(wert, dict):
        return wert
    try:
        d = json.loads(wert) if wert else {}
    except (TypeError, ValueError):
        return {}
    return d if isinstance(d, dict) else {}


def _farbe(text, standard=(0, 0, 0, 255), transparenz: float = 0.0):
    try:
        r, g, b, _a = rgba(text or "#000000")
    except (ValueError, IndexError, TypeError, AttributeError):
        r, g, b, _a = standard
    return (r, g, b, int(255 * max(0.0, min(1.0, 1.0 - transparenz / 100.0))))


def _abbilden(ops: list, a: float, b: float, c: float, d: float, e: float, f: float) -> list:
    """Die Pfadanweisungen affin abgebildet: x' = a·x + c·y + e, y' = b·x + d·y + f."""
    aus = []
    for op in ops:
        if op[0] == "Z":
            aus.append(op)
        elif op[0] in ("M", "L", "Q", "C"):
            punkte = []
            for i in range(1, len(op), 2):
                punkte += [a * op[i] + c * op[i + 1] + e, b * op[i] + d * op[i + 1] + f]
            aus.append((op[0],) + tuple(punkte))
        else:
            aus.append(op)
    return aus


def _schranken(ops: list):
    xs = [op[i] for op in ops if op[0] in ("M", "L", "Q", "C") for i in range(1, len(op), 2)]
    ys = [op[i] for op in ops if op[0] in ("M", "L", "Q", "C") for i in range(2, len(op), 2)]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0.0, 0.0, 0.0, 0.0)


def _verlauf(schranken, v: dict) -> LinearGradient:
    x0, y0, x1, y1 = schranken
    w = math.radians(float(v.get("winkel", 90)))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    r = (abs(math.cos(w)) * (x1 - x0) + abs(math.sin(w)) * (y1 - y0)) / 2 or 1.0
    dx, dy = math.cos(w) * r, math.sin(w) * r
    return LinearGradient(Point(mx - dx, my - dy), Point(mx + dx, my + dy), ((0.0, _farbe(v.get("farbe1"))), (1.0, _farbe(v.get("farbe2"), (255, 255, 255, 255)))))


def _pinsel(d: dict, farbe):
    art = d.get("art", "muster")
    if art == "muster":
        return PatternFill(str(d.get("key", "rein")), str(d.get("farbe") or "#000000"), d.get("grund") or None)
    if art == "textur":
        return TextureFill(str(d.get("key", "papier")))
    if art == "bild":
        try:
            return ImageFill(base64.b64decode(d.get("bild_b64", "")))
        except (ValueError, TypeError):
            return None
    return None


def _warp_y(art: str, y: float, u: float, hoehe: float, mitte_y: float) -> float:
    """Die Höhe eines Punktes nach der Textverformung ``art`` (``u``: Lage 0..1 in der Breite des Textes)."""
    if art == "bogen":
        return y - hoehe * 0.7 * math.sin(math.pi * u)
    if art == "bogen_unten":
        return y + hoehe * 0.7 * math.sin(math.pi * u)
    if art == "welle":
        return y + hoehe * 0.4 * math.sin(2 * math.pi * u)
    if art == "trichter":
        return mitte_y + (y - mitte_y) * (1.0 - 0.6 * u)
    if art == "kaskade_auf":
        return y - hoehe * 0.8 * u
    if art == "kaskade_ab":
        return y + hoehe * 0.8 * u
    return y


def _drehen_3d(x: float, y: float, mx: float, my: float, rx: float, ry: float, rz: float, dist: float) -> tuple:
    """Ein Punkt nach der Drehung um Z, X, Y (Bogenmaß) um die Mitte mit Perspektive (``dist``: Augenabstand, 0 = keine)."""
    a, b, c = x - mx, y - my, 0.0
    a, b = a * math.cos(rz) - b * math.sin(rz), a * math.sin(rz) + b * math.cos(rz)
    b, c = b * math.cos(rx) - c * math.sin(rx), b * math.sin(rx) + c * math.cos(rx)
    a, c = a * math.cos(ry) + c * math.sin(ry), -a * math.sin(ry) + c * math.cos(ry)
    f = dist / max(dist - c, dist * 0.2) if dist else 1.0
    return mx + a * f, my + b * f


def _linienzuege(ops: list) -> list:
    """Die Pfadanweisungen als feine Linienzüge (Kurven unterteilt): Liste von Punktlisten."""
    zuege, akt, ax, ay = [], None, 0.0, 0.0
    for op in ops:
        k = op[0]
        if k == "M":
            akt = [(op[1], op[2])]
            zuege.append(akt)
            ax, ay = op[1], op[2]
        elif k == "L" and akt is not None:
            akt.append((op[1], op[2]))
            ax, ay = op[1], op[2]
        elif k == "Q" and akt is not None:
            for t in range(1, 13):
                u = t / 12
                akt.append(((1 - u) ** 2 * ax + 2 * (1 - u) * u * op[1] + u * u * op[3], (1 - u) ** 2 * ay + 2 * (1 - u) * u * op[2] + u * u * op[4]))
            ax, ay = op[3], op[4]
        elif k == "C" and akt is not None:
            for t in range(1, 17):
                u = t / 16
                v = 1 - u
                akt.append((v ** 3 * ax + 3 * v * v * u * op[1] + 3 * v * u * u * op[3] + u ** 3 * op[5], v ** 3 * ay + 3 * v * v * u * op[2] + 3 * v * u * u * op[4] + u ** 3 * op[6]))
            ax, ay = op[5], op[6]
    return zuege


def pfad_verformen(ops: list, fx: dict | None) -> list:
    """Die Glyphenpfade nach ``warp`` (Transformieren) und ``text_3d`` (3D-Drehung um X, Y, Z mit Perspektive); ohne beides unverändert."""
    fx = fx or {}
    art = (fx.get("warp") or {}).get("art", "keine")
    d3 = fx.get("text_3d") or {}
    dreh = tuple(math.radians(float(d3.get(k, 0) or 0)) for k in ("x", "y", "z"))
    if (art == "keine" and not any(dreh)) or not ops:
        return ops
    x0, y0, x1, y1 = _schranken(ops)
    breite, hoehe = max(x1 - x0, 1.0), max(y1 - y0, 1.0)
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    persp = max(0.0, min(120.0, float(d3.get("perspektive", 45) or 0)))
    dist = (max(breite, hoehe) / 2) / math.tan(math.radians(persp) / 2) if persp > 1 else 0.0
    aus = []
    for zug in _linienzuege(ops):
        pts = []
        for x, y in zug:
            y = _warp_y(art, y, (x - x0) / breite, hoehe, my)
            if any(dreh):
                x, y = _drehen_3d(x, y, mx, my, *dreh, dist)
            pts.append((x, y))
        if len(pts) > 1:
            aus.append(("M", *pts[0]))
            aus += [("L", *q) for q in pts[1:]]
            aus.append(("Z",))
    return aus


# ---- Mehrfachkonturen, Verlaufskontur, innerer Schatten ----------------------------------------------------------------------
# Bahnen der Mehrfachlinien: (Abstand von der Mitte, Dicke) in Linienbreiten (negativ = links der Laufrichtung)
_BAHNEN = {"doppelt": ((-1.0, 1.0), (1.0, 1.0)), "dick_duenn": ((-0.9, 1.2), (0.9, 0.6)), "duenn_dick": ((-0.9, 0.6), (0.9, 1.2)),
           "dreifach": ((-1.4, 0.6), (0.0, 0.6), (1.4, 0.6))}


def _zuege_geschlossen(ops: list) -> list:
    """Die Pfadanweisungen als feine Linienzüge: Liste von ``(Punkte, geschlossen)``."""
    aus, akt, ax, ay = [], None, 0.0, 0.0
    for op in ops:
        k = op[0]
        if k == "M":
            akt = [(op[1], op[2])]
            aus.append([akt, False])
            ax, ay = op[1], op[2]
        elif k == "Z" and akt is not None:
            aus[-1][1] = True
        elif k == "L" and akt is not None:
            akt.append((op[1], op[2]))
            ax, ay = op[1], op[2]
        elif k == "Q" and akt is not None:
            for t in range(1, 13):
                u = t / 12
                akt.append(((1 - u) ** 2 * ax + 2 * (1 - u) * u * op[1] + u * u * op[3], (1 - u) ** 2 * ay + 2 * (1 - u) * u * op[2] + u * u * op[4]))
            ax, ay = op[3], op[4]
        elif k == "C" and akt is not None:
            for t in range(1, 17):
                u = t / 16
                v = 1 - u
                akt.append((v ** 3 * ax + 3 * v * v * u * op[1] + 3 * v * u * u * op[3] + u ** 3 * op[5], v ** 3 * ay + 3 * v * v * u * op[2] + 3 * v * u * u * op[4] + u ** 3 * op[6]))
            ax, ay = op[5], op[6]
    return [(a[0], a[1]) for a in aus]


def _normale(a, q, b) -> tuple:
    """Die Einheitsnormale am Eckpunkt ``q`` zwischen Vorgänger ``a`` und Nachfolger ``b`` (fehlende Nachbarn zählen nicht)."""
    nx = ny = 0.0
    for u, v in ((a, q), (q, b)):
        if u is None or v is None:
            continue
        dx, dy = v[0] - u[0], v[1] - u[1]
        n = math.hypot(dx, dy) or 1.0
        nx += -dy / n
        ny += dx / n
    n = math.hypot(nx, ny) or 1.0
    return nx / n, ny / n


def _versetzt(ops: list, abstand: float) -> list:
    """Der Pfad seitlich um ``abstand`` verschoben (Eckpunkte entlang ihrer Normalen)."""
    aus = []
    for pts, zu in _zuege_geschlossen(ops):
        if len(pts) < 2:
            continue
        if zu and len(pts) > 2 and pts[0] == pts[-1]:
            pts = pts[:-1]
        n = len(pts)
        neu = []
        for i, q in enumerate(pts):
            nx, ny = _normale(pts[i - 1] if (i > 0 or zu) else None, q, pts[(i + 1) % n] if (i < n - 1 or zu) else None)
            neu.append((q[0] + nx * abstand, q[1] + ny * abstand))
        aus.append(("M", *neu[0]))
        aus += [("L", *q) for q in neu[1:]]
        if zu:
            aus.append(("Z",))
    return aus


def _bahnen(ops: list, form: str, breite: float) -> list:
    """Die Striche einer Konturlinie: ``[(Pfad, Strichbreite)]`` — einfach ein Strich, sonst die Bahnen der Mehrfachlinie."""
    if form in _BAHNEN:
        return [(_versetzt(ops, o * breite), max(0.1, d * breite)) for o, d in _BAHNEN[form]]
    return [(ops, breite)]


def _ebene(b, schranken: tuple, rand: float, zeichne):
    """Das, was ``zeichne(ziel)`` zeichnet, als Alphaebene auf einer eigenen Fläche um die Schranken → ``(x0, y0, breite, hoehe, alpha, faktor)`` (Maße in Pixeln der Ebene)."""
    from .rasterziel import RasterZiel
    from .textpfad import gemeinsame_engine
    faktor = 2.0
    if hasattr(b, "_massstab"):
        faktor = max(1.0, min(4.0, float(b._massstab())))
    x0, y0 = schranken[0] - rand, schranken[1] - rand
    z = RasterZiel(getattr(b, "engine", None) or gemeinsame_engine(), schranken[2] - schranken[0] + 2 * rand, schranken[3] - schranken[1] + 2 * rand, faktor, (0, 0, 0, 0))
    z.push_state(translate=Point(-x0, -y0))
    zeichne(z)
    z.pop_state()
    w, h, roh = z.als_rgba()
    return x0, y0, w, h, bytearray(roh[3::4]), faktor


def _ebene_zeichnen(b, x0: float, y0: float, w: int, h: int, rgba_puffer, faktor: float) -> None:
    from .bildeffekte import png_bytes
    from lunivo_writer.kern.geometrie import Rect
    b.draw_image(png_bytes(w, h, rgba_puffer), Rect(x0, y0, w / faktor, h / faktor), True)


def _schieben(daten, w: int, h: int, sx: int, sy: int, fuell: int) -> bytearray:
    aus = bytearray([fuell]) * (w * h)
    for y in range(h):
        qy = y - sy
        if not 0 <= qy < h:
            continue
        zeile = daten[qy * w:(qy + 1) * w]
        if sx >= 0:
            neu = bytes([fuell]) * min(w, sx) + bytes(zeile[:max(0, w - sx)])
        else:
            neu = bytes(zeile[-sx:]) + bytes([fuell]) * min(w, -sx)
        aus[y * w:(y + 1) * w] = neu
    return aus


def _innerer_schatten(b, ops: list, s: dict, box: tuple) -> None:
    """Innerer Schatten: der Schatten der Fläche außerhalb des Textes, versetzt und weichgezeichnet, nur innerhalb der Buchstaben."""
    from .bildeffekte import getoent, weichgezeichnet
    abst = float(s.get("abstand", 3)) * PX
    w_ = math.radians(float(s.get("winkel", 45)))
    weich = float(s.get("weich", 4)) * PX * 0.6
    x0, y0, w, h, maske, f = _ebene(b, box, int(abst + weich * 2) + 3, lambda z: z.draw_path(ops, Style(color=(0, 0, 0, 255), width=0, filled=True), True, True))
    aussen = bytearray(255 - a for a in maske)
    aussen = _schieben(aussen, w, h, int(round(math.cos(w_) * abst * f)), int(round(math.sin(w_) * abst * f)), 255)
    if weich * f >= 1:
        aussen = weichgezeichnet(aussen, w, h, weich * f)
    innen = bytearray(a * m // 255 for a, m in zip(aussen, maske))
    c = _farbe(s.get("farbe", "#000000"), transparenz=float(s.get("transparenz", 50)))
    _ebene_zeichnen(b, x0, y0, w, h, getoent(innen, w, h, c[:3], c[3] / 255.0), f)


def _verlauf_kontur(b, bahnen: list, fx: dict, box: tuple, breite: float) -> None:
    """Konturlinie mit Farbverlauf: die Striche (auch Mehrfachlinien) als Maske, gefüllt mit dem Verlauf."""
    v = fx["kontur_verlauf"]
    g = _verlauf(box, v)
    stil = lambda bw: Style(color=(0, 0, 0, 255), width=bw, filled=False, join="round")
    rand = breite * 3 + 3
    x0, y0, w, h, maske, f = _ebene(b, box, rand, lambda z: [z.draw_path(pfad, stil(bw), True, True) for pfad, bw in bahnen])
    (px0, py0), (px1, py1) = (g.start.x, g.start.y), (g.end.x, g.end.y)
    dx, dy = px1 - px0, py1 - py0
    n = (dx * dx + dy * dy) or 1.0
    (c0, c1) = g.stops[0][1], g.stops[-1][1]
    out = bytearray(w * h * 4)
    for y in range(h):
        py = y0 + (y + 0.5) / f
        for x in range(w):
            a = maske[y * w + x]
            if a:
                t = max(0.0, min(1.0, ((x0 + (x + 0.5) / f - px0) * dx + (py - py0) * dy) / n))
                o = (y * w + x) * 4
                out[o], out[o + 1], out[o + 2] = (int(c0[i] + (c1[i] - c0[i]) * t + 0.5) for i in range(3))
                out[o + 3] = int(a * (c0[3] + (c1[3] - c0[3]) * t) / 255 + 0.5)
    _ebene_zeichnen(b, x0, y0, w, h, out, f)


def zeichne_text_mit_effekt(b, engine, text: str, position: Point, font, farbe, fx: dict, kontur=None) -> None:
    """Das Textstück ``text`` mit Grundlinie bei ``position.y`` samt Effekten: erst, was hinter dem Text liegt (Spiegelung, 3D-Tiefe, Schatten, Leuchten), dann der Text, dann
    Füllung und Kontur darüber. ``kontur``: ``(Farbe, Breite in Bildpunkten)`` des Textes selbst, falls er eine Kontur hat."""
    ops = pfad_verformen(engine.glyphen_pfad(text, font, position.x, position.y), fx)
    if not ops:
        return
    gl, px = position.y, font.size_pt * PX
    box = _schranken(ops)
    # ---- hinter dem Text
    r = fx.get("reflektion")
    if r:
        abstand = float(r.get("abstand", 0)) * PX
        spiegel = _abbilden(ops, 1, 0, 0, -1, 0, 2 * gl + abstand)
        hoch = max(1.0, px * float(r.get("groesse", 50)) / 100.0)
        c = _farbe("#%02x%02x%02x" % tuple(farbe[:3]) if farbe else "#000000", transparenz=float(r.get("transparenz", 50)))
        verlauf = LinearGradient(Point(0, gl + abstand), Point(0, gl + abstand + hoch), ((0.0, c), (1.0, (c[0], c[1], c[2], 0))))
        b.draw_path(spiegel, Style(color=c, width=0, filled=True, fill=verlauf), True, True)
    d3 = fx.get("d3")
    if d3 and float(d3.get("tiefe", 0)) > 0:
        tiefe = float(d3["tiefe"]) * PX
        w = math.radians(float(d3.get("winkel", 45)) + 45)
        n = max(2, int(tiefe))
        basis = _farbe(d3.get("tiefe_farbe", "#808080"))
        for k in range(n, 0, -1):
            t = k / n
            f = {"plastik": 1.25 - 0.5 * t, "metall": 1.0 + 0.45 * math.sin(t * math.pi * 2), "dunkel": 0.6 + 0.4 * (1 - t), "weich": 1.15 - 0.25 * t, "hell": 1.3}.get(d3.get("material", "matt"), 1.0)
            c = (max(0, min(255, int(basis[0] * f))), max(0, min(255, int(basis[1] * f))), max(0, min(255, int(basis[2] * f))), 255)
            b.draw_path(_abbilden(ops, 1, 0, 0, 1, math.cos(w) * tiefe * t, math.sin(w) * tiefe * t), Style(color=c, width=0, filled=True), True, True)
        if float(d3.get("kontur", 0)) > 0:
            b.draw_path(_abbilden(ops, 1, 0, 0, 1, math.cos(w) * tiefe, math.sin(w) * tiefe), Style(color=_farbe(d3.get("kontur_farbe", "#404040")), width=float(d3["kontur"]) * PX, join="round"), True, True)
    s = fx.get("schatten")
    if s and s.get("art", "aussen") != "innen":
        abst = float(s.get("abstand", 3)) * PX
        w = math.radians(float(s.get("winkel", 45)))
        sk = float(s.get("groesse", 100)) / 100.0
        mx, my = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
        if s.get("art") == "persp":                                               # flach auf den Boden gelegt und in Richtung des Lichts geneigt
            shx = -math.cos(w) * 0.8
            c_ = shx * (-0.4 * sk)
            t = _abbilden(ops, sk, 0, c_, -0.4 * sk, c_ * (-gl) + math.cos(w) * abst * 0.5, 0.4 * sk * gl + gl + abst * 0.3)
        else:
            t = _abbilden(ops, sk, 0, 0, sk, (1 - sk) * mx + math.cos(w) * abst, (1 - sk) * my + math.sin(w) * abst)
        b.draw_shadow(t, _farbe(s.get("farbe", "#000000"), transparenz=float(s.get("transparenz", 50))), float(s.get("weich", 4)) * PX * 0.6, 0.0, 0.0)
    g = fx.get("leuchten")
    if g and float(g.get("groesse", 0)) > 0:
        b.draw_shadow(ops, _farbe(g.get("farbe", "#4472c4"), transparenz=float(g.get("transparenz", 60))), float(g["groesse"]) * PX, 0.0, 0.0)
    # ---- der Text
    if farbe is not None and farbe[3] > 0:
        b.draw_path(ops, Style(color=farbe, width=0, filled=True), True, True)
    # ---- darüber
    if "verlauf" in fx:
        b.draw_path(ops, Style(color=farbe or (0, 0, 0, 255), width=0, filled=True, fill=_verlauf(box, fx["verlauf"])), True, True)
    if fx.get("fuell_pinsel"):
        pinsel = _pinsel(fx["fuell_pinsel"], farbe)
        if pinsel is not None:
            b.draw_path(ops, Style(color=farbe or (0, 0, 0, 255), width=0, filled=True, fill=pinsel), True, True)
    if s and s.get("art") == "innen":
        _innerer_schatten(b, ops, s, box)
    if kontur is not None or "kontur_verlauf" in fx or fx.get("kontur_form", "einfach") != "einfach":
        c, breite = kontur if kontur is not None else (_farbe(fx.get("kontur_farbe", "#000000")), max(0.1, float(fx.get("kontur_breite", 0.75))) * PX)
        bahnen = _bahnen(ops, fx.get("kontur_form", "einfach"), breite)
        if "kontur_verlauf" in fx:                                               # Verlaufskontur: Maske der Striche, gefüllt mit dem Verlauf
            _verlauf_kontur(b, bahnen, fx, box, breite)
        else:
            for pfad, bw in bahnen:
                b.draw_path(pfad, Style(color=c, width=bw, filled=False, join="round"), True, True)
