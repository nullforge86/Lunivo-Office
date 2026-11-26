"""Klappen (Pfeilmenüs) des Markups im Reiter „Überprüfen“: Markup anzeigen, Überprüfen (Bearbeiter, Zeiten, Fenster), Annehmen und Ablehnen.
Zustände und Filter kommen vom Farmwork."""
from __future__ import annotations

from writer.anbindung import ueberpruefen_einstellungen as ueberpruefen_einstellungen
from writer.anbindung.ueberpruefen_einstellungen import ballon_werte
from writer.hauptfenster import entscheiden_zustand_leer
from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe


class MarkupKlappen:
    def _filter_setzen(self, **werte) -> None:
        fw = self._markup()
        if fw is not None:
            fw.filter_setzen(**werte)

    def _bearbeiter_fuellen(self, m) -> None:
        fw = self._markup()
        namen = fw.bearbeiter_namen() if fw is not None else ()
        m.clear(); m.setEnabled(bool(namen))
        gewaehlt = fw.filter().bearbeiter if fw is not None else None
        m.eintrag("Alle Bearbeiter", lambda: self._filter_setzen(bearbeiter=None), haken=gewaehlt is None)
        m.trenner()
        for n in namen:
            m.eintrag(n, lambda n=n: self._markup().bearbeiter_umschalten(n), haken=gewaehlt is None or n in gewaehlt)

    def _zeiten_fuellen(self, m) -> None:
        fw = self._markup()
        tage = fw.zeiten() if fw is not None else ()
        m.clear(); m.setEnabled(bool(tage))
        gewaehlt = fw.filter().zeit if fw is not None else None
        m.eintrag("Alle Zeiten", lambda: self._filter_setzen(zeit=None), haken=gewaehlt is None)
        m.trenner()
        for tag in tage:
            m.eintrag(tag, lambda tag=tag: self._filter_setzen(zeit=tag), haken=gewaehlt == tag)

    def menue_markupKlappe(self):
        m = MenueListe()
        kom = m.eintrag("Kommentare anzeigen(&C)", lambda: self._filter_setzen(kommentare=not self._markup().filter().kommentare), haken=True)
        ein = m.eintrag("Einfügungen und Löschungen anzeigen",
                        lambda: self._filter_setzen(einfuegungen=not self._markup().filter().einfuegungen), haken=True)
        form = m.eintrag("Formatierung anzeigen", haken=True, aktiv=False, tip="Formatänderungen verfolgt Lunivo noch nicht.")
        bearb = m.untermenue("Bearbeiter", self._sym("bearbeiter"))
        ballons = m.untermenue("Ballons verwenden", self._sym("sprechblase"))

        def setze_ballons(wert):
            ueberpruefen_einstellungen.ballons_setzen(self.w.settings, wert)
            self.w.markup_neu()

        def auffrischen():
            fw = self._markup()
            da = fw is not None
            for a in (kom, ein):
                a.setEnabled(da)
            if da:
                f = fw.filter()
                kom.setChecked(f.kommentare); ein.setChecked(f.einfuegungen)
            form.setChecked(True)
            self._bearbeiter_fuellen(bearb)
            ballons.clear()
            jetzt = ueberpruefen_einstellungen.ballons(self.w.settings)
            for text, wert in ballon_werte():
                ballons.eintrag(text, lambda w=wert: setze_ballons(w), haken=jetzt == wert)
        m.aboutToShow.connect(auffrischen)
        return m

    def menue_ueberpruefenKlappe(self):
        m = MenueListe()
        bearb = m.untermenue("Bearbeiter", self._sym("bearbeiter"))
        zeit = m.untermenue("Überprüfungszeit", self._sym("pruefzeit"))
        fenster = m.untermenue("Überarbeitungsfenster(&P)", self._sym("ueberpruefenfenster"))
        fenster.eintrag("Vertikales Überarbeitungsfenster", self.ueberarbeitungsbereich, symbol=self._sym("bereich"))
        fenster.eintrag("Horizontales Überarbeitungsfenster", aktiv=False, tip="Das Überarbeitungsfenster steht in Lunivo links.")
        m.aboutToShow.connect(lambda: (self._bearbeiter_fuellen(bearb), self._zeiten_fuellen(zeit)))
        return m

    def _angezeigte(self, annehmen: bool) -> None:
        fw = self._markup()
        if fw is not None:
            fw.angezeigte_entscheiden(annehmen, self._schutz_wert())

    def _entscheiden_menue(self, annehmen: bool):
        wort = "annehmen" if annehmen else "ablehnen"
        sym = self._sym("aenderungannehmen" if annehmen else "aenderungablehnen")
        m = MenueListe()
        eins = m.eintrag(f"Änderung {wort}(&C)", self.aenderungAnnehmen if annehmen else self.aenderungAblehnen, symbol=sym)
        m.eintrag(f"Formatänderungen im Dokument {wort}", aktiv=False, tip="Formatänderungen verfolgt Lunivo noch nicht.")
        gezeigt = m.eintrag(f"Angezeigte Änderungen im Dokument {wort}", lambda: self._angezeigte(annehmen))
        alle = m.eintrag(f"Alle Änderungen in Dokument {wort}",
                         self.aenderungenUebernehmen if annehmen else self.aenderungenVerwerfen,
                         symbol=sym)

        def auffrischen():
            fw = self._markup()
            z = fw.entscheiden_zustand(self._schutz_wert()) if fw is not None else entscheiden_zustand_leer()
            eins.setEnabled(z.eine)
            gezeigt.setEnabled(z.angezeigte)
            alle.setEnabled(z.alle)
        m.aboutToShow.connect(auffrischen)
        return m

    def menue_annehmenKlappe(self): return self._entscheiden_menue(True)

    def menue_ablehnenKlappe(self): return self._entscheiden_menue(False)
