"""Kopf- und Fußzeile einer Seite zeichnen, ohne Qt: Textstücke mit eigener Schrift, Farbe, Unterstreichen, Durchstreichen und Hervorheben, Zeile für Zeile ausgerichtet, vertikal in der
Zeilenhöhe zentriert. Kopf-/Fußzeilen mit Texteffekten (Schatten, Kontur …) zeichnet weiter der Editor (``False`` als Ergebnis).

``kopf_fuss`` liefert die Seitenräume: ``einr.kopf_fuss(n, angezeigt)`` → (Kopf, Fuß) mit ``is_empty()``, ``text``, ``laeufe()``, ``fmt`` und ``align``."""
from __future__ import annotations

from typing import Callable

from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering.backend import RenderBackend, Style, rgba
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine

PX_JE_PT = 96.0 / 72.0
STANDARD_PX = 13                                    # Schriftgröße ohne Angabe (Bildpunkte)


def schrift(grund: FontSpec, fmt: dict) -> FontSpec:
    """Schrift einer Kopf-/Fußzeile aus ihrem Zeichenformat (``family``, ``size_pt``, ``bold``, ``italic``, ``script`` hoch/tief verkleinert)."""
    pt = float(fmt["size_pt"]) if fmt.get("size_pt") else STANDARD_PX / PX_JE_PT
    if fmt.get("script") in ("sup", "sub"):
        pt = max(1.0, round(round(pt * PX_JE_PT) * 0.65)) / PX_JE_PT
    return FontSpec(fmt.get("family") or grund.family, pt, 700 if fmt.get("bold", grund.weight >= 600) else 400, bool(fmt.get("italic", grund.italic)))


def _mit_effekt(hf) -> bool:
    return any((fmt or {}).get("effekt") or (fmt or {}).get("kontur") for _t, fmt in hf.laeufe())


def zeichne_zeile(b: RenderBackend, engine: TextLayoutEngine, hf, rect: Rect, text_fn: Callable[[str], str], ausrichtung: str, grund: FontSpec) -> bool:
    """Eine Kopf- oder Fußzeile in ``rect``. ``text_fn`` ersetzt Felder (Seitenzahl …) im Text. ``False``, wenn sie Texteffekte trägt und der Aufrufer sie anders zeichnen muss."""
    if hf.is_empty():
        return True
    if _mit_effekt(hf):
        return False
    zeilen: list[list] = [[]]
    for text, fmt in hf.laeufe():
        for k, teil in enumerate(text_fn(text).split("\n")):
            if k:
                zeilen.append([])
            if teil:
                zeilen[-1].append((teil, fmt or {}))
    gesetzt = []                                                       # je Zeile: (Stücke, Höhe, Oberlänge, Breite)
    for zeile in zeilen:
        stuecke, hoch, steig = [], 0.0, 0.0
        for teil, fmt in zeile:
            f = schrift(grund, fmt)
            m = engine.font_metrics(f)
            stuecke.append((teil, f, fmt, engine.measure_text(teil, f)))
            hoch, steig = max(hoch, m.ascent + m.descent), max(steig, m.ascent)
        if not stuecke:
            m = engine.font_metrics(schrift(grund, hf.fmt or {}))
            hoch, steig = m.ascent + m.descent, m.ascent
        gesetzt.append((stuecke, hoch, steig, sum(s[3] for s in stuecke)))
    y = rect.y + rect.height / 2 - sum(z[1] for z in gesetzt) / 2
    for stuecke, hoch, steig, breite in gesetzt:
        x = rect.x + rect.width / 2 - breite / 2 if ausrichtung == "center" else rect.right - breite if ausrichtung == "right" else rect.x
        for teil, f, fmt, w in stuecke:
            farbe = rgba(fmt.get("color") or (hf.fmt or {}).get("color") or "#000000")
            if fmt.get("highlight"):
                b.draw_rect(Rect(x, y, w, hoch), Style(color=rgba(fmt["highlight"]), width=0, filled=True))
            b.draw_text(teil, Point(x, y + steig), f, Style(color=farbe))
            if fmt.get("underline"):
                b.draw_line(Point(x, y + steig + 2), Point(x + w, y + steig + 2), Style(color=farbe, width=1.0))
            if fmt.get("strike"):
                b.draw_line(Point(x, y + steig - f.size_pt * PX_JE_PT / 3), Point(x + w, y + steig - f.size_pt * PX_JE_PT / 3), Style(color=farbe, width=1.0))
            x += w
        y += hoch
    return True
