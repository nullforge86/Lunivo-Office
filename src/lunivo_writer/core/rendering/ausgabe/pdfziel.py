"""PDF-Zeichenfläche des Kerns: ein ``RenderBackend``, das Seiten direkt als PDF schreibt, ohne Qt und ohne weitere Bibliothek.

* Text steht als echter Text mit eingebetteter Schrift (Glyphen-IDs und Vorschübe aus HarfBuzz, Bruchgrößen der Engine); Schriften, die sich so nicht einbetten lassen
  (CFF, Sammlungen), werden als Glyphenpfade gezeichnet.
* Pfade, Rechtecke, Ellipsen, Linien, Strichmuster, Verläufe (Achsen- und Kreisverlauf), Ausschnitte, Deckkraft, Verschiebung, Drehung und Spiegelung sind PDF-Anweisungen.
* Bilder: PNG und JPEG werden eingebettet; was sich nicht lesen lässt, steht als Platzhalter im Bericht (``hinweise``).
Koordinaten wie im Kern: Bildpunkte bei 96 dpi, y nach unten; die Seite rechnet mit 0,75 in PDF-Punkte um."""
from __future__ import annotations

import hashlib
import math
import struct
import zlib

import uharfbuzz as hb

from lunivo_writer.core.geometrie import Point, Rect
from lunivo_writer.core.textsatz.engine import FontSpec
from .backend import ImageFill, LinearGradient, PatternFill, RadialGradient, RenderBackend, Style, TextureFill, rgba
from lunivo_writer.core.rendering.bild import bild3d, bildeffekte
from lunivo_writer.core.rendering.bild.bildeffekte import skaliert
from lunivo_writer.core.rendering.bild.bilddecoder import bild_dekodieren
from lunivo_writer.core.rendering.bild.fuellmuster import kachel_von
from lunivo_writer.core.rendering.text.textpfad import TextAusKern

_PT = 0.75                                                                   # Punkte je Bildpunkt
_KAPPA = 0.5522847498307936
_STRICH = {"dot": (1, 1), "dash": (4, 2), "dashdot": (4, 2, 1, 2), "dashdotdot": (4, 2, 1, 2, 1, 2)}


def _mal(m, a):
    """Matrix ``m`` nach ``a`` angewendet (zuerst ``a``, dann ``m``)."""
    return (m[0] * a[0] + m[2] * a[1], m[1] * a[0] + m[3] * a[1], m[0] * a[2] + m[2] * a[3], m[1] * a[2] + m[3] * a[3],
            m[0] * a[4] + m[2] * a[5] + m[4], m[1] * a[4] + m[3] * a[5] + m[5])


def _z(v: float) -> str:
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


def _hex_text(s: str) -> str:
    return "<FEFF" + s.encode("utf-16-be").hex().upper() + ">"


class _Bild:
    def __init__(self, nr: int, breite: int, hoehe: int):
        self.nr, self.breite, self.hoehe = nr, breite, hoehe


class _Schriftobjekt:
    def __init__(self, name: str, schrift, datei: bytes):
        self.name, self.schrift, self.datei = name, schrift, datei
        self.glyphen: dict[int, tuple[float, str]] = {}                       # Glyphe → (Vorschub in Schrifteinheiten, Text)
        self.nr = 0


