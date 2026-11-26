"""Suchen und Ersetzen für die Oberfläche: ordnet den Suchauftrag den Framework-Befehlen zu. Bedingungen an die Formatierung wertet die
Oberfläche selbst aus (über ``suche_zeichenformate`` und ``suche_absaetze``) und gibt nur die passenden Schlüssel und Ids weiter."""
from __future__ import annotations

from typing import NamedTuple

from framework.befehle import bearbeiten as _befehle
from writer.werte import eigene_kopie


class Suchabsatz(NamedTuple):
    id: int
    vorlage: str


def suchangabe(text: str, *, gross: bool = False, ganz: bool = False, platzhalter: bool = False, praefix: bool = False, suffix: bool = False,
               ohne_satzzeichen: bool = False, ohne_leerzeichen: bool = False, zeichen: frozenset | None = None,
               absaetze: frozenset | None = None) -> _befehle.Suchangabe:
    """Der Suchauftrag; ``zeichen``/``absaetze``: Schlüssel der Zeichenformate und Ids der Absätze, die passen (``None``: keine Bedingung)."""
    return _befehle.Suchangabe(text, gross, ganz, platzhalter, praefix, suffix, ohne_satzzeichen, ohne_leerzeichen, zeichen, absaetze)


def suche_zeichenformate(kennung: int) -> list[tuple[str, dict]]:
    """Die verschiedenen Zeichenformate der Textstücke des Dokuments als (Schlüssel, Format)."""
    return [(k, eigene_kopie(f)) for k, f in _befehle.suche_zeichenformate(kennung)]


def suche_absaetze(kennung: int) -> list[Suchabsatz]:
    """Die Absätze des Dokuments mit dem Namen ihrer Formatvorlage."""
    return [Suchabsatz(i, v) for i, v in _befehle.suche_absaetze(kennung)]


def suche_gueltig(angabe: _befehle.Suchangabe) -> bool:
    return _befehle.suche_gueltig(angabe)


def suche_treffer(kennung: int, angabe: _befehle.Suchangabe, von: int = 0, bis: int | None = None) -> list[tuple[int, int]]:
    """Alle Treffer im Bereich [von, bis) als (von, bis), Stellen im Rohtext."""
    return list(_befehle.suche_treffer(kennung, angabe, von, bis))


def suche_naechster(kennung: int, angabe: _befehle.Suchangabe, ab: int, rueckwaerts: bool = False, von: int = 0, bis: int | None = None,
                    umlauf: bool = True) -> tuple[int, int] | None:
    return _befehle.suche_naechster(kennung, angabe, ab, rueckwaerts, von, bis, umlauf)


def suche_ersatz_text(angabe: _befehle.Suchangabe, ersatz: str, gefunden: str, zwischenablage: str = "") -> str:
    return _befehle.suche_ersatz_text(angabe, ersatz, gefunden, zwischenablage)


def suche_alle_ersetzen(kennung: int, angabe: _befehle.Suchangabe, ersatz: str, von: int = 0, bis: int | None = None, zeichen: dict | None = None,
                        absatz: dict | None = None, zwischenablage: str = "") -> int:
    """Alle Treffer im Bereich ersetzen, als ein Schritt für Rückgängig. → Zahl der Ersetzungen; -1, wenn der Kern ablehnt."""
    return _befehle.suche_alle_ersetzen(kennung, angabe, ersatz, von, bis, zeichen, absatz, zwischenablage)
