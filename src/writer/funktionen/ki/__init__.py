"""Tür des Pakets ``writer.funktionen.ki``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "absatz_geaendert": ("ki_dienst", "absatz_geaendert"),
    "als_geld": ("ki_dienst", "als_geld"),
    "anbieter_modelle": ("ki_einstellungen", "anbieter_modelle"),
    "anbieter_tags": ("ki_einstellungen", "anbieter_tags"),
    "anbieter_vorlagen": ("ki_einstellungen", "anbieter_vorlagen"),
    "argos_installierte_richtungen": ("ki_einstellungen", "argos_installierte_richtungen"),
    "argos_marke": ("ki_einstellungen", "argos_marke"),
    "argos_richtung_installieren": ("ki_einstellungen", "argos_richtung_installieren"),
    "argos_verfuegbare_richtungen": ("ki_einstellungen", "argos_verfuegbare_richtungen"),
    "assistent_ausloeser": ("ki_einstellungen", "assistent_ausloeser"),
    "assistent_umfaenge": ("ki_einstellungen", "assistent_umfaenge"),
    "assistenten_drossel": ("ki_dienst", "assistenten_drossel"),
    "aufgaben": ("ki_einstellungen", "aufgaben"),
    "auto_marke": ("ki_dienst", "auto_marke"),
    "bezug_angewendet": ("ki_dienst", "bezug_angewendet"),
    "bezug_bauen": ("ki_dienst", "bezug_bauen"),
    "bezug_pruefen": ("ki_dienst", "bezug_pruefen"),
    "bild_pruefen": ("ki_dienst", "bild_pruefen"),
    "chat_meldung": ("ki_dienst", "chat_meldung"),
    "chat_verlauf": ("ki_dienst", "chat_verlauf"),
    "chat_vorschlaege": ("ki_dienst", "chat_vorschlaege"),
    "denkstufe": ("ki_dienst", "denkstufe"),
    "denkstufen": ("ki_dienst", "denkstufen"),
    "dokumentindex_aktualisieren": ("ki_einstellungen", "dokumentindex_aktualisieren"),
    "dokumentindex_anzahl": ("ki_einstellungen", "dokumentindex_anzahl"),
    "eigen_marke": ("ki_dienst", "eigen_marke"),
    "eingabe_kuerzen": ("ki_dienst", "eingabe_kuerzen"),
    "ergebnis_wirkt": ("ki_dienst", "ergebnis_wirkt"),
    "ersetz_schritte": ("ki_dienst", "ersetz_schritte"),
    "ersetze_ergebnis": ("ki_dienst", "ersetze_ergebnis"),
    "fortlaufend_modi": ("ki_einstellungen", "fortlaufend_modi"),
    "ist_lokale_url": ("ki_einstellungen", "ist_lokale_url"),
    "keep_alive_begrenzen": ("ki_einstellungen", "keep_alive_begrenzen"),
    "keep_alive_max": ("ki_einstellungen", "keep_alive_max"),
    "kern_von": ("ki_dienst", "kern_von"),
    "ki_anbinden": ("ki_dienst", "ki_anbinden"),
    "ki_konfiguration": ("ki_dienst", "ki_konfiguration"),
    "mcp_pruefen": ("ki_einstellungen", "mcp_pruefen"),
    "mindestabstand": ("ki_dienst", "mindestabstand"),
    "modelle_fest": ("ki_einstellungen", "modelle_fest"),
    "num_ctx_begrenzen": ("ki_einstellungen", "num_ctx_begrenzen"),
    "num_ctx_stufen": ("ki_einstellungen", "num_ctx_stufen"),
    "num_thread_begrenzen": ("ki_einstellungen", "num_thread_begrenzen"),
    "ollama_marke": ("ki_dienst", "ollama_marke"),
    "sprachen": ("ki_einstellungen", "sprachen"),
    "text_aktionen": ("ki_dienst", "text_aktionen"),
    "trenne_begruendung": ("ki_dienst", "trenne_begruendung"),
    "umfaenge": ("ki_einstellungen", "umfaenge"),
    "unveraenderlich": ("werte", "unveraenderlich"),
    "verzoegerung_begrenzen": ("ki_dienst", "verzoegerung_begrenzen"),
    "verzoegerung_max": ("ki_einstellungen", "verzoegerung_max"),
    "verzoegerung_min": ("ki_einstellungen", "verzoegerung_min"),
    "verzoegerung_vorgabe": ("ki_einstellungen", "verzoegerung_vorgabe"),
    "vorher_der_nachricht": ("ki_dienst", "vorher_der_nachricht"),
    "vorlagen_assistent": ("ki_einstellungen", "vorlagen_assistent"),
    "vorschau_der_nachricht": ("ki_dienst", "vorschau_der_nachricht"),
    "vorschau_einfuegen": ("ki_dienst", "vorschau_einfuegen"),
    "vorschau_stuecke": ("ki_dienst", "vorschau_stuecke"),
    "websuche": ("ki_einstellungen", "websuche"),
    "websuche_anbieter": ("ki_einstellungen", "websuche_anbieter"),
    "werkzeug_modi": ("ki_dienst", "werkzeug_modi"),
    "zettel_grenze": ("zettel", "zettel_grenze"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "ki_dienst":
        from . import ki_dienst as _datei
    elif datei == "ki_einstellungen":
        from . import ki_einstellungen as _datei
    elif datei == "werte":
        from . import werte as _datei
    elif datei == "zettel":
        from . import zettel as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
