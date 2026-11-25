"""Rasterzeichenfläche des Kerns: ein ``RenderBackend``, das Seiten ohne Qt und ohne weitere Bibliothek in ein RGBA-Bild zeichnet (Editor-Ansicht, Druck, Bildexport).

Alles Gezeichnete besteht aus Pfaden: Glyphen (Konturen aus dem Textsatz-Kern), Formen, Linien (Strichgeometrie mit Enden, Ecken und Strichmustern) und Bildern
(abgetastet nach der Abbildung). Abdeckung: Scanline mit vier Teilzeilen je Pixelzeile und exakter Abdeckung in x. Ausschnitte sind Rechtecke oder Masken, Deckkraft multipliziert,
Verschiebung, Drehung und Spiegelung wirken über eine Matrix. Die Rasterung auf Ausgabepixel passiert erst hier, nicht im Layout."""
from __future__ import annotations

import hashlib
import math

from lunivo_writer.kern.geometrie import Point, Rect
from lunivo_writer.kern.textsatz.engine import FontSpec
from .backend import ImageFill, LinearGradient, PatternFill, RadialGradient, RenderBackend, Style, TextureFill, rgba
from lunivo_writer.kern.rendering import bild3d, bildeffekte
from .bildeffekte import skaliert
from .bilddecoder import bild_dekodieren
from .fuellmuster import kachel_von
from .textpfad import TextAusKern

_TEIL = 4                                                                    # Teilzeilen je Pixelzeile
_STRICH = {"dot": (1, 1), "dash": (4, 2), "dashdot": (4, 2, 1, 2), "dashdotdot": (4, 2, 1, 2, 1, 2)}


def _pt(m, x, y):
    return (m[0] * x + m[2] * y + m[4], m[1] * x + m[3] * y + m[5])


def _mal(m, a):
    """Matrix ``m`` nach ``a`` angewendet (zuerst ``a``, dann ``m``)."""
    return (m[0] * a[0] + m[2] * a[1], m[1] * a[0] + m[3] * a[1], m[0] * a[2] + m[2] * a[3], m[1] * a[2] + m[3] * a[3],
            m[0] * a[4] + m[2] * a[5] + m[4], m[1] * a[4] + m[3] * a[5] + m[5])


def _invers(m):
    det = m[0] * m[3] - m[1] * m[2]
    if abs(det) < 1e-12:
        return None
    a, b, c, d = m[3] / det, -m[1] / det, -m[2] / det, m[0] / det
    return (a, b, c, d, -(a * m[4] + c * m[5]), -(b * m[4] + d * m[5]))


def _flaeche(poly) -> float:
    return sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly))) / 2.0


