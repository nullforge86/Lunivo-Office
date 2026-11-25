"""Aktionen der Auswahl: alles markieren, Tabelle ohne Rahmen, ähnliche Formatierung, Auswahlbereich. Die Befehle liegen im Farmwork."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.interaktion.felder.auswahl_bereich import AuswahlBereich
from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren


class AuswahlAktionen:
    def allesMarkieren(self, k=None):
        fw = self._bearbeiten()
        if fw is not None:
            fw.alles_markieren()

    def tabelleOhneRahmen(self, k=None):
        fw = self._bearbeiten()
        if fw is not None:
            fw.tabelle_ohne_rahmen_waehlen()

    def aehnlicheFormatierung(self, k=None):
        fw = self._bearbeiten()
        if fw is not None:
            fw.aehnliche_formatierung()

    def auswahlbereich(self, k=None):
        """Der Bereich „Auswahl“: alle Bilder, Formen und Tabellen des Dokuments in einer Liste; ein Klick markiert das Objekt."""
        if not self.ed:
            return
        ausfuehren(AuswahlBereich(self.w, self.ed))
