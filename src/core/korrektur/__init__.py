"""Tür des Pakets ``core.korrektur``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ARTEN": ("korrektur", "ARTEN"),
    "ART_RANG": ("fund", "ART_RANG"),
    "FundFehler": ("korrektur", "FundFehler"),
    "MAX_ANTEIL": ("inkrement", "MAX_ANTEIL"),
    "MIN_ZEICHEN": ("inkrement", "MIN_ZEICHEN"),
    "ProofingIssue": ("korrektur", "ProofingIssue"),
    "QUELLEN": ("korrektur", "QUELLEN"),
    "QUELLE_RANG": ("fund", "QUELLE_RANG"),
    "SICHERHEIT_ABSAETZE": ("inkrement", "SICHERHEIT_ABSAETZE"),
    "STANDARD": ("fund", "STANDARD"),
    "Verdraengt": ("korrektur", "Verdraengt"),
    "abstimmen": ("fund", "abstimmen"),
    "bereinigen": ("korrektur", "bereinigen"),
    "einsetzen": ("inkrement", "einsetzen"),
    "klemmen": ("fund", "klemmen"),
    "loesen": ("fund", "loesen"),
    "lohnt": ("inkrement", "lohnt"),
    "markieren": ("fund", "markieren"),
    "pruefbereich": ("inkrement", "pruefbereich"),
    "schmutz_abbilden": ("inkrement", "schmutz_abbilden"),
    "verschieben": ("inkrement", "verschieben"),
    "zeige_leer": ("korrektur", "zeige_leer"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "fund":
        from . import fund as _datei
    elif datei == "inkrement":
        from . import inkrement as _datei
    elif datei == "korrektur":
        from . import korrektur as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
