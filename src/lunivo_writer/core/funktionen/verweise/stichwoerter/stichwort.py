"""Stichwörter (Indexeinträge) im Text markieren: an der Markierung, an allen gleichen Stellen oder als einfacher Begriff."""
from __future__ import annotations

from lunivo_writer.core.dokument.dokument import Auswahl


def index_eintragen(ed, e, alle: bool = False) -> int:
    """Indexeintrag ``e`` (``stichwoerter.indexeintrag.Eintrag``) an die Markierung setzen (ohne Markierung: das Wort an der
    Schreibmarke); ``alle`` markiert jede Stelle im Dokument mit demselben Text. Gibt die Zahl der markierten Stellen zurück."""
    s = ed.sitzung
    if not e.haupt:
        return 0
    start, ende = s._bereich_oder_wort(None)
    stellen = [Auswahl(start, ende)]
    if alle:
        such = s.text(Auswahl(start, ende))
        stellen = s.suche(such, gross_klein=True) or stellen
    zaehler = [0]

    def f(sitz):
        with sitz.gruppe("Indexeintrag"):
            for st in stellen:
                sitz.index_eintragen(e.text(), e.schalter(), st)
                zaehler[0] += 1
    ed.ansicht._aendern(f)
    return zaehler[0]


def index_markieren(ed, term: str) -> bool:
    s = ed.sitzung
    try:
        start, ende = s._bereich_oder_wort(None)
    except Exception:
        return False
    return ed.ansicht._aendern(lambda sitz: sitz.index_eintragen(term or sitz.text(Auswahl(start, ende)), "", Auswahl(start, ende)))
