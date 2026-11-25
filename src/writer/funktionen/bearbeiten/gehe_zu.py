"""„Gehe zu“: ordnet die Bedienung des Reiters den Framework-Befehlen zu."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle


def gehe_zu_elemente() -> tuple[str, ...]:
    return _befehle.ELEMENTE


def gehe_zu_eingabe_titel(element: str) -> str:
    return _befehle.eingabe_titel(element)


def gehe_zu_hat_elemente(kennung: int, element: str) -> bool:
    return _befehle.hat_elemente(kennung, element)


def gehe_zu_element(kennung: int, element: str, eingabe: str = "", richtung: int = 1) -> bool:
    return _befehle.gehe_zu_element(kennung, element, eingabe, richtung)
