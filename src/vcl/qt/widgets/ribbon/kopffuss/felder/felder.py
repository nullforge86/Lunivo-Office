"""Felder im Reiter „Kopf- und Fußzeile“: Kopfzeilenhöhe und Fußzeilenhöhe; Werte kommen vom Framework, gebaut wird mit ``abstandsfeld``."""
from __future__ import annotations

from vcl.qt.widgets.ribbon.kopffuss.felder.abstandsfeld import abstandsfeld


class KopfFussFelder:
    def _kf_abstandsfeld(self, zone: str, name: str, symbol: str):
        def lesen():
            fw = self._fw()
            if fw is None:
                return None
            o = fw.optionen()
            return o.kopf_abstand_mm if zone == "kopf" else o.fuss_abstand_mm

        def schreiben(wert):
            fw = self._fw()
            if fw is not None:
                fw.abstand_setzen(zone, float(wert))
        return abstandsfeld(name, symbol, lesen, schreiben)

    def feld_kopfHoehe(self): return self._kf_abstandsfeld("kopf", "Kopfzeilenhöhe", "kopfz")

    def feld_fussHoehe(self): return self._kf_abstandsfeld("fuss", "Fußzeilenhöhe", "fussz")
