"""Anbindung an ``core.layout.drucklayout.ausgabe.seite.seitenrahmen``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Mapping

import core.layout.drucklayout.ausgabe.seite as _k
from framework.anbindung import fest


def abstaende_pt(b: Mapping) -> tuple[float, float, float, float]:
    """(oben, unten, links, rechts) in pt."""
    return fest(_k.abstaende_pt(b))
