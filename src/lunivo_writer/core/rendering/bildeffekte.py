"""Bildeffekte ohne Qt: Schatten, Leuchten, Spiegelung (Reflektion) und weiche Kanten als reine Pufferoperationen auf RGBA-Bytes (``bytearray``, Zeile für Zeile).

Alle Maße in Ausgabepixeln der Zeichenfläche, die den Effekt braucht. Die Ergebnisse sind fertige RGBA-Puffer, die Rasterer und PDF-Ziel wie jedes andere Bild zeichnen."""
from __future__ import annotations

import math

PX_PT = 96.0 / 72.0


def skaliert(bw: int, bh: int, daten, w: int, h: int) -> bytearray:
    """Das RGBA-Bild auf ``w`` × ``h`` (bilinear; beim Verkleinern über Mittel vorab gemittelter Taps); ``daten`` wird nicht verändert."""
    if (bw, bh) == (w, h):
        return bytearray(daten)
    aus = bytearray(w * h * 4)
    sx, sy = bw / w, bh / h
    taps = 1 if max(sx, sy) < 1.6 else 2
    for y in range(h):
        for x in range(w):
            r = g = b = al = 0.0
            for ty in range(taps):
                fy = (y + (ty + 0.5) / taps) * sy - 0.5
                iy = min(bh - 1, max(0, int(math.floor(fy))))
                wy = fy - math.floor(fy)
                iy2 = min(bh - 1, iy + 1)
                for tx in range(taps):
                    fx = (x + (tx + 0.5) / taps) * sx - 0.5
                    ix = min(bw - 1, max(0, int(math.floor(fx))))
                    wx = fx - math.floor(fx)
                    ix2 = min(bw - 1, ix + 1)
                    for (qx, qy, wt) in ((ix, iy, (1 - wx) * (1 - wy)), (ix2, iy, wx * (1 - wy)), (ix, iy2, (1 - wx) * wy), (ix2, iy2, wx * wy)):
                        o = (qy * bw + qx) * 4
                        pa = daten[o + 3] * wt
                        r += daten[o] * pa
                        g += daten[o + 1] * pa
                        b += daten[o + 2] * pa
                        al += pa
            n = taps * taps
            o = (y * w + x) * 4
            if al > 0:
                aus[o], aus[o + 1], aus[o + 2], aus[o + 3] = int(r / al + 0.5), int(g / al + 0.5), int(b / al + 0.5), min(255, int(al / n + 0.5))
    return aus


def ellipse_alpha(w: int, h: int) -> bytearray:
    """Ellipse im Rechteck ``w`` × ``h`` als geglättete Alphaebene (0…255)."""
    aus = bytearray(w * h)
    rx, ry = w / 2.0, h / 2.0
    kleiner = min(rx, ry) or 1.0
    for y in range(h):
        dy = ((y + 0.5 - ry) / ry) ** 2
        for x in range(w):
            d = math.sqrt(((x + 0.5 - rx) / rx) ** 2 + dy)
            c = (1.0 - d) * kleiner + 0.5
            aus[y * w + x] = 255 if c >= 1.0 else (0 if c <= 0.0 else int(c * 255))
    return aus


