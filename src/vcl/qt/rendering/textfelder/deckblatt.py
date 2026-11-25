from __future__ import annotations
import copy
from PySide6.QtGui import QImage
from vcl.qt.rendering.formen import rect_from_qt
from core.dokument.dokument import Auswahl, Position
from core.geometrie import Rect
from framework.dokumentverwaltung.ausgabe.textsatz import standard_engine
from core.dokument.abschnitte.seite import mm_to_px
from core.dokument.abschnitte.deckblatt_vorlagen import _grafik, _schrift, entfernen, gestaltung, zeichnen_mit


def zeichnen(p, name: str, r, mit_text: bool = True) -> None:
    """Gestaltung ``name`` auf das Blatt ``r`` (QPainter, QRectF): für die Galerie."""
    from vcl.qt.rendering.formen import kern_malen
    kern_malen(p, r, lambda z: zeichnen_mit(z, name, rect_from_qt(r), mit_text, standard_engine()))                  # der Kern zeichnet, Qt legt nur das fertige Bild auf


def grafik_bild(name: str, breite_px: int, hoehe_px: int) -> QImage:
    from vcl.qt.rendering.formen import kern_bild
    return kern_bild(breite_px, hoehe_px, lambda z: _grafik(z, name, Rect(0, 0, breite_px, hoehe_px)), (255, 255, 255, 255))


def einfuegen(ed, name: str, quer: bool = False) -> None:
    """Deckblatt ``name`` als ersten Abschnitt an den Anfang setzen (ersetzt ein vorhandenes)."""
    entfernen(ed)
    g = gestaltung(name)
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

    def f(s):
        with s.gruppe("Deckblatt"):
            erster = next(s.dokument.absaetze())
            s.text_einfuegen("\n".join(x.text for x in g.felder) + "\n", s.dokument.anfang(), format={})
            absaetze = list(s.dokument.absaetze())
            y = mm_to_px(deck.margin_top_mm)
            for feld, a in zip(g.felder, absaetze):
                spec = _schrift(feld, bh if not quer else bw, quer)
                ziel = feld.y * bh
                af = {"abstand_vor": max(0.0, ziel - y) or None, "deckblatt": name,
                      "ausrichtung": {"links": "links", "mitte": "mitte", "rechts": "rechts"}[feld.ausrichtung]}
                if feld.ausrichtung == "links":
                    af["einzug_links"] = max(0.0, feld.x * bw - links_px) or None
                else:
                    af["einzug_links"] = max(0.0, 0.1 * bw - links_px) or None
                    af["einzug_rechts"] = max(0.0, 0.1 * bw - rechts_px) or None
                zf = {"schrift": feld.schrift, "groesse_pt": feld.pt * (0.85 if quer else 1.0), "farbe": feld.farbe, "fett": True if feld.fett else None}
                s.absatzformat_anwenden(af, absatz_ids=[a.id])
                s.absatz_zeichenformat_anwenden(zf, absatz_ids=[a.id])
                if a.laenge:
                    s.zeichenformat_anwenden(zf, Auswahl(Position(a.id, 0), Position(a.id, a.laenge)))
                m = standard_engine().font_metrics(spec)
                y = max(y, ziel) + (m.ascent + m.descent) * 1.15
            s.abschnitt_einfuegen(Position(erster.id, 0), "naechste", rest)       # das Dokument beginnt hinter dem Deckblatt auf einem neuen Blatt
            s.seite_ersetzen(0, deck)
            s.setze_auswahl(Position(absaetze[0].id, 0))
    ed.ansicht._aendern(f)


def _bild_text(img: QImage) -> str:
    from vcl.qt.rendering.textfelder.wasserzeichen import bild_zu_text
    return bild_zu_text(img)
