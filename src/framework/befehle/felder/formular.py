"""Formularfelder (Text, Auswahl, Datum, Kontrollkästchen, Schaltfläche): Beschreibung der Felder und ihre Änderungen am Dokument.

Die Fachlogik liegt im Kern. Gelesen und geändert wird im Dokument der Kennung; die Oberfläche kennt weder Felddefinitionen
noch Dokumentmodell."""
from __future__ import annotations

from core.objekte.textfelder.modell import formular_daten as modell
from framework.sitzungen import sitzung as _steuerung
from framework.schnittstellen.datentypen.formulardaten import FeldTreffer, Feldbeschreibung

AKTIONEN: tuple[str, ...] = tuple(modell.AKTIONEN)
DATUMSFORMAT: str = modell.DATUMSFORMAT
AKTION_ZURUECKSETZEN = "Felder zurücksetzen"
AKTION_DRUCKEN = "Drucken"
AKTION_PDF = "Als PDF exportieren"


def _aus_kern(m: dict) -> Feldbeschreibung:
    """Kopie der Felddaten des Kerns als unveränderliche Beschreibung."""
    return Feldbeschreibung(art=m["art"], name=m.get("name") or "", platzhalter=m.get("platzhalter") or "", beschriftung=m.get("beschriftung") or "",
                            optionen=tuple(m.get("optionen") or ()), aufschrift=m.get("aufschrift") or "", aktion=m.get("aktion") or "",
                            leer=bool(m.get("leer")))


def _zum_kern(f: Feldbeschreibung) -> dict:
    """Die Felddaten im Format des Kerns (leere Angaben entfallen)."""
    angaben: dict = {"platzhalter": f.platzhalter, "beschriftung": f.beschriftung, "optionen": list(f.optionen) or None, "aufschrift": f.aufschrift,
                     "aktion": f.aktion}
    m = modell.meta(f.art, f.name, **angaben)
    if f.leer:
        m["leer"] = True
    return m


def meta(art: str, name: str = "", platzhalter: str = "", beschriftung: str = "", optionen: tuple[str, ...] = (), aufschrift: str = "",
         aktion: str = "") -> Feldbeschreibung:
    """Die Beschreibung eines Feldes (Art, Name, Platzhalter, Optionen …); leere Angaben bleiben leer."""
    return Feldbeschreibung(art=art, name=name, platzhalter=platzhalter, beschriftung=beschriftung, optionen=tuple(optionen), aufschrift=aufschrift,
                            aktion=aktion)


def _sitzung(kennung: int):
    return _steuerung._sitzungen[kennung].sitzung


def _geschuetzt(aenderung):
    """Die Änderung für den Anschluss des Editors: ``True``, wenn sie ausgeführt ist; ``False``, wenn der Kern sie ablehnt."""
    from core.bearbeitung import BearbeitungsFehler

    def tat(sitzung) -> bool:
        try:
            aenderung(sitzung)
        except BearbeitungsFehler:
            return False
        return True
    return tat


def einfuegen(kennung: int, m: Feldbeschreibung, wert: str | None = None) -> bool:
    """Das Feld an der Schreibmarke (oder anstelle der Markierung) einfügen."""
    daten = _zum_kern(m)
    return _geschuetzt(lambda sitzung: modell.einfuegen(sitzung, daten, wert))(_sitzung(kennung))


def feld_an(kennung: int, pos: int) -> FeldTreffer | None:
    """Das Feld (Stellen im Rohtext und Beschreibung) an der Stelle ``pos`` oder ``None``."""
    treffer = modell.feld_an(_sitzung(kennung).dokument, pos)
    return None if treffer is None else FeldTreffer(treffer[0], treffer[1], _aus_kern(treffer[2]))


def ist_leer(kennung: int, pos: int) -> bool:
    """Ob das Feld an ``pos`` nur seinen Platzhalter zeigt."""
    return bool(modell.ist_leer(_sitzung(kennung), pos))


def wert_von(kennung: int, v: int, e: int) -> str:
    """Der Text des Feldes zwischen den Stellen ``v`` und ``e``."""
    return modell.wert_von(_sitzung(kennung), v, e)


def ersetzen(kennung: int, v: int, e: int, m: Feldbeschreibung, text: str, leer: bool = False) -> bool:
    """Den Text des Feldes ersetzen (``leer``: er zeigt dann nur den Platzhalter)."""
    daten = _zum_kern(m)
    return _geschuetzt(lambda sitzung: modell.ersetzen(sitzung, v, e, daten, text, leer))(_sitzung(kennung))


def kasten_umschalten(kennung: int, v: int, e: int, m: Feldbeschreibung) -> bool:
    """Das Kontrollkästchen zwischen leer und angekreuzt wechseln."""
    daten = _zum_kern(m)
    return _geschuetzt(lambda sitzung: modell.kasten_umschalten(sitzung, v, e, daten))(_sitzung(kennung))


def alle_zuruecksetzen(kennung: int) -> int:
    """Alle Felder auf ihren Anfangswert zurücksetzen. → Zahl der zurückgesetzten Felder."""
    zaehler = [0]
    _geschuetzt(lambda sitzung: zaehler.__setitem__(0, modell.alle_zuruecksetzen(sitzung)))(_sitzung(kennung))
    return zaehler[0]


def nur_formulardaten(kennung: int) -> int:
    """„Nur Formulardaten drucken“ in der KOPIE eines Dokuments: Text außerhalb der Felder wird unsichtbar, Bilder entfallen. → Zahl der Felder."""
    return modell.nur_formulardaten(_sitzung(kennung).dokument)
