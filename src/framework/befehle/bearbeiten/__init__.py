"""Tür des Pakets ``framework.befehle.bearbeiten``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "BearbeitenBefehle": ("befehle", "BearbeitenBefehle"),
    "ELEMENTE": ("gehe_zu", "ELEMENTE"),
    "eingabe_titel": ("gehe_zu", "eingabe_titel"),
    "formatvorlage_abgleichen": ("formatvorlagen", "formatvorlage_abgleichen"),
    "formatvorlage_aus_auswahl": ("formatvorlagen", "formatvorlage_aus_auswahl"),
    "formatvorlage_anwenden": ("formatvorlagen", "formatvorlage_anwenden"),
    "gehe_zu_element": ("gehe_zu", "gehe_zu_element"),
    "hat_elemente": ("gehe_zu", "hat_elemente"),
    "tabs_als_text": ("formatvorlagen", "tabs_als_text"),
    "tabs_aus_text": ("formatvorlagen", "tabs_aus_text"),
    "MENUE": ("wortextras", "MENUE"),
    "wortextra_ausfuehren": ("wortextras", "wortextra_ausfuehren"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "befehle":
        from . import befehle as _datei
    elif datei == "formatvorlagen":
        from . import formatvorlagen as _datei
    elif datei == "gehe_zu":
        from . import gehe_zu as _datei
    elif datei == "wortextras":
        from . import wortextras as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
