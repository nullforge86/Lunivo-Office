"""Bilder und dekorative Objekte im Dokumentenmodell, ohne Qt: Bildobjekt, Formobjekt, Vektorpfad, Füllung, Kontur, Schatten, Transformation, Verankerung, Textumfluss.

Jede Struktur ist ein ``dataclass`` mit ``zu_dict``/``aus_dict``. Das Wörterbuch ist das JSON-Format, in dem die Anwendung Bilder und Formen schon speichert
(frei positionierte Bilder: ``freie_bilder`` — Angaben an Absätzen und in ``PageSettings.bilder``; Formen: ``formen`` — Parameter am Bild). Unbekannte Schlüssel bleiben in ``extra``
erhalten, so verliert die Umwandlung nichts (``aus_dict(d).zu_dict() == d``). Maße in Bildpunkten bei 96 dpi, Winkel in Grad."""
from __future__ import annotations

from dataclasses import dataclass, field, replace

from lunivo_writer.core.document.bildformat import format_erkennen, masse


P_BILDANKER = "user:1048623"            # Absatzeigenschaft mit den frei positionierten Bildern (JSON-Liste); entspricht ``editor/dokument/zusatz.B_BILDANKER``


def _rest(d: dict, bekannt: set[str]) -> dict:
    return {k: v for k, v in d.items() if k not in bekannt}


@dataclass(frozen=True)
class Transform:
    """Drehung um die Mitte des Objekts und Spiegelung."""
    rotation: float = 0.0
    flip_h: bool = False
    flip_v: bool = False


@dataclass(frozen=True)
class Anchor:
    """Lage auf dem Blatt. Waagerecht: Bezug ``seite`` | ``rand`` | ``spalte``, Versatz ``x`` oder Ausrichtung ``left`` | ``center`` | ``right`` | ``inside`` | ``outside``.
    Senkrecht: Bezug ``seite`` | ``rand`` | ``absatz``, Versatz ``y`` oder Ausrichtung ``top`` | ``center`` | ``bottom``."""
    h_ref: str = "spalte"
    x: float = 0.0
    h_align: str = ""
    v_ref: str = "absatz"
    y: float = 0.0
    v_align: str = ""


@dataclass(frozen=True)
class WrapSettings:
    """Textumfluss: ``behind`` = hinter dem Text (sonst davor), ``mode`` = ``none`` (frei, ohne Umfluss) oder die Umbruchart des Fensters „Layout“; Abstände zum Text."""
    behind: bool = False
    mode: str = "none"
    distance: tuple[float, float, float, float] = (0.0, 0.0, 0.0, 0.0)             # oben, unten, links, rechts
    side: str = "beide"
    overlap: bool = True
    with_text: bool = False
    lock_anchor: bool = False


@dataclass(frozen=True)
class FillStyle:
    """Füllung: ``kind`` = ``farbe`` | ``verlauf`` | ``graduell`` | ``muster`` | ``textur`` | ``bild``; die Angaben der Art stehen in ``params``."""
    kind: str = "farbe"
    color: str = ""
    params: dict = field(default_factory=dict, hash=False, compare=True)

    @staticmethod
    def aus_dict(d: dict | None) -> "FillStyle | None":
        if not d:
            return None
        return FillStyle(str(d.get("art", "farbe")), str(d.get("farbe", "")), _rest(d, {"art", "farbe"}))

    def zu_dict(self) -> dict:
        return {"art": self.kind, "farbe": self.color, **self.params}


@dataclass(frozen=True)
class StrokeStyle:
    """Kontur: Farbe, Stärke, Linienart (``einfach``, ``gestrichelt`` …)."""
    color: str = "#ffffff"
    width: float = 1.0
    dash: str = "einfach"
    params: dict = field(default_factory=dict, hash=False, compare=True)

    @staticmethod
    def aus_dict(d: dict | None) -> "StrokeStyle | None":
        if not d:
            return None
        return StrokeStyle(str(d.get("farbe", "#ffffff")), float(d.get("b", 1.0)), str(d.get("art", "einfach")), _rest(d, {"farbe", "b", "art"}))

    def zu_dict(self) -> dict:
        return {"b": self.width, "farbe": self.color, "art": self.dash, **self.params}


@dataclass(frozen=True)
class Shadow:
    color: str = "#000000"
    blur: float = 4.0
    dx: float = 3.0
    dy: float = 3.0
    opacity: float = 0.4


