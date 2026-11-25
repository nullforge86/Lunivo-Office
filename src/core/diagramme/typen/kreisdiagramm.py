"""Kreisdiagramm: aus ``core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner`` herausgelöst."""
from __future__ import annotations
import math
from core.geometrie import Rect
from core.layout.drucklayout.ausgabe.backend import Style
from core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner_hilfen import _Z, _dunkel, _hell


# ---- Kreis ----------------------------------------------------------------------------------------------------------------------
def _sektor(b, mx, my, rx, ry, w0, w1, farbe, innen: float = 0.0, tiefe: float = 0.0) -> None:
    n = max(2, int(abs(w1 - w0) / math.radians(3)) + 1)
    aussen = [(mx + rx * math.cos(w0 + (w1 - w0) * k / n), my + ry * math.sin(w0 + (w1 - w0) * k / n)) for k in range(n + 1)]
    if innen > 0:
        ein = [(mx + rx * innen * math.cos(w1 - (w1 - w0) * k / n), my + ry * innen * math.sin(w1 - (w1 - w0) * k / n)) for k in range(n + 1)]
        ops = [("M", *aussen[0])] + [("L", *q) for q in aussen[1:]] + [("L", *q) for q in ein] + [("Z",)]
    else:
        ops = [("M", mx, my)] + [("L", *q) for q in aussen] + [("Z",)]
    b.draw_path(ops, Style(color=farbe, width=1, filled=True, outline=(255, 255, 255, 255)), True, True)


def _kreis(z: _Z, f: Rect) -> None:
    v, b = z.v, z.b
    art, kat = v["art"], v["kat"]
    werte = [max(0.0, w) for w in v["reihen"][list(v["reihen"])[0]]]
    werte += [0.0] * (len(kat) - len(werte))
    farben = v["palette"]
    von_kreis = art in ("kreis_von_kreis", "kreis_balken")
    haupt = f
    if von_kreis:
        haupt = Rect(f.x, f.y, f.width * 0.58, f.height)
    plus = (len(kat) > 3) if von_kreis else False
    rest = werte[-min(3, max(2, len(werte) // 3)):] if von_kreis and len(werte) > 2 else []
    hauptwerte = (werte[:len(werte) - len(rest)] + [sum(rest)]) if von_kreis else werte
    summe = sum(hauptwerte) or 1.0
    schief = 0.62 if art == "kreis_3d" else 1.0
    radius = min(haupt.width, haupt.height / schief) / 2 - 6
    mx, my = haupt.x + haupt.width / 2, haupt.y + haupt.height / 2 - (8 if schief < 1 else 0)
    if art == "kreis_3d":
        for t in range(14, 0, -1):                                                      # Tiefe: abgedunkelte Scheiben unter dem Kreis
            w0 = -math.pi / 2
            for i, w in enumerate(hauptwerte):
                if w <= 0:
                    continue
                s = 2 * math.pi * w / summe
                _sektor(b, mx, my + t, radius, radius * schief, w0, w0 + s, _dunkel(farben[i % len(farben)], 0.35))
                w0 += s
    w0 = -math.pi / 2
    mitten = []
    for i, w in enumerate(hauptwerte):
        if w <= 0:
            mitten.append(None)
            continue
        s = 2 * math.pi * w / summe
        farbe = farben[i % len(farben)] if not (von_kreis and i == len(hauptwerte) - 1) else _hell(farben[(len(farben) - 1)], 0.3)
        _sektor(b, mx, my, radius, radius * schief, w0, w0 + s, farbe, 0.5 if art == "ring" else 0.0)
        mitten.append((w0 + s / 2, w / summe))
        w0 += s
    z.teil("zeichnungsbereich", Rect(mx - radius, my - radius * schief, 2 * radius, 2 * radius * schief))
    if v["labels"]:
        for m in mitten:
            if m is not None:
                w, anteil = m
                z.text_(f"{anteil * 100:.0f} %".replace(".", ","), Rect(mx + math.cos(w) * radius * 0.7 - 25, my + math.sin(w) * radius * schief * 0.7 - 7, 50, 14), "center")
    if von_kreis and rest:
        sub = Rect(f.x + f.width * 0.62, f.y, f.width * 0.38, f.height)
        sm = sum(rest) or 1.0
        if art == "kreis_balken":
            h = min(sub.height * 0.7, 160.0)
            y = sub.y + (sub.height - h) / 2
            lauf = 0.0
            for i, w in enumerate(rest):
                hh = h * w / sm
                b.draw_rect(Rect(sub.x + 10, y + lauf, 26, hh), Style(color=farben[(len(werte) - len(rest) + i) % len(farben)], width=1, filled=True, outline=(255, 255, 255, 255)))
                lauf += hh
        else:
            rr = min(sub.width, sub.height) / 2 - 6
            w0 = -math.pi / 2
            for i, w in enumerate(rest):
                s = 2 * math.pi * w / sm
                _sektor(b, sub.x + sub.width / 2, sub.y + sub.height / 2, rr, rr, w0, w0 + s, farben[(len(werte) - len(rest) + i) % len(farben)])
                w0 += s
