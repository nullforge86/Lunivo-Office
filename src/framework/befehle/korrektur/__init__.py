"""Tür des Pakets ``framework.befehle.korrektur``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "KONSENS_GEGENPROBE": ("einstellungen", "KONSENS_GEGENPROBE"),
    "KorrekturEinstellungenAnbieter": ("anbieter", "KorrekturEinstellungenAnbieter"),
    "PRUEFER_VORSILBE": ("einstellungen", "PRUEFER_VORSILBE"),
    "PRUEFSPRACHE": ("einstellungen", "PRUEFSPRACHE"),
    "SCHALTER_VORSILBE": ("einstellungen", "SCHALTER_VORSILBE"),
    "THEMA": ("einstellungen", "THEMA"),
    "VORGABEN": ("einstellungen", "VORGABEN"),
    "VORSCHLAEGE": ("einstellungen", "VORSCHLAEGE"),
    "konsens_gegenprobe": ("einstellungen", "konsens_gegenprobe"),
    "pruefer_aktiv": ("einstellungen", "pruefer_aktiv"),
    "pruefsprache": ("einstellungen", "pruefsprache"),
    "pruefsprache_setzen": ("einstellungen", "pruefsprache_setzen"),
    "schalter": ("einstellungen", "schalter"),
    "schalter_setzen": ("einstellungen", "schalter_setzen"),
    "thema": ("einstellungen", "thema"),
    "thema_setzen": ("einstellungen", "thema_setzen"),
    "vorschlaege_anzeigen": ("einstellungen", "vorschlaege_anzeigen"),
    "vorschlaege_fuer": ("vorschlaege", "vorschlaege_fuer"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "anbieter":
        from . import anbieter as _datei
    elif datei == "einstellungen":
        from . import einstellungen as _datei
    elif datei == "vorschlaege":
        from . import vorschlaege as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