@dataclass(frozen=True)
class VectorPath:
    """Pfad aus Anweisungen wie bei ``RenderBackend.draw_path``: ``("M", x, y)``, ``("L", x, y)``, ``("Q", cx, cy, x, y)``, ``("C", …)``, ``("Z",)``, ``("E", mx, my, rx, ry)``, ``("R", x, y, b, h)``."""
    ops: tuple[tuple, ...] = ()

    @staticmethod
    def polygon(punkte: list[tuple[float, float]]) -> "VectorPath":
        if not punkte:
            return VectorPath()
        return VectorPath((("M", *punkte[0]),) + tuple(("L", *p) for p in punkte[1:]) + (("Z",),))

    @staticmethod
    def rounded_rect(x: float, y: float, b: float, h: float, r: float) -> "VectorPath":
        r = max(0.0, min(r, b / 2, h / 2))
        if r == 0:
            return VectorPath((("R", x, y, b, h),))
        k = 0.5522847498 * r
        return VectorPath((("M", x + r, y), ("L", x + b - r, y), ("C", x + b - r + k, y, x + b, y + r - k, x + b, y + r), ("L", x + b, y + h - r),
                           ("C", x + b, y + h - r + k, x + b - r + k, y + h, x + b - r, y + h), ("L", x + r, y + h),
                           ("C", x + r - k, y + h, x, y + h - r + k, x, y + h - r), ("L", x, y + r), ("C", x, y + r - k, x + r - k, y, x + r, y), ("Z",)))

    @staticmethod
    def arrow(x0: float, y0: float, x1: float, y1: float, kopf: float = 10.0) -> "VectorPath":
        import math
        w = math.atan2(y1 - y0, x1 - x0)
        a = lambda d: (x1 - kopf * math.cos(w + d), y1 - kopf * math.sin(w + d))                      # noqa: E731
        (ax, ay), (bx, by) = a(0.45), a(-0.45)
        return VectorPath((("M", x0, y0), ("L", x1, y1), ("M", ax, ay), ("L", x1, y1), ("L", bx, by)))

    def zu_liste(self) -> list:
        return [list(o) for o in self.ops]

    @staticmethod
    def aus_liste(liste: list) -> "VectorPath":
        return VectorPath(tuple(tuple(o) for o in liste))


@dataclass
class ImageObject:
    """Ein Bild als Objekt: Bilddaten (Originalbytes) oder Platzhalter (fehlende Datei), Größe, Lage, Umfluss, Zuschnitt, Maske, Füllung, Kontur, Drehung, Beschriftung."""
    width: float
    height: float
    data: bytes | None = None                        # Originalbytes (PNG, JPEG, SVG …); None = fehlendes Bild (Platzhalter)
    anchor: Anchor = field(default_factory=Anchor)
    wrap: WrapSettings = field(default_factory=WrapSettings)
    transform: Transform = field(default_factory=Transform)
    ellipse: bool = False
    crop: object = None                              # Zuschnitt wie in ``bildzuschnitt`` gespeichert
    mask: str = ""
    fill: FillStyle | None = None
    stroke: StrokeStyle | None = None
    effects: dict | None = None
    opacity: float = 1.0
    alt_text: str = ""
    title: str = ""
    caption: str = ""
    name: str = ""
    extra: dict = field(default_factory=dict)

    @property
    def format(self) -> str | None:
        return format_erkennen(self.data) if self.data else None

    @property
    def placeholder(self) -> bool:
        return not self.data

    @property
    def pixel_size(self) -> tuple[float, float] | None:
        return masse(self.data) if self.data else None

    def scaled_to_width(self, b: float) -> "ImageObject":
        """Auf Breite ``b`` skaliert, Seitenverhältnis bleibt."""
        return replace(self, width=b, height=b * self.height / self.width if self.width else self.height)

    _BEKANNT = {"b", "h", "bh", "xh", "ah", "bv", "yv", "av", "hinter", "ellipse", "zu", "maske", "dreh", "flipH", "flipV", "rand", "fuell", "fx", "alt", "titel", "beschriftung", "n", "name"}

    @staticmethod
    def aus_angabe(a: dict, data: bytes | None = None) -> "ImageObject":
        """Aus der Angabe eines frei positionierten Bildes (``freie_bilder``)."""
        anker = Anchor(str(a.get("bh", "spalte")), float(a.get("xh", 0)), str(a.get("ah") or ""), str(a.get("bv", "absatz")), float(a.get("yv", 0)), str(a.get("av") or ""))
        umfluss = WrapSettings(behind=bool(a.get("hinter", False)), mode="none", overlap=bool(a.get("ueberlappen", True)), lock_anchor=bool(a.get("verankern", False)))
        return ImageObject(float(a.get("b", 0)), float(a.get("h", 0)), data, anker, umfluss,
                           Transform(float(a.get("dreh", 0.0)), bool(a.get("flipH", False)), bool(a.get("flipV", False))), bool(a.get("ellipse", False)),
                           a.get("zu"), str(a.get("maske") or ""), FillStyle.aus_dict(a.get("fuell")), StrokeStyle.aus_dict(a.get("rand")), a.get("fx"),
                           alt_text=str(a.get("alt", "")), title=str(a.get("titel", "")), caption=str(a.get("beschriftung", "")), name=str(a.get("n", a.get("name", ""))),
                           extra=_rest(a, ImageObject._BEKANNT))

    def zu_angabe(self) -> dict:
        """Die Angabe im Format von ``freie_bilder``; Schlüssel, die nicht gesetzt waren, bleiben weg."""
        d: dict = dict(self.extra)
        d.update({"b": self.width, "h": self.height, "bh": self.anchor.h_ref, "xh": self.anchor.x, "bv": self.anchor.v_ref, "yv": self.anchor.y})
        if self.anchor.h_align:
            d["ah"] = self.anchor.h_align
        if self.anchor.v_align:
            d["av"] = self.anchor.v_align
        if self.wrap.behind:
            d["hinter"] = True
        if self.ellipse:
            d["ellipse"] = True
        if self.crop is not None:
            d["zu"] = self.crop
        if self.mask:
            d["maske"] = self.mask
        if self.transform.rotation:
            d["dreh"] = self.transform.rotation
        if self.transform.flip_h:
            d["flipH"] = True
        if self.transform.flip_v:
            d["flipV"] = True
        if self.fill:
            d["fuell"] = self.fill.zu_dict()
        if self.stroke:
            d["rand"] = self.stroke.zu_dict()
        if self.effects:
            d["fx"] = self.effects
        for k, v in (("alt", self.alt_text), ("titel", self.title), ("beschriftung", self.caption), ("n", self.name)):
            if v:
                d[k] = v
        return d


