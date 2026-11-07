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
from lunivo_writer.ui.hauptfenster.backstage_navigation import BackstageNavigationBaustein


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
class BackstageBaustein(BackstageObjektformatBaustein, BackstageDokumentBaustein, BackstageSeitenleistenBaustein, BackstageNavigationBaustein):
    """Datei-Ansicht (Backstage). Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""


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
