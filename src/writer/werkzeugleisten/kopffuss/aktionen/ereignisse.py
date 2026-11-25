"""Ereignisse des Frameworks für „Kopf- und Fußzeile“ in der Oberfläche: Meldungen in die Statusleiste, Fenster und Dialoge öffnen."""
from __future__ import annotations

from framework.schnittstellen.datentypen.ereignisdaten import Ereignis


class KopfFussEreignisse:
    def _kf_meldung(self, e: Ereignis) -> None:
        self.w.statusBar().showMessage(e.text, e.daten.get("dauer_ms", 4000))

    def _kf_oeffnen(self, e: Ereignis) -> None:
        if e.text == "bearbeiten":
            self._kf_start(e.daten["zone"])
        elif e.text == "optionen":
            self.kfOptionen()
        elif e.text == "seite_einrichten":
            self.w.page_setup()

    def _kf_start(self, zone: str):
        t = self.w.current_tab()
        if t:
            self.w.kopffuss_starten(t.editor, zone == "kopf")
