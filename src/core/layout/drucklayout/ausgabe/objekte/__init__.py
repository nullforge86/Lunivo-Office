"""Tür des Pakets ``core.layout.drucklayout.ausgabe.objekte``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "ALLE_SEITEN": ("linien", "ALLE_SEITEN"),
    "ANKER_RADIUS": ("blasen", "ANKER_RADIUS"),
    "FORMATZEICHEN_FARBE": ("auswahlrenderer", "FORMATZEICHEN_FARBE"),
    "KOPF_HOEHE": ("blasen", "KOPF_HOEHE"),
    "LINIE_BREITE": ("blasen", "LINIE_BREITE"),
    "PX_JE_PT": ("linien", "PX_JE_PT"),
    "RAHMEN_POLSTER": ("linien", "RAHMEN_POLSTER"),
    "SCHATTEN_DECKKRAFT": ("blasen", "SCHATTEN_DECKKRAFT"),
    "SCHATTEN_VERSATZ": ("blasen", "SCHATTEN_VERSATZ"),
    "SCHATTEN_WEICH": ("blasen", "SCHATTEN_WEICH"),
    "STILE": ("linien", "STILE"),
    "STRICH": ("objekte", "STRICH"),
    "dunkler": ("objekte", "dunkler"),
    "form_pfad": ("objekte", "form_pfad"),
    "fuellstil": ("objekte", "fuellstil"),
    "heller": ("objekte", "heller"),
    "kontur_stil": ("objekte", "kontur_stil"),
    "messen": ("blasen", "messen"),
    "rahmen_aus_text": ("linien", "rahmen_aus_text"),
    "schrift_von": ("blasen", "schrift_von"),
    "verbindung": ("blasen", "verbindung"),
    "zeichne_absatzrahmen": ("linien", "zeichne_absatzrahmen"),
    "zeichne_auswahl": ("auswahlrenderer", "zeichne_auswahl"),
    "zeichne_bild": ("objekte", "zeichne_bild"),
    "zeichne_blase": ("blasen", "zeichne_blase"),
    "zeichne_cursor": ("auswahlrenderer", "zeichne_cursor"),
    "zeichne_form": ("objekte", "zeichne_form"),
    "zeichne_formatzeichen": ("auswahlrenderer", "zeichne_formatzeichen"),
    "zeichne_linie": ("linien", "zeichne_linie"),
    "zeichne_objekt": ("objektrenderer", "zeichne_objekt"),
    "zeichne_platzhalter": ("objekte", "zeichne_platzhalter"),
    "zeichne_rahmen": ("linien", "zeichne_rahmen"),
    "zeichne_textfeld": ("objektrenderer", "zeichne_textfeld"),
    "zeichne_wordart": ("objektrenderer", "zeichne_wordart"),
    "zeilen": ("blasen", "zeilen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "auswahlrenderer":
        from . import auswahlrenderer as _datei
    elif datei == "blasen":
        from . import blasen as _datei
    elif datei == "linien":
        from . import linien as _datei
    elif datei == "objekte":
        from . import objekte as _datei
    elif datei == "objektrenderer":
        from . import objektrenderer as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
