"""Befehle: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen.

``KontextBefehle`` bündelt die Fachbereiche: Tabellen (``tabellen.py``, ``tabellen_format.py``), Zeichentools (``zeichentools.py``); Bild- und Formbefehle stehen in
``bildtools.py`` und ``formtools.py``. Hier bleiben Absatzformat, Wort-Extras und RTF-Export. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``)."""
from __future__ import annotations

from framework.befehle.kontextreiter.tabellen import TabellenBefehle
from framework.befehle.kontextreiter.tabellen_format import TabellenFormatBefehle
from framework.befehle.kontextreiter.zeichentools import ZeichenToolsBefehle


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
        from core.text import wortextras as W
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole

        def fuellen(m, zeilen):
            for z in zeilen:
                if z == "-":
                    m.trenner()
                elif isinstance(z[2], list):
                    fuellen(m.untermenue(z[0], symbole.icon(z[1], 16)), z[2])
                else:
                    m.eintrag(z[0], lambda t=z[0], f=z[2]: self.ed and self._wort_extra(t, f), symbol=symbole.icon(z[1], 16))
        m = MenueListe()
        fuellen(m, W.MENUE)
        return m

    def _wort_extra(self, text, f):
        n = f(self.ed)
        self.w.statusBar().showMessage(f"{text}: {n} Stelle(n) geändert." if n else f"{text}: nichts zu ändern.", 5000)

    def exportierenRtf(self, k=None): self.w.export_as(".rtf")
