"""Abgeleitete Dokumente (Vergleich, Zusammenführung, Serienbrief): Das Framework erzeugt sie aus dem Dokument einer Kennung und hält sie unter
einer Nummer bereit, bis sie in ein neues Blatt eingesetzt werden. Dazu Abfragen, die das ganze Dokument lesen (Wortstatistik)."""
from __future__ import annotations

import os
from collections.abc import Mapping, Sequence

from framework.anbindung import Daten, fest
from framework.sitzungen import sitzung as _steuerung

_ERGEBNISSE: dict = {}                 # Nummer → Dokument (oder ``None``), bis es eingesetzt oder verworfen ist
_naechste = [1]


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _merken(dokument) -> int:
    nummer = _naechste[0]
    _naechste[0] += 1
    _ERGEBNISSE[nummer] = dokument
    return nummer


def fassung_laden(pfad: str) -> int:
    """Eine Datei als Fassung zum Vergleichen oder Zusammenführen laden; → ihre Nummer. Eine unlesbare Datei löst den Fehler des Ladens aus."""
    from framework.dokumentverwaltung.dateizugriff import lade_modell
    return _merken(lade_modell(pfad).document)


def ergebnis_verwerfen(nummer: int) -> None:
    _ERGEBNISSE.pop(nummer, None)


def ergebnis_einsetzen(kennung: int, nummer: int) -> bool:
    """Das bereitgehaltene Dokument ``nummer`` als Inhalt des Dokuments ``kennung`` einsetzen; ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    ziel = _ERGEBNISSE.pop(nummer)
    try:
        _sitzung(kennung).dokument_ersetzen(ziel)
    except BearbeitungsFehler:
        return False
    return True


def vergleichen(kennung: int, fassung: int, autor: str) -> tuple[int, Mapping[str, Daten]]:
    """Das Dokument mit der geladenen Fassung vergleichen: → (Nummer des Ergebnisses mit nachverfolgten Änderungen, Statistik)."""
    from core.aenderungsverfolgung.vergleich import vergleichen as kern_vergleichen
    ziel, st = kern_vergleichen(_sitzung(kennung).dokument, _ERGEBNISSE.pop(fassung), autor)
    return _merken(ziel), fest(st)


def zusammenfuehren(kennung: int, fassungen: Sequence[tuple[str, int]]) -> tuple[int, Mapping[str, Daten], tuple[str, ...]]:
    """Überarbeitete Fassungen ((Autor, Nummer der geladenen Fassung) …) mit dem Dokument zusammenführen: → (Nummer des Ergebnisses, Statistik, Konflikte)."""
    from core.aenderungsverfolgung.vergleich import zusammenfuehren as kern_zusammenfuehren
    ziel, st, konflikte = kern_zusammenfuehren(_sitzung(kennung).dokument, [(autor, _ERGEBNISSE.pop(nr)) for autor, nr in fassungen])
    return _merken(ziel), fest(st), tuple(konflikte)


def serienbrief_gruppen(kennung: int, saetze: Sequence[Mapping[str, str]]) -> Sequence[Sequence[Mapping[str, str]]]:
    """Die Datensätze je Brief (mehrere, wenn „Nächster Datensatz“ im Text steht)."""
    from framework.serienbriefe.erstellung import gruppen
    return fest(gruppen(_sitzung(kennung).dokument, list(saetze)))


def serienbrief_erzeugen(kennung: int, saetze: Sequence[Mapping[str, str]]) -> tuple[int, int]:
    """Alle Briefe in EIN Dokument, durch Seitenumbrüche getrennt: → (Nummer des Ergebnisses, Zahl der Briefe)."""
    from framework.serienbriefe.erstellung import serienbrief_erzeugen as erzeugen
    ziel, n = erzeugen(_sitzung(kennung).dokument, list(saetze))
    return _merken(ziel), n


def serienbriefe_speichern(kennung: int, ordner: str, name: str, saetze: Sequence[Mapping[str, str]], meta: Mapping[str, Daten]) -> int:
    """Jeden Brief als eigene DOCX-Datei ``<name> 001.docx`` … in ``ordner`` schreiben (Seiteneinrichtung des Abschnitts an der Schreibmarke); → Zahl der Briefe."""
    from framework.dokumentverwaltung.dateizugriff import speichere_modell
    from framework.serienbriefe.erstellung import brief_fuer, gruppen
    s = _sitzung(kennung)
    dok = s.dokument
    seite = dok.abschnitte[min(s.abschnitt_index(s.auswahl.kopf.absatz_id), len(dok.abschnitte) - 1)].seite
    briefe = gruppen(dok, list(saetze))
    for i, gruppe in enumerate(briefe, 1):
        speichere_modell(os.path.join(ordner, f"{name} {i:03d}.docx"), brief_fuer(dok, gruppe), seite, dict(meta), sicherung=False)
    return len(briefe)


def texte_des_dokuments(kennung: int) -> tuple[str, ...]:
    """Die Texte der Absätze des Dokuments (samt denen in Tabellen) für die Wortstatistik."""
    from core.text import texte_des_dokuments as texte
    return tuple(texte(_sitzung(kennung).dokument))
