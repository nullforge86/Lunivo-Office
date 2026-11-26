"""Abstände, Maße und Raster der Oberfläche.

Tür des Pakets: Aufrufer außerhalb importieren die hier genannten Maße von hier. Die Datei wird erst beim ersten Zugriff geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "BLATTSCHATTEN_VERSATZ": ("mass", "BLATTSCHATTEN_VERSATZ"),
    "BLATTSCHATTEN_WEITE": ("mass", "BLATTSCHATTEN_WEITE"),
    "LEERZUSTAND_ICON": ("mass", "LEERZUSTAND_ICON"),
    "LINEAL_ABSTAND": ("mass", "LINEAL_ABSTAND"),
    "KOPFFUSS_BILD_HOEHE_MM": ("mass", "KOPFFUSS_BILD_HOEHE_MM"),
    "KOPFFUSS_ETIKETT_ABSTAND": ("mass", "KOPFFUSS_ETIKETT_ABSTAND"),
    "KOPFFUSS_ETIKETT_RAND": ("mass", "KOPFFUSS_ETIKETT_RAND"),
    "KOPFFUSS_FELD_HOEHE_MM": ("mass", "KOPFFUSS_FELD_HOEHE_MM"),
    "KOPFFUSS_FUSS_VON_UNTEN_MM": ("mass", "KOPFFUSS_FUSS_VON_UNTEN_MM"),
    "KOPFFUSS_HINWEIS_MS": ("mass", "KOPFFUSS_HINWEIS_MS"),
    "KOPFFUSS_KACHEL": ("mass", "KOPFFUSS_KACHEL"),
    "KOPFFUSS_KACHEL_BILD": ("mass", "KOPFFUSS_KACHEL_BILD"),
    "KOPFFUSS_KOPF_OBEN_MM": ("mass", "KOPFFUSS_KOPF_OBEN_MM"),
    "KOPFFUSS_LEISTE_ABSTAND": ("mass", "KOPFFUSS_LEISTE_ABSTAND"),
    "KOPFFUSS_NUMMER_MAX": ("mass", "KOPFFUSS_NUMMER_MAX"),
    "KOPFFUSS_LINIE_ABSTAND": ("mass", "KOPFFUSS_LINIE_ABSTAND"),
    "KOPFFUSS_LINIE_HOEHE": ("mass", "KOPFFUSS_LINIE_HOEHE"),
    "KOPFFUSS_SCHRIFT_PT": ("mass", "KOPFFUSS_SCHRIFT_PT"),
    "KOPFFUSS_SCHRIFT_PX": ("mass", "KOPFFUSS_SCHRIFT_PX"),
    "KOPFFUSS_SCHRIFT_PX_MIN": ("mass", "KOPFFUSS_SCHRIFT_PX_MIN"),
    "KOPFFUSS_SPEICHERN_MS": ("mass", "KOPFFUSS_SPEICHERN_MS"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "mass":
        from . import mass as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
