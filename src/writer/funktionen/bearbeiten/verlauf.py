"""Verlauf eines Dokuments für die Oberfläche: mehrere Befehle als ein Schritt, Rückgängig und Wiederholen, Live-Vorschau, Nachverfolgen und der
Zustand „geändert“ – zugeordnet den Framework-Befehlen."""
from __future__ import annotations

from contextlib import contextmanager

from framework.befehle import bearbeiten as _befehle


@contextmanager
def schritt(kennung: int, name: str):
    """Alle Befehle im Block zählen als ein Schritt für Rückgängig; scheitert der Block, werden seine Änderungen zurückgenommen."""
    _befehle.verlauf_schritt_beginnen(kennung, name)
    try:
        yield
    except BaseException:
        _befehle.verlauf_schritt_abbrechen(kennung)
        raise
    _befehle.verlauf_schritt_beenden(kennung)


def rueckgaengig(kennung: int) -> bool:
    return _befehle.verlauf_rueckgaengig(kennung)


def wiederholen(kennung: int) -> bool:
    return _befehle.verlauf_wiederholen(kennung)


def vorschau_beginnen(kennung: int) -> None:
    """Den Stand vor einer Live-Vorschau merken."""
    _befehle.verlauf_vorschau_beginnen(kennung)


def vorschau_schritte(kennung: int) -> int:
    """Wie viele Schritte seit ``vorschau_beginnen`` dazugekommen sind."""
    return _befehle.verlauf_vorschau_schritte(kennung)


def vorschau_beenden(kennung: int, schritte: int) -> None:
    """Die Live-Vorschau zurücknehmen."""
    _befehle.verlauf_vorschau_beenden(kennung, schritte)


def nachverfolgen(kennung: int) -> bool:
    return _befehle.verlauf_nachverfolgen(kennung)


def nachverfolgen_setzen(kennung: int, an: bool) -> None:
    _befehle.verlauf_nachverfolgen_setzen(kennung, an)


def dokument_geaendert(kennung: int) -> bool:
    return _befehle.verlauf_geaendert(kennung)


def als_gespeichert_merken(kennung: int) -> None:
    _befehle.verlauf_als_gespeichert_merken(kennung)


def auswahl_text(kennung: int) -> str:
    return _befehle.verlauf_auswahl_text(kennung)


def textmarke_anspringen(kennung: int, name: str) -> bool:
    return _befehle.verlauf_textmarke_anspringen(kennung, name)


def bearbeiter_stempeln(kennung: int, autor: str) -> None:
    """Vor einer Änderung: Bearbeiter und Zeit für nachverfolgte Änderungen und Kommentare setzen."""
    _befehle.verlauf_stempeln(kennung, autor)


def dokument_beobachten(kennung: int, empfaenger):
    """``empfaenger()`` nach jeder Änderung des Dokuments aufrufen; → Funktion zum Abmelden."""
    from framework.ereignisse import melder
    from framework.schnittstellen.datentypen import Art
    _befehle.verlauf_beobachten(kennung)
    nummer = melder.abonnieren(Art.GEAENDERT, lambda ereignis: empfaenger() if ereignis.daten.get("kennung") == kennung else None)
    return lambda: melder.abmelden(nummer)
