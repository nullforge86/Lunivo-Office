"""Eine geladene Schrift in einer Größe: HarfBuzz-Font zum Formen, FreeType-Schrift für Konturen und Maße, dazu die Zeilenmaße.

Maße sind Bildpunkte bei 96 dpi wie im übrigen Kern. Die Größe gilt in Bruchteilen von Bildpunkten (1/64, wie in Word und LibreOffice): 11 pt sind 14,67 px, nicht 15 —
ganze Bildpunkte machten den Text rund 2 % breiter. Alles wird ungehintet und mit Bruchteilen gemessen."""
from __future__ import annotations

from dataclasses import dataclass

import freetype
import uharfbuzz as hb

from core.formatierung.schrift.datenbank import Schnitt

PX_JE_PT = 96.0 / 72.0


@dataclass
class Schrift:
    hb_font: hb.Font
    upem: int
    ascent: float
    descent: float
    line_spacing: float
    px: float
    ft_face: object
    pfad: str
    index: int

    @property
    def schluessel(self) -> tuple[str, int]:
        """Die Schriftdatei samt Schnitt: unabhängig von der Größe (Formen und Konturen gelten in Schrifteinheiten)."""
        return self.pfad, self.index


def groesse_px(size_pt: float) -> float:
    """Schriftgröße in Bildpunkten, auf 1/64 genau."""
    return max(1.0, round(size_pt * PX_JE_PT * 64.0) / 64.0)


def laden(schnitt: Schnitt, size_pt: float, hb_flaechen: dict) -> Schrift:
    """Die Schrift ``schnitt`` in der Größe ``size_pt``; ``hb_flaechen`` gibt die HarfBuzz-Flächen wieder frei (eine je Datei und Schnitt)."""
    schluessel = (schnitt.pfad, schnitt.index)
    flaeche = hb_flaechen.get(schluessel)
    if flaeche is None:
        with open(schnitt.pfad, "rb") as f:
            flaeche = hb.Face(hb.Blob(f.read()), schnitt.index)
        hb_flaechen[schluessel] = flaeche
    px = groesse_px(size_pt)
    ft = freetype.Face(schnitt.pfad, schnitt.index)
    upem = ft.units_per_EM or 1000
    k = px / upem
    ascent, descent = ft.ascender * k, -ft.descender * k             # Zeilenabstand = Ober- + Unterlänge; der Zusatz ``lineGap`` der Schrift bleibt weg
    font = hb.Font(flaeche)
    font.scale = (upem, upem)
    return Schrift(font, upem, ascent, descent, ascent + descent, px, ft, schnitt.pfad, schnitt.index)
