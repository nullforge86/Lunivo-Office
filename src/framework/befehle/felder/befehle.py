"""Befehle der Funktion „Felder“ (Formularfelder im Text): Textfeld, Kontrollkästchen, Schaltfläche und das Umschalten eines Kästchens per Klick."""
from __future__ import annotations

from framework.schnittstellen.aenderungs_port import AenderungsPort
from core.dokument import formularfelder
from framework.befehle.felder.formular import _geschuetzt


def form_textfeld(editor: AenderungsPort, text: str = "Text eingeben") -> None:
    editor.aendern(_geschuetzt(lambda sitzung: formularfelder.form_textfeld(sitzung, text)))


def form_kasten(editor: AenderungsPort, beschriftung: str = "Auswahl") -> None:
    editor.aendern(_geschuetzt(lambda sitzung: formularfelder.form_kasten(sitzung, beschriftung)))


def form_knopf(editor: AenderungsPort, aufschrift: str) -> None:
    editor.aendern(_geschuetzt(lambda sitzung: formularfelder.form_knopf(sitzung, aufschrift)))


def kasten_umschalten(editor: AenderungsPort, pos: int) -> bool:
    """Klick auf ein Kontrollkästchen ☐/☒ wechselt den Zustand; ``False``, wenn an der Stelle keines steht."""
    ziel = editor.lesen(lambda sitzung: formularfelder.kasten_ziel(sitzung, pos))
    if ziel is None:
        return False
    auswahl, neu = ziel
    return editor.aendern(_geschuetzt(lambda sitzung: sitzung.ersetzen(neu, auswahl)))
