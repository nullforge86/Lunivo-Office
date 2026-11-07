"""Datei-Ansicht (Backstage)."""
from __future__ import annotations

import os
from datetime import datetime
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QFrame, QMessageBox
from lunivo_writer.ui.baukasten.eingabe_fenster import EingabeFenster
from lunivo_writer.ui.baukasten.speichern_fenster import Dateifenster
from lunivo_writer.models.page import HeaderFooter
from lunivo_writer.ui.dialogs.dokument_dialoge import HeaderFooterDialog, TableDialog
from lunivo_writer.ui.baukasten.dropdown.menue_tafel import MenueTafel
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.theme import kopf_symbolfarbe
from lunivo_writer.ui.hauptfenster.backstage_objektformat import BackstageObjektformatBaustein


from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.mass import (
    ABSTAND_NORMAL,
    BREITE_SCHIENE,
    BREITE_SCHIENE_BESCHRIFTET,
    GROESSE_KNOPF_SCHIENE,
    GROESSE_KNOPF_SCHIENE_TEXT,
    ICON_ASSISTENT,
    ICON_KNOPF_GROSS,
    ICON_LISTE,
    ICON_MITTEL,
    ICON_NORMAL,
    PADDING_BACKSTAGE_STEUERKNOPF,
    RAND_SCHIENE,
)
class BackstageBaustein(BackstageObjektformatBaustein):
    """Datei-Ansicht (Backstage). Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""


    def _backstage_verbinden(self):
        r = getattr(self.band, "reiter", None)
        if r is None:
            return
        self.backstage.hide()
        self.arbeit.show()
        r.currentChanged.connect(self._reiter_gewechselt)
        r.tabBarClicked.connect(self._reiter_angeklickt)
        # Die Datei-Ansicht heißt „☰ Menü“ und steht ganz links vor dem Schnellzugriff; der Reiter „Datei“ bleibt dafür verborgen
        for i in range(r.count()):
            if r.tabText(i) == "Datei":
                r.setTabVisible(i, False)
        k = self.band.menue_knopf
        try:
            k.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        k.setText("Menü"); k.setIcon(icons.icon("menu", ICON_NORMAL, kopf_symbolfarbe())); k.setIconSize(QSize(ICON_NORMAL, ICON_NORMAL)); k.setCheckable(True); k.setToolTip("Menü: Neu, Öffnen, Speichern, Exportieren, Drucken, Optionen, Hilfe")
        k.setStyleSheet('QToolButton { font-weight: 600; padding: ' f"{PADDING_BACKSTAGE_STEUERKNOPF}" '; }')          # die Farbe des geöffneten Menüs kommt aus dem Thema (theme.py)
        k.clicked.connect(self._menue_geklickt)
        r.currentChanged.connect(lambda i, kk=k: kk.setChecked(self._ist_datei(i)))


    def _menue_geklickt(self):
        """☰ Menü: öffnet die Datei-Ansicht, ein zweiter Klick schließt sie wieder."""
        r = self.band.reiter
        if self.backstage.isVisible():
            self.backstage_schliessen()
            return
        i = next((n for n in range(r.count()) if r.tabText(n) == "Datei"), None)
        if i is not None:
            r.setCurrentIndex(i)
        self.band.menue_knopf.setChecked(self.backstage.isVisible())


    def _ist_datei(self, i: int) -> bool:
        r = self.band.reiter
        return 0 <= i < r.count() and r.tabText(i) == "Datei"


    def _reiter_gewechselt(self, i: int):
        if self._ist_datei(i):
            self.backstage_oeffnen()
        else:
            self._letzter_reiter = i
            self.backstage_zu()


    def _reiter_angeklickt(self, i: int):
        import time
        if self._ist_datei(i) and self.backstage.isVisible() and time.monotonic() - self._bs_zeit > 0.4:   # zweiter Klick schließt
            self.backstage_schliessen()


    def backstage_oeffnen(self, seite: str = "zuletzt", unter: str | None = None):
        import time
        self._bs_zeit = time.monotonic()
        for name in ("stapel", "linie"):                              # die Oberfläche „Symbolleisten“ hat nur eine Leiste, kein Band mit Reitern
            if hasattr(self.band, name):
                getattr(self.band, name).hide()
        self.arbeit.hide()
        self.backstage.oeffnen(seite, unter)
        self.backstage.show()
        if hasattr(self.band, "menue_knopf"):
            self.band.menue_knopf.setChecked(True)


    def backstage_zu(self):
        if not self.backstage.isVisible():
            return
        self.backstage.hide()
        self.arbeit.show()
        if hasattr(self.band, "stapel") and not self.band._eingeklappt:
            self.band.stapel.show()
        if hasattr(self.band, "linie"):
            self.band.linie.show()
        if hasattr(self.band, "menue_knopf"):
            self.band.menue_knopf.setChecked(False)
        self.ki.geaendert.emit()                                   # Einstellungen der Optionen übernehmen (KI, Anbieter …)
        t = self.current_tab()
        if t is not None:
            t.editor.setFocus()                                    # Arbeitskontext: weiterschreiben, wo man aufgehört hat


    def backstage_schliessen(self):
        r = self.band.reiter
        if self._ist_datei(r.currentIndex()):
            r.setCurrentIndex(self._letzter_reiter if not self._ist_datei(self._letzter_reiter) else 1)
        self.backstage_zu()


    def show_main_menu(self):
        daten = next(m for m in self.band.daten["menues"] if m["name"] == "Datei")
        self._tafel = MenueTafel(daten["punkte"], self.befehle, self)
        self._tafel.zeigen_unter(self.band.menue_knopf)


    def _leiste_links(self):
        """Schmale Leiste links: Suchen, Kommentare, Überschriften, Änderungen, Noten, Vorlesen. Ein Klick öffnet das Feld, ein zweiter schließt es."""
        from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout
        from lunivo_writer.ui.document.navigation import SEITEN, TITEL
        from lunivo_writer.ui.widgets import icons
        leiste = QFrame()
        leiste.setObjectName("leisteLinks")
        leiste.setFixedWidth(BREITE_SCHIENE)
        v = QVBoxLayout(leiste)
        v.setContentsMargins(*RAND_SCHIENE)
        v.setSpacing(ABSTAND_NORMAL)
        self._links = {}
        symbole = {"suche": "lupe", "kommentare": "notiz", "ueberschriften": "gliederung", "aenderungen": "verfolgt", "noten": "fussnote", "vorlesen": "vorlesen"}
        for key in SEITEN:
            b = QToolButton()
            icons.setze(b, symbole[key], ICON_MITTEL); b.setIconSize(QSize(ICON_MITTEL, ICON_MITTEL))
            b.setToolTip(TITEL[key]); b.setAccessibleName(TITEL[key])
            b.setCheckable(True)
            b.setFixedSize(*GROESSE_KNOPF_SCHIENE)
            b.clicked.connect(lambda _=False, k=key: self._links_klick(k))
            v.addWidget(b)
            self._links[key] = b
        v.addStretch(1)
        self.navigation.zustandGeaendert.connect(self._links_sync)
        self._links_sync()
        return leiste


    KURZTEXT_LINKS = {"suche": "Suchen", "kommentare": "Kommentare", "ueberschriften": "Gliederung", "aenderungen": "Änderungen", "noten": "Noten", "vorlesen": "Vorlesen"}

    def leisten_beschriften(self) -> None:
        """Option „Seitenleisten mit Text“: unter jedem Symbol der beiden Randleisten steht sein Name (breitere Leiste, kleinere Schrift)."""
        mit = self.settings.get_bool("ui/leisten_text", False)
        for leiste_name, knoepfe, kurz in (("leisteLinks", getattr(self, "_links", {}), self.KURZTEXT_LINKS),
                                           ("leisteRechts", getattr(self, "_rechts", {}), {})):
            leiste = self.findChild(QFrame, leiste_name)
            if leiste is None:
                continue
            leiste.setFixedWidth(BREITE_SCHIENE_BESCHRIFTET if mit else BREITE_SCHIENE)
            for key, b in knoepfe.items():
                if mit:
                    b.setText(kurz.get(key, key)); b.setToolTipDuration(-1)
                    f = b.font(); f.setPointSizeF(max(7.0, f.pointSizeF() * 0.85)); b.setFont(f)
                    b.setToolButtonStyle(Qt.ToolButtonTextUnderIcon); b.setFixedSize(*GROESSE_KNOPF_SCHIENE_TEXT)
                else:
                    name = kurz.get(key, key)
                    b.setText(""); b.setFont(self.font())
                    b.setAccessibleName(name)                                    # ohne Text unter dem Symbol: der Name bleibt als Tooltip und für die Bedienhilfe
                    if not b.toolTip():
                        b.setToolTip(name)
                    b.setToolButtonStyle(Qt.ToolButtonIconOnly); b.setFixedSize(*GROESSE_KNOPF_SCHIENE)

    def _links_klick(self, key: str):
        if self.navigation.isVisible() and self.navigation.aktuelle_seite == key:
            self.navigation.hide()
        else:
            self.navigation.show()
            if key == "suche":
                self.navigation.suche_zeigen()
            else:
                self.navigation.zeige_tab(key)
        self._links_sync()


    def _links_sync(self):
        sicht = self.navigation.isVisible()
        for key, b in self._links.items():
            b.setChecked(sicht and self.navigation.aktuelle_seite == key)


    def _leiste_rechts(self):
        """Schmale Leiste rechts: Die vier Reiter der Schreibhilfe (Prüfen, Lesen, Schreiben, KI) und der KI-Chat schalten die Seitenleiste um."""
        from PySide6.QtWidgets import QFrame, QToolButton, QVBoxLayout
        from lunivo_writer.ui.widgets import icons
        leiste = QFrame()
        leiste.setObjectName("leisteRechts")
        leiste.setFixedWidth(BREITE_SCHIENE)
        v = QVBoxLayout(leiste)
        v.setContentsMargins(*RAND_SCHIENE)
        v.setSpacing(ABSTAND_NORMAL)
        self._rechts = {}
        # gleiche sichtbare Symbolgröße wie links (dort füllen die Zeichnungen ~18 px von 22): Haken, KI-Plus und Chat sind kleiner gezeichnet und bekommen mehr Platz
        px_rechts = {"haken": ICON_KNOPF_GROSS, "assistent": ICON_ASSISTENT, "chat": ICON_LISTE, "brille": ICON_MITTEL, "stift": ICON_MITTEL}
        for name, sym, tip in (("Prüfen", "haken", "Prüfen — die Funde der Schreibhilfe"), ("Lesen", "brille", "Lesen — Lesehilfe, Vorlesen"),
                               ("Schreiben", "stift", "Schreiben — Schalter, Textbausteine, Sprache"), ("KI", "assistent", "KI — Korrektur, Übersetzen, Aktionen"),
                               ("Chat", "chat", "KI-Chat")):
            b = QToolButton()
            px = px_rechts.get(sym, ICON_MITTEL)
            icons.setze(b, sym, px); b.setIconSize(QSize(px, px))
            b.setToolTip(tip); b.setAccessibleName(name)
            b.setCheckable(True)
            b.setFixedSize(*GROESSE_KNOPF_SCHIENE)
            b.clicked.connect(lambda _=False, n=name: self._rechts_klick(n))
            if name == "Chat":
                v.addSpacing(8)
            v.addWidget(b)
            self._rechts[name] = b
        v.addStretch(1)
        self.sidebar.bereich_geaendert.connect(lambda _i: self._rechts_sync())
        self._rechts_sync()
        return leiste


    def _rechts_klick(self, name: str):
        """Ein Knopf der Leiste: öffnet die Seitenleiste auf dem Reiter; ein zweiter Klick auf denselben Reiter schließt sie wieder."""
        ist_chat = name == "Chat"
        schon_da = (not self.sidebar.isHidden() and ((ist_chat and self.sidebar.stapel.currentIndex() == 1)
                    or (not ist_chat and self.sidebar.stapel.currentIndex() == 0 and self.sidebar.aktueller_reiter == name)))
        if schon_da:
            self.toggle_sidebar()
        else:
            if self.sidebar.isHidden():
                self.toggle_sidebar()
            self.sidebar.zeige_bereich(1) if ist_chat else self.sidebar.zeige_reiter(name)
        self._rechts_sync()


    def _rechts_sync(self):
        sicht = not self.sidebar.isHidden()
        i = self.sidebar.stapel.currentIndex()
        for name, b in self._rechts.items():
            an = sicht and ((name == "Chat" and i == 1) or (name != "Chat" and i == 0 and self.sidebar.aktueller_reiter == name))
            b.setChecked(an)


    def texteffekte_seitenleiste(self):
        """Den Bereich „Texteffekte formatieren“ in der Seitenleiste öffnen; Änderungen gelten sofort für die Markierung."""
        from lunivo_writer.editor import texteffekt
        if self.current_editor() is None:
            return
        self._seitenleiste_oeffnen()

        def anwenden(w: dict):
            e = self.current_editor()
            if e is not None:
                e._merge(texteffekt.zu_format(w))
        self.sidebar.zeige_texteffekte(texteffekt.aus_format(self.befehle._fmt()), anwenden)


    def _effekt_sync(self):
        """Folgt die Markierung einer anderen Formatierung, zeigt der offene Bereich „Texteffekte“ deren Werte."""
        from lunivo_writer.editor import texteffekt
        self._format_folgen("texteffekte", lambda e: texteffekt.aus_format(self.befehle._fmt()))


    def toggle_sidebar(self):
        on = self.sidebar.isHidden()
        self.sidebar.setVisible(on)
        self.settings.set("ui/seitenleiste", on)
        if not on and self.current_tab() is not None:
            self.current_tab().editor.setFocus()                   # Seitenleiste zu: weiterschreiben, wo man war
        if hasattr(self, "_rechts"):
            self._rechts_sync()
        self._chat_knopf_pruefen()


    def zum_band_springen(self) -> None:
        """F10: aus dem Text zu den Reitern des Bandes (dann mit Tab und Pfeiltasten weiter), noch einmal F10: zurück in den Text."""
        from PySide6.QtWidgets import QApplication
        f = QApplication.focusWidget()
        t = self.current_tab()
        if f is not None and self.band.isAncestorOf(f) and t is not None:
            t.editor.setFocus()
        else:
            self.band.reiter.setFocusPolicy(Qt.StrongFocus)
            self.band.reiter.setFocus()

    def toggle_menubar(self):
        self.menubar_wanted = not self.menubar_wanted
        self.menuBar().setVisible(self.menubar_wanted)
        self.settings.set("ui/menueleiste", self.menubar_wanted)


    def rename_document(self):
        t = self.current_tab()
        if not t or not t.path:
            QMessageBox.information(self, "Umbenennen", "Das Dokument ist noch nicht gespeichert.")
            return
        neu, ok = EingabeFenster.getText(self, "Umbenennen", "Neuer Dateiname:", text=os.path.basename(t.path))
        if not ok or not neu.strip() or neu == os.path.basename(t.path):
            return
        ziel = os.path.join(os.path.dirname(t.path), neu.strip())
        if os.path.exists(ziel):
            QMessageBox.warning(self, "Umbenennen", "Eine Datei mit diesem Namen gibt es schon.")
            return
        try:
            os.rename(t.path, ziel)
        except OSError as e:
            QMessageBox.warning(self, "Umbenennen", f"Nicht möglich: {e.strerror or e}")
            return
        self.settings.remove_recent(t.path)
        t.set_path(ziel)
        self.settings.add_recent(ziel)
        self._update_tab_titles()


    def toggle_sperre(self):
        """Überprüfen ▸ Bearbeitung einschränken: Dokument schreibgeschützt (nur in dieser Sitzung)."""
        t = self.current_tab() if hasattr(self, "current_tab") else None
        if not t:
            return
        t.gesperrt = not getattr(t, "gesperrt", False)
        t.editor.setReadOnly(t.gesperrt or self.lesemodus)
        self.statusBar().showMessage("Bearbeitung gesperrt." if t.gesperrt else "Bearbeitung freigegeben.", 4000)


    def toggle_marks(self, on: bool):
        self.marken_setzen(on, on)


    def insert_table(self):
        if not self.current_editor():
            return
        d = TableDialog(self, (self.settings.get_int("tabelle/spalten", 5), self.settings.get_int("tabelle/zeilen", 2)))
        if d.exec():
            if d.speichern.isChecked():
                self.settings.set("tabelle/spalten", d.cols.value()); self.settings.set("tabelle/zeilen", d.rows.value())
            self._ed(lambda e: e.insert_table(d.rows.value(), d.cols.value(), spaltenbreite=d.spaltenbreite_px()))


    def insert_image(self):
        e = self.current_editor()
        if not e:
            return
        path, _ = Dateifenster.getOpenFileName(self, "Bild einfügen", self.settings.get("last_dir", os.path.expanduser("~")),
                                              "Bilder (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;Alle Dateien (*)")
        if path and not e.insert_image(path):
            QMessageBox.warning(self, "Bild einfügen", "Die Datei ist kein lesbares Bild.")


    def insert_link(self):
        e = self.current_editor()
        if not e:
            return
        url, ok = EingabeFenster.getText(self, "Hyperlink", "Adresse (z. B. https://…):")
        if ok and url.strip():
            e.insert_link(url.strip())


    def insert_date(self):
        self._ed(lambda e: e.textCursor().insertText(datetime.now().strftime("%d.%m.%Y")))


    def edit_header_footer(self, header: bool):
        t = self.current_tab()
        if not t:
            return
        if not t.editor.web:                                  # Bearbeiten direkt auf der Seite, dazu der Kontext-Reiter
            self.kopffuss_starten(t.editor, header)
            return
        page = t.editor.abschnitt_seite()
        erste = False
        if page.diff_first:
            w, ok = EingabeFenster.getItem(self, "Kopf- und Fußzeile", "Welche Seiten?", ["Erste Seite", "Übrige Seiten"], 0, False)
            if not ok:
                return
            erste = w == "Erste Seite"
        if erste:
            hf = page.first_header if header else page.first_footer
        else:
            hf = page.header if header else page.footer
        d = HeaderFooterDialog(("Kopfzeile" if header else "Fußzeile") + (" (erste Seite)" if erste else ""), hf, self)
        if d.exec():
            if erste:
                if header:
                    page.first_header = d.value()
                else:
                    page.first_footer = d.value()
            elif header:
                page.header = d.value()
            else:
                page.footer = d.value()
            t.editor.page_settings_changed(page)


    def kopffuss_starten(self, editor, header: bool = True):
        """Kopf- oder Fußzeile auf der Seite bearbeiten: Textfeld über dem Rand, Kontext-Reiter „Kopf- und Fußzeile“ eingeblendet und aktiv."""
        from PySide6.QtCore import Qt
        b = editor.kopffuss()
        b.beendet.connect(self._kopffuss_aus, Qt.UniqueConnection)
        if b.starte("kopf" if header else "fuss"):
            self.band.kontext("kopffuss", True, True)


    def _kopffuss_aus(self):
        self.band.kontext("kopffuss", False)


    def insert_page_number(self):
        t = self.current_tab()
        if not t:
            return
        page = t.editor.abschnitt_seite()
        if page.footer.is_empty():
            page.footer = HeaderFooter("{PAGE}", "center")
        elif "{PAGE}" not in page.footer.text:
            page.footer.text += " {PAGE}"
        t.editor.page_settings_changed(page)


    def find_dialog_show(self, reiter: str = "Suchen", element: str = ""):
        """Strg+F, Strg+H, Strg+G: „Suchen und ersetzen“ als Feld in der linken Seitenleiste (Reiter Suchen, Ersetzen oder Gehe zu)."""
        if self.current_editor():
            self.navigation.suche_zeigen(reiter=reiter, element=element)
