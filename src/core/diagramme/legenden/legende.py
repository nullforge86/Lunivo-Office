"""Legende: aus ``core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner`` herausgelöst."""
from __future__ import annotations
from core.geometrie import Rect
from core.layout.drucklayout.ausgabe.backend import Style
from core.layout.drucklayout.ausgabe.diagramm import diagrammformat as DF
from core.layout.drucklayout.ausgabe.diagramm.diagrammtypen import ist_kreis
from core.layout.drucklayout.ausgabe.diagramm.diagrammzeichner_hilfen import _Z, _reihenfarbe


# ---- Legende ------------------------------------------------------------------------------------------------------------------
def _eintraege(z: _Z) -> list:
    v = z.v
    if ist_kreis(v["art"]):
        return [(str(k), z.v["palette"][i % len(z.v["palette"])]) for i, k in enumerate(v["kat"])]
    if v["art"].startswith("kurs"):
        return []
    return [(str(n), _reihenfarbe(v, i, v["nummern"][i] if i < len(v["nummern"]) else i)) for i, n in enumerate(v["reihen"])]


def _legende(z: _Z, flaeche: Rect) -> Rect:
    v = z.v
    eintraege = _eintraege(z)
    if not v["legende"] or not eintraege:
        return flaeche
    pos = v["legende_pos"] if v["legende_pos"] in ("oben", "unten", "links", "rechts") else "unten"
    lfmt = z.tf.get("legende") or {}
    lf, lfarbe, _fx = DF.schrift(lfmt.get("text"), z.schrift, z.text)
    breiten = [z.engine.measure_text(n, lf) + 22 for n, _c in eintraege]
    zeile = max(20.0, z.engine.font_metrics(lf).line_spacing + 4)

    def box(rect: Rect) -> Rect:
        if any(lfmt.get(k) for k in ("fuell", "linie")) or DF.hat_effekte(lfmt):
            DF.teil_zeichnen(z.b, z.engine, rect, {k: x for k, x in lfmt.items() if k in ("fuell", "linie") or k in DF.FX_SCHLUESSEL}, z.grund)
        return rect

    def eintrag(n: str, c: tuple, x: float, y: float, w: float, h: float) -> None:
        z.b.draw_rect(Rect(x, y + h / 2 - 4, 8, 8), Style(color=c, width=0, filled=True))
        z.b.draw_text_box(n, Rect(x + 12, y, w - 12, h), lf, Style(color=lfarbe), "left", False, "center")
    if pos in ("oben", "unten"):
        h = zeile + 2
        y = flaeche.y + 2 if pos == "oben" else flaeche.bottom - h
        x = flaeche.x + (flaeche.width - sum(breiten)) / 2
        z.teil("legende", box(Rect(x, y, sum(breiten), h)))
        for i, (n, c) in enumerate(eintraege):
            eintrag(n, c, x, y, breiten[i], h)
            z.teil(f"legendeneintrag_{i}", Rect(x, y, breiten[i], h))
            x += breiten[i]
        return Rect(flaeche.x, flaeche.y + (h + 4 if pos == "oben" else 0), flaeche.width, flaeche.height - h - 4)
    br = max(breiten) + 8
    x = flaeche.x + 4 if pos == "links" else flaeche.right - br
    y0 = flaeche.y + (flaeche.height - len(eintraege) * zeile) / 2
    z.teil("legende", box(Rect(x, y0, br, len(eintraege) * zeile)))
    for i, (n, c) in enumerate(eintraege):
        eintrag(n, c, x, y0 + i * zeile, br, zeile)
        z.teil(f"legendeneintrag_{i}", Rect(x, y0 + i * zeile, br, zeile))
    return Rect(flaeche.x + (br + 6 if pos == "links" else 0), flaeche.y, flaeche.width - br - 6, flaeche.height)
