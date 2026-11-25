"""Anbindung der Oberfläche an ``core.dokument.vorlagen`` über ``framework.anbindung.vorlagen``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import framework.anbindung.vorlagen as _fw
from writer.werte import eigene_kopie


def muster() -> Sequence[Mapping]:
    return eigene_kopie(_fw.muster())


def rubriken(ordner: str) -> tuple[Mapping[str, Sequence[str]], Sequence[str]]:
    """Der Vorlagenordner nach Rubriken: jeder Unterordner ist eine Rubrik (Name → Dateien); lose Dateien liegen im Ordner selbst."""
    return eigene_kopie(_fw.rubriken(ordner))
