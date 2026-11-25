"""Tür des Pakets ``vcl.qt.rendering.wordart``: alle öffentlichen Namen des Pakets. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen). Gibt es einen Namen in
mehreren Dateien, heißt er hier ``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "EFFEKT": ("texteffekt", "EFFEKT"),
    "KONTUR_ARTEN": ("texteffekt", "KONTUR_ARTEN"),
    "KONTUR_ARTEN_PLUS": ("texteffekt", "KONTUR_ARTEN_PLUS"),
    "KONTUR_FORMEN": ("texteffekt", "KONTUR_FORMEN"),
    "aus_zeichen": ("texteffekt", "aus_zeichen"),
    "form_kachel_icon": ("textfx_vorgaben", "form_kachel_icon"),
    "fuell_pinsel_von": ("textfx", "fuell_pinsel_von"),
    "fx_zeichnen": ("textfx", "fx_zeichnen"),
    "hat_effekt": ("textfx", "hat_effekt"),
    "leuchten_vorgaben": ("textfx", "leuchten_vorgaben"),
    "reflektion_vorgaben": ("textfx", "reflektion_vorgaben"),
    "schatten_vorgaben": ("textfx", "schatten_vorgaben"),
    "strich_setzen": ("texteffekt", "strich_setzen"),
    "text_kachel_icon": ("textfx_vorgaben", "text_kachel_icon"),
    "texteffekt_als_text": ("texteffekt", "als_text"),
    "texteffekt_aus_text": ("texteffekt", "aus_text"),
    "textfx_als_text": ("textfx", "als_text"),
    "textfx_aus_text": ("textfx", "aus_text"),
    "unter_symbol": ("textfx_zeichen", "unter_symbol"),
    "unter_zeichnen": ("textfx_zeichen", "unter_zeichnen"),
    "voreinstellung_icon": ("textfx_vorgaben", "voreinstellung_icon"),
    "vorschau_zeichnen": ("textfx", "vorschau_zeichnen"),
    "wordart_bild": ("wordart_einfuegen", "wordart_bild"),
    "wordart_icon": ("textfx_vorgaben", "wordart_icon"),
    "wordart_vorgaben": ("textfx", "wordart_vorgaben"),
    "wordart_vorlage_bild": ("wordart_einfuegen", "wordart_vorlage_bild"),
    "zu_daten": ("effekt_umwandlung", "zu_daten"),
    "zu_dict": ("effekt_umwandlung", "zu_dict"),
    "zu_zeichen": ("texteffekt", "zu_zeichen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "effekt_umwandlung":
        from . import effekt_umwandlung as _datei
    elif datei == "texteffekt":
        from . import texteffekt as _datei
    elif datei == "textfx":
        from . import textfx as _datei
    elif datei == "textfx_vorgaben":
        from . import textfx_vorgaben as _datei
    elif datei == "textfx_zeichen":
        from . import textfx_zeichen as _datei
    elif datei == "wordart_einfuegen":
        from . import wordart_einfuegen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
