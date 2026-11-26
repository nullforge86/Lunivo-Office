"""Tür des Pakets ``framework.befehle.datei``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AUTOSPEICHERN_SEKUNDEN": ("einstellungen", "AUTOSPEICHERN_SEKUNDEN"),
    "BENUTZER_NAME": ("einstellungen", "BENUTZER_NAME"),
    "BENUTZER_VERWENDEN": ("einstellungen", "BENUTZER_VERWENDEN"),
    "BILDER_NICHT_KOMPRIMIEREN": ("einstellungen", "BILDER_NICHT_KOMPRIMIEREN"),
    "KOMPATIBILITAET": ("einstellungen", "KOMPATIBILITAET"),
    "LETZTER_ORDNER": ("einstellungen", "LETZTER_ORDNER"),
    "LETZTES_OEFFNEN": ("einstellungen", "LETZTES_OEFFNEN"),
    "PERSONENDATEN_WEG": ("einstellungen", "PERSONENDATEN_WEG"),
    "SICHERUNG_AKTIV": ("einstellungen", "SICHERUNG_AKTIV"),
    "SICHERUNG_STAENDE": ("einstellungen", "SICHERUNG_STAENDE"),
    "SICHERUNG_TAGE": ("einstellungen", "SICHERUNG_TAGE"),
    "VORGABEN": ("einstellungen", "VORGABEN"),
    "aufbewahrung_tage": ("einstellungen", "aufbewahrung_tage"),
    "bilder_komprimieren": ("einstellungen", "bilder_komprimieren"),
    "data_dir": ("orte", "data_dir"),
    "kompatibilitaet": ("einstellungen", "kompatibilitaet"),
    "letzten_ordner_merken": ("einstellungen", "letzten_ordner_merken"),
    "letztes_dokument_oeffnen": ("einstellungen", "letztes_dokument_oeffnen"),
    "pdf_druckrechte": ("pdf", "pdf_druckrechte"),
    "pdf_kennwort_fehler": ("pdf", "pdf_kennwort_fehler"),
    "pdf_schreiben": ("pdf", "pdf_schreiben"),
    "Pdfangabe": ("pdf", "Pdfangabe"),
    "pdf_wahl": ("pdf", "pdf_wahl"),
    "pdf_wahl_mit": ("pdf", "pdf_wahl_mit"),
    "schriften_dir": ("orte", "schriften_dir"),
    "sicherung_aktiv": ("einstellungen", "sicherung_aktiv"),
    "staende_sichern": ("einstellungen", "staende_sichern"),
    "verfasser": ("einstellungen", "verfasser"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "einstellungen":
        from . import einstellungen as _datei
    elif datei == "pdf":
        from . import pdf as _datei
    elif datei == "orte":
        from . import orte as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
