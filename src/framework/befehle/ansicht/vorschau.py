"""Vorschau im Dokumentfenster: abgeleitete Fassungen eines Dokuments als Nebendokument. Die Oberfläche bekommt nur die Kennung."""
from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence

from framework.sitzungen import sitzung as _steuerung


def vorschau_kopie(kennung: int) -> int:
    """Eine unabhängige Kopie des Dokuments als Nebendokument; → dessen Kennung."""
    return _steuerung._neben(copy.deepcopy(_steuerung._sitzungen[kennung].sitzung.dokument))


def vorschau_brief(kennung: int, satz: Mapping[str, str] | Sequence[Mapping[str, str]]) -> int:
    """Der Serienbrief des Dokuments für einen Datensatz (oder die Sätze eines Blattes) als Nebendokument; → dessen Kennung."""
    from framework.serienbriefe.erstellung import brief_fuer
    return _steuerung._neben(brief_fuer(_steuerung._sitzungen[kennung].sitzung.dokument, satz))


def vorschau_schliessen(kennung: int) -> None:
    """Das Nebendokument einer Vorschau wieder freigeben."""
    _steuerung.neben_schliessen(kennung)
