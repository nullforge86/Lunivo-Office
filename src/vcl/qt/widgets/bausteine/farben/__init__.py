"""Farben der Oberfläche.

Tür des Pakets: Aufrufer außerhalb importieren die hier genannten Farben von hier. Die Datei wird erst beim ersten Zugriff geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "KOPFFUSS_AUSWAHL": ("farben", "KOPFFUSS_AUSWAHL"),
    "KOPFFUSS_AUSWAHL_TEXT": ("farben", "KOPFFUSS_AUSWAHL_TEXT"),
    "KOPFFUSS_ETIKETT_GRUND": ("farben", "KOPFFUSS_ETIKETT_GRUND"),
    "KOPFFUSS_ETIKETT_TEXT": ("farben", "KOPFFUSS_ETIKETT_TEXT"),
    "KOPFFUSS_FELDGRUND": ("farben", "KOPFFUSS_FELDGRUND"),
    "KOPFFUSS_KNOPF_TEXT": ("farben", "KOPFFUSS_KNOPF_TEXT"),
    "KOPFFUSS_PAPIER": ("farben", "KOPFFUSS_PAPIER"),
    "papierfeld": ("darstellung", "papierfeld"),
    "papierleiste": ("darstellung", "papierleiste"),
    "papierpanel": ("darstellung", "papierpanel"),
    "KOPFFUSS_RAHMEN": ("farben", "KOPFFUSS_RAHMEN"),
    "KOPFFUSS_TEXT": ("farben", "KOPFFUSS_TEXT"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "farben":
        from . import farben as _datei
    elif datei == "darstellung":
        from . import darstellung as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
