"""Einfügen-Befehle für Illustrationen, Text, Symbole und Seiten."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication, QMenu, QMessageBox
from lunivo_writer.core.befehle.hilfen import _farbfeld
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten import farben as BF


class EinfuegenObjektBefehle:
    # ---- Einfügen: Illustrationen, Text, Symbole, Tabellen, Seiten ----------------------------------------------------
    def _bild_einfuegen(self, img, alt, art=None, daten=None):
        from lunivo_writer.editor import einfuegen as E
        E.qimage_einfuegen(self.ed, img, alt, art, daten)


    def formenGalerie(self, k=None):
        if self.ed:
            self._popup(self.menue_formenKlappe())


    def menue_formenKlappe(self):
        """Formen wie in der Vorlage: Gruppen (Linie, Rechteck, Standardformen, Blockpfeile, …) mit kleinen Umrissbildern."""
        from PySide6.QtCore import QRectF, QSize
        from PySide6.QtGui import QColor, QPalette, QPen
        from lunivo_writer.core.farben import Farbe
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.editor import formen_katalog as K
        from lunivo_writer.ui.baukasten.dropdown.raster_auswahl import RasterAuswahl
        m = None
        for gruppe, formen in K.KATEGORIEN:
            if m is None:
                m = RasterAuswahl(self.w, titel=gruppe, spalten=16, groesse=QSize(22, 22))
            else:
                m.abschnitt(gruppe)
            for name in formen:
                def zeichne(p, r, name=name):
                    from PySide6.QtWidgets import QApplication
                    p.setPen(QPen(QApplication.palette().color(QPalette.WindowText), 1.3)); p.setBrush(Qt.NoBrush)
                    p.drawPath(K.pfad(name, QRectF(r).adjusted(2, 3, -2, -3)))
                m.kachel(name, name, zeichne).setCheckable(False)

        m.gewaehlt.connect(lambda f: self.formEinfuegen(None, f))
        bereich = m.fuss("Neuer &Zeichenbereich", self.zeichenbereich)
        bereich.setIcon(self._sym("textrahmen"))
        bereich.setToolTip("Fügt einen Bereich ein, der Formen aufnimmt: Bereich markieren, dann eine Form wählen.")
        return m


    def formEinfuegen(self, k=None, name=None):
        """Die Form ``name`` (Katalog ``formen_katalog``, auch Linien und Pfeile) einfügen: im Zeichenbereich dort, sonst als freies Objekt."""
        from lunivo_writer.editor import formen as F
        from lunivo_writer.editor import formen_katalog as K
        from lunivo_writer.editor import frei_objekt as FO
        if self.ed and name and K.hat(name) and not F.in_zeichenbereich(self.ed, name):
            return FO.einfuegen(self.ed, "form", {**FO.FORM_STANDARD, "form": name}, *((240, 60) if K.ist_linie(name) else (160, 120)))


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
                from lunivo_writer.editor import frei_objekt as FO
                FO.einfuegen(self.ed, "form", d.daten(), d.breite.value(), d.hoehe.value())


    def smartart(self, k=None):
        if self.ed:
            from lunivo_writer.editor import smartart as SA
            from lunivo_writer.ui.dialogs.smartart_dialog_foto import SmartArtDialogFoto
            d = SmartArtDialogFoto(self.w)
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
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for e in SA.LAYOUT_KATALOG:
            m.eintrag(e["name"], lambda n=e["schluessel"]: self.ed and SA.aendern(self.ed, layout=n))
        return m


    def menue_smartartFarben(self):
        from lunivo_writer.editor import smartart as SA
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for n, f in SA.FARBEN.items():
            m.eintrag(n, lambda n=n: self.ed and SA.aendern(self.ed, farben=n), symbol=_farbfeld(f[0]))
        return m


    def wordart(self, k=None):
        if self.ed:
            from lunivo_writer.editor import frei_objekt as FO
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import WordArtDialog
            d = WordArtDialog(self.w, self.ed.textCursor().selectedText().replace("\u2029", " ").strip() or "Ihr Text")
            if d.exec():
                daten = {"text": d.text.text() or " ", "vorlage": d.vorlage_nr(), "schrift": d.schrift.text() or "Liberation Sans",
                         "pt": d.pt.value(), "stil": d.stil.currentText(), "farbe": d.farbe.farbe}
                FO.einfuegen(self.ed, "wordart", daten)


    def wordartVorgabe(self, k=None, nr=0):
        """WordArt aus der Galerie: fügt sofort „Hier Text einfügen“ im gewählten Stil als freies Objekt ein — ausgewählt (Rahmen, acht Griffe,
        Drehgriff, Schnellleiste), der Text grau hinterlegt; Text ändern: Doppelklick oder „WordArt bearbeiten …“."""
        if not self.ed:
            return
        from lunivo_writer.editor import frei_objekt as FO
        text = self.ed.textCursor().selectedText().replace("\u2029", " ").strip() or FO.WORDART_STANDARD["text"]
        FO.einfuegen(self.ed, "wordart", {**FO.WORDART_STANDARD, "text": text, "vorlage": nr})
        self.w._sync_format()


    def wordartBearbeiten(self, k=None):
        """Text und Stil des gewählten WordArt-Objekts im Fenster „WordArt“ ändern."""
        if not self.ed:
            return
        from lunivo_writer.editor import frei_objekt as FO
        from lunivo_writer.ui.dialogs.einfuegen_dialoge import WordArtDialog
        d0 = FO.daten_lesen(self.ed, "wordart")
        if d0 is None:
            self.w.lbl_msg.setText("Bitte zuerst ein WordArt-Objekt markieren.")
            return
        d = WordArtDialog(self.w, d0.get("text", ""), d0.get("stil", "Verlauf"), d0.get("farbe", BF.VORGABE_WORDART), d0.get("vorlage"))
        if d.exec():
            FO.aendern(self.ed, "wordart", text=d.text.text() or " ", vorlage=d.vorlage_nr(), schrift=d.schrift.text() or "Liberation Sans",
                       pt=d.pt.value(), stil=d.stil.currentText(), farbe=d.farbe.farbe)
            self.w._sync_format()


    def textfeldBearbeiten(self, k=None):
        """Im gewählten Textfeld direkt schreiben (Doppelklick, Enter oder F2 auf das Textfeld)."""
        if self.ed:
            from lunivo_writer.editor import frei_objekt as FO
            if not FO.bearbeiten_starten(self.ed):
                self.w.lbl_msg.setText("Bitte zuerst ein Textfeld markieren.")


    def menue_wordartKlappe(self):
        """Galerie „Formatvorlage“: 15 Stile als „A“ auf hellem Kachelgrund (wie in der Vorlage, auch im dunklen Thema gut zu erkennen)."""
        from PySide6.QtCore import QRectF, QSize
        from PySide6.QtGui import QColor, QPainter, QPen, QPixmap
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.baukasten.dropdown.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, titel="Formatvorlage", spalten=9, groesse=QSize(40, 40))
        for i, (name, *_r) in enumerate(E.WORDART_VORLAGEN):
            img = E.wordart_bild("A", vorlage=i, pt=80)
            pm = QPixmap(QSize(40, 40)); pm.fill(Qt.transparent)
            p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.SmoothPixmapTransform)
            p.setBrush(QColor(BF.KACHEL_GRUND)); p.setPen(QPen(QColor(BF.KACHEL_RAND), 1)); p.drawRoundedRect(QRectF(0.5, 0.5, 39, 39), 4, 4)
            z = img.scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            p.drawImage((40 - z.width()) // 2, (40 - z.height()) // 2, z)
            p.end()
            b = m.kachel(str(i), name, pm)
            b.setCheckable(False)
        m.gewaehlt.connect(lambda schl: self.wordartVorgabe(None, int(schl)))
        return m


    def menue_gleichungKlappe(self):
        """Gleichung wie in der Vorlage: eingebaute Gleichungen als große Kacheln mit Namen, darunter „Neue Gleichung einfügen …“."""
        from PySide6.QtCore import QSize
        from PySide6.QtGui import QColor, QPainter, QPixmap
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.baukasten.dropdown.raster_auswahl import RasterAuswahl
        groesse = QSize(380, 54)
        m = RasterAuswahl(self.w, titel="Integriert", spalten=1, groesse=groesse, beschriftet=True)
        for i, (name, formel) in enumerate(E.GLEICHUNGEN):
            img = E.formel_bild(formel, 13)
            pm = QPixmap(groesse); pm.fill(QColor(Farbe.PAPIER))
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
        from lunivo_writer.ui.baukasten.dropdown.raster_auswahl import RasterAuswahl
        HOCH, QUER = QSize(130, 184), QSize(184, 130)
        m = RasterAuswahl(self.w, spalten=4, groesse=HOCH, hoehe_max=640)

        def zeichner(name):
            def f(p: QPainter, r: QRectF) -> None:
                p.setPen(QColor(Farbe.LEISTE_RAND)); p.drawRect(r.adjusted(0.5, 0.5, -0.5, -0.5))
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


    def menue_diagrammKlappe(self):
        """Klappe am Diagramm-Knopf: Diagramm … (Fenster) und Neuer Zeichenbereich."""
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Diagramm …", self.diagramm, symbol=self._sym("saeule"))
        m.eintrag("Neuer Zeichenbereich", self.zeichenbereich, symbol=self._sym("textrahmen"))
        return m


    def diagramm(self, k=None):
        if self.ed:
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import DiagrammDialog
            d = DiagrammDialog(self.w)
            if d.exec():
                from lunivo_writer.editor import frei_objekt as FO
                FO.einfuegen(self.ed, "diagramm", d.daten(), *FO.STANDARD_MASS["diagramm"])


    def piktogramm(self, k=None):
        if self.ed:
            from lunivo_writer.editor import einfuegen as E
            from lunivo_writer.ui.dialogs.einfuegen_dialoge import PiktogrammDialog
            d = PiktogrammDialog(self.w)
            if d.exec():
                n, farbe = d.ergebnis()
                if n:
                    from lunivo_writer.editor import frei_objekt as FO
                    FO.einfuegen(self.ed, "piktogramm", {"name": n, "farbe": farbe}, 96, 96)


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
        # Ziel beim Start festhalten: die verzögerte Aufnahme darf später nicht
        # versehentlich in einen inzwischen aktiven anderen Dokumentreiter einfügen.
        self._foto_editor = self.ed
        try:
            self._foto_dokument = self._foto_editor.document() if self._foto_editor is not None else None
            self._foto_revision = self._foto_dokument.revision() if self._foto_dokument is not None else -1
        except RuntimeError:
            self._foto_editor = self._foto_dokument = None
            self._foto_revision = -1
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
        ed = getattr(self, "_foto_editor", None)
        try:
            if (ed is None or self.ed is not ed or ed.document() is not getattr(self, "_foto_dokument", None)
                    or ed.document().revision() != getattr(self, "_foto_revision", -1)):
                self.w.statusBar().showMessage("Das ursprüngliche Dokument wurde gewechselt oder geändert — das Bildschirmfoto wurde nicht eingefügt.", 6000)
                return
        except RuntimeError:
            self.w.statusBar().showMessage("Das ursprüngliche Dokument ist nicht mehr verfügbar — das Bildschirmfoto wurde nicht eingefügt.", 6000)
            return
        if pm is not None and not pm.isNull():
            from lunivo_writer.editor import frei_objekt as FO
            img = pm.toImage()
            FO.bild_einfuegen(ed, img, float(img.width()), float(img.height()), alt="Bildschirmfoto")


    def textfeld(self, k=None):
        if self.ed:
            from lunivo_writer.editor import frei_objekt as FO
            FO.einfuegen(self.ed, "textfeld", dict(FO.TEXTFELD_STANDARD), 240, 60)


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
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for n in E.SCHNELLTABELLEN:
            m.eintrag(n, lambda n=n: E.schnelltabelle(self.ed, n))
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
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        self._bausteine_fuellen(m)
        self._popup(m)
