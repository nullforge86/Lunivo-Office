"""Anbindung der Oberfläche an ``framework.zeichnen``: Zeichnungen des Kerns als fertiges Rasterbild (Fläche und Rechtecke als einfache Tupel)."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

import framework.zeichnen as _fw
from framework.schnittstellen import BlasenSchrift
from writer.werte import eigene_kopie


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


def diagramm(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], r: tuple[float, float, float, float], d: Mapping, mit_geo: bool=False) -> tuple[tuple[int, int, bytes], dict]:
    """Das Diagramm ``d`` in ``r``; → (Bild, Rechtecke der Teile als ``(x, y, Breite, Höhe)``, bei mehreren Balken als Liste)."""
    bild, geo = _fw.diagramm(flaeche, r, d, mit_geo)
    return bild, eigene_kopie(geo)


def seitenrahmen_rechteck(b: Mapping, raender_mm: tuple[float, float, float, float], seite: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
    """Das Rechteck des Seitenrahmens ``b`` auf einer Seite mit dem Rechteck ``seite``; ``raender_mm``: Seitenränder (links, oben, rechts, unten)."""
    return _fw.seitenrahmen_rechteck(b, raender_mm, seite)


def seitenrahmen(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], b: Mapping, raender_mm: tuple[float, float, float, float], seite: tuple[float, float, float, float]) -> tuple[int, int, bytes]:
    """Den Seitenrahmen ``b`` auf eine Seite zeichnen (Linie in ihrer Art oder Kunstrahmen)."""
    return _fw.seitenrahmen(flaeche, b, raender_mm, seite)


def bild(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], r: tuple[float, float, float, float], daten: bytes, ellipse: bool, rand: Mapping | None, dreh: float, fuell: Mapping | None, fuellbild: bytes | None, fx: Mapping | None) -> tuple[int, int, bytes]:
    """Ein Bild in ``r`` mit Füllung, Kontur, Drehung und Effekten."""
    return _fw.bild(flaeche, r, daten, ellipse, rand, dreh, fuell, fuellbild, fx)


def text_mit_effekt(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], text: str, mitte: tuple[float, float], schrift: tuple[str, float, int, bool], farbe: tuple[int, int, int, int], fx: Mapping, kontur: tuple[tuple[int, int, int, int], float] | None=None) -> tuple[int, int, bytes]:
    """Text mit Effekt, um ``mitte`` zentriert; ``schrift``: (Familie, Größe in pt, Gewicht, kursiv); ``kontur``: (Farbe, Breite in Bildpunkten)."""
    return _fw.text_mit_effekt(flaeche, text, mitte, schrift, farbe, fx, kontur)


def form(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], ops: Sequence[tuple], offen: bool, ist_linie: bool, vertikal: bool, kasten: tuple[float, float, float, float], fuell: str, fuell_art: str, linie: str, strich: float, text: str) -> tuple[int, int, bytes]:
    """Eine Form aus ihrem Umriss ``ops`` im Rechteck ``kasten``: Füllung, Kontur und Text; ``vertikal``: Textfeld mit senkrecht laufendem Text."""
    return _fw.form(flaeche, ops, offen, ist_linie, vertikal, kasten, fuell, fuell_art, linie, strich, text)


def formel(teile: Sequence[tuple[str, str]], pt: int, farbe: str) -> tuple[int, int, bytes]:
    """Die Formel aus ihren Stücken ``(Text, "normal" | "hoch" | "tief")`` als Bild."""
    return _fw.formel(teile, pt, farbe)


def wordart_stil(text: str, stil: str, schrift: str, pt: int, farbe: str, regenbogen: Sequence[str]) -> tuple[int, int, bytes]:
    """WordArt in einem der älteren Stile (Verlauf, Schatten, Umriss, Regenbogen, Welle); ``regenbogen``: die Farben des Regenbogenverlaufs."""
    return _fw.wordart_stil(text, stil, schrift, pt, farbe, regenbogen)


def datei_symbol(name: str, symbol: tuple[int, int, bytes], breite: int, farbe: str) -> tuple[int, int, bytes]:
    """Dateisymbol (``symbol``: Breite, Höhe, Bildpunkte als RGBA) mit dem Namen darunter."""
    return _fw.datei_symbol(name, symbol, breite, farbe)


def smartart_beginnen(knoten: Sequence[Mapping], formate: Sequence[Mapping | None], format_alle: Mapping) -> None:
    """Ein neues SmartArt wird gezeichnet: Knoten, das Format je Knoten und das Format aller Knoten."""
    _fw.smartart_beginnen(knoten, formate, format_alle)


def smartart_schrift(pt: float) -> None:
    """Die Schrift des nächsten Textes: die Grundschrift des Dokuments in der Größe ``pt``."""
    _fw.smartart_schrift(pt)


def smartart_schrift_uebernehmen(t: Mapping | None) -> None:
    """Die Schrift bekommt die Angaben des Textformats ``t`` (Name, Größe, fett, kursiv) über der aktuellen Schrift."""
    _fw.smartart_schrift_uebernehmen(t)


def smartart_format_von(nr: int | None) -> dict | None:
    """Das Format des Knotens Nummer ``nr``: das des Knotens über dem von allen Knoten."""
    return eigene_kopie(_fw.smartart_format_von(nr))


def smartart_gruppen(pts: Sequence[tuple[int, str]]) -> list[tuple[int, str, list[tuple[int, str]]]]:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])]."""
    return eigene_kopie(_fw.smartart_gruppen(pts))


