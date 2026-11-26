"""Abgeleitete Dokumente (Vergleich, Zusammenführung, Serienbrief) und die Wortstatistik: ordnet die Bedienung den Framework-Befehlen zu.
Die Oberfläche bekommt Nummern und Werte, nie ein Dokument."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle
from writer.werte import eigene_kopie


def fassung_laden(pfad: str) -> int:
    """Eine Datei als Fassung zum Vergleichen oder Zusammenführen laden; → ihre Nummer."""
    return _befehle.ergebnisse_fassung_laden(pfad)


def ergebnis_verwerfen(nummer: int) -> None:
    _befehle.ergebnisse_ergebnis_verwerfen(nummer)


def ergebnis_einsetzen(kennung: int, nummer: int) -> bool:
    """Das bereitgehaltene Dokument ``nummer`` als Inhalt des Dokuments ``kennung`` einsetzen."""
    return _befehle.ergebnisse_ergebnis_einsetzen(kennung, nummer)


def dokumente_vergleichen(kennung: int, fassung: int, autor: str) -> tuple[int, dict]:
    """→ (Nummer des Ergebnisses mit nachverfolgten Änderungen, Statistik)."""
    nummer, st = _befehle.ergebnisse_vergleichen(kennung, fassung, autor)
    return nummer, eigene_kopie(st)


def dokumente_zusammenfuehren(kennung: int, fassungen: list[tuple[str, int]]) -> tuple[int, dict, list[str]]:
    """→ (Nummer des Ergebnisses, Statistik, Konflikte)."""
    nummer, st, konflikte = _befehle.ergebnisse_zusammenfuehren(kennung, tuple(fassungen))
    return nummer, eigene_kopie(st), list(konflikte)


def serienbrief_gruppen(kennung: int, saetze: list[dict]) -> list[list[dict]]:
    """Die Datensätze je Brief."""
    return eigene_kopie(_befehle.ergebnisse_serienbrief_gruppen(kennung, saetze))


def serienbrief_erzeugen(kennung: int, saetze: list[dict]) -> tuple[int, int]:
    """Alle Briefe in EIN Dokument: → (Nummer des Ergebnisses, Zahl der Briefe)."""
    return _befehle.ergebnisse_serienbrief_erzeugen(kennung, saetze)


def serienbriefe_speichern(kennung: int, ordner: str, name: str, saetze: list[dict], meta: dict) -> int:
    """Jeden Brief als eigene DOCX-Datei in ``ordner`` schreiben; → Zahl der Briefe."""
    return _befehle.ergebnisse_serienbriefe_speichern(kennung, ordner, name, saetze, meta)


def texte_des_dokuments(kennung: int) -> list[str]:
    """Die Texte der Absätze des Dokuments für die Wortstatistik."""
    return list(_befehle.ergebnisse_texte_des_dokuments(kennung))
