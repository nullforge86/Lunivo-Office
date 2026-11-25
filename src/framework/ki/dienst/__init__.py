"""Tür des Pakets ``framework.ki.dienst``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "AKTIONS_MODI": ("ki_konfiguration", "AKTIONS_MODI"),
    "ANBIETER_TAGS": ("ki_konfiguration", "ANBIETER_TAGS"),
    "ANBIETER_VORLAGEN": ("ki_konfiguration", "ANBIETER_VORLAGEN"),
    "ANWEISUNG_ANALYSE": ("ki_anweisungen", "ANWEISUNG_ANALYSE"),
    "ANWEISUNG_ZUSAMMENFASSUNG": ("ki_anweisungen", "ANWEISUNG_ZUSAMMENFASSUNG"),
    "ARGOS_MARKE": ("ki_konfiguration", "ARGOS_MARKE"),
    "ASSISTENT_ARTEN": ("ki_konfiguration", "ASSISTENT_ARTEN"),
    "ASSISTENT_AUSLOESER": ("ki_konfiguration", "ASSISTENT_AUSLOESER"),
    "ASSISTENT_UMFAENGE": ("ki_konfiguration", "ASSISTENT_UMFAENGE"),
    "AUFGABEN": ("ki_konfiguration", "AUFGABEN"),
    "AUTO_MARKE": ("ki_konfiguration", "AUTO_MARKE"),
    "BEGRUENDUNG_TRENNER": ("assistent_lauf", "BEGRUENDUNG_TRENNER"),
    "CHAT_VORGABE": ("ki_konfiguration", "CHAT_VORGABE"),
    "CLAUDE_URL": ("ki_konfiguration", "CLAUDE_URL"),
    "Drossel": ("assistent_lauf", "Drossel"),
    "EIGEN_MARKE": ("ki_konfiguration", "EIGEN_MARKE"),
    "EMPFAENGER": ("ki_konfiguration", "EMPFAENGER"),
    "ERGEBNIS_GRENZE": ("ki_werkzeugschleife", "ERGEBNIS_GRENZE"),
    "FEHLER_FORM": ("ki_textaktionen", "FEHLER_FORM"),
    "FORTLAUFEND_MODI": ("ki_konfiguration", "FORTLAUFEND_MODI"),
    "HOECHSTZAHL_STUNDE": ("assistent_lauf", "HOECHSTZAHL_STUNDE"),
    "KI": ("ki", "KI"),
    "KIKonfig": ("ki_konfiguration", "KIKonfig"),
    "KOMMENTAR_NUR": ("ki_konfiguration", "KOMMENTAR_NUR"),
    "KOMMENTAR_ZUSATZ": ("ki_konfiguration", "KOMMENTAR_ZUSATZ"),
    "LERN_SCHWELLE": ("ki_konfiguration", "LERN_SCHWELLE"),
    "MAX_RUNDEN": ("ki_werkzeugschleife", "MAX_RUNDEN"),
    "MAX_ZEICHEN": ("assistent_lauf", "MAX_ZEICHEN"),
    "MINDESTABSTAND": ("assistent_lauf", "MINDESTABSTAND"),
    "MIN_ZEICHEN": ("assistent_lauf", "MIN_ZEICHEN"),
    "MODELLE_FEST": ("ki_konfiguration", "MODELLE_FEST"),
    "OLLAMA_MARKE": ("ki_konfiguration", "OLLAMA_MARKE"),
    "OLLAMA_URL": ("ki_konfiguration", "OLLAMA_URL"),
    "PREISE": ("ki_konfiguration", "PREISE"),
    "SPRACHEN": ("ki_konfiguration", "SPRACHEN"),
    "SYNONYM_BAUPLAN": ("ki_textaktionen", "SYNONYM_BAUPLAN"),
    "SYNONYM_LAENGE": ("ki_textaktionen", "SYNONYM_LAENGE"),
    "SYNONYM_MAX": ("ki_textaktionen", "SYNONYM_MAX"),
    "TEXT_AKTIONEN": ("ki_konfiguration", "TEXT_AKTIONEN"),
    "UMFAENGE": ("ki_konfiguration", "UMFAENGE"),
    "VERZOEGERUNG_MAX": ("assistent_lauf", "VERZOEGERUNG_MAX"),
    "VERZOEGERUNG_MIN": ("assistent_lauf", "VERZOEGERUNG_MIN"),
    "VERZOEGERUNG_VORGABE": ("assistent_lauf", "VERZOEGERUNG_VORGABE"),
    "VORLAGEN_ASSISTENT": ("ki_konfiguration", "VORLAGEN_ASSISTENT"),
    "VORLAGE_ANWEISUNG": ("ki_konfiguration", "VORLAGE_ANWEISUNG"),
    "VORSCHLAG_BAUPLAN": ("ki_konfiguration", "VORSCHLAG_BAUPLAN"),
    "ZETTEL_GRENZE": ("ki_konfiguration", "ZETTEL_GRENZE"),
    "absatz_geaendert": ("assistent_lauf", "absatz_geaendert"),
    "aenderungen": ("ki_diff", "aenderungen"),
    "als_geld": ("ki", "als_geld"),
    "anbieter_modelle": ("ki", "anbieter_modelle"),
    "anweisung_korrektur": ("ki_anweisungen", "anweisung_korrektur"),
    "anweisung_synonyme": ("ki_textaktionen", "anweisung_synonyme"),
    "anweisung_text_aktion": ("ki_anweisungen", "anweisung_text_aktion"),
    "anweisung_uebersetzung": ("ki_anweisungen", "anweisung_uebersetzung"),
    "anweisung_vorschlaege": ("ki_anweisungen", "anweisung_vorschlaege"),
    "assistent_normiert": ("ki_konfiguration", "assistent_normiert"),
    "chat": ("ki_werkzeugschleife", "chat"),
    "eingabe_kuerzen": ("assistent_lauf", "eingabe_kuerzen"),
    "ergebnis_wirkt": ("assistent_lauf", "ergebnis_wirkt"),
    "ersetze_ergebnis": ("ki_diff", "ersetze_ergebnis"),
    "ist_lokale_url": ("ki_konfiguration", "ist_lokale_url"),
    "liste_lesen": ("ki_textaktionen", "liste_lesen"),
    "steckbrief": ("ki_anweisungen", "steckbrief"),
    "synonyme_bereinigen": ("ki_textaktionen", "synonyme_bereinigen"),
    "trenne_begruendung": ("assistent_lauf", "trenne_begruendung"),
    "verzoegerung_begrenzen": ("assistent_lauf", "verzoegerung_begrenzen"),
    "vorschlaege_bereinigen": ("ki_textaktionen", "vorschlaege_bereinigen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "assistent_lauf":
        from . import assistent_lauf as _datei
    elif datei == "ki":
        from . import ki as _datei
    elif datei == "ki_anweisungen":
        from . import ki_anweisungen as _datei
    elif datei == "ki_diff":
        from . import ki_diff as _datei
    elif datei == "ki_konfiguration":
        from . import ki_konfiguration as _datei
    elif datei == "ki_textaktionen":
        from . import ki_textaktionen as _datei
    elif datei == "ki_werkzeugschleife":
        from . import ki_werkzeugschleife as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
