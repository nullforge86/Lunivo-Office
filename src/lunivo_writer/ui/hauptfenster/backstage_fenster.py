"""Weitere Fenster- und Seitenleistenaktionen der Backstage-Ansicht."""
from __future__ import annotations

from PySide6.QtCore import Qt


class BackstageFensterBaustein:
    """Baustein für Texteffekte und allgemeine Fensteraktionen."""

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
