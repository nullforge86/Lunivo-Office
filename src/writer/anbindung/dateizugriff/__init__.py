"""Tür des Pakets ``writer.anbindung.dateizugriff``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "fremd_geoeffnet": ("anbindung", "fremd_geoeffnet"),
    "pdf_druckrechte": ("anbindung", "pdf_druckrechte"),
    "pdf_kennwort_fehler": ("anbindung", "pdf_kennwort_fehler"),
    "pdf_schreiben": ("anbindung", "pdf_schreiben"),
    "pdf_wahl": ("anbindung", "pdf_wahl"),
    "pdf_wahl_mit": ("anbindung", "pdf_wahl_mit"),
    "sicherungs_ordner": ("anbindung", "sicherungs_ordner"),
    "stand": ("anbindung", "stand"),
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
