"""Windows-Metafiles (EMF und WMF) ohne Qt: die Datensätze für Linien, Rechtecke, Ellipsen, Pfade, Schrift und Bitmaps werden auf eine ``RenderTarget`` des Kerns gezeichnet.

Der Interpreter rechnet die Koordinaten selbst durch die Matrix des Metafiles (Weltumwandlung, Fenster → Ansicht, Zielrechteck) und zeichnet Pfade, Text und Bilder.
Unbekannte Datensätze werden übersprungen; ein Datensatz, der sich nicht lesen lässt, bricht das Bild nicht ab."""
from __future__ import annotations

import math
import struct

from lunivo_writer.kern.geometrie import Point, Rect
from lunivo_writer.kern.textsatz.engine import FontSpec
from .backend import Style

_EMF_SIGNATUR = b" EMF"
_KOPF_BYTES = 88
_PLACEABLE = b"\xd7\xcd\xc6\x9a"
_KAPPA = 0.5522847498
MAX_SEITE_PX = 3000
_EINS = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def ist_emf(blob: bytes) -> bool:
    return len(blob) >= 44 and blob[40:44] == _EMF_SIGNATUR


def ist_wmf(blob: bytes) -> bool:
    if blob[:4] == _PLACEABLE:
        return True
    return len(blob) >= 18 and struct.unpack_from("<HH", blob, 0) in ((1, 9), (2, 9))


def _mal(m, a):
    """Matrix ``m`` nach ``a`` angewendet (zuerst ``a``, dann ``m``)."""
    return (m[0] * a[0] + m[2] * a[1], m[1] * a[0] + m[3] * a[1], m[0] * a[2] + m[2] * a[3], m[1] * a[2] + m[3] * a[3],
            m[0] * a[4] + m[2] * a[5] + m[4], m[1] * a[4] + m[3] * a[5] + m[5])


