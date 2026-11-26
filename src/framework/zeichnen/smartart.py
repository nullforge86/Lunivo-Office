"""SmartArt zeichnen: Der Kern hält, was zum Dokument gehört (Knoten, Formate, Schrift), setzt und zeichnet den Text; die Oberfläche zeichnet nur ihre Formen."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from framework.anbindung import Daten, fest
from framework.zeichnen.raster import Flaeche, Rasterbild, Rechteck, _malen, _rect


def smartart_beginnen(knoten: Sequence[Mapping[str, Daten]], formate: Sequence[Mapping[str, Daten] | None], format_alle: Mapping[str, Daten]) -> None:
    """Ein neues SmartArt wird gezeichnet: Knoten, das Format je Knoten und das Format aller Knoten."""
    from core.objekte.smartart import beginnen
    beginnen(knoten, formate, format_alle)


def smartart_schrift(pt: float) -> None:
    """Die Schrift des nächsten Textes: die Grundschrift des Dokuments in der Größe ``pt``."""
    from core.objekte.smartart import grundschrift_setzen
    grundschrift_setzen(pt)


def smartart_schrift_uebernehmen(t: Mapping[str, Daten] | None) -> None:
    """Die Schrift bekommt die Angaben des Textformats ``t`` (Name, Größe, fett, kursiv) über der aktuellen Schrift."""
    from core.objekte.smartart import schrift_uebernehmen
    schrift_uebernehmen(t)


def smartart_format_von(nr: int | None) -> Mapping[str, Daten] | None:
    """Das Format des Knotens Nummer ``nr``: das des Knotens über dem von allen Knoten."""
    from core.objekte.smartart import format_von
    return fest(format_von(nr))


def smartart_gruppen(pts: Sequence[tuple[int, str]]) -> Daten:
    """Oberste Ebene als Überschrift, alles Eingerückte darunter als Unterpunkte: [(Nr. der Überschrift, Text, [(Nr., Unterpunkt)])]."""
    from core.objekte.smartart import gruppen
    return fest(gruppen(pts))


def smartart_baum(pts: Sequence[tuple[int, str]]) -> Daten:
    """Die Wurzeln des Knotenbaums; jeder Knoten {i (Nr.), t (Text), e (Ebene), k (Kinder), a (Assistent)}."""
    from core.objekte.smartart import baum
    return fest(baum(pts))


def smartart_text(flaeche: Flaeche, text: str, r: Rechteck, farbe: tuple[int, int, int, int], ausrichtung: str, umbruch: bool) -> Rasterbild:
    """Den Text eines Kastens in der aktuellen Schrift setzen und zeichnen (senkrecht mittig)."""
    from core.layout.drucklayout.ausgabe import Style
    from core.objekte.smartart import schrift
    spec = schrift()
    stil = Style(color=farbe)
    return _malen(flaeche, lambda z: z.draw_text_box(text, _rect(r), spec, stil, ausrichtung, umbruch, "center"))
