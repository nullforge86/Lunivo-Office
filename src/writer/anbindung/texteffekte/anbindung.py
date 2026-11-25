"""Anbindung der Oberfläche an ``core.layout.drucklayout.ausgabe.text.texteffekte`` über ``framework.anbindung.texteffekte``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import framework.anbindung.texteffekte as _fw
from writer.werte import eigene_kopie


def pfad_verformen(ops: Sequence, fx: Mapping | None) -> Sequence:
    """Die Glyphenpfade nach ``warp`` (Transformieren) und ``text_3d`` (3D-Drehung um X, Y, Z mit Perspektive); ohne beides unverändert."""
    return eigene_kopie(_fw.pfad_verformen(ops, fx))
