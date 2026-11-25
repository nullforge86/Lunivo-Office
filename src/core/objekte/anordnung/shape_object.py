"""Shape object: aus ``core.objekte.anordnung.objekte`` herausgelöst."""
from __future__ import annotations
from dataclasses import dataclass, field
from core.objekte.anordnung.objekte_hilfen import Anchor, FillStyle, Shadow, StrokeStyle, Transform, VectorPath, WrapSettings, _rest


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
