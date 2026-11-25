"""Befehle der nachverfolgten Änderungen: verfolgen, Markup, durchgehen, annehmen und ablehnen – für das Dokument mit der Kennung.

Verfolgen gehört zur Bearbeitungssitzung, das Markup zur Anzeige des Dokuments im Framework; beides meldet ``anzeige_geaendert``."""
from __future__ import annotations

from core.bearbeitung import Kontext
from framework.befehle import ausfuehren, im_kontext_bewegen, im_kontext_lesen, lesen
from framework.befehle.ueberpruefen.schutz import SCHUTZ_HINWEIS, ist_geschuetzt
from framework.ereignisse import Melder
from framework.schnittstellen.datentypen import Art, Ereignis
from framework.sitzungen import sitzung as _steuerung

_ENTSCHEIDEN = ("aenderungen", "lesen", "kommentare")      # bei diesen Schutzarten dürfen Änderungen nicht angenommen oder abgelehnt werden


def _verfolgen_setzen(s, an: bool) -> int:
    s.nachverfolgen = bool(an)
    return 1


class AenderungenBefehle:
    def __init__(self, kennung: int, melder: Melder):
        self._kennung = kennung
        self._melder = melder

    def _melden(self, text: str, dauer_ms: int = 4000) -> None:
        self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": dauer_ms}))

    def _frei(self, schutz: str | None, *arten: str) -> bool:
        if ist_geschuetzt(schutz, *arten):
            self._melden(SCHUTZ_HINWEIS)
            return False
        return True

    # ---- Verfolgen und Markup ---------------------------------------------------------------------------------------------
    def verfolgen_umschalten(self, schutz: str | None) -> None:
        if not self._frei(schutz, "aenderungen"):
            return
        an = not self.verfolgt()
        lesen(self._kennung, lambda s: _verfolgen_setzen(s, an))
        _steuerung.anzeige_melden(self._kennung)
        self._melden("Änderungen werden verfolgt." if self.verfolgt() else "Verfolgung beendet.", 3000)

    def verfolgt(self) -> bool:
        return bool(lesen(self._kennung, lambda s: int(bool(s.nachverfolgen))))

    def markup_umschalten(self) -> None:
        _steuerung.markup_setzen(self._kennung, not _steuerung.markup_an(self._kennung))

    def markup_an(self) -> bool:
        return _steuerung.markup_an(self._kennung)

    # ---- Durchgehen, annehmen, ablehnen -------------------------------------------------------------------------------------
    def _springe(self, delta: int):
        return im_kontext_bewegen(self._kennung, lambda k: k.springe(k.aenderungen(), delta))

    def springen(self, delta: int) -> None:
        self._springe(delta)

    def entscheiden(self, von: int, bis: int, annehmen: bool) -> None:
        """Die Änderung zwischen den Stellen ``von`` und ``bis`` annehmen oder ablehnen."""
        ausfuehren(self._kennung, lambda s: _abschliessen(s, von, bis, annehmen))

    def am_zeiger_entscheiden(self, annehmen: bool, schutz: str | None) -> None:
        if not self._frei(schutz, *_ENTSCHEIDEN):
            return
        b = im_kontext_lesen(self._kennung, lambda k: k.aenderung_am_zeiger()) or self._springe(1)
        if b:
            self.entscheiden(b["von"], b["bis"], annehmen)
            self._springe(1)

    def alle_entscheiden(self, annehmen: bool, schutz: str | None) -> None:
        if self._frei(schutz, *_ENTSCHEIDEN):
            n = im_kontext_lesen(self._kennung, lambda k: len(k.aenderungen())) or 0
            ausfuehren(self._kennung, lambda s: (s.aenderungen_annehmen if annehmen else s.aenderungen_ablehnen)(None))
            self._melden(f"{n} Änderungen {'angenommen' if annehmen else 'abgelehnt'}.")


def _abschliessen(s, von: int, bis: int, annehmen: bool) -> int:
    bereich = Kontext(s).bereich(von, bis)
    return (s.aenderungen_annehmen if annehmen else s.aenderungen_ablehnen)(bereich)
