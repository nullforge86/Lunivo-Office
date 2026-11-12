"""Die Schnittstelle des Zeichnens. Koordinaten in Bildpunkten (96 dpi), y nach unten. Jede Methode muss vom Backend umgesetzt werden."""
from __future__ import annotations

from dataclasses import dataclass

from lunivo_writer.core.geometry import Point, Rect


RGBA = tuple[int, int, int, int]


@dataclass(frozen=True)
class LinearGradient:
    """Linearer Farbverlauf von ``start`` nach ``end``; ``stops`` = ((Stelle 0…1, Farbe), …)."""
    start: Point
    end: Point
    stops: tuple[tuple[float, RGBA], ...]


@dataclass(frozen=True)
class RadialGradient:
    """Runder Farbverlauf um ``center`` mit ``radius``; ``stops`` wie beim linearen Verlauf."""
    center: Point
    radius: float
    stops: tuple[tuple[float, RGBA], ...]


@dataclass(frozen=True)
class PatternFill:
    """Muster (``key`` wie in der Mustergalerie) in ``color`` über der Grundfarbe ``ground``."""
    key: str
    color: str = "#000000"
    ground: str = "#ffffff"


@dataclass(frozen=True)
class TextureFill:
    """Eine der mitgelieferten Texturen (``papier``, ``granit``, ``holz``, ``stoff``, ``marmor``, ``sand``)."""
    key: str


@dataclass(frozen=True)
class ImageFill:
    """Ein Bild (Bytes einer Bilddatei), auf die Fläche gestreckt."""
    data: bytes


@dataclass(frozen=True)
class Style:
    """Linien- und Füllangaben: Farbe als (r, g, b, a), Strichstärke in Bildpunkten (0 = keine Linie), Füllung ja/nein, gestrichelt ja/nein."""
    color: tuple[int, int, int, int] = (0, 0, 0, 255)
    width: float = 1.0
    filled: bool = False
    dashed: bool = False
    dash: str | tuple[float, ...] | None = None              # Strichart: "dot", "dash", "dashdot", "dashdotdot" oder ein Muster (Strich, Lücke, …) in Linienbreiten
    cap: str = "square"                                       # Linienenden: "square" (Standard wie bei Qt), "flat" oder "round"
    join: str = "miter"                                       # Ecken der Linie: "miter", "round" oder "bevel"
    outline: RGBA | None = None                              # Linienfarbe, wenn sie von der Füllfarbe abweicht
    fill: LinearGradient | RadialGradient | PatternFill | TextureFill | ImageFill | None = None      # Verlauf als Füllung (gilt statt ``color``, wenn ``filled``)


def rgba(text: str, alpha: int = 255) -> RGBA:
    """Farbe aus ``#rrggbb`` oder ``#rrggbbaa`` (``#rgb`` auch); ``alpha`` gilt, wenn der Text keinen eigenen Alphawert hat."""
    t = text.lstrip("#")
    if len(t) == 3:
        t = "".join(c * 2 for c in t)
    return int(t[0:2], 16), int(t[2:4], 16), int(t[4:6], 16), int(t[6:8], 16) if len(t) >= 8 else alpha


class RenderBackend:
    def draw_text(self, text: str, position: Point, font, style: Style) -> None:
        raise NotImplementedError

    def draw_text_box(self, text: str, rect: Rect, font, style: Style, align: str = "left", wrap: bool = True, valign: str = "center") -> None:
        """Text in einem Rechteck: vertikal nach ``valign`` ("top", "center"), horizontal nach ``align`` ("left", "center", "right"), mit Zeilenumbruch bei ``wrap``."""
        raise NotImplementedError

    def text_bounds(self, text: str, rect: Rect, font, align: str = "left", wrap: bool = True) -> Rect:
        """Die Fläche, die ``draw_text_box`` mit denselben Angaben belegen würde."""
        raise NotImplementedError

    def draw_rect(self, rect: Rect, style: Style) -> None:
        raise NotImplementedError

    def push_state(self, opacity: float = 1.0, translate: Point | None = None, rotate: float = 0.0, clip: Rect | None = None,
                   antialias: bool | None = None, clip_ellipse: Rect | None = None) -> None:
        """Zeichenzustand sichern und ändern: Ausschnitt ``clip`` (Rechteck) oder ``clip_ellipse`` (Ellipse im Rechteck, im bisherigen Koordinatensystem), Kantenglättung, Deckkraft (mit der bisherigen multipliziert),
        dann Verschiebung, dann Drehung (Grad) um den neuen Ursprung."""
        raise NotImplementedError

    def pop_state(self) -> None:
        """Den mit ``push_state`` gesicherten Zustand wiederherstellen."""
        raise NotImplementedError

    def draw_image(self, data: bytes, rect: Rect, smooth: bool = False, wash: float = 0.0) -> None:
        """Bild aus den Bytes einer Bilddatei (PNG, JPEG, GIF, BMP, TIFF, WebP; SVG und EMF/WMF als Vektor) in ``rect``; ``wash`` 0…1: so weit zum Weiß hin ausgewaschen."""
        raise NotImplementedError

    def apply_image_effects(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> tuple[bytes, bool]:
        """Effekte, die das Bild selbst verändern (weiche Kanten, 3D-Format, 3D-Drehung): → (neue Bilddaten als PNG, ob die Ellipsenform noch gilt)."""
        raise NotImplementedError

    def draw_effects_behind(self, data: bytes, rect: Rect, ellipse: bool, effects: dict) -> None:
        """Leuchten, Schatten, Tiefe und Spiegelung hinter dem Bild."""
        raise NotImplementedError

    def draw_text_effects(self, text: str, font, origin: Point, color: RGBA, effects: dict | None, contour: dict | None, highlight: RGBA | None,
                          width: float, line_height: float, ascent: float, underline: bool = False) -> None:
        """Eine Textzeile mit Texteffekten (Schatten, Spiegelung, Leuchten, 3D, Kontur, Füllarten …): ``origin`` = Anfang der Grundlinie, ``width`` = Breite der Zeile,
        ``effects`` = Effekte (``editor/text/textfx.py``), ``contour`` = {"farbe", "breite", "stil"}, ``highlight`` = Farbe hinter der Zeile."""
        raise NotImplementedError

    def draw_shadow(self, ops: list, color: RGBA, blur: float, dx: float, dy: float) -> None:
        """Schatten eines Pfades: die Fläche in ``color`` (mit ihrem Alphawert), um (dx, dy) versetzt und mit Radius ``blur`` weichgezeichnet."""
        raise NotImplementedError

    def draw_path(self, ops: list, style: Style, antialias: bool | None = True, union: bool = False) -> None:
        """Linienzug oder Fläche aus Anweisungen: ``("M", x, y)``, ``("L", x, y)``, ``("Q", cx, cy, x, y)``, ``("C", x1, y1, x2, y2, x, y)``, ``("Z",)`` (Teilpfad schließen),
        ``("E", mx, my, rx, ry)`` (Ellipse) und ``("R", x, y, b, h)`` (Rechteck) als eigene Teilpfade. Gefüllt bei ``style.filled``; ``style.width`` 0 = ohne Linie.
        ``antialias=None``: die Einstellung des Zeichners bleibt. Mit ``union`` wird die Vereinigung aller Teilpfade gezeichnet (eine Außenlinie ohne innere Kanten)."""
        raise NotImplementedError

    def draw_ellipse(self, center: Point, rx: float, ry: float, style: Style) -> None:
        raise NotImplementedError

    def draw_line(self, start: Point, end: Point, style: Style) -> None:
        raise NotImplementedError
