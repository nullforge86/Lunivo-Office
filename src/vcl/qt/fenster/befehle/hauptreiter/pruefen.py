"""Befehle: Überprüfen, Schreibhilfe, Vergleichen."""
from __future__ import annotations

import os
from PySide6.QtWidgets import QMessageBox
from writer.funktionen import bearbeiten as _bearbeiten
from writer.anbindung import serienquelle as serienquelle
from writer.ueberpruefung.korrektur.einstellungen import pruefsprache, pruefsprache_setzen
from writer import serienbriefwerkzeuge as sendungen
from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
from vcl.qt.widgets.dialoge.dokument.speichern_fenster import Dateifenster


class PruefenBefehle:
    """Befehle des Bandes: Überprüfen, Schreibhilfe, Vergleichen. Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``)."""


    # ---- Überprüfen / Schreibhilfe --------------------------------------------------------------------------------------------
    def woerterZaehlen(self, k=None):
        """Wörter zählen wie in der Vorlage: Statistiken des Dokuments, auf Wunsch samt Fuß- und Endnoten."""
        if not self.ed:
            return
        from writer.anbindung import statistik as _statistik
        from vcl.qt.widgets.dialoge.ueberpruefen.woerter_dialog import WoerterDialog
        texte = _bearbeiten.texte_des_dokuments(self.ed.kennung)
        noten = [t for art in ("f", "e") for t in self.ed.noten.get(art, {}).values()]
        seiten = self.ed.page_count
        WoerterDialog(self.w, _statistik.zaehlen(texte, seiten), _statistik.zaehlen(texte + noten, seiten)).exec()


    def _jetzt_pruefen(self) -> None:
        """Prüfen (F7): ohne Text eine deutliche Rückmeldung statt einer leeren Seitenleiste."""
        if not self.ed or not self.ed.toPlainText().strip():
            QMessageBox.information(self.w, "Prüfen", "Es steht noch kein Text da, den ich prüfen könnte.")
            return
        self.w.assistant.pruefen(True)


    def rechtschreibung(self, k=None):
        self._jetzt_pruefen()


    def w_pruefen(self, k=None):
        self._jetzt_pruefen()


    def gruendlichPruefen(self, k=None):
        self.w.assistant.gruendlich()


    def wellen(self, k=None):
        """Rote Wellenlinien beim Schreiben an/aus (derselbe Schalter wie „We“ in der Seitenleiste und in „Welche Hilfe wann“)."""
        self.w.assistant.setze("wellen", not self.w.assistant.an("wellen"))


    def an_wellen(self): return self.w.assistant.an("wellen")


    def vorhersage(self, k=None):
        self.w.assistant.setze("vorhersage", not self.w.assistant.an("vorhersage"))


    def an_vorhersage(self): return self.w.assistant.an("vorhersage")


    def autokorrektur(self, k=None):
        self.w.assistant.setze("autokorr", not self.w.assistant.an("autokorr"))


    def an_autokorrektur(self): return self.w.assistant.an("autokorr")


    def tafelZeigen(self, k=None):
        self.w.toggle_sidebar()


    def welcheHilfe(self, k=None):
        self.w.sidebar.welche_hilfe()


    def w_optionenOeffnen(self, k=None, seite=None):
        self.w.show_options(seite) if seite else self.w.show_options()


    # ==== Schreibhilfe: Lesen =====================================================================================================
    def zeilenfokus(self, k=None):
        if self.ed:
            self.ed.set_zeilenfokus(not self.ed.zeilenfokus)


    def an_zeilenfokus(self): return bool(self.ed) and self.ed.zeilenfokus


    def bearbeitungSperren(self, k=None):
        self.w.toggle_sperre()


    def an_bearbeitungSperren(self):
        t = self.w.current_tab()
        return bool(t and getattr(t, "gesperrt", False))


    def lesemodus(self, k=None):
        self.w.toggle_lesemodus()


    def an_lesemodus(self): return self.w.lesemodus


    # ---- Sendungen --------------------------------------------------------------------------------------------
    # ---- Vergleichen und Zusammenführen ---------------------------------------------------------------------------------------
    def _fassung_laden(self, pfad: str):
        """Die Datei als Fassung beim Framework laden; → ihre Nummer (``None``, wenn sie sich nicht lesen lässt)."""
        try:
            return _bearbeiten.fassung_laden(pfad)
        except Exception as e:                                  # unlesbare Datei: melden, nicht abbrechen
            QMessageBox.warning(self.w, "Datei lesen", f"„{os.path.basename(pfad)}“ lässt sich nicht lesen:\n{e}")
            return None


    def _ergebnis_blatt(self, titel: str, ziel, page=None):
        """Öffnet das Ergebnis (``ziel``: Nummer eines Dokuments, das das Framework bereithält) in einem neuen Blatt."""
        t = self._neues_blatt(titel)
        try:
            t.editor.ansicht._befehl(lambda: _bearbeiten.ergebnis_einsetzen(t.editor.kennung, ziel))
        finally:
            _bearbeiten.ergebnis_verwerfen(ziel)
        t.editor.document().setModified(True)
        return t


    def dokumenteVergleichen(self, k=None):
        t = self.w.current_tab()
        if not t:
            return
        pfad, _ = Dateifenster.getOpenFileName(self.w, "Mit welchem Dokument vergleichen?", self.w.settings.get("last_dir", os.path.expanduser("~")),
                                              "Dokumente (*.docx *.odt *.txt *.md);;Alle Dateien (*)")
        if not pfad:
            return
        andere = self._fassung_laden(pfad)
        if andere is None:
            return
        autor = os.path.splitext(os.path.basename(pfad))[0]
        ziel, st = _bearbeiten.dokumente_vergleichen(t.editor.kennung, andere, autor)
        self._ergebnis_blatt(f"Vergleich — {t.title} ↔ {autor}", ziel, t.page)
        self.w.statusBar().showMessage(
            (f"Vergleich fertig: {st['eingefuegt']} Zeichen eingefügt, {st['geloescht']} gelöscht (Überprüfen ▸ Änderungen: annehmen oder ablehnen)."
             if st["operationen"] else "Die beiden Dokumente haben denselben Text."), 9000)


    def dokumenteZusammenfuehren(self, k=None):
        t = self.w.current_tab()
        if not t:
            return
        pfade, _ = Dateifenster.getOpenFileNames(self.w, "Überarbeitete Fassungen auswählen (jede Datei ist ein Autor)",
                                                self.w.settings.get("last_dir", os.path.expanduser("~")),
                                                "Dokumente (*.docx *.odt *.txt *.md);;Alle Dateien (*)")
        fassungen = []
        for p in pfade:
            d = self._fassung_laden(p)
            if d is not None:
                fassungen.append((os.path.splitext(os.path.basename(p))[0], d))
        if not fassungen:
            return
        ziel, st, konflikte = _bearbeiten.dokumente_zusammenfuehren(t.editor.kennung, fassungen)
        self._ergebnis_blatt(f"Zusammenführung — {t.title}", ziel, t.page)
        msg = f"{len(fassungen)} Fassungen zusammengeführt: {st['eingefuegt']} Zeichen eingefügt, {st['geloescht']} gelöscht."
        if konflikte:
            msg += f" {len(konflikte)} Konflikt(e) — die erste Fassung gilt."
            QMessageBox.information(self.w, "Konflikte beim Zusammenführen", "\n".join(konflikte[:30]))
        self.w.statusBar().showMessage(msg, 9000)


    def _neues_blatt(self, titel: str):
        self.w.new_document()
        t = self.w.current_tab()
        t.title = titel
        self.w._update_tab_titles()
        return t


    def umschlag(self, k=None):
        from vcl.qt.widgets.dialoge.sendungen.umschlag_dialog import UmschlagDialog
        b = self.w.benutzerdaten()
        absender = "\n".join(x for x in (b["name"], b["strasse"], b["plz_ort"]) if x)
        d = UmschlagDialog(self.w, absender)
        if d.exec():
            t = self._neues_blatt("Umschlag")
            sendungen.umschlag_aufbauen(t.editor.kennung, d.format.currentText(), d.absender.toPlainText(), d.empfaenger.toPlainText())
            self.w.statusBar().showMessage(f"Umschlag im Format {d.format.currentText()} angelegt.", 5000)


    def etiketten(self, k=None):
        from vcl.qt.widgets.dialoge.sendungen.etiketten_dialog import EtikettenDialog
        d = EtikettenDialog(self.w)
        if d.exec():
            t = self._neues_blatt("Etiketten")
            sendungen.etiketten_aufbauen(t.editor.kennung, d.bogen.currentText(), d.text.toPlainText(), d.gleich.currentIndex() == 0)
            self.w.statusBar().showMessage("Bogen angelegt.", 5000)


    def seriendruckfeld(self, k=None):
        if self.ed:
            from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
            n, ok = EingabeFenster.getText(self.w, "Seriendruckfeld", "Feldname (muss in der Kopfzeile der Empfängerliste stehen):", text="Name")
            if ok and n.strip():
                sendungen.seriendruckfeld_einfuegen(self.ed.kennung, n.strip().replace("{", "").replace("}", ""))


    def adressblock(self, k=None):
        if self.ed:
            namen = {"Adressblock (Name, Straße, Ort)": "adresse", "Grußzeile (Anrede + Name)": "gruss", "Adressblock und Grußzeile": "beides"}
            from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
            n, ok = EingabeFenster.getItem(self.w, "Adressblock und Grußzeile", "Einfügen:", list(namen), 0, False)
            if ok:
                sendungen.adressblock_einfuegen(self.ed.kennung, namen[n])


    def seriendruckregel(self, k=None):
        if self.ed:
            from vcl.qt.widgets.dialoge.sendungen.regel_dialog import RegelDialog
            d = RegelDialog(self.w)
            if d.exec() and d.feld.text().strip():
                sendungen.seriendruckregel_einfuegen(self.ed.kennung, d.feld.text().strip(), d.wert.text().strip(), d.dann.text(), d.sonst.text())


    def seriendruck(self, k=None):
        if not self.ed:
            return
        from vcl.qt.widgets.dialoge.sendungen.seriendruck_dialog import SeriendruckDialog
        d = SeriendruckDialog(self.w, list(sendungen.seriendruckfelder_im_text(self.ed.kennung)), self.w.settings.get("serien/liste", ""))
        if not d.exec():
            return
        tab = serienquelle.tabelle_lesen(d.daten.toPlainText())
        if not tab:
            QMessageBox.information(self.w, "Seriendruck", "Dafür braucht es eine Kopfzeile und mindestens einen Empfänger.")
            return
        self.w.settings.set("serien/liste", d.daten.toPlainText())
        titel = self.w.current_tab().title
        ziel, n = _bearbeiten.serienbrief_erzeugen(self.ed.kennung, tab[1])
        t = self._ergebnis_blatt(titel + " — Seriendruck", ziel)
        self.w.statusBar().showMessage(f"{n} Briefe erzeugt (neues Dokument; die Vorlage bleibt unverändert).", 6000)


    def _form_dialog(self, art: str):
        if not self.ed:
            return
        from vcl.qt.rendering import textfelder as FO
        from vcl.qt.widgets.dialoge.einfuegen.formular_dialog import FormFeldDialog
        d = FormFeldDialog(self.w, art)
        if d.exec():
            m = d.meta()
            FO.formular_einfuegen(self.ed, m)
            if art == "kasten" and m.beschriftung:
                self.ed.textCursor().insertText(" " + m.beschriftung)


    def formTextfeld(self, k=None): self._form_dialog("text")

    def formAuswahl(self, k=None): self._form_dialog("auswahl")


    def tabstopps(self, k=None): self.w.tabstopp_dialog()


    def geheZu(self, k=None, art="Seite"):
        """„Gehe zu“ (Strg+G): der Reiter im Feld „Suchen und ersetzen“ der linken Seitenleiste."""
        if self.ed:
            self.w.find_dialog_show("Gehe zu", art)


    def vollbild(self, k=None): self.w.a_fullscreen.trigger()

    def an_vollbild(self): return self.w.isFullScreen()

    def formDatum(self, k=None): self._form_dialog("datum")

    def formKasten(self, k=None): self._form_dialog("kasten")

    def formKnopf(self, k=None): self._form_dialog("knopf")


    def formLeeren(self, k=None):
        if self.ed:
            from vcl.qt.rendering import textfelder as FO
            n = FO.alle_zuruecksetzen(self.ed)
            self.w.statusBar().showMessage(f"{n} Formularfeld{'er' if n != 1 else ''} zurückgesetzt.", 4000)


    # ---- Überprüfen: Thesaurus, Barrierefreiheit, Korrektursprache ------------------------------------------
    def thesaurus(self, k=None):
        ki = getattr(self.w, "ki", None)
        ed = self.ed
        if ed is None or ki is None:
            return
        try:
            dokument = ed.document()
            revision = dokument.revision()
        except RuntimeError:
            return

        def danach(wort, lst, von, bis):
            # Die Antwort darf nur auf den Editor angewendet werden, von dem
            # aus die Anfrage gestartet wurde – niemals auf den inzwischen aktiven Tab.
            try:
                if (self.w.current_editor() is not ed or ed.document() is not dokument
                        or dokument.revision() != revision):
                    self.w.statusBar().showMessage("Das Dokument wurde gewechselt oder geändert — das Synonym wurde nicht eingesetzt.", 6000)
                    return
            except RuntimeError:
                return
            n, ok = EingabeFenster.getItem(self.w, f"Wörter für „{wort}“", "Statt dessen:", lst, 0, False)
            if ok:
                try:
                    if (self.w.current_editor() is ed and ed.document() is dokument
                            and dokument.revision() == revision):
                        ed.replace_range(von, bis, self._wie_geschrieben(wort, n))
                except RuntimeError:
                    pass
        ki.thesaurus(danach)


    @staticmethod
    def _wie_geschrieben(alt: str, neu: str) -> str:
        return neu[:1].upper() + neu[1:] if alt[:1].isupper() else neu[:1].lower() + neu[1:]


    def barrierefrei(self, k=None):
        if not self.ed:
            return
        from vcl.qt.eingabe.barrierefreiheit import pruefe
        funde = pruefe(self.ed)
        text = ("\n\n".join(f"{i}. {f}" for i, f in enumerate(funde, 1)) if funde else
                "Nichts gefunden. Bilder beschrieben, Überschriften der Reihe nach, Tabellen mit Kopfzeile, Schrift kräftig genug.")
        QMessageBox.information(self.w, "Barrierefreiheit", text)


    SPRACHEN = [("de-DE", "Deutsch"), ("de-AT", "Deutsch (Österreich)"), ("de-CH", "Deutsch (Schweiz)"), ("en-US", "Englisch"),
                ("en-GB", "Englisch (UK)"), ("fr-FR", "Französisch"), ("es-ES", "Spanisch"), ("it-IT", "Italienisch"),
                ("nl-NL", "Niederländisch"), ("pl-PL", "Polnisch"), ("ru-RU", "Russisch"), ("tr-TR", "Türkisch")]


    def pruefsprache(self, k=None):
        self.w_kiSprache()                  # ein Fenster für die Sprache: „KI-Einstellungen → Sprache“ (Prüfsprache und Übersetzungssprache)


    def pruefsprache_aktuell(self) -> str:
        t = self.w.current_tab()
        return (t.meta.get("sprache") if t is not None else "") or pruefsprache(self.w.settings)


    def pruefsprache_setzen(self, kennung: str) -> None:
        """Die Sprache des Dokuments für die Korrekturhilfen (wird in der Datei vermerkt) — vom Band und vom Fenster „KI-Einstellungen“ benutzt."""
        n = dict(self.SPRACHEN).get(kennung, kennung)
        if self.w.current_tab() is not None:
            self.w.current_tab().meta["sprache"] = kennung
            if self.ed:
                self.ed.document().setModified(True)
        pruefsprache_setzen(self.w.settings, kennung)
        self.w.statusBar().showMessage(f"Dokumentsprache: {n}.", 4000)
