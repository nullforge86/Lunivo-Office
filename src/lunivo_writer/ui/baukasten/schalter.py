"""Chips und an/aus-Schalter der Oberfläche — ein Baustein statt einzelner Stylesheets.

``chip_stil`` (Auswahl-Chip, gewählt = Akzent), ``chip_gruen_stil`` (grüner Schalter-Chip), ``schalter_an_stil``/``schalter_aus_stil``
(die „an/aus“-Kapseln der Werkbank, Größe ``CHIP_B`` × ``CHIP_H``). Die Farben werden bei jedem Aufruf aus ``Farbe`` gelesen (Thema gilt).
"""
from __future__ import annotations

from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.mass import PADDING_SCHALTER_CHIP, RADIUS_CHIP

CHIP_B, CHIP_H = 52, 26                      # Schalter-Chip „an/aus“: feste, großzügige Größe (Kapsel, Radius = halbe Höhe)


def chip_stil() -> str:
    """Auswahl-Chip mit Rahmen; gewählt: Akzentfläche."""
    return (('QPushButton { border: 1px solid palette(mid); border-radius: ' + str(RADIUS_CHIP) + 'px; padding: ' f"{PADDING_SCHALTER_CHIP}" '; color: palette(window-text); }QPushButton:checked { background: palette(highlight); color: palette(highlighted-text); border-color: palette(highlight); }'))


def chip_gruen_stil() -> str:
    """Grüner Schalter-Chip (gewählt = ``Farbe.AN``)."""
    return ("QPushButton { border: 1px solid palette(mid); border-radius: %dpx; padding: 0px; font-weight: bold; color: palette(window-text); }"
            "QPushButton:checked { background: %s; color: %s; border-color: %s; }" % (RADIUS_CHIP, Farbe.AN, Farbe.AN_SCHRIFT, Farbe.AN))


def schalter_an_stil() -> str:
    """Die Kapsel „an“ (gefüllt)."""
    return "background: %s; color: %s; border: 1px solid %s; border-radius: %dpx; font-weight: bold;" % (Farbe.AN, Farbe.AN_SCHRIFT, Farbe.AN, CHIP_H // 2)


def schalter_aus_stil() -> str:
    """Die Kapsel „aus“ (nur Rahmen)."""
    return "background: transparent; color: palette(mid); border: 1px solid palette(mid); border-radius: %dpx;" % (CHIP_H // 2)
