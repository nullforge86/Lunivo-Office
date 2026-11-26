"""Tür des Pakets ``framework.dokumentverwaltung.integrationen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "LanguageToolFehler": ("languagetool", "LanguageToolFehler"),
    "jar_finden": ("languagetool", "jar_finden"),
    "ordner": ("languagetool", "ordner"),
    "pruefe": ("languagetool", "pruefe"),
    "verfuegbar": ("languagetool", "verfuegbar"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "languagetool":
        from . import languagetool as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
