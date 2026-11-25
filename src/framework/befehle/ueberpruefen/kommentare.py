"""Befehle der Kommentare: durchgehen, am Zeiger löschen, alle löschen – für das Dokument mit der Kennung, über den Änderungsrahmen.
Meldungen gehen als Ereignis an den Melder der Oberfläche."""
from __future__ import annotations

from framework.befehle import ausfuehren, im_kontext_bewegen, im_kontext_lesen, lesen
from framework.befehle.ueberpruefen.schutz import SCHUTZ_HINWEIS, ist_geschuetzt
from framework.ereignisse import Melder
from framework.schnittstellen.datentypen import Art, Ereignis


class KommentareBefehle:
    def __init__(self, kennung: int, melder: Melder):
        self._kennung = kennung
        self._melder = melder

    def _melden(self, text: str, dauer_ms: int = 4000) -> None:
        self._melder.melden(Ereignis(Art.MELDUNG, text, {"dauer_ms": dauer_ms}))

    def neu_erlaubt(self, schutz: str | None) -> bool:
        """Ein neuer Kommentar ist nur ohne Schreibschutz erlaubt; sonst Hinweis in der Statusleiste."""
        if ist_geschuetzt(schutz, "lesen"):
            self._melden(SCHUTZ_HINWEIS)
            return False
        return True

    def springen(self, delta: int) -> None:
        im_kontext_bewegen(self._kennung, lambda k: int(k.springe(k.kommentar_bereiche(), delta) is not None))

    def am_zeiger_loeschen(self) -> None:
        kid = im_kontext_lesen(self._kennung, lambda k: k.kommentar_am_zeiger())
        if kid is not None:
            ausfuehren(self._kennung, lambda s: s.kommentar_loeschen(kid))
        else:
            self._melden("Der Zeiger steht in keinem Kommentar.")

    def vorhanden(self) -> bool:
        return bool(lesen(self._kennung, lambda s: len(s.dokument.kommentare)))

    def alle_loeschen(self) -> None:
        ausfuehren(self._kennung, lambda s: s.kommentar_loeschen(None))
