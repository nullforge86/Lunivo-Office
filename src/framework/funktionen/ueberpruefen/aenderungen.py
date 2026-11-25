"""Befehle der nachverfolgten Änderungen: verfolgen, Markup, durchgehen, annehmen und ablehnen. Der Editor kommt über den ``EditorPort`` herein."""
from __future__ import annotations

from framework.datentypen.ereignisdaten import Art, Ereignis
from framework.funktionen.ueberpruefen.schutz import SCHUTZ_HINWEIS, ist_geschuetzt
from framework.schnittstellen.dokument import EditorPort
from framework.steuerung.ereignissteuerung import Melder

_ENTSCHEIDEN = ("aenderungen", "lesen", "kommentare")      # bei diesen Schutzarten dürfen Änderungen nicht angenommen oder abgelehnt werden


class AenderungenBefehle:
    def __init__(self, editor: EditorPort, melder: Melder):
        self._editor = editor
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
        self._editor.set_verfolgen(not self._editor.verfolgen)
        self._melden("Änderungen werden verfolgt." if self._editor.verfolgen else "Verfolgung beendet.", 3000)

    def verfolgt(self) -> bool:
        return bool(self._editor.verfolgen)

    def markup_umschalten(self) -> None:
        self._editor.set_markup(not self._editor.markup)

    def markup_an(self) -> bool:
        return bool(self._editor.markup)

    # ---- Durchgehen, annehmen, ablehnen -------------------------------------------------------------------------------------
    def springen(self, delta: int) -> None:
        self._editor.aenderung_springen(delta)

    def am_zeiger_entscheiden(self, annehmen: bool, schutz: str | None) -> None:
        if not self._frei(schutz, *_ENTSCHEIDEN):
            return
        b = self._editor.aenderung_am_cursor() or self._editor.aenderung_springen(1)
        if b:
            self._editor.aenderung_annehmen(b, annehmen)
            self._editor.aenderung_springen(1)

    def alle_entscheiden(self, annehmen: bool, schutz: str | None) -> None:
        if self._frei(schutz, *_ENTSCHEIDEN):
            n = self._editor.alle_aenderungen(annehmen)
            self._melden(f"{n} Änderungen {'angenommen' if annehmen else 'abgelehnt'}.")
