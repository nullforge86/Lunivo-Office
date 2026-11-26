"""Tür des Pakets ``core.layout.drucklayout.ausgabe.diagramm``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ALT": ("diagrammtypen", "ALT"),
    "BEISPIEL_KATEGORIEN": ("diagrammtypen", "BEISPIEL_KATEGORIEN"),
    "BEISPIEL_REIHEN": ("diagrammtypen", "BEISPIEL_REIHEN"),
    "FARBEN": ("diagrammtypen", "FARBEN"),
    "FX_SCHLUESSEL": ("diagrammformat", "FX_SCHLUESSEL"),
    "KOMBI_TYPEN": ("diagrammtypen", "KOMBI_TYPEN"),
    "NAMEN": ("diagrammtypen", "NAMEN"),
    "PX": ("diagrammformat", "PX"),
    "STANDARD_ELEMENTE": ("diagrammzeichner", "STANDARD_ELEMENTE"),
    "STILE": ("diagrammzeichner_hilfen", "STILE"),
    "STIL_EXTRA": ("diagrammzeichner", "STIL_EXTRA"),
    "TYPEN": ("diagrammtypen", "TYPEN"),
    "VORGABEN": ("diagrammformat", "VORGABEN"),
    "VORLAGEN": ("diagrammtypen", "VORLAGEN"),
    "art": ("diagrammtypen", "art"),
    "beispiel": ("diagrammtypen", "beispiel"),
    "effekt": ("diagrammformat", "effekt"),
    "effekte_hinter": ("diagrammformat", "effekte_hinter"),
    "fuell_dict": ("diagrammformat", "fuell_dict"),
    "fuell_style": ("diagrammformat", "fuell_style"),
    "hat_effekte": ("diagrammformat", "hat_effekte"),
    "hat_linien": ("diagrammtypen", "hat_linien"),
    "hauptfarbe": ("diagrammformat", "hauptfarbe"),
    "ist_keine": ("diagrammformat", "ist_keine"),
    "ist_kreis": ("diagrammtypen", "ist_kreis"),
    "kombi_vorgabe": ("diagrammtypen", "kombi_vorgabe"),
    "linie_stile": ("diagrammformat", "linie_stile"),
    "namen_angewendet": ("diagrammzeichner", "namen_angewendet"),
    "pfeil_zeichnen": ("diagrammformat", "pfeil_zeichnen"),
    "rahmen_zeichnen": ("diagrammformat", "rahmen_zeichnen"),
    "schrift": ("diagrammformat", "schrift"),
    "teil_zeichnen": ("diagrammformat", "teil_zeichnen"),
    "text_zeichnen": ("diagrammformat", "text_zeichnen"),
    "textwinkel": ("diagrammformat", "textwinkel"),
    "zeichne_diagramm": ("diagrammzeichner", "zeichne_diagramm"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "diagrammformat":
        from . import diagrammformat as _datei
    elif datei == "diagrammtypen":
        from . import diagrammtypen as _datei
    elif datei == "diagrammzeichner":
        from . import diagrammzeichner as _datei
    elif datei == "diagrammzeichner_hilfen":
        from . import diagrammzeichner_hilfen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
