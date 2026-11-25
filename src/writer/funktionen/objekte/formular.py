"""Formularfelder: die Steuerung der Oberfläche. Reicht Abfragen und Befehle an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.felder import formular as befehle
from framework.schnittstellen.aenderungs_port import AenderungsPort
from framework.schnittstellen.datentypen.formulardaten import FeldTreffer, Feldbeschreibung

AKTIONEN: tuple[str, ...] = befehle.AKTIONEN
DATUMSFORMAT: str = befehle.DATUMSFORMAT
AKTION_ZURUECKSETZEN: str = befehle.AKTION_ZURUECKSETZEN
AKTION_DRUCKEN: str = befehle.AKTION_DRUCKEN
AKTION_PDF: str = befehle.AKTION_PDF


def meta(art: str, name: str = "", platzhalter: str = "", beschriftung: str = "", optionen: tuple[str, ...] = (), aufschrift: str = "",
         aktion: str = "") -> Feldbeschreibung:
    return befehle.meta(art, name, platzhalter, beschriftung, optionen, aufschrift, aktion)


def einfuegen(editor: AenderungsPort, m: Feldbeschreibung, wert: str | None = None) -> bool:
    return befehle.einfuegen(editor, m, wert)


def feld_an(editor: AenderungsPort, pos: int) -> FeldTreffer | None:
    return befehle.feld_an(editor, pos)


def ist_leer(editor: AenderungsPort, pos: int) -> bool:
    return befehle.ist_leer(editor, pos)


def wert_von(editor: AenderungsPort, v: int, e: int) -> str:
    return befehle.wert_von(editor, v, e)


def ersetzen(editor: AenderungsPort, v: int, e: int, m: Feldbeschreibung, text: str, leer: bool = False) -> bool:
    return befehle.ersetzen(editor, v, e, m, text, leer)


def kasten_umschalten(editor: AenderungsPort, v: int, e: int, m: Feldbeschreibung) -> bool:
    return befehle.kasten_umschalten(editor, v, e, m)


def alle_zuruecksetzen(editor: AenderungsPort) -> int:
    return befehle.alle_zuruecksetzen(editor)


def nur_formulardaten(editor: AenderungsPort) -> int:
    return befehle.nur_formulardaten(editor)
