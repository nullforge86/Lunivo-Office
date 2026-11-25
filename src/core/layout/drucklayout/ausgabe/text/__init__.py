"""Tür des Pakets ``core.layout.drucklayout.ausgabe.text``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "FUELL_LUECKE": ("textrenderer", "FUELL_LUECKE"),
    "FUELL_STRICH": ("textrenderer", "FUELL_STRICH"),
    "PX_JE_PT": ("textrenderer", "PX_JE_PT"),
    "RAND": ("wordart", "RAND"),
    "SS": ("wordartobjekt", "SS"),
    "TextAusKern": ("textpfad", "TextAusKern"),
    "UNTER_MUSTER": ("zeichenzusatz", "UNTER_MUSTER"),
    "ZEICHEN_SCHLUESSEL": ("wordartobjekt", "ZEICHEN_SCHLUESSEL"),
    "anzeige_laeufe": ("wordartobjekt", "anzeige_laeufe"),
    "betonung": ("zeichenzusatz", "betonung"),
    "doppelt_durch": ("zeichenzusatz", "doppelt_durch"),
    "effekt_lesen": ("texteffekte", "effekt_lesen"),
    "engine_fuer": ("textrenderer", "engine_fuer"),
    "gemeinsame_engine": ("textpfad", "gemeinsame_engine"),
    "laeufe_text": ("wordartobjekt", "laeufe_text"),
    "listenmarken": ("wordartobjekt", "listenmarken"),
    "masse": ("wordart", "masse"),
    "nummer_text": ("wordartobjekt", "nummer_text"),
    "pfad_verformen": ("texteffekte", "pfad_verformen"),
    "ruby": ("zeichenzusatz", "ruby"),
    "texteffekte_PX": ("texteffekte", "PX"),
    "umschlossen": ("zeichenzusatz", "umschlossen"),
    "unterstrich": ("zeichenzusatz", "unterstrich"),
    "wordart_rgba": ("wordartobjekt", "wordart_rgba"),
    "wordartobjekt_PX": ("wordartobjekt", "PX"),
    "zeichne": ("wordart", "zeichne"),
    "zeichne_listenmarke": ("textrenderer", "zeichne_listenmarke"),
    "zeichne_marke": ("textrenderer", "zeichne_marke"),
    "zeichne_tabfuellung": ("textrenderer", "zeichne_tabfuellung"),
    "zeichne_text": ("textpfad", "zeichne_text"),
    "zeichne_text_kontur": ("textpfad", "zeichne_text_kontur"),
    "zeichne_text_mit_effekt": ("texteffekte", "zeichne_text_mit_effekt"),
    "zeichne_zeile": ("textrenderer", "zeichne_zeile"),
    "zeichne_zeilennummern": ("textrenderer", "zeichne_zeilennummern"),
    "zeilen_laeufe": ("wordartobjekt", "zeilen_laeufe"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "texteffekte":
        from . import texteffekte as _datei
    elif datei == "textpfad":
        from . import textpfad as _datei
    elif datei == "textrenderer":
        from . import textrenderer as _datei
    elif datei == "wordart":
        from . import wordart as _datei
    elif datei == "wordartobjekt":
        from . import wordartobjekt as _datei
    elif datei == "zeichenzusatz":
        from . import zeichenzusatz as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