def _kreis(cx: float, cy: float, r: float, n: int = 16):
    return [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _ellipse(cx: float, cy: float, rx: float, ry: float, n: int = 48):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


class RasterZiel(TextAusKern, RenderBackend):
    glyphen_aus_kern = False                                                  # Text kommt als Glyphenpfade (``zeichne_text``)

    def __init__(self, engine, breite_px: float, hoehe_px: float, massstab: float = 1.0, papier: tuple = (255, 255, 255, 255)):
        self.engine = engine
        self.b, self.h = max(1, round(breite_px * massstab)), max(1, round(hoehe_px * massstab))
        self.px = bytearray(bytes(papier) * (self.b * self.h))
        self._m = (massstab, 0.0, 0.0, massstab, 0.0, 0.0)
        self._clip = (0, 0, self.b, self.h, None)
        self._deckkraft = 1.0
        self._stapel: list = []
        self._bilder: dict = {}
        self.hinweise: list[str] = []

    def als_rgba(self) -> tuple[int, int, bytes]:
        return self.b, self.h, bytes(self.px)

    # ---- Zustand ----
    def push_state(self, opacity: float = 1.0, translate: Point | None = None, rotate: float = 0.0, clip: Rect | None = None,
                   antialias: bool | None = None, clip_ellipse: Rect | None = None, flip_h: bool = False, flip_v: bool = False) -> None:
        self._stapel.append((self._m, self._clip, self._deckkraft))
        if clip is not None:
            self._ausschnitt([(clip.x, clip.y), (clip.x + clip.width, clip.y), (clip.x + clip.width, clip.y + clip.height), (clip.x, clip.y + clip.height)], True)
        if clip_ellipse is not None:
            self._ausschnitt(_ellipse(clip_ellipse.x + clip_ellipse.width / 2, clip_ellipse.y + clip_ellipse.height / 2, clip_ellipse.width / 2, clip_ellipse.height / 2), False)
        self._deckkraft *= max(0.0, min(1.0, opacity))
        if translate is not None:
            self._m = _mal(self._m, (1.0, 0.0, 0.0, 1.0, translate.x, translate.y))
        if rotate:
            c, s = math.cos(math.radians(rotate)), math.sin(math.radians(rotate))
            self._m = _mal(self._m, (c, s, -s, c, 0.0, 0.0))
        if flip_h or flip_v:
            self._m = _mal(self._m, (-1.0 if flip_h else 1.0, 0.0, 0.0, -1.0 if flip_v else 1.0, 0.0, 0.0))

    def pop_state(self) -> None:
        if self._stapel:
            self._m, self._clip, self._deckkraft = self._stapel.pop()

    def _ausschnitt(self, user_poly, ist_rechteck: bool) -> None:
        dev = [_pt(self._m, x, y) for x, y in user_poly]
        x0, y0, x1, y1, maske = self._clip
        achsen = abs(self._m[1]) < 1e-9 and abs(self._m[2]) < 1e-9 or abs(self._m[0]) < 1e-9 and abs(self._m[3]) < 1e-9
        xs, ys = [p[0] for p in dev], [p[1] for p in dev]
        if ist_rechteck and achsen:
            self._clip = (max(x0, round(min(xs))), max(y0, round(min(ys))), min(x1, round(max(xs))), min(y1, round(max(ys))), maske)
            return
        neu = bytearray(self.b * self.h)
        grenze = (max(x0, int(math.floor(min(xs)))), max(y0, int(math.floor(min(ys)))), min(x1, int(math.ceil(max(xs)))), min(y1, int(math.ceil(max(ys)))))
        for y, xa, cov in self._abdecken([dev], True, grenze):
            o = y * self.b + xa
            for i, c in enumerate(cov):
                if c > 0.004:
                    v = int(c * 255 + 0.5)
                    neu[o + i] = v * maske[o + i] // 255 if maske is not None else v
        self._clip = (grenze[0], grenze[1], max(grenze[0], grenze[2]), max(grenze[1], grenze[3]), neu)

    # ---- Abdeckung ----
    def _abdecken(self, polys, gerade: bool = True, grenze=None):
        cx0, cy0, cx1, cy1 = grenze if grenze is not None else self._clip[:4]
        kanten = []
        mnx = mny = 1e18
        mxx = mxy = -1e18
        for pts in polys:
            n = len(pts)
            if n < 3:
                continue
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                mnx, mxx = min(mnx, x0), max(mxx, x0)
                mny, mxy = min(mny, y0), max(mxy, y0)
                if y0 == y1:
                    continue
                if y0 < y1:
                    kanten.append((y0, y1, x0, (x1 - x0) / (y1 - y0), 1))
                else:
                    kanten.append((y1, y0, x1, (x0 - x1) / (y0 - y1), -1))
        if not kanten:
            return
        ya, ye = max(cy0, int(math.floor(mny))), min(cy1, int(math.ceil(mxy)))
        xa, xe = max(cx0, int(math.floor(mnx))), min(cx1, int(math.ceil(mxx)))
        if ya >= ye or xa >= xe:
            return
        kanten.sort()
        breite, nk, nxt, aktiv = xe - xa, len(kanten), 0, []
        gew = 1.0 / _TEIL
        for y in range(ya, ye):
            while nxt < nk and kanten[nxt][0] < y + 1:
                aktiv.append(kanten[nxt])
                nxt += 1
            aktiv = [k for k in aktiv if k[1] > y]
            if not aktiv:
                continue
            zeile, diff = [0.0] * (breite + 2), [0.0] * (breite + 3)
            for s in range(_TEIL):
                sy = y + (s + 0.5) / _TEIL
                kreuz = [(kx + steig * (sy - ky0), r) for ky0, ky1, kx, steig, r in aktiv if ky0 <= sy < ky1]
                if len(kreuz) < 2:
                    continue
                kreuz.sort()
                wind = 0
                for j in range(len(kreuz) - 1):
                    wind += kreuz[j][1]
                    if (wind & 1) if gerade else (wind != 0):
                        a, b = kreuz[j][0] - xa, kreuz[j + 1][0] - xa
                        a, b = (0.0 if a < 0 else a), (float(breite) if b > breite else b)
                        if b <= a:
                            continue
                        ia, ib = int(a), int(b)
                        if ia == ib:
                            zeile[ia] += (b - a) * gew
                        else:
                            zeile[ia] += (ia + 1 - a) * gew
                            zeile[ib] += (b - ib) * gew
                            diff[ia + 1] += gew
                            diff[ib] -= gew
            lauf, cov = 0.0, [0.0] * breite
            for i in range(breite):
                lauf += diff[i]
                v = zeile[i] + lauf
                cov[i] = 1.0 if v > 1.0 else (v if v > 0.0 else 0.0)
            yield y, xa, cov

    def _zeile(self, y: int, x0: int, cov: list, farbe, shader) -> None:
        px, breite, maske = self.px, self.b, self._clip[4]
        basis = (y * breite + x0)
        deck = self._deckkraft
        if shader is None:
            r, g, bl, a0 = farbe
            fa = a0 / 255.0 * deck
        for i, c in enumerate(cov):
            if c <= 0.004:
                continue
            if maske is not None:
                c = c * maske[basis + i] / 255.0
                if c <= 0.004:
                    continue
            if shader is not None:
                r, g, bl, a0 = shader(x0 + i + 0.5, y + 0.5)
                a = c * a0 / 255.0 * deck
            else:
                a = c * fa
            if a <= 0.004:
                continue
            o = (basis + i) * 4
            if a >= 0.996:
                px[o], px[o + 1], px[o + 2], px[o + 3] = r, g, bl, 255
            else:
                da = px[o + 3]
                if da == 255:
                    px[o] = int(px[o] + (r - px[o]) * a + 0.5)
                    px[o + 1] = int(px[o + 1] + (g - px[o + 1]) * a + 0.5)
                    px[o + 2] = int(px[o + 2] + (bl - px[o + 2]) * a + 0.5)
                else:
                    ra = a + da / 255.0 * (1.0 - a)
                    if ra > 0:
                        for k, v in enumerate((r, g, bl)):
                            px[o + k] = int((v * a + px[o + k] * da / 255.0 * (1.0 - a)) / ra + 0.5)
                    px[o + 3] = int(ra * 255 + 0.5)

    def _fuellen(self, polys, gerade: bool, farbe=None, shader=None) -> None:
        for y, xa, cov in self._abdecken(polys, gerade):
            self._zeile(y, xa, cov, farbe, shader)

    # ---- Pfade ----
    def _flach(self, ops: list) -> list:
        sc = math.sqrt(abs(self._m[0] * self._m[3] - self._m[1] * self._m[2])) or 1.0
        teile, akt, ax, ay = [], None, 0.0, 0.0

        def neu(punkt):
            nonlocal akt
            akt = [punkt]
            teile.append([akt, False])

        for op in ops:
            k = op[0]
            if k == "M":
                neu((op[1], op[2]))
                ax, ay = op[1], op[2]
            elif k == "L" and akt is not None:
                akt.append((op[1], op[2]))
                ax, ay = op[1], op[2]
            elif k == "Q" and akt is not None:
                laenge = (math.hypot(op[1] - ax, op[2] - ay) + math.hypot(op[3] - op[1], op[4] - op[2])) * sc
                n = max(2, min(40, int(laenge / 4) + 2))
                for t in range(1, n + 1):
                    u = t / n
                    akt.append(((1 - u) ** 2 * ax + 2 * (1 - u) * u * op[1] + u * u * op[3], (1 - u) ** 2 * ay + 2 * (1 - u) * u * op[2] + u * u * op[4]))
                ax, ay = op[3], op[4]
            elif k == "C" and akt is not None:
                laenge = (math.hypot(op[1] - ax, op[2] - ay) + math.hypot(op[3] - op[1], op[4] - op[2]) + math.hypot(op[5] - op[3], op[6] - op[4])) * sc
                n = max(2, min(48, int(laenge / 4) + 2))
                for t in range(1, n + 1):
                    u = t / n
                    v = 1 - u
                    akt.append((v ** 3 * ax + 3 * v * v * u * op[1] + 3 * v * u * u * op[3] + u ** 3 * op[5], v ** 3 * ay + 3 * v * v * u * op[2] + 3 * v * u * u * op[4] + u ** 3 * op[6]))
                ax, ay = op[5], op[6]
            elif k == "Z" and akt is not None:
                teile[-1][1] = True
                ax, ay = akt[0]
                neu((ax, ay))
            elif k == "E":
                teile.append([_ellipse(op[1], op[2], op[3], op[4], max(24, min(96, int(max(op[3], op[4]) * sc / 2)))), True])
                akt = None
            elif k == "R":
                teile.append([[(op[1], op[2]), (op[1] + op[3], op[2]), (op[1] + op[3], op[2] + op[4]), (op[1], op[2] + op[4])], True])
                akt = None
        return teile

    def _paint(self, teile: list, style: Style, rechteck: bool = False, gerade: bool = True) -> None:
        fuell, linie = bool(style.filled), style.width > 0
        if fuell:
            polys = [[_pt(self._m, x, y) for x, y in pts] for pts, _g in teile if len(pts) >= 3]
            f = style.fill
            if isinstance(f, (LinearGradient, RadialGradient)):
                self._fuellen(polys, gerade, shader=self._verlauf(f))
            elif isinstance(f, ImageFill):
                xs = [p[0] for pts, _g in teile for p in pts]
                ys = [p[1] for pts, _g in teile for p in pts]
                if xs:
                    self._bild_fuellen(f.data, Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)), polys, gerade)
            elif isinstance(f, (PatternFill, TextureFill)):
                self._fuellen(polys, gerade, shader=self._kachel_shader(f))
            else:
                self._fuellen(polys, gerade, farbe=style.color)
        if linie:
            muster = _STRICH.get(style.dash) if isinstance(style.dash, str) else (style.dash if isinstance(style.dash, tuple) else (_STRICH["dash"] if style.dashed else None))
            polys = [[_pt(self._m, x, y) for x, y in p] for p in self._strich(teile, style.width, style.cap, style.join, muster)]
            self._fuellen(polys, False, farbe=style.outline or style.color)

    def draw_path(self, ops: list, style: Style, antialias: bool | None = True, union: bool = False) -> None:
        if ops:
            self._paint(self._flach(ops), style, gerade=not union)

    def draw_rect(self, rect: Rect, style: Style) -> None:
        m, x, y, w, h = self._m, rect.x, rect.y, rect.width, rect.height
        a = style.color[3] / 255.0 * self._deckkraft
        if (style.filled and style.width <= 0 and style.fill is None and abs(m[1]) < 1e-9 and abs(m[2]) < 1e-9 and self._clip[4] is None and a >= 0.004 and w > 0 and h > 0):
            ax, ay = _pt(m, x, y)
            bx, by = _pt(m, x + w, y + h)
            x0, x1, y0, y1 = min(ax, bx), max(ax, bx), min(ay, by), max(ay, by)
            cx0, cy0, cx1, cy1 = self._clip[:4]
            ix0, ix1, iy0, iy1 = max(cx0, int(math.ceil(x0))), min(cx1, int(math.floor(x1))), max(cy0, int(math.ceil(y0))), min(cy1, int(math.floor(y1)))
            if ix1 > ix0 and iy1 > iy0:
                deckend = a >= 0.996
                zeile = bytes((style.color[0], style.color[1], style.color[2], 255 if deckend else round(a * 255))) * (ix1 - ix0)
                leer = bytes(len(zeile))
                for yy in range(iy0, iy1):
                    o = (yy * self.b + ix0) * 4
                    if deckend or self.px[o:o + len(zeile)] == leer:           # deckend oder auf durchsichtigem Grund: Zeile am Stück setzen
                        self.px[o:o + len(zeile)] = zeile
                    else:
                        self._zeile(yy, ix0, [1.0] * (ix1 - ix0), style.color, None)
                farbe = style.color
                for (sx0, sy0, sx1, sy1) in ((x0, y0, x1, iy0), (x0, iy1, x1, y1), (x0, iy0, ix0, iy1), (ix1, iy0, x1, iy1)):
                    if sx1 > sx0 and sy1 > sy0:
                        self._fuellen([[(sx0, sy0), (sx1, sy0), (sx1, sy1), (sx0, sy1)]], True, farbe=farbe)
                return
        self._paint([[[(x, y), (x + w, y), (x + w, y + h), (x, y + h)], True]], style)

    def draw_ellipse(self, center: Point, rx: float, ry: float, style: Style) -> None:
        self._paint([[_ellipse(center.x, center.y, rx, ry, max(24, min(96, int(max(rx, ry) * math.sqrt(abs(self._m[0] * self._m[3])) / 2)))), True]], style)

    def draw_line(self, start: Point, end: Point, style: Style) -> None:
        self._paint([[[(start.x, start.y), (end.x, end.y)], False]], Style(color=style.color, width=style.width, filled=False, dashed=style.dashed, dash=style.dash,
                                                                          cap=style.cap, join=style.join, outline=style.outline))

    def draw_shadow(self, ops: list, color: tuple, blur: float, dx: float, dy: float) -> None:
        """Schatten: die Abdeckung der Form, um (dx, dy) versetzt und mit Radius ``blur`` (Bildpunkte) weichgezeichnet (dreimal Kastenfilter ≈ Gauß)."""
        teile = self._flach(ops)
        polys = [[_pt(self._m, x + dx, y + dy) for x, y in pts] for pts, _g in teile if len(pts) >= 3]
        if not polys:
            return
        sc = math.sqrt(abs(self._m[0] * self._m[3] - self._m[1] * self._m[2])) or 1.0
        r = int(round(blur * sc / 2.0))
        if r < 1:
            self._fuellen(polys, True, farbe=color)
            return
        xs = [p[0] for poly in polys for p in poly]
        ys = [p[1] for poly in polys for p in poly]
        cx0, cy0, cx1, cy1 = self._clip[:4]
        pad = 3 * r + 2
        x0, y0 = max(cx0 - pad, int(math.floor(min(xs))) - pad), max(cy0 - pad, int(math.floor(min(ys))) - pad)
        x1, y1 = min(cx1 + pad, int(math.ceil(max(xs))) + pad), min(cy1 + pad, int(math.ceil(max(ys))) + pad)
        w, h = x1 - x0, y1 - y0
        if w <= 0 or h <= 0 or w * h > 16_000_000:
            return
        gitter = [[0.0] * w for _ in range(h)]
        for y, xa, cov in self._abdecken(polys, True, (x0, y0, x1, y1)):
            zeile = gitter[y - y0]
            for i, c in enumerate(cov):
                if c > 0:
                    zeile[xa - x0 + i] = c
        for _ in range(3):
            for y in range(h):                                                          # waagerecht: gleitende Summe
                z, neu, summe = gitter[y], [0.0] * w, 0.0
                n = 2 * r + 1
                for x in range(min(r, w)):
                    summe += z[x]
                for x in range(w):
                    if x + r < w:
                        summe += z[x + r]
                    if x - r - 1 >= 0:
                        summe -= z[x - r - 1]
                    neu[x] = summe / n
                gitter[y] = neu
            for x in range(w):                                                          # senkrecht
                summe, n = 0.0, 2 * r + 1
                spalte = [gitter[y][x] for y in range(h)]
                for y in range(min(r, h)):
                    summe += spalte[y]
                for y in range(h):
                    if y + r < h:
                        summe += spalte[y + r]
                    if y - r - 1 >= 0:
                        summe -= spalte[y - r - 1]
                    gitter[y][x] = summe / n
        for y in range(max(y0, cy0), min(y1, cy1)):
            a, b = max(x0, cx0), min(x1, cx1)
            if b > a:
                self._zeile(y, a, gitter[y - y0][a - x0:b - x0], color, None)

    def draw_text(self, text: str, position: Point, font, style: Style) -> None:
        """Waagerechter Text wird in Gerätegröße gerastert (scharf, Grundlinie auf ganzer Pixelzeile); gedrehter oder gespiegelter Text füllt die Glyphenpfade."""
        if not text or not isinstance(font, FontSpec):
            return
        m = self._m
        if abs(m[1]) < 1e-9 and abs(m[2]) < 1e-9 and m[0] > 1e-9 and abs(m[0] - m[3]) < 1e-9 * m[0] and hasattr(self.engine, "text_deckung"):
            x, y = m[0] * position.x + m[4], m[3] * position.y + m[5]
            for gx, gy, b, h, zeilen in self.engine.text_deckung(text, font, x, y, m[0]):
                cx0, cy0, cx1, cy1 = self._clip[:4]
                for r in range(max(0, cy0 - gy), min(h, cy1 - gy)):
                    a0, a1 = max(0, cx0 - gx), min(b, cx1 - gx)
                    if a1 > a0:
                        self._zeile(gy + r, gx + a0, [v / 255.0 for v in zeilen[r * b + a0:r * b + a1]], style.color, None)
            return
        self.draw_path(self.engine.glyphen_pfad(text, font, position.x, position.y), Style(color=style.color, width=0, filled=True), True, True)

    # ---- Strichgeometrie ----
    def _strich(self, teile: list, breite: float, kappe: str, ecke: str, muster) -> list:
        hw = breite / 2.0
        aus = []
        for pts, geschl in teile:
            p = [pts[0]] if pts else []
            for q in pts[1:]:
                if abs(q[0] - p[-1][0]) > 1e-9 or abs(q[1] - p[-1][1]) > 1e-9:
                    p.append(q)
            if len(p) < 2:
                continue
            if geschl and (abs(p[0][0] - p[-1][0]) > 1e-9 or abs(p[0][1] - p[-1][1]) > 1e-9):
                p.append(p[0])
            stuecke = self._gestrichelt(p, [m * breite for m in muster], geschl) if muster else [(p, geschl)]
            for sp, sg in stuecke:
                aus += self._linie(sp, hw, kappe, ecke, sg)
        return aus

    @staticmethod
    def _gestrichelt(pts: list, muster: list, geschlossen: bool) -> list:
        aus, i, rest, an = [], 0, muster[0], True
        akt = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            laenge = math.hypot(b[0] - a[0], b[1] - a[1])
            if laenge == 0:
                continue
            pos = 0.0
            while laenge - pos > rest:
                pos += rest
                punkt = (a[0] + (b[0] - a[0]) * pos / laenge, a[1] + (b[1] - a[1]) * pos / laenge)
                if an:
                    akt.append(punkt)
                    aus.append((akt, False))
                    akt = []
                else:
                    akt = [punkt]
                an = not an
                i = (i + 1) % len(muster)
                rest = muster[i] or 1e-6
            rest -= laenge - pos
            if an:
                akt.append(b)
        if an and len(akt) > 1:
            aus.append((akt, False))
        return aus

    @staticmethod
    def _linie(pts: list, hw: float, kappe: str, ecke: str, geschlossen: bool) -> list:
        polys = []
        n = len(pts) - 1
        richt = []
        for a, b in zip(pts, pts[1:]):
            l = math.hypot(b[0] - a[0], b[1] - a[1]) or 1.0
            richt.append(((b[0] - a[0]) / l, (b[1] - a[1]) / l))

        def ccw(poly):
            return poly if _flaeche(poly) >= 0 else poly[::-1]

        for i in range(n):
            a, b = pts[i], pts[i + 1]
            dx, dy = richt[i]
            if not geschlossen and kappe == "square":
                if i == 0:
                    a = (a[0] - dx * hw, a[1] - dy * hw)
                if i == n - 1:
                    b = (b[0] + dx * hw, b[1] + dy * hw)
            nx, ny = -dy * hw, dx * hw
            polys.append(ccw([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)]))
        if not geschlossen and kappe == "round":
            polys.append(ccw(_kreis(pts[0][0], pts[0][1], hw)))
            polys.append(ccw(_kreis(pts[-1][0], pts[-1][1], hw)))
        verbindungen = list(range(1, n)) + ([0] if geschlossen and n > 1 else [])
        for i in verbindungen:
            v = pts[i]
            d1, d2 = richt[i - 1], richt[i]
            if ecke == "round":
                polys.append(ccw(_kreis(v[0], v[1], hw)))
                continue
            kreuz = d1[0] * d2[1] - d1[1] * d2[0]
            if abs(kreuz) < 1e-9:
                continue
            vz = -1.0 if kreuz > 0 else 1.0
            n1, n2 = (-d1[1] * hw * vz, d1[0] * hw * vz), (-d2[1] * hw * vz, d2[0] * hw * vz)
            a, c = (v[0] + n1[0], v[1] + n1[1]), (v[0] + n2[0], v[1] + n2[1])
            punkt = d1[0] * d2[0] + d1[1] * d2[1]
            if ecke == "miter" and 1 + punkt > 1e-9 and math.sqrt(2.0 / (1 + punkt)) <= 2.0:
                spitze = (v[0] + (n1[0] + n2[0]) / (1 + punkt), v[1] + (n1[1] + n2[1]) / (1 + punkt))
                polys.append(ccw([v, a, spitze, c]))
            else:
                polys.append(ccw([v, a, c]))
        return polys

    # ---- Muster und Texturen ----
    def _kachel_shader(self, fuellung):
        """Farbe je Ausgabepixel aus der Kachel; die Kachel liegt im Benutzerkoordinatensystem (sie folgt Drehung und Zoom der Zeichenfläche)."""
        tw, th, kachel = kachel_von(fuellung)
        inv = _invers(self._m)
        if inv is None:
            return lambda x, y: kachel[0]

        def schatten(x, y):
            ux, uy = _pt(inv, x, y)
            return kachel[(int(math.floor(uy)) % th) * tw + int(math.floor(ux)) % tw]
        return schatten

    # ---- Verläufe ----
    def _verlauf(self, f):
        stops = sorted(f.stops, key=lambda s: s[0]) or [(0.0, (0, 0, 0, 255)), (1.0, (255, 255, 255, 255))]
        tabelle = []
        for k in range(256):
            t = k / 255.0
            if t <= stops[0][0]:
                tabelle.append(tuple(stops[0][1]))
            elif t >= stops[-1][0]:
                tabelle.append(tuple(stops[-1][1]))
            else:
                for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
                    if p0 <= t <= p1:
                        u = (t - p0) / ((p1 - p0) or 1.0)
                        tabelle.append(tuple(int(c0[i] + (c1[i] - c0[i]) * u + 0.5) for i in range(4)))
                        break
        inv = _invers(self._m)
        if inv is None:
            return lambda x, y: tabelle[0]
        if isinstance(f, LinearGradient):
            ex, ey = f.end.x - f.start.x, f.end.y - f.start.y
            q = (ex * ex + ey * ey) or 1.0

            def schatten(x, y):
                ux, uy = _pt(inv, x, y)
                t = ((ux - f.start.x) * ex + (uy - f.start.y) * ey) / q
                return tabelle[int(255 * (0.0 if t < 0 else 1.0 if t > 1 else t))]
        else:
            def schatten(x, y):
                ux, uy = _pt(inv, x, y)
                t = math.hypot(ux - f.center.x, uy - f.center.y) / (f.radius or 1.0)
                return tabelle[int(255 * (1.0 if t > 1 else t))]
        return schatten

    # ---- Bilder ----
    def _bild(self, daten: bytes, ziel_breite: float):
        gruppe = 0 if ziel_breite <= 0 else min(4, max(0, int(math.log2(max(1.0, ziel_breite / 64.0)))))
        schluessel = (hashlib.sha1(daten).hexdigest(), gruppe)
        if schluessel not in self._bilder:
            self._bilder[schluessel] = bild_dekodieren(daten, ziel_breite * 1.0 if ziel_breite > 0 else None)
        return self._bilder[schluessel]

    def draw_image(self, data: bytes, rect: Rect, smooth: bool = False, wash: float = 0.0, source_rect: Rect | None = None) -> None:
        quad = [(rect.x, rect.y), (rect.x + rect.width, rect.y), (rect.x + rect.width, rect.y + rect.height), (rect.x, rect.y + rect.height)]
        self._bild_fuellen(data, rect, [[_pt(self._m, x, y) for x, y in quad]], True, smooth, wash, source_rect)

    def _bild_fuellen(self, data: bytes, rect: Rect, polys: list, gerade: bool, smooth: bool = True, wash: float = 0.0, source_rect: Rect | None = None, fertig=None) -> None:
        sx, sy = math.hypot(self._m[0], self._m[1]), math.hypot(self._m[2], self._m[3])
        bild = fertig if fertig is not None else self._bild(data, rect.width * sx / (source_rect.width if source_rect is not None and source_rect.width > 0 else 1.0))
        if bild is None or rect.width <= 0 or rect.height <= 0:
            self.hinweise.append("Ein Bild in einem Format, das hier nicht gelesen wird (PNG und sequenzielles JPEG), steht als Platzhalter.")
            self._fuellen(polys, gerade, farbe=(232, 232, 236, 255))
            return
        bw, bh, daten = bild
        u0, v0, du, dv = (0.0, 0.0, 1.0, 1.0) if source_rect is None else (source_rect.x, source_rect.y, source_rect.width, source_rect.height)
        a = _mal(self._m, (rect.width, 0.0, 0.0, rect.height, rect.x, rect.y))
        inv = _invers(a)
        if inv is None:
            return
        schritt = max((bw * du) / max(1.0, rect.width * sx), (bh * dv) / max(1.0, rect.height * sy))
        taps = [(0.0, 0.0)] if schritt < 1.6 else ([(-0.25, -0.25), (0.25, -0.25), (-0.25, 0.25), (0.25, 0.25)] if schritt < 3.0 else [((a_ - 1) / 3.0, (b_ - 1) / 3.0) for a_ in range(3) for b_ in range(3)])
        taps = [(tx * schritt, ty * schritt) for tx, ty in taps]
        weiss = max(0.0, min(1.0, wash))

        ia, ib, ic, id_, ie, if_ = inv
        if len(taps) == 1 and not (smooth and schritt < 1.6):                  # Schnellpfad: eine Abtastung, nächster Nachbar (kein Funktionsaufruf je Pixel)
            fa, fb = du * bw, dv * bh
            ox, oy = u0 * bw - 0.5 + taps[0][0] + 0.5, v0 * bh - 0.5 + taps[0][1] + 0.5
            bw1, bh1 = bw - 1, bh - 1

            def schnell(x, y):
                u = ia * x + ic * y + ie
                v = ib * x + id_ * y + if_
                u = 0.0 if u < 0.0 else 1.0 if u > 1.0 else u
                v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
                qx, qy = int(u * fa + ox), int(v * fb + oy)
                o = ((0 if qy < 0 else bh1 if qy > bh1 else qy) * bw + (0 if qx < 0 else bw1 if qx > bw1 else qx)) * 4
                pa = daten[o + 3]
                if pa == 0:
                    return (0, 0, 0, 0)
                if weiss:
                    return (int(daten[o] + (255 - daten[o]) * weiss + 0.5), int(daten[o + 1] + (255 - daten[o + 1]) * weiss + 0.5),
                            int(daten[o + 2] + (255 - daten[o + 2]) * weiss + 0.5), pa)
                return (daten[o], daten[o + 1], daten[o + 2], pa)
            self._fuellen(polys, gerade, shader=schnell)
            return

        if len(taps) == 1 and smooth:                                          # Schnellpfad: bilinear, eine Abtastung
            fa, fb = du * bw, dv * bh
            ox, oy = u0 * bw - 0.5 + taps[0][0], v0 * bh - 0.5 + taps[0][1]
            bw1, bh1 = bw - 1, bh - 1

            def bilinear(x, y):
                u = ia * x + ic * y + ie
                v = ib * x + id_ * y + if_
                u = 0.0 if u < 0.0 else 1.0 if u > 1.0 else u
                v = 0.0 if v < 0.0 else 1.0 if v > 1.0 else v
                fx, fy = u * fa + ox, v * fb + oy
                ix, iy = int(fx) if fx >= 0 else int(fx) - 1, int(fy) if fy >= 0 else int(fy) - 1
                wx, wy = fx - ix, fy - iy
                x0_, x1_ = (0 if ix < 0 else bw1 if ix > bw1 else ix), (0 if ix + 1 < 0 else bw1 if ix + 1 > bw1 else ix + 1)
                y0_, y1_ = (0 if iy < 0 else bh1 if iy > bh1 else iy) * bw, (0 if iy + 1 < 0 else bh1 if iy + 1 > bh1 else iy + 1) * bw
                r = g = b_ = al = 0.0
                for o, wgt in (((y0_ + x0_) * 4, (1 - wx) * (1 - wy)), ((y0_ + x1_) * 4, wx * (1 - wy)), ((y1_ + x0_) * 4, (1 - wx) * wy), ((y1_ + x1_) * 4, wx * wy)):
                    pa = daten[o + 3] * wgt
                    r += daten[o] * pa
                    g += daten[o + 1] * pa
                    b_ += daten[o + 2] * pa
                    al += pa
                if al <= 0:
                    return (0, 0, 0, 0)
                r, g, b_ = r / al, g / al, b_ / al
                if weiss:
                    r, g, b_ = r + (255 - r) * weiss, g + (255 - g) * weiss, b_ + (255 - b_) * weiss
                return (int(r + 0.5), int(g + 0.5), int(b_ + 0.5), int(al + 0.5))
            self._fuellen(polys, gerade, shader=bilinear)
            return

        def abtasten(x, y):
            u, v = _pt(inv, x, y)
            r = g = b_ = al = 0.0
            for tx, ty in taps:
                fx = (u0 + min(1.0, max(0.0, u)) * du) * bw - 0.5 + tx
                fy = (v0 + min(1.0, max(0.0, v)) * dv) * bh - 0.5 + ty
                if smooth and schritt < 1.6:
                    ix, iy = int(math.floor(fx)), int(math.floor(fy))
                    ax_, ay_ = fx - ix, fy - iy
                    for (qx, qy, wgt) in ((ix, iy, (1 - ax_) * (1 - ay_)), (ix + 1, iy, ax_ * (1 - ay_)), (ix, iy + 1, (1 - ax_) * ay_), (ix + 1, iy + 1, ax_ * ay_)):
                        o = (min(bh - 1, max(0, qy)) * bw + min(bw - 1, max(0, qx))) * 4
                        pa = daten[o + 3] * wgt
                        r += daten[o] * pa
                        g += daten[o + 1] * pa
                        b_ += daten[o + 2] * pa
                        al += pa
                else:
                    o = (min(bh - 1, max(0, int(fy + 0.5))) * bw + min(bw - 1, max(0, int(fx + 0.5)))) * 4
                    pa = daten[o + 3]
                    r += daten[o] * pa
                    g += daten[o + 1] * pa
                    b_ += daten[o + 2] * pa
                    al += pa
            if al <= 0:
                return (0, 0, 0, 0)
            n = len(taps)
            out = (r / al, g / al, b_ / al, al / n)
            if weiss:
                out = (out[0] + (255 - out[0]) * weiss, out[1] + (255 - out[1]) * weiss, out[2] + (255 - out[2]) * weiss, out[3])
            return (int(out[0] + 0.5), int(out[1] + 0.5), int(out[2] + 0.5), int(out[3] + 0.5))
        self._fuellen(polys, gerade, shader=abtasten)

    # ---- Bildeffekte ----
    def _massstab(self) -> float:
        return math.sqrt(abs(self._m[0] * self._m[3] - self._m[1] * self._m[2])) or 1.0

    def _bild_in_groesse(self, data: bytes, rect: Rect):
        sc = self._massstab()
        w, h = max(1, int(round(rect.width * sc))), max(1, int(round(rect.height * sc)))
        bild = self._bild(data, float(w))
        if bild is None or w * h > 6_000_000:
            return None
        return w, h, skaliert(bild[0], bild[1], bild[2], w, h)

    def _puffer_zeichnen(self, w: int, h: int, puffer, rect: Rect) -> None:
        quad = [(rect.x, rect.y), (rect.x + rect.width, rect.y), (rect.x + rect.width, rect.y + rect.height), (rect.x, rect.y + rect.height)]
        self._bild_fuellen(b"", rect, [[_pt(self._m, x, y) for x, y in quad]], True, True, 0.0, None, (w, h, puffer))

    def apply_image_effects(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> tuple[bytes, bool]:
        if effects.get("weich") or bild3d.braucht_nachbearbeitung(effects):
            g = self._bild_in_groesse(data, rect)
            if g is not None:
                w, h, pix = g
                sc = self._massstab()
                if effects.get("weich"):
                    pix = bildeffekte.weiche_kanten(pix, w, h, ellipse, float(effects["weich"].get("radius", 6.0)) * bildeffekte.PX_PT * sc)
                if bild3d.braucht_nachbearbeitung(effects):                    # oberer Abschluss und Drehung im Raum
                    pix, ellipse = bild3d.nachbearbeitet(pix, w, h, ellipse, effects, sc), False
                return bildeffekte.png_bytes(w, h, pix), ellipse
        return data, ellipse

    def draw_effects_behind(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> None:
        """Leuchten, Schatten und Spiegelung hinter dem Bild (in dieser Reihenfolge)."""
        if not (effects.get("leuchten") or effects.get("schatten") or effects.get("reflektion") or bild3d.hat_extrusion(effects)):
            return
        g = self._bild_in_groesse(data, rect)
        if g is None:
            return
        w, h, pix = g
        if bild3d.dreht(effects.get("drehung")):                                           # Schatten, Leuchten und Tiefe gehören zur gedrehten Form
            pix, ellipse = bild3d.gedreht(pix, w, h, ellipse, {**effects["drehung"], "text_gerade": False}), False
        sc = self._massstab()
        dreh = effects.get("drehung") or {}
        boden = max(0.0, float(dreh.get("boden", 0.0))) * bildeffekte.PX_PT

        def rgb(text, standard):
            try:
                return rgba(text or standard)[:3]
            except (ValueError, IndexError, TypeError):
                return rgba(standard)[:3]
        leu = effects.get("leuchten")
        if leu:
            rad = float(leu.get("groesse", 8.0)) * bildeffekte.PX_PT * sc
            W, H, puffer, pad = bildeffekte.schatten_bild(pix, w, h, ellipse, rgb(leu.get("farbe"), "#4472c4"), max(0.0, min(1.0, 1 - leu.get("transparenz", 60) / 100)),
                                                         rad * 0.9, 1.0 + 2 * rad / max(w, h))
            self._puffer_zeichnen(W, H, puffer, Rect(rect.x - pad / sc, rect.y - pad / sc, W / sc, H / sc))
        sch = effects.get("schatten")
        if sch:
            weich = float(sch.get("weich", 4.0)) * bildeffekte.PX_PT * sc
            W, H, puffer, pad = bildeffekte.schatten_bild(pix, w, h, ellipse, rgb(sch.get("farbe"), "#000000"), max(0.0, min(1.0, 1 - sch.get("transparenz", 60) / 100)),
                                                         weich, max(0.2, sch.get("groesse", 100) / 100.0))
            a = math.radians(float(sch.get("winkel", 45)))
            d = float(sch.get("abstand", 4.0)) * bildeffekte.PX_PT
            self._puffer_zeichnen(W, H, puffer, Rect(rect.x - pad / sc + math.cos(a) * d, rect.y - pad / sc + math.sin(a) * d + boden, W / sc, H / sc))
        if bild3d.hat_extrusion(effects):                                                  # 3D-Format: Tiefe, Kontur, unterer Abschluss
            W, H, puffer, pad = bild3d.extrusion(pix, w, h, ellipse, effects.get("d3") or {}, effects.get("drehung") or None, sc)
            self._puffer_zeichnen(W, H, puffer, Rect(rect.x - pad / sc, rect.y - pad / sc, W / sc, H / sc))
        refl = effects.get("reflektion")
        if refl:
            hoehe = max(1, int(h * refl.get("groesse", 50) / 100.0))
            W, H, puffer = bildeffekte.reflektion_bild(pix, w, h, ellipse, hoehe, max(0.0, min(1.0, 1 - refl.get("transparenz", 50) / 100)))
            self._puffer_zeichnen(W, H, puffer, Rect(rect.x, rect.y + rect.height + float(refl.get("abstand", 0.0)) * bildeffekte.PX_PT + boden, W / sc, H / sc))
