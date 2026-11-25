"""Tür des Pakets ``framework.dokumentverwaltung.dateizugriff``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "FORMATE": ("formate", "FORMATE"),
    "FormatInfo": ("formate", "FormatInfo"),
    "GRENZEN": ("import_grenzen", "GRENZEN"),
    "Grenzen": ("import_grenzen", "Grenzen"),
    "MB": ("import_grenzen", "MB"),
    "ModellGeladen": ("modell_laden", "ModellGeladen"),
    "NICHT_UNTERSTUETZT": ("dateiformate", "NICHT_UNTERSTUETZT"),
    "ODT_MIMETYPE": ("sicher_schreiben", "ODT_MIMETYPE"),
    "OLE_KOPF": ("sicher_schreiben", "OLE_KOPF"),
    "OPEN_FILTER": ("dateiformate", "OPEN_FILTER"),
    "PDF_FILTER": ("dateiformate", "PDF_FILTER"),
    "REST_ALTER_S": ("sicher_schreiben", "REST_ALTER_S"),
    "SAVE_FILTERS": ("dateiformate", "SAVE_FILTERS"),
    "SICHERUNGEN_JE_DOKUMENT": ("sicher_schreiben", "SICHERUNGEN_JE_DOKUMENT"),
    "SICHERUNG_TAGE": ("sicher_schreiben", "SICHERUNG_TAGE"),
    "SchreibKonflikt": ("sicher_schreiben", "SchreibKonflikt"),
    "T": ("sicher_schreiben", "T"),
    "UNGEPRUEFT": ("sicher_schreiben", "UNGEPRUEFT"),
    "als_markdown": ("formate", "als_markdown"),
    "bytes_schreiben": ("sicher_schreiben", "bytes_schreiben"),
    "endung_zum_filter": ("dateiformate", "endung_zum_filter"),
    "ext": ("dateiformate", "ext"),
    "fehlertext": ("sicher_schreiben", "fehlertext"),
    "finde": ("formate", "finde"),
    "fremd_geoeffnet": ("sicher_schreiben", "fremd_geoeffnet"),
    "lade_modell": ("modell_laden", "lade_modell"),
    "lesbar": ("formate", "lesbar"),
    "lxml_parser": ("import_grenzen", "lxml_parser"),
    "meta_aus_dokument": ("modell_speichern", "meta_aus_dokument"),
    "pruefe_dateigroesse": ("import_grenzen", "pruefe_dateigroesse"),
    "pruefe_format": ("sicher_schreiben", "pruefe_format"),
    "pruefe_paket": ("import_grenzen", "pruefe_paket"),
    "save_docx_daten": ("dateiformate", "save_docx_daten"),
    "schreiben": ("sicher_schreiben", "schreiben"),
    "sicheres_xml": ("import_grenzen", "sicheres_xml"),
    "sicherungen": ("sicher_schreiben", "sicherungen"),
    "sicherungen_aufraeumen": ("sicher_schreiben", "sicherungen_aufraeumen"),
    "sicherungs_ordner": ("sicher_schreiben", "sicherungs_ordner"),
    "sicherungskopie": ("sicher_schreiben", "sicherungskopie"),
    "speicherbar": ("formate", "speicherbar"),
    "speichere_modell": ("modell_speichern", "speichere_modell"),
    "sperre": ("sicher_schreiben", "sperre"),
    "stand": ("sicher_schreiben", "stand"),
    "ziel": ("sicher_schreiben", "ziel"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "dateiformate":
        from . import dateiformate as _datei
    elif datei == "formate":
        from . import formate as _datei
    elif datei == "import_grenzen":
        from . import import_grenzen as _datei
    elif datei == "modell_laden":
        from . import modell_laden as _datei
    elif datei == "modell_speichern":
        from . import modell_speichern as _datei
    elif datei == "sicher_schreiben":
        from . import sicher_schreiben as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