@dataclass
class ShapeObject:
    """Eine Form: Art (``rechteck``, ``abgerundet``, ``ellipse``, ``linie``, ``pfeil``, ``vieleck``, ``freihand``, Katalogname), Größe, Füllung, Kontur, Text, Schatten, Pfad."""
    kind: str
    width: float
    height: float
    fill: FillStyle | None = None
    stroke: StrokeStyle | None = None
    text: str = ""
    adjust: tuple[float, ...] = ()
    path: VectorPath | None = None
    shadow: Shadow | None = None
    opacity: float = 1.0
    anchor: Anchor = field(default_factory=Anchor)
    wrap: WrapSettings = field(default_factory=WrapSettings)
    transform: Transform = field(default_factory=Transform)
    extra: dict = field(default_factory=dict)

    _BEKANNT = {"form", "breite", "hoehe", "fuell", "linie", "strich", "text", "adj", "fuell_art", "punkte"}

    @staticmethod
    def aus_parametern(d: dict) -> "ShapeObject":
        """Aus den Formparametern (``formen.STANDARD``: ``fuell`` Farbe, ``linie`` Farbe, ``strich`` Stärke)."""
        fuell = d.get("fuell") or ""
        pfad = None
        if d.get("punkte"):
            pfad = VectorPath.polygon([(float(p[0]), float(p[1])) for p in d["punkte"]])
        return ShapeObject(str(d.get("form", "rechteck")), float(d.get("breite", 0)), float(d.get("hoehe", 0)),
                           FillStyle(str(d.get("fuell_art") or "farbe"), fuell) if fuell else None,
                           StrokeStyle(str(d.get("linie", "#000000")), float(d.get("strich", 1.0))) if d.get("linie") else None,
                           str(d.get("text", "")), tuple(d.get("adj") or ()), pfad, extra=_rest(d, ShapeObject._BEKANNT) | ({"punkte": d["punkte"]} if d.get("punkte") else {}))

    def zu_parametern(self) -> dict:
        d: dict = dict(self.extra)
        d.update({"form": self.kind, "breite": self.width, "hoehe": self.height, "fuell": self.fill.color if self.fill else "",
                  "linie": self.stroke.color if self.stroke else "", "strich": self.stroke.width if self.stroke else 0.0, "text": self.text})
        if self.fill and self.fill.kind != "farbe":
            d["fuell_art"] = self.fill.kind
        if self.adjust:
            d["adj"] = list(self.adjust)
        return d


Objekt = ImageObject | ShapeObject
