"""Einstellungen der Funktion „Korrektur“ (Schreibhilfe): Schlüssel, Vorgaben, Lesen und Ändern.

Autokorrektur, Wellenlinien, Vorhersage, Sprache. Die Werte gehen als Parameter an den Kern; der Kern liest keine Einstellungen."""
from __future__ import annotations

from framework.schnittstellen.einstellungen import Einstellungen

VORSCHLAEGE = "schreibhilfe/vorschlaege"
KONSENS_GEGENPROBE = "schreibhilfe/konsens_gegenprobe"
THEMA = "schreibhilfe/thema"
PRUEFER_VORSILBE = "schreibhilfe/pruefer_"
SCHALTER_VORSILBE = "schreibhilfe/"
PRUEFSPRACHE = "pruefsprache"

VORGABEN = {VORSCHLAEGE: True, KONSENS_GEGENPROBE: False, THEMA: "egal", PRUEFSPRACHE: "de-DE"}


def schalter(e: Einstellungen, name: str, vorgabe: bool) -> bool:
    return e.get_bool(SCHALTER_VORSILBE + name, vorgabe)


def schalter_setzen(e: Einstellungen, name: str, wert: bool) -> None:
    e.set(SCHALTER_VORSILBE + name, wert)


def pruefer_aktiv(e: Einstellungen, name: str) -> bool:
    return e.get_bool(PRUEFER_VORSILBE + name, True)


def vorschlaege_anzeigen(e: Einstellungen) -> bool:
    return e.get_bool(VORSCHLAEGE, VORGABEN[VORSCHLAEGE])


def konsens_gegenprobe(e: Einstellungen) -> bool:
    return e.get_bool(KONSENS_GEGENPROBE, VORGABEN[KONSENS_GEGENPROBE])


def thema(e: Einstellungen) -> str:
    return e.get(THEMA, VORGABEN[THEMA])


def thema_setzen(e: Einstellungen, name: str) -> None:
    e.set(THEMA, name)


def pruefsprache(e: Einstellungen) -> str:
    return e.get(PRUEFSPRACHE, VORGABEN[PRUEFSPRACHE])


def pruefsprache_setzen(e: Einstellungen, kennung: str) -> None:
    e.set(PRUEFSPRACHE, kennung)
