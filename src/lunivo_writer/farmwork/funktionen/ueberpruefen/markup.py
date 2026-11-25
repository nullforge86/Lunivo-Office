"""Befehle des Markups: Filter (Kommentare, Einfügungen, Bearbeiter, Zeiten), Zustände der Klappen und das Entscheiden über angezeigte Änderungen.

Der Editor kommt über den ``EditorPort`` herein; die Fassungen (Bearbeiter, Zeiten) liefert ``editor/dokument/fassungen.py``."""
from __future__ import annotations

from lunivo_writer.core.funktionen.ueberpruefen import fassungen
from lunivo_writer.farmwork.datentypen.ereignisdaten import Art, Ereignis
from lunivo_writer.farmwork.funktionen.ueberpruefen import einstellungen as ueberpruefen_einstellungen
from lunivo_writer.farmwork.funktionen.ueberpruefen.schutz import SCHUTZ_HINWEIS, ist_geschuetzt
from lunivo_writer.farmwork.funktionen.ueberpruefen.typen import EntscheidenZustand, MarkupFilter
from lunivo_writer.farmwork.schnittstellen.dokument import EditorPort
from lunivo_writer.farmwork.schnittstellen.einstellungen import Einstellungen
from lunivo_writer.farmwork.steuerung.ereignissteuerung import Melder


class MarkupBefehle:
    def __init__(self, editor: EditorPort, einstellungen: Einstellungen, melder: Melder):
        self._e = editor
        self._einstellungen = einstellungen
        self._melder = melder

    def _melden(self, text: str, dauer_ms: int = 4000) -> None:
        self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": dauer_ms}))

    # ---- Zustand ------------------------------------------------------------------------------------------------------------------
    def hat_kommentare(self) -> bool:
        return bool(self._e.kommentar_bereiche())

    def hat_aenderungen(self) -> bool:
        return bool(self._e.aenderungen())

    def kommentar_am_zeiger(self) -> bool:
        return self._e.kommentar_am_cursor() is not None

    def markup_an(self) -> bool:
        return bool(self._e.markup)

    # ---- Filter -------------------------------------------------------------------------------------------------------------------
    def filter(self) -> MarkupFilter:
        f = self._e.markup_filter
        b = f["bearbeiter"]
        return MarkupFilter(bool(f["kommentare"]), bool(f["einfuegungen"]), None if b is None else frozenset(b), f["zeit"])

    def filter_setzen(self, **werte) -> None:
        self._e.markup_filter_setzen(**werte)

    def bearbeiter_namen(self) -> tuple[str, ...]:
        return tuple(fassungen.bearbeiter(self._e.sitzung.dokument))

    def zeiten(self) -> tuple[str, ...]:
        return tuple(fassungen.zeiten(self._e.sitzung.dokument))

    def bearbeiter_umschalten(self, name: str) -> None:
        alle = fassungen.bearbeiter(self._e.sitzung.dokument)
        jetzt = set(alle if self._e.markup_filter["bearbeiter"] is None else self._e.markup_filter["bearbeiter"])
        jetzt ^= {name}
        self.filter_setzen(bearbeiter=None if jetzt >= set(alle) else jetzt)

    def ballons(self) -> str:
        return ueberpruefen_einstellungen.ballons(self._einstellungen)

    def ballons_setzen(self, wert: str) -> None:
        ueberpruefen_einstellungen.ballons_setzen(self._einstellungen, wert)

    # ---- Annehmen und Ablehnen --------------------------------------------------------------------------------------------------
    def entscheiden_zustand(self, schutz: str | None) -> EntscheidenZustand:
        frei = self.hat_aenderungen() and schutz is None
        f = self._e.markup_filter
        gefiltert = bool(f) and (f["bearbeiter"] is not None or f["zeit"] is not None or not f["einfuegungen"])
        gezeigt = frei and gefiltert and any(self._e.aenderung_sichtbar(b) for b in self._e.aenderungen())
        return EntscheidenZustand(frei and self._e.aenderung_am_cursor() is not None, bool(gezeigt), frei)

    def angezeigte_entscheiden(self, annehmen: bool, schutz: str | None) -> None:
        if ist_geschuetzt(schutz, "aenderungen", "lesen", "kommentare"):
            self._melden(SCHUTZ_HINWEIS)
            return
        n = self._e.angezeigte_aenderungen(annehmen)
        self._melden(f"{n} angezeigte Änderungen {'angenommen' if annehmen else 'abgelehnt'}.")
