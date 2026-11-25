"""„Gehe zu“ (Reiter im Feld „Suchen und ersetzen“): Sprungziele des Dokuments über das Framework.

Die Fachlogik liegt in ``core.dokument.gehe_zu``; sie rechnet mit dem Kontext des Dokuments (Layout mit den Optionen der Ansicht). Ein Sprung
setzt nur die Auswahl, das Framework meldet ``auswahl_geaendert``, die Oberfläche zeigt daraufhin die Stelle."""
from __future__ import annotations

from core.dokument import GEHE_ZU_EINGABE, GEHE_ZU_ELEMENTE, gehe_zu_positionen, gehe_zu_springen, gehe_zu_ziel
from framework.befehle import im_kontext_bewegen, im_kontext_lesen

ELEMENTE: tuple[str, ...] = tuple(GEHE_ZU_ELEMENTE)


def eingabe_titel(element: str) -> str:
    """Beschriftung des Eingabefelds für die Elementart ``element``."""
    return GEHE_ZU_EINGABE.get(element, "Nummer eingeben:")


def hat_elemente(kennung: int, element: str) -> bool:
    """Enthält das Dokument mindestens ein Element dieser Art?"""
    return bool(im_kontext_lesen(kennung, lambda k: len(gehe_zu_positionen(k, element))))


def gehe_zu_element(kennung: int, element: str, eingabe: str = "", richtung: int = 1) -> bool:
    """Springt zum Element (``richtung`` 1 = weiter, -1 = zurück; ``eingabe`` wie im Kern). → ``False``, wenn es kein solches Ziel gibt."""
    def arbeit(k) -> int:
        pos = gehe_zu_ziel(k, element, eingabe, richtung)
        return 0 if pos is None else gehe_zu_springen(k, pos)
    return bool(im_kontext_bewegen(kennung, arbeit))
