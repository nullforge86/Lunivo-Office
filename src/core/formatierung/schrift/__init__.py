"""Die Schrift im Dokumentenkern, von der Datei bis zum Pixel — ohne Oberfläche und ohne fremde Textsatz-Systeme.

    datenbank   welche Schriften es gibt, Auflösung von Familie, Gewicht und Kursiv zu einer Datei (Ersatz: ``ersatz``)
    schrift     eine geladene Schrift in einer Größe (HarfBuzz-Font, FreeType-Schrift, Zeilenmaße)
    formen      Text formen: Glyphen, Vorschübe, Kerning, Ligaturen (HarfBuzz)
    konturen    Glyphenpfade für gedrehten Text, PDF und Texteffekte (FreeType)
    raster      scharfe Deckungsbilder in Gerätegröße für Rasterflächen (FreeType)
    engine      ``HarfBuzzEngine``: die eine Stelle, an der Maße, Umbruch und Ausgabe zusammenlaufen"""
from core.formatierung.schrift.datenbank import SchriftDatenbank, Schnitt, standard_datenbank
from core.formatierung.schrift.engine import HarfBuzzEngine
from core.formatierung.schrift.schrift import PX_JE_PT, Schrift

__all__ = ["HarfBuzzEngine", "PX_JE_PT", "Schnitt", "Schrift", "SchriftDatenbank", "standard_datenbank",
           "ZUSATZ_AUSRICHTUNGEN", "ZUSATZ_FORMEN", "ZUSATZ_VORLAGEN", "ruby_text", "umschlossen_text"]

# Erst beim ersten Zugriff geladen: Zeichenzusätze (Ruby, umschlossene Zeichen).
_SPAET: dict[str, tuple[str, str]] = {"ZUSATZ_AUSRICHTUNGEN": ("zeichenzusatz", "AUSRICHTUNGEN"), "ZUSATZ_FORMEN": ("zeichenzusatz", "FORMEN"),
                                      "ZUSATZ_VORLAGEN": ("zeichenzusatz", "VORLAGEN"), "ruby_text": ("zeichenzusatz", "ruby_text"),
                                      "umschlossen_text": ("zeichenzusatz", "umschlossen_text")}

def __getattr__(name: str):
    datei, original = _SPAET.get(name, (None, None))
    if datei == "zeichenzusatz":
        from . import zeichenzusatz as _datei
    else:
        raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
    wert = getattr(_datei, original)
    globals()[name] = wert
    return wert
