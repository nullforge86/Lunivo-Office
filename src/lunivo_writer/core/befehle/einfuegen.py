"""Befehle: Einfügen."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox
from lunivo_writer.core.befehle.hilfen import _farbfeld


class EinfuegenBefehle:
    """Befehle des Bandes: Einfügen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""


    # ---- Einfügen -------------------------------------------------------------------------------------------------
    def seitenumbruch(self, k=None):
        if self.ed: self.ed.insert_page_break()


    def tabelleRaster(self, k=None):
        self.w.insert_table()


    def tabelleZeichnen(self, k=None):
        """Stift: Rechteck aufziehen, die Tabelle kommt dorthin (siehe ``ui/document/tabelle_stift.py``)."""
        if self.ed and not self.ed.isReadOnly():
            from lunivo_writer.ui.document.tabelle_stift import TabellenStift
            TabellenStift(self.ed)


    def bild(self, k=None):
        self.w.insert_image()


    def hyperlink(self, k=None):
        """Fenster „Hyperlink“ (Datei oder Webseite, Aktuelles Dokument, E-Mail-Adresse)."""
        e = self.ed
        if not e:
            return
        import json
        from lunivo_writer.editor import verweise
        from lunivo_writer.ui.dialogs.einfuegen_fenster import HyperlinkDialog
        try:
            adressen = json.loads(str(self.w.settings.get("einfuegen/mail_zuletzt", "") or "[]"))
        except ValueError:
            adressen = []
        markiert = e.textCursor().selectedText().replace("\u2029", " ").strip()
        d = HyperlinkDialog(self.w, text=markiert, ziele=verweise.querverweis_ziele(e), ordner=self.w.settings.get("last_dir", ""),
                            adressen=[a for a in adressen if isinstance(a, str)])
        if not d.exec():
            return
        r = d.ergebnis()
        if r["art"] == "dokument":
            href = "#" + verweise.marke_sichern(e, r["ziel"])
        else:
            href = r["href"]
        if r["art"] == "mail":
            liste = [r["adresse"]] + [a for a in adressen if a != r["adresse"]]
            self.w.settings.set("einfuegen/mail_zuletzt", json.dumps(liste[:10], ensure_ascii=False))
        c = e.textCursor()
        if c.hasSelection() and r["text"] != markiert:
            c.removeSelectedText(); e.setTextCursor(c)
        e.insert_link(href, r["text"], r["tipp"])
        e.document().setModified(True)


    def objekt(self, k=None, als_symbol=False):
        """Fenster „Objekt einfügen“: Inhalt einer Datei (Text, Bild) oder ein Dateisymbol mit Link."""
        e = self.ed
        if not e:
            return
        from lunivo_writer.ui.dialogs.einfuegen_fenster import ObjektDialog
        d = ObjektDialog(self.w, als_symbol=bool(als_symbol), ordner=self.w.settings.get("last_dir", ""))
        if not d.exec():
            return
        self._datei_einsetzen(d.datei.text().strip(), d.art())


    def _datei_einsetzen(self, pfad: str, art: str) -> None:
        """Bild ins Dokument, Text (DOCX, ODT, RTF, TXT, MD) mit seinem Inhalt, alles andere als Dateisymbol mit Link."""
        import os
        e = self.ed
        if art == "bild" and e.insert_image(pfad):
            return
        if art == "text":
            from lunivo_writer.editor import einfuegen as E
            from lunivo_writer.models.report import DocumentIOError
            try:
                self.w._show_report(E.text_aus_datei(e, pfad), "Hinweise zum eingefügten Objekt", "beim Einfügen")
                return
            except DocumentIOError:
                pass                                            # nicht lesbar: dann als Symbol
        from PySide6.QtCore import QFileInfo, QUrl
        from PySide6.QtWidgets import QFileIconProvider
        from lunivo_writer.editor import einfuegen as E
        symbol = QFileIconProvider().icon(QFileInfo(pfad)).pixmap(48, 48).toImage()
        self._bild_einfuegen(E.datei_symbol_bild(os.path.basename(pfad), symbol), f"Datei: {os.path.basename(pfad)}")
        c = e.textCursor(); c.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
        f = c.charFormat(); f.setAnchor(True); f.setAnchorHref(QUrl.fromLocalFile(pfad).toString()); f.setToolTip(pfad)
        c.mergeCharFormat(f)


    # Dateitypen im Fenster „Dateiobjekt einfügen“ (wie die Reiter ALL / WPS / ET / WPP / PDF der Vorlage)
    DATEIOBJEKT_TYPEN = [("Alle Dateien", "*"), ("Dokumente", "*.docx *.doc *.odt *.rtf *.txt *.md"),
                         ("Tabellen", "*.xlsx *.xls *.ods *.csv"), ("Präsentationen", "*.pptx *.ppt *.odp"), ("PDF", "*.pdf"),
                         ("Bilder", "*.png *.jpg *.jpeg *.gif *.bmp *.webp *.svg")]

    def dateiObjekt(self, k=None):
        """„Datei-Objekt“ wie in WPS: gleich das Fenster „Dateiobjekt einfügen“ (Lunivos Dateifenster); die gewählte Datei kommt
        ins Dokument — Text und Bilder mit Inhalt, andere Dateien als Symbol mit Link."""
        if not self.ed:
            return
        import os
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_waehlen
        filter_text = ";;".join(f"{n} ({m})" for n, m in self.DATEIOBJEKT_TYPEN)
        gewaehlt = datei_waehlen(self.w, "Dateiobjekt einfügen", self.w.settings.get("last_dir", ""), filter_text)
        if not gewaehlt:
            return
        pfad = gewaehlt[0]
        endung = os.path.splitext(pfad)[1].lower()
        art = ("bild" if endung in (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg")
               else "text" if endung in (".docx", ".odt", ".rtf", ".txt", ".md") else "symbol")
        self._datei_einsetzen(pfad, art)


    def menue_objektKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Objekt …", self.objekt, symbol=self._sym("objekte"))
        m.eintrag("Text aus Datei …", self.textAusDatei, symbol=self._sym("ausdatei"))
        return m


    def kopfFussZeigen(self, k=None):
        self.w.edit_header_footer(True)


    def menue_seitenzahlKlappe(self):
        """Seitenzahl wie in WPS: zehn Vorgaben (Kopf-/Fußzeile links, Mitte, rechts, außen, innen), darunter Einfügen … und Entfernen.
        „außen“ und „innen“ wechseln die Seite zwischen geraden und ungeraden Seiten."""
        from PySide6.QtCore import QSize
        from lunivo_writer.editor import seitenzahl as SZ
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        from lunivo_writer.ui.baukasten.seiten_bildchen import seitenzahl_zeichner
        m = RasterAuswahl(self.w, titel="Vorgaben", spalten=5, groesse=QSize(92, 96), beschriftet=True)
        for schl, text, ort, ausr in SZ.VORGABEN:
            m.kachel(schl, text, seitenzahl_zeichner(ort, ausr)).setCheckable(False)
        m.gewaehlt.connect(lambda schl: self._seitenzahl_vorgabe(schl))
        m.fuss("Seitenzahl einfügen …", self.seitenzahlEinfuegen)
        m.fuss("Seitenzahlen entfernen", self.seitenzahlenEntfernen)
        return m


    def _seitenzahl_vorgabe(self, schl: str) -> None:
        from lunivo_writer.editor import seitenzahl as SZ
        _s, _t, ort, ausr = next(v for v in SZ.VORGABEN if v[0] == schl)
        if self.ed:
            self.ed.page_settings_changed(SZ.seitenzahl_setzen(self.ed.abschnitt_seite(), ort, ausr))


    def seitenzahlEinfuegen(self, k=None):
        """Fenster „Seitenzahl einfügen“; „Übernehmen für“ entscheidet, welche Abschnitte es trifft. „Von aktueller Seite“ beginnt am
        Anfang der Seite mit der Schreibmarke einen neuen Abschnitt (wie in WPS)."""
        if not self.ed:
            return
        from lunivo_writer.editor import abschnitte as AB
        from lunivo_writer.editor import seitenzahl as SZ
        from lunivo_writer.ui.dialogs.einfuegen_fenster import SeitenzahlDialog
        ed = self.ed
        d = SeitenzahlDialog(self.w, ed.abschnitt_seite())
        if not d.exec():
            return
        w = d.werte()
        doc = ed.document()
        if w["bereich"] == "dokument":
            ziele = list(range(AB.anzahl(doc)))
        elif w["bereich"] == "seite":
            pos = ed.textCursor().position()
            anfang = max([AB.beginn(doc, ed.abschnitt_nr())] + [s for s in ed.seitenwechsel if s <= pos])
            ziele = [AB.einfuegen_an(doc, anfang, "naechste", ed.page)]
        else:
            ziele = [ed.abschnitt_nr()]
        for i, nr in enumerate(ziele):
            ps = SZ.seitenzahl_setzen(ed.abschnitt_seite(nr), w["ort"], w["ausrichtung"], w["muster"], w["format"],
                                      w["start"] if i == 0 else 0, w["kapitel"])
            if nr == 0:
                ed.apply_page(ps)
            else:
                AB.setzen(doc, nr, ps)
        ed._recount()
        doc.setModified(True)


    def seitenzahlenEntfernen(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import seitenzahl as SZ
        page = self.ed.abschnitt_seite()
        if SZ.seitenzahlen_entfernen(page):
            self.ed.page_settings_changed(page)
        else:
            self.w.statusBar().showMessage("In Kopf- und Fußzeile steht keine Seitenzahl.", 4000)


    # ---- Wasserzeichen-Galerie --------------------------------------------------------------------------------------------
    WASSERZEICHEN_VORGABEN = (("VERTRAULICH", -45), ("NICHT KOPIEREN", -45), ("ORIGINAL", 0), ("BEISPIEL", 0), ("STRENG GEHEIM", -45),
                              ("EILT", 0))
    EIGENE_WASSERZEICHEN = "einfuegen/wasserzeichen_eigene"
    EIGENE_ANZAHL = 6


    def _eigene_wasserzeichen(self) -> list[dict]:
        """Eigene Wasserzeichen (Text oder Bild) aus den Einstellungen."""
        import json
        try:
            d = json.loads(str(self.w.settings.get(self.EIGENE_WASSERZEICHEN, "") or "[]"))
        except ValueError:
            return []
        return [x for x in d if isinstance(x, dict) and (x.get("text") or x.get("bild"))] if isinstance(d, list) else []


    def menue_wasserzeichenKlappe(self):
        """Wasserzeichen wie in WPS: „Benutzerdefiniert“ (eigene + Hinzufügen), „Voreinstellung“, darunter Einfügen … und Entfernen."""
        import json
        from PySide6.QtCore import QSize
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        from lunivo_writer.ui.baukasten.seiten_bildchen import plus_zeichner, wasserzeichen_vorschau, wasserzeichen_zeichner
        m = RasterAuswahl(self.w, titel="Benutzerdefiniertes Wasserzeichen", spalten=3, groesse=QSize(84, 112), beschriftet=True)
        for i in range(self.EIGENE_ANZAHL):
            m.kachel(f"eigen{i}")
        m.kachel("neu", "Hinzufügen", plus_zeichner())
        m.abschnitt("Voreinstellung")
        for text, winkel in self.WASSERZEICHEN_VORGABEN:
            m.kachel(text, text, wasserzeichen_zeichner(text, winkel))
        for b in m.knoepfe.values():
            b.setCheckable(False)
        m.fuss("Wasserzeichen einfügen …", self.wasserzeichen)
        m.fuss("Wasserzeichen entfernen", lambda: self._wasserzeichen_setzen(None))

        def auffrischen():
            eigene = self._eigene_wasserzeichen()
            for i in range(self.EIGENE_ANZAHL):
                b = m.knoepfe[f"eigen{i}"]
                b.setVisible(i < len(eigene))
                if i < len(eigene):
                    w = eigene[i]
                    name = w.get("text") or w.get("bild_name") or "Bild"
                    m.bild_setzen(f"eigen{i}", wasserzeichen_vorschau(w), name)
                    b.setText(b.fontMetrics().elidedText(name, Qt.ElideRight, 88))

        def gewaehlt(schl: str):
            if schl == "neu":
                from lunivo_writer.ui.dialogs.wasserzeichen_fenster import WasserzeichenDialog
                d = WasserzeichenDialog(self.w, {"text": "VERTRAULICH", "winkel": -45, "transparenz": 50},
                                        self.ed.abschnitt_seite() if self.ed else None, str(self.w.settings.get("last_dir", "") or ""))
                if d.exec() and d.ergebnis():
                    neu = {k: v for k, v in d.ergebnis().items() if k != "abschnitt"}
                    eigene = [neu] + self._eigene_wasserzeichen()
                    self.w.settings.set(self.EIGENE_WASSERZEICHEN, json.dumps(eigene[:self.EIGENE_ANZAHL], ensure_ascii=False))
                    self._wasserzeichen_setzen(neu, d.bereich())
            elif schl.startswith("eigen"):
                eigene = self._eigene_wasserzeichen()
                i = int(schl[5:])
                if i < len(eigene):
                    self._wasserzeichen_setzen(dict(eigene[i]))
            else:
                winkel = dict(self.WASSERZEICHEN_VORGABEN)[schl]
                self._wasserzeichen_setzen({"text": schl, "farbe": "#c0c0c0", "winkel": winkel, "groesse_pt": 0, "transparenz": 50})
        m.aboutToShow.connect(auffrischen)
        m.gewaehlt.connect(gewaehlt)
        auffrischen()
        return m


    def seitenzahlKlappe(self, k=None):
        self.w.insert_page_number()


    # ==== Einfügen ===========================================================================================================
    def leereSeite(self, k=None, quer=None):
        """Leere Seite: ein neues Blatt hinter der Seite der Schreibmarke (Vertikal/Horizontal; ohne Angabe wie die Seite davor).
        Der Text wird nicht geteilt; ein Blatt in anderer Ausrichtung steht in einem eigenen Abschnitt."""
        from lunivo_writer.editor.leere_seite import leere_seite
        e = self.ed
        if not e:
            return
        c = leere_seite(e.document(), e.seite_letzter_block(), e.abschnitt_seite(), quer)
        e.setTextCursor(c)
        e.document().setModified(True)
        e._recount()
        e.ensureCursorVisible()


    def sonderzeichen(self, k=None):
        """Fenster „Symbol“ (Weitere Symbole …) in der Seitenleiste; „Einfügen“ setzt das Zeichen an die Schreibmarke."""
        from lunivo_writer.ui.dialogs.sonderzeichen import SonderzeichenDialog
        e = self.ed
        if e:
            SonderzeichenDialog(self.w, e.insertPlainText, self._symbol_daten(), bei_tasten=self.symbol_tasten_anwenden).exec()


    def _symbol_daten(self):
        """Die eine Datenbasis von Klappe und Fenster „Symbol“: zuletzt verwendet, benutzerdefinierte Liste, Tastenkombinationen."""
        from lunivo_writer.ui.dialogs.sonderzeichen import SymbolDaten
        return SymbolDaten(self.w.settings, self.BENUTZER_SYMBOLE, self.ZULETZT_ANZAHL)


    def symbol_tasten_anwenden(self) -> None:
        """Tastenkombinationen der benutzerdefinierten Symbole als Kürzel des Hauptfensters setzen (alte werden ersetzt)."""
        from PySide6.QtGui import QKeySequence, QShortcut
        for sc in getattr(self, "_symbol_kuerzel", []):
            sc.setEnabled(False); sc.deleteLater()
        self._symbol_kuerzel = []
        daten = self._symbol_daten()
        sichtbar = set(daten.sichtbar())
        for z, t in daten.tasten().items():
            if z in sichtbar and t:
                sc = QShortcut(QKeySequence(t), self.w)
                sc.activated.connect(lambda z=z: self._symbol_einfuegen(z))
                self._symbol_kuerzel.append(sc)


    # ---- Klappmenüs nach den WPS-Vorlagen (Ordner einfuegen/) ------------------------------------------------------------
    BENUTZER_SYMBOLE = ("—", "+", "-", "×", "÷", "kg", "mm", "cm", "m²", "α", "g", "β", "θ", "℃", "〖", "{", "©", "®", "@", "&", "*", "#",
                        "%", "‰", "$", "¥", "§", "¦", "※", "◎", "≈", "…", "≤", "≥", "≦", "≧")
    ZULETZT_SYMBOLE = "einfuegen/symbole_zuletzt"
    ZULETZT_ANZAHL = 24


    @staticmethod
    def _sym(name):
        from lunivo_writer.ui.widgets import icons
        return icons.icon(name, 18)


    def menue_umbruecheKlappe(self):
        """Umbrüche wie in WPS: Seite, Spalte, Textfluss, dann die vier Abschnittsumbrüche."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Seitenumbruch(&P)", self.seitenumbruch, symbol=self._sym("umbruch"), kuerzel="Strg+Enter")
        m.eintrag("Spaltenumbr&uch", self.spaltenumbruch, symbol=self._sym("spaltenumbruch"))
        m.eintrag("Textflussumbruch(&W)", self.textflussumbruch, symbol=self._sym("textflussumbruch"), kuerzel="Umschalt+Enter")
        m.trenner()
        for art, text, sym in (("NextPage", "Abschnittsumbruch von &nächster Seite", "abschnitt"),
                               ("Continuous", "Fortlaufenden Abschni&ttsumbruch", "abschnittlaufend"),
                               ("EvenPage", "Abschnittsumbruch von &gerader Seite", "abschnittgerade"),
                               ("OddPage", "Abschnittsumbruch v&on ungerader Seite", "abschnittungerade")):
            m.eintrag(text, lambda a=art: self.abschnittsumbruch(None, a), symbol=self._sym(sym))
        return m


    def menue_leereSeiteKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("&Vertikal", lambda: self.leereSeite(None, False), symbol=self._sym("leereseite"))
        m.eintrag("&Horizontal", lambda: self.leereSeite(None, True), symbol=self._sym("querformat"))
        return m


    def menue_tabelleKlappe(self):
        """Tabelle wie in WPS: 10 × 10 Zellen (fügt an der Schreibmarke ein), darunter Einfügen, Zeichnen, Text ↔ Tabelle;
        was nicht passt, bleibt grau."""
        from lunivo_writer.ui.baukasten.zellen_raster import ZellenRaster
        m = ZellenRaster(self.w, 10, 10)
        m.gewaehlt.connect(lambda z, s: self.ed and self.ed.insert_table(z, s))
        m.addSeparator()
        m.addAction(self._sym("tabelle"), "Tabelle e&infügen", self.tabelleRaster)
        m.addAction(self._sym("tabelleZeichnen"), "Tabelle zeichnen(&W)", self.tabelleZeichnen)
        zu_tab = m.addAction(self._sym("tabelleWahl"), "Text in Tabelle umwandeln...", self.textInTabelle)
        zu_text = m.addAction(self._sym("schnelltab"), "Tabelle in Text konvertieren...", self.tabelleInText)

        def zustand():
            c = self.ed.textCursor() if self.ed else None
            zu_tab.setEnabled(bool(c and c.hasSelection() and c.currentTable() is None))
            zu_text.setEnabled(bool(c and c.currentTable() is not None))
        m.aboutToShow.connect(zustand)
        return m


    def menue_bildKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Bild aus Datei einfügen …", self.bild, symbol=self._sym("bild"))
        m.eintrag("Bildschirmfoto …", self.screenshot, symbol=self._sym("bildfoto"))
        m.eintrag("Piktogramm …", self.piktogramm, symbol=self._sym("piktogramm"))
        return m


    def menue_textfeldKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Horizontal", self.textfeld, symbol=self._sym("textrahmen"))
        m.eintrag("Vertikal", self.textfeldVertikal, symbol=self._sym("textrichtung"))
        m.eintrag("Mehrzeiliger Text", self.textfeldMehrzeilig, symbol=self._sym("block"))
        return m


    def textfeldVertikal(self, k=None):
        """Textfeld mit senkrecht laufendem Text: eine Form (weiß, dunkler Rahmen); Text, Füllung und Kontur über die Formwerkzeuge."""
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            daten = {"form": E.TEXTFELD_VERTIKAL, "fuell": "#ffffff", "linie": "#1f3864", "strich": 1.5, "text": "Text hier eingeben"}
            self._bild_einfuegen(E.form_bild(E.TEXTFELD_VERTIKAL, 70, 180, "#ffffff", "#1f3864", 1.5, daten["text"]),
                                 "Textfeld (vertikal)", "form", daten)


    def textfeldMehrzeilig(self, k=None):
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            E.textfeld(self.ed, "Text hier eingeben\n\n", breite=100)


    def menue_schnellbausteineKlappe(self):
        """Schnellbausteine wie in WPS: AutoText-Liste ▸ und Felder …"""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        liste = m.untermenue("AutoText-Liste", self._sym("baustein"))
        liste.aboutToShow.connect(lambda: (liste.clear(), self._bausteine_fuellen(liste)))
        m.eintrag("Felder …", self.felder, symbol=self._sym("feld"))
        return m


    # Seitenzahl-AutoTexte der Vorlage: (Name, [Text oder (Feldanweisung)])
    AUTOTEXTE_SEITE = [("- Seite -", ["- ", ("PAGE",), " -"]), ("Seite X", ["Seite ", ("PAGE",)]),
                       ("Gesamtmenge von Y Seite", ["Gesamt ", ("NUMPAGES",), " Seiten"]),
                       ("Seite X von Y", ["Seite ", ("PAGE",), " von ", ("NUMPAGES",)])]

    def _bausteine_fuellen(self, m) -> None:
        """AutoText-Liste wie in der Vorlage: die vier Seitenzahl-Texte, dann die eigenen und mitgelieferten Bausteine, zuletzt
        „AutoText hinzufügen …“ (nur mit Markierung)."""
        from lunivo_writer.services import bausteine
        for name, teile in self.AUTOTEXTE_SEITE:
            m.addAction(name, lambda _=False, teile=teile: self._autotext_seite(teile))
        for titel, liste in (("Eigene", bausteine.laden()), ("Standard", bausteine.standard())):
            if not liste:
                continue
            m.addSection(titel)
            for b in liste:
                m.addAction(b["name"] + (f"   [{b['kuerzel']}]" if b.get("kuerzel") else ""),
                            lambda _=False, b=b: self.ed and (bausteine.einfuegen(self.ed.textCursor(), b), self.ed.document().setModified(True)))
        m.addSeparator()
        neu = m.addAction(self._sym("baustein"), "AutoText hinzufügen …", self.autotextHinzufuegen)
        neu.setEnabled(bool(self.ed and self.ed.textCursor().hasSelection()))
        m.addAction("Textbausteine verwalten …", self.textbaustein)


    def _autotext_seite(self, teile) -> None:
        if not self.ed:
            return
        from lunivo_writer.editor import felder as F
        kontext = F.kontext_sammeln(self.ed)
        c = self.ed.textCursor(); c.beginEditBlock()
        for t in teile:
            if isinstance(t, tuple):
                F.feld_einfuegen(self.ed, t[0], F.ergebnis(t[0], kontext))
            else:
                self.ed.textCursor().insertText(t)
        c.endEditBlock()
        self.ed.document().setModified(True)


    def autotextHinzufuegen(self, k=None):
        """Die Markierung als AutoText (Textbaustein) speichern; der Name kommt aus dem Fenster „AutoText erstellen“."""
        if not self.ed or not self.ed.textCursor().hasSelection():
            return
        from lunivo_writer.services import bausteine
        from lunivo_writer.ui.dialogs.einfuegen_fenster import AutoTextDialog
        c = self.ed.textCursor()
        d = AutoTextDialog(self.w, c.selectedText().replace("\u2029", " "))
        if d.exec() and d.name():
            bausteine.hinzufuegen(d.name(), c.selection())
            self.w.statusBar().showMessage(f"AutoText „{d.name()}“ gespeichert.", 4000)


    def schnellbausteine(self, k=None):
        self._popup(self.menue_schnellbausteineKlappe())


    def felder(self, k=None):
        """Fenster „Felder“ (Schnellbausteine ▸ Felder …). TOC fügt ein echtes Inhaltsverzeichnis ein, TC einen ausgeblendeten
        Eintrag; alle anderen Felder stehen mit Ergebnis und Feldanweisung im Text."""
        if not self.ed:
            return
        import re
        from lunivo_writer.editor import felder as F
        from lunivo_writer.ui.dialogs.einfuegen_fenster import FelderDialog
        t = self.w.current_tab()
        kontext = F.kontext_sammeln(self.ed, self.w.settings.get("benutzer/name", ""), getattr(t, "path", "") or "")
        kontext["serienfelder"] = list((getattr(t, "serie", None) or {}).get("spalten", []))
        d = FelderDialog(self.w, kontext)
        if not d.exec():
            return
        anweisung, text = d.feld()
        if anweisung.upper().startswith("TOC"):
            from lunivo_writer.editor import verzeichnis as V
            m = re.search(r'\\o\s*"(\d)-(\d)"', anweisung)
            V.verzeichnis_einfuegen(self.ed, "toc", dict(V.TOC_VORGABE, ebenen=int(m.group(2)) if m else 3))
            return
        F.feld_einfuegen(self.ed, anweisung, text, versteckt=anweisung.upper().startswith("TC"))


    def menue_symbolKlappe(self):
        """Symbol wie in WPS: zuletzt verwendete und benutzerdefinierte Symbole als Kacheln, darunter „Weitere Symbole …“.
        Die zuletzt verwendeten werden bei jedem Aufklappen neu gesetzt (das Menü entsteht nur einmal)."""
        from PySide6.QtCore import QSize
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, textkachel
        m = RasterAuswahl(self.w, titel="Aktuell verwendete Symbole:", spalten=12, groesse=QSize(24, 24))
        for i in range(self.ZULETZT_ANZAHL):
            m.kachel(f"zuletzt{i}")
        m.abschnitt("Benutzerdefinierte Symbole:")
        m.kacheln([(z, f"„{z}“ einfügen", textkachel(z)) for z in self._symbol_daten().sichtbar()])
        m.fuss("Weitere Symbole …", self.sonderzeichen)
        for b in m.knoepfe.values():
            b.setCheckable(False)
        if not hasattr(self, "_symbol_kuerzel"):
            self.symbol_tasten_anwenden()                        # Tastenkombinationen der Symbole gelten ab dem ersten Öffnen der Klappe
        belegt: dict[str, str] = {}

        def auffrischen():
            zuletzt = self._symbole_zuletzt()
            belegt.clear()
            for i in range(self.ZULETZT_ANZAHL):
                schl = f"zuletzt{i}"
                z = zuletzt[i] if i < len(zuletzt) else ""
                m.knoepfe[schl].setVisible(bool(z))
                if z:
                    belegt[schl] = z
                    m.bild_setzen(schl, textkachel(z), f"„{z}“ einfügen")
        m.aboutToShow.connect(auffrischen)
        m.gewaehlt.connect(lambda schl: self._symbol_einfuegen(belegt.get(schl, schl)))
        auffrischen()
        return m


    def _symbole_zuletzt(self) -> list[str]:
        return self._symbol_daten().zuletzt()


    def _symbol_merken(self, z: str) -> None:
        self._symbol_daten().merken(z)


    def _symbol_einfuegen(self, z: str) -> None:
        if self.ed:
            self.ed.insertPlainText(z)
            self._symbol_merken(z)


    def symbol(self, k=None):
        self._popup(self.menue_symbolKlappe())


    def zahl(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.ui.dialogs.einfuegen_fenster import ZahlDialog
        d = ZahlDialog(self.w)
        if d.exec():
            self.ed.insertPlainText(d.ergebnis())


    def textInTabelle(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import tabelle_text as TT
        from lunivo_writer.ui.dialogs.einfuegen_fenster import TrennerDialog
        texte = TT.markierte_absaetze(self.ed)
        if not texte:
            self.w.statusBar().showMessage("Bitte zuerst den Text markieren, der eine Tabelle werden soll.", 5000)
            return
        d = TrennerDialog(self.w, zu_tabelle=True, texte=texte)
        if d.exec():
            TT.text_zu_tabelle(self.ed, d.trenner(), d.spalten())


    def tabelleInText(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import tabelle_text as TT
        from lunivo_writer.ui.dialogs.einfuegen_fenster import TrennerDialog
        if self.ed.textCursor().currentTable() is None:
            self.w.statusBar().showMessage("Die Schreibmarke steht in keiner Tabelle.", 5000)
            return
        d = TrennerDialog(self.w, zu_tabelle=False)
        if d.exec():
            TT.tabelle_zu_text(self.ed, d.trenner(), d.geschachtelt.isChecked())


    def inhaltsverzeichnis(self, k=None):
        """Fenster „Inhaltsverzeichnis“ (Füllzeichen, Ebenen, Seitenzahlen, Verknüpfungen); OK fügt es ein oder schreibt das
        vorhandene mit den neuen Einstellungen neu."""
        if not self.ed:
            return
        from lunivo_writer.editor import verzeichnis as V
        from lunivo_writer.ui.dialogs.verweise_fenster import InhaltsverzeichnisDialog
        d = InhaltsverzeichnisDialog(self.w, V.toc_optionen(self.ed.document()) or V.TOC_VORGABE)
        if d.exec() and not V.verzeichnis_einfuegen(self.ed, "toc", d.ergebnis()):
            self.w.statusBar().showMessage("Im Dokument gibt es keine Überschriften. Legen Sie sie mit Verweise ▸ Inhaltsverzeichnis "
                                           "(Ebene 1–9) oder den Formatvorlagen „Überschrift 1–9“ fest.", 6000)


    def verzeichnisseAktualisieren(self, k=None):
        if self.ed:
            from lunivo_writer.editor.verzeichnis import verzeichnis_aktualisieren
            verzeichnis_aktualisieren(self.ed)


    # ---- Einfügen: Illustrationen, Text, Symbole, Tabellen, Seiten ----------------------------------------------------
    def _bild_einfuegen(self, img, alt, art=None, daten=None):
        from lunivo_writer.editor import einfuegen as E
        E.qimage_einfuegen(self.ed, img, alt, art, daten)


    def formenGalerie(self, k=None):
        if self.ed:
            self._popup(self.menue_formenKlappe())


    def menue_formenKlappe(self):
        """Formen wie in WPS: Gruppen (Linie, Rechteck, Standardformen, Blockpfeile, …) mit kleinen Umrissbildern."""
        from PySide6.QtCore import QRectF, QSize
        from PySide6.QtGui import QColor, QPen
        from lunivo_writer.core.farben import Farbe
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.editor import formen_katalog as K
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = None
        for gruppe, formen in K.KATEGORIEN:
            if m is None:
                m = RasterAuswahl(self.w, titel=gruppe, spalten=16, groesse=QSize(22, 22))
            else:
                m.abschnitt(gruppe)
            for name in formen:
                def zeichne(p, r, name=name):
                    p.setPen(QPen(QColor(Farbe.AKZENT), 1.3)); p.setBrush(Qt.NoBrush)
                    p.drawPath(K.pfad(name, QRectF(r).adjusted(2, 3, -2, -3)))
                m.kachel(name, name, zeichne).setCheckable(False)

        def einfuegen(f):
            from lunivo_writer.editor import formen as F
            if self.ed and not F.in_zeichenbereich(self.ed, f):
                self._bild_einfuegen(E.form_bild(f, *((240, 60) if K.ist_linie(f) else (160, 120))), f"Form: {f}", "form", {"form": f})
        m.gewaehlt.connect(einfuegen)
        m.fuss("Weitere Formen und Farben …", self.zeichnen)
        m.trenner()
        bereich = m.fuss("Neuer &Zeichenbereich", self.zeichenbereich)
        bereich.setIcon(self._sym("textrahmen"))
        bereich.setToolTip("Fügt einen Bereich ein, der Formen aufnimmt: Bereich markieren, dann eine Form wählen.")
        return m


    def zeichenbereich(self, k=None):
        """Einfügen ▸ Formen ▸ Neuer Zeichenbereich (siehe ``editor/formen.py``)."""
        if self.ed and not self.ed.isReadOnly():
            from lunivo_writer.editor import formen as F
            F.zeichenbereich_einfuegen(self.ed)
            c = self.ed.textCursor(); c.movePosition(c.MoveOperation.PreviousCharacter, c.MoveMode.KeepAnchor); self.ed.setTextCursor(c)


    def zeichnen(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import FormDialog
            d = FormDialog(self.w)
            if d.exec():
                self._bild_einfuegen(d.bild(), f"Form: {d.art.currentText()}", "form", d.daten())


    def smartart(self, k=None):
        if self.ed:
            from lunivo_writer.editor import smartart as SA
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import SmartArtDialog
            d = SmartArtDialog(self.w)
            if d.exec():
                SA.einfuegen(self.ed, d.daten())


    def smartartText(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import smartart as SA
        from lunivo_writer.ui.dialogs.einfuegen_dialoge import SmartArtDialog
        daten = SA.daten_der_auswahl(self.ed)
        if daten is None:
            self.w.statusBar().showMessage("Bitte zuerst ein SmartArt-Bild auswählen (Schreibmarke davor oder Bild markieren).", 5000)
            return
        d = SmartArtDialog(self.w, daten)
        if d.exec():
            SA.aendern(self.ed, **d.daten())


    def menue_smartartLayout(self):
        from lunivo_writer.editor import smartart as SA
        m = QMenu()
        for n in SA.LAYOUTS:
            m.addAction(n, lambda _=False, n=n: self.ed and SA.aendern(self.ed, layout=n))
        return m


    def menue_smartartFarben(self):
        from lunivo_writer.editor import smartart as SA
        m = QMenu()
        for n, f in SA.FARBEN.items():
            m.addAction(_farbfeld(f[0]), n, lambda _=False, n=n: self.ed and SA.aendern(self.ed, farben=n))
        return m


    def wordart(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import WordArtDialog
            d = WordArtDialog(self.w)
            if d.exec():
                self._bild_einfuegen(d.bild(), "WordArt: " + d.text.text(), "wordart", {"text": d.text.text()})


    def wordartVorgabe(self, k=None, nr=0):
        """WordArt aus der Galerie: das Fenster öffnet mit Stil und Farbe der Vorlage (und dem markierten Text)."""
        if not self.ed:
            return
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.dialogs.einfuegen_dialoge import WordArtDialog
        _n, stil, farbe = E.WORDART_VORGABEN[nr]
        markiert = self.ed.textCursor().selectedText().replace("\u2029", " ").strip()
        d = WordArtDialog(self.w, markiert, stil, farbe)
        if d.exec():
            self._bild_einfuegen(d.bild(), "WordArt: " + d.text.text(), "wordart", {"text": d.text.text()})


    def menue_wordartKlappe(self):
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QPixmap
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, titel="Formatvorlage", spalten=6, groesse=QSize(44, 44))
        for i, (name, stil, farbe) in enumerate(E.WORDART_VORGABEN):
            img = E.wordart_bild("A", stil, pt=110, farbe=farbe)
            b = m.kachel(str(i), name, QPixmap.fromImage(img).scaled(44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            b.setCheckable(False)
        m.gewaehlt.connect(lambda schl: self.wordartVorgabe(None, int(schl)))
        return m


    def menue_gleichungKlappe(self):
        """Gleichung wie in WPS: eingebaute Gleichungen als große Kacheln mit Namen, darunter „Neue Gleichung einfügen …“."""
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QPainter, QPixmap
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        groesse = QSize(380, 54)
        m = RasterAuswahl(self.w, titel="Integriert", spalten=1, groesse=groesse, beschriftet=True)
        for i, (name, formel) in enumerate(E.GLEICHUNGEN):
            img = E.formel_bild(formel, 13)
            pm = QPixmap(groesse); pm.fill(Qt.white)
            p = QPainter(pm); p.setPen(Qt.lightGray); p.drawRect(0, 0, groesse.width() - 1, groesse.height() - 1)
            bild = img.scaled(groesse.width() - 12, groesse.height() - 8, Qt.KeepAspectRatio, Qt.SmoothTransformation) \
                if img.width() > groesse.width() - 12 or img.height() > groesse.height() - 8 else img
            p.drawImage((groesse.width() - bild.width()) // 2, (groesse.height() - bild.height()) // 2, bild); p.end()
            b = m.kachel(str(i), name, pm)
            b.setCheckable(False)
        m.gewaehlt.connect(lambda schl: self.ed and E.formel_einfuegen(self.ed, E.GLEICHUNGEN[int(schl)][1]))
        m.fuss("Neue Gleichung einfügen …", self.formel)
        return m


    def menue_deckblattKlappe(self):
        """Deckblätter wie in der Vorlage: Kopf „Stil“ mit Hochformat/Querformat, darunter die Gestaltungen als Seitenbilder in vier Spalten
        (rollend). Ein Klick setzt das Deckblatt als ersten Abschnitt an den Anfang (ersetzt ein vorhandenes)."""
        from PySide6.QtCore import QRectF, QSize
        from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
        from PySide6.QtWidgets import QButtonGroup, QHBoxLayout, QLabel, QToolButton, QWidget
        from lunivo_writer.core.farben import Farbe
        from lunivo_writer.editor import deckblatt as DB
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        HOCH, QUER = QSize(130, 184), QSize(184, 130)
        m = RasterAuswahl(self.w, spalten=4, groesse=HOCH, hoehe_max=640)

        def zeichner(name):
            def f(p: QPainter, r: QRectF) -> None:
                p.setPen(QColor("#c8c8c8")); p.drawRect(r.adjusted(0.5, 0.5, -0.5, -0.5))
                DB.zeichnen(p, name, r.adjusted(1, 1, -1, -1))
            return f

        def fuellen(quer: bool) -> None:
            m.leeren(QUER if quer else HOCH)
            m.quer = quer
            for name in DB.NAMEN:
                m.kachel(name, f"{name} ({DB.gestaltung(name).gruppe})", zeichner(name)).setCheckable(False)
            if m.isVisible():
                m.neu_messen()

        def symbol(senkrecht: bool) -> QIcon:
            pm = QPixmap(16, 16); pm.fill(Qt.transparent)
            p = QPainter(pm); p.setPen(QColor(Farbe.AKZENT))
            for i in range(3):
                (p.drawLine(4 + i * 4, 2, 4 + i * 4, 13) if senkrecht else p.drawLine(2, 4 + i * 4, 13, 4 + i * 4))
            p.end()
            return QIcon(pm)
        kopf = QWidget(); h = QHBoxLayout(kopf); h.setContentsMargins(2, 0, 2, 4)
        h.addWidget(QLabel("Stil")); h.addStretch(1)
        gruppe = QButtonGroup(kopf)
        for text, quer in (("Hochformat", False), ("Querformat", True)):
            k = QToolButton(); k.setText(text); k.setIcon(symbol(not quer)); k.setCheckable(True); k.setAutoRaise(True)
            k.setToolButtonStyle(Qt.ToolButtonTextBesideIcon); k.setChecked(not quer); k.setAccessibleName(f"Deckblätter im {text}")
            k.clicked.connect(lambda _c=False, q=quer: fuellen(q))
            gruppe.addButton(k); h.addWidget(k)
        m.kopf(kopf)
        fuellen(False)
        m.gewaehlt.connect(lambda name: self.deckblattVorlage(name, quer=m.quer))
        return m


    def deckblattVorlage(self, k=None, vorlage=None, quer=False):
        """Aus der Galerie (``gewaehlt`` liefert den Namen als ``k``) oder als Befehl ``deckblattVorlage:["Sonne"]``."""
        if not self.ed:
            return
        from lunivo_writer.editor import deckblatt as DB
        name = vorlage or (k if isinstance(k, str) and k in DB.NAMEN else DB.NAMEN[0])
        DB.einfuegen(self.ed, name, quer)
        self.ed._recount(); self.ed.viewport().update()
        c = self.ed.textCursor(); c.setPosition(0); self.ed.setTextCursor(c)
        self.w.statusBar().showMessage(f"Deckblatt „{name}“ eingefügt — die Platzhalter in [ ] überschreiben.", 6000)


    def diagramm(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import DiagrammDialog
            d = DiagrammDialog(self.w)
            if d.exec():
                self._bild_einfuegen(d.bild(), f"Diagramm ({d.name.text()}): {d.titel_text}", "diagramm", d.daten())


    def piktogramm(self, k=None):
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import PiktogrammDialog
            d = PiktogrammDialog(self.w)
            if d.exec():
                n, farbe = d.ergebnis()
                if n:
                    self._bild_einfuegen(E.piktogramm_bild(n, 96, farbe), f"Piktogramm: {n}", "piktogramm", {"name": n, "farbe": farbe})


    def screenshot(self, k=None):
        if not self.ed:
            return
        antwort = QMessageBox(QMessageBox.Question, "Bildschirmfoto", "Was soll aufgenommen werden?", QMessageBox.NoButton, self.w)
        ganz = antwort.addButton("Ganzer Bildschirm", QMessageBox.AcceptRole)
        bereich = antwort.addButton("Bereich wählen …", QMessageBox.AcceptRole)
        antwort.addButton("Abbrechen", QMessageBox.RejectRole)
        antwort.exec()
        if antwort.clickedButton() not in (ganz, bereich):
            return
        nur_bereich = antwort.clickedButton() is bereich
        from PySide6.QtCore import QTimer
        self.w.hide()
        QTimer.singleShot(500, lambda: self._aufnehmen(nur_bereich))


    def _aufnehmen(self, nur_bereich: bool):
        pm = QApplication.primaryScreen().grabWindow(0)
        if not nur_bereich:
            self.w.show()
            self._foto_einfuegen(pm)
            return
        from lunivo_writer.ui.dialogs.bildschirmfoto import BereichWahl
        self._wahl = BereichWahl(pm)
        self._wahl.fertig.connect(self._bereich_fertig)
        self._wahl.showFullScreen()


    def _bereich_fertig(self, pm):
        self.w.show()
        self._foto_einfuegen(pm)


    def _foto_einfuegen(self, pm):
        if pm is not None and not pm.isNull() and self.ed:
            self._bild_einfuegen(pm.toImage(), "Bildschirmfoto")


    def textfeld(self, k=None):
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            E.textfeld(self.ed)


    def initiale(self, k=None):
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            if not E.initiale(self.ed):
                self.w.statusBar().showMessage("Der Absatz ist leer.", 3000)


    def textAusDatei(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.services import file_service as formats
        from lunivo_writer.models.report import DocumentIOError
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_waehlen
        wahl = datei_waehlen(self.w, "Text aus Datei einfügen", self.w.settings.get("last_dir", "") or "", formats.OPEN_FILTER)
        if not wahl:
            return
        pfad = wahl[0]
        try:
            rep = E.text_aus_datei(self.ed, pfad)
        except DocumentIOError as e:
            QMessageBox.warning(self.w, "Einfügen nicht möglich", str(e))
            return
        self.w._show_report(rep, "Hinweise zur eingefügten Datei", "beim Einfügen")


    def formel(self, k=None):
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import FormelDialog
            d = FormelDialog(self.w)
            if d.exec() and d.eingabe.text().strip():
                E.formel_einfuegen(self.ed, d.eingabe.text())


    def schnelltabelle(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import einfuegen as E
        m = QMenu()
        for n in E.SCHNELLTABELLEN:
            m.addAction(n, lambda _=False, n=n: E.schnelltabelle(self.ed, n))
        self._popup(m)


    def deckblatt(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.dialogs.einfuegen_dialoge import DeckblattDialog
        d = DeckblattDialog(self.w, self.w.settings.get("benutzer/name", ""))
        if d.exec():
            E.deckblatt_einfuegen(self.ed, d.vorlage.currentText(), d.titel.text(), d.unter.text(), d.autor.text(), d.datum.text())


    def datumUhrzeit(self, k=None):
        if self.ed:
            from lunivo_writer.editor import felder as F
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import DatumDialog
            d = DatumDialog(self.w, self.w.settings.get("einfuegen/datum_sprache", "de_DE") or "de_DE")
            if d.exec() and d.ergebnis():
                self.w.settings.set("einfuegen/datum_sprache", d.sprache.currentData())
                if d.feldanweisung():
                    F.feld_einfuegen(self.ed, d.feldanweisung(), d.ergebnis())
                else:
                    self.ed.textCursor().insertText(d.ergebnis())
                    self.ed.document().setModified(True)


    def textbaustein(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import BausteinDialog
            BausteinDialog(self.w, self.ed).exec()


    def textbausteine(self, k=None):
        self.textbaustein()


    def schnellbaustein(self, k=None):
        """F3: steht vor der Schreibmarke ein Kürzel, kommt der Baustein sofort; sonst die Liste aller Bausteine zum Auswählen."""
        if not self.ed:
            return
        from PySide6.QtGui import QTextCursor
        from lunivo_writer.services import bausteine
        c = self.ed.textCursor()
        if not c.hasSelection():
            w = QTextCursor(c); w.movePosition(QTextCursor.StartOfWord, QTextCursor.KeepAnchor)
            b = bausteine.finde_kuerzel(w.selectedText())
            if b is not None:
                w.removeSelectedText(); bausteine.einfuegen(w, b); self.ed.document().setModified(True)
                return
        m = QMenu()
        self._bausteine_fuellen(m)
        self._popup(m)
