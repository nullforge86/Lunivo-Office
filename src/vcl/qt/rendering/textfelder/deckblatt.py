from __future__ import annotations
import dataclasses
from writer.funktionen import bearbeiten as _bearbeiten
import copy
from PySide6.QtGui import QImage
from writer.werte import Bereich, Stelle
from writer.werte import mm_zu_px as mm_to_px
from writer.funktionen.objekte import deckblatt_entfernen
from writer.funktionen.objekte import deckblatt_felder


def zeichnen(p, name: str, r, mit_text: bool = True) -> None:
    """Gestaltung ``name`` auf das Blatt ``r`` (QPainter, QRectF): für die Galerie."""
    from vcl.qt.rendering.formen import raster_malen
    from writer.anbindung import zeichnen as ZW
    raster_malen(p, r, lambda f: ZW.deckblatt(f, name, (r.x(), r.y(), r.width(), r.height()), mit_text))                  # der Kern zeichnet, Qt legt nur das fertige Bild auf


def grafik_bild(name: str, breite_px: int, hoehe_px: int) -> QImage:
    from vcl.qt.rendering.formen import raster_bild
    from writer.anbindung import zeichnen as ZW
    return raster_bild(breite_px, hoehe_px, lambda f: ZW.deckblatt_grafik(f, name, (0, 0, breite_px, hoehe_px)), (255, 255, 255, 255))


def einfuegen(ed, name: str, quer: bool = False) -> None:
    """Deckblatt ``name`` als ersten Abschnitt an den Anfang setzen (ersetzt ein vorhandenes)."""
    deckblatt_entfernen(ed.kennung)            # ein vorhandenes Deckblatt nimmt das Framework heraus
    alt = copy.deepcopy(ed.page)
    rest = copy.deepcopy(alt)                           # das Dokument nach dem Deckblatt: alles wie bisher, Wasserzeichen nur dort
    rest.watermark = {**(alt.watermark or {}), "abschnitt": True} if alt.watermark else {"abschnitt": True, "deckblatt_leer": True}
    deck = copy.deepcopy(alt)
    deck.set_orientation(quer)
    for hf in ("header", "footer", "first_header", "first_footer", "even_header", "even_footer"):
        getattr(deck, hf).text = ""
    deck.diff_first = False
    bw, bh = mm_to_px(deck.width_mm), mm_to_px(deck.height_mm)
    deck.watermark = {"bild": _bild_text(grafik_bild(name, round(bw), round(bh))), "bild_name": f"Deckblatt {name}", "ganzseitig": True,
                      "auswaschen": False, "transparenz": 0, "winkel": 0, "abschnitt": True}
    links_px, rechts_px = mm_to_px(deck.margin_left_mm), mm_to_px(deck.margin_right_mm)

    felder = deckblatt_felder(name, bw, bh, quer, mm_to_px(deck.margin_top_mm), links_px, rechts_px)        # Lage und Schrift je Feld rechnet der Kern

    ed.ansicht._befehl(lambda: _bearbeiten.aenderung_deckblatt_einfuegen(ed.kennung, felder, dataclasses.asdict(deck), dataclasses.asdict(rest)))


def _bild_text(img: QImage) -> str:
    from vcl.qt.rendering.textfelder.wasserzeichen import bild_zu_text
    return bild_zu_text(img)