class PdfZiel(TextAusKern, RenderBackend):
    glyphen_aus_kern = True                                                   # ``draw_text`` schreibt echten Text mit Schrift aus dem Kern, nichts Fremdes zeichnet Buchstaben

    def __init__(self, engine, titel: str = "", autor: str = ""):
        self.engine, self.titel, self.autor = engine, titel, autor
        self.hinweise: list[str] = []
        self._objekte: list[bytes | None] = [None]                            # Index = Objektnummer
        self._seiten: list[tuple[int, float, float]] = []                     # (Inhalt-Objekt, Breite pt, Höhe pt) mit Ressourcen unten
        self._seite_res: list[dict] = []
        self._inhalt: list[str] = []
        self._res: dict = {}
        self._stapel: list = []                                               # (Deckkraft, Matrix) der gesicherten Zustände
        self._deckkraft = 1.0
        self._m = (_PT, 0.0, 0.0, -_PT, 0.0, 0.0)                              # Benutzerkoordinaten → PDF-Punkte (für Kachelmuster)
        self._gs: dict[tuple[float, float], str] = {}
        self._bilder: dict[str, _Bild | None] = {}
        self._schriften: dict[tuple[str, int], _Schriftobjekt | None] = {}
        self._schaerfe = 0

    # ---- Seiten und Datei ----
    def neue_seite(self, breite_px: float, hoehe_px: float) -> None:
        self._seite_abschliessen()
        self._inhalt, self._stapel, self._deckkraft = [f"{_z(_PT)} 0 0 {_z(-_PT)} 0 {_z(hoehe_px * _PT)} cm"], [], 1.0
        self._res = {"Font": {}, "XObject": {}, "ExtGState": {}, "Pattern": {}}
        self._m = (_PT, 0.0, 0.0, -_PT, 0.0, hoehe_px * _PT)
        self._masse = (breite_px * _PT, hoehe_px * _PT)

    def _seite_abschliessen(self) -> None:
        if not self._inhalt:
            return
        while self._stapel:
            self.pop_state()
        daten = zlib.compress("\n".join(self._inhalt).encode("latin-1", "replace"))
        nr = self._neu(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(daten) + daten + b"\nendstream")
        self._seiten.append((nr, *self._masse))
        self._seite_res.append(self._res)
        self._inhalt = []

    def _neu(self, inhalt: bytes | None = None) -> int:
        self._objekte.append(inhalt)
        return len(self._objekte) - 1

    def als_bytes(self) -> bytes:
        self._seite_abschliessen()
        for f in self._schriften.values():
            if f is not None:
                self._schrift_schreiben(f)
        schriftnr = {f.name: f.nr for f in self._schriften.values() if f is not None}
        seitenbaum = self._neu()
        seiten_nr = []
        for (inhalt, b, h), res in zip(self._seiten, self._seite_res):
            teile = []
            if res["Font"]:
                teile.append("/Font << " + " ".join(f"/{k} {schriftnr[k]} 0 R" for k in res["Font"]) + " >>")
            if res["XObject"]:
                teile.append("/XObject << " + " ".join(f"/{k} {v} 0 R" for k, v in res["XObject"].items()) + " >>")
            if res["ExtGState"]:
                teile.append("/ExtGState << " + " ".join(f"/{k} << /ca {_z(c)} /CA {_z(s)} >>" for k, (c, s) in res["ExtGState"].items()) + " >>")
            if res.get("Pattern"):
                teile.append("/Pattern << " + " ".join(f"/{k} {v} 0 R" for k, v in res["Pattern"].items()) + " >>")
            if res.get("Shading"):
                teile.append("/Shading << " + " ".join(f"/{k} {v} 0 R" for k, v in res["Shading"].items()) + " >>")
            seiten_nr.append(self._neu(f"<< /Type /Page /Parent {seitenbaum} 0 R /MediaBox [0 0 {_z(b)} {_z(h)}] /Contents {inhalt} 0 R /Resources << {' '.join(teile)} >> >>".encode()))
        self._objekte[seitenbaum] = f"<< /Type /Pages /Count {len(seiten_nr)} /Kids [{' '.join(f'{n} 0 R' for n in seiten_nr)}] >>".encode()
        info = f"<< /Producer {_hex_text('Lunivo Writer')} /Creator {_hex_text(self.autor or 'Lunivo Writer')}"
        if self.titel:
            info += f" /Title {_hex_text(self.titel)}"
        if self.autor:
            info += f" /Author {_hex_text(self.autor)}"
        info_nr = self._neu((info + " >>").encode())
        wurzel = self._neu(f"<< /Type /Catalog /Pages {seitenbaum} 0 R >>".encode())
        aus, stellen = bytearray(b"%PDF-1.5\n%\xe2\xe3\xcf\xd3\n"), [0]
        for nr in range(1, len(self._objekte)):
            stellen.append(len(aus))
            aus += b"%d 0 obj\n" % nr + (self._objekte[nr] or b"null") + b"\nendobj\n"
        start = len(aus)
        aus += b"xref\n0 %d\n0000000000 65535 f \n" % len(self._objekte)
        for s in stellen[1:]:
            aus += b"%010d 00000 n \n" % s
        aus += b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n" % (len(self._objekte), wurzel, info_nr, start)
        return bytes(aus)

    def speichern(self, pfad: str) -> None:
        with open(pfad, "wb") as f:
            f.write(self.als_bytes())

    # ---- Zustand ----
    def push_state(self, opacity: float = 1.0, translate: Point | None = None, rotate: float = 0.0, clip: Rect | None = None,
                   antialias: bool | None = None, clip_ellipse: Rect | None = None, flip_h: bool = False, flip_v: bool = False) -> None:
        a = self._inhalt.append
        a("q")
        self._stapel.append((self._deckkraft, self._m))
        if clip is not None:
            a(f"{_z(clip.x)} {_z(clip.y)} {_z(clip.width)} {_z(clip.height)} re W n")
        if clip_ellipse is not None:
            a(self._ellipse(clip_ellipse.x + clip_ellipse.width / 2, clip_ellipse.y + clip_ellipse.height / 2, clip_ellipse.width / 2, clip_ellipse.height / 2) + " W n")
        self._deckkraft *= max(0.0, min(1.0, opacity))
        if translate is not None:
            a(f"1 0 0 1 {_z(translate.x)} {_z(translate.y)} cm")
            self._m = _mal(self._m, (1.0, 0.0, 0.0, 1.0, translate.x, translate.y))
        if rotate:
            c, s = math.cos(math.radians(rotate)), math.sin(math.radians(rotate))
            a(f"{_z(c)} {_z(s)} {_z(-s)} {_z(c)} 0 0 cm")
            self._m = _mal(self._m, (c, s, -s, c, 0.0, 0.0))
        if flip_h or flip_v:
            a(f"{-1 if flip_h else 1} 0 0 {-1 if flip_v else 1} 0 0 cm")
            self._m = _mal(self._m, (-1.0 if flip_h else 1.0, 0.0, 0.0, -1.0 if flip_v else 1.0, 0.0, 0.0))

    def pop_state(self) -> None:
        if self._stapel:
            self._inhalt.append("Q")
            self._deckkraft, self._m = self._stapel.pop()

    # ---- Farbe und Deckkraft ----
    def _gs_name(self, ca: float, cs: float) -> str:
        schluessel = (round(ca, 3), round(cs, 3))
        name = self._gs.get(schluessel)
        if name is None:
            name = f"G{len(self._gs)}"
            self._gs[schluessel] = name
        self._res["ExtGState"][name] = schluessel
        return name

    @staticmethod
    def _farbe(c) -> str:
        return f"{_z(c[0] / 255)} {_z(c[1] / 255)} {_z(c[2] / 255)}"

    def _paint(self, pfad: str, style: Style) -> None:
        """Pfad (PDF-Anweisungen) nach ``style`` füllen und/oder umranden."""
        fuell, linie = bool(style.filled), style.width > 0
        if not fuell and not linie:
            return
        a = self._inhalt.append
        fa = self._deckkraft * (style.color[3] / 255 if style.color is not None else 1.0)
        lc = style.outline or style.color
        la = self._deckkraft * lc[3] / 255
        verlauf = fuell and isinstance(style.fill, (LinearGradient, RadialGradient))
        bildfuellung = fuell and isinstance(style.fill, ImageFill)
        kachel = fuell and isinstance(style.fill, (PatternFill, TextureFill))
        if verlauf:
            a("q")
            a(pfad + " W n")
            self._verlauf(style.fill)
            a("Q")
            fuell = False
        elif bildfuellung:
            a("q")
            a(pfad + " W n")
            x0, y0, x1, y1 = self._schranken(pfad)
            self.draw_image(style.fill.data, Rect(x0, y0, x1 - x0, y1 - y0))
            a("Q")
            fuell = False
        if not fuell and not linie:
            return
        a("q")
        a(f"/{self._gs_name(fa, la)} gs")
        if kachel:
            a(f"/Pattern cs /{self._kachelmuster(style.fill)} scn")
        elif fuell:
            a(self._farbe(style.color) + " rg")
        if linie:
            a(self._farbe(lc) + " RG")
            a(f"{_z(style.width)} w {({'flat': 0, 'round': 1}.get(style.cap, 2))} J {({'round': 1, 'bevel': 2}.get(style.join, 0))} j")
            muster = _STRICH.get(style.dash) if isinstance(style.dash, str) else (style.dash if isinstance(style.dash, tuple) else (_STRICH["dash"] if style.dashed else None))
            if muster:
                a("[" + " ".join(_z(m * style.width) for m in muster) + "] 0 d")
        a(pfad + (" B*" if fuell and linie else " f*" if fuell else " S"))
        a("Q")

    @staticmethod
    def _schranken(pfad: str) -> tuple[float, float, float, float]:
        zahlen = []
        for t in pfad.split():
            try:
                zahlen.append(float(t))
            except ValueError:
                pass
        xs, ys = zahlen[0::2] or [0.0], zahlen[1::2] or [0.0]
        return min(xs), min(ys), max(xs), max(ys)

    def _verlauf(self, f) -> None:
        stops = sorted(f.stops, key=lambda s: s[0]) or [(0.0, (0, 0, 0, 255)), (1.0, (255, 255, 255, 255))]
        if stops[0][0] > 0:
            stops = [(0.0, stops[0][1])] + stops
        if stops[-1][0] < 1:
            stops = stops + [(1.0, stops[-1][1])]
        funktionen, grenzen = [], []
        for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
            funktionen.append(f"<< /FunctionType 2 /Domain [0 1] /C0 [{self._farbe(c0)}] /C1 [{self._farbe(c1)}] /N 1 >>")
            grenzen.append(_z(p1))
        fn = f"<< /FunctionType 3 /Domain [0 1] /Functions [{' '.join(funktionen)}] /Bounds [{' '.join(grenzen[:-1])}] /Encode [{' '.join(['0 1'] * len(funktionen))}] >>"
        if isinstance(f, LinearGradient):
            sh = f"<< /ShadingType 2 /ColorSpace /DeviceRGB /Coords [{_z(f.start.x)} {_z(f.start.y)} {_z(f.end.x)} {_z(f.end.y)}] /Function {fn} /Extend [true true] >>"
        else:
            sh = f"<< /ShadingType 3 /ColorSpace /DeviceRGB /Coords [{_z(f.center.x)} {_z(f.center.y)} 0 {_z(f.center.x)} {_z(f.center.y)} {_z(f.radius)}] /Function {fn} /Extend [true true] >>"
        nr = self._neu(sh.encode())
        name = f"S{nr}"
        self._res.setdefault("Shading", {})[name] = nr
        self._inhalt.append(f"/{name} sh")

    # ---- Muster und Texturen ----
    def _kachelmuster(self, fuellung) -> str:
        """Ein Kachelmuster (PDF ``PatternType 1``) mit der Kachel der Füllung, verankert im Benutzerkoordinatensystem; → Name in den Seitenressourcen."""
        tw, th, kachel = kachel_von(fuellung)
        zeilen = []
        for y in range(th):
            x = 0
            while x < tw:
                c = kachel[y * tw + x]
                n = 1
                while x + n < tw and kachel[y * tw + x + n] == c:
                    n += 1
                if c[3] > 0:
                    zeilen.append(f"/{self._gs_name(c[3] / 255.0, c[3] / 255.0)} gs {self._farbe(c)} rg {x} {y} {n} 1 re f" if c[3] < 255 else f"{self._farbe(c)} rg {x} {y} {n} 1 re f")
                x += n
            if y == th - 1:
                break
        daten = zlib.compress("\n".join(zeilen).encode("latin-1"))
        gs = {name: (ca, ca) for (ca, _cs), name in self._gs.items()}
        res = "/ExtGState << " + " ".join(f"/{n} << /ca {_z(c[0])} /CA {_z(c[1])} >>" for n, c in gs.items()) + " >>" if gs else ""
        nr = self._neu(f"<< /Type /Pattern /PatternType 1 /PaintType 1 /TilingType 1 /BBox [0 0 {tw} {th}] /XStep {tw} /YStep {th} /Resources << {res} >> "
                       f"/Matrix [{' '.join(_z(v) for v in self._m)}] /Filter /FlateDecode /Length {len(daten)} >>\nstream\n".encode() + daten + b"\nendstream")
        name = f"P{nr}"
        self._res["Pattern"][name] = nr
        return name

    # ---- Pfade ----
    @staticmethod
    def _ellipse(cx: float, cy: float, rx: float, ry: float) -> str:
        kx, ky = rx * _KAPPA, ry * _KAPPA
        return (f"{_z(cx + rx)} {_z(cy)} m {_z(cx + rx)} {_z(cy + ky)} {_z(cx + kx)} {_z(cy + ry)} {_z(cx)} {_z(cy + ry)} c "
                f"{_z(cx - kx)} {_z(cy + ry)} {_z(cx - rx)} {_z(cy + ky)} {_z(cx - rx)} {_z(cy)} c "
                f"{_z(cx - rx)} {_z(cy - ky)} {_z(cx - kx)} {_z(cy - ry)} {_z(cx)} {_z(cy - ry)} c "
                f"{_z(cx + kx)} {_z(cy - ry)} {_z(cx + rx)} {_z(cy - ky)} {_z(cx + rx)} {_z(cy)} c h")

    def _ops(self, ops: list) -> str:
        teile, ax, ay = [], 0.0, 0.0
        for op in ops:
            k = op[0]
            if k == "M":
                teile.append(f"{_z(op[1])} {_z(op[2])} m")
                ax, ay = op[1], op[2]
            elif k == "L":
                teile.append(f"{_z(op[1])} {_z(op[2])} l")
                ax, ay = op[1], op[2]
            elif k == "Q":                                                    # quadratisch → kubisch
                c1x, c1y = ax + 2 / 3 * (op[1] - ax), ay + 2 / 3 * (op[2] - ay)
                c2x, c2y = op[3] + 2 / 3 * (op[1] - op[3]), op[4] + 2 / 3 * (op[2] - op[4])
                teile.append(f"{_z(c1x)} {_z(c1y)} {_z(c2x)} {_z(c2y)} {_z(op[3])} {_z(op[4])} c")
                ax, ay = op[3], op[4]
            elif k == "C":
                teile.append(" ".join(_z(v) for v in op[1:7]) + " c")
                ax, ay = op[5], op[6]
            elif k == "Z":
                teile.append("h")
            elif k == "E":
                teile.append(self._ellipse(op[1], op[2], op[3], op[4]))
            elif k == "R":
                teile.append(f"{_z(op[1])} {_z(op[2])} {_z(op[3])} {_z(op[4])} re")
        return " ".join(teile)

    def draw_path(self, ops: list, style: Style, antialias: bool | None = True, union: bool = False) -> None:
        if ops:
            self._paint(self._ops(ops), style)

    def draw_rect(self, rect: Rect, style: Style) -> None:
        self._paint(f"{_z(rect.x)} {_z(rect.y)} {_z(rect.width)} {_z(rect.height)} re", style)

    def draw_ellipse(self, center: Point, rx: float, ry: float, style: Style) -> None:
        self._paint(self._ellipse(center.x, center.y, rx, ry), style)

    def draw_line(self, start: Point, end: Point, style: Style) -> None:
        self._paint(f"{_z(start.x)} {_z(start.y)} m {_z(end.x)} {_z(end.y)} l", Style(color=style.color, width=style.width, filled=False, dashed=style.dashed, dash=style.dash,
                                                                                    cap=style.cap, join=style.join, outline=style.outline))

    def draw_shadow(self, ops: list, color: tuple, blur: float, dx: float, dy: float) -> None:
        """Schatten: PDF kennt keinen Weichzeichner; die Kante wird aus mehreren, nach außen wachsenden und schwächer werdenden Schichten gestuft."""
        self._inhalt.append(f"q 1 0 0 1 {_z(dx)} {_z(dy)} cm")
        schichten = 1 if blur < 1.0 else min(10, max(3, int(blur)))
        a = color[3] / schichten if schichten > 1 else color[3]
        for k in range(schichten):
            ausdehnung = blur * (schichten - 1 - k) / max(1, schichten - 1) if schichten > 1 else 0.0
            self.draw_path(ops, Style(color=(color[0], color[1], color[2], max(1, int(a * (1.6 if schichten > 1 else 1.0)))), width=2 * ausdehnung, filled=True, join="round", cap="round",
                                      outline=(color[0], color[1], color[2], max(1, int(a * 1.6)))))
        self._inhalt.append("Q")

    # ---- Text ----
    def _schriftobjekt(self, font: FontSpec) -> _Schriftobjekt | None:
        schnitt = self.engine.schnitt_von(font)
        schluessel = (schnitt.pfad, schnitt.index)
        if schluessel not in self._schriften:
            obj = None
            try:
                with open(schnitt.pfad, "rb") as f:
                    daten = f.read()
                if daten[:4] in (b"\x00\x01\x00\x00", b"true"):
                    obj = _Schriftobjekt(f"F{len(self._schriften)}", self.engine.schrift_von(font), daten)
            except OSError:
                obj = None
            self._schriften[schluessel] = obj
        return self._schriften[schluessel]

    def draw_text(self, text: str, position: Point, font, style: Style) -> None:
        if not text or not isinstance(font, FontSpec):
            return
        so = self._schriftobjekt(font)
        s = self.engine.schrift_von(font)
        if so is None:                                                        # nicht einbettbar: Glyphenpfade
            self.draw_path(self.engine.glyphen_pfad(text, font, position.x, position.y), Style(color=style.color, width=0, filled=True))
            return
        buf = hb.Buffer()
        buf.add_str(text)
        buf.guess_segment_properties()
        hb.shape(s.hb_font, buf, {"kern": True, "liga": True})
        infos, pos = buf.glyph_infos, buf.glyph_positions
        stuecke, vorher = [], 0
        for i, (info, p) in enumerate(zip(infos, pos)):
            gid = info.codepoint
            nominal = s.hb_font.get_glyph_h_advance(gid)
            if gid not in so.glyphen:
                naechst = next((infos[j].cluster for j in range(i + 1, len(infos)) if infos[j].cluster != info.cluster), len(text))
                so.glyphen[gid] = (nominal, text[info.cluster:naechst])
            stuecke.append(f"<{gid:04X}>")
            stuecke.append(_z((nominal - p.x_advance) * 1000.0 / s.upem))
        self._res["Font"][so.name] = None                                     # die Objektnummer trägt ``als_bytes`` ein, wenn die Schrift geschrieben ist
        fa = self._deckkraft * style.color[3] / 255
        a = self._inhalt.append
        a("q")
        a(f"/{self._gs_name(fa, fa)} gs {self._farbe(style.color)} rg")
        a(f"BT /{so.name} {_z(s.px)} Tf 1 0 0 -1 {_z(position.x)} {_z(position.y)} Tm [{' '.join(stuecke)}] TJ ET")
        a("Q")

    def _schrift_schreiben(self, f: _Schriftobjekt) -> None:
        s = f.schrift
        upem = s.upem or 1000
        fd = zlib.compress(f.datei)
        datei = self._neu(b"<< /Length %d /Length1 %d /Filter /FlateDecode >>\nstream\n" % (len(fd), len(f.datei)) + fd + b"\nendstream")
        face = s.ft_face
        bb = face.bbox if face is not None else None
        name = "".join(ch for ch in (face.postscript_name.decode("latin-1") if face is not None and face.postscript_name else "Schrift") if ch.isalnum() or ch in "-_") or "Schrift"
        box = f"[{_z(bb.xMin * 1000 / upem)} {_z(bb.yMin * 1000 / upem)} {_z(bb.xMax * 1000 / upem)} {_z(bb.yMax * 1000 / upem)}]" if bb is not None else "[-200 -300 1200 1000]"
        beschr = self._neu(f"<< /Type /FontDescriptor /FontName /{name} /Flags 32 /FontBBox {box} /ItalicAngle 0 /Ascent {_z(s.ascent / s.px * 1000)} /Descent {_z(-s.descent / s.px * 1000)} "
                           f"/CapHeight {_z(s.ascent / s.px * 700)} /StemV 80 /FontFile2 {datei} 0 R >>".encode())
        breiten = " ".join(f"{g} [{_z(w * 1000.0 / upem)}]" for g, (w, _t) in sorted(f.glyphen.items()))
        cid = self._neu(f"<< /Type /Font /Subtype /CIDFontType2 /BaseFont /{name} /CIDSystemInfo << /Registry (Adobe) /Ordering (Identity) /Supplement 0 >> /FontDescriptor {beschr} 0 R "
                        f"/CIDToGIDMap /Identity /DW 1000 /W [{breiten}] >>".encode())
        zeilen = [f"<{g:04X}> <{t.encode('utf-16-be').hex().upper()}>" for g, (_w, t) in sorted(f.glyphen.items()) if t]
        cmap = ("/CIDInit /ProcSet findresource begin 12 dict begin begincmap /CMapName /Adobe-Identity-UCS def /CMapType 2 def 1 begincodespacerange <0000> <FFFF> endcodespacerange\n"
                + "".join(f"{len(zeilen[i:i + 100])} beginbfchar\n" + "\n".join(zeilen[i:i + 100]) + "\nendbfchar\n" for i in range(0, len(zeilen), 100)) + "endcmap CMapName currentdict /CMap defineresource pop end end").encode()
        cd = zlib.compress(cmap)
        tounicode = self._neu(b"<< /Length %d /Filter /FlateDecode >>\nstream\n" % len(cd) + cd + b"\nendstream")
        f.nr = self._neu(f"<< /Type /Font /Subtype /Type0 /BaseFont /{name} /Encoding /Identity-H /DescendantFonts [{cid} 0 R] /ToUnicode {tounicode} 0 R >>".encode())

    # ---- Bilder ----
    def _xobjekt_rgba(self, w: int, h: int, puffer) -> _Bild:
        """Ein RGBA-Puffer als Bild-XObject (Farbe flach, Alpha als weiche Maske)."""
        rgb = bytearray(w * h * 3)
        rgb[0::3], rgb[1::3], rgb[2::3] = puffer[0::4], puffer[1::4], puffer[2::4]
        alpha = bytes(puffer[3::4])
        maske = ""
        if alpha.count(255) != len(alpha):
            ac = zlib.compress(alpha)
            nr_m = self._neu(f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode /Length {len(ac)} >>\nstream\n".encode() + ac + b"\nendstream")
            maske = f"/SMask {nr_m} 0 R "
        fc = zlib.compress(bytes(rgb))
        nr = self._neu(f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceRGB /BitsPerComponent 8 {maske}/Filter /FlateDecode /Length {len(fc)} >>\nstream\n".encode()
                       + fc + b"\nendstream")
        return _Bild(nr, w, h)

    def _puffer_zeichnen(self, w: int, h: int, puffer, rect: Rect) -> None:
        bild = self._xobjekt_rgba(w, h, puffer)
        name = f"I{bild.nr}"
        self._res["XObject"][name] = bild.nr
        a = self._inhalt.append
        a("q")
        if self._deckkraft < 1.0:
            a(f"/{self._gs_name(self._deckkraft, self._deckkraft)} gs")
        a(f"{_z(rect.width)} 0 0 {_z(-rect.height)} {_z(rect.x)} {_z(rect.y + rect.height)} cm /{name} Do")
        a("Q")

    _EFFEKTAUFLOESUNG = 1.5                                                    # Pixel je Bildpunkt der Effektbilder

    def _bild_in_groesse(self, data: bytes, rect: Rect):
        sc = self._EFFEKTAUFLOESUNG
        w, h = max(1, int(round(rect.width * sc))), max(1, int(round(rect.height * sc)))
        bild = bild_dekodieren(data, float(w))
        if bild is None or w * h > 4_000_000:
            return None
        return w, h, skaliert(bild[0], bild[1], bild[2], w, h)

    def apply_image_effects(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> tuple[bytes, bool]:
        if effects.get("weich") or bild3d.braucht_nachbearbeitung(effects):
            g = self._bild_in_groesse(data, rect)
            if g is not None:
                w, h, pix = g
                sc = self._EFFEKTAUFLOESUNG
                if effects.get("weich"):
                    pix = bildeffekte.weiche_kanten(pix, w, h, ellipse, float(effects["weich"].get("radius", 6.0)) * bildeffekte.PX_PT * sc)
                if bild3d.braucht_nachbearbeitung(effects):                    # oberer Abschluss und Drehung im Raum
                    pix, ellipse = bild3d.nachbearbeitet(pix, w, h, ellipse, effects, sc), False
                return bildeffekte.png_bytes(w, h, pix), ellipse
        return data, ellipse

    def draw_effects_behind(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> None:
        """Leuchten, Schatten und Spiegelung hinter dem Bild: dieselben Puffer wie im Rasterer, als Bilder mit Alpha eingebettet."""
        if not (effects.get("leuchten") or effects.get("schatten") or effects.get("reflektion") or bild3d.hat_extrusion(effects)):
            return
        g = self._bild_in_groesse(data, rect)
        if g is None:
            return
        w, h, pix = g
        if bild3d.dreht(effects.get("drehung")):                                           # Schatten, Leuchten und Tiefe gehören zur gedrehten Form
            pix, ellipse = bild3d.gedreht(pix, w, h, ellipse, {**effects["drehung"], "text_gerade": False}), False
        sc = self._EFFEKTAUFLOESUNG
        boden = max(0.0, float((effects.get("drehung") or {}).get("boden", 0.0))) * bildeffekte.PX_PT

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

    def draw_image(self, data: bytes, rect: Rect, smooth: bool = False, wash: float = 0.0, source_rect: Rect | None = None) -> None:
        schluessel = hashlib.sha1(data).hexdigest()
        if schluessel not in self._bilder:
            self._bilder[schluessel] = self._bild_lesen(data)
        bild = self._bilder[schluessel]
        a = self._inhalt.append
        if bild is None:
            self.hinweise.append("Ein Bild in einem Format, das der PDF-Ausgabe nicht bekannt ist (nur PNG und JPEG), steht als Platzhalter.")
            self.draw_rect(rect, Style(color=(232, 232, 236, 255), width=0, filled=True))
            self.draw_rect(rect, Style(color=(150, 150, 156, 255), width=1.0))
            return
        name = f"I{bild.nr}"
        self._res["XObject"][name] = bild.nr
        x, y, w, h = rect.x, rect.y, rect.width, rect.height
        a("q")
        if source_rect is not None and source_rect.width > 0 and source_rect.height > 0:
            a(f"{_z(x)} {_z(y)} {_z(w)} {_z(h)} re W n")
            x, y, w, h = x - source_rect.x * w / source_rect.width, y - source_rect.y * h / source_rect.height, w / source_rect.width, h / source_rect.height
        fa = self._deckkraft
        if fa < 1.0:
            a(f"/{self._gs_name(fa, fa)} gs")
        a(f"{_z(w)} 0 0 {_z(-h)} {_z(x)} {_z(y + h)} cm /{name} Do")
        a("Q")
        if wash > 0:
            self.draw_rect(rect, Style(color=(255, 255, 255, int(255 * min(1.0, wash))), width=0, filled=True))

    def _bild_lesen(self, daten: bytes) -> _Bild | None:
        try:
            erg = self._png(daten) if daten[:8] == b"\x89PNG\r\n\x1a\n" else self._jpeg(daten) if daten[:2] == b"\xff\xd8" else None
            if erg is not None:
                return erg
        except Exception:
            pass
        erg = bild_dekodieren(daten, None)                                      # alle anderen Formate (GIF, BMP, WebP, TIFF, PNG mit Zeilensprung …) über den Decoder des Kerns
        return self._xobjekt_rgba(erg[0], erg[1], erg[2]) if erg is not None else None

    def _jpeg(self, d: bytes) -> _Bild | None:
        i, adobe = 2, False
        while i + 4 < len(d):
            if d[i] != 0xFF:
                i += 1
                continue
            m, n = d[i + 1], struct.unpack(">H", d[i + 2:i + 4])[0]
            if m == 0xEE and d[i + 4:i + 9] == b"Adobe":
                adobe = True
            if m in (0xC0, 0xC1, 0xC2):
                _p, h, w, komp = struct.unpack(">BHHB", d[i + 4:i + 10])
                raum = {1: "/DeviceGray", 3: "/DeviceRGB", 4: "/DeviceCMYK"}.get(komp)
                if raum is None:
                    return None
                dec = " /Decode [1 0 1 0 1 0 1 0]" if komp == 4 and adobe else ""
                nr = self._neu(f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace {raum} /BitsPerComponent 8 /Filter /DCTDecode{dec} /Length {len(d)} >>\nstream\n".encode() + d + b"\nendstream")
                return _Bild(nr, w, h)
            i += 2 + n
        return None

    def _png(self, d: bytes) -> _Bild | None:
        stellen, idat, plte, i = {}, b"", b"", 8
        while i < len(d):
            n, art = struct.unpack(">I4s", d[i:i + 8])
            teil = d[i + 8:i + 8 + n]
            if art == b"IHDR":
                stellen["h"] = teil
            elif art == b"IDAT":
                idat += teil
            elif art == b"PLTE":
                plte = teil
            i += 12 + n
        w, h, tiefe, ct, _k, _f, interlace = struct.unpack(">IIBBBBB", stellen["h"])
        if interlace:
            return None
        if ct in (0, 2, 3):                                                   # ohne Alpha: die Daten gehen mit PNG-Vorhersage unverändert in das PDF
            farben = {0: 1, 2: 3, 3: 1}[ct]
            raum = {0: "/DeviceGray", 2: "/DeviceRGB", 3: f"[/Indexed /DeviceRGB {len(plte) // 3 - 1} <{plte.hex()}>]"}[ct]
            nr = self._neu(f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace {raum} /BitsPerComponent {tiefe} /Filter /FlateDecode "
                           f"/DecodeParms << /Predictor 15 /Colors {farben} /BitsPerComponent {tiefe} /Columns {w} >> /Length {len(idat)} >>\nstream\n".encode() + idat + b"\nendstream")
            return _Bild(nr, w, h)
        if tiefe != 8 or ct not in (4, 6):
            return None
        bpp = 2 if ct == 4 else 4
        roh = _entfiltern(zlib.decompress(idat), w, bpp, h)
        farbe, alpha = bytearray(), bytearray()
        for y in range(h):
            z = roh[y * w * bpp:(y + 1) * w * bpp]
            if ct == 6:
                zeile = bytearray(w * 3)
                zeile[0::3], zeile[1::3], zeile[2::3] = z[0::4], z[1::4], z[2::4]
                farbe += zeile
                alpha += z[3::4]
            else:
                farbe += z[0::2]
                alpha += z[1::2]
        ac = zlib.compress(bytes(alpha))
        maske = self._neu(f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace /DeviceGray /BitsPerComponent 8 /Filter /FlateDecode /Length {len(ac)} >>\nstream\n".encode() + ac + b"\nendstream")
        fc = zlib.compress(bytes(farbe))
        nr = self._neu(f"<< /Type /XObject /Subtype /Image /Width {w} /Height {h} /ColorSpace {'/DeviceRGB' if ct == 6 else '/DeviceGray'} /BitsPerComponent 8 /SMask {maske} 0 R "
                       f"/Filter /FlateDecode /Length {len(fc)} >>\nstream\n".encode() + fc + b"\nendstream")
        return _Bild(nr, w, h)


def _entfiltern(roh: bytes, w: int, bpp: int, h: int) -> bytearray:
    """PNG-Zeilenfilter rückgängig machen (8 Bit je Kanal)."""
    breite = w * bpp
    aus, vorige = bytearray(), bytearray(breite)
    for y in range(h):
        f = roh[y * (breite + 1)]
        z = bytearray(roh[y * (breite + 1) + 1:(y + 1) * (breite + 1)])
        if f == 1:
            for i in range(bpp, breite):
                z[i] = (z[i] + z[i - bpp]) & 255
        elif f == 2:
            z = bytearray((a + b) & 255 for a, b in zip(z, vorige))
        elif f == 3:
            for i in range(breite):
                z[i] = (z[i] + (((z[i - bpp] if i >= bpp else 0) + vorige[i]) >> 1)) & 255
        elif f == 4:
            for i in range(breite):
                a, b, c = (z[i - bpp] if i >= bpp else 0), vorige[i], (vorige[i - bpp] if i >= bpp else 0)
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                z[i] = (z[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        aus += z
        vorige = z
    return aus
