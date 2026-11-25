"""Formularfelder (Text, Auswahl, Datum, Kontrollkästchen, Schaltfläche): Beschreibung der Felder und ihre Änderungen am Dokument.

Die Fachlogik liegt im Kern. Gelesen und geändert wird über den Anschluss des Editors (``AenderungsPort``); die Oberfläche kennt weder Felddefinitionen
noch Dokumentmodell."""
from __future__ import annotations

from core.objekte.textfelder.modell import formular_daten as modell
from framework.schnittstellen.aenderungs_port import AenderungsPort
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


def einfuegen(editor: AenderungsPort, m: Feldbeschreibung, wert: str | None = None) -> bool:
    """Das Feld an der Schreibmarke (oder anstelle der Markierung) einfügen."""
    daten = _zum_kern(m)
    return editor.aendern(lambda sitzung: modell.einfuegen(sitzung, daten, wert))


def feld_an(editor: AenderungsPort, pos: int) -> FeldTreffer | None:
    """Das Feld (Stellen im Rohtext und Beschreibung) an der Stelle ``pos`` oder ``None``."""
    treffer = editor.lesen(lambda sitzung: modell.feld_an(sitzung.dokument, pos))
    return None if treffer is None else FeldTreffer(treffer[0], treffer[1], _aus_kern(treffer[2]))


def ist_leer(editor: AenderungsPort, pos: int) -> bool:
    """Ob das Feld an ``pos`` nur seinen Platzhalter zeigt."""
    return bool(editor.lesen(lambda sitzung: modell.ist_leer(sitzung, pos)))


def wert_von(editor: AenderungsPort, v: int, e: int) -> str:
    """Der Text des Feldes zwischen den Stellen ``v`` und ``e``."""
    return editor.lesen(lambda sitzung: modell.wert_von(sitzung, v, e))


def ersetzen(editor: AenderungsPort, v: int, e: int, m: Feldbeschreibung, text: str, leer: bool = False) -> bool:
    """Den Text des Feldes ersetzen (``leer``: er zeigt dann nur den Platzhalter)."""
    daten = _zum_kern(m)
    return editor.aendern(lambda sitzung: modell.ersetzen(sitzung, v, e, daten, text, leer))


def kasten_umschalten(editor: AenderungsPort, v: int, e: int, m: Feldbeschreibung) -> bool:
    """Das Kontrollkästchen zwischen leer und angekreuzt wechseln."""
    daten = _zum_kern(m)
    return editor.aendern(lambda sitzung: modell.kasten_umschalten(sitzung, v, e, daten))


def alle_zuruecksetzen(editor: AenderungsPort) -> int:
    """Alle Felder auf ihren Anfangswert zurücksetzen. → Zahl der zurückgesetzten Felder."""
    zaehler = [0]
    editor.aendern(lambda sitzung: zaehler.__setitem__(0, modell.alle_zuruecksetzen(sitzung)))
    return zaehler[0]


def nur_formulardaten(editor: AenderungsPort) -> int:
    """„Nur Formulardaten drucken“ in der KOPIE eines Dokuments: Text außerhalb der Felder wird unsichtbar, Bilder entfallen. → Zahl der Felder."""
    return editor.lesen(lambda sitzung: modell.nur_formulardaten(sitzung.dokument))
