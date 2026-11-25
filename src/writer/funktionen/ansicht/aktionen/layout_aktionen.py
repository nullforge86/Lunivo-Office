"""Aktionen der Dokumentansichten: Layout (Blatt, Entwurf …), Gliederung, Lineale, versteckter Text, Marken, Navigation. Einstellungen und Editor-Befehle liegen im Farmwork."""
from __future__ import annotations

from framework.funktionen.ansicht import einstellungen as ansicht_einstellungen


class LayoutAktionen:
    def w_setzeLayout(self, k=None, art="blatt"):
        t = self.w.current_tab()
        if t:
            if art != "blatt" and t.editor.gliederung:
                self.gliederung()
            t.set_layout(art)
            self.w.band.aktualisieren(True)

    def w_layoutJetzt(self, k=None):
        t = self.w.current_tab()
        return t.layout_art if t else "blatt"

    def gliederung(self, k=None):
        t = self.w.current_tab()
        if not t:
            return
        if t.layout_art != "blatt":
            t.set_layout("blatt")
        self._ansicht().gliederung_umschalten()

    def an_gliederung(self):
        fw = self._ansicht()
        return bool(fw is not None and fw.gliederung_an())

    def linealZeigen(self, k=None):
        ansicht_einstellungen.lineal_umschalten(self.w.settings)
        self.w.lineale_anwenden()

    def linealHochZeigen(self, k=None):
        ansicht_einstellungen.lineal_hoch_umschalten(self.w.settings)
        self.w.lineale_anwenden()

    def an_linealZeigen(self): return ansicht_einstellungen.lineal_zeigen(self.w.settings)

    def an_linealHochZeigen(self): return ansicht_einstellungen.lineal_hoch_zeigen(self.w.settings)

    def versteckteZeigen(self, k=None):
        ansicht_einstellungen.verstecktes_umschalten(self.w.settings)
        self.w.versteckt_anwenden()

    def an_versteckteZeigen(self): return ansicht_einstellungen.verstecktes_zeigen(self.w.settings)

    def markenZeigen(self, k=None):
        fw = self._ansicht()
        if fw is not None:
            self.w.set_marken(not fw.marken_an())

    def an_markenZeigen(self):
        fw = self._ansicht()
        return bool(fw is not None and fw.marken_an())

    def navigation(self, k=None):
        self.w.toggle_navigation()

    def an_navigation(self): return self.w.navigation.isVisible()