def _pt(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def _basis(ziel: Rect, grenzen: Rect, spiegel=(False, False)):
    """Zielrechteck ← logische Grenzen (und gegebenenfalls Spiegelung der Achsen)."""
    m = (1.0, 0.0, 0.0, 1.0, ziel.x, ziel.y)
    m = _mal(m, (ziel.width / grenzen.width, 0.0, 0.0, ziel.height / grenzen.height, 0.0, 0.0))
    m = _mal(m, (1.0, 0.0, 0.0, 1.0, -grenzen.x, -grenzen.y))
    if spiegel[0] or spiegel[1]:
        m = _mal(m, (1.0, 0.0, 0.0, 1.0, grenzen.x * 2 + grenzen.width if spiegel[0] else 0.0, grenzen.y * 2 + grenzen.height if spiegel[1] else 0.0))
        m = _mal(m, (-1.0 if spiegel[0] else 1.0, 0.0, 0.0, -1.0 if spiegel[1] else 1.0, 0.0, 0.0))
    return m


def _farbe(c: int) -> tuple:
    return (c & 0xFF, (c >> 8) & 0xFF, (c >> 16) & 0xFF, 255)


class _Stift:
    def __init__(self, farbe=(0, 0, 0, 255), breite: float = 1.0, aus: bool = False):
        self.farbe, self.breite, self.aus = farbe, breite, aus


class _Pinsel:
    def __init__(self, farbe=(255, 255, 255, 255), aus: bool = False):
        self.farbe, self.aus = farbe, aus


class _Schrift:
    def __init__(self, name="Liberation Sans", px=12.0, fett=False, kursiv=False):
        self.name, self.px, self.fett, self.kursiv = name, px, fett, kursiv


class _Zeichner:
    """Der Zustand des Zeichnens (Stift, Pinsel, Schrift, Matrix) und die Zeichenvorgänge auf der Fläche ``b``."""

    def __init__(self, b, engine, basis):
        self.b, self.engine, self.basis = b, engine, basis
        self.stift, self.pinsel, self.schrift = _Stift(), _Pinsel(), _Schrift()
        self.textfarbe = (0, 0, 0, 255)
        self.welt, self.seite = _EINS, _EINS
        self.klemmen = 0                                           # so oft hat dieser Zeichner ``push_state`` für Ausschnitte benutzt
        self.stapel: list = []

    # ---- Matrix und Ausgabe ----
    def m(self):
        return _mal(self.basis, _mal(self.seite, self.welt))

    def _ops(self, ops: list) -> list:
        m = self.m()
        aus = []
        for op in ops:
            if op[0] == "Z":
                aus.append(op)
            else:
                pts = []
                for i in range(1, len(op), 2):
                    pts += list(_pt(m, op[i], op[i + 1]))
                aus.append((op[0],) + tuple(pts))
        return aus

    def _stil(self, gefuellt: bool, gestrichelt: bool = True) -> Style | None:
        m = self.m()
        massstab = math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1.0
        strich = (not self.stift.aus) and gestrichelt
        fuell = gefuellt and not self.pinsel.aus
        if not strich and not fuell:
            return None
        return Style(color=self.pinsel.farbe if fuell else self.stift.farbe, width=max(0.0, self.stift.breite * massstab) if strich else 0.0, filled=fuell,
                     outline=self.stift.farbe if (strich and fuell) else None, join="miter")

    def zeichne(self, ops: list, gefuellt: bool = True, gestrichelt: bool = True, oben: bool = False) -> None:
        stil = self._stil(gefuellt, gestrichelt)
        if stil is not None and ops:
            self.b.draw_path(self._ops(ops), stil, True, False)

    def ausschnitt(self, x0: float, y0: float, x1: float, y1: float) -> None:
        """Rechteckiger Ausschnitt in logischen Koordinaten (im Rechteck der abgebildeten Eckpunkte)."""
        m = self.m()
        pts = [_pt(m, x0, y0), _pt(m, x1, y0), _pt(m, x1, y1), _pt(m, x0, y1)]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        self.b.push_state(clip=Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)))
        self.klemmen += 1

    def sichern(self, extra=()) -> None:
        self.stapel.append((self.stift, self.pinsel, self.schrift, self.textfarbe, self.klemmen, self.welt, self.seite) + tuple(extra))

    def wiederherstellen(self):
        if not self.stapel:
            return None
        s = self.stapel.pop()
        self.stift, self.pinsel, self.schrift, self.textfarbe, klemmen, self.welt, self.seite = s[:7]
        while self.klemmen > klemmen:
            self.b.pop_state()
            self.klemmen -= 1
        return s[7:]

    def abschliessen(self) -> None:
        while self.klemmen > 0:
            self.b.pop_state()
            self.klemmen -= 1

    def text(self, t: str, x: float, y: float, grundlinie_versatz: float = 0.0) -> None:
        if not t:
            return
        m = self.m()
        massstab = math.sqrt(abs(m[0] * m[3] - m[1] * m[2])) or 1.0
        px = max(1.0, self.schrift.px * massstab)
        font = FontSpec(self.schrift.name or "Liberation Sans", px * 72.0 / 96.0, 700 if self.schrift.fett else 400, self.schrift.kursiv)
        if grundlinie_versatz:
            y = y + self.engine.font_metrics(FontSpec(font.family, self.schrift.px * 72.0 / 96.0, font.weight, font.italic)).ascent
        ax, ay = _pt(m, x, y)
        self.b.draw_text(t, Point(ax, ay), font, Style(color=self.textfarbe))

    def bild(self, datei: bytes, x: float, y: float, breite: float, hoehe: float) -> None:
        from .bildeffekte import png_bytes
        from .bilddecoder import bild_dekodieren
        erg = bild_dekodieren(datei)
        if erg is None:
            return
        m = self.m()
        a, c = _pt(m, x, y), _pt(m, x + breite, y + hoehe)
        self.b.draw_image(png_bytes(erg[0], erg[1], erg[2]), Rect(min(a[0], c[0]), min(a[1], c[1]), abs(c[0] - a[0]), abs(c[1] - a[1])), smooth=True)


# ---- Pfade ----------------------------------------------------------------------------------------------------------------
def _rechteck_ops(x, y, w, h):
    return [("M", x, y), ("L", x + w, y), ("L", x + w, y + h), ("L", x, y + h), ("Z",)]


def _ellipse_ops(x, y, w, h):
    cx, cy, rx, ry = x + w / 2, y + h / 2, w / 2, h / 2
    kx, ky = rx * _KAPPA, ry * _KAPPA
    return [("M", cx + rx, cy), ("C", cx + rx, cy + ky, cx + kx, cy + ry, cx, cy + ry), ("C", cx - kx, cy + ry, cx - rx, cy + ky, cx - rx, cy),
            ("C", cx - rx, cy - ky, cx - kx, cy - ry, cx, cy - ry), ("C", cx + kx, cy - ry, cx + rx, cy - ky, cx + rx, cy), ("Z",)]


