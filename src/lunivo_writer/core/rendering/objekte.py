"""Bilder und Formen über das Rendering-Backend zeichnen (ohne Qt): Füllung, Bild, Ausschnitt (Ellipse), Kontur und Drehung eines Bildobjekts; Formen aus Grundformen und Pfaden.

Die Lage kommt vom Layoutkern (``core/layout/objekte.py``); hier wird nur gezeichnet. Das Backend decodiert die Bilddaten (``draw_image``)."""
from __future__ import annotations

import colorsys

from lunivo_writer.core.document.objekte import FillStyle, ImageObject, ShapeObject, StrokeStyle, VectorPath
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering.backend import ImageFill, LinearGradient, PatternFill, RenderTarget, Style, TextureFill, rgba

STRICH = {"einfach": None, "gepunktet": "dot", "fein_gestrichelt": (3.0, 2.0), "gestrichelt": "dash", "strichpunkt": "dashdot", "strichpunktpunkt": "dashdotdot"}


def heller(farbe: tuple[int, int, int, int], faktor: int = 160) -> tuple[int, int, int, int]:
    """Aufhellen wie ``QColor.lighter``: der Hellwert (V) wird mit ``faktor`` / 100 multipliziert; was über 255 hinausgeht, nimmt die Sättigung weg."""
    r, g, b, a = farbe
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    s, v = s * 255, v * 255
    v = v * faktor / 100
    if v > 255:
        s = max(0.0, s - (v - 255))
        v = 255.0
    r2, g2, b2 = colorsys.hsv_to_rgb(h, s / 255, v / 255)
    return round(r2 * 255), round(g2 * 255), round(b2 * 255), a


def fuellstil(f: FillStyle | None, r: Rect, bild: bytes | None = None) -> Style | None:
    """Der Stil für die Füllung eines Rechtecks; ``None``, wenn es keine Füllung gibt (oder eine Bildfüllung ohne ``bild``). ``bild``: Bytes des Füllbildes."""
    if f is None:
        return None
    if f.kind == "farbe":
        return Style(color=rgba(f.color), width=0, filled=True)
    if f.kind in ("verlauf", "graduell"):
        dunkel = rgba(f.color) if f.kind == "verlauf" else rgba(f.params.get("dunkel", f.color))
        hell = heller(rgba(f.color)) if f.kind == "verlauf" else rgba(f.params.get("hell", "#ffffff"))
        return Style(width=0, filled=True, fill=LinearGradient(Point(r.x, r.y), Point(r.x, r.bottom), ((0.0, hell), (1.0, dunkel))))
    if f.kind == "muster":
        return Style(width=0, filled=True, fill=PatternFill(str(f.params.get("key", "rein")), f.color or "#000000", f.params.get("grund") or "#ffffff"))
    if f.kind == "textur":
        return Style(width=0, filled=True, fill=TextureFill(str(f.params.get("key", "papier"))))
    if f.kind == "bild" and bild:
        return Style(width=0, filled=True, fill=ImageFill(bild))
    return None


def kontur_stil(s: StrokeStyle) -> Style:
    return Style(color=rgba(s.color), width=s.width, dash=STRICH.get(s.dash))


def zeichne_bild(b: RenderTarget, obj: ImageObject, rect: Rect, daten: bytes | None = None, fuellbild: bytes | None = None) -> None:
    """Das Bildobjekt in ``rect`` zeichnen: Drehung um die Mitte, Effekte hinter dem Bild, Füllung, Bild (bei ``ellipse`` im Oval beschnitten), Kontur innerhalb des Rechtecks.
    ``daten`` überschreibt die Bilddaten des Objekts (zum Beispiel ein zugeschnittenes Bild), ``fuellbild`` ist das Bild einer Bildfüllung; ohne Bilddaten wird ein Platzhalter gezeichnet."""
    if rect.width <= 0 or rect.height <= 0:
        return
    transform = obj.transform
    veraendert = bool(transform.rotation or transform.flip_h or transform.flip_v)
    b.push_state(opacity=obj.opacity, translate=Point(rect.x + rect.width / 2, rect.y + rect.height / 2) if veraendert else None,
                 rotate=transform.rotation, antialias=True, flip_h=transform.flip_h, flip_v=transform.flip_v)
    ziel = Rect(-rect.width / 2, -rect.height / 2, rect.width, rect.height) if veraendert else rect
    bytes_ = daten if daten is not None else obj.data
    ellipse = obj.ellipse or str(obj.mask).casefold() in ("ellipse", "kreis")
    source_rect = None
    if bytes_ and isinstance(obj.crop, (list, tuple)) and len(obj.crop) == 4:
        try:
            links, oben, rechts, unten = (max(0.0, min(1.0, float(v))) for v in obj.crop)
            breite, hoehe = max(0.0, 1.0 - links - rechts), max(0.0, 1.0 - oben - unten)
            if breite > 0.0 and hoehe > 0.0 and (links or oben or rechts or unten):
                source_rect = Rect(links, oben, breite, hoehe)
        except (TypeError, ValueError):
            source_rect = None
    if obj.effects and bytes_:
        b.draw_effects_behind(bytes_, ziel, ellipse, obj.effects)
        bytes_, ellipse = b.apply_image_effects(bytes_, ziel, ellipse, obj.effects)
    b.push_state(clip_ellipse=ziel if ellipse else None)
    stil = fuellstil(obj.fill, ziel, fuellbild)
    if stil is not None:
        b.draw_rect(ziel, stil)
    if bytes_:
        if source_rect is None:
            b.draw_image(bytes_, ziel, smooth=True)
        else:
            b.draw_image(bytes_, ziel, smooth=True, source_rect=source_rect)
    else:
        zeichne_platzhalter(b, ziel)
    b.pop_state()
    if obj.stroke:
        k = obj.stroke.width / 2
        innen = Rect(ziel.x + k, ziel.y + k, ziel.width - 2 * k, ziel.height - 2 * k)
        if ellipse:
            b.draw_ellipse(Point(innen.x + innen.width / 2, innen.y + innen.height / 2), innen.width / 2, innen.height / 2, kontur_stil(obj.stroke))
        else:
            b.draw_rect(innen, kontur_stil(obj.stroke))
    b.pop_state()


