"""Befehle der Funktion „Ansicht“, die den Editor betreffen: Zoom, ausgeblendeter Text, Marken und Gliederung. Der Editor kommt über den ``EditorPort``
herein; Meldungen gehen als Ereignis an den ``Melder``. Fenster, Band und Dialoge sind Sache der Oberfläche."""
from __future__ import annotations

from lunivo_writer.farmwork.datentypen.ereignisdaten import Art, Ereignis
from lunivo_writer.farmwork.schnittstellen.dokument import EditorPort
from lunivo_writer.farmwork.steuerung.ereignissteuerung import Melder

GLIEDERUNG_AN = "Gliederung: nur Überschriften. Alt+Umschalt+←/→ ändert die Ebene."
GLIEDERUNG_AUS = "Gliederung beendet."


class AnsichtBefehle:
    def __init__(self, editor: EditorPort, melder: Melder):
        self._e = editor
        self._melder = melder

    # ---- Zoom -----------------------------------------------------------------------------------------------------------------
    def zoom(self) -> float:
        return float(self._e.zoom)

    def zoom_um(self, faktor: float) -> None:
        self._e.set_zoom(self._e.zoom * faktor)

    def zoom_setzen(self, wert: float) -> None:
        self._e.set_zoom(wert)

    # ---- Text -----------------------------------------------------------------------------------------------------------------
    def ausblenden_umschalten(self) -> None:
        """Markierten Text als „ausgeblendet“ formatieren (Strg+Umschalt+H)."""
        self._e.set_versteckt(not self._e.ist_versteckt())

    def ausgeblendet(self) -> bool:
        return bool(self._e.ist_versteckt())

    def marken_an(self) -> bool:
        return bool(self._e.marken)

    # ---- Gliederung -------------------------------------------------------------------------------------------------------------
    def gliederung_an(self) -> bool:
        return bool(self._e.gliederung)

    def gliederung_umschalten(self) -> bool:
        neu = not self._e.gliederung
        self._e.set_gliederung(neu)
        self._melder.melden(Ereignis(Art.MELDUNG, GLIEDERUNG_AN if neu else GLIEDERUNG_AUS, {"dauer_ms": 5000}))
        return neu