def _rund_ops(x, y, w, h, rx, ry):
    rx, ry = min(rx, w / 2), min(ry, h / 2)
    kx, ky = rx * _KAPPA, ry * _KAPPA
    r, b = x + w, y + h
    return [("M", x + rx, y), ("L", r - rx, y), ("C", r - rx + kx, y, r, y + ry - ky, r, y + ry), ("L", r, b - ry), ("C", r, b - ry + ky, r - rx + kx, b, r - rx, b),
            ("L", x + rx, b), ("C", x + rx - kx, b, x, b - ry + ky, x, b - ry), ("L", x, y + ry), ("C", x, y + ry - ky, x + rx - kx, y, x + rx, y), ("Z",)]


def _poly_ops(punkte, geschlossen):
    if not punkte:
        return []
    return [("M", *punkte[0])] + [("L", *q) for q in punkte[1:]] + ([("Z",)] if geschlossen else [])


def _norm(l, t, r, u):
    return min(l, r), min(t, u), abs(r - l), abs(u - t)


# ---- EMF ------------------------------------------------------------------------------------------------------------------
def _rechteck(b: bytes, off: int) -> Rect:
    l, t, r, u = struct.unpack_from("<iiii", b, off)
    return Rect(l, t, r - l, u - t)


def _emf_kopf(blob: bytes):
    if not ist_emf(blob) or len(blob) < _KOPF_BYTES:
        return None
    grenzen, rahmen = _rechteck(blob, 8), _rechteck(blob, 24)
    return (grenzen, rahmen) if grenzen.width > 0 and grenzen.height > 0 else None


def masse_px(blob: bytes):
    """Die Größe, die das Metafile auf dem Blatt haben soll (96 dpi), aus Rahmen (EMF) bzw. Platzhalterkopf (WMF); sonst ``None``."""
    kopf = _emf_kopf(blob)
    if kopf is not None and kopf[1].width > 0 and kopf[1].height > 0:
        return kopf[1].width / 2540 * 96, kopf[1].height / 2540 * 96
    if blob[:4] == _PLACEABLE and len(blob) >= 22:
        links, oben, rechts, unten = struct.unpack_from("<hhhh", blob, 6)
        einheiten = struct.unpack_from("<H", blob, 14)[0] or 1440
        if rechts > links and unten > oben:
            return (rechts - links) / einheiten * 96, (unten - oben) / einheiten * 96
    return None


def begrenzt(breite: float, hoehe: float) -> tuple[int, int]:
    f = min(1.0, MAX_SEITE_PX / max(breite, hoehe, 1.0))
    return max(1, round(breite * f)), max(1, round(hoehe * f))


def emf_zeichnen(blob: bytes, b, ziel: Rect, engine=None) -> bool:
    """Das EMF als Vektorzeichnung in ``ziel`` auf ``b`` zeichnen (nichts außerhalb). ``False``, wenn es kein lesbares EMF ist."""
    kopf = _emf_kopf(blob)
    if kopf is None:
        return False
    if engine is None:
        from .textpfad import gemeinsame_engine
        engine = gemeinsame_engine()
    b.push_state(clip=ziel)
    z = _Zeichner(b, engine, _basis(ziel, kopf[0]))
    try:
        _emf(blob, z)
    except (struct.error, IndexError, ValueError, OverflowError):
        pass
    finally:
        z.abschliessen()
        b.pop_state()
    return True


