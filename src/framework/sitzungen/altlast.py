"""Übergangszugang (vom Eigentümer freigegeben und gezählt, Regel ``altlast_sitzungszugang``): nur ``kern_editor.py`` darf ihn nutzen."""
from __future__ import annotations

from dataclasses import dataclass

from core.bearbeitung import Bearbeitungssitzung
from framework.sitzungen.dokumentsteuerung import sitzung as _steuerung


@dataclass(frozen=True)
class EditorZugang:
    sitzung: Bearbeitungssitzung
    meta: dict
    page: object


def zugang_fuer_editor(kennung: int) -> EditorZugang:
    """Die vorhandenen Objekte der Sitzung (keine Kopien); erzeugt nie eine neue."""
    satz = _steuerung._sitzungen[kennung]
    return EditorZugang(satz.sitzung, satz.meta, satz.page)
