"""Bilder lesen ohne Qt: zuerst über Pillow (alle gängigen Formate, schnell, mit Verkleinerung und EXIF-Drehung); ohne Pillow oder bei einem Fehler über die eigenen Decoder
für PNG (alle Farbtypen und Tiefen, ohne Adam7-Zeilensprung) und sequenzielles JPEG (für die Bildschirmgröße auf 1/2, 1/4 oder 1/8 verkleinert dekodiert).
Ergebnis: ``(breite, hoehe, bytearray RGBA)`` oder ``None``, wenn das Format nicht gelesen wird."""
from __future__ import annotations

import math
import struct
import zlib
from operator import mul

_ZICKZACK = (0, 1, 8, 16, 9, 2, 3, 10, 17, 24, 32, 25, 18, 11, 4, 5, 12, 19, 26, 33, 40, 48, 41, 34, 27, 20, 13, 6, 7, 14, 21, 28,
             35, 42, 49, 56, 57, 50, 43, 36, 29, 22, 15, 23, 30, 37, 44, 51, 58, 59, 52, 45, 38, 31, 39, 46, 53, 60, 61, 54, 47, 55, 62, 63)


_MAX_PIXEL = 24_000_000                                                       # größere Bilder werden beim Lesen verkleinert (Speicher)


def _pillow(daten: bytes, ziel_breite: float | None):
    """Alle gängigen Formate (JPEG auch progressiv, GIF, BMP, WebP, TIFF, PNG mit Zeilensprung …) über Pillow, ohne Qt; ``None``, wenn Pillow fehlt oder das Bild unlesbar ist."""
    try:
        import io
        from PIL import Image, ImageOps
    except ImportError:
        return None
    try:
        Image.MAX_IMAGE_PIXELS = 400_000_000                                      # Schutz vor Dekompressionsbomben: darüber löst Pillow einen Fehler aus
        with Image.open(io.BytesIO(daten)) as bild:
            bild.seek(0)
            breite, hoehe = bild.size
            if bild.format == "JPEG" and ziel_breite and breite > ziel_breite * 2:
                bild.draft("RGB", (max(1, int(ziel_breite)), max(1, int(hoehe * ziel_breite / breite))))      # JPEG gleich verkleinert dekodieren
            bild.load()
            bild = ImageOps.exif_transpose(bild)                                   # Drehung nach EXIF
            if bild.width * bild.height > _MAX_PIXEL:
                faktor = int(math.ceil(math.sqrt(bild.width * bild.height / _MAX_PIXEL)))
                bild = bild.reduce(faktor)
            rgba = bild.convert("RGBA")
            return rgba.width, rgba.height, bytearray(rgba.tobytes())
    except Exception:
        return None


def _entpackt(daten: bytes) -> bytes | None:
    """gzip-gepackte Vektorbilder (EMZ, WMZ, SVGZ) entpacken; höchstens 64 MB (Schutz vor gepackten Bomben)."""
    import zlib as _z
    try:
        o = _z.decompressobj(16 + _z.MAX_WBITS)
        roh = o.decompress(daten, 64_000_000)
        return roh if not o.unconsumed_tail else None
    except _z.error:
        return None


def _vektor(daten: bytes, ziel_breite: float | None):
    """EMF, WMF und SVG (auch gepackt) über die Interpreter des Kerns, gerastert; ``None``, wenn es kein solches Bild ist."""
    if daten[:2] == b"\x1f\x8b":
        daten = _entpackt(daten) or b""
    from core.layout.drucklayout.ausgabe.bild import metafile, svg
    if metafile.ist_emf(daten) or metafile.ist_wmf(daten):
        return metafile.metafile_rgba(daten)
    if svg.ist_svg(daten):
        return svg.svg_rgba(daten, int(ziel_breite or 0))
    return None


