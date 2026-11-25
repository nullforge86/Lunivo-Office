"""Befehle der Kommentare: durchgehen, am Zeiger löschen, alle löschen. Der Editor kommt über den ``EditorPort`` herein; Meldungen gehen als Ereignis."""
from __future__ import annotations

from framework.datentypen.ereignisdaten import Art, Ereignis
from framework.funktionen.ueberpruefen.schutz import SCHUTZ_HINWEIS, ist_geschuetzt
from framework.schnittstellen.dokument import EditorPort
from framework.steuerung.ereignissteuerung import Melder


class KommentareBefehle:
    def __init__(self, editor: EditorPort, melder: Melder):
        self._editor = editor
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
        self._editor.kommentar_springen(delta)

    def am_zeiger_loeschen(self) -> None:
        kid = self._editor.kommentar_am_cursor()
        if kid is not None:
            self._editor.kommentar_loeschen(kid)
        else:
            self._melden("Der Zeiger steht in keinem Kommentar.")

    def vorhanden(self) -> bool:
        return bool(self._editor.kommentare)

    def alle_loeschen(self) -> None:
        self._editor.kommentare_alle_loeschen()
