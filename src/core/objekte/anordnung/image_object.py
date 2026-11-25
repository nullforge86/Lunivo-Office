"""Image object: aus ``core.objekte.anordnung.objekte`` herausgelöst."""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from core.objekte.bilder.modell.bildformat import format_erkennen, masse
from core.objekte.anordnung.objekte_hilfen import Anchor, FillStyle, StrokeStyle, Transform, WrapSettings, _rest


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