def _emf(b: bytes, z: _Zeichner) -> None:
    off = 0
    pfad: list | None = None
    pos = (0.0, 0.0)
    modus, fenster, ansicht = 1, [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 1.0, 1.0]
    objekte: dict = {}

    def abbilden() -> None:
        z.seite = _EINS
        if modus in (7, 8) and fenster[2] and fenster[3] and ansicht[2] and ansicht[3]:
            m = (1.0, 0.0, 0.0, 1.0, ansicht[0], ansicht[1])
            m = _mal(m, (ansicht[2] / fenster[2], 0.0, 0.0, ansicht[3] / fenster[3], 0.0, 0.0))
            m = _mal(m, (1.0, 0.0, 0.0, 1.0, -fenster[0], -fenster[1]))
            z.seite = m

    def aufnehmen(ops: list, gefuellt: bool = True, gestrichelt: bool = True) -> None:
        """In den offenen Pfad aufnehmen (noch nicht gezeichnet) oder gleich zeichnen."""
        if pfad is not None:
            pfad.extend(ops)
        else:
            z.zeichne(ops, gefuellt, gestrichelt)
    while off + 8 <= len(b):
        typ, groesse = struct.unpack_from("<II", b, off)
        if groesse < 8 or off + groesse > len(b):
            break
        try:
            d = off
            if typ == 14:                                         # EOF
                break
            elif typ in (27, 54):                                 # MOVETOEX, LINETO
                x, y = struct.unpack_from("<ii", b, d + 8)
                if typ == 27:
                    if pfad is not None:
                        pfad.append(("M", x, y))
                else:
                    if pfad is not None:
                        pfad.append(("L", x, y))
                    else:
                        z.zeichne([("M", *pos), ("L", x, y)], False, True)
                pos = (float(x), float(y))
            elif typ == 37:                                       # SELECTOBJECT
                h = struct.unpack_from("<I", b, d + 8)[0]
                obj = {0x80000000: _Pinsel(), 0x80000004: _Pinsel(aus=True), 0x80000008: _Stift(), 0x80000006: _Stift(aus=True)}.get(h) if h & 0x80000000 else objekte.get(h)
                if isinstance(obj, _Stift):
                    z.stift = obj
                elif isinstance(obj, _Pinsel):
                    z.pinsel = obj
                elif isinstance(obj, _Schrift):
                    z.schrift = obj
            elif typ == 40:                                       # DELETEOBJECT
                objekte.pop(struct.unpack_from("<I", b, d + 8)[0], None)
            elif typ == 38:                                       # CREATEPEN
                h, stil, breite, _x, farbe = struct.unpack_from("<IIiiI", b, d + 8)
                objekte[h] = _Stift(aus=True) if stil == 5 else _Stift(_farbe(farbe), max(0, breite) or 1)
            elif typ == 95:                                       # EXTCREATEPEN
                h = struct.unpack_from("<I", b, d + 8)[0]
                stil, breite, _pinsel, farbe = struct.unpack_from("<IIII", b, d + 28)
                objekte[h] = _Stift(aus=True) if stil == 5 else _Stift(_farbe(farbe), max(1, breite) or 1)
            elif typ == 39:                                       # CREATEBRUSHINDIRECT
                h, stil, farbe, _hatch = struct.unpack_from("<IIII", b, d + 8)
                objekte[h] = _Pinsel(aus=True) if stil == 1 else _Pinsel(_farbe(farbe))
            elif typ == 82:                                       # EXTCREATEFONTINDIRECTW
                h = struct.unpack_from("<I", b, d + 8)[0]
                hoehe, _breite, _esc, _ori, gewicht = struct.unpack_from("<iiiii", b, d + 12)
                kursiv = b[d + 12 + 20]
                name = b[d + 12 + 28:d + 12 + 28 + 64].decode("utf-16-le", "ignore").split("\x00")[0]
                objekte[h] = _Schrift(name or "Liberation Sans", max(1, abs(hoehe)) if hoehe else 12.0, gewicht >= 600, bool(kursiv))
            elif typ == 24:                                       # SETTEXTCOLOR
                z.textfarbe = _farbe(struct.unpack_from("<I", b, d + 8)[0])
            elif typ == 43:                                       # RECTANGLE
                r = _rechteck(b, d + 8)
                aufnehmen(_rechteck_ops(r.x, r.y, r.width, r.height)) if pfad is None else None
            elif typ == 42:                                       # ELLIPSE
                r = _rechteck(b, d + 8)
                aufnehmen(_ellipse_ops(r.x, r.y, r.width, r.height)) if pfad is None else None
            elif typ == 44:                                       # ROUNDRECT
                r = _rechteck(b, d + 8)
                bw, bh = struct.unpack_from("<ii", b, d + 24)
                aufnehmen(_rund_ops(r.x, r.y, r.width, r.height, bw / 2 or 1, bh / 2 or 1)) if pfad is None else None
            elif typ in (2, 3, 4, 5, 6, 85, 86, 87, 88, 89):      # POLYBEZIER, POLYGON, POLYLINE (und …TO, 16-Bit-Varianten)
                wide = typ < 85
                n = struct.unpack_from("<I", b, d + 24)[0]
                fmt = "<ii" if wide else "<hh"
                punkte = [struct.unpack_from(fmt, b, d + 28 + i * (8 if wide else 4)) for i in range(n)]
                punkte = [(float(x), float(y)) for x, y in punkte]
                if typ in (5, 6, 88, 89):                         # …TO: ab der aktuellen Position
                    punkte = [pos] + punkte
                if typ in (2, 5, 85, 88):                         # POLYBEZIER: Anfangspunkt, dann je drei Punkte
                    if len(punkte) >= 4:
                        ops = ([("M", *punkte[0])] if pfad is None or not pfad else []) + [("C", *punkte[i], *punkte[i + 1], *punkte[i + 2]) for i in range(1, len(punkte) - 2, 3)]
                        if pfad is not None:
                            pfad.extend(ops)
                        else:
                            z.zeichne(ops, False, True)
                else:
                    geschl = typ in (3, 86)
                    ops = _poly_ops(punkte, geschl)
                    if pfad is not None:
                        pfad.extend(ops)
                    else:
                        z.zeichne(ops, geschl, True)
                if punkte:
                    pos = punkte[-1]
            elif typ == 59:                                       # BEGINPATH
                pfad = [("M", *pos)]
            elif typ == 61:                                       # CLOSEFIGURE
                if pfad is not None:
                    pfad.append(("Z",))
            elif typ == 60:                                       # ENDPATH
                pass
            elif typ in (62, 63, 64):                             # FILLPATH, STROKEANDFILLPATH, STROKEPATH
                if pfad is not None:
                    gefuellt, gestrichelt = typ in (62, 63), typ in (63, 64)
                    stil = z._stil(gefuellt, gestrichelt)
                    if stil is not None:
                        z.b.draw_path(z._ops(pfad), stil, True, False)
                pfad = None
            elif typ == 30:                                       # INTERSECTCLIPRECT
                r = _rechteck(b, d + 8)
                z.ausschnitt(r.x, r.y, r.x + r.width, r.y + r.height)
            elif typ == 33:                                       # SAVEDC
                z.sichern((pos,))
            elif typ == 34:                                       # RESTOREDC
                rest = z.wiederherstellen()
                if rest:
                    pos = rest[0]
            elif typ == 17:                                       # SETMAPMODE
                modus = struct.unpack_from("<I", b, d + 8)[0]
                abbilden()
            elif typ in (9, 10, 11, 12):                          # SETWINDOWEXTEX, SETWINDOWORGEX, SETVIEWPORTEXTEX, SETVIEWPORTORGEX
                x, y = struct.unpack_from("<ii", b, d + 8)
                ziel = fenster if typ in (9, 10) else ansicht
                if typ in (9, 11):
                    ziel[2], ziel[3] = x, y
                else:
                    ziel[0], ziel[1] = x, y
                abbilden()
            elif typ in (7, 8, 90, 91):                           # POLYPOLYLINE, POLYPOLYGON (32 und 16 Bit)
                geschl, breit = typ in (8, 91), typ < 90
                teile, gesamt = struct.unpack_from("<II", b, d + 24)
                if teile > 65536 or gesamt > 1_000_000:
                    raise ValueError
                zaehler = struct.unpack_from("<%dI" % teile, b, d + 32)
                ab, gross, i, ops = d + 32 + 4 * teile, 8 if breit else 4, 0, []
                for n in zaehler:
                    pts = [tuple(float(v) for v in struct.unpack_from("<ii" if breit else "<hh", b, ab + (i + j) * gross)) for j in range(n)]
                    i += n
                    ops += _poly_ops(pts, geschl)
                if pfad is not None:
                    pfad.extend(ops)
                else:
                    z.zeichne(ops, geschl, True)
            elif typ in (35, 36):                                 # SETWORLDTRANSFORM, MODIFYWORLDTRANSFORM
                m11, m12, m21, m22, dx, dy = struct.unpack_from("<6f", b, d + 8)
                m = (m11, m12, m21, m22, dx, dy)
                mod = 4 if typ == 35 else struct.unpack_from("<I", b, d + 32)[0]
                z.welt = _EINS if mod == 1 else _mal(z.welt, m) if mod == 2 else _mal(m, z.welt) if mod == 3 else m
                abbilden()
            elif typ == 84:                                       # EXTTEXTOUTW
                refx, refy, zeichen, text_off = struct.unpack_from("<iiII", b, d + 36)
                if zeichen and text_off > 0:
                    z.text(b[d + text_off:d + text_off + zeichen * 2].decode("utf-16-le", "ignore"), refx, refy)
            elif typ in (76, 81):                                 # BITBLT und STRETCHDIBITS mit eingebetteter Bitmap
                if typ == 81:
                    x, y = struct.unpack_from("<ii", b, d + 24)
                    bmi_off, bmi_len, bits_off, bits_len = struct.unpack_from("<IIII", b, d + 48)
                    breite, hoehe = struct.unpack_from("<ii", b, d + 72)
                else:
                    x, y, breite, hoehe = struct.unpack_from("<iiii", b, d + 24)
                    bmi_off, bmi_len, bits_off, bits_len = struct.unpack_from("<IIII", b, d + 84)
                if bmi_len and bits_len:
                    kopf, bits = b[d + bmi_off:d + bmi_off + bmi_len], b[d + bits_off:d + bits_off + bits_len]
                    z.bild(b"BM" + struct.pack("<IHHI", 14 + len(kopf) + len(bits), 0, 0, 14 + len(kopf)) + kopf + bits, x, y, breite, hoehe)
        except (struct.error, IndexError, ValueError, OverflowError):
            pass                                                  # ein nicht lesbarer Befehl wird übersprungen, die übrigen werden gezeichnet
        off += groesse


