"""Einstellungen der Funktion „Ansicht“: Schlüssel, Vorgaben, Lesen und Ändern (Lineal, versteckter Text, Oberflächenart, Thema)."""
from __future__ import annotations

from framework.schnittstellen.einstellungen import Einstellungen

LINEAL = "ansicht/lineal"
LINEAL_HOCH = "ansicht/lineal_hoch"
VERSTECKT_ZEIGEN = "ui/versteckt_zeigen"
OBERFLAECHE = "ui/oberflaeche"
THEMA = "theme"
WEICH = "ui/weich"

VORGABEN = {LINEAL: False, LINEAL_HOCH: False, VERSTECKT_ZEIGEN: False, OBERFLAECHE: "register", THEMA: "system", WEICH: False}


def lineal_zeigen(e: Einstellungen) -> bool:
    return e.get_bool(LINEAL, VORGABEN[LINEAL])


def lineal_umschalten(e: Einstellungen) -> None:
    e.set(LINEAL, not lineal_zeigen(e))


def lineal_hoch_zeigen(e: Einstellungen) -> bool:
    return e.get_bool(LINEAL_HOCH, VORGABEN[LINEAL_HOCH])


def lineal_hoch_umschalten(e: Einstellungen) -> None:
    e.set(LINEAL_HOCH, not lineal_hoch_zeigen(e))


def verstecktes_zeigen(e: Einstellungen) -> bool:
    return e.get_bool(VERSTECKT_ZEIGEN, VORGABEN[VERSTECKT_ZEIGEN])


def verstecktes_umschalten(e: Einstellungen) -> None:
    e.set(VERSTECKT_ZEIGEN, not verstecktes_zeigen(e))


def symbolleisten_statt_register(e: Einstellungen) -> bool:
    return e.get(OBERFLAECHE, VORGABEN[OBERFLAECHE]) == "symbolleisten"


def oberflaeche_umschalten(e: Einstellungen) -> None:
    e.set(OBERFLAECHE, "register" if symbolleisten_statt_register(e) else "symbolleisten")


OBERFLAECHE_SCHLUESSEL = ("ui/register_plan", "ui/schnellzugriff", "ui/symbol_tausch", "ui/oberflaeche")


def oberflaeche_zuruecksetzen(e: Einstellungen) -> None:
    """Register, Schnellzugriff, ausgetauschte Symbole und Oberflächenart auf die Vorgabe zurücksetzen."""
    for schluessel in OBERFLAECHE_SCHLUESSEL:
        e.remove(schluessel)


def thema(e: Einstellungen) -> str:
    return e.get(THEMA, VORGABEN[THEMA])


def weich(e: Einstellungen) -> bool:
    return e.get_bool(WEICH, VORGABEN[WEICH])