def zeichne_platzhalter(b: RenderTarget, r: Rect) -> None:
    """Ersatz für ein fehlendes Bild: graue Fläche mit Rahmen und Kreuz."""
    b.draw_rect(r, Style(color=(235, 235, 235, 255), width=0, filled=True))
    b.draw_rect(r, Style(color=(160, 160, 160, 255), width=1))
    b.draw_line(Point(r.x, r.y), Point(r.right, r.bottom), Style(color=(160, 160, 160, 255), width=1))
    b.draw_line(Point(r.right, r.y), Point(r.x, r.bottom), Style(color=(160, 160, 160, 255), width=1))


def form_pfad(s: ShapeObject, r: Rect) -> VectorPath | None:
    """Der Umriss der einfachen Grundformen in ``r``; ``None`` für Katalogformen, die das Backend nicht aus Grundformen baut."""
    if s.path is not None:
        return s.path
    if s.kind == "rechteck":
        return VectorPath((("R", r.x, r.y, r.width, r.height),))
    if s.kind in ("abgerundet", "abgerundetes_rechteck"):
        radius = (s.adjust[0] if s.adjust else 0.16667) * min(r.width, r.height)
        return VectorPath.rounded_rect(r.x, r.y, r.width, r.height, radius)
    if s.kind in ("ellipse", "kreis"):
        return VectorPath((("E", r.x + r.width / 2, r.y + r.height / 2, r.width / 2, r.height / 2),))
    if s.kind == "linie":
        return VectorPath((("M", r.x, r.y), ("L", r.right, r.bottom)))
    if s.kind == "pfeil":
        return VectorPath.arrow(r.x, r.y + r.height / 2, r.right, r.y + r.height / 2, min(14.0, r.width / 3))
    return None


def zeichne_form(b: RenderTarget, s: ShapeObject, rect: Rect) -> bool:
    """Eine Form in ``rect`` zeichnen (Schatten, Füllung, Kontur, Drehung, Deckkraft). ``False``, wenn die Art nur das Qt-Zeichnen der Anwendung kennt."""
    pfad = form_pfad(s, rect)
    if pfad is None:
        return False
    transform = s.transform
    veraendert = bool(transform.rotation or transform.flip_h or transform.flip_v)
    b.push_state(opacity=s.opacity, translate=Point(rect.x + rect.width / 2, rect.y + rect.height / 2) if veraendert else None,
                 rotate=transform.rotation, antialias=True, flip_h=transform.flip_h, flip_v=transform.flip_v)
    if veraendert and s.path is None:
        rect = Rect(-rect.width / 2, -rect.height / 2, rect.width, rect.height)
        pfad = form_pfad(s, rect)
    if s.shadow:
        sch = s.shadow
        b.draw_shadow(list(pfad.ops), rgba(sch.color, round(255 * sch.opacity)), sch.blur, sch.dx, sch.dy)
    offen = s.kind in ("linie", "pfeil")
    stil = fuellstil(s.fill, rect) if not offen else None
    kontur = kontur_stil(s.stroke) if s.stroke and s.stroke.width > 0 else None
    if stil is not None:
        b.draw_path(list(pfad.ops), Style(color=stil.color, width=0, filled=True, fill=stil.fill))
    if kontur is not None:
        b.draw_path(list(pfad.ops), kontur)
    b.pop_state()
    return True