# ---- WMF ------------------------------------------------------------------------------------------------------------------
def _wmf_fenster(b: bytes, off: int):
    org, ext = (0, 0), None
    while off + 6 <= len(b):
        groesse, fn = struct.unpack_from("<IH", b, off)
        if groesse < 3 or off + groesse * 2 > len(b) or fn == 0:
            break
        if fn == 0x020B and groesse >= 5:
            org = struct.unpack_from("<hh", b, off + 6)[::-1]
        elif fn == 0x020C and groesse >= 5:
            ext = struct.unpack_from("<hh", b, off + 6)[::-1]
        off += groesse * 2
    if ext is None or not ext[0] or not ext[1]:
        return None, (False, False)
    r = Rect(org[0], org[1], ext[0], ext[1])
    r = Rect(min(r.x, r.x + r.width), min(r.y, r.y + r.height), abs(r.width), abs(r.height))
    return r, (ext[0] < 0, ext[1] < 0)


def _wmf_kopf(blob: bytes):
    """(Logische Grenzen, Beginn der Datensätze, Größe in px bei 96 dpi, Spiegelung waagerecht/senkrecht)."""
    if not ist_wmf(blob) or len(blob) < 40:
        return None
    start = 22 + 18 if blob[:4] == _PLACEABLE else 18
    fenster, spiegel = _wmf_fenster(blob, start)
    if blob[:4] == _PLACEABLE:
        links, oben, rechts, unten = struct.unpack_from("<hhhh", blob, 6)
        einheiten = struct.unpack_from("<H", blob, 14)[0] or 1440
        if rechts > links and unten > oben:
            return fenster or Rect(links, oben, rechts - links, unten - oben), start, ((rechts - links) / einheiten * 96, (unten - oben) / einheiten * 96), spiegel
    return fenster or Rect(0, 0, 1000, 1000), start, (400.0, 400.0), spiegel


