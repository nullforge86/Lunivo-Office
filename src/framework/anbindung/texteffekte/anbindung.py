"""Anbindung an ``core.layout.drucklayout.ausgabe.text.texteffekte``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import core.layout.drucklayout.ausgabe.text as _k
from framework.anbindung import fest


def pfad_verformen(ops: Sequence, fx: Mapping | None) -> Sequence:
    """Die Glyphenpfade nach ``warp`` (Transformieren) und ``text_3d`` (3D-Drehung um X, Y, Z mit Perspektive); ohne beides unverändert."""
    return fest(_k.pfad_verformen(ops, fx))
