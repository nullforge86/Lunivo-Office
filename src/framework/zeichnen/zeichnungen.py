"""Einzelne Zeichnungen des Kerns (Sprechblasen, Linien, Zeichenzusätze, Wasserzeichen, Deckblatt, Platzhalter, Diagramm, SVG, WordArt) als Rasterbild."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from framework.anbindung import Daten, fest
from framework.schnittstellen import BlasenSchrift
from framework.zeichnen.raster import Flaeche, Rasterbild, Rechteck, _malen, _rect

Farbe = tuple[int, int, int, int]


def blase(flaeche: Flaeche, autor: str, datum: str, farbe: Farbe, text: str, r: Rechteck, schrift: BlasenSchrift, farben: tuple[Farbe, Farbe, Farbe]) -> Rasterbild:
    """Eine Sprechblase wie eine Karte."""
    import core.layout.drucklayout.ausgabe.objekte as blasen
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    return _malen(flaeche, lambda z: blasen.zeichne_blase(z, engine, autor, datum, farbe, text, _rect(r), schrift, farben))


def blasen_verbindung(flaeche: Flaeche, farbe: Farbe, x_text: float, y_text: float, r: Rechteck, rechts: bool) -> Rasterbild:
    """Linie vom Text zur Blase."""
    import core.layout.drucklayout.ausgabe.objekte as blasen
    return _malen(flaeche, lambda z: blasen.verbindung(z, farbe, x_text, y_text, _rect(r), rechts))


def linie(flaeche: Flaeche, farbe: str, breite_pt: float, art: str, x1: float, y1: float, x2: float, y2: float, massstab: float = 1.0) -> Rasterbild:
    """Eine einzelne Linie in ihrer Art."""
    from core.layout.drucklayout.ausgabe.objekte import zeichne_linie
    return _malen(flaeche, lambda z: zeichne_linie(z, farbe, breite_pt, art, x1, y1, x2, y2, massstab))


def rahmen(flaeche: Flaeche, farbe: str, breite_pt: float, art: str, seiten: str, r: Rechteck, massstab: float = 1.0, innen_y: Sequence[float] = ()) -> Rasterbild:
    """Die gemeinten Seiten eines Rechtecks in der Linienart."""
    from core.layout.drucklayout.ausgabe.objekte import zeichne_rahmen
    return _malen(flaeche, lambda z: zeichne_rahmen(z, farbe, breite_pt, art, seiten, _rect(r), massstab, innen_y))


def unterstrich(flaeche: Flaeche, strecken: Sequence[tuple[float, float]], art: str, grundlinie: float, groesse: float, farbe: Farbe) -> Rasterbild:
    """Unterstreichung in ihrer Art über die Strecken."""
    import core.layout.drucklayout.ausgabe.text as Z
    return _malen(flaeche, lambda z: Z.unterstrich(z, [tuple(s) for s in strecken], art, grundlinie, groesse, farbe) if art else None)


def doppelt_durch(flaeche: Flaeche, r: Rechteck, grundlinie: float, groesse: float, farbe: Farbe) -> Rasterbild:
    """Doppelt durchgestrichen."""
    import core.layout.drucklayout.ausgabe.text as Z
    return _malen(flaeche, lambda z: Z.doppelt_durch(z, _rect(r), grundlinie, groesse, farbe))


def betonung(flaeche: Flaeche, glyphen: Sequence[tuple[float, float, float]], art: str, grundlinie: float, groesse: float, farbe: Farbe) -> Rasterbild:
    """Betonungszeichen über den Glyphen."""
    import core.layout.drucklayout.ausgabe.text as Z
    return _malen(flaeche, lambda z: Z.betonung(z, [tuple(g) for g in glyphen], art, grundlinie, groesse, farbe))


def umschlossen(flaeche: Flaeche, kasten: Rechteck, wie: tuple[str, str], farbe: Farbe, groesse: float) -> Rasterbild:
    """Umschlossenes Zeichen (Kreis, Quadrat …)."""
    import core.layout.drucklayout.ausgabe.text as Z
    return _malen(flaeche, lambda z: Z.umschlossen(z, _rect(kasten), wie, farbe, groesse))


def ruby(flaeche: Flaeche, x0: float, x1: float, grundlinie: float, groesse: float, ruby_: Mapping[str, str | float], farbe: Farbe) -> Rasterbild:
    """Ruby-Text über dem Grundtext."""
    import core.layout.drucklayout.ausgabe.text as Z
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    return _malen(flaeche, lambda z: Z.ruby(z, engine, x0, x1, grundlinie, groesse, dict(ruby_), farbe))


def wasserzeichen(flaeche: Flaeche, w: Mapping[str, str | int | float | bool | None] | None, r: Rechteck) -> Rasterbild:
    """Das Wasserzeichen in ``r``."""
    from core.layout.drucklayout.ausgabe.seite import zeichne
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    return _malen(flaeche, lambda z: zeichne(z, engine, dict(w) if w is not None else None, _rect(r)))


def deckblatt(flaeche: Flaeche, name: str, r: Rechteck, mit_text: bool = True) -> Rasterbild:
    """Ein Deckblatt (mit oder ohne Beispieltext)."""
    from core.dokument.abschnitte import zeichnen_mit
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    return _malen(flaeche, lambda z: zeichnen_mit(z, name, _rect(r), mit_text, engine))


def deckblatt_grafik(flaeche: Flaeche, name: str, r: Rechteck) -> Rasterbild:
    """Nur die Grafik eines Deckblatts."""
    from core.dokument.abschnitte import grafik
    return _malen(flaeche, lambda z: grafik(z, name, _rect(r)))


def platzhalter(flaeche: Flaeche, r: Rechteck) -> Rasterbild:
    """Platzhalter für ein fehlendes Bild."""
    from core.layout.drucklayout.ausgabe.objekte import zeichne_platzhalter
    return _malen(flaeche, lambda z: zeichne_platzhalter(z, _rect(r)))


def svg(flaeche: Flaeche, daten: bytes, r: Rechteck) -> tuple[Rasterbild, bool]:
    """Ein SVG-Bild in ``r``; → (Bild, gelungen)."""
    from core.layout.drucklayout.ausgabe.bild import svg_zeichnen
    gelungen = [False]

    def los(z) -> None:
        gelungen[0] = svg_zeichnen(daten, z, _rect(r))
    bild = _malen(flaeche, los)
    return bild, gelungen[0]


def diagramm(flaeche: Flaeche, r: Rechteck, d: Mapping[str, Daten], mit_geo: bool = False) -> tuple[Rasterbild, Mapping[str, Daten]]:
    """Das Diagramm ``d`` in ``r``; → (Bild, Rechtecke der Teile als ``(x, y, Breite, Höhe)``, bei mehreren Balken als Liste; leer ohne ``mit_geo``)."""
    from core.layout.drucklayout.ausgabe.diagramm import zeichne_diagramm
    geo = {} if mit_geo else None
    bild = _malen(flaeche, lambda z: zeichne_diagramm(z, _rect(r), d, geo))
    return bild, fest({k: [(x.x, x.y, x.width, x.height) for x in v] if isinstance(v, list) else (v.x, v.y, v.width, v.height) for k, v in (geo or {}).items()})


def _seite_mit_raendern(raender_mm: tuple[float, float, float, float]):
    from types import SimpleNamespace
    links, oben, rechts, unten = raender_mm
    return SimpleNamespace(margin_left_mm=links, margin_top_mm=oben, margin_right_mm=rechts, margin_bottom_mm=unten)


def seitenrahmen_rechteck(b: Mapping[str, Daten], raender_mm: tuple[float, float, float, float], seite: Rechteck) -> Rechteck:
    """Das Rechteck des Seitenrahmens ``b`` auf einer Seite mit dem Rechteck ``seite``; ``raender_mm``: Seitenränder (links, oben, rechts, unten)."""
    from core.layout.drucklayout.ausgabe.seite import rechteck
    e = rechteck(b, _seite_mit_raendern(raender_mm), _rect(seite))
    return Rechteck(e.x, e.y, e.width, e.height)


def seitenrahmen(flaeche: Flaeche, b: Mapping[str, Daten], raender_mm: tuple[float, float, float, float], seite: Rechteck) -> Rasterbild:
    """Den Seitenrahmen ``b`` auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen)."""
    from core.layout.drucklayout.ausgabe.seite import zeichnen
    page = _seite_mit_raendern(raender_mm)
    return _malen(flaeche, lambda z: zeichnen(z, b, page, _rect(seite)))


def bild(flaeche: Flaeche, r: Rechteck, daten: bytes, ellipse: bool, rand: Mapping[str, Daten] | None, dreh: float, fuell: Mapping[str, Daten] | None,
         fuellbild: bytes | None, fx: Mapping[str, Daten] | None) -> Rasterbild:
    """Ein Bild in ``r`` mit Füllung, Kontur, Drehung und Effekten."""
    from core.layout.drucklayout.ausgabe.objekte import zeichne_bild
    from core.objekte.anordnung import FillStyle, ImageObject, StrokeStyle, Transform
    obj = ImageObject(r[2], r[3], None, ellipse=ellipse, transform=Transform(dreh), fill=FillStyle.aus_dict(fuell), stroke=StrokeStyle.aus_dict(rand), effects=fx or None)
    return _malen(flaeche, lambda z: zeichne_bild(z, obj, _rect(r), daten, fuellbild))


def text_mit_effekt(flaeche: Flaeche, text: str, mitte: tuple[float, float], schrift: tuple[str, float, int, bool], farbe: Farbe, fx: Mapping[str, Daten],
                    kontur: tuple[Farbe, float] | None = None) -> Rasterbild:
    """Text mit Effekt, um ``mitte`` zentriert; ``schrift``: (Familie, Größe in pt, Gewicht, kursiv); ``kontur``: (Farbe, Breite in Bildpunkten)."""
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe.text import zeichne_text_mit_effekt
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    fs = FontSpec(schrift[0], schrift[1], schrift[2], schrift[3])
    m = engine.font_metrics(fs)
    x = mitte[0] - engine.measure_text(text, fs) / 2
    y = mitte[1] + (m.ascent - m.descent) / 2
    return _malen(flaeche, lambda z: zeichne_text_mit_effekt(z, engine, text, Point(x, y), fs, farbe, fx, kontur))


def wordart_masse(text: str, schrift: str, pt: int) -> tuple[float, float]:
    """Breite und Höhe einer WordArt-Vorschau."""
    import core.layout.drucklayout.ausgabe.text as wordart
    from framework.dokumentverwaltung.ausgabe import standard_engine
    b, h = wordart.masse(standard_engine(), text, schrift, pt)
    return float(b), float(h)


def wordart(flaeche: Flaeche, text: str, nr: int, schrift: str, pt: int) -> Rasterbild:
    """WordArt nach einem der Stile der Galerie."""
    from core.bearbeitung import WORDART_VORLAGEN
    import core.layout.drucklayout.ausgabe.text as W
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    return _malen(flaeche, lambda z: W.zeichne(z, engine, text, WORDART_VORLAGEN[nr], schrift, pt))
