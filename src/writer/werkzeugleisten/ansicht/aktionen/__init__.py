"""Tür des Pakets ``writer.werkzeugleisten.ansicht.aktionen``: öffentliche Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AnsichtswahlAktionen": ("ansichtswahl_aktionen", "AnsichtswahlAktionen"),
    "FensterAktionen": ("fenster_aktionen", "FensterAktionen"),
    "LayoutAktionen": ("layout_aktionen", "LayoutAktionen"),
    "LesenAktionen": ("lesen_aktionen", "LesenAktionen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "ansichtswahl_aktionen":
        from . import ansichtswahl_aktionen as _datei
    elif datei == "fenster_aktionen":
        from . import fenster_aktionen as _datei
    elif datei == "layout_aktionen":
        from . import layout_aktionen as _datei
    elif datei == "lesen_aktionen":
        from . import lesen_aktionen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
