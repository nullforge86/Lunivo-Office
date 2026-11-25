"""Formularfelder im Text: Textfeld, Kontrollkästchen, Schaltfläche. Arbeitet auf einer Bearbeitungssitzung (``s``); die Änderung gelangt über den Aufrufer
in den Editor."""
from __future__ import annotations

from core.suche.textsuche.suche import offset_zu_position
from core.dokument.dokument import Auswahl

KASTEN_LEER, KASTEN_VOLL = "☐", "☒"


def form_textfeld(s, text: str = "Text eingeben") -> None:
    s.text_einfuegen(f"[ {text} ]", format={"marker": "#f1f3f5", "unterstrichen": True, "unter_art": "gepunktet"})


def form_kasten(s, beschriftung: str = "Auswahl") -> None:
    with s.gruppe("Kontrollkästchen"):
        s.text_einfuegen(KASTEN_LEER, format={"groesse_pt": 14.0})
        s.text_einfuegen(" " + beschriftung, format={})


def form_knopf(s, aufschrift: str) -> None:
    s.text_einfuegen(f"  {aufschrift or 'Schaltfläche'}  ", format={"marker": "#dee2e6", "fett": True})


def kasten_ziel(s, pos: int):
    """Die Auswahl und der neue Text für den Klick auf ein Kontrollkästchen ☐/☒ an Zeichenstelle ``pos``; ``None``, wenn dort keines steht."""
    dok = s.dokument
    for p in (pos, pos - 1):
        if p < 0:
            continue
        von, bis = offset_zu_position(dok, p), offset_zu_position(dok, p + 1)
        if von.absatz_id != bis.absatz_id:
            continue
        auswahl = Auswahl(von, bis)
        t = s.text(auswahl)
        if t in (KASTEN_LEER, KASTEN_VOLL):
            return auswahl, (KASTEN_VOLL if t == KASTEN_LEER else KASTEN_LEER)
    return None
