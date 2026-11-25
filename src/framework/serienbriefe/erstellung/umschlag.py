"""Umschlag: Absender klein oben links, Empfänger rechts darunter, auf einem Dokumentmodell mit der Seiteneinrichtung des Umschlags."""
from __future__ import annotations

from core.bearbeitung import Bearbeitungssitzung
from core.dokument.dokument import Auswahl, Dokument, Position, neues_dokument
from core.dokument.abschnitte.seite import PageSettings
from framework.serienbriefe.platzhalter.konstanten import einzeilig
from core.geometrie import mm_to_px

UMSCHLAEGE = {"DIN lang (220 × 110 mm)": (220, 110), "C6 (162 × 114 mm)": (162, 114), "C5 (229 × 162 mm)": (229, 162),
              "C4 (324 × 229 mm)": (324, 229)}


def umschlag_erstellen(format_name: str, absender: str, empfaenger: str) -> tuple[Dokument, PageSettings]:
    """Das Dokument des Umschlags und seine Seiteneinrichtung; die Übernahme in den Editor ist Sache des Aufrufers."""
    b, h = UMSCHLAEGE[format_name]
    pg = PageSettings(width_mm=b, height_mm=h, margin_top_mm=12, margin_bottom_mm=10, margin_left_mm=15, margin_right_mm=12)
    neu = neues_dokument()
    s = Bearbeitungssitzung(neu)
    a = next(neu.absaetze())
    s.text_einfuegen(einzeilig(absender) + "\n" + einzeilig(empfaenger), Position(a.id, 0), format={})
    erster, zweiter = list(neu.absaetze())[:2]
    s.zeichenformat_anwenden({"groesse_pt": 8.0}, Auswahl(Position(erster.id, 0), Position(erster.id, erster.laenge)))
    s.zeichenformat_anwenden({"groesse_pt": 12.0}, Auswahl(Position(zweiter.id, 0), Position(zweiter.id, zweiter.laenge)))
    s.absatzformat_anwenden({"abstand_vor": mm_to_px(max(10, h * 0.2)), "einzug_links": mm_to_px(b * 0.42)}, absatz_ids=[zweiter.id])
    neu.abschnitte[0].seite = pg
    return neu, pg
