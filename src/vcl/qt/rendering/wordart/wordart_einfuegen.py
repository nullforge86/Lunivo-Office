"""Wordart einfuegen: aus ``vcl.qt.rendering.formen.einfuegen`` herausgelöst."""
from __future__ import annotations
from PySide6.QtGui import QImage
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from writer.anbindung.einfuegen_hilfen import wordart_vorlagen


def wordart_vorlage_bild(text: str, nr: int, schrift: str = "Liberation Sans", pt: int = 48) -> QImage:
    """WordArt nach einem der 15 Stile der Galerie: Füllverlauf, Kontur und Schatten (gezeichnet über ``core/rendering/wordart.py``)."""
    from vcl.qt.rendering.formen import raster_bild
    from writer.anbindung import zeichnen as ZW
    b, h = ZW.wordart_masse(text, schrift, pt)
    return raster_bild(b, h, lambda f: ZW.wordart(f, text, nr, schrift, pt))


def wordart_bild(text: str, stil: str = "Verlauf", schrift: str = "Liberation Sans", pt: int = 48, farbe: str = Farbe.AKZENT,
                 vorlage: int | None = None) -> QImage:
    """WordArt in einem der älteren Stile (Verlauf, Schatten, Umriss, Regenbogen, Welle) oder nach einer Vorlage der Galerie; gezeichnet vom Kern."""
    if vorlage is not None:
        return wordart_vorlage_bild(text, vorlage, schrift, pt)
    from writer.anbindung import zeichnen as ZW
    breite, hoehe, roh = ZW.wordart_stil(text, stil, schrift, pt, farbe, tuple(Farbe.REGENBOGEN))
    return QImage(roh, breite, hoehe, breite * 4, QImage.Format_RGBA8888).copy()
