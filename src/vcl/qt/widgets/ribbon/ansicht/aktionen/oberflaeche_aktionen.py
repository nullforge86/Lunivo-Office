"""Aktionen zur Benutzeroberfläche in der Ansicht: Vorlagen, Menüleiste, Register und Schnellzugriff anpassen, Symbole tauschen, Leisten umschalten, zurücksetzen.
Einstellungen und der Vorlagenordner kommen vom Farmwork."""
from __future__ import annotations

from PySide6.QtCore import QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import QMessageBox

from writer.anbindung import ansicht_einstellungen as ansicht_einstellungen
from writer.anbindung.vorlagenordner import vorlagen_ordner


class OberflaecheAktionen:
    def vorlagenWaehlen(self, k=None): self.w.neu_aus_vorlage()

    def vorlagenOrdner(self, k=None):
        QDesktopServices.openUrl(QUrl.fromLocalFile(vorlagen_ordner(self.w.settings)))

    def menueleisteZeigen(self, k=None):
        self.w.toggle_menubar()

    def an_menueleisteZeigen(self): return self.w.menubar_wanted

    def registerAnpassen(self, k=None):
        from vcl.qt.widgets.dialoge.oberflaeche_dialoge import RegisterAnpassenDialog
        if RegisterAnpassenDialog(self.w, self.w.settings, self.w.band.daten).exec():
            self.w.neu_bauen_band()

    def schnellzugriffAnpassen(self, k=None):
        from vcl.qt.widgets.dialoge.oberflaeche_dialoge import SchnellzugriffDialog
        from vcl.qt.widgets.dialoge.oberflaeche_dialoge_hilfen import lade_json
        from vcl.qt.widgets.ribbon.band_leiste import RegisterBand
        akt = lade_json(self.w.settings, "ui/schnellzugriff", None)
        if akt is None:
            akt = [a for _s, _n, a in RegisterBand.SCHNELL]
        if SchnellzugriffDialog(self.w, self.w.settings, RegisterBand.SCHNELL_ALLE, akt).exec():
            self.w.neu_bauen_band()

    def symbolTauschen(self, k=None, name=None):
        """Symbol austauschen (Ansicht ▸ Oberfläche, Optionen — und Rechtsklick auf einen Knopf, dann mit dessen Symbol)."""
        from vcl.qt.widgets.dialoge.symbol_tauschen_dialog import SymbolTauschenDialog
        d = SymbolTauschenDialog(self.w, self.w.settings, name)
        d.exec()
        if d.geaendert:
            QTimer.singleShot(0, self.w.neu_bauen_band)             # nicht mitten im Klick auf den Knopf, der gerade neu gebaut wird

    def benutzeroberflaeche(self, k=None):
        from vcl.qt.widgets.dialoge.oberflaeche_dialoge import OberflaecheDialog
        d = OberflaecheDialog(self.w, self.w.settings)
        if d.exec():
            self.w.oberflaeche_aendern(d.wahl(), d.menue.isChecked())

    def leistenZeigen(self, k=None):
        neu = "register" if ansicht_einstellungen.symbolleisten_statt_register(self.w.settings) else "symbolleisten"
        self.w.oberflaeche_aendern(neu, self.w.menubar_wanted)

    def an_leistenZeigen(self): return ansicht_einstellungen.symbolleisten_statt_register(self.w.settings)

    def vorlagenZurueck(self, k=None):
        if QMessageBox.question(self.w, "Vorlagen zurücksetzen",
                                "Register, Schnellzugriff und ausgetauschte Symbole auf die Vorgabe zurücksetzen?") != QMessageBox.Yes:
            return
        ansicht_einstellungen.oberflaeche_zuruecksetzen(self.w.settings)
        self.w._symbole_anwenden()
        self.w.neu_bauen_band()
