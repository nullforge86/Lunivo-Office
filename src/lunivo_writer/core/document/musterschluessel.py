"""Die Schlüssel der Füllmuster (Prozentraster und Linienmuster) und ihre Namen in DOCX/OOXML — Qt-frei, für Oberfläche, DOCX und ODT gemeinsam.

Ein Muster ist ein Schlüssel (``pct25``, ``dunkel_h`` …); ``rein`` ist die volle Farbe. In einer Absatzschattierung (``w:shd``) heißen die Werte ``pct25``,
``horzStripe`` …; in einer Mustervorgabe einer Form (``a:pattFill``) ``pct25``, ``dkHorz`` …: ``OOXML_SHD`` und ``OOXML_PATT`` halten beide.
"""
from __future__ import annotations

PROZENT = (5, 10, 12.5, 15, 20, 25, 30, 35, 37.5, 40, 45, 50, 55, 60, 62.5, 65, 70, 75, 80, 85, 87.5, 90, 95)
LINIEN = (("dunkel_h", "Dunkle horizontale Linie", "horzStripe"), ("dunkel_v", "Dunkle vertikale Linie", "vertStripe"),
          ("dunkel_ab", "Dunkel abwärts", "diagStripe"), ("dunkel_auf", "Dunkel aufwärts", "reverseDiagStripe"),
          ("dunkel_raster", "Dunkler Raster", "horzCross"), ("dunkel_karo", "Dunkel Karo", "diagCross"),
          ("hell_h", "Helle horizontale Linie", "thinHorzStripe"), ("hell_v", "Helle vertikale Linie", "thinVertStripe"),
          ("hell_ab", "Hell abwärts", "thinDiagStripe"), ("hell_auf", "Hell aufwärts", "thinReverseDiagStripe"),
          ("hell_raster", "Heller Raster", "thinHorzCross"), ("hell_karo", "Hell Karo", "thinDiagCross"))


def _pct_name(p: float) -> str:
    return f"{p:g}".replace(".", ",") + "%"


# (Schlüssel, Anzeigename, OOXML-Wert der Absatzschattierung) — in der Reihenfolge der Auswahlliste
MUSTER: list[tuple[str, str, str]] = (
    [("loeschen", "Löschen", "clear"), ("rein", "Rein(100%)", "solid")]
    + [(f"pct{p:g}".replace(".", "_"), _pct_name(p), f"pct{int(p)}") for p in PROZENT]
    + list(LINIEN)
)

# Mustervorgabe einer Form (a:pattFill/@prst) ↔ Schlüssel. Nicht jedes OOXML-Muster hat ein Gegenstück: das nächstliegende Raster- oder Linienmuster steht dann stellvertretend.
OOXML_PATT = {"pct5": "pct5", "pct10": "pct10", "pct20": "pct20", "pct25": "pct25", "pct30": "pct30", "pct40": "pct40", "pct50": "pct50", "pct60": "pct60",
              "pct70": "pct70", "pct75": "pct75", "pct80": "pct80", "pct90": "pct90",
              "horz": "hell_h", "ltHorz": "hell_h", "narHorz": "hell_h", "dashHorz": "hell_h", "dkHorz": "dunkel_h",
              "vert": "hell_v", "ltVert": "hell_v", "narVert": "hell_v", "dashVert": "hell_v", "dkVert": "dunkel_v",
              "dnDiag": "dunkel_ab", "ltDnDiag": "hell_ab", "dkDnDiag": "dunkel_ab", "wdDnDiag": "dunkel_ab", "dashDnDiag": "hell_ab",
              "upDiag": "dunkel_auf", "ltUpDiag": "hell_auf", "dkUpDiag": "dunkel_auf", "wdUpDiag": "dunkel_auf", "dashUpDiag": "hell_auf",
              "cross": "dunkel_raster", "lgGrid": "dunkel_raster", "smGrid": "hell_raster", "dotGrid": "hell_raster",
              "diagCross": "dunkel_karo", "smCheck": "hell_karo", "lgCheck": "dunkel_karo", "trellis": "hell_karo", "plaid": "dunkel_karo",
              "smConfetti": "pct25", "lgConfetti": "pct40", "horzBrick": "dunkel_raster", "diagBrick": "dunkel_karo", "solidDmnd": "dunkel_karo",
              "openDmnd": "hell_karo", "dotDmnd": "hell_karo", "sphere": "pct50", "weave": "dunkel_karo", "divot": "pct40", "shingle": "dunkel_ab",
              "wave": "hell_h", "zigZag": "hell_h"}
_PATT_AUS = {"hell_h": "ltHorz", "hell_v": "ltVert", "hell_ab": "ltDnDiag", "hell_auf": "ltUpDiag", "hell_raster": "smGrid", "hell_karo": "smCheck",
             "dunkel_h": "dkHorz", "dunkel_v": "dkVert", "dunkel_ab": "dkDnDiag", "dunkel_auf": "dkUpDiag", "dunkel_raster": "cross", "dunkel_karo": "diagCross"}

OOXML_SHD = {k: o for k, _n, o in MUSTER}
VON_OOXML_SHD = {o: k for k, _n, o in MUSTER}


def patt_von_schluessel(schluessel: str) -> str:
    """Der Name der Mustervorgabe (``a:pattFill/@prst``) zu einem Schlüssel; Prozentraster behalten ihren Namen (``pct25_5`` → ``pct25``)."""
    if schluessel in _PATT_AUS:
        return _PATT_AUS[schluessel]
    if schluessel.startswith("pct"):
        return "pct" + str(int(float(schluessel[3:].replace("_", "."))))
    return "pct50"


def schluessel_von_patt(prst: str | None) -> str:
    return OOXML_PATT.get(prst or "", "pct50")
