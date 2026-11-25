"""Objekte hilfen: aus ``core.objekte.anordnung.objekte`` herausgelöst."""
from __future__ import annotations
from dataclasses import dataclass, field


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
