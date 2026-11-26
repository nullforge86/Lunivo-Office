"""Abfragen und Befehle des Editors über das ganze Dokument: ordnet sie den Framework-Befehlen zu."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle


def rohtext(kennung: int) -> str:
    """Der Text des Dokuments mit U+2029 zwischen den Absätzen."""
    return _befehle.abfragen_rohtext(kennung)


def tab_abstand(kennung: int) -> float:
    """Der Standardabstand der Tabulatoren des Dokuments in Bildpunkten."""
    return _befehle.abfragen_tab_abstand(kennung)


def ueberschriftsebene_an_marke(kennung: int) -> int:
    """Die Gliederungsebene des Absatzes an der Schreibmarke (0 = Fließtext)."""
    return _befehle.abfragen_ueberschriftsebene_an_marke(kennung)


def tabellen_ohne_rahmen(kennung: int) -> list[tuple[int, int]]:
    """(Stelle des Tabellenanfangs, Tabellen-Id) aller Tabellen ohne Rahmen, nach der Stelle geordnet."""
    return list(_befehle.abfragen_tabellen_ohne_rahmen(kennung))


def aehnlich_formatiert(kennung: int) -> list[tuple[int, int]]:
    """Alle Strecken (von, bis) mit derselben Zeichenformatierung wie das Zeichen an der Schreibmarke."""
    return list(_befehle.abfragen_aehnlich_formatiert(kennung))


def objekte_nach_stelle(kennung: int) -> list[tuple[int, str, int]]:
    """(Stelle, Art, Id) aller Objekte – ``text`` oder ``frei`` – nach der Stelle geordnet."""
    return list(_befehle.abfragen_objekte_nach_stelle(kennung))


def seitenzahl_setzen(kennung: int, bereich: str, erster_absatz: int | None, abschnitt: int, ort: str, ausrichtung: str, muster: str, zahlformat: str | None,
                      start: int | None = None, kapitel: tuple[int, str] | None = None, mit_start: bool = False) -> bool:
    """Seitenzahl in Kopf- oder Fußzeile für das Dokument, ab einem Absatz (neuer Abschnitt) oder einen Abschnitt."""
    return _befehle.abfragen_seitenzahl_setzen(kennung, bereich, erster_absatz, abschnitt, ort, ausrichtung, muster, zahlformat, start, kapitel, mit_start)


def objektliste(kennung: int) -> list[tuple[int, str, int, str]]:
    """(Stelle, ``text`` | ``frei``, Id, Objektart) aller Objekte: erst die im Text in Dokumentreihenfolge, dann die frei positionierten."""
    return list(_befehle.abfragen_objektliste(kennung))


def tabellenstellen(kennung: int) -> list[int]:
    """Die Stellen der Tabellenanfänge aller Tabellen (auch geschachtelter), aufsteigend."""
    return list(_befehle.abfragen_tabellenstellen(kennung))


def barrierefreiheit_befund(kennung: int) -> _befehle.Barrierebefund:
    """Was die Prüfung der Barrierefreiheit im Dokument gezählt hat (unveränderliche Angaben des Frameworks)."""
    return _befehle.abfragen_barrierefreiheit_befund(kennung)


def ueberschriften(kennung: int) -> list[tuple[int, int, str]]:
    """(Stelle des Absatzanfangs im Rohtext, Gliederungsebene, Text) aller Überschriften mit Text, in Dokumentreihenfolge."""
    return list(_befehle.abfragen_ueberschriften(kennung))


def seitenzahl_vorgabe_setzen(kennung: int, ort: str, ausrichtung: str) -> bool:
    """Seitenzahl nach einer Vorgabe der Galerie in Kopf- oder Fußzeile des Abschnitts an der Schreibmarke."""
    return _befehle.abfragen_seitenzahl_vorgabe_setzen(kennung, ort, ausrichtung)


def seitenzahlen_entfernen(kennung: int) -> bool | None:
    """Die Seitenzahlen aus Kopf- und Fußzeile des Abschnitts an der Schreibmarke nehmen; ``None``, wenn dort keine steht."""
    return _befehle.abfragen_seitenzahlen_entfernen(kennung)


def toc_optionen(kennung: int) -> dict | None:
    """Einstellungen des ersten Inhaltsverzeichnisses im Dokument (None, wenn es keines gibt)."""
    from writer.werte import eigene_kopie
    return eigene_kopie(_befehle.abfragen_toc_optionen(kennung))


def silbentrennung_verfuegbar(sprache: str) -> bool:
    """Gibt es für die Sprache eine Silbentrennung?"""
    return _befehle.abfragen_silbentrennung_verfuegbar(sprache)
