"""Tür des Pakets ``framework.anbindung.fund``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Fund": ("anbindung", "Fund"),
    "Verdraengter": ("anbindung", "Verdraengter"),
    "abstimmen": ("anbindung", "abstimmen"),
    "autokorrigiere": ("anbindung", "autokorrigiere"),
    "einsetzen": ("anbindung", "einsetzen"),
    "finde_probleme": ("anbindung", "finde_probleme"),
    "loesen": ("anbindung", "loesen"),
    "markieren": ("anbindung", "markieren"),
    "thema_aufnehmen": ("anbindung", "thema_aufnehmen"),
    "uebernimm_schreibweise": ("anbindung", "uebernimm_schreibweise"),
    "verschieben": ("anbindung", "verschieben"),
    "wort_bekannt": ("anbindung", "wort_bekannt"),
    "wort_muster": ("anbindung", "wort_muster"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "anbindung":
        from . import anbindung as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
