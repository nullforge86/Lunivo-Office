"""Klappen (Pfeilmenüs) im Reiter „Überprüfen“: Rechtschreibprüfung, Kommentar löschen, Änderungen nachverfolgen, Vergleichen."""
from __future__ import annotations

from vcl.qt.widgets.bausteine.dropdown.menue_liste import MenueListe

VERFOLGEN_TIP = "Strg+Umschalt+E ist in Lunivo „Als PDF exportieren“."


class PruefenKlappen:
    def menue_rechtschreibKlappe(self):
        m = MenueListe()
        m.eintrag("Rechtschreibprüfung …", self.rechtschreibung, symbol=self._sym("rechtschreibpruefung"), kuerzel="F7")
        m.eintrag("Sprache festlegen …", self.pruefsprache, symbol=self._sym("sprache"))
        return m

    def menue_kommentarLoeschenKlappe(self):
        m = MenueListe()
        eins = m.eintrag("Kommentar löschen", self.kommentarWeg, symbol=self._sym("kommentarloeschen"))
        alle = m.eintrag("Alle Kommentare im Dokument löschen", self.kommentareAlleWeg, symbol=self._sym("kommentareweg"))

        def auffrischen():
            fw = self._markup()
            eins.setEnabled(bool(fw is not None and fw.kommentar_am_zeiger()))
            alle.setEnabled(self._hat_kommentare())
        m.aboutToShow.connect(auffrischen)
        return m

    def menue_verfolgenKlappe(self):
        m = MenueListe()
        an = m.eintrag("Änderungen nachverfolgen", lambda: (self.verfolgen(), self.w.band.aktualisieren()),
                       symbol=self._sym("nachverfolgen"), haken=False, tip=VERFOLGEN_TIP)
        m.eintrag("Optionen zum Nachverfolgen von Änderungen …", lambda: self.w.show_options("verfolgen"), symbol=self._sym("verfolgoptionen"))
        m.eintrag("Benutzernamen ändern …", lambda: self.w.show_options("benutzer"), symbol=self._sym("benutzername"))
        m.aboutToShow.connect(lambda: (an.setChecked(self.an_verfolgen()), an.setEnabled(self.ed is not None)))
        return m

    def menue_vergleichenKlappe(self):
        m = MenueListe()
        m.eintrag("Vergleichen …", self.dokumenteVergleichen, symbol=self._sym("vergleichen"))
        m.eintrag("Zusammenführen …", self.dokumenteZusammenfuehren, symbol=self._sym("zusammenfuehren"))
        quellen = m.untermenue("Quelldokumente anzeigen(&S)", self._sym("kopie"), aktiv=False)
        quellen.eintrag("Quelldokumente ausblenden")
        return m
