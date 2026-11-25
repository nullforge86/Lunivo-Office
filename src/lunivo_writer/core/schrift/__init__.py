"""Die Schrift im Dokumentenkern, von der Datei bis zum Pixel — ohne Oberfläche und ohne fremde Textsatz-Systeme.

    datenbank   welche Schriften es gibt, Auflösung von Familie, Gewicht und Kursiv zu einer Datei (Ersatz: ``ersatz``)
    schrift     eine geladene Schrift in einer Größe (HarfBuzz-Font, FreeType-Schrift, Zeilenmaße)
    formen      Text formen: Glyphen, Vorschübe, Kerning, Ligaturen (HarfBuzz)
    konturen    Glyphenpfade für gedrehten Text, PDF und Texteffekte (FreeType)
    raster      scharfe Deckungsbilder in Gerätegröße für Rasterflächen (FreeType)
    engine      ``HarfBuzzEngine``: die eine Stelle, an der Maße, Umbruch und Ausgabe zusammenlaufen"""
from .datenbank import SchriftDatenbank, Schnitt, standard_datenbank
from .engine import HarfBuzzEngine
from .schrift import PX_JE_PT, Schrift

__all__ = ["HarfBuzzEngine", "PX_JE_PT", "Schnitt", "Schrift", "SchriftDatenbank", "standard_datenbank"]
