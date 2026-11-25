"""Befehle: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen.

``KontextBefehle`` bündelt die Fachbereiche: Tabellen (``tabellen.py``, ``tabellen_format.py``), Zeichentools (``zeichentools.py``); Bild- und Formbefehle stehen in
``bildtools.py`` und ``formtools.py``. Hier bleiben Absatzformat, Wort-Extras und RTF-Export. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``)."""
from __future__ import annotations

from vcl.qt.fenster.befehle.kontextreiter.tabellen import TabellenBefehle
from vcl.qt.fenster.befehle.kontextreiter.tabellen_format import TabellenFormatBefehle
from vcl.qt.fenster.befehle.kontextreiter.zeichentools import ZeichenToolsBefehle


class KontextBefehle(TabellenBefehle, TabellenFormatBefehle, ZeichenToolsBefehle):
    """Befehle des Bandes: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``)."""

    def absatzFormatZuruecksetzen(self, k=None):
        """Absatzformat (Blockformat) der Absätze an der Schreibmarke/Auswahl auf Standard; Zeichenformat bleibt. Ein Rückgängig-Schritt."""
        e = self.ed
        if e:
            e.ansicht._aendern(lambda s: s.absatzformat_anwenden({}, ersetzen=True))

    def wortExtras(self, k=None):
        """Wort-Extras: Absätze aufräumen (Markierung, sonst das ganze Dokument)."""
        if self.ed:
            self._popup(self.menue_wortExtrasKlappe())

    def menue_wortExtrasKlappe(self):
        """Das Menü „Wort-Extras“ wie in der Vorlage, mit dem Untermenü „Löschen“; jeder Eintrag ist ein Schritt für Rückgängig."""
        from writer.funktionen import bearbeiten as WX
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole

        def fuellen(m, eintraege):
            for e in eintraege:
                if e.trenner:
                    m.trenner()
                elif e.unter:
                    fuellen(m.untermenue(e.text, symbole.icon(e.symbol, 16)), e.unter)
                else:
                    m.eintrag(e.text, lambda t=e.text, b=e.befehl: self.ed and self._wort_extra(t, b), symbol=symbole.icon(e.symbol, 16))
        m = MenueListe()
        fuellen(m, WX.wortextras_menue())
        return m

    def _wort_extra(self, text, befehl):
        from writer.funktionen import bearbeiten as WX
        n = WX.wortextra_ausfuehren(self.ed.kennung, befehl)
        self.w.statusBar().showMessage(f"{text}: {n} Stelle(n) geändert." if n else f"{text}: nichts zu ändern.", 5000)

    def exportierenRtf(self, k=None): self.w.export_as(".rtf")