def wmf_zeichnen(blob: bytes, b, ziel: Rect, engine=None) -> bool:
    """Das WMF als Vektorzeichnung in ``ziel`` auf ``b`` zeichnen. ``False``, wenn es kein lesbares WMF ist."""
    kopf = _wmf_kopf(blob)
    if kopf is None:
        return False
    grenzen, start, _mass, spiegel = kopf
    if engine is None:
        from .textpfad import gemeinsame_engine
        engine = gemeinsame_engine()
    b.push_state(clip=ziel)
    z = _Zeichner(b, engine, _basis(ziel, grenzen, spiegel))
    try:
        _wmf(blob, start, z)
    except (struct.error, IndexError, ValueError, OverflowError):
        pass
    finally:
        z.abschliessen()
        b.pop_state()
    return True


def _wmf(b: bytes, off: int, z: _Zeichner) -> None:
    objekte: list = []
    ausrichtung = 0
    pos = (0.0, 0.0)

    def stock(idx: int):
        return {0: _Pinsel(), 4: _Pinsel(aus=True), 8: _Stift(), 6: _Stift(aus=True)}.get(idx)

    def ablegen(obj) -> None:
        for i, alt in enumerate(objekte):
            if alt is None:
                objekte[i] = obj
                return
        objekte.append(obj)

    def worte(o: int, n: int) -> list:
        return list(struct.unpack_from("<%dh" % n, b, o))

    while off + 6 <= len(b):
        groesse, fn = struct.unpack_from("<IH", b, off)
        if groesse < 3 or off + groesse * 2 > len(b):
            break
        try:
            d = off + 6
            ende = off + groesse * 2
            if fn == 0:
                break
            if fn in (0x020B, 0x020C):
                pass
            elif fn == 0x0418:                                    # ELLIPSE
                u, r_, o, l = worte(d, 4)
                x, y, w, h = _norm(l, o, r_, u)
                z.zeichne(_ellipse_ops(x, y, w, h))
            elif fn == 0x0416:                                    # INTERSECTCLIPRECT
                u, r_, o, l = worte(d, 4)
                x, y, w, h = _norm(l, o, r_, u)
                z.ausschnitt(x, y, x + w, y + h)
            elif fn == 0x0538:                                    # POLYPOLYGON
                n = worte(d, 1)[0]
                zaehler = worte(d + 2, n)
                ab, ops = d + 2 + 2 * n, []
                for c in zaehler:
                    pts = [tuple(float(v) for v in struct.unpack_from("<hh", b, ab + j * 4)) for j in range(c)]
                    ab += c * 4
                    ops += _poly_ops(pts, True)
                z.zeichne(ops)
            elif fn == 0x0214:                                    # MOVETO (y, x)
                y, x = worte(d, 2)
                pos = (float(x), float(y))
            elif fn == 0x0213:                                    # LINETO (y, x)
                y, x = worte(d, 2)
                z.zeichne([("M", *pos), ("L", x, y)], False, True)
                pos = (float(x), float(y))
            elif fn in (0x0324, 0x0325):                          # POLYGON, POLYLINE
                n = worte(d, 1)[0]
                pts = [tuple(float(v) for v in worte(d + 2 + i * 4, 2)) for i in range(n)]
                z.zeichne(_poly_ops(pts, fn == 0x0324), fn == 0x0324, True)
            elif fn == 0x061D:                                    # ROUNDRECT
                eh, ew, u, r_, o, l = worte(d, 6)
                x, y, w, h = _norm(l, o, r_, u)
                z.zeichne(_rund_ops(x, y, w, h, ew / 2 or 1, eh / 2 or 1))
            elif fn == 0x041B:                                    # RECTANGLE
                u, r_, o, l = worte(d, 4)
                x, y, w, h = _norm(l, o, r_, u)
                z.zeichne(_rechteck_ops(x, y, w, h))
            elif fn == 0x012D:                                    # SELECTOBJECT
                idx = struct.unpack_from("<H", b, d)[0]
                obj = stock(idx & 0x7FFF) if idx & 0x8000 else (objekte[idx] if idx < len(objekte) else None)
                if isinstance(obj, _Stift):
                    z.stift = obj
                elif isinstance(obj, _Pinsel):
                    z.pinsel = obj
                elif isinstance(obj, _Schrift):
                    z.schrift = obj
            elif fn == 0x01F0:                                    # DELETEOBJECT
                idx = struct.unpack_from("<H", b, d)[0]
                if idx < len(objekte):
                    objekte[idx] = None
            elif fn == 0x02FA:                                    # CREATEPENINDIRECT
                stil = struct.unpack_from("<H", b, d)[0]
                breite = struct.unpack_from("<h", b, d + 2)[0]
                farbe = struct.unpack_from("<I", b, d + 6)[0]
                ablegen(_Stift(aus=True) if stil == 5 else _Stift(_farbe(farbe), max(1, breite) or 1))
            elif fn == 0x02FC:                                    # CREATEBRUSHINDIRECT
                stil = struct.unpack_from("<H", b, d)[0]
                farbe = struct.unpack_from("<I", b, d + 2)[0]
                ablegen(_Pinsel(aus=True) if stil == 1 else _Pinsel(_farbe(farbe)))
            elif fn == 0x02FB:                                    # CREATEFONTINDIRECT
                hoehe, _b, _e, _o, gewicht = struct.unpack_from("<hhhhh", b, d)
                kursiv = b[d + 10]
                name = b[d + 18:d + 18 + 32].split(b"\x00")[0].decode("cp1252", "ignore")
                ablegen(_Schrift(name or "Liberation Sans", max(1, abs(hoehe)) if hoehe else 12.0, gewicht >= 600, bool(kursiv)))
            elif fn == 0x0209:                                    # SETTEXTCOLOR
                z.textfarbe = _farbe(struct.unpack_from("<I", b, d)[0])
            elif fn == 0x012E:                                    # SETTEXTALIGN
                ausrichtung = struct.unpack_from("<H", b, d)[0]
            elif fn == 0x001E:                                    # SAVEDC
                z.sichern((pos,))
            elif fn == 0x0127:                                    # RESTOREDC
                rest = z.wiederherstellen()
                if rest:
                    pos = rest[0]
            elif fn == 0x0A32:                                    # EXTTEXTOUT
                y, x, laenge, optionen = worte(d, 4)
                t = d + 8 + (8 if optionen & 6 else 0)
                z.text(b[t:t + laenge].decode("cp1252", "ignore"), x, y, 0.0 if (ausrichtung & 24) == 24 else 1.0)
            elif fn == 0x0521:                                    # TEXTOUT
                laenge = worte(d, 1)[0]
                text = b[d + 2:d + 2 + laenge].decode("cp1252", "ignore")
                y, x = struct.unpack_from("<hh", b, d + 2 + laenge + (laenge & 1))
                z.text(text, x, y, 0.0 if (ausrichtung & 24) == 24 else 1.0)
            elif fn == 0x0F43:                                    # STRETCHDIB
                _rop, _usage, _sh, _sb, _ys, _xs, zh, zb, yd, xd = struct.unpack_from("<IHhhhhhhhh", b, d)
                dib = d + 22
                kopf_groesse = struct.unpack_from("<I", b, dib)[0]
                _w, _h, _planes, bpp, komp = struct.unpack_from("<iiHHI", b, dib + 4)
                clr_used = struct.unpack_from("<I", b, dib + 32)[0] if kopf_groesse >= 40 else 0
                palette_bytes = (clr_used or (1 << bpp if bpp <= 8 else 0)) * 4
                zeile = ((abs(_w) * bpp + 31) // 32) * 4
                bild_bytes = zeile * abs(_h) if komp == 0 else struct.unpack_from("<I", b, dib + 20)[0]
                kopf = b[dib:dib + kopf_groesse + palette_bytes]
                bits = b[dib + kopf_groesse + palette_bytes:dib + kopf_groesse + palette_bytes + bild_bytes]
                z.bild(b"BM" + struct.pack("<IHHI", 14 + len(kopf) + len(bits), 0, 0, 14 + len(kopf)) + kopf + bits, xd, yd, zb, zh)
        except (struct.error, IndexError, ValueError, OverflowError):
            pass
        off = ende


def metafile_rgba(blob: bytes, breite_px: int = 0, hoehe_px: int = 0, engine=None):
    """Das EMF oder WMF gerastert: ``(breite, hoehe, RGBA)`` (doppelt so fein wie 96 dpi, höchstens ``MAX_SEITE_PX``); ``None``, wenn es kein lesbares Metafile ist."""
    from .rasterziel import RasterZiel
    if ist_emf(blob):
        kopf = _emf_kopf(blob)
        if kopf is None:
            return None
        gross = (kopf[1].width / 2540 * 96 * 2, kopf[1].height / 2540 * 96 * 2) if kopf[1].width > 0 and kopf[1].height > 0 else (400.0, 400.0)
        zeichne = emf_zeichnen
    elif ist_wmf(blob):
        kopf = _wmf_kopf(blob)
        if kopf is None:
            return None
        gross = (kopf[2][0] * 2, kopf[2][1] * 2)
        zeichne = wmf_zeichnen
    else:
        return None
    if not breite_px or not hoehe_px:
        breite_px, hoehe_px = begrenzt(*gross)
    if engine is None:
        from .textpfad import gemeinsame_engine
        engine = gemeinsame_engine()
    ziel = RasterZiel(engine, breite_px, hoehe_px, 1.0, (255, 255, 255, 0))
    if not zeichne(blob, ziel, Rect(0, 0, breite_px, hoehe_px), engine):
        return None
    b, h, roh = ziel.als_rgba()
    return b, h, bytearray(roh)
