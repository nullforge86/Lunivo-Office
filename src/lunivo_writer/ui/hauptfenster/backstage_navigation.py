"""Navigation und Öffnen/Schließen der Backstage-Dateiansicht."""
from __future__ import annotations

from PySide6.QtCore import QSize
from lunivo_writer.ui.baukasten.dropdown.menue_tafel import MenueTafel
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.theme import kopf_symbolfarbe
from lunivo_writer.ui.baukasten.basis.mass import ICON_NORMAL, PADDING_BACKSTAGE_STEUERKNOPF


class BackstageNavigationBaustein:
    """Baustein für die Navigation der Backstage-Dateiansicht."""

    def _backstage_verbinden(self):
        r = getattr(self.band, "reiter", None)
        if r is None:
            return
        self.backstage.hide()
        self.arbeit.show()
        r.currentChanged.connect(self._reiter_gewechselt)
        r.tabBarClicked.connect(self._reiter_angeklickt)
        # Die Datei-Ansicht heißt „☰ Menü“ und steht ganz links vor dem Schnellzugriff; der Reiter „Datei“ bleibt dafür verborgen
        for i in range(r.count()):
            if r.tabText(i) == "Datei":
                r.setTabVisible(i, False)
        k = self.band.menue_knopf
        try:
            k.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        k.setText("Menü"); k.setIcon(icons.icon("menu", ICON_NORMAL, kopf_symbolfarbe())); k.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL)); k.setCheckable(True); k.setToolTip("Menü: Neu, Öffnen, Speichern, Exportieren, Drucken, Optionen, Hilfe")
        k.setStyleSheet('QToolButton { font-weight: 600; padding: ' f"{PADDING_BACKSTAGE_STEUERKNOPF}" '; }')          # die Farbe des geöffneten Menüs kommt aus dem Thema (theme.py)
        k.clicked.connect(self._menue_geklickt)
        r.currentChanged.connect(lambda i, kk=k: kk.setChecked(self._ist_datei(i)))


    def _menue_geklickt(self):
        """☰ Menü: öffnet die Datei-Ansicht, ein zweiter Klick schließt sie wieder."""
        r = self.band.reiter
        if self.backstage.isVisible():
            self.backstage_schliessen()
            return
        i = next((n for n in range(r.count()) if r.tabText(n) == "Datei"), None)
        if i is not None:
            r.setCurrentIndex(i)
        self.band.menue_knopf.setChecked(self.backstage.isVisible())


    def _ist_datei(self, i: int) -> bool:
        r = self.band.reiter
        return 0 <= i < r.count() and r.tabText(i) == "Datei"


    def _reiter_gewechselt(self, i: int):
        if self._ist_datei(i):
            self.backstage_oeffnen()
        else:
            self._letzter_reiter = i
            self.backstage_zu()


    def _reiter_angeklickt(self, i: int):
        import time
        if self._ist_datei(i) and self.backstage.isVisible() and time.monotonic() - self._bs_zeit > 0.4:   # zweiter Klick schließt
            self.backstage_schliessen()


    def backstage_oeffnen(self, seite: str = "zuletzt", unter: str | None = None):
        import time
        self._bs_zeit = time.monotonic()
        for name in ("stapel", "linie"):                              # die Oberfläche „Symbolleisten“ hat nur eine Leiste, kein Band mit Reitern
            if hasattr(self.band, name):
                getattr(self.band, name).hide()
        self.arbeit.hide()
        self.backstage.oeffnen(seite, unter)
        self.backstage.show()
        if hasattr(self.band, "menue_knopf"):
            self.band.menue_knopf.setChecked(True)


    def backstage_zu(self):
        if not self.backstage.isVisible():
            return
        self.backstage.hide()
        self.arbeit.show()
        if hasattr(self.band, "stapel") and not self.band._eingeklappt:
            self.band.stapel.show()
        if hasattr(self.band, "linie"):
            self.band.linie.show()
        if hasattr(self.band, "menue_knopf"):
            self.band.menue_knopf.setChecked(False)
        self.ki.geaendert.emit()                                   # Einstellungen der Optionen übernehmen (KI, Anbieter …)
        t = self.current_tab()
        if t is not None:
            t.editor.setFocus()                                    # Arbeitskontext: weiterschreiben, wo man aufgehört hat


    def backstage_schliessen(self):
        r = self.band.reiter
        if self._ist_datei(r.currentIndex()):
            r.setCurrentIndex(self._letzter_reiter if not self._ist_datei(self._letzter_reiter) else 1)
        self.backstage_zu()


    def show_main_menu(self):
        daten = next(m for m in self.band.daten["menues"] if m["name"] == "Datei")
        self._tafel = MenueTafel(daten["punkte"], self.befehle, self)
        self._tafel.zeigen_unter(self.band.menue_knopf)
