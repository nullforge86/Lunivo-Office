"""Anbindung der Oberfläche an ``framework.zeichnen``: Zeichnungen des Kerns als fertiges Rasterbild (Fläche und Rechtecke als einfache Tupel)."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import framework.zeichnen as _fw
from framework.schnittstellen import BlasenSchrift


def blase(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], autor: str, datum: str, farbe: tuple[int, int, int, int], text: str, r: tuple[float, float, float, float], schrift: BlasenSchrift, farben: tuple[tuple[int, int, int, int], tuple[int, int, int, int], tuple[int, int, int, int]]) -> tuple[int, int, bytes]:
    """Eine Sprechblase wie eine Karte."""
    return _fw.blase(flaeche, autor, datum, farbe, text, r, schrift, farben)


def blasen_verbindung(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], farbe: tuple[int, int, int, int], x_text: float, y_text: float, r: tuple[float, float, float, float], rechts: bool) -> tuple[int, int, bytes]:
    """Linie vom Text zur Blase."""
    return _fw.blasen_verbindung(flaeche, farbe, x_text, y_text, r, rechts)


def linie(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], farbe: str, breite_pt: float, art: str, x1: float, y1: float, x2: float, y2: float, massstab: float=1.0) -> tuple[int, int, bytes]:
    """Eine einzelne Linie in ihrer Art."""
    return _fw.linie(flaeche, farbe, breite_pt, art, x1, y1, x2, y2, massstab)


def rahmen(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], farbe: str, breite_pt: float, art: str, seiten: str, r: tuple[float, float, float, float], massstab: float=1.0, innen_y: Sequence[float]=()) -> tuple[int, int, bytes]:
    """Die gemeinten Seiten eines Rechtecks in der Linienart."""
    return _fw.rahmen(flaeche, farbe, breite_pt, art, seiten, r, massstab, innen_y)


def unterstrich(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], strecken: Sequence[tuple[float, float]], art: str, grundlinie: float, groesse: float, farbe: tuple[int, int, int, int]) -> tuple[int, int, bytes]:
    """Unterstreichung in ihrer Art über die Strecken."""
    return _fw.unterstrich(flaeche, strecken, art, grundlinie, groesse, farbe)


def doppelt_durch(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], r: tuple[float, float, float, float], grundlinie: float, groesse: float, farbe: tuple[int, int, int, int]) -> tuple[int, int, bytes]:
    """Doppelt durchgestrichen."""
    return _fw.doppelt_durch(flaeche, r, grundlinie, groesse, farbe)


def betonung(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], glyphen: Sequence[tuple[float, float, float]], art: str, grundlinie: float, groesse: float, farbe: tuple[int, int, int, int]) -> tuple[int, int, bytes]:
    """Betonungszeichen über den Glyphen."""
    return _fw.betonung(flaeche, glyphen, art, grundlinie, groesse, farbe)


def umschlossen(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], kasten: tuple[float, float, float, float], wie: tuple[str, str], farbe: tuple[int, int, int, int], groesse: float) -> tuple[int, int, bytes]:
    """Umschlossenes Zeichen (Kreis, Quadrat …)."""
    return _fw.umschlossen(flaeche, kasten, wie, farbe, groesse)


def ruby(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], x0: float, x1: float, grundlinie: float, groesse: float, ruby_: Mapping[str, str | float], farbe: tuple[int, int, int, int]) -> tuple[int, int, bytes]:
    """Ruby-Text über dem Grundtext."""
    return _fw.ruby(flaeche, x0, x1, grundlinie, groesse, ruby_, farbe)


def wasserzeichen(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], w: Mapping[str, str | int | float | bool | None] | None, r: tuple[float, float, float, float]) -> tuple[int, int, bytes]:
    """Das Wasserzeichen in ``r``."""
    return _fw.wasserzeichen(flaeche, w, r)


def deckblatt(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], name: str, r: tuple[float, float, float, float], mit_text: bool=True) -> tuple[int, int, bytes]:
    """Ein Deckblatt (mit oder ohne Beispieltext)."""
    return _fw.deckblatt(flaeche, name, r, mit_text)


def deckblatt_grafik(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], name: str, r: tuple[float, float, float, float]) -> tuple[int, int, bytes]:
    """Nur die Grafik eines Deckblatts."""
    return _fw.deckblatt_grafik(flaeche, name, r)


def platzhalter(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], r: tuple[float, float, float, float]) -> tuple[int, int, bytes]:
    """Platzhalter für ein fehlendes Bild."""
    return _fw.platzhalter(flaeche, r)


def svg(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], daten: bytes, r: tuple[float, float, float, float]) -> tuple[tuple[int, int, bytes], bool]:
    """Ein SVG-Bild in ``r``; → (Bild, gelungen)."""
    return _fw.svg(flaeche, daten, r)


def wordart_masse(text: str, schrift: str, pt: int) -> tuple[float, float]:
    """Breite und Höhe einer WordArt-Vorschau."""
    return _fw.wordart_masse(text, schrift, pt)


def wordart(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], text: str, nr: int, schrift: str, pt: int) -> tuple[int, int, bytes]:
    """WordArt nach einem der Stile der Galerie."""
    return _fw.wordart(flaeche, text, nr, schrift, pt)
