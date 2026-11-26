"""Formularfelder: die Steuerung der Oberfläche. Reicht Abfragen und Befehle an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.felder import formular as befehle
from framework.schnittstellen.datentypen.formulardaten import FeldTreffer, Feldbeschreibung
from writer.werte import unveraenderlich


def formular_aktionen() -> tuple[str, ...]:
    return unveraenderlich(befehle.AKTIONEN)


def formular_datumsformat() -> str:
    return str(befehle.DATUMSFORMAT)


def formular_aktion_zuruecksetzen() -> str:
    return str(befehle.AKTION_ZURUECKSETZEN)


def formular_aktion_drucken() -> str:
    return str(befehle.AKTION_DRUCKEN)


def formular_aktion_pdf() -> str:
    return str(befehle.AKTION_PDF)

def meta(art: str, name: str = "", platzhalter: str = "", beschriftung: str = "", optionen: tuple[str, ...] = (), aufschrift: str = "",
         aktion: str = "") -> Feldbeschreibung:
    return befehle.meta(art, name, platzhalter, beschriftung, optionen, aufschrift, aktion)


def einfuegen(kennung: int, m: Feldbeschreibung, wert: str | None = None) -> bool:
    return befehle.einfuegen(kennung, m, wert)


def feld_an(kennung: int, pos: int) -> FeldTreffer | None:
    return befehle.feld_an(kennung, pos)


def ist_leer(kennung: int, pos: int) -> bool:
    return befehle.ist_leer(kennung, pos)


def wert_von(kennung: int, v: int, e: int) -> str:
    return befehle.wert_von(kennung, v, e)


def ersetzen(kennung: int, v: int, e: int, m: Feldbeschreibung, text: str, leer: bool = False) -> bool:
    return befehle.ersetzen(kennung, v, e, m, text, leer)


def kasten_umschalten(kennung: int, v: int, e: int, m: Feldbeschreibung) -> bool:
    return befehle.kasten_umschalten(kennung, v, e, m)


def alle_zuruecksetzen(kennung: int) -> int:
    return befehle.alle_zuruecksetzen(kennung)


def nur_formulardaten(kennung: int) -> int:
    return befehle.nur_formulardaten(kennung)
