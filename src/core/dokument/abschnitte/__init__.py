"""Tür des Pakets ``core.dokument.abschnitte``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ARBEIT": ("deckblatt_vorlagen", "ARBEIT"),
    "ARTIKEL": ("deckblatt_vorlagen", "ARTIKEL"),
    "AbschnittTeil": ("abschnittsbearbeitung", "AbschnittTeil"),
    "FIRMA": ("deckblatt_vorlagen", "FIRMA"),
    "Feld": ("deckblatt_vorlagen", "Feld"),
    "GESTALTUNGEN": ("deckblatt_vorlagen", "GESTALTUNGEN"),
    "Gestaltung": ("deckblatt_vorlagen", "Gestaltung"),
    "HeaderFooter": ("seite", "HeaderFooter"),
    "KOPF_FUSS": ("abschnittsbearbeitung", "KOPF_FUSS"),
    "LEBENSLAUF": ("deckblatt_vorlagen", "LEBENSLAUF"),
    "NAMEN": ("deckblatt_vorlagen", "NAMEN"),
    "PAPER_MM": ("seite", "PAPER_MM"),
    "PageSettings": ("seite", "PageSettings"),
    "SERIF": ("deckblatt_vorlagen", "SERIF"),
    "entfernen": ("deckblatt_vorlagen", "entfernen"),
    "gestaltung": ("deckblatt_vorlagen", "gestaltung"),
    "grafik": ("deckblatt_vorlagen", "grafik"),
    "hat_deckblatt": ("deckblatt_vorlagen", "hat_deckblatt"),
    "zeichnen_mit": ("deckblatt_vorlagen", "zeichnen_mit"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "abschnittsbearbeitung":
        from . import abschnittsbearbeitung as _datei
    elif datei == "deckblatt_vorlagen":
        from . import deckblatt_vorlagen as _datei
    elif datei == "seite":
        from . import seite as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
