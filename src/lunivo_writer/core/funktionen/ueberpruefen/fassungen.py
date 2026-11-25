"""Fassungen eines Dokuments mit verfolgten Änderungen, für die Anzeige „Original“: eine Kopie, in der jede Einfügung fehlt und jede
Löschung wieder normaler Text ist. Das Dokument selbst bleibt unverändert. Keine Oberfläche, kein Qt.

    original(dok)      → Kopie wie vor den Änderungen
    bearbeiter(dok)    → Namen aller Bearbeiter mit Änderungen (sortiert)
    zeiten(dok)        → Tage (JJJJ-MM-TT) mit Änderungen (sortiert)
"""
from __future__ import annotations

import copy

from lunivo_writer.core.dokument.dokument import Dokument
from lunivo_writer.core.bearbeitung import Bearbeitungssitzung


def _stuecke(dok: Dokument) -> list[tuple[str, str, str]]:
    """(Art, Autor, Datum) jedes Stücks mit Änderungsmarke."""
    return [(x.format["aenderung"], x.format.get("autor", ""), x.format.get("datum", "")) for a in dok.absaetze() for x in a.inhalte if "aenderung" in x.format]


def original(dok: Dokument) -> Dokument:
    """Die Kopie des Dokuments, in der alle verfolgten Änderungen abgelehnt sind (Einfügungen fehlen, Löschungen stehen wieder da)."""
    kopie = copy.deepcopy(dok)
    Bearbeitungssitzung(kopie).aenderungen_ablehnen()
    return kopie


def bearbeiter(dok: Dokument) -> list[str]:
    return sorted({a for _art, a, _z in _stuecke(dok) if a})


def zeiten(dok: Dokument) -> list[str]:
    return sorted({z[:10] for _art, _a, z in _stuecke(dok) if z})
