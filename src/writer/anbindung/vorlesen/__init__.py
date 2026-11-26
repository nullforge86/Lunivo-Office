"""Tür des Pakets ``writer.anbindung.vorlesen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Vorlesefehler": ("anbindung", "Vorlesefehler"),
    "beenden": ("anbindung", "beenden"),
    "einstellung_stimme": ("anbindung", "einstellung_stimme"),
    "einstellung_tempo": ("anbindung", "einstellung_tempo"),
    "lies_vor": ("anbindung", "lies_vor"),
    "piper_da": ("anbindung", "piper_da"),
    "piper_programm": ("anbindung", "piper_programm"),
    "piper_stimmen": ("anbindung", "piper_stimmen"),
    "stimmen": ("anbindung", "stimmen"),
    "tempo_grenzen": ("anbindung", "tempo_grenzen"),
    "verfuegbar": ("anbindung", "verfuegbar"),
    "vorlesetext": ("anbindung", "vorlesetext"),
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
