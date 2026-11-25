"""Freie Objekte (Textfeld, WordArt, Form, Bild): die Steuerung der Oberfläche. Reicht Abfragen an das Framework weiter; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from collections.abc import Hashable

from framework.befehle.objekte import freie_objekte as befehle
from framework.schnittstellen.datentypen.objektdaten import TextfeldVorgabe, WordartVorgabe
from framework.schnittstellen.freie_objekte_port import FreieObjektePort

TEXTFELD_STANDARD: TextfeldVorgabe = befehle.TEXTFELD_STANDARD
WORDART_STANDARD: WordartVorgabe = befehle.WORDART_STANDARD


def ist_verknuepft(editor: FreieObjektePort, schluessel: Hashable) -> bool:
    return befehle.ist_verknuepft(editor, schluessel)


def ohne_hilfsangaben(schluessel: tuple[str, ...]) -> tuple[str, ...]:
    return befehle.ohne_hilfsangaben(schluessel)
