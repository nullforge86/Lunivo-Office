"""Tür des Pakets ``framework.befehle.ueberpruefen``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ANZEIGEN": ("anzeige", "ANZEIGEN"),
    "AenderungenBefehle": ("aenderungen", "AenderungenBefehle"),
    "AnzeigeBefehle": ("anzeige", "AnzeigeBefehle"),
    "BALLONS": ("einstellungen", "BALLONS"),
    "BALLON_WERTE": ("einstellungen", "BALLON_WERTE"),
    "EntscheidenZustand": ("typen", "EntscheidenZustand"),
    "KommentareBefehle": ("kommentare", "KommentareBefehle"),
    "MarkupBefehle": ("markup", "MarkupBefehle"),
    "MarkupFilter": ("typen", "MarkupFilter"),
    "NotenBefehle": ("noten", "NotenBefehle"),
    "ORIGINAL": ("anzeige", "ORIGINAL"),
    "SCHUTZ_HINWEIS": ("schutz", "SCHUTZ_HINWEIS"),
    "ballons": ("einstellungen", "ballons"),
    "ballons_setzen": ("einstellungen", "ballons_setzen"),
    "ist_geschuetzt": ("schutz", "ist_geschuetzt"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "aenderungen":
        from . import aenderungen as _datei
    elif datei == "anzeige":
        from . import anzeige as _datei
    elif datei == "einstellungen":
        from . import einstellungen as _datei
    elif datei == "kommentare":
        from . import kommentare as _datei
    elif datei == "markup":
        from . import markup as _datei
    elif datei == "noten":
        from . import noten as _datei
    elif datei == "schutz":
        from . import schutz as _datei
    elif datei == "typen":
        from . import typen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
