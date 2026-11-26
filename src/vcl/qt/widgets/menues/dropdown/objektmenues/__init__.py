"""Unterpaket ``objektmenues`` von ``vcl.qt.widgets.menues.dropdown``. Tür des Pakets: Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen (keine zusätzlichen Importzyklen). Die Namen heißen hier
``<datei>_<name>`` ohne die Endung ``_menues`` der Datei."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "smartart_form_menue": ("smartart_menues", "form_menue"),
    "smartart_hierarchie_menue": ("smartart_menues", "hierarchie_menue"),
    "smartart_layout_menue": ("smartart_menues", "layout_menue"),
    "smartart_level_menue": ("smartart_menues", "level_menue"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "smartart_menues":
        from . import smartart_menues as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
