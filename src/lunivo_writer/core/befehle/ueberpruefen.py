"""Befehle: Reiter „Überprüfen“ nach den Vorlagen (ueberpruefen/01–10) — Klappen, Anzeige der Fassung, Markup-Auswahl,
Annehmen/Ablehnen der angezeigten Änderungen, Bearbeitung einschränken."""
from __future__ import annotations

ANZEIGEN = ("Endgültige Version enthält Markups", "Endgültige Version", "Original enthält Markups", "Original")
VERFOLGEN_TIP = "Strg+Umschalt+E ist in Lunivo „Als PDF exportieren“."


class UeberpruefenBefehle:
    """Befehle des Reiters „Überprüfen“. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).

    Was das Markup zeigt, steht am Editor (``markup_filter``); der Dokumentschutz am Dokumentfenster (``tab.schutz``: None,
    "lesen", "aenderungen" oder "kommentare") — beides nur für diese Sitzung, nichts davon landet in der Datei."""

    @staticmethod
    def _sym(name):
        from lunivo_writer.ui.widgets import icons
        return icons.icon(name, 18)

    # ---- Zustand -----------------------------------------------------------------------------------------------
    def _hat_kommentare(self) -> bool:
        return bool(self.ed and self.ed.kommentar_bereiche())

    def _hat_aenderungen(self) -> bool:
        return bool(self.ed and self.ed.aenderungen())

    def _schutz(self) -> str | None:
        t = self.w.current_tab()
        return getattr(t, "schutz", None) if t else None

    def _darf_aendern(self) -> bool:
        """Annehmen und Ablehnen: nicht, solange ein Dokumentschutz steht."""
        return self._schutz() is None

    kann_kommentarWeg = kann_kommentarWeiter = kann_kommentarZurueck = _hat_kommentare
    kann_aenderungAnnehmen = kann_aenderungAblehnen = _darf_aendern

    def an_bearbeitungEinschraenken(self) -> bool:
        return self._schutz() is not None

    # ---- Rechtschreibprüfung -----------------------------------------------------------------------------------
    def menue_rechtschreibKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Rechtschreibprüfung …", self.rechtschreibung, symbol=self._sym("rechtschreibpruefung"), kuerzel="F7")
        m.eintrag("Sprache festlegen …", self.pruefsprache, symbol=self._sym("sprache"))
        return m

    # ---- Kommentare --------------------------------------------------------------------------------------------
    def menue_kommentarLoeschenKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        eins = m.eintrag("Kommentar löschen", self.kommentarWeg, symbol=self._sym("kommentarloeschen"))
        alle = m.eintrag("Alle Kommentare im Dokument löschen", self.kommentareAlleWeg, symbol=self._sym("kommentareweg"))
        m.aboutToShow.connect(lambda: (eins.setEnabled(bool(self.ed and self.ed.kommentar_am_cursor() is not None)),
                                       alle.setEnabled(self._hat_kommentare())))
        return m

    # ---- Änderungen nachverfolgen ------------------------------------------------------------------------------
    def menue_verfolgenKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        an = m.eintrag("Änderungen nachverfolgen", lambda: (self.verfolgen(), self.w.band.aktualisieren()),
                       symbol=self._sym("nachverfolgen"), haken=False, tip=VERFOLGEN_TIP)
        m.eintrag("Optionen zum Nachverfolgen von Änderungen …", lambda: self.w.show_options("verfolgen"), symbol=self._sym("verfolgoptionen"))
        m.eintrag("Benutzernamen ändern …", lambda: self.w.show_options("benutzer"), symbol=self._sym("benutzername"))
        m.aboutToShow.connect(lambda: (an.setChecked(self.an_verfolgen()), an.setEnabled(self.ed is not None)))
        return m

    # ---- Anzeige: Endgültige Version / Original ----------------------------------------------------------------
    def _anzeige_index(self) -> int:
        from lunivo_writer.ui.document import vorschau_ansicht
        t = self.w.current_tab()
        if t is not None and vorschau_ansicht.aktiv(t, "original"):
            return 3
        return 0 if (self.ed is None or self.ed.markup) else 1

    def ueberpruefenAnzeige(self, k=None, index: int = 0):
        """Was das Dokumentfenster zeigt: mit oder ohne Markup, oder das Original ohne die verfolgten Änderungen (schreibgeschützt)."""
        from lunivo_writer.editor import fassungen
        from lunivo_writer.ui.document import vorschau_ansicht
        t = self.w.current_tab()
        if t is None:
            return
        if index == 3:
            vorschau_ansicht.zeigen(t, fassungen.original(t.editor.document()), "original")
            return
        if vorschau_ansicht.aktiv(t, "original"):
            vorschau_ansicht.beenden(t)
        t.editor.set_markup(index != 1)

    def feld_anzeige(self):
        """Die Auswahl über „Markup anzeigen“ wie in der Vorlage: die Fassung, darunter das Markup-Menü."""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QStandardItemModel
        from PySide6.QtWidgets import QComboBox, QToolButton, QVBoxLayout, QWidget
        halter = QWidget()
        v = QVBoxLayout(halter); v.setContentsMargins(2, 4, 2, 4); v.setSpacing(4)
        cb = QComboBox(); cb.addItems(list(ANZEIGEN)); cb.setMinimumHeight(36); cb.setMinimumWidth(270)
        cb.setAccessibleName("Anzeige zur Überprüfung"); cb.setToolTip("Anzeige zur Überprüfung")
        modell = cb.model()
        if isinstance(modell, QStandardItemModel):
            it = modell.item(2)
            it.setEnabled(False); it.setToolTip("Lunivo zeigt das Original ohne Markup; mit Markup kommt noch.")
        cb.activated.connect(lambda i: (self.ueberpruefenAnzeige(None, i), self.w.band.aktualisieren()))
        markup = QToolButton(); markup.setAutoRaise(True); markup.setText("Markup anzeigen"); markup.setToolTip("Markup anzeigen")
        markup.setIcon(self._sym("markupzeigen")); markup.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        markup.setPopupMode(QToolButton.InstantPopup); markup.setMinimumHeight(30)
        menue = self.menue_markupKlappe(); menue.setParent(markup, Qt.Popup)        # das Menü gehört dem Knopf (sonst räumt Python es weg)
        markup.setMenu(menue)
        v.addWidget(cb); v.addWidget(markup, 0, Qt.AlignLeft); v.addStretch(1)
        halter.anzeige, halter.markup = cb, markup

        def auffrischen():
            cb.blockSignals(True); cb.setCurrentIndex(self._anzeige_index()); cb.blockSignals(False)
            cb.setEnabled(self.ed is not None); markup.setEnabled(self.ed is not None)
        halter.auffrischen = auffrischen
        auffrischen()
        return halter

    # ---- Markup anzeigen und Überprüfen ------------------------------------------------------------------------
    def _filter_setzen(self, **werte) -> None:
        if self.ed:
            self.ed.markup_filter_setzen(**werte)

    def _bearbeiter_fuellen(self, m) -> None:
        from lunivo_writer.editor import fassungen
        namen = fassungen.bearbeiter(self.ed.document()) if self.ed else []
        m.clear(); m.setEnabled(bool(namen))
        gewaehlt = self.ed.markup_filter["bearbeiter"] if self.ed else None
        m.eintrag("Alle Bearbeiter", lambda: self._filter_setzen(bearbeiter=None), haken=gewaehlt is None)
        m.trenner()
        for n in namen:
            def umschalten(n=n):
                alle = fassungen.bearbeiter(self.ed.document())
                jetzt = set(alle if self.ed.markup_filter["bearbeiter"] is None else self.ed.markup_filter["bearbeiter"])
                jetzt ^= {n}
                self._filter_setzen(bearbeiter=None if jetzt >= set(alle) else jetzt)
            m.eintrag(n, umschalten, haken=gewaehlt is None or n in gewaehlt)

    def _zeiten_fuellen(self, m) -> None:
        from lunivo_writer.editor import fassungen
        tage = fassungen.zeiten(self.ed.document()) if self.ed else []
        m.clear(); m.setEnabled(bool(tage))
        gewaehlt = self.ed.markup_filter["zeit"] if self.ed else None
        m.eintrag("Alle Zeiten", lambda: self._filter_setzen(zeit=None), haken=gewaehlt is None)
        m.trenner()
        for tag in tage:
            m.eintrag(tag, lambda tag=tag: self._filter_setzen(zeit=tag), haken=gewaehlt == tag)

    def menue_markupKlappe(self):
        from lunivo_writer.editor import sprechblasen as SB
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        kom = m.eintrag("Kommentare anzeigen(&C)", lambda: self._filter_setzen(kommentare=not self.ed.markup_filter["kommentare"]), haken=True)
        ein = m.eintrag("Einfügungen und Löschungen anzeigen",
                        lambda: self._filter_setzen(einfuegungen=not self.ed.markup_filter["einfuegungen"]), haken=True)
        form = m.eintrag("Formatierung anzeigen", haken=True, aktiv=False, tip="Formatänderungen verfolgt Lunivo noch nicht.")
        bearb = m.untermenue("Bearbeiter", self._sym("bearbeiter"))
        ballons = m.untermenue("Ballons verwenden", self._sym("sprechblase"))

        def setze_ballons(wert):
            self.w.settings.set("sprechblasen/verwenden", wert)
            self.w.markup_neu()

        def auffrischen():
            da = self.ed is not None
            for a in (kom, ein):
                a.setEnabled(da)
            if da:
                kom.setChecked(self.ed.markup_filter["kommentare"]); ein.setChecked(self.ed.markup_filter["einfuegungen"])
            form.setChecked(True)
            self._bearbeiter_fuellen(bearb)
            ballons.clear()
            jetzt = self.w.settings.get("sprechblasen/verwenden", SB.STANDARD["verwenden"])
            for text, wert in (("Sprechblasen für Überarbeitungen verwenden", "Immer"),
                               ("Alle Überarbeitungen inline anzeigen", "Nie"),
                               ("Nur Kommentare in Sprechblasen anzeigen", "Nur für Kommentare")):
                ballons.eintrag(text, lambda w=wert: setze_ballons(w), haken=jetzt == wert)
        m.aboutToShow.connect(auffrischen)
        return m

    def menue_ueberpruefenKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        bearb = m.untermenue("Bearbeiter", self._sym("bearbeiter"))
        zeit = m.untermenue("Überprüfungszeit", self._sym("pruefzeit"))
        fenster = m.untermenue("Überarbeitungsfenster(&P)", self._sym("ueberpruefenfenster"))
        fenster.eintrag("Vertikales Überarbeitungsfenster", self.ueberarbeitungsbereich, symbol=self._sym("bereich"))
        fenster.eintrag("Horizontales Überarbeitungsfenster", aktiv=False, tip="Das Überarbeitungsfenster steht in Lunivo links.")
        m.aboutToShow.connect(lambda: (self._bearbeiter_fuellen(bearb), self._zeiten_fuellen(zeit)))
        return m

    # ---- Annehmen / Ablehnen -----------------------------------------------------------------------------------
    def _angezeigte(self, annehmen: bool) -> None:
        if self.ed and not self._geschuetzt("aenderungen", "lesen", "kommentare"):
            n = self.ed.angezeigte_aenderungen(annehmen)
            self.w.statusBar().showMessage(f"{n} angezeigte Änderungen {'angenommen' if annehmen else 'abgelehnt'}.", 4000)

    def _entscheiden_menue(self, annehmen: bool):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
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
            frei = self._hat_aenderungen() and self._darf_aendern()
            eins.setEnabled(frei and self.ed.aenderung_am_cursor() is not None)
            f = self.ed.markup_filter if self.ed else {}
            gefiltert = bool(f) and (f["bearbeiter"] is not None or f["zeit"] is not None or not f["einfuegungen"])
            gezeigt.setEnabled(frei and gefiltert and any(self.ed.aenderung_sichtbar(b) for b in self.ed.aenderungen()))
            alle.setEnabled(frei)
        m.aboutToShow.connect(auffrischen)
        return m

    def menue_annehmenKlappe(self): return self._entscheiden_menue(True)

    def menue_ablehnenKlappe(self): return self._entscheiden_menue(False)

    # ---- Vergleichen -------------------------------------------------------------------------------------------
    def menue_vergleichenKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Vergleichen …", self.dokumenteVergleichen, symbol=self._sym("vergleichen"))
        m.eintrag("Zusammenführen …", self.dokumenteZusammenfuehren, symbol=self._sym("zusammenfuehren"))
        quellen = m.untermenue("Quelldokumente anzeigen(&S)", self._sym("kopie"), aktiv=False)
        quellen.eintrag("Quelldokumente ausblenden")
        return m

    # ---- Bearbeitung einschränken ------------------------------------------------------------------------------
    def bearbeitungEinschraenken(self, k=None):
        """Seitenleiste „Bearbeitung einschränken“: Schreibgeschützt, nur nachverfolgte Änderungen oder nur Kommentare."""
        from lunivo_writer.ui.dialogs.ueberpruefen_fenster import SchutzDialog
        t = self.w.current_tab()
        if t is None:
            return
        d = SchutzDialog(self.w, getattr(t, "schutz", None))
        if d.exec():
            self.schutz_setzen(t, d.ergebnis())

    def schutz_setzen(self, t, art: str | None) -> None:
        t.schutz = art
        t.gesperrt = art in ("lesen", "kommentare")       # Kommentare gehen auch im schreibgeschützten Text
        t.editor.setReadOnly(t.gesperrt or self.w.lesemodus)
        if art == "aenderungen":
            t.editor.set_verfolgen(True)
        text = {None: "Dokumentschutz beendet.", "lesen": "Dokument ist schreibgeschützt.",
                "aenderungen": "Alle Änderungen werden nachverfolgt.", "kommentare": "Nur Kommentare sind erlaubt."}[art]
        self.w.statusBar().showMessage(text, 5000)
        self.w.band.aktualisieren()