def form_alpha(daten, w: int, h: int, ellipse: bool) -> bytearray:
    """Die Form des Bildes (seine Alphaebene), bei ``ellipse`` zusätzlich in der Ellipse beschnitten."""
    a = bytearray(daten[3::4])
    if ellipse:
        m = ellipse_alpha(w, h)
        a = bytearray(x * y // 255 for x, y in zip(a, m))
    return a


def weichgezeichnet(ebene, w: int, h: int, radius: float) -> bytearray:
    """Die Alphaebene weichgezeichnet (dreimal Kastenfilter ≈ Gauß); große Radien rechnen verkleinert und vergrößern bilinear zurück."""
    r = int(round(radius))
    if r < 1:
        return bytearray(ebene)
    f = 1
    if r >= 6:
        f = max(1, r // 3)
    if f > 1:
        kw, kh = max(1, -(-w // f)), max(1, -(-h // f))
        klein = [[0.0] * kw for _ in range(kh)]
        for y in range(h):
            zeile = klein[y // f]
            for x in range(w):
                zeile[x // f] += ebene[y * w + x]
        norm = 1.0 / (f * f)
        gitter = [[v * norm for v in z] for z in klein]
        r2 = max(1, r // f)
    else:
        kw, kh = w, h
        gitter = [[float(v) for v in ebene[y * w:(y + 1) * w]] for y in range(h)]
        r2 = r
    for _ in range(3):
        n = 2 * r2 + 1
        for y in range(kh):
            z, neu, summe = gitter[y], [0.0] * kw, 0.0
            for x in range(min(r2, kw)):
                summe += z[x]
            for x in range(kw):
                if x + r2 < kw:
                    summe += z[x + r2]
                if x - r2 - 1 >= 0:
                    summe -= z[x - r2 - 1]
                neu[x] = summe / n
            gitter[y] = neu
        for x in range(kw):
            spalte = [gitter[y][x] for y in range(kh)]
            summe = 0.0
            for y in range(min(r2, kh)):
                summe += spalte[y]
            for y in range(kh):
                if y + r2 < kh:
                    summe += spalte[y + r2]
                if y - r2 - 1 >= 0:
                    summe -= spalte[y - r2 - 1]
                gitter[y][x] = summe / n
    aus = bytearray(w * h)
    for y in range(h):
        if f > 1:
            fy = (y + 0.5) / f - 0.5
            y0 = min(kh - 1, max(0, int(math.floor(fy))))
            y1 = min(kh - 1, y0 + 1)
            wy = min(1.0, max(0.0, fy - y0))
        for x in range(w):
            if f > 1:
                fx = (x + 0.5) / f - 0.5
                x0 = min(kw - 1, max(0, int(math.floor(fx))))
                x1 = min(kw - 1, x0 + 1)
                wx = min(1.0, max(0.0, fx - x0))
                v = (gitter[y0][x0] * (1 - wx) + gitter[y0][x1] * wx) * (1 - wy) + (gitter[y1][x0] * (1 - wx) + gitter[y1][x1] * wx) * wy
            else:
                v = gitter[y][x]
            aus[y * w + x] = 255 if v >= 255 else (0 if v <= 0 else int(v + 0.5))
    return aus


def weiche_kanten(daten, w: int, h: int, ellipse: bool, radius: float) -> bytearray:
    """Das Bild mit zum Rand hin auslaufendem Alpha: die Form, um ``radius`` verkleinert und weichgezeichnet, als Maske."""
    out = bytearray(daten)
    form = form_alpha(daten, w, h, ellipse)
    rad = max(1.0, radius)
    # um ``rad`` schrumpfen: Minimum über die Nachbarschaft (getrennt waagerecht und senkrecht, Würfelabstand genügt für den Verlauf)
    k = int(rad)
    schmal = bytearray(form)
    tmp = bytearray(w * h)
    for y in range(h):
        z = schmal[y * w:(y + 1) * w]
        for x in range(w):
            lo, hi = max(0, x - k), min(w, x + k + 1)
            tmp[y * w + x] = min(z[lo:hi])
    for x in range(w):
        spalte = bytes(tmp[y * w + x] for y in range(h))
        for y in range(h):
            lo, hi = max(0, y - k), min(h, y + k + 1)
            schmal[y * w + x] = min(spalte[lo:hi])
    weich = weichgezeichnet(schmal, w, h, rad)
    for i in range(w * h):
        out[i * 4 + 3] = out[i * 4 + 3] * weich[i] // 255
    return out


def png_bytes(w: int, h: int, rgba) -> bytes:
    """Ein RGBA-Puffer als PNG-Datei (für Bilder, die weiter durch ``draw_image`` laufen)."""
    import struct
    import zlib

    def chunk(art: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + art + d + struct.pack(">I", zlib.crc32(art + d) & 0xFFFFFFFF)
    roh = b"".join(b"\x00" + bytes(rgba[y * w * 4:(y + 1) * w * 4]) for y in range(h))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(roh)) + chunk(b"IEND", b"")


def getoent(ebene, w: int, h: int, farbe: tuple, deckkraft: float) -> bytearray:
    """Die Alphaebene als RGBA-Puffer in ``farbe`` (r, g, b) mit der Deckkraft ``deckkraft`` (0…1)."""
    out = bytearray(w * h * 4)
    out[0::4] = bytes([farbe[0]]) * (w * h)
    out[1::4] = bytes([farbe[1]]) * (w * h)
    out[2::4] = bytes([farbe[2]]) * (w * h)
    out[3::4] = bytes(min(255, int(a * deckkraft + 0.5)) for a in ebene)
    return out


def schatten_bild(daten, w: int, h: int, ellipse: bool, farbe: tuple, deckkraft: float, weich_px: float, faktor: float):
    """Schatten oder Leuchten: die getönte Form, um ``faktor`` skaliert und weichgezeichnet → ``(W, H, RGBA, Rand)``; das Bild ist um ``Rand`` Pixel größer als ``w`` × ``h``."""
    pad = int(weich_px * 2 + max(w, h) * max(0.0, faktor - 1.0) / 2) + 4
    form = form_alpha(daten, w, h, ellipse)
    W, H = w + 2 * pad, h + 2 * pad
    gross = bytearray(W * H)
    sw, sh = max(1, int(round(w * faktor))), max(1, int(round(h * faktor)))
    x0, y0 = pad + (w - sw) // 2, pad + (h - sh) // 2
    for y in range(sh):
        qy = min(h - 1, int(y * h / sh))
        for x in range(sw):
            qx = min(w - 1, int(x * w / sw))
            gx, gy = x0 + x, y0 + y
            if 0 <= gx < W and 0 <= gy < H:
                gross[gy * W + gx] = form[qy * w + qx]
    return W, H, getoent(weichgezeichnet(gross, W, H, weich_px), W, H, farbe, deckkraft), pad


def reflektion_bild(daten, w: int, h: int, ellipse: bool, hoehe: int, alpha0: float):
    """Spiegelung: das Bild senkrecht gespiegelt, nur der obere Streifen der Höhe ``hoehe``, nach unten ausblendend → ``(w, hoehe, RGBA)``."""
    form = form_alpha(daten, w, h, ellipse)
    out = bytearray(w * hoehe * 4)
    for y in range(hoehe):
        q = h - 1 - y
        fade = alpha0 * (1.0 - y / max(1, hoehe))
        for x in range(w):
            o, s = (y * w + x) * 4, (q * w + x) * 4
            out[o], out[o + 1], out[o + 2] = daten[s], daten[s + 1], daten[s + 2]
            out[o + 3] = int(daten[s + 3] * form[q * w + x] / 255 * fade + 0.5) if ellipse else int(daten[s + 3] * fade + 0.5)
    return w, hoehe, out
