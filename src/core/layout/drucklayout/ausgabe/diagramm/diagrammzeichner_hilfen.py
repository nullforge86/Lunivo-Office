"""Diagrammzeichner hilfen: aus ``core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner`` herausgelöst."""
from __future__ import annotations
from core.geometrie import Rect
from core.textsatz.engine import FontSpec
from core.layout.drucklayout.ausgabe.backend import RenderTarget, Style, rgba
from core.layout.drucklayout.ausgabe.diagramm import diagrammformat as DF


_SCHRIFT = "Liberation Sans"


STILE = [("Standard", "#ffffff", "#3c4043", True), ("Ohne Raster", "#ffffff", "#3c4043", False), ("Hellgrau", "#f1f3f5", "#343a40", True), ("Dunkel", "#2b2d42", "#f1f3f5", True),
         ("Fetter Titel", "#ffffff", "#212529", True), ("Mit Datenbeschriftung", "#ffffff", "#3c4043", False), ("Mit Rahmen", "#ffffff", "#1f3864", True),
         ("Hellblau", "#e7f1fb", "#1c4f8c", True), ("Warm", "#fff4e6", "#7a3e00", True), ("Hellgrün", "#ebf7ee", "#1d4f28", False), ("Nachtblau", "#14213d", "#e5e5e5", True),
         ("Schwarz", "#000000", "#ffffff", False), ("Papier", "#fdf6e3", "#586e75", True), ("Hoher Kontrast", "#ffffff", "#000000", True)]


# ---- Daten vorbereiten ------------------------------------------------------------------------------------------------------
def _hell(c: tuple, f: float) -> tuple:
    return tuple(int(c[i] + (255 - c[i]) * f) for i in range(3)) + (c[3],)


def _dunkel(c: tuple, f: float) -> tuple:
    return tuple(int(c[i] * (1 - f)) for i in range(3)) + (c[3],)


def _farbe(text, standard=(0, 0, 0, 255)) -> tuple:
    try:
        return rgba(text)
    except (ValueError, IndexError, TypeError, AttributeError):
        return standard


def _reihenfarbe(v: dict, i: int, nr: int) -> tuple:
    fmt = (v["tf"].get(f"reihe_{nr}") or {}).get("fuell")
    if isinstance(fmt, dict) and fmt.get("farbe"):
        return _farbe(fmt["farbe"])
    return v["palette"][i % len(v["palette"])]


# ---- Zeichenkontext ------------------------------------------------------------------------------------------------------------
class _Z:
    def __init__(self, b: RenderTarget, v: dict, r: Rect, geo):
        self.b, self.v, self.r, self.geo = b, v, r, geo
        stil = STILE[v["stil"]]
        self.grund, self.text, self.raster_an = _farbe(stil[1]), _farbe(stil[2]), stil[3]
        self.raster = _farbe(v["ex"].get("raster_farbe") or ("#3a4a6b" if v["stil"] in (3, 10) else "#d9d9d9"))
        self.achse = _hell(self.text, 0.45) if sum(self.text[:3]) < 400 else _dunkel(self.text, 0.35)
        self.schrift = FontSpec(_SCHRIFT, 9.5)
        self.ts = Style(color=self.text)
        self.tf = v["tf"]
        self.engine = getattr(b, "engine", None)
        if self.engine is None:
            from core.layout.drucklayout.ausgabe.text.textpfad import gemeinsame_engine
            self.engine = gemeinsame_engine()
        self.hinweise: list = []

    def textformat(self, schluessel: str):
        return (self.tf.get(schluessel) or {}).get("text")

    def tx(self, schluessel: str, t: str, rect: Rect, ausr: str = "center", valign: str = "center", box=None, raender=None) -> Rect:
        """Text nach dem Textformat des Teils ``schluessel`` (Größe, Winkel, Ränder, Effekte); → das Feld um den Text."""
        return DF.text_zeichnen(self.b, self.engine, t, rect, self.textformat(schluessel), self.schrift, self.text, ausr, valign, raender, box, self.v.get("objekt_dreh", 0.0))

    def melden(self, text: str) -> None:
        if text not in self.hinweise:
            self.hinweise.append(text)
        if hasattr(self.b, "hinweise") and text not in self.b.hinweise:
            self.b.hinweise.append(text)

    def breite(self, t: str, f=None) -> float:
        return self.b.text_bounds(t, Rect(0, 0, 3000, 200), f or self.schrift, "left", False).width

    def text_(self, t: str, rect: Rect, ausr="center", valign="center", f=None, farbe=None) -> None:
        self.b.draw_text_box(t, rect, f or self.schrift, Style(color=farbe or self.text), ausr, False, valign)

    def teil(self, schluessel: str, rect: Rect) -> None:
        if self.geo is not None:
            self.geo[schluessel] = rect
