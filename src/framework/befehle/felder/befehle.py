"""Befehle der Funktion „Felder“ (Formularfelder im Text): Textfeld, Kontrollkästchen, Schaltfläche und das Umschalten eines Kästchens per Klick."""
from __future__ import annotations

from core.dokument import formularfelder
from framework.befehle.felder.formular import _geschuetzt, _sitzung


def form_textfeld(kennung: int, text: str = "Text eingeben") -> None:
    _geschuetzt(lambda sitzung: formularfelder.form_textfeld(sitzung, text))(_sitzung(kennung))


def form_kasten(kennung: int, beschriftung: str = "Auswahl") -> None:
    _geschuetzt(lambda sitzung: formularfelder.form_kasten(sitzung, beschriftung))(_sitzung(kennung))


def form_knopf(kennung: int, aufschrift: str) -> None:
    _geschuetzt(lambda sitzung: formularfelder.form_knopf(sitzung, aufschrift))(_sitzung(kennung))


def kasten_umschalten(kennung: int, pos: int) -> bool:
    """Klick auf ein Kontrollkästchen ☐/☒ wechselt den Zustand; ``False``, wenn an der Stelle keines steht."""
    ziel = (lambda sitzung: formularfelder.kasten_ziel(sitzung, pos))(_sitzung(kennung))
    if ziel is None:
        return False
    auswahl, neu = ziel
    return _geschuetzt(lambda sitzung: sitzung.ersetzen(neu, auswahl))(_sitzung(kennung))
