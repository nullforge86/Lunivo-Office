"""Tür des Pakets ``framework.dokumentverwaltung.dokumentpflege``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "EINSTELLUNG_STIMME": ("vorlesen", "EINSTELLUNG_STIMME"),
    "EINSTELLUNG_TEMPO": ("vorlesen", "EINSTELLUNG_TEMPO"),
    "Gelernt": ("gelernt", "Gelernt"),
    "LERN_SCHWELLE": ("gelernt", "LERN_SCHWELLE"),
    "MAX_ZEICHEN": ("vorlesen", "MAX_ZEICHEN"),
    "PIPER_NAMEN": ("vorlesen", "PIPER_NAMEN"),
    "RecoveryEntry": ("wiederherstellung", "RecoveryEntry"),
    "TEMPO_MAX": ("vorlesen", "TEMPO_MAX"),
    "TEMPO_MIN": ("vorlesen", "TEMPO_MIN"),
    "TEMPO_SCHRITT": ("vorlesen", "TEMPO_SCHRITT"),
    "VorlesenFehler": ("vorlesen", "VorlesenFehler"),
    "WORT": ("gelernt", "WORT"),
    "alle": ("bausteine", "alle"),
    "beenden": ("vorlesen", "beenden"),
    "discard": ("wiederherstellung", "discard"),
    "einfuegen": ("bausteine", "einfuegen"),
    "entfernen": ("bausteine", "entfernen"),
    "finde_kuerzel": ("bausteine", "finde_kuerzel"),
    "hinzufuegen": ("bausteine", "hinzufuegen"),
    "laden": ("bausteine", "laden"),
    "lies_vor": ("vorlesen", "lies_vor"),
    "new_token": ("wiederherstellung", "new_token"),
    "paths": ("wiederherstellung", "paths"),
    "pending": ("wiederherstellung", "pending"),
    "piper_da": ("vorlesen", "piper_da"),
    "piper_programm": ("vorlesen", "piper_programm"),
    "piper_stimmen": ("vorlesen", "piper_stimmen"),
    "recovery_dir": ("wiederherstellung", "recovery_dir"),
    "spd_da": ("vorlesen", "spd_da"),
    "speichern": ("bausteine", "speichern"),
    "standard": ("bausteine", "standard"),
    "stimmen": ("vorlesen", "stimmen"),
    "tempo_begrenzen": ("vorlesen", "tempo_begrenzen"),
    "tempo_piper": ("vorlesen", "tempo_piper"),
    "verfuegbar": ("vorlesen", "verfuegbar"),
    "vorlesetext": ("vorlesen", "vorlesetext"),
    "write_meta": ("wiederherstellung", "write_meta"),
    "zwischenstand": ("wiederherstellung", "zwischenstand"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "bausteine":
        from . import bausteine as _datei
    elif datei == "gelernt":
        from . import gelernt as _datei
    elif datei == "vorlesen":
        from . import vorlesen as _datei
    elif datei == "wiederherstellung":
        from . import wiederherstellung as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
