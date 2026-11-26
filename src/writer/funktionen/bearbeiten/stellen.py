"""Textstellen und Auswahl für die Ansicht: ordnet die Bedienung den Framework-Befehlen zu; Stellen als Werte der Oberfläche (``Stelle``, ``Bereich``)."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle
from writer.werte import Bereich, Stelle, eigene_kopie


def auswahl(kennung: int) -> Bereich:
    """Die Auswahl (Anker und Kopf); ``leer``: nur die Schreibmarke."""
    anker, kopf = _befehle.stellen_auswahl(kennung)
    return Bereich(Stelle(*anker), Stelle(*kopf))


def auswahl_bereich(kennung: int) -> tuple[Stelle, Stelle]:
    """(Anfang, Ende) der Auswahl in Dokumentreihenfolge."""
    start, ende = _befehle.stellen_bereich(kennung)
    return Stelle(*start), Stelle(*ende)


def auswahl_setzen(kennung: int, anker: tuple[int, int], kopf: tuple[int, int]) -> None:
    _befehle.stellen_auswahl_setzen(kennung, (anker[0], anker[1]), (kopf[0], kopf[1]))


def gehen(kennung: int, ziel: tuple[int, int], auswaehlen: bool) -> None:
    """Die Schreibmarke an ``ziel`` setzen; mit ``auswaehlen`` bleibt der Anker stehen."""
    _befehle.stellen_gehen(kennung, (ziel[0], ziel[1]), bool(auswaehlen))


def alles_auswaehlen(kennung: int) -> None:
    _befehle.stellen_alles_auswaehlen(kennung)


def zeichenformat_bei(kennung: int, stelle: tuple[int, int]) -> dict:
    """Das Zeichenformat an der Stelle (eigene Kopie)."""
    return eigene_kopie(_befehle.stellen_zeichenformat_bei(kennung, (stelle[0], stelle[1])))


def absatz_laenge(kennung: int, absatz_id: int) -> int:
    return _befehle.stellen_absatz_laenge(kennung, absatz_id)


def stelle_im_text(kennung: int, stelle: tuple[int, int]) -> int:
    """Die Stelle als Zeichenstelle im Rohtext (Absätze durch ein Zeichen getrennt)."""
    return _befehle.stellen_stelle_im_text(kennung, (stelle[0], stelle[1]))


def stelle_von(kennung: int, im_text: int) -> Stelle:
    """Die Zeichenstelle im Rohtext als ``Stelle``."""
    return Stelle(*_befehle.stellen_stelle_von(kennung, im_text))


def objekt_vorhanden(kennung: int, objekt_id: int) -> bool:
    return _befehle.stellen_objekt_vorhanden(kennung, objekt_id)


def tabellenzellen(kennung: int, absatz_id: int) -> tuple[int, int, tuple[tuple[int, int], ...], tuple[int, int]] | None:
    """Die Tabelle, in deren Zelle der Absatz steht: (Tabellen-Id, Zeilenzahl, sichtbare Zellen in Lesereihenfolge, Zelle des Absatzes)."""
    return _befehle.stellen_tabellenzellen(kennung, absatz_id)


def sichtbare_zellen(kennung: int, tabellen_id: int) -> tuple[tuple[int, int], ...]:
    """Die sichtbaren Zellen der Tabelle (ohne verbundene, verdeckte) in Lesereihenfolge."""
    return _befehle.stellen_sichtbare_zellen(kennung, tabellen_id)


def zelle_anfang(kennung: int, tabellen_id: int, zeile: int, spalte: int) -> Stelle:
    """Die erste Textstelle der Zelle."""
    return Stelle(*_befehle.stellen_zelle_anfang(kennung, tabellen_id, zeile, spalte))


def tabellenmasse(kennung: int, tabellen_id: int) -> tuple[int, int, dict]:
    """(Zeilen, Spalten, (Zeile, Spalte) → (Zeilenspanne, Spaltenspanne)) der Tabelle."""
    zeilen, spalten, spannen = _befehle.stellen_tabellenmasse(kennung, tabellen_id)
    return zeilen, spalten, eigene_kopie(spannen)


def ausschnitt_kopieren(kennung: int) -> tuple[str, str] | None:
    """Die Auswahl für die Zwischenablage: (reiner Text, Ausschnitt als JSON-Text); ``None`` ohne Auswahl."""
    return _befehle.stellen_ausschnitt_kopieren(kennung)


def ausschnitt_gueltig(inhalt: str) -> bool:
    return _befehle.stellen_ausschnitt_gueltig(inhalt)


def ausschnitt_einsetzen(kennung: int, inhalt: str) -> bool:
    """Den Ausschnitt an der Auswahl einfügen; ``False``, wenn der Kern ablehnt."""
    return _befehle.stellen_ausschnitt_einsetzen(kennung, inhalt)


def lauf_format_bei(kennung: int, stelle: tuple[int, int]) -> dict:
    """Das eigene Format des Textstücks an der Stelle (leer am Absatzende)."""
    return eigene_kopie(_befehle.stellen_lauf_format_bei(kennung, (stelle[0], stelle[1])))


def wirksames_zeichenformat(kennung: int) -> dict:
    """Das wirksame Zeichenformat an der Schreibmarke (am Anfang einer Auswahl: das erste Zeichen)."""
    return eigene_kopie(_befehle.stellen_wirksames_zeichenformat(kennung))


def wirksames_absatzformat(kennung: int) -> dict:
    """Das wirksame Absatzformat des Absatzes an der Schreibmarke."""
    return eigene_kopie(_befehle.stellen_wirksames_absatzformat(kennung))


def absatz_formatwert(kennung: int, name: str) -> float:
    """Ein Zahlenwert des wirksamen Absatzformats an der Schreibmarke (0, wenn er fehlt)."""
    return _befehle.stellen_absatz_formatwert(kennung, name)


def geruest_schreiben(kennung: int, zeilen: list[str], benutzer: dict, heute: str) -> bool:
    """Schreibt das Gerüst einer Dokumentvorlage in das (leere) Dokument."""
    return _befehle.stellen_geruest_schreiben(kennung, zeilen, benutzer, heute)


def tabelle_teilen(kennung: int, tabellen_id: int, ab_zeile: int) -> bool:
    """Teilt die Tabelle oberhalb der Zeile ``ab_zeile``."""
    return _befehle.stellen_tabelle_teilen(kennung, tabellen_id, ab_zeile)


def absatz_schriftgroesse(kennung: int) -> float:
    """Die Schriftgröße (pt) des Absatzes an der Schreibmarke ohne eigenes Zeichenformat."""
    return _befehle.stellen_absatz_schriftgroesse(kennung)


def absatzformat_von(kennung: int, absatz_id: int) -> dict:
    """Das wirksame Absatzformat des Absatzes ``absatz_id`` (eigene Kopie)."""
    return eigene_kopie(_befehle.stellen_absatzformat_von(kennung, absatz_id))
