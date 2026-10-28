"""Befehle: Einfügen."""
from __future__ import annotations

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QFileDialog, QMenu, QMessageBox
from lunivo_writer.core.befehle.hilfen import _farbfeld


class EinfuegenBefehle:
    """Befehle des Bandes: Einfügen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""


    # ---- Einfügen -------------------------------------------------------------------------------------------------
    def seitenumbruch(self, k=None):
        if self.ed: self.ed.insert_page_break()


    def tabelleRaster(self, k=None):
        self.w.insert_table()


    def bild(self, k=None):
        self.w.insert_image()


    def hyperlink(self, k=None):
        self.w.insert_link()


    def kopfFussZeigen(self, k=None):
        self.w.edit_header_footer(True)


    def menue_seitenzahlKlappe(self):
        m = QMenu()
        m.addAction("Seitenzahl in die Fußzeile", self.w.insert_page_number)
        return m


    def seitenzahlKlappe(self, k=None):
        self.w.insert_page_number()


    # ==== Einfügen ===========================================================================================================
    def leereSeite(self, k=None, quer=None):
        """Leere Seite (Vertikal/Horizontal; ohne Angabe wie die Seite davor). Hat sie eine andere Ausrichtung als die Seite davor, steht sie
        in einem eigenen Abschnitt."""
        e = self.ed
        if not e:
            return
        if quer is None or bool(quer) == e.abschnitt_seite().landscape:
            e.insert_page_break(); e.insert_page_break()
            return
        alt = e.abschnitt_seite().landscape
        e.abschnitt_einfuegen("naechste")
        e.abschnitt_einfuegen("naechste")
        c = e.textCursor(); c.movePosition(QTextCursor.PreviousBlock); e.setTextCursor(c)
        self.w.set_orientation(bool(quer))
        c = e.textCursor(); c.movePosition(QTextCursor.NextBlock); e.setTextCursor(c)
        if e.abschnitt_seite().landscape != alt:
            self.w.set_orientation(alt)


    def sonderzeichen(self, k=None):
        from lunivo_writer.ui.dialogs.sonderzeichen import SonderzeichenDialog
        e = self.ed
        if e:
            d = SonderzeichenDialog(self.w, lambda z: (e.insertPlainText(z), self._symbol_merken(z)))
            d.show()
            self._sz = d


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
        m.eintrag("Seitenumbruch", self.seitenumbruch, symbol=self._sym("umbruch"), kuerzel="Strg+Enter")
        m.eintrag("Spaltenumbruch", self.spaltenumbruch, symbol=self._sym("spaltenumbruch"))
        m.eintrag("Textflussumbruch", self.textflussumbruch, symbol=self._sym("textflussumbruch"), kuerzel="Umschalt+Enter")
        m.trenner()
        for art, text, sym in (("NextPage", "Abschnittsumbruch auf nächster Seite", "abschnitt"),
                               ("Continuous", "Fortlaufender Abschnittsumbruch", "abschnittlaufend"),
                               ("EvenPage", "Abschnittsumbruch auf gerader Seite", "abschnittgerade"),
                               ("OddPage", "Abschnittsumbruch auf ungerader Seite", "abschnittungerade")):
            m.eintrag(text, lambda a=art: self.abschnittsumbruch(None, a), symbol=self._sym(sym))
        return m


    def menue_leereSeiteKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Vertikal", lambda: self.leereSeite(None, False), symbol=self._sym("leereseite"))
        m.eintrag("Horizontal", lambda: self.leereSeite(None, True), symbol=self._sym("querformat"))
        return m


    def menue_tabelleKlappe(self):
        """Tabelle wie in WPS: 10 × 10 Zellen, darunter Einfügen, Zeichnen, Text ↔ Tabelle; was nicht passt, bleibt grau."""
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.baukasten.zellen_raster import ZellenRaster
        m = ZellenRaster(self.w, 10, 10)
        m.gewaehlt.connect(lambda z, s: self.ed and self.ed.insert_table(z, s))
        m.addSeparator()
        m.addAction(self._sym("tabelle"), "Tabelle einfügen …", self.tabelleRaster)
        zeichnen = m.addAction(self._sym("stift"), "Tabelle zeichnen")
        zeichnen.setEnabled(False); zeichnen.setToolTip("Tabellen mit dem Stift zeichnen kann Lunivo noch nicht.")
        zu_tab = m.addAction(self._sym("tabelleWahl"), "Text in Tabelle umwandeln …", self.textInTabelle)
        zu_text = m.addAction(self._sym("schnelltab"), "Tabelle in Text konvertieren …", self.tabelleInText)
        m.addSeparator()
        schnell = m.addMenu(self._sym("schnelltab"), "Schnelltabelle")
        for n in E.SCHNELLTABELLEN:
            schnell.addAction(n, lambda n=n: self.ed and E.schnelltabelle(self.ed, n))

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
        return m


    def menue_textfeldKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Horizontal", self.textfeld, symbol=self._sym("textrahmen"))
        m.eintrag("Vertikal", None, symbol=self._sym("textrichtung"), aktiv=False,
                  tip="Senkrecht laufender Text in Textfeldern ist in Lunivo noch nicht möglich.")
        m.eintrag("Mehrzeiliger Text", self.textfeldMehrzeilig, symbol=self._sym("block"))
        return m


    def textfeldMehrzeilig(self, k=None):
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            E.textfeld(self.ed, "Text hier eingeben\n\n", breite=100)


    def menue_schnellbausteineKlappe(self):
        """Schnellbausteine wie in WPS: AutoText-Liste ▸ (die Textbausteine) und Felder …"""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        liste = m.untermenue("AutoText-Liste", self._sym("baustein"))
        liste.aboutToShow.connect(lambda: (liste.clear(), self._bausteine_fuellen(liste)))
        m.eintrag("Felder …", self.felder, symbol=self._sym("feld"))
        return m


    def _bausteine_fuellen(self, m) -> None:
        from lunivo_writer.services import bausteine
        for titel, liste in (("Eigene", bausteine.laden()), ("Standard", bausteine.standard())):
            if not liste:
                continue
            m.addSection(titel)
            for b in liste:
                m.addAction(b["name"] + (f"   [{b['kuerzel']}]" if b.get("kuerzel") else ""),
                            lambda _=False, b=b: self.ed and (bausteine.einfuegen(self.ed.textCursor(), b), self.ed.document().setModified(True)))
        m.addSeparator()
        m.addAction("Textbausteine verwalten …", self.textbaustein)


    def schnellbausteine(self, k=None):
        self._popup(self.menue_schnellbausteineKlappe())


    def felder(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import felder as F
        from lunivo_writer.ui.dialogs.einfuegen_fenster import FelderDialog
        t = self.w.current_tab()
        kontext = {"seiten": getattr(self.ed, "_pages", 1), "woerter": len(self.ed.toPlainText().split()),
                   "autor": self.w.settings.get("benutzer/name", ""), "pfad": getattr(t, "path", "") or ""}
        d = FelderDialog(self.w, kontext)
        if d.exec():
            F.feld_einfuegen(self.ed, *d.feld())


    def menue_symbolKlappe(self):
        """Symbol wie in WPS: zuletzt verwendete und benutzerdefinierte Symbole als Kacheln, darunter „Weitere Symbole …“.
        Die zuletzt verwendeten werden bei jedem Aufklappen neu gesetzt (das Menü entsteht nur einmal)."""
        from PySide6.QtCore import QSize
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, textkachel
        m = RasterAuswahl(self.w, titel="Aktuell verwendete Symbole:", spalten=12, groesse=QSize(24, 24))
        for i in range(self.ZULETZT_ANZAHL):
            m.kachel(f"zuletzt{i}")
        m.abschnitt("Benutzerdefinierte Symbole:")
        m.kacheln([(z, f"„{z}“ einfügen", textkachel(z)) for z in self.BENUTZER_SYMBOLE])
        m.fuss("Weitere Symbole …", self.sonderzeichen)
        for b in m.knoepfe.values():
            b.setCheckable(False)
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
        import json
        try:
            liste = json.loads(str(self.w.settings.get(self.ZULETZT_SYMBOLE, "") or "[]"))
        except ValueError:
            return []
        return [z for z in liste if isinstance(z, str) and z] if isinstance(liste, list) else []


    def _symbol_merken(self, z: str) -> None:
        liste = [z] + [x for x in self._symbole_zuletzt() if x != z]
        import json
        self.w.settings.set(self.ZULETZT_SYMBOLE, json.dumps(liste[:self.ZULETZT_ANZAHL], ensure_ascii=False))


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
            TT.tabelle_zu_text(self.ed, d.trenner())


    def inhaltsverzeichnis(self, k=None):
        if self.ed:
            from lunivo_writer.editor.verzeichnis import verzeichnis_einfuegen
            n = verzeichnis_einfuegen(self.ed)
            if not n:
                QMessageBox.information(self.w, "Inhaltsverzeichnis", "Im Dokument gibt es keine Überschriften. "
                                        "Formatieren Sie Überschriften mit den Stilen „Überschrift 1–3“.")


    def verzeichnisseAktualisieren(self, k=None):
        if self.ed:
            from lunivo_writer.editor.verzeichnis import verzeichnis_aktualisieren
            verzeichnis_aktualisieren(self.ed)


    # ---- Einfügen: Illustrationen, Text, Symbole, Tabellen, Seiten ----------------------------------------------------
    def _bild_einfuegen(self, img, alt, art=None, daten=None):
        from lunivo_writer.editor import einfuegen as E
        E.qimage_einfuegen(self.ed, img, alt, art, daten)


    def formenGalerie(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor import einfuegen as E
        m = QMenu()
        for f in E.FORMEN:
            m.addAction(f, lambda _=False, f=f: self._bild_einfuegen(E.form_bild(f), f"Form: {f}", "form", {"form": f}))
        m.addSeparator()
        m.addAction("Weitere Formen und Farben …", self.zeichnen)
        self._popup(m)


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


    def diagramm(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import DiagrammDialog
            d = DiagrammDialog(self.w)
            if d.exec():
                self._bild_einfuegen(d.bild(), f"{d.art.currentText()}diagramm: {d.titel.text()}", "diagramm", {"art": d.art.currentText(), "titel": d.titel.text()})


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
        pfad, _ = QFileDialog.getOpenFileName(self.w, "Text aus Datei einfügen", self.w.settings.get("last_dir", ""), formats.OPEN_FILTER)
        if not pfad:
            return
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
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import DatumDialog
            d = DatumDialog(self.w)
            if d.exec() and d.ergebnis():
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
