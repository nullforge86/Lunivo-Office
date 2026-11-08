"""Befehle: KI, Vorlesen."""
from __future__ import annotations

from PySide6.QtWidgets import QMenu


class KIBefehle:
    """Befehle des Bandes: KI, Vorlesen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""


    # ---- KI: Schnelle KI-Aktionen und fortlaufende Assistenten -----------------------------------------------------------
    def w_schnelleAktionErstellen(self, k=None):
        """„Schnelle KI-Aktion erstellen“: ein Eintrag (art „aktion“) in der Liste der Assistenten."""
        from lunivo_writer.ui.dialogs.ki.ki_dialoge import SchnelleAktionDialog
        d = SchnelleAktionDialog(self.w)
        if d.exec():
            e = self.w.ki.konfig.assistent_hinzufuegen(*d.werte())
            self.w.ki.geaendert.emit()
            self.w.statusBar().showMessage(f"Aktion „{e['name']}“ angelegt (KI ▸ Eigene Assistenten).", 5000)


    def w_kiAssistentErstellen(self, k=None):
        """„Neuen Assistenten erstellen“: das Fenster ``KIAssistentDialog`` (ui/dialogs/ki/ki_dialoge.py); ``werte()`` liefert die Felder für
        ``konfig.assistent_hinzufuegen(name, prompt, modus, **mehr)`` mit ``art="fortlaufend"``."""
        from lunivo_writer.ui.baukasten.geruest.fenster_stapel import ausfuehren
        from lunivo_writer.ui.dialogs.ki.ki_dialoge import KIAssistentDialog
        d = KIAssistentDialog(self.w)
        if ausfuehren(d):
            name, prompt, modus, mehr = d.werte()
            e = self.w.ki.konfig.assistent_hinzufuegen(name, prompt, modus, art="fortlaufend", **mehr)
            self.w.ki.geaendert.emit()
            self.w.statusBar().showMessage(f"Assistent „{e['name']}“ angelegt (KI ▸ Assistenten).", 5000)


    def menue_assistenten(self):
        """Das Menü „KI-Aktionen“: Schnelle KI-Aktionen und fortlaufende Assistenten (mit Haken an/aus) getrennt, neu anlegen, entfernen, Ergebnisse."""
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()

        def fuellen():
            m.clear()
            ki = self.w.ki
            aktionen, laufend = ki.konfig.assistenten("aktion"), ki.konfig.assistenten("fortlaufend")
            for a in aktionen:
                m.eintrag(a["name"], lambda a=a: ki.assistent(a))
            if not aktionen:
                m.eintrag("Noch keine eigenen KI-Aktionen", aktiv=False)
            m.addSeparator()
            m.eintrag("Neue Schnelle KI-Aktion …", self.w_schnelleAktionErstellen)
            m.addSeparator()
            m.eintrag(("✓ " if ki.dauerbetrieb() else "") + "Fortlaufende Assistenten", lambda: ki.dauerbetrieb_setzen(not ki.dauerbetrieb()))
            for a in laufend:
                m.eintrag(("✓ " if a["an"] else "") + a["name"], lambda a=a: ki.assistent_an_setzen(a["id"], not a["an"]))
            m.eintrag("Neuen Assistenten erstellen …", self.w_kiAssistentErstellen)
            alle = aktionen + laufend
            if alle:
                entf = m.untermenue("Entfernen")
                for a in alle:
                    entf.eintrag(a["name"], lambda a=a: (ki.konfig.assistent_entfernen(a["id"]), ki.geaendert.emit()))
            m.addSeparator()
            m.eintrag("Alle Ergebnisse anzeigen", self.w_kiErgebnisse)
        m.aboutToShow.connect(fuellen)
        fuellen()
        return m


    def menue_silbenTrennungMenue(self):
        """Zur Silbentrennung: wo man die Trennstriche sieht (die Bearbeitungsansicht zeigt sie nicht) und die Einstellungen."""
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Trennstriche in der Druckvorschau ansehen", self.silbentrennungVorschau)
        m.eintrag("Einstellungen der Silbentrennung …", lambda: self.w.show_options("sprache"))
        return m


    def silbentrennungVorschau(self, k=None):
        self.tun("vorschau")


    def menue_silbenMenue(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Silben einstellen …", self.silbenEinstellen)
        return m


    # ==== Vorlesen ==================================================================================================
    def vorlesen(self, k=None):
        self.w.vorlesen(ab_hier=False)


    def vorlesenAbSatz(self, k=None):
        self.w.vorlesen(ab_hier=True)


    def vorlesenStopp(self, k=None):
        from lunivo_writer.services import vorlesen as v
        v.beenden()
        self.w.lbl_msg.setText("Vorlesen angehalten.")


    def stimmeWaehlen(self, k=None):
        self.w.stimme_waehlen()


    # ==== KI ========================================================================================================
    def kiKorrektur(self, k=None): self.w.ki.korrigieren()

    def kiVorschlaege(self, k=None):
        self.w.sidebar._funde_zeigen(); self.w.ki.vorschlaege_holen()

    def kiUmformulieren(self, k=None): self.w.ki.text_aktion("umformulieren")

    def kiZusammenfassen(self, k=None):
        self.w.sidebar._funde_zeigen(); self.w.ki.zusammenfassen()

    def w_kiUebersetzenErsetzen(self, k=None): self.w.ki.uebersetzen(modus="ersetzen")

    def w_kiUebersetzenZeigen(self, k=None): self.w.ki.uebersetzen(modus="zeigen")


    def kiEntwerfen(self, k=None): self.w.chat_oeffnen("Entwirf einen Text zu folgendem Anliegen: ")

    def w_chatUmschalten(self, k=None): self.w.chat_oeffnen("")

    def _ki_einstellungen(self, reiter: int) -> None:
        from lunivo_writer.ui.baukasten.geruest.fenster_stapel import ausfuehren
        from lunivo_writer.ui.dialogs.ki.ki_dialoge import KIEinstellungenDialog
        ausfuehren(KIEinstellungenDialog(self.w, reiter))


    def w_kiEinstellungen(self, k=None): self._ki_einstellungen(0)

    def w_kiKonfiguration(self, k=None): self._ki_einstellungen(1)

    def w_kiSprache(self, k=None): self._ki_einstellungen(2)

    def w_eigenenAnbieterHinzufuegen(self, k=None): self._ki_einstellungen(0)


    def w_kiErgebnisse(self, k=None):
        from lunivo_writer.ui.dialogs.ki.ki_dialoge import ErgebnisseDialog
        ErgebnisseDialog(self.w).exec()


    def kiTextInBild(self, k=None): self.w.ki.bild_aus_text()

    def kiTextAktion(self, k=None, aktion="verbessern"): self.w.ki.text_aktion(aktion)
