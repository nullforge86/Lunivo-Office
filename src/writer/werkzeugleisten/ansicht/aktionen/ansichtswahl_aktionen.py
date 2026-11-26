"""Aktionen der Ansichtswahl in der Statusleiste: ordnet die gewählte Dokumentansicht (Drucklayout, Gliederung, Lesemodus, Weblayout) den vorhandenen
Befehlen zu und nennt die Ansicht, die im Augenblick gilt. Die Ansichten schließen einander aus."""
from __future__ import annotations


class AnsichtswahlAktionen:
    def ansichtWaehlen(self, k=None, art="blatt"):
        """``art``: ``blatt`` | ``gliederung`` | ``lesen`` | ``web`` (Kennungen aus ``writer.funktionen.ansicht.ANSICHTSARTEN``)."""
        if art == "lesen":
            if not self.an_lesemodus():
                self.lesemodus()
            return
        if self.an_lesemodus():
            self.lesemodus()
        if art == "gliederung":
            if not self.an_gliederung():
                self.gliederung()
            return
        if self.an_gliederung():
            self.gliederung()
        self.w_setzeLayout(art=art)

    def ansichtJetzt(self) -> str:
        """Kennung der Ansicht, die im Augenblick gilt; zwei Seiten nebeneinander zählen zum Drucklayout."""
        if self.an_lesemodus():
            return "lesen"
        if self.an_gliederung():
            return "gliederung"
        return "web" if self.w_layoutJetzt() == "web" else "blatt"
