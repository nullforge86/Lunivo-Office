"""Tür des Pakets ``writer.serienbriefwerkzeuge``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "adressblock_einfuegen": ("sendungen", "adressblock_einfuegen"),
    "etiketten_aufbauen": ("sendungen", "etiketten_aufbauen"),
    "naechster_datensatz_einfuegen": ("sendungen", "naechster_datensatz_einfuegen"),
    "seriendruckfeld_einfuegen": ("sendungen", "seriendruckfeld_einfuegen"),
    "seriendruckfelder_hervorheben": ("sendungen", "seriendruckfelder_hervorheben"),
    "seriendruckfelder_im_text": ("sendungen", "seriendruckfelder_im_text"),
    "seriendruckregel_einfuegen": ("sendungen", "seriendruckregel_einfuegen"),
    "umschlag_aufbauen": ("sendungen", "umschlag_aufbauen"),
    "zuordenbare_seriendruckfelder": ("sendungen", "zuordenbare_seriendruckfelder"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "sendungen":
        from . import sendungen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
