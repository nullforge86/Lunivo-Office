"""Wasserzeichen einer Seite ohne Qt: Text oder Bild mit Lage, Größe, Drehung und Deckkraft als Zeichenanweisungen für ein ``RenderTarget``.

Das Wasserzeichen ist ein Wörterbuch (``PageSettings.watermark``): ``text``, ``schrift``, ``groesse_pt`` (0 = automatisch), ``farbe``, ``winkel``, ``bild`` (Bilddatei als Base64), ``zoom`` (0 = automatisch),
``auswaschen``, ``h``/``h_mm``, ``v``/``v_mm``, ``transparenz`` (0…100), ``ganzseitig`` (das Bild füllt das ganze Blatt)."""
from __future__ import annotations

import base64

from lunivo_writer.core.document.bildformat import format_erkennen, masse
from lunivo_writer.core.geometry import Point, Rect
from lunivo_writer.core.rendering.backend import RenderTarget, Style, rgba
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine

PX_JE_MM = 96.0 / 25.4
STANDARD_FARBE = "#c0c0c0"
ALT_DECKKRAFT = 110 / 255                     # so sahen Wasserzeichen ohne Angabe „transparenz“ bisher aus
AUSWASCHEN = 217 / 255                        # „Auswaschen“: 85 % zum Weiß hin


def da(w: dict | None) -> bool:
    """Ob das Wasserzeichen etwas zeigt (Text oder Bild)."""
    return bool(w and ((w.get("text") or "").strip() or w.get("bild")))


def bild_bytes(text: str | None) -> bytes | None:
    """Die Bilddatei aus dem Base64-Text; ``None``, wenn sie fehlt oder kein bekanntes Bildformat ist."""
    try:
        blob = base64.b64decode(text or "")
    except (ValueError, TypeError):
        return None
    return blob if blob and format_erkennen(blob) else None


def deckkraft(w: dict) -> float:
    if "transparenz" not in w:
        return ALT_DECKKRAFT
    return max(0.0, min(1.0, 1.0 - float(w["transparenz"]) / 100.0))


def lage(w: dict, r: Rect, b: float, h: float) -> Point:
    """Mittelpunkt des Wasserzeichens (Breite b, Höhe h) im Seitenrechteck r."""
    mm = lambda k: float(w.get(k, 0)) * PX_JE_MM                                        # noqa: E731
    x = {"links": r.x + mm("h_mm") + b / 2, "rechts": r.right - mm("h_mm") - b / 2}.get(w.get("h", "mitte"), r.x + r.width / 2)
    y = {"oben": r.y + mm("v_mm") + h / 2, "unten": r.bottom - mm("v_mm") - h / 2}.get(w.get("v", "mitte"), r.y + r.height / 2)
    return Point(x, y)


def schrift(engine: TextLayoutEngine, w: dict, r: Rect) -> FontSpec:
    """Schrift des Textwasserzeichens; „automatisch“ füllt die Seite (waagerecht 80 % der Breite, schräg 78 % der Diagonale)."""
    familie = w.get("schrift") or "Liberation Sans"
    pt = float(w.get("groesse_pt", 80) or 0)
    if pt > 0:
        return FontSpec(familie, max(4, int(pt * 96 / 72)) * 72 / 96, 700)
    breite = engine.measure_text(w.get("text") or "", FontSpec(familie, 100 * 72 / 96, 700)) or 1
    laenge = (r.width ** 2 + r.height ** 2) ** 0.5 * 0.78 if w.get("winkel", -45) else r.width * 0.8
    px = max(4, min(int(r.height * 0.4), int(100 * laenge / breite)))
    return FontSpec(familie, px * 72 / 96, 700)


def zeichne(b: RenderTarget, engine: TextLayoutEngine, w: dict | None, r: Rect) -> None:
    """Das Wasserzeichen ``w`` auf die Seite ``r`` (96-dpi-Bildpunkte) zeichnen."""
    if not da(w):
        return
    winkel = float(w.get("winkel", -45) or 0)
    if w.get("bild"):
        blob = bild_bytes(w["bild"])
        if blob is None:
            return
        if w.get("ganzseitig"):                                       # Grafik eines Deckblatts: füllt das ganze Blatt
            b.push_state(opacity=deckkraft(w))
            b.draw_image(blob, r, smooth=True)
            b.pop_state()
            return
        iw, ih = masse(blob) or (100.0, 100.0)
        zoom = float(w.get("zoom", 0) or 0)
        if zoom > 0:
            bw, bh = iw * zoom / 100, ih * zoom / 100
        else:                                                         # automatisch: in die Seite mit 15 % Rand
            f = min(r.width * 0.7 / max(1, iw), r.height * 0.7 / max(1, ih))
            bw, bh = iw * f, ih * f
        mitte = lage(w, r, bw, bh)
        b.push_state(opacity=deckkraft(w), translate=mitte, rotate=winkel)
        b.draw_image(blob, Rect(-bw / 2, -bh / 2, bw, bh), smooth=True, wash=AUSWASCHEN if w.get("auswaschen", True) else 0.0)
        b.pop_state()
        return
    text = w["text"]
    f = schrift(engine, w, r)
    m = engine.font_metrics(f)
    bw, bh = engine.measure_text(text, f), m.ascent + m.descent
    mitte = lage(w, r, bw, bh)
    b.push_state(opacity=deckkraft(w), translate=mitte, rotate=winkel)
    b.draw_text_box(text, Rect(-r.width, -bh / 2, 2 * r.width, bh), f, Style(color=rgba(w.get("farbe") or STANDARD_FARBE)), align="center", wrap=False)
    b.pop_state()
