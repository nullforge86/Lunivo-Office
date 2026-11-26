"""Vorschaubilder für das Einfügen (Form, Formel, WordArt in den älteren Stilen, Dateisymbol): Der Kern misst und zeichnet, hinaus geht nur das Rasterbild."""
from __future__ import annotations

from collections.abc import Sequence

from framework.zeichnen.raster import Flaeche, Rasterbild, Rechteck, _malen

Pfad = Sequence[tuple[str | float, ...]]


def _fuellstil(fuell: str, art: str, x: float, y: float, w: float, h: float):
    """Füllung einer Form als ``Style``: einfarbig, ``verlauf`` (hell nach Farbe), ``abgestuft`` (drei Stufen), ``glanz`` (obere Hälfte heller)."""
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe import LinearGradient, Style, rgba
    from core.layout.drucklayout.ausgabe.objekte import dunkler, heller
    c = rgba(fuell)
    if art not in ("verlauf", "abgestuft", "glanz"):
        return Style(color=c, width=0, filled=True)
    if art == "verlauf":
        stops = ((0.0, heller(c, 170)), (1.0, c))
    elif art == "abgestuft":
        stops = tuple((pos, heller(c, f)) for pos, f in ((0, 150), (0.33, 150), (0.34, 115), (0.66, 115), (0.67, 100), (1, 100)))
    else:
        stops = ((0.0, heller(c, 165)), (0.49, heller(c, 125)), (0.5, dunkler(c, 108)), (1.0, c))
    return Style(color=c, width=0, filled=True, fill=LinearGradient(Point(x, y), Point(x, y + h), stops))


def form(flaeche: Flaeche, ops: Pfad, offen: bool, ist_linie: bool, vertikal: bool, kasten: Rechteck, fuell: str, fuell_art: str, linie: str, strich: float,
         text: str) -> Rasterbild:
    """Eine Form aus ihrem Umriss ``ops`` im Rechteck ``kasten``: Füllung, Kontur und Text; ``vertikal``: Textfeld mit senkrecht laufendem Text."""
    from core.geometrie import Point, Rect
    from core.layout.drucklayout.ausgabe import Style, rgba
    from core.textsatz import FontSpec
    x, y, w, h = kasten

    def zeichnen(z) -> None:
        if fuell and not offen and not ist_linie:
            z.draw_path(ops, _fuellstil(fuell, fuell_art, x, y, w, h), True, True)
        lc = rgba(linie)
        if lc[3] > 0:
            z.draw_path(ops, Style(color=lc, width=strich, join="round"), True, True)
        if vertikal:                                                     # Textfeld mit senkrecht laufendem Text (90° gedreht)
            z.draw_rect(Rect(x, y, w, h), Style(color=lc, width=strich))
        if text:
            hell = rgba(fuell) if fuell else None
            weiss = hell is not None and (max(hell[:3]) + min(hell[:3])) / 2 < 140
            farbe = (255, 255, 255, 255) if weiss else (0, 0, 0, 255)
            schrift = FontSpec("Liberation Sans", 12)
            if vertikal:
                z.push_state(translate=Point(x + w / 2, y + h / 2), rotate=90)
                z.draw_text_box(text, Rect(-h / 2 + 6, -w / 2 + 6, h - 12, w - 12), schrift, Style(color=farbe), align="left", wrap=True, valign="top")
                z.pop_state()
            else:
                z.draw_text_box(text, Rect(x, y, w, h), schrift, Style(color=farbe), align="center", wrap=True, valign="center")
    return _malen(flaeche, zeichnen)


def formel(teile: Sequence[tuple[str, str]], pt: int, farbe: str) -> Rasterbild:
    """Die Formel aus ihren Stücken ``(Text, "normal" | "hoch" | "tief")``: kursiv, Hoch- und Tiefgestelltes verkleinert und versetzt."""
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe import Style, rgba
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    basis, klein = FontSpec("DejaVu Serif", float(pt), 400, True), FontSpec("DejaVu Serif", pt * 2 / 3, 400, True)
    stuecke, x = [], 0.0
    for t, a in teile:
        f = klein if a in ("hoch", "tief") else basis
        stuecke.append((t, a, f, x))
        x += engine.measure_text(t, f)
    m = engine.font_metrics(basis)
    grund = 2 + pt * 0.45 + m.ascent
    b, h = int(x) + 8, int(grund + m.descent + pt * 0.3) + 4

    def zeichnen(z) -> None:
        for t, a, f, x0 in stuecke:
            z.draw_text(t, Point(4 + x0, grund - pt * 0.4 if a == "hoch" else grund + pt * 0.2 if a == "tief" else grund), f, Style(color=rgba(farbe)))
    return _malen(Flaeche(b, h), zeichnen)


def wordart_stil(text: str, stil: str, schrift: str, pt: int, farbe: str, regenbogen: Sequence[str]) -> Rasterbild:
    """WordArt in einem der älteren Stile (Verlauf, Schatten, Umriss, Regenbogen, Welle); ``regenbogen``: die Farben des Regenbogenverlaufs."""
    import math as _m
    from core.geometrie import Point
    from core.layout.drucklayout.ausgabe import LinearGradient, Style, rgba
    from core.layout.drucklayout.ausgabe.objekte import dunkler, heller
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe import standard_engine
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
            cs = regenbogen
            fill = LinearGradient(Point(0, 0), Point(b, 0), tuple((i / 5, rgba(c)) for i, c in enumerate(cs)))
        else:
            c = rgba(farbe)
            fill = LinearGradient(Point(0, 0), Point(0, h), ((0.0, heller(c, 150)), (1.0, dunkler(c, 150))))
        z.draw_path(ops, Style(color=rgba(farbe), width=0, filled=True, fill=fill), True, True)
    return _malen(Flaeche(b, h), zeichnen)


def datei_symbol(name: str, symbol: Rasterbild, breite: int, farbe: str) -> Rasterbild:
    """Dateisymbol (``symbol``: Bildpunkte als RGBA) mit dem Namen darunter; ein zu langer Name wird in der Mitte gekürzt."""
    from core.geometrie import Point, Rect
    from core.layout.drucklayout.ausgabe import Style, rgba
    from core.layout.drucklayout.ausgabe.bild import png_bytes
    from core.textsatz import FontSpec
    from framework.dokumentverwaltung.ausgabe import standard_engine
    engine = standard_engine()
    sym_b, sym_h, roh = symbol
    f = FontSpec("Liberation Sans", 9.0)
    zeile = name
    if engine.measure_text(zeile, f) > breite - 8:                           # in der Mitte kürzen, bis der Name passt
        rest, links, rechts = name, 0, 0
        while len(rest) > 2 and engine.measure_text(name[:links + 1] + "…" + name[len(name) - rechts:], f) <= breite - 8:
            if links <= rechts:
                links += 1
            else:
                rechts += 1
        zeile = name[:links] + "…" + (name[len(name) - rechts:] if rechts else "")
    m = engine.font_metrics(f)
    png = png_bytes(sym_b, sym_h, roh)
    b, h = breite, sym_h + 12 + int(m.line_spacing)

    def zeichnen(z) -> None:
        z.draw_image(png, Rect((breite - sym_b) // 2, 4, sym_b, sym_h), smooth=True)
        z.draw_text(zeile, Point((breite - engine.measure_text(zeile, f)) / 2, sym_h + 8 + m.ascent), f, Style(color=rgba(farbe)))
    return _malen(Flaeche(b, h), zeichnen)
