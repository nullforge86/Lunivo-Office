"""Funde der Schreibhilfe für die Oberfläche über ``framework.anbindung.fund``: Die Oberfläche arbeitet mit dem unveränderlichen Fund-Typ des
Frameworks und bekommt Listen davon; Prüfen, Auflösen und Abstimmen rechnet der Kern."""
from __future__ import annotations

import framework.anbindung.fund as _fw
from framework.dokumentverwaltung.dokumentpflege import Gelernt


def gelernt() -> Gelernt:
    """Was die Schreibhilfe vom Benutzer gelernt hat (eigene Wörter, in Ruhe gelassene Funde)."""
    return Gelernt()


def fund(von: int, bis: int, alt: str, neu: str | None = None, grund: str = "", art: str = "fehler", wort_ebene: bool = False):
    """Ein neuer Fund (zum Beispiel ein Vorschlag aus dem Wörterbuch)."""
    return _fw.Fund(von=von, bis=bis, alt=alt, neu=neu, grund=grund, art=art, wort_ebene=wort_ebene)


def finde_probleme(text: str, gelernt_daten=None, schalter=None) -> list:
    """Alle Stellen des Textes, die auffällig sind."""
    return list(_fw.finde_probleme(text, gelernt_daten, schalter))


def verschieben(funde: list, pos: int, entfernt: int, hinzu: int) -> list:
    return list(_fw.verschieben(funde, pos, entfernt, hinzu))


def einsetzen(alt: list, von: int, bis: int, neue_relativ: list) -> list:
    return list(_fw.einsetzen(alt, von, bis, neue_relativ))


def markieren(funde: list, quelle: str, text_laenge: int | None = None) -> list:
    return list(_fw.markieren(funde, quelle, text_laenge))


def loesen(funde: list) -> list:
    return list(_fw.loesen(funde))


def abstimmen(funde: list, geprueft: dict | None = None, in_ruhe: dict | None = None, selbst: dict | None = None, gegenprobe: bool = False) -> list:
    return list(_fw.abstimmen(funde, geprueft, in_ruhe, selbst, gegenprobe))


def uebernimm_schreibweise(original: str, verbesserung: str) -> str:
    return _fw.uebernimm_schreibweise(original, verbesserung)


def wort_muster() -> str:
    """Das Muster (regulärer Ausdruck), nach dem die Prüfung Wörter im Text findet."""
    return _fw.wort_muster()


def wort_bekannt(wort: str) -> bool:
    return _fw.wort_bekannt(wort)


def autokorrigiere(text: str, schalter: dict) -> str:
    """Die Autokorrektur auf den Text vor der Schreibmarke anwenden; ``schalter``: Name der Regelgruppe → an?"""
    return _fw.autokorrigiere(text, schalter)


def thema_aufnehmen(woerter) -> None:
    _fw.thema_aufnehmen(woerter)
