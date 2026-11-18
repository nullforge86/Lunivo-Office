"""Eine geladene Schrift (HarfBuzz-Font samt Maßen) der Textsatz-Engine."""
from __future__ import annotations

from dataclasses import dataclass

import uharfbuzz as hb

PX_JE_PT = 96.0 / 72.0


@dataclass
class Schrift:
    hb_font: hb.Font
    upem: int
    ascent: float
    descent: float
    line_spacing: float
    px: float
