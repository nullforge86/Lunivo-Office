"""Tür des Pakets ``core.formatvorlagen.zeichen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "DESIGNS": ("designs", "DESIGNS"),
    "EFFEKTE": ("designs", "EFFEKTE"),
    "FARBSCHEMEN": ("designs", "FARBSCHEMEN"),
    "FELDER": ("stile", "FELDER"),
    "MAX_BASIS": ("stile", "MAX_BASIS"),
    "NAMEN": ("stile", "NAMEN"),
    "PRAEFIX": ("stile", "PRAEFIX"),
    "SCHRIFTPAARE": ("designs", "SCHRIFTPAARE"),
    "VORGABE": ("stile", "VORGABE"),
    "VORLAGE": ("stile", "VORLAGE"),
    "aendern": ("stile", "aendern"),
    "als_json": ("stile", "als_json"),
    "als_json_neu": ("stile", "als_json_neu"),
    "anlegen": ("stile", "anlegen"),
    "definition": ("stile", "definition"),
    "design": ("designs", "design"),
    "eigene_angaben": ("stile", "eigene_angaben"),
    "ist_eigen": ("stile", "ist_eigen"),
    "key_zu_name": ("stile", "key_zu_name"),
    "laden": ("stile", "laden"),
    "laden_neu": ("stile", "laden_neu"),
    "loeschen": ("stile", "loeschen"),
    "name_zu_key": ("stile", "name_zu_key"),
    "namen": ("stile", "namen"),
    "pruefe_name": ("stile", "pruefe_name"),
    "ueberschrift_farbe": ("designs", "ueberschrift_farbe"),
    "zuruecksetzen": ("stile", "zuruecksetzen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "designs":
        from . import designs as _datei
    elif datei == "stile":
        from . import stile as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
