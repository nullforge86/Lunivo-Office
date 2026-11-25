"""Aktionen der Knöpfe im Reiter „Kopf- und Fußzeile“: ruft die Befehle des Frameworks auf."""
from __future__ import annotations

from lunivo_writer.oberflaeche.funktionen.kopffuss.dialoge.optionen_dialog import optionen_fragen


class KopfFussAktionen:
    def kopfFussSchliessen(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.schliessen()

    def kfWechseln(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.wechseln()

    def kfVorige(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.springen(-1)

    def kfNaechste(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.springen(1)

    def kfVerknuepfen(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.bearbeiter_verknuepfen()

    def kfTabstopp(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.tabstopp_einfuegen()

    def kfOptionen(self, k=None):
        """Seitenleistenfenster: Erste Seite anders; Gerade und ungerade Seiten unterschiedlich."""
        fw = self._fw()
        if fw is None:
            return
        antwort = optionen_fragen(self.w, fw.optionen())
        if antwort is not None:
            fw.optionen_setzen(*antwort)

    def kopfVerknuepfen(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.verknuepfung_umschalten("kopf")

    def fussVerknuepfen(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.verknuepfung_umschalten("fuss")

    def ersteSeiteAnders(self, k=None):
        fw = self._fw()
        if fw is not None:
            fw.erste_seite_anders_umschalten()

    def geradeUngerade(self, k=None):
        """„Gerade und ungerade Seiten sind unterschiedlich“: gerade Seiten bekommen eine eigene Kopf-/Fußzeile (zuerst eine Kopie der gewöhnlichen)."""
        fw = self._fw()
        if fw is not None:
            fw.gerade_ungerade_umschalten()
