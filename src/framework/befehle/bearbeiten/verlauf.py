"""Verlauf eines Dokuments anhand der Kennung: mehrere Befehle zu einem Schritt zusammenfassen, Rückgängig und Wiederholen, der Stand für eine
Live-Vorschau, Nachverfolgen von Änderungen und der Zustand „geändert“."""
from __future__ import annotations

from framework.sitzungen import sitzung as _steuerung

_OFFEN: dict[int, list] = {}          # Kennung → offene Schrittgruppen (innerste zuletzt)
_BEOBACHTET: set[int] = set()         # Kennungen, deren Änderungen als Ereignis gemeldet werden
_VORSCHAU: dict[int, tuple] = {}      # Kennung → (Länge des Verlaufs, Format am Zeiger) vor der Live-Vorschau


class _Abbruch(Exception):
    """Bricht eine offene Schrittgruppe ab: der Kern nimmt ihre Änderungen zurück."""


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def schritt_beginnen(kennung: int, name: str) -> None:
    """Alle folgenden Befehle bis ``schritt_beenden`` zählen als ein Schritt für Rückgängig."""
    gruppe = _sitzung(kennung).gruppe(name)
    gruppe.__enter__()
    _OFFEN.setdefault(kennung, []).append(gruppe)


def schritt_beenden(kennung: int) -> None:
    """Die zuletzt begonnene Schrittgruppe abschließen."""
    _OFFEN[kennung].pop().__exit__(None, None, None)


def schritt_abbrechen(kennung: int) -> None:
    """Die zuletzt begonnene Schrittgruppe verwerfen: ihre Änderungen werden zurückgenommen."""
    fehler = _Abbruch()
    try:
        _OFFEN[kennung].pop().__exit__(_Abbruch, fehler, None)
    except _Abbruch:
        pass


def rueckgaengig(kennung: int) -> bool:
    return bool(_sitzung(kennung).rueckgaengig())


def wiederholen(kennung: int) -> bool:
    return bool(_sitzung(kennung).wiederholen())


def vorschau_beginnen(kennung: int) -> None:
    """Den Stand vor einer Live-Vorschau merken (Länge des Verlaufs und Format am Zeiger)."""
    s = _sitzung(kennung)
    _VORSCHAU[kennung] = (s.verlauf_laenge, s.tippformat)


def vorschau_schritte(kennung: int) -> int:
    """Wie viele Schritte seit ``vorschau_beginnen`` dazugekommen sind."""
    return max(0, _sitzung(kennung).verlauf_laenge - _VORSCHAU[kennung][0])


def vorschau_beenden(kennung: int, schritte: int) -> None:
    """Die Live-Vorschau zurücknehmen: mit Schritten der Stand davor, sonst nur das Format am Zeiger."""
    s = _sitzung(kennung)
    vorher, format = _VORSCHAU.pop(kennung)
    if schritte:
        s.verlauf_zurueck_auf(vorher)             # der Stand vor der Vorschau; Wiederholen-Schritte der Vorschau fallen weg
    else:
        s.tippformat = format                     # ohne Markierung ändert die Vorschau nur das Format am Zeiger


def nachverfolgen(kennung: int) -> bool:
    return bool(_sitzung(kennung).nachverfolgen)


def nachverfolgen_setzen(kennung: int, an: bool) -> None:
    _sitzung(kennung).nachverfolgen = bool(an)


def geaendert(kennung: int) -> bool:
    """Ob das Dokument seit dem letzten Merken geändert wurde."""
    return bool(_sitzung(kennung).geaendert)


def als_gespeichert_merken(kennung: int) -> None:
    _sitzung(kennung).als_gespeichert_merken()


def auswahl_text(kennung: int) -> str:
    """Der Text der Auswahl."""
    s = _sitzung(kennung)
    return s.text(s.auswahl)


def textmarke_anspringen(kennung: int, name: str) -> bool:
    """Die Textmarke ``name`` auswählen; ``False``, wenn es sie nicht gibt."""
    s = _sitzung(kennung)
    marken = s.textmarken()
    if name not in marken:
        return False
    s.setze_auswahl(marken[name].anker, marken[name].kopf)
    return True


def stempeln(kennung: int, autor: str) -> None:
    """Vor einer Änderung: Bearbeiter und Zeit für nachverfolgte Änderungen und Kommentare setzen."""
    import datetime
    s = _sitzung(kennung)
    s.autor = autor
    s.datum = datetime.datetime.now().replace(microsecond=0).isoformat()


def beobachten(kennung: int) -> None:
    """Ab jetzt meldet das Framework jede Änderung des Dokuments als Ereignis ``GEAENDERT`` mit der Kennung in den Daten."""
    from framework.ereignisse import melder
    from framework.schnittstellen.datentypen import Art, Ereignis
    if kennung in _BEOBACHTET:
        return
    _BEOBACHTET.add(kennung)
    _sitzung(kennung).beobachte(lambda _aenderung: melder.melden(Ereignis(Art.GEAENDERT, daten={"kennung": kennung})))
