"""Tür des Pakets ``core.tabellen.modell``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AUSSEN": ("tabellenzustand", "AUSSEN"),
    "EINZELZELLE_GANZ": ("tabellenzustand", "EINZELZELLE_GANZ"),
    "GANZE_TABELLE": ("tabellenzustand", "GANZE_TABELLE"),
    "MEHRERE_ZELLEN": ("tabellenzustand", "MEHRERE_ZELLEN"),
    "NUR_LESEN": ("tabellenzustand", "NUR_LESEN"),
    "SCHNELLTABELLEN": ("tabelle_einfuegen", "SCHNELLTABELLEN"),
    "TEXT_IN_ZELLE": ("tabellenzustand", "TEXT_IN_ZELLE"),
    "TRENNER": ("tabelle_text", "TRENNER"),
    "TabellenTeil": ("tabellenbearbeitung", "TabellenTeil"),
    "VORGABE": ("tabelleneigenschaften", "VORGABE"),
    "abgleichen": ("tabellenbearbeitung", "abgleichen"),
    "gedreht": ("tabellenbearbeitung", "gedreht"),
    "schnelltabelle": ("tabelle_einfuegen", "schnelltabelle"),
    "tabellenmodus": ("tabellenzustand", "tabellenmodus"),
    "zellen": ("tabelle_text", "zellen"),
    "zustand": ("tabellenzustand", "zustand"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "tabelle_einfuegen":
        from . import tabelle_einfuegen as _datei
    elif datei == "tabelle_text":
        from . import tabelle_text as _datei
    elif datei == "tabellenbearbeitung":
        from . import tabellenbearbeitung as _datei
    elif datei == "tabelleneigenschaften":
        from . import tabelleneigenschaften as _datei
    elif datei == "tabellenzustand":
        from . import tabellenzustand as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