def bild_dekodieren(daten: bytes, ziel_breite: float | None = None):
    if daten[:8] != b"\x89PNG\r\n\x1a\n" and daten[:2] != b"\xff\xd8":
        try:
            erg = _vektor(daten, ziel_breite)
        except Exception:
            erg = None
        if erg is not None:
            return erg
    erg = _pillow(daten, ziel_breite)
    if erg is not None:
        return erg
    try:
        if daten[:8] == b"\x89PNG\r\n\x1a\n":
            return _png(daten)
        if daten[:2] == b"\xff\xd8":
            return _jpeg(daten, ziel_breite)
    except Exception:
        return None
    return None


# ---------------------------------------------------------------- PNG
def _png(d: bytes):
    i, idat, plte, trns, kopf = 8, [], b"", b"", None
    while i + 8 <= len(d):
        n, art = struct.unpack(">I4s", d[i:i + 8])
        teil = d[i + 8:i + 8 + n]
        if art == b"IHDR":
            kopf = struct.unpack(">IIBBBBB", teil)
        elif art == b"IDAT":
            idat.append(teil)
        elif art == b"PLTE":
            plte = teil
        elif art == b"tRNS":
            trns = teil
        i += 12 + n
    if kopf is None:
        return None
    w, h, tiefe, ct, _k, _f, zeilensprung = kopf
    if zeilensprung or ct not in (0, 2, 3, 4, 6) or tiefe not in (1, 2, 4, 8, 16):
        return None
    kanaele = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    bits = kanaele * tiefe
    zeile_b = (w * bits + 7) // 8
    bpp = max(1, bits // 8)
    roh = zlib.decompress(b"".join(idat))
    aus = bytearray(w * h * 4)
    vorige = bytearray(zeile_b)
    palette = [(plte[k], plte[k + 1], plte[k + 2], trns[k // 3] if k // 3 < len(trns) else 255) for k in range(0, len(plte) - 2, 3)] if ct == 3 else None
    for y in range(h):
        f = roh[y * (zeile_b + 1)]
        z = bytearray(roh[y * (zeile_b + 1) + 1:(y + 1) * (zeile_b + 1)])
        if f == 1:
            for k in range(bpp, zeile_b):
                z[k] = (z[k] + z[k - bpp]) & 255
        elif f == 2:
            z = bytearray((a + b) & 255 for a, b in zip(z, vorige))
        elif f == 3:
            for k in range(zeile_b):
                z[k] = (z[k] + (((z[k - bpp] if k >= bpp else 0) + vorige[k]) >> 1)) & 255
        elif f == 4:
            for k in range(zeile_b):
                a, b, c = (z[k - bpp] if k >= bpp else 0), vorige[k], (vorige[k - bpp] if k >= bpp else 0)
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                z[k] = (z[k] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        vorige = z
        o = y * w * 4
        if tiefe == 16:
            z = z[0::2]                                                       # nur das höhere Byte
            tiefe_z = 8
        else:
            tiefe_z = tiefe
        if ct == 6 and tiefe_z == 8:
            aus[o:o + w * 4] = z
        elif ct == 2 and tiefe_z == 8:
            zeile = bytearray(b"\xff" * (w * 4))
            zeile[0::4], zeile[1::4], zeile[2::4] = z[0::3], z[1::3], z[2::3]
            aus[o:o + w * 4] = zeile
        elif ct == 0 and tiefe_z == 8:
            zeile = bytearray(b"\xff" * (w * 4))
            zeile[0::4], zeile[1::4], zeile[2::4] = z[:w], z[:w], z[:w]
            aus[o:o + w * 4] = zeile
        elif ct == 4 and tiefe_z == 8:
            zeile = bytearray(w * 4)
            zeile[0::4], zeile[1::4], zeile[2::4], zeile[3::4] = z[0::2], z[0::2], z[0::2], z[1::2]
            aus[o:o + w * 4] = zeile
        else:                                                                 # Palette oder Graustufen mit 1, 2, 4 Bit
            werte = _bits_lesen(z, w, tiefe_z)
            for x, v in enumerate(werte):
                if ct == 3:
                    r, g, bl, al = palette[v] if v < len(palette) else (0, 0, 0, 255)
                else:
                    g8 = v * 255 // ((1 << tiefe_z) - 1)
                    r = g = bl = g8
                    al = 255
                aus[o + x * 4:o + x * 4 + 4] = bytes((r, g, bl, al))
            continue
    return w, h, aus


def _bits_lesen(z: bytes, n: int, tiefe: int) -> list[int]:
    aus, maske = [], (1 << tiefe) - 1
    for byte in z:
        for s in range(8 - tiefe, -1, -tiefe):
            aus.append((byte >> s) & maske)
    return aus[:n]


# ---------------------------------------------------------------- JPEG
def _basis(n: int) -> list[list[float]]:
    """Orthonormale DCT-Basis der Größe n: ``c[x][u]``."""
    return [[(math.sqrt(1.0 / n) if u == 0 else math.sqrt(2.0 / n)) * math.cos((2 * x + 1) * u * math.pi / (2 * n)) for u in range(n)] for x in range(n)]


class _Huffman:
    def __init__(self, zaehler: list[int], symbole: list[int]):
        self.schnell: dict[int, tuple[int, int]] = {}
        self.min, self.max, self.ptr, self.sym = [0] * 18, [-1] * 18, [0] * 18, symbole
        code, k = 0, 0
        for laenge in range(1, 17):
            self.ptr[laenge] = k
            self.min[laenge] = code
            for _ in range(zaehler[laenge - 1]):
                if laenge <= 8:
                    spanne = 1 << (8 - laenge)
                    for fuell in range(spanne):
                        self.schnell[(code << (8 - laenge)) | fuell] = (laenge, symbole[k])
                code += 1
                k += 1
            self.max[laenge] = code - 1 if zaehler[laenge - 1] else -1
            code <<= 1


class _Bits:
    def __init__(self, daten: bytes):
        self.d, self.p = daten + b"\x00\x00\x00\x00", 0

    def lesen(self, n: int) -> int:
        if n == 0:
            return 0
        p, d = self.p, self.d
        i = p >> 3
        wert = (d[i] << 24) | (d[i + 1] << 16) | (d[i + 2] << 8) | d[i + 3]
        self.p = p + n
        return (wert >> (32 - (p & 7) - n)) & ((1 << n) - 1)

    def symbol(self, h: _Huffman) -> int:
        p, d = self.p, self.d
        i = p >> 3
        fenster = (((d[i] << 16) | (d[i + 1] << 8) | d[i + 2]) >> (16 - (p & 7))) & 255
        treffer = h.schnell.get(fenster)
        if treffer is not None:
            self.p = p + treffer[0]
            return treffer[1]
        code = 0
        for laenge in range(1, 17):
            code = (code << 1) | self.lesen(1)
            if h.max[laenge] >= 0 and h.min[laenge] <= code <= h.max[laenge]:
                return h.sym[h.ptr[laenge] + code - h.min[laenge]]
        return 0


def _erweitern(v: int, n: int) -> int:
    return v if n == 0 or v >= (1 << (n - 1)) else v - (1 << n) + 1


def _jpeg(d: bytes, ziel_breite):
    i, quant, dc, ac, komp, rst, adobe, rahmen = 2, {}, {}, {}, [], 0, None, None
    while i + 4 <= len(d):
        if d[i] != 0xFF:
            i += 1
            continue
        m = d[i + 1]
        if m == 0xD8 or 0xD0 <= m <= 0xD7 or m == 0x01 or m == 0xFF:
            i += 1 if m == 0xFF else 2
            continue
        n = struct.unpack(">H", d[i + 2:i + 4])[0]
        seg = d[i + 4:i + 2 + n]
        if m == 0xDB:
            k = 0
            while k < len(seg):
                pq, tq = seg[k] >> 4, seg[k] & 15
                k += 1
                if pq:
                    tab = [struct.unpack(">H", seg[k + 2 * j:k + 2 * j + 2])[0] for j in range(64)]
                    k += 128
                else:
                    tab = list(seg[k:k + 64])
                    k += 64
                quant[tq] = tab
        elif m == 0xC4:
            k = 0
            while k < len(seg):
                tc, th = seg[k] >> 4, seg[k] & 15
                zaehler = list(seg[k + 1:k + 17])
                gesamt = sum(zaehler)
                (ac if tc else dc)[th] = _Huffman(zaehler, list(seg[k + 17:k + 17 + gesamt]))
                k += 17 + gesamt
        elif m in (0xC0, 0xC1):
            p, hoch, breit, nk = struct.unpack(">BHHB", seg[:6])
            if p != 8:
                return None
            komp = [(seg[6 + 3 * j], seg[7 + 3 * j] >> 4, seg[7 + 3 * j] & 15, seg[8 + 3 * j]) for j in range(nk)]
            rahmen = (breit, hoch)
        elif m in (0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
            return None                                                       # progressiv, verlustfrei, arithmetisch: hier nicht gelesen
        elif m == 0xDD:
            rst = struct.unpack(">H", seg[:2])[0]
        elif m == 0xEE and seg[:5] == b"Adobe":
            adobe = seg[11] if len(seg) > 11 else 0
        elif m == 0xDA:
            sos = seg
            i += 2 + n
            break
        i += 2 + n
    else:
        return None
    if rahmen is None:
        return None
    breit, hoch = rahmen
    nk = len(komp)
    if sos[0] != nk:
        return None                                                           # mehrere Durchgänge (nicht verschachtelt)
    tabellen = {sos[1 + 2 * j]: (sos[2 + 2 * j] >> 4, sos[2 + 2 * j] & 15) for j in range(nk)}
    hmax, vmax = max(k[1] for k in komp), max(k[2] for k in komp)
    skala = 8
    if ziel_breite:
        for kandidat in (1, 2, 4, 8):
            if breit * kandidat / 8 >= ziel_breite:
                skala = kandidat
                break
    mcux, mcuy = -(-breit // (8 * hmax)), -(-hoch // (8 * vmax))
    # Eintropiedaten in Teile bei Neustartmarken zerlegen
    teile, start, pos = [], i, i
    while True:
        pos = d.find(b"\xff", pos)
        if pos < 0 or pos + 1 >= len(d):
            teile.append(d[start:])
            break
        nxt = d[pos + 1]
        if nxt == 0x00:
            pos += 2
        elif 0xD0 <= nxt <= 0xD7:
            teile.append(d[start:pos])
            start = pos = pos + 2
        elif nxt == 0xFF:
            pos += 1
        else:
            teile.append(d[start:pos])
            break
    teile = [t.replace(b"\xff\x00", b"\xff") for t in teile]
    basis = _basis(skala) if skala > 1 else None
    ebenen = []
    for (cid, h, v, tq) in komp:
        ebenen.append((bytearray(mcux * h * skala * mcuy * v * skala), mcux * h * skala))
    gesamt_mcu, mcu_nr, teil_nr = mcux * mcuy, 0, 0
    while mcu_nr < gesamt_mcu and teil_nr < len(teile):
        bits, vorher = _Bits(teile[teil_nr]), [0] * nk
        teil_nr += 1
        for _ in range(rst or gesamt_mcu):
            if mcu_nr >= gesamt_mcu:
                break
            mx, my = mcu_nr % mcux, mcu_nr // mcux
            for ci, (cid, h, v, tq) in enumerate(komp):
                td, ta = tabellen[cid]
                q, hd, ha = quant[tq], dc[td], ac[ta]
                plane, breite_p = ebenen[ci]
                for by in range(v):
                    for bx in range(h):
                        t = bits.symbol(hd)
                        vorher[ci] += _erweitern(bits.lesen(t), t)
                        blk = [0] * 64
                        blk[0] = vorher[ci] * q[0]
                        hat_ac = False
                        k = 1
                        while k < 64:
                            rs = bits.symbol(ha)
                            r, s = rs >> 4, rs & 15
                            if s == 0:
                                if r == 15:
                                    k += 16
                                    continue
                                break
                            k += r
                            if k > 63:
                                break
                            blk[_ZICKZACK[k]] = _erweitern(bits.lesen(s), s) * q[k]
                            hat_ac = True
                            k += 1
                        x0, y0 = (mx * h + bx) * skala, (my * v + by) * skala
                        if skala == 1:
                            plane[y0 * breite_p + x0] = max(0, min(255, int(blk[0] / 8 + 128.5)))
                        elif not hat_ac:                                                  # nur Gleichanteil: der Block ist eine Fläche
                            wert = max(0, min(255, int(blk[0] / 8 + 128.5)))
                            fl = bytes((wert,)) * skala
                            for y in range(skala):
                                o = (y0 + y) * breite_p + x0
                                plane[o:o + skala] = fl
                        else:
                            n = skala
                            f = [blk[u * 8:u * 8 + n] for u in range(n)]
                            t = [[sum(map(mul, f[vv], basis[x])) for x in range(n)] for vv in range(n)]
                            spalten = list(zip(*t))
                            fak = n / 8.0
                            for y in range(n):
                                by, o = basis[y], (y0 + y) * breite_p + x0
                                for x in range(n):
                                    val = fak * sum(map(mul, by, spalten[x])) + 128.5
                                    plane[o + x] = 0 if val < 0 else 255 if val > 255 else int(val)
            mcu_nr += 1
    w2, h2 = -(-breit * skala // 8), -(-hoch * skala // 8)
    aus = bytearray(w2 * h2 * 4)
    xmap = [[min(x * k[1] // hmax, (ebenen[ci][1] - 1)) for x in range(w2)] for ci, k in enumerate(komp)]
    klemme = bytes([0] * 256 + list(range(256)) + [255] * 256)
    crr = [int(1.402 * (c - 128)) + 256 for c in range(256)]
    cbb = [int(1.772 * (c - 128)) + 256 for c in range(256)]
    cbg = [-0.344136 * (c - 128) for c in range(256)]
    crg = [-0.714136 * (c - 128) for c in range(256)]
    ycc = nk == 3 and adobe != 0
    for y in range(h2):
        zeilen = []
        for ci, k in enumerate(komp):
            plane, bp = ebenen[ci]
            yy = min(y * k[2] // vmax, len(plane) // bp - 1)
            zeilen.append(plane[yy * bp:(yy + 1) * bp])
        o = y * w2 * 4
        if nk == 1:
            g = zeilen[0][:w2]
            aus[o:o + w2 * 4:4] = g
            aus[o + 1:o + w2 * 4:4] = g
            aus[o + 2:o + w2 * 4:4] = g
            aus[o + 3:o + w2 * 4:4] = b"\xff" * w2
            continue
        a0, a1, a2 = zeilen[0], zeilen[1], zeilen[2]
        a3 = zeilen[3] if nk == 4 else None
        m0, m1, m2 = xmap[0], xmap[1], xmap[2]
        for x in range(w2):
            c0, c1, c2 = a0[m0[x]], a1[m1[x]], a2[m2[x]]
            if ycc:
                r, g, b = klemme[c0 + crr[c2]], klemme[int(c0 + cbg[c1] + crg[c2]) + 256], klemme[c0 + cbb[c1]]
            else:
                r, g, b = c0, c1, c2
            if a3 is not None:                                                # CMYK (Adobe, invertiert)
                kk = a3[xmap[0][x]]
                r, g, b = r * kk // 255, g * kk // 255, b * kk // 255
            p = o + x * 4
            aus[p], aus[p + 1], aus[p + 2], aus[p + 3] = r, g, b, 255
    return w2, h2, aus
