"""Tür des Pakets ``core.layout.drucklayout.ausgabe.bild``: alle öffentlichen Namen seiner Dateien. Aufrufer außerhalb des Pakets importieren nur von hier.

Die Dateien werden erst beim ersten Zugriff auf einen ihrer Namen geladen. Gibt es einen Namen in mehreren Dateien, heißt er hier
``<datei>_<name>``."""
from __future__ import annotations

_NAMEN: dict[str, tuple[str, str]] = {
    "MAX_BYTES": ("svg", "MAX_BYTES"),
    "MAX_SEITE_PX": ("metafile", "MAX_SEITE_PX"),
    "PX_PT": ("bildeffekte", "PX_PT"),
    "abschluss_oben": ("bild3d", "abschluss_oben"),
    "begrenzt": ("metafile", "begrenzt"),
    "bild_dekodieren": ("bilddecoder", "bild_dekodieren"),
    "braucht_nachbearbeitung": ("bild3d", "braucht_nachbearbeitung"),
    "dreht": ("bild3d", "dreht"),
    "ellipse_alpha": ("bildeffekte", "ellipse_alpha"),
    "emf_zeichnen": ("metafile", "emf_zeichnen"),
    "extrusion": ("bild3d", "extrusion"),
    "form_alpha": ("bildeffekte", "form_alpha"),
    "gedreht": ("bild3d", "gedreht"),
    "getoent": ("bildeffekte", "getoent"),
    "hat_abschluss": ("bild3d", "hat_abschluss"),
    "hat_extrusion": ("bild3d", "hat_extrusion"),
    "ist_emf": ("metafile", "ist_emf"),
    "ist_svg": ("svg", "ist_svg"),
    "ist_wmf": ("metafile", "ist_wmf"),
    "kachel_von": ("fuellmuster", "kachel_von"),
    "masse_px": ("metafile", "masse_px"),
    "metafile_rgba": ("metafile", "metafile_rgba"),
    "muster_an": ("fuellmuster", "muster_an"),
    "muster_kachel": ("fuellmuster", "muster_kachel"),
    "nachbearbeitet": ("bild3d", "nachbearbeitet"),
    "pfad_ops": ("svg", "pfad_ops"),
    "png_bytes": ("bildeffekte", "png_bytes"),
    "reflektion_bild": ("bildeffekte", "reflektion_bild"),
    "schatten_bild": ("bildeffekte", "schatten_bild"),
    "skaliert": ("bildeffekte", "skaliert"),
    "stufenfarbe": ("bild3d", "stufenfarbe"),
    "svg_masse": ("svg", "svg_masse"),
    "svg_rgba": ("svg", "svg_rgba"),
    "svg_zeichnen": ("svg", "svg_zeichnen"),
    "textur_kachel": ("fuellmuster", "textur_kachel"),
    "tiefe_richtung": ("bild3d", "tiefe_richtung"),
    "weiche_kanten": ("bildeffekte", "weiche_kanten"),
    "weichgezeichnet": ("bildeffekte", "weichgezeichnet"),
    "wmf_zeichnen": ("metafile", "wmf_zeichnen"),
}

__all__ = sorted(_NAMEN)


def __getattr__(name: str):
    datei, original = _NAMEN.get(name, (None, None))
    if datei == "bild3d":
        from . import bild3d as _datei
    elif datei == "bilddecoder":
        from . import bilddecoder as _datei
    elif datei == "bildeffekte":
        from . import bildeffekte as _datei
    elif datei == "fuellmuster":
        from . import fuellmuster as _datei
    elif datei == "metafile":
        from . import metafile as _datei
    elif datei == "svg":
        from . import svg as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert


def __dir__() -> list[str]:
    return __all__