def smartart_baum(pts: Sequence[tuple[int, str]]) -> list[dict]:
    """Die Wurzeln des Knotenbaums; jeder Knoten {i (Nr.), t (Text), e (Ebene), k (Kinder), a (Assistent)}."""
    return eigene_kopie(_fw.smartart_baum(pts))


def smartart_text(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], text: str, r: tuple[float, float, float, float], farbe: tuple[int, int, int, int], ausrichtung: str, umbruch: bool) -> tuple[int, int, bytes]:
    """Den Text eines Kastens in der aktuellen Schrift setzen und zeichnen (senkrecht mittig)."""
    return _fw.smartart_text(flaeche, text, r, farbe, ausrichtung, umbruch)


def textfeld_setzen(d: Mapping, laeufe: Sequence[Mapping], b: float, h: float, standard_farbe: str, farbe_ueber: str | None=None) -> int:
    """Den Text eines Textfelds in ein Feld ``b`` × ``h`` setzen; → Nummer des Satzes (mit ``textfeld_freigeben`` beenden)."""
    return _fw.textfeld_setzen(d, laeufe, b, h, standard_farbe, farbe_ueber)


def textfeld_freigeben(nummer: int) -> None:
    _fw.textfeld_freigeben(nummer)


def textfeld_zeilen(nummer: int) -> tuple[tuple[float, float, float, float], ...]:
    """Die Rechtecke ``(x, y, Breite, Höhe)`` der Textzeilen, die auf dem Feld stehen."""
    return _fw.textfeld_zeilen(nummer)


def textfeld_hoehe(nummer: int) -> float:
    """Obere Kante des Innenraums bis zur Unterkante der letzten Zeile auf dem Feld."""
    return _fw.textfeld_hoehe(nummer)


def textfeld_farbe(nummer: int) -> str:
    return _fw.textfeld_farbe(nummer)


def textfeld_blatt(nummer: int) -> tuple[float, float]:
    """Breite und Höhe des gesetzten Feldes in Bildpunkten (96 dpi)."""
    return _fw.textfeld_blatt(nummer)


def textfeld_bild(nummer: int, faktor: float) -> tuple[int, int, bytes]:
    """Der gesetzte Text des Feldes (durchsichtiger Grund) in der Auflösung ``faktor``."""
    return _fw.textfeld_bild(nummer, faktor)


def textfeld_passt(d: Mapping, laeufe: Sequence[Mapping], b: float, h: float, standard_farbe: str) -> int:
    """Wie viele Zeichen der Läufe im Feld ``b`` × ``h`` stehen — für verknüpfte Textfelder."""
    return _fw.textfeld_passt(d, laeufe, b, h, standard_farbe)


def wordart_objekt(d: Mapping) -> tuple[tuple[int, int, bytes], tuple[tuple[int, int], ...]]:
    """Das WordArt-Objekt ``d`` als Bild in doppelter Auflösung; dazu (oben, Höhe) jeder Zeile in Bildpunkten des Bildes."""
    return _fw.wordart_objekt(d)


def absaetze(flaeche: tuple[float, float, float, float, float, tuple[int, int, int, int]], r: tuple[float, float, float, float], texte: Sequence[tuple[Mapping, Mapping, str]], mittig: bool=False) -> tuple[int, int, bytes]:
    """Absätze (Absatzformat, Zeichenformat, Text) in das Rechteck ``r`` setzen und zeichnen: die Vorschau der Formatierungsfenster."""
    return _fw.absaetze(flaeche, r, texte, mittig)
