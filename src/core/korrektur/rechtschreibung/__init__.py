"""Tür des Pakets ``core.korrektur.rechtschreibung``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ABC": ("pruefung", "ABC"),
    "ABKUERZUNG": ("pruefung", "ABKUERZUNG"),
    "ADR_A": ("pruefung_hilfen", "ADR_A"),
    "ADR_B": ("pruefung_hilfen", "ADR_B"),
    "ADR_C": ("pruefung_hilfen", "ADR_C"),
    "DASS_EIGENSCHAFTEN": ("pruefung", "DASS_EIGENSCHAFTEN"),
    "DENK_ZEITWOERTER": ("pruefung", "DENK_ZEITWOERTER"),
    "DENK_ZEITWOERTER_ENG": ("pruefung", "DENK_ZEITWOERTER_ENG"),
    "FOLGT_NEBENSATZ": ("pruefung", "FOLGT_NEBENSATZ"),
    "FORM_ZU_ZEITWORT": ("pruefung_hilfen", "FORM_ZU_ZEITWORT"),
    "FUERWOERTER": ("pruefung", "FUERWOERTER"),
    "GRAMMATIK_PRUEFER": ("pruefung", "GRAMMATIK_PRUEFER"),
    "GRAMMATIK_REGELN": ("pruefung", "GRAMMATIK_REGELN"),
    "GROSS_ANFANG": ("pruefung_hilfen", "GROSS_ANFANG"),
    "GROSS_REGELN": ("pruefung", "GROSS_REGELN"),
    "HINWEIS_PRUEFER": ("pruefung", "HINWEIS_PRUEFER"),
    "HOCH": ("autokorrektur", "HOCH"),
    "KEIN_HAUPTWORT": ("pruefung", "KEIN_HAUPTWORT"),
    "KEIN_KOMMA_DAVOR": ("pruefung", "KEIN_KOMMA_DAVOR"),
    "KOMMA_REGELN": ("pruefung", "KOMMA_REGELN"),
    "NEBENSATZ_WOERTER": ("pruefung", "NEBENSATZ_WOERTER"),
    "PRUEFER_NAMEN": ("pruefung", "PRUEFER_NAMEN"),
    "REGEL_PRUEFER": ("pruefung", "REGEL_PRUEFER"),
    "SCHALTER": ("autokorrektur", "SCHALTER"),
    "SCHALTER_STANDARD": ("pruefung_hilfen", "SCHALTER_STANDARD"),
    "STEIGERUNGEN": ("pruefung", "STEIGERUNGEN"),
    "TRENN_KURZ": ("pruefung_hilfen", "TRENN_KURZ"),
    "WOCHENTAGE": ("autokorrektur", "WOCHENTAGE"),
    "WOERTERBUCH": ("pruefung_hilfen", "WOERTERBUCH"),
    "WORT_MUSTER": ("pruefung_hilfen", "WORT_MUSTER"),
    "WORT_PRUEFER": ("pruefung", "WORT_PRUEFER"),
    "ZEICHEN_REGELN": ("pruefung", "ZEICHEN_REGELN"),
    "ZEITANGABEN": ("pruefung", "ZEITANGABEN"),
    "ZEITWOERTER": ("pruefung", "ZEITWOERTER"),
    "daten_ordner": ("pruefung_hilfen", "daten_ordner"),
    "finde_probleme": ("pruefung", "finde_probleme"),
    "gross_dahinter": ("pruefung", "gross_dahinter"),
    "ist_abkuerzung": ("pruefung", "ist_abkuerzung"),
    "ist_adresse": ("pruefung_hilfen", "ist_adresse"),
    "ist_korrektur": ("pruefung", "ist_korrektur"),
    "kleinste_aenderung": ("autokorrektur", "kleinste_aenderung"),
    "korrigiere": ("autokorrektur", "korrigiere"),
    "lade_woerter": ("pruefung_hilfen", "lade_woerter"),
    "mach_fund": ("pruefung_hilfen", "mach_fund"),
    "nachbar_woerter": ("pruefung", "nachbar_woerter"),
    "ohne_ueberschneidung": ("pruefung", "ohne_ueberschneidung"),
    "pruefe_tippfehler": ("pruefung", "pruefe_tippfehler"),
    "pruefe_woerter": ("pruefung", "pruefe_woerter"),
    "pruefer_aktiv": ("pruefung", "pruefer_aktiv"),
    "regel": ("pruefung", "regel"),
    "tippfehler_vorschlag": ("pruefung", "tippfehler_vorschlag"),
    "uebergehen": ("pruefung_hilfen", "uebergehen"),
    "uebernimm_schreibweise": ("pruefung_hilfen", "uebernimm_schreibweise"),
    "wende_regeln_an": ("pruefung", "wende_regeln_an"),
    "wort_abstand": ("pruefung_hilfen", "wort_abstand"),
    "wort_um": ("pruefung_hilfen", "wort_um"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "autokorrektur":
        from . import autokorrektur as _datei
    elif datei == "pruefung":
        from . import pruefung as _datei
    elif datei == "pruefung_hilfen":
        from . import pruefung_hilfen as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
