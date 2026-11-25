"""Scharfer Text für Rasterflächen: FreeType rastert jede Glyphe in der tatsächlichen Gerätegröße (Zoom mal Bildschirmfaktor) mit leichtem senkrechtem Hinting,
Graustufen-Antialiasing und Viertelpixel waagerecht; geliefert werden Deckungsbilder.

Das Layout bleibt unberührt: Stellen und Vorschübe kommen ungehintet und in Bruchteilen von Bildpunkten aus ``formen``; nur die Darstellung der einzelnen Glyphe wird auf
das Pixelraster des Bildschirms abgestimmt. Die Grundlinie liegt auf einer ganzen Pixelzeile."""
from __future__ import annotations

import math

import freetype

from .formen import forme
from .schrift import Schrift

_LADEN = freetype.FT_LOAD_TARGET_LIGHT | freetype.FT_LOAD_NO_BITMAP | freetype.FT_LOAD_FORCE_AUTOHINT
_VIERTEL = 4                                                   # waagerechte Stellen je Pixel
_MAX_GROESSEN, _MAX_GLYPHEN = 48, 20000
_flaechen: dict[tuple, freetype.Face] = {}
_glyphen: dict[tuple, tuple] = {}
# Deckung leicht anheben: dunkle Schrift auf hellem Grund behält so ihre Strichstärke
_DECKUNG = bytes(min(255, int(255.0 * (i / 255.0) ** 0.8 + 0.5)) for i in range(256))


def _flaeche(s: Schrift, geraete_px: float):
    """Die Schrift, eingestellt auf ``geraete_px`` (Bruchteile von Geräte-Pixeln, nie auf ganze Pixel gerundet)."""
    schluessel = (s.schluessel, round(geraete_px * 64))
    f = _flaechen.get(schluessel)
    if f is None:
        if len(_flaechen) >= _MAX_GROESSEN:
            _flaechen.clear()
            _glyphen.clear()
        f = freetype.Face(s.pfad, s.index)
        f.set_char_size(max(64, round(geraete_px * 64)), 0, 72, 72)
        _flaechen[schluessel] = f
    return f, schluessel


def _glyphe(s: Schrift, geraete_px: float, nummer: int, viertel: int):
    """Deckungsbild einer Glyphe: ``(links, oben, breite, hoehe, zeilen)``; ``oben`` zählt von der Grundlinie nach oben."""
    f, groesse = _flaeche(s, geraete_px)
    schluessel = (groesse, nummer, viertel)
    g = _glyphen.get(schluessel)
    if g is not None:
        return g
    g = (0, 0, 0, 0, b"")
    try:
        f.set_transform(freetype.Matrix(0x10000, 0, 0, 0x10000), freetype.Vector(round(viertel * 64 / _VIERTEL), 0))
        f.load_glyph(nummer, _LADEN)
        f.glyph.render(freetype.FT_RENDER_MODE_LIGHT)
        b = f.glyph.bitmap
        if b.width and b.rows:
            roh = bytes(b.buffer)
            zeilen = b"".join(roh[r * b.pitch:r * b.pitch + b.width] for r in range(b.rows)).translate(_DECKUNG)
            g = (f.glyph.bitmap_left, f.glyph.bitmap_top, b.width, b.rows, zeilen)
    except Exception:                                          # eine nicht lesbare Glyphe bleibt leer
        pass
    if len(_glyphen) >= _MAX_GLYPHEN:
        _glyphen.clear()
    _glyphen[schluessel] = g
    return g


def text_deckung(s: Schrift, text: str, x: float, grundlinie: float, massstab: float) -> list[tuple[int, int, int, int, bytes]]:
    """Die Glyphen des Textes als Deckungsbilder ``(x, y, breite, hoehe, bytes)`` in Geräte-Pixeln. ``x`` und ``grundlinie`` sind Geräte-Koordinaten (y nach unten),
    ``massstab`` sind Geräte-Pixel je Bildpunkt des Kerns."""
    if not text:
        return []
    k = s.px / s.upem * massstab                               # Schrifteinheiten → Geräte-Pixel
    geraete_px = s.px * massstab
    zeile = round(grundlinie)
    stelle, bilder = 0, []
    for g in forme(s, text):
        gx = x + (stelle + g.dx) * k
        stelle += g.vorschub
        ganz = math.floor(gx)
        viertel = int((gx - ganz) * _VIERTEL + 0.5)
        if viertel >= _VIERTEL:
            ganz, viertel = ganz + 1, 0
        links, oben, breite, hoehe, zeilen = _glyphe(s, geraete_px, g.nummer, viertel)
        if breite:
            bilder.append((ganz + links, zeile - round(g.dy * k) - oben, breite, hoehe, zeilen))
    return bilder
