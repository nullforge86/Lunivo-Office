"""Datei-Ansicht (Backstage)."""
from __future__ import annotations

import os
from datetime import datetime
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QMessageBox
from lunivo_writer.ui.baukasten.eingabe_fenster import EingabeFenster
from lunivo_writer.ui.baukasten.speichern_fenster import Dateifenster
from lunivo_writer.models.page import HeaderFooter
from lunivo_writer.ui.dialogs.dokument_dialoge import HeaderFooterDialog, TableDialog
from lunivo_writer.ui.baukasten.dropdown.menue_tafel import MenueTafel
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.theme import kopf_symbolfarbe
from lunivo_writer.ui.hauptfenster.backstage_objektformat import BackstageObjektformatBaustein
from lunivo_writer.ui.hauptfenster.backstage_dokument import BackstageDokumentBaustein
from lunivo_writer.ui.hauptfenster.backstage_seitenleisten import BackstageSeitenleistenBaustein


from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.mass import (
    ABSTAND_NORMAL,
    BREITE_SCHIENE,
    BREITE_SCHIENE_BESCHRIFTET,
    GROESSE_KNOPF_SCHIENE,
    GROESSE_KNOPF_SCHIENE_TEXT,
    ICON_ASSISTENT,
    ICON_KNOPF_GROSS,
    ICON_LISTE,
    ICON_MITTEL,
    ICON_NORMAL,
    PADDING_BACKSTAGE_STEUERKNOPF,
    RAND_SCHIENE,
)
class BackstageBaustein(BackstageObjektformatBaustein, BackstageDokumentBaustein, BackstageSeitenleistenBaustein):
    """Datei-Ansicht (Backstage). Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""


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


    def texteffekte_seitenleiste(self):
        """Den Bereich „Texteffekte formatieren“ in der Seitenleiste öffnen; Änderungen gelten sofort für die Markierung."""
        from lunivo_writer.editor import texteffekt
        if self.current_editor() is None:
            return
        self._seitenleiste_oeffnen()

        def anwenden(w: dict):
            e = self.current_editor()
            if e is not None:
                e._merge(texteffekt.zu_format(w))
        self.sidebar.zeige_texteffekte(texteffekt.aus_format(self.befehle._fmt()), anwenden)


    def _effekt_sync(self):
        """Folgt die Markierung einer anderen Formatierung, zeigt der offene Bereich „Texteffekte“ deren Werte."""
        from lunivo_writer.editor import texteffekt
        self._format_folgen("texteffekte", lambda e: texteffekt.aus_format(self.befehle._fmt()))


    def toggle_sidebar(self):
        on = self.sidebar.isHidden()
        self.sidebar.setVisible(on)
        self.settings.set("ui/seitenleiste", on)
        if not on and self.current_tab() is not None:
            self.current_tab().editor.setFocus()                   # Seitenleiste zu: weiterschreiben, wo man war
        if hasattr(self, "_rechts"):
            self._rechts_sync()
        self._chat_knopf_pruefen()


    def zum_band_springen(self) -> None:
        """F10: aus dem Text zu den Reitern des Bandes (dann mit Tab und Pfeiltasten weiter), noch einmal F10: zurück in den Text."""
        from PySide6.QtWidgets import QApplication
        f = QApplication.focusWidget()
        t = self.current_tab()
        if f is not None and self.band.isAncestorOf(f) and t is not None:
            t.editor.setFocus()
        else:
            self.band.reiter.setFocusPolicy(Qt.StrongFocus)
            self.band.reiter.setFocus()

    def toggle_menubar(self):
        self.menubar_wanted = not self.menubar_wanted
        self.menuBar().setVisible(self.menubar_wanted)
        self.settings.set("ui/menueleiste", self.menubar_wanted)


    def find_dialog_show(self, reiter: str = "Suchen", element: str = ""):
        """Strg+F, Strg+H, Strg+G: „Suchen und ersetzen“ als Feld in der linken Seitenleiste (Reiter Suchen, Ersetzen oder Gehe zu)."""
        if self.current_editor():
            self.navigation.suche_zeigen(reiter=reiter, element=element)
