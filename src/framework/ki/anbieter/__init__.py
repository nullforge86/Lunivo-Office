"""Tür des Pakets ``framework.ki.anbieter``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "BILD_MAX_BYTES": ("modellfaehigkeit", "BILD_MAX_BYTES"),
    "BILD_TYPEN": ("modellfaehigkeit", "BILD_TYPEN"),
    "CLAUDE_FAEHIGKEITEN": ("modellfaehigkeit", "CLAUDE_FAEHIGKEITEN"),
    "CODES": ("argos", "CODES"),
    "DENKSTUFEN": ("modellfaehigkeit", "DENKSTUFEN"),
    "DENK_VORGABE": ("modellfaehigkeit", "DENK_VORGABE"),
    "FEHLER_HTTP": ("ki_claude", "FEHLER_HTTP"),
    "FEHLER_ZEIT": ("ki_ollama", "FEHLER_ZEIT"),
    "KEEP_ALIVE_MAX": ("ki_ollama", "KEEP_ALIVE_MAX"),
    "KEEP_ALIVE_MIN": ("ki_ollama", "KEEP_ALIVE_MIN"),
    "LEBENSDAUER": ("mcp", "LEBENSDAUER"),
    "MAX_ERGEBNIS": ("mcp", "MAX_ERGEBNIS"),
    "MAX_NACHRICHTEN": ("mcp", "MAX_NACHRICHTEN"),
    "MAX_ZEILE": ("mcp", "MAX_ZEILE"),
    "McpClient": ("mcp", "McpClient"),
    "McpFehler": ("mcp", "McpFehler"),
    "NUM_CTX_STUFEN": ("ki_ollama", "NUM_CTX_STUFEN"),
    "NUM_PREDICT_CHAT": ("ki_ollama", "NUM_PREDICT_CHAT"),
    "NUM_PREDICT_MAX": ("ki_ollama", "NUM_PREDICT_MAX"),
    "NUM_PREDICT_MIN": ("ki_ollama", "NUM_PREDICT_MIN"),
    "STROM_TAKT": ("ki_ollama", "STROM_TAKT"),
    "WERKZEUG_AUTOMATISCH": ("modellfaehigkeit", "WERKZEUG_AUTOMATISCH"),
    "WERKZEUG_MODI": ("modellfaehigkeit", "WERKZEUG_MODI"),
    "ZEICHEN_JE_TOKEN": ("ki_ollama", "ZEICHEN_JE_TOKEN"),
    "ZEIT": ("mcp", "ZEIT"),
    "anbieter_pruefen": ("ki_bildgenerierung", "anbieter_pruefen"),
    "art_des_werkzeugs": ("mcp", "art_des_werkzeugs"),
    "bearer_kopf": ("ki_transport", "bearer_kopf"),
    "bild_block": ("ki_transport", "bild_block"),
    "bild_pruefen": ("modellfaehigkeit", "bild_pruefen"),
    "bilder_lesen": ("ki_transport", "bilder_lesen"),
    "bildtyp_aus_inhalt": ("modellfaehigkeit", "bildtyp_aus_inhalt"),
    "cent_fuer": ("ki_claude", "cent_fuer"),
    "claude_faehig": ("modellfaehigkeit", "claude_faehig"),
    "code_fuer": ("argos", "code_fuer"),
    "denkstufe": ("modellfaehigkeit", "denkstufe"),
    "erkenne_sprache": ("argos", "erkenne_sprache"),
    "erste_nachricht": ("ki_transport", "erste_nachricht"),
    "erzeugen": ("ki_bildgenerierung", "erzeugen"),
    "fehler_http": ("ki_claude", "fehler_http"),
    "installierte_richtungen": ("argos", "installierte_richtungen"),
    "json_dict": ("ki_transport", "json_dict"),
    "json_nach_marken": ("ki_transport", "json_nach_marken"),
    "keep_alive_begrenzen": ("ki_ollama", "keep_alive_begrenzen"),
    "ki_claude_anfrage": ("ki_claude", "anfrage"),
    "ki_claude_antwort_lesen": ("ki_claude", "antwort_lesen"),
    "ki_claude_bitte_bauen": ("ki_claude", "bitte_bauen"),
    "ki_eigen_anfrage": ("ki_eigen", "anfrage"),
    "ki_eigen_antwort_lesen": ("ki_eigen", "antwort_lesen"),
    "ki_eigen_bitte_bauen": ("ki_eigen", "bitte_bauen"),
    "ki_ollama_anfrage": ("ki_ollama", "anfrage"),
    "ki_ollama_antwort_lesen": ("ki_ollama", "antwort_lesen"),
    "ki_ollama_bitte_bauen": ("ki_ollama", "bitte_bauen"),
    "nachricht": ("ki_transport", "nachricht"),
    "nachrichten": ("ki_transport", "nachrichten"),
    "num_ctx_begrenzen": ("ki_ollama", "num_ctx_begrenzen"),
    "num_ctx_fuer": ("ki_ollama", "num_ctx_fuer"),
    "num_predict_fuer": ("ki_ollama", "num_predict_fuer"),
    "num_thread_begrenzen": ("ki_ollama", "num_thread_begrenzen"),
    "ohne_gruebeln": ("ki_transport", "ohne_gruebeln"),
    "post": ("ki_transport", "post"),
    "post_roh": ("ki_transport", "post_roh"),
    "pruefen": ("mcp", "pruefen"),
    "richtung_installieren": ("argos", "richtung_installieren"),
    "stopp_liste": ("ki_transport", "stopp_liste"),
    "strom_lesen": ("ki_ollama", "strom_lesen"),
    "stufe": ("ki_transport", "stufe"),
    "uebersetze": ("argos", "uebersetze"),
    "verfuegbare_richtungen": ("argos", "verfuegbare_richtungen"),
    "werkzeug_erlaubt": ("modellfaehigkeit", "werkzeug_erlaubt"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "argos":
        from . import argos as _datei
    elif datei == "ki_bildgenerierung":
        from . import ki_bildgenerierung as _datei
    elif datei == "ki_claude":
        from . import ki_claude as _datei
    elif datei == "ki_eigen":
        from . import ki_eigen as _datei
    elif datei == "ki_ollama":
        from . import ki_ollama as _datei
    elif datei == "ki_transport":
        from . import ki_transport as _datei
    elif datei == "mcp":
        from . import mcp as _datei
    elif datei == "modellfaehigkeit":
        from . import modellfaehigkeit as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
