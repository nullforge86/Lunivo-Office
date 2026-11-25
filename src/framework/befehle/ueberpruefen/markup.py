"""Befehle des Markups: Filter (Kommentare, Einfügungen, Bearbeiter, Zeiten), Zustände der Klappen und das Entscheiden über angezeigte Änderungen.

Für das Dokument mit der Kennung; der Filter ist Zustand der Anzeige im Framework, die Fassungen (Bearbeiter, Zeiten) kommen aus dem Kern."""
from __future__ import annotations

from core.aenderungsverfolgung.vergleich import fassungen
from core.aenderungsverfolgung.vergleich import ist_gefiltert, ist_sichtbar
from framework.befehle import im_kontext_lesen, lesen
from framework.befehle.ueberpruefen import einstellungen as ueberpruefen_einstellungen
from framework.befehle.ueberpruefen.aenderungen import AenderungenBefehle
from framework.befehle.ueberpruefen.schutz import SCHUTZ_HINWEIS, ist_geschuetzt
from framework.befehle.ueberpruefen.typen import EntscheidenZustand, MarkupFilter
from framework.ereignisse import Melder
from framework.schnittstellen.datentypen import Art, Ereignis
from framework.schnittstellen.einstellungen import Einstellungen
from framework.sitzungen import sitzung as _steuerung


class MarkupBefehle:
    def __init__(self, kennung: int, einstellungen: Einstellungen, melder: Melder):
        self._kennung = kennung
        self._einstellungen = einstellungen
        self._melder = melder

    def _melden(self, text: str, dauer_ms: int = 4000) -> None:
        self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": dauer_ms}))

    def _aenderungen(self) -> list:
        return im_kontext_lesen(self._kennung, lambda k: k.aenderungen()) or []

    # ---- Zustand ------------------------------------------------------------------------------------------------------------------
    def hat_kommentare(self) -> bool:
        return bool(im_kontext_lesen(self._kennung, lambda k: len(k.kommentar_bereiche())))

    def hat_aenderungen(self) -> bool:
        return bool(self._aenderungen())

    def kommentar_am_zeiger(self) -> bool:
        return im_kontext_lesen(self._kennung, lambda k: k.kommentar_am_zeiger()) is not None

    def markup_an(self) -> bool:
        return _steuerung.markup_an(self._kennung)

    # ---- Filter -------------------------------------------------------------------------------------------------------------------
    def filter(self) -> MarkupFilter:
        f = _steuerung.markup_filter(self._kennung)
        b = f["bearbeiter"]
        return MarkupFilter(bool(f["kommentare"]), bool(f["einfuegungen"]), None if b is None else frozenset(b), f["zeit"])

    def filter_setzen(self, **werte) -> None:
        _steuerung.markup_filter_setzen(self._kennung, **werte)

    def bearbeiter_namen(self) -> tuple[str, ...]:
        return tuple(lesen(self._kennung, lambda s: fassungen.bearbeiter(s.dokument)) or ())

    def zeiten(self) -> tuple[str, ...]:
        return tuple(lesen(self._kennung, lambda s: fassungen.zeiten(s.dokument)) or ())

    def bearbeiter_umschalten(self, name: str) -> None:
        alle = self.bearbeiter_namen()
        gewaehlt = _steuerung.markup_filter(self._kennung)["bearbeiter"]
        jetzt = set(alle if gewaehlt is None else gewaehlt)
        jetzt ^= {name}
        self.filter_setzen(bearbeiter=None if jetzt >= set(alle) else jetzt)

    def ballons(self) -> str:
        return ueberpruefen_einstellungen.ballons(self._einstellungen)

    def ballons_setzen(self, wert: str) -> None:
        ueberpruefen_einstellungen.ballons_setzen(self._einstellungen, wert)

    # ---- Annehmen und Ablehnen --------------------------------------------------------------------------------------------------
    def entscheiden_zustand(self, schutz: str | None) -> EntscheidenZustand:
        alle = self._aenderungen()
        frei = bool(alle) and schutz is None
        f = _steuerung.markup_filter(self._kennung)
        gezeigt = frei and ist_gefiltert(f) and any(ist_sichtbar(b, f) for b in alle)
        am_zeiger = im_kontext_lesen(self._kennung, lambda k: k.aenderung_am_zeiger()) is not None
        return EntscheidenZustand(frei and am_zeiger, bool(gezeigt), frei)

    def angezeigte_entscheiden(self, annehmen: bool, schutz: str | None) -> None:
        if ist_geschuetzt(schutz, "aenderungen", "lesen", "kommentare"):
            self._melden(SCHUTZ_HINWEIS)
            return
        f = _steuerung.markup_filter(self._kennung)
        einzeln = AenderungenBefehle(self._kennung, self._melder)
        n = 0
        for b in reversed(self._aenderungen()):                     # von hinten, damit die Stellen davor gültig bleiben
            if ist_sichtbar(b, f):
                einzeln.entscheiden(b["von"], b["bis"], annehmen)
                n += 1
        self._melden(f"{n} angezeigte Änderungen {'angenommen' if annehmen else 'abgelehnt'}.")
