"""Wordart einfuegen: aus ``core.bearbeitung.einfuegen`` herausgelöst."""
from __future__ import annotations
from PySide6.QtGui import QImage
from core.formatierung.farben.farben import Farbe
from core.bearbeitung.einfuegen_hilfen import WORDART_VORLAGEN


def wordart_vorlage_bild(text: str, nr: int, schrift: str = "Liberation Sans", pt: int = 48) -> QImage:
    """WordArt nach einem der 15 Stile der Galerie: Füllverlauf, Kontur und Schatten (gezeichnet über ``core/rendering/wordart.py``)."""
    from vcl.qt.rendering.formen.anzeige import kern_bild
    from core.layout.drucklayout.ausgabe.text import wordart
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    b, h = wordart.masse(engine, text, schrift, pt)
    return kern_bild(b, h, lambda z: wordart.zeichne(z, engine, text, WORDART_VORLAGEN[nr], schrift, pt))


def wordart_bild(text: str, stil: str = "Verlauf", schrift: str = "Liberation Sans", pt: int = 48, farbe: str = Farbe.AKZENT,
                 vorlage: int | None = None) -> QImage:
    """WordArt in einem der älteren Stile (Verlauf, Schatten, Umriss, Regenbogen, Welle) oder nach einer Vorlage der Galerie; gezeichnet vom Kern."""
    if vorlage is not None:
        return wordart_vorlage_bild(text, vorlage, schrift, pt)
    import math as _m
    from vcl.qt.rendering.formen.anzeige import kern_bild
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe.backend import LinearGradient, Style, rgba
    from core.layout.drucklayout.ausgabe.objekte.objekte import dunkler, heller
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
    engine = standard_engine()
    f = FontSpec(schrift, float(pt), 700)
    m = engine.font_metrics(f)
    b, h = int(engine.measure_text(text, f)) + 40, int(m.line_spacing) + 40
    ops = engine.glyphen_pfad(text, f, 20.0, 20.0 + m.ascent)
    if stil == "Welle":                                                      # Wellenlinie über die Breite
        ops = [op if op[0] == "Z" else (op[0],) + tuple(v + (_m.sin(op[i - 1] / 18) * h * 0.08 if i % 2 == 0 else 0.0) for i, v in enumerate(op[1:], 1)) for op in ops]

    def zeichnen(z) -> None:
        if stil == "Schatten":
            z.push_state(translate=Point(4, 4))
            z.draw_path(ops, Style(color=(0, 0, 0, 90), width=0, filled=True), True, True)
            z.pop_state()
        if stil == "Umriss":
            z.draw_path(ops, Style(color=rgba(farbe), width=2.2), True, True)
            return
        if stil == "Regenbogen":
            cs = ("#e03131", "#f08c00", "#ffd43b", Farbe.GRUEN, "#1971c2", "#7048a8")
            fill = LinearGradient(Point(0, 0), Point(b, 0), tuple((i / 5, rgba(c)) for i, c in enumerate(cs)))
        else:
            c = rgba(farbe)
            fill = LinearGradient(Point(0, 0), Point(0, h), ((0.0, heller(c, 150)), (1.0, dunkler(c, 150))))
        z.draw_path(ops, Style(color=rgba(farbe), width=0, filled=True, fill=fill), True, True)
    return kern_bild(b, h, zeichnen)
