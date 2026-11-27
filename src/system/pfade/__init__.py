"""Tür des Pakets ``system.pfade``: der eine Eingang für alle Orte des Programms.

Programmdaten (gepackt oder aus dem Quellcode), Benutzerordner je Betriebssystem, Schriftordner des Systems und die Suchorte und Erkennung der
Zusatzpakete. Aufrufer außerhalb des Pakets importieren nur von hier; kein anderer Programmteil setzt solche Pfade selbst zusammen.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ASSETS": ("ressourcen_pfade", "ASSETS"),
    "ORGANISATION": ("benutzerorte", "ORGANISATION"),
    "PAKET": ("ressourcen_pfade", "PAKET"),
    "PROGRAMM": ("benutzerorte", "PROGRAMM"),
    "PROGRAMMORDNER": ("ressourcen_pfade", "PROGRAMMORDNER"),
    "RESSOURCEN": ("ressourcen_pfade", "RESSOURCEN"),
    "SYMBOLE": ("ressourcen_pfade", "SYMBOLE"),
    "WURZEL": ("ressourcen_pfade", "WURZEL"),
    "Zusatzpaket": ("zusatzpakete", "Zusatzpaket"),
    "argos_dirs": ("zusatzpakete", "argos_dirs"),
    "argos_pakete_dir": ("zusatzpakete", "argos_pakete_dir"),
    "cache_basis": ("benutzerorte", "cache_basis"),
    "cache_dir": ("benutzerorte", "cache_dir"),
    "config_basis": ("benutzerorte", "config_basis"),
    "config_dir": ("benutzerorte", "config_dir"),
    "data_dir": ("benutzerorte", "data_dir"),
    "daten_basis": ("benutzerorte", "daten_basis"),
    "piper_dirs": ("zusatzpakete", "piper_dirs"),
    "schrift_ordner": ("schriften", "schrift_ordner"),
    "schriften_dir": ("benutzerorte", "schriften_dir"),
    "vorlagen_dir": ("benutzerorte", "vorlagen_dir"),
    "zusatzpakete_erkennen": ("zusatzpakete", "zusatzpakete_erkennen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "benutzerorte":
        from . import benutzerorte as _datei
    elif datei == "ressourcen_pfade":
        from . import ressourcen_pfade as _datei
    elif datei == "schriften":
        from . import schriften as _datei
    elif datei == "zusatzpakete":
        from . import zusatzpakete as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
