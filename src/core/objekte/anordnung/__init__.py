"""Tür des Pakets ``core.objekte.anordnung``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "Anchor": ("objekte_hilfen", "Anchor"),
    "FillStyle": ("objekte_hilfen", "FillStyle"),
    "ImageObject": ("image_object", "ImageObject"),
    "StrokeStyle": ("objekte_hilfen", "StrokeStyle"),
    "Transform": ("objekte_hilfen", "Transform"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "image_object":
        from . import image_object as _datei
    elif datei == "objekte_hilfen":
        from . import objekte_hilfen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
