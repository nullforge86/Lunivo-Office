"""Tür des Pakets ``framework.ki.chat``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ANLIEGEN_AEHNLICH": ("chat_bezug", "ANLIEGEN_AEHNLICH"),
    "ChatModell": ("chat_modell", "ChatModell"),
    "DOKUMENT_GRENZE": ("ki_chat_kontext", "DOKUMENT_GRENZE"),
    "FORMAT_ZEILE": ("chat_antwort", "FORMAT_ZEILE"),
    "KUERZUNG_HINWEIS": ("ki_chat_kontext", "KUERZUNG_HINWEIS"),
    "MARKE_ANFANG": ("chat_antwort", "MARKE_ANFANG"),
    "MARKE_ENDE": ("chat_antwort", "MARKE_ENDE"),
    "MAX_GESPRAECHE": ("chat_modell", "MAX_GESPRAECHE"),
    "MELDUNG_ANGEWENDET": ("chat_bezug", "MELDUNG_ANGEWENDET"),
    "MELDUNG_EDITOR": ("chat_bezug", "MELDUNG_EDITOR"),
    "MELDUNG_GEAENDERT": ("chat_bezug", "MELDUNG_GEAENDERT"),
    "MELDUNG_KEINE_REZENSION": ("chat_bezug", "MELDUNG_KEINE_REZENSION"),
    "MELDUNG_KEIN_BEZUG": ("chat_bezug", "MELDUNG_KEIN_BEZUG"),
    "MELDUNG_OHNE_MARKIERUNG": ("chat_bezug", "MELDUNG_OHNE_MARKIERUNG"),
    "MELDUNG_OHNE_VERFOLGUNG": ("chat_bezug", "MELDUNG_OHNE_VERFOLGUNG"),
    "MELDUNG_REZENSION": ("chat_bezug", "MELDUNG_REZENSION"),
    "PHASEN": ("chat_modell", "PHASEN"),
    "TITEL_LAENGE": ("chat_modell", "TITEL_LAENGE"),
    "abschliessen": ("ki_chat_kontext", "abschliessen"),
    "bezug_angewendet": ("chat_bezug", "bezug_angewendet"),
    "bezug_bauen": ("chat_bezug", "bezug_bauen"),
    "bezug_pruefen": ("chat_bezug", "bezug_pruefen"),
    "bilder": ("ki_chat_kontext", "bilder"),
    "chat_vorschlaege_chat_vorschlaege": ("chat_vorschlaege", "chat_vorschlaege"),
    "dokumentensuche": ("ki_chat_kontext", "dokumentensuche"),
    "ersetz_schritte": ("chat_bezug", "ersetz_schritte"),
    "fehler_objekt": ("chat_modell", "fehler_objekt"),
    "felder": ("chat_antwort", "felder"),
    "gespraechstitel": ("chat_modell", "gespraechstitel"),
    "kern_von": ("chat_antwort", "kern_von"),
    "sperre": ("ki_chat_kontext", "sperre"),
    "strom_text": ("chat_antwort", "strom_text"),
    "system_text": ("ki_chat_kontext", "system_text"),
    "teilen": ("chat_antwort", "teilen"),
    "vorher_der_nachricht": ("chat_bezug", "vorher_der_nachricht"),
    "vorschau_der_nachricht": ("chat_bezug", "vorschau_der_nachricht"),
    "vorschau_einfuegen": ("chat_bezug", "vorschau_einfuegen"),
    "vorschau_stuecke": ("chat_bezug", "vorschau_stuecke"),
    "websuche": ("ki_chat_kontext", "websuche"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "chat_antwort":
        from . import chat_antwort as _datei
    elif datei == "chat_bezug":
        from . import chat_bezug as _datei
    elif datei == "chat_modell":
        from . import chat_modell as _datei
    elif datei == "chat_vorschlaege":
        from . import chat_vorschlaege as _datei
    elif datei == "ki_chat_kontext":
        from . import ki_chat_kontext as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
