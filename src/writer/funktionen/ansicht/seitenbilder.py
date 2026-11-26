"""Die Bilder der Ansicht für die Oberfläche: Blatt, durchsichtige Ebene und Schreibmarke als fertige Bildpunkte ``(Breite, Höhe, RGBA)``.
Gerendert wird im Framework anhand der Kennung des Dokuments."""
from __future__ import annotations

from collections.abc import Sequence

from framework.befehle import ansicht as _fw
from writer.werte import Rechteck


def seitenbild(kennung: int, index: int, faktor: float, papier: str) -> tuple[int, int, bytes]:
    """Das Blatt ``index`` in der Auflösung ``faktor`` (Zoom mal Bildschirmfaktor) auf der Papierfarbe ``papier``."""
    return _fw.seitenbild(kennung, index, faktor, papier)


def ueberlagerung_setzen(kennung: int, formatzeichen: tuple[bool, bool], auswahlfarbe: tuple[int, int, int, int], gitter: bool, textgrenzen: bool,
                         lesefokus: float, zeilenfokus: bool, papier: str, markup: bool, autor_farben: Sequence[str],
                         wellen: Sequence[tuple[int, int, str]], treffer: Sequence[tuple[int, int]]) -> tuple[int, Rechteck] | None:
    """Vor dem Zeichnen: was über dem Text liegt; → (Seite, Rechteck) der Schreibmarke oder ``None``."""
    anzeige = _fw.Anzeige(tuple(formatzeichen), tuple(auswahlfarbe), bool(gitter), bool(textgrenzen), lesefokus, bool(zeilenfokus), papier, bool(markup),
                          tuple(autor_farben))
    marke = _fw.ueberlagerung_setzen(kennung, anzeige, tuple(wellen), tuple(treffer))
    return None if marke is None else (marke[0], Rechteck(*marke[1]))


def ueberlagerung_stand(kennung: int, index: int, faktor: float) -> tuple[int, bool]:
    """(Nummer, leer?) der durchsichtigen Ebene des Blattes: Die Nummer bleibt gleich, solange sich das Bild nicht ändert."""
    return _fw.ueberlagerung_stand(kennung, index, faktor)


def ueberlagerungsbild(kennung: int, index: int, faktor: float) -> tuple[int, int, bytes]:
    """Die durchsichtige Ebene des Blattes ``index`` in Geräte-Pixeln."""
    return _fw.ueberlagerungsbild(kennung, index, faktor)


def cursorbild(kennung: int, faktor: float, farbe: str) -> tuple[int, int, tuple[int, int, bytes]] | None:
    """Die Schreibmarke als kleines Bild: (x, y, Bild) mit der Lage in Geräte-Pixeln des Blattes."""
    return _fw.cursorbild(kennung, faktor, farbe)
