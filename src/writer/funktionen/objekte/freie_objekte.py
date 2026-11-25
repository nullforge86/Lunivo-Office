"""Freie Objekte (Textfeld, WordArt, Form, Bild): die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from framework.befehle.objekte import freie_objekte as befehle
from framework.schnittstellen.datentypen.objektdaten import TextfeldVorgabe, WordartVorgabe

TEXTFELD_STANDARD: TextfeldVorgabe = befehle.TEXTFELD_STANDARD
WORDART_STANDARD: WordartVorgabe = befehle.WORDART_STANDARD


def ist_verknuepft(kennung: int, schluessel: tuple[str, int]) -> bool:
    return befehle.ist_verknuepft(kennung, schluessel)


def textfeld_hat_nachfolger(kennung: int, schluessel: tuple[str, int]) -> bool:
    return befehle.hat_nachfolger(kennung, schluessel)


def ohne_hilfsangaben(schluessel: tuple[str, ...]) -> tuple[str, ...]:
    return befehle.ohne_hilfsangaben(schluessel)
