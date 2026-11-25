"""Tür des Pakets ``writer.vorlagenkatalog``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "aendern": ("katalog", "aendern"),
    "als_json": ("katalog", "als_json"),
    "als_json_neu": ("katalog", "als_json_neu"),
    "anlegen": ("katalog", "anlegen"),
    "definition": ("katalog", "definition"),
    "design": ("katalog", "design"),
    "designs": ("katalog", "designs"),
    "effekte": ("katalog", "effekte"),
    "eigene_angaben": ("katalog", "eigene_angaben"),
    "eingebaute_namen": ("katalog", "eingebaute_namen"),
    "farbschemen": ("katalog", "farbschemen"),
    "ist_eigen": ("katalog", "ist_eigen"),
    "laden": ("katalog", "laden"),
    "laden_neu": ("katalog", "laden_neu"),
    "loeschen": ("katalog", "loeschen"),
    "namen": ("katalog", "namen"),
    "pruefe_name": ("katalog", "pruefe_name"),
    "schriftpaare": ("katalog", "schriftpaare"),
    "ueberschrift_farbe": ("katalog", "ueberschrift_farbe"),
    "vorlage": ("katalog", "vorlage"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "katalog":
        from . import katalog as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
