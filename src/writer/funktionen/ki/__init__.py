"""Tür des Pakets ``writer.funktionen.ki``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AUTO_MARKE": ("ki_dienst", "AUTO_MARKE"),
    "DENKSTUFEN": ("ki_dienst", "DENKSTUFEN"),
    "EIGEN_MARKE": ("ki_dienst", "EIGEN_MARKE"),
    "MELDUNG_EDITOR": ("ki_dienst", "MELDUNG_EDITOR"),
    "MELDUNG_GEAENDERT": ("ki_dienst", "MELDUNG_GEAENDERT"),
    "MELDUNG_KEINE_REZENSION": ("ki_dienst", "MELDUNG_KEINE_REZENSION"),
    "MELDUNG_KEIN_BEZUG": ("ki_dienst", "MELDUNG_KEIN_BEZUG"),
    "MELDUNG_OHNE_MARKIERUNG": ("ki_dienst", "MELDUNG_OHNE_MARKIERUNG"),
    "MELDUNG_OHNE_VERFOLGUNG": ("ki_dienst", "MELDUNG_OHNE_VERFOLGUNG"),
    "MELDUNG_REZENSION": ("ki_dienst", "MELDUNG_REZENSION"),
    "MINDESTABSTAND": ("ki_dienst", "MINDESTABSTAND"),
    "OLLAMA_MARKE": ("ki_dienst", "OLLAMA_MARKE"),
    "TEXT_AKTIONEN": ("ki_dienst", "TEXT_AKTIONEN"),
    "WERKZEUG_MODI": ("ki_dienst", "WERKZEUG_MODI"),
    "ZETTEL_GRENZE": ("zettel", "ZETTEL_GRENZE"),
    "absatz_geaendert": ("ki_dienst", "absatz_geaendert"),
    "als_geld": ("ki_dienst", "als_geld"),
    "assistenten_drossel": ("ki_dienst", "assistenten_drossel"),
    "bezug_angewendet": ("ki_dienst", "bezug_angewendet"),
    "bezug_bauen": ("ki_dienst", "bezug_bauen"),
    "bezug_pruefen": ("ki_dienst", "bezug_pruefen"),
    "bild_pruefen": ("ki_dienst", "bild_pruefen"),
    "chat_verlauf": ("ki_dienst", "chat_verlauf"),
    "chat_vorschlaege": ("ki_dienst", "chat_vorschlaege"),
    "denkstufe": ("ki_dienst", "denkstufe"),
    "eingabe_kuerzen": ("ki_dienst", "eingabe_kuerzen"),
    "ergebnis_wirkt": ("ki_dienst", "ergebnis_wirkt"),
    "ersetz_schritte": ("ki_dienst", "ersetz_schritte"),
    "ersetze_ergebnis": ("ki_dienst", "ersetze_ergebnis"),
    "kern_von": ("ki_dienst", "kern_von"),
    "ki_anbinden": ("ki_dienst", "ki_anbinden"),
    "ki_konfiguration": ("ki_dienst", "ki_konfiguration"),
    "trenne_begruendung": ("ki_dienst", "trenne_begruendung"),
    "verzoegerung_begrenzen": ("ki_dienst", "verzoegerung_begrenzen"),
    "vorher_der_nachricht": ("ki_dienst", "vorher_der_nachricht"),
    "vorschau_der_nachricht": ("ki_dienst", "vorschau_der_nachricht"),
    "vorschau_einfuegen": ("ki_dienst", "vorschau_einfuegen"),
    "vorschau_stuecke": ("ki_dienst", "vorschau_stuecke"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "ki_dienst":
        from . import ki_dienst as _datei
    elif datei == "zettel":
        from . import zettel as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
