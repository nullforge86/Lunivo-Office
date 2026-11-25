"""Tür des Pakets ``core.formatvorlagen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "EINGEBAUT": ("formatvorlagen", "EINGEBAUT"),
    "PX_JE_PT": ("formatvorlagen", "PX_JE_PT"),
    "eingebaute_vorlagen": ("formatvorlagen", "eingebaute_vorlagen"),
    "katalog_zu_vorlage": ("katalog", "katalog_zu_vorlage"),
    "ueberschriftsebene": ("formatvorlagen", "ueberschriftsebene"),
    "vorlage_abgleichen": ("katalog", "vorlage_abgleichen"),
    "vorlage_anwenden": ("katalog", "vorlage_anwenden"),
    "vorlage_zu_katalog": ("katalog", "vorlage_zu_katalog"),
    "vorlagenkette": ("formatvorlagen", "vorlagenkette"),
    "werte_aus_auswahl": ("katalog", "werte_aus_auswahl"),
    "wirksames_absatzformat": ("formatvorlagen", "wirksames_absatzformat"),
    "wirksames_zeichenformat": ("formatvorlagen", "wirksames_zeichenformat"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "formatvorlagen":
        from . import formatvorlagen as _datei
    elif datei == "katalog":
        from . import katalog as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
