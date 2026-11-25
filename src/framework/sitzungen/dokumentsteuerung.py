"""Sitzung: offene Dokumente und das aktive Dokument. Nach außen gibt es nur Nummern (``int``) der Dokumente, nie Kern-Objekte.

Das Framework erzeugt und besitzt die Bearbeitungssitzungen (je Kennung ein privater Datensatz aus Bearbeitungssitzung, Meta und Seite).
Die Qt-freien Teile von ``anwendung.py`` und ``dokument_verwaltung.py`` kommen schrittweise hierher (Übergang: ``NOCH_NICHT_UMGESTELLT``)."""
from __future__ import annotations

from dataclasses import dataclass, field

from core.bearbeitung import Bearbeitungssitzung
from core.dokument import neues_dokument
from core.formatvorlagen.formatvorlagen import eingebaute_vorlagen
from framework.dokumentverwaltung.dateizugriff.modell_laden import lade_modell
from framework.schnittstellen.datentypen.ereignisdaten import Art, Ereignis
from framework.schnittstellen.datentypen.geoeffnet import Geoeffnet
from framework.ereignisse.ereignissteuerung import melder


@dataclass
class _Datensatz:
    sitzung: Bearbeitungssitzung
    meta: dict
    page: object
    bearbeiter: str = ""                 # Name für nachverfolgte Änderungen und Kommentare
    nur_lesen: bool = False
    layout_optionen: dict = field(default_factory=dict)   # Ansichtsoptionen des Layouts (Lesehilfe, Web-Layout): Seitenzahlen wie in der Ansicht


class Sitzung:
    def __init__(self) -> None:
        self._sitzungen: dict[int, _Datensatz] = {}             # privat: Kern-Dokumente bleiben im Framework
        self._aktiv: int | None = None
        self._naechste = 1

    def neu(self, grundschrift: tuple[str, float] | None = None) -> int:
        dokument = neues_dokument()
        if grundschrift is not None:
            dokument.standardformat = {"schrift": grundschrift[0], "groesse_pt": float(grundschrift[1])}
        meta = {"kommentare": {}, "noten": {"f": {}, "e": {}}, "quellen": [], "zitierweise": "APA"}
        return self._anlegen(dokument, meta, None)

    def oeffnen_datei(self, pfad: str, kennwort: str | None = None) -> Geoeffnet:
        geladen = lade_modell(pfad, kennwort)                   # wirft DocumentIOError / PasswortNoetig an den Aufrufer
        hinweise = tuple(getattr(geladen.report, "warnings", ()) or ())
        return Geoeffnet(self._anlegen(geladen.document, dict(geladen.meta), geladen.page), hinweise)

    def _anlegen(self, dokument, meta: dict, page: object) -> int:
        for name, vorlage in eingebaute_vorlagen().items():
            dokument.vorlagen.setdefault(name, vorlage)
        nummer = self._naechste
        self._naechste += 1
        self._sitzungen[nummer] = _Datensatz(Bearbeitungssitzung(dokument), meta, page)
        self._aktiv = nummer
        melder.melden(Ereignis(Art.GEAENDERT, "dokument_geoeffnet", {"nummer": nummer}))
        return nummer

    def schliessen(self, nummer: int) -> None:
        self._sitzungen.pop(nummer, None)
        if self._aktiv == nummer:
            self._aktiv = next(reversed(self._sitzungen), None)
        melder.melden(Ereignis(Art.GEAENDERT, "dokument_geschlossen", {"nummer": nummer}))

    def aktivieren(self, nummer: int) -> None:
        if nummer in self._sitzungen:
            self._aktiv = nummer
            melder.melden(Ereignis(Art.GEAENDERT, "dokument_aktiv", {"nummer": nummer}))

    def bearbeiter_setzen(self, nummer: int, name: str) -> None:
        """Wer bearbeitet: steht an nachverfolgten Änderungen und Kommentaren."""
        if nummer in self._sitzungen:
            self._sitzungen[nummer].bearbeiter = name

    def nur_lesen_setzen(self, nummer: int, an: bool) -> None:
        """Schreibschutz des Dokuments: Änderungen über das Framework werden dann abgelehnt."""
        if nummer in self._sitzungen:
            self._sitzungen[nummer].nur_lesen = bool(an)

    def layout_option_setzen(self, nummer: int, name: str, wert: float | bool | None) -> None:
        """Eine Layout-Option der Ansicht (``buchstaben``, ``wort``, ``zeilenluft``, ``versteckt``, ``web``); ``None`` nimmt sie heraus."""
        satz = self._sitzungen.get(nummer)
        if satz is None:
            return
        if wert is None:
            satz.layout_optionen.pop(name, None)
        else:
            satz.layout_optionen[name] = wert

    @property
    def aktiv(self) -> int | None:
        return self._aktiv

    @property
    def offene(self) -> tuple[int, ...]:
        return tuple(self._sitzungen)


sitzung = Sitzung()
