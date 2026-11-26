"""Vorschau im Dokumentfenster: abgeleitete Fassungen eines Dokuments als Nebendokument des Frameworks; die Oberfläche kennt nur die Kennung."""
from __future__ import annotations

from framework.befehle import ansicht as _fw


def vorschau_kopie(kennung: int) -> int:
    """Eine unabhängige Kopie des Dokuments als Nebendokument; → dessen Kennung."""
    return _fw.vorschau_kopie(kennung)


def vorschau_brief(kennung: int, satz) -> int:
    """Der Serienbrief des Dokuments für einen Datensatz (oder die Sätze eines Blattes) als Nebendokument; → dessen Kennung."""
    return _fw.vorschau_brief(kennung, satz)


def vorschau_schliessen(kennung: int) -> None:
    """Das Nebendokument einer Vorschau wieder freigeben."""
    _fw.vorschau_schliessen(kennung)
