"""Tür des Pakets ``core.text``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AKTIONEN": ("wortextras", "AKTIONEN"),
    "ASIATISCH": ("statistik", "ASIATISCH"),
    "AUFZAEHLUNG_EBENEN": ("ki_markdown", "AUFZAEHLUNG_EBENEN"),
    "MENUE": ("wortextras", "MENUE"),
    "SATZENDE": ("wortextras", "SATZENDE"),
    "TYPEN": ("zahlformat", "TYPEN"),
    "ZEILENUMBRUCH": ("wortextras", "ZEILENUMBRUCH"),
    "absaetze_neu_anordnen": ("wortextras", "absaetze_neu_anordnen"),
    "einzug_in_leerzeichen": ("wortextras", "einzug_in_leerzeichen"),
    "einzug_zwei_zeichen": ("wortextras", "einzug_zwei_zeichen"),
    "fuehrende_leerzeichen_loeschen": ("wortextras", "fuehrende_leerzeichen_loeschen"),
    "grenzen": ("zahlformat", "grenzen"),
    "hat_struktur": ("ki_markdown", "hat_struktur"),
    "klartext": ("ki_markdown", "klartext"),
    "leerabsatz_modus_wechseln": ("wortextras", "leerabsatz_modus_wechseln"),
    "leere_einfuegen": ("wortextras", "leere_einfuegen"),
    "leere_loeschen": ("wortextras", "leere_loeschen"),
    "leerzeichen_bereinigen": ("wortextras", "leerzeichen_bereinigen"),
    "markdown_bloecke": ("ki_markdown", "markdown_bloecke"),
    "normalisieren": ("ki_markdown", "normalisieren"),
    "smart_anordnen": ("wortextras", "smart_anordnen"),
    "texte_des_dokuments": ("statistik", "texte_des_dokuments"),
    "zaehlen": ("statistik", "zaehlen"),
    "zahl_text": ("zahlformat", "zahl_text"),
    "zahlwort": ("zahlformat", "zahlwort"),
    "zeilenumbruch_in_return": ("wortextras", "zeilenumbruch_in_return"),
    "zeilenumbrueche_loeschen": ("wortextras", "zeilenumbrueche_loeschen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "ki_markdown":
        from . import ki_markdown as _datei
    elif datei == "statistik":
        from . import statistik as _datei
    elif datei == "wortextras":
        from . import wortextras as _datei
    elif datei == "zahlformat":
        from . import zahlformat as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
