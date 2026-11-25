"""Aktionen des Zooms: größer, kleiner, normal, Seitenbreite, ganze Seite, Zoomstufe wählen. Der Zoomwert liegt im Editor, die Befehle im Farmwork."""
from __future__ import annotations

from lunivo_writer.oberflaeche.dialoge.dokument_dialoge import ZoomDialog


class ZoomAktionen:
    def groesser(self, k=None):
        fw = self._ansicht()
        if fw is not None:
            fw.zoom_um(1.1)

    def kleiner(self, k=None):
        fw = self._ansicht()
        if fw is not None:
            fw.zoom_um(1 / 1.1)

    def normal(self, k=None):
        fw = self._ansicht()
        if fw is not None:
            fw.zoom_setzen(1.0)

    def zoomBreite(self, k=None):
        t = self.w.current_tab()
        if t:
            t.zoom_breite()

    def zoomSeite(self, k=None):
        t = self.w.current_tab()
        if t:
            t.zoom_seite()

    def zoomStufe(self, k=None):
        fw = self._ansicht()
        if fw is None:
            return
        d = ZoomDialog(self.w, fw.zoom())
        if d.exec():
            art, wert = d.ergebnis()
            if art == "breite":
                self.zoomBreite()
            elif art == "seite":
                self.zoomSeite()
            else:
                fw.zoom_setzen(wert)
