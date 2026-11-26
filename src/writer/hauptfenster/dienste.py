"""Dienste des Hauptfensters: Die Oberfläche lässt sich die Dienste des Frameworks (Einstellungen, Dokumentverwaltung, Anbieter der Korrektur) und
einzelne Angaben hier geben, statt das Framework selbst anzusprechen."""
from __future__ import annotations

from framework.befehle.korrektur import KorrekturEinstellungenAnbieter
from framework.befehle.ueberpruefen import EntscheidenZustand
from framework.befehle.verweise import IndexEintrag
from framework.schnittstellen import ORGANISATION, PROGRAMM, Einstellungen
from framework.sitzungen import DocumentManager


def einstellungen() -> Einstellungen:
    """Die Einstellungen des Programms (JSON-Datei im Benutzerordner)."""
    return Einstellungen()


def organisation() -> str:
    return ORGANISATION


def programmname() -> str:
    return PROGRAMM


def korrektur_anbieter(e: Einstellungen) -> KorrekturEinstellungenAnbieter:
    """Der Anbieter der Korrektureinstellungen für die Schreibhilfe."""
    return KorrekturEinstellungenAnbieter(e)


def dokumentverwaltung(e: Einstellungen) -> DocumentManager:
    """Die Dokumentverwaltung des Fensters (Laden, Speichern, zuletzt geöffnet, Wiederherstellung)."""
    return DocumentManager(e)


def index_eintrag(haupt: str, unter: str = "", lesung: str = "", lesung_unter: str = "", siehe: str = "", marke: str = "", fett: bool = False,
                  kursiv: bool = False) -> IndexEintrag:
    """Ein Indexeintrag aus den Angaben des Fensters „Indexeintrag festlegen“."""
    return IndexEintrag(haupt, unter, lesung, lesung_unter, siehe=siehe, marke=marke, fett=fett, kursiv=kursiv)


def entscheiden_zustand_leer() -> EntscheidenZustand:
    """Der Zustand der Knöpfe „Annehmen/Ablehnen“ ohne Dokument."""
    return EntscheidenZustand()


def dokument_speichern(verwaltung: DocumentManager, kennung: int, pfad: str, seite, meta: dict, erwartet=None) -> tuple[str, ...]:
    """Schreibt das Dokument ``kennung`` nach ``pfad``; → Hinweise über nicht Übernommenes. Meldet ``Dateifehler`` (``writer.werte``), wenn das nicht geht."""
    from framework.schnittstellen import Dateifehler as _Dateifehler
    from writer.werte import Dateifehler
    try:
        return verwaltung.speichern_dokument(kennung, pfad, seite, meta, erwartet)
    except _Dateifehler as e:
        raise Dateifehler(str(e)) from None
