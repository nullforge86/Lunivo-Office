"""Bearbeiten, Einfügen, Seite."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication, QMessageBox
from vcl.qt.widgets.dialoge.dokument.eingabe_fenster import EingabeFenster
from vcl.qt.widgets.bausteine import weitere_farben
from vcl.qt.widgets.dialoge.dokument_dialoge import PageSetupDialog
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import AUGENSCHUTZ_PAPIER, VORGABE_MARKER
from vcl.qt.fenster.fenster.gemeinsam import _QuickInfo


class BearbeitenBaustein:
    """Bearbeiten, Einfügen, Seite. Baustein von ``MainWindow`` (siehe ``lunivo_writer/oberflaeche/programmfenster.py``)."""


    # ==== Bearbeiten/Einfügen ===================================================================
    def paste_plain(self):
        e = self.current_editor()
        if e:
            t = QApplication.clipboard().text()
            kf = e._kf()
            if t and kf is not None:
                kf.feld.insertPlainText(t)
            elif t:
                e.textCursor().insertText(t)


    def choose_color(self):
        c = weitere_farben(self, QColor(Farbe.SCHWARZ), "Schriftfarbe")
        if c is not None:
            self._ed(lambda e: e.set_text_color(c))


    def choose_highlight(self):
        c = weitere_farben(self, QColor(VORGABE_MARKER), "Texthervorhebungsfarbe")
        if c is not None:
            self._ed(lambda e: e.set_highlight(c))


    def paragraph_dialog(self):
        e = self.current_editor()
        if not e:
            return
        from vcl.qt.widgets.dialoge.formatierung.absatz_dialog import AbsatzDialog, werte_an_marke
        vorher = werte_an_marke(e)
        rtl = vorher["rtl"]
        d = AbsatzDialog(self, vorher)
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
        if ausfuehren(d):
            w = d.werte()
            if w["ebene"] != vorher["ebene"]:                       # die Gliederungsebene ist die Überschriftsebene des Absatzes
                e.apply_style("Standard" if not w["ebene"] else f"Überschrift {w['ebene']}")
            e.set_alignment({"mitte": Qt.AlignHCenter, "rechts": Qt.AlignRight, "block": Qt.AlignJustify}.get(w["ausr"], Qt.AlignLeft))
            e.set_page_break_before(w["umbruch"])
            e.set_absatzopt(w["opt"])
            e.set_indents(w["einzug"], w["rechts"], w["erste"])
            e.set_paragraph_spacing(w["vor"], w["nach"])
            e.set_line_height(w["zeilen_art"], w["zeilen"] if w["zeilen_art"] == "faktor" else w["zeilen_pt"])
            e.set_tabstopps(w["tabs"])
            if w["rtl"] != rtl:
                e.toggle_rtl()


    def tabstopp_dialog(self):
        e = self.current_editor()
        if not e:
            return
        from vcl.qt.widgets.dialoge.formatierung.absatz_dialog import werte_an_marke
        from vcl.qt.widgets.dialoge.dokument.tabstopp_dialog import TabstoppDialog
        d = TabstoppDialog(self, werte_an_marke(e)["tabs"])
        if d.exec():
            e.set_tabstopps(d.stopps())


    def _lesehilfe_auf(self, e):
        from vcl.qt.widgets.dialoge.lesen_hilfe.lesehilfe_dialog import PAPIERTOENE
        s = self.settings
        papier = AUGENSCHUTZ_PAPIER if self.befehle.an_augenschutz() else PAPIERTOENE.get(s.get("lesehilfe/papier", "Weiß"), Farbe.WEISS)
        e.set_lesehilfe(papier,
                        float(s.get("lesehilfe/buchstaben", 0)), float(s.get("lesehilfe/wort", 0)))
        e.set_zeilenluft(float(s.get("lesehilfe/zeilenluft", 1.0)))
        e.set_zeilenfokus(s.get_bool("lesehilfe/zeilenfokus", False))
        e.set_lesefokus({"etwas": 1.05, "deutlich": 1.10}.get(str(s.get("lesehilfe/groesser", "keine")), 1.0),
                        {"etwas": 0.62, "deutlich": 0.38}.get(str(s.get("lesehilfe/zurueck", "keine")), 1.0))
        e.setAcceptDrops(s.get_bool("bearbeiten/ziehen", True))          # Text mit der Maus verschieben
        self.silbenfarben_anwenden(e)
        self.versteckt_anwenden(e)


    def mini_zeigen(self, ed, pos, rechtsklick: bool = False, menue=None):
        from vcl.qt.widgets.bausteine.symbole.bauteile.mini_leiste import MiniLeiste
        if getattr(self, "_mini", None) is None:
            self._mini = MiniLeiste(self)
        if ed is None:
            self._mini.hide()
        else:
            self._mini.zeigen(ed, pos, rechtsklick, menue)


    def markup_neu(self) -> None:
        """Markup- und Sprechblasen-Einstellungen haben sich geändert: Seitenrand für Blasen und Auszeichnung neu aufbauen."""
        from writer.funktionen.ansicht import sprechblasen as SB
        for t in self._doc_tabs():
            t.editor.blasen_setzen(SB.konfig_lesen(self.settings), self.settings.get("kommentare/schrift", "mittel"))
            t.editor.viewport().update()


    def versteckt_anwenden(self, e=None):
        an = self.settings.get_bool("ui/versteckt_zeigen", False)
        for ed in ([e] if e is not None else [t.editor for t in self._doc_tabs()]):
            ed.set_versteckt_zeigen(an)


    def silbenfarben_anwenden(self, e=None):
        from writer.formatierungswerkzeuge.schrift import silbenfarben as W
        k = W.einstellung_lesen(self.settings)
        for ed in ([e] if e is not None else [t.editor for t in self._doc_tabs()]):
            ed.set_silbenfarben(k)
        if e is None:
            self.lesehilfe_geaendert.emit()


    def lineale_anwenden(self, tab=None):
        h = self.settings.get_bool("ansicht/lineal", False)
        v = self.settings.get_bool("ansicht/lineal_hoch", False)
        for t in ([tab] if tab is not None else self._doc_tabs()):
            t.zeige_lineale(h, v)
        self.band.aktualisieren(self.current_tab() is not None)


    def formatzeichen_anwenden(self, e=None):
        """Formatierungszeichen für Reiter: Absatzmarken und Leerzeichen/Tabstopps getrennt (Optionen ▸ Ansicht)."""
        alt = self.settings.get_bool("ui/steuerzeichen", False)            # früherer gemeinsamer Schalter
        absatz = self.settings.get_bool("ui/marken_absatz", alt)
        leer = self.settings.get_bool("ui/marken_leer", alt)
        self.marks_on = absatz or leer
        for ed in ([e] if e is not None else [t.editor for t in self._doc_tabs()]):
            ed.set_formatzeichen(absatz, leer)


    def marken_setzen(self, absatz: bool | None = None, leer: bool | None = None):
        """Absatzmarken und/oder Leerzeichen und Tabstopps ein- oder ausschalten (None = unverändert)."""
        alt = self.settings.get_bool("ui/steuerzeichen", False)
        a = self.settings.get_bool("ui/marken_absatz", alt) if absatz is None else absatz
        l = self.settings.get_bool("ui/marken_leer", alt) if leer is None else leer
        self.settings.set("ui/marken_absatz", a); self.settings.set("ui/marken_leer", l)
        self.settings.set("ui/steuerzeichen", a or l)
        self.formatzeichen_anwenden()
        if hasattr(self, "a_marks"):
            self.a_marks.blockSignals(True); self.a_marks.setChecked(a or l); self.a_marks.blockSignals(False)


    def ansicht_optionen_anwenden(self):
        """Statusleiste, QuickInfo, Bedienschrift, Symbolgröße — aus den Optionen."""
        self.statusBar().setVisible(self.settings.get_bool("ui/statusleiste", True))
        self.leisten_beschriften()
        app = QApplication.instance()
        if getattr(self, "_quickinfo", None) is None:
            self._quickinfo = _QuickInfo()
        self._quickinfo.an = self.settings.get_bool("ui/quickinfo", True)
        app.removeEventFilter(self._quickinfo)
        if not self._quickinfo.an:                    # nur solange QuickInfo aus ist, sonst prüft er jedes Ereignis des Programms
            app.installEventFilter(self._quickinfo)
        fam = self.settings.get("ui/bedienschrift", "")
        gr = self.settings.get_int("ui/bedienschrift_groesse", 0)
        prozent = self.settings.get_int("ui/bedien_prozent", 100)
        if getattr(self, "_app_font0", None) is None:
            self._app_font0 = QFont(app.font())                       # die Schrift des Systems, Grundlage für die Prozente
        f = QFont(self._app_font0)
        if fam:
            f.setFamily(fam)
        if gr:
            f.setPointSize(gr)
        elif prozent != 100:
            f.setPointSizeF(max(6.0, self._app_font0.pointSizeF() * prozent / 100))
        if f != app.font():
            app.setFont(f)
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        faktor = {"klein": 0.8, "mittel": 1.0, "gross": 1.3}.get(self.settings.get("ui/icongroesse", "mittel"), 1.0)
        if abs(symbole.FAKTOR - faktor) > 1e-6:
            symbole.FAKTOR = faktor
            symbole.leeren()
            symbole.alle_neu()
            self.neu_bauen_band()


    def lesehilfe_anwenden(self):
        for t in self._doc_tabs():
            self._lesehilfe_auf(t.editor)
        self.lesehilfe_geaendert.emit()


    def set_marken(self, an: bool):
        self.settings.set("ui/marken", an)
        for t in self._doc_tabs():
            t.editor.set_marken(an)


    def chat_oeffnen(self, vorlage: str):
        if not self.sidebar.isVisible():
            self.toggle_sidebar()
        self.sidebar.zeige_bereich(1)
        ch = getattr(self.sidebar, "chat", None)
        if ch is not None:
            ch.eingabe.setText(vorlage); ch.eingabe.setFocus()


    def vorlesen(self, ab_hier: bool):
        from writer.anbindung import vorlesen as v
        e = self.current_editor()
        if e is None:
            return
        c = e.textCursor()
        if c.hasSelection():
            text = v.vorlesetext(e.kennung, c.selectionStart(), c.selectionEnd())
        elif ab_hier:
            text = v.vorlesetext(e.kennung, c.position())
        else:
            text = v.vorlesetext(e.kennung)            # Bilder mit Beschreibung ansagen, dekorative überspringen
        try:
            ok = v.lies_vor(text, self.settings.get(v.einstellung_stimme(), ""), self.settings.get_int(v.einstellung_tempo(), 0))
        except v.Vorlesefehler as ex:
            QMessageBox.information(self, "Vorlesen", str(ex))
            return
        if ok:
            self.lbl_msg.setText("Vorlesen …")
        else:
            QMessageBox.information(self, "Vorlesen", "Es gibt nichts zum Vorlesen. Schreiben Sie etwas oder markieren Sie eine Stelle.")


    def stimme_waehlen(self):
        from writer.anbindung import vorlesen as v
        liste = v.stimmen()
        if not liste:
            QMessageBox.information(self, "Stimme", "Es ist keine Stimme eingerichtet. Siehe dokumentation/benutzerhandbuch/installation.md.")
            return
        from vcl.qt.widgets.dialoge.dokument.stimme_dialog import StimmeDialog
        d = StimmeDialog(self, liste, self.settings.get(v.einstellung_stimme(), ""), self.settings.get_int(v.einstellung_tempo(), 0),
                         v.tempo_grenzen())
        if d.exec():
            self.settings.set(v.einstellung_stimme(), d.stimme())
            self.settings.set(v.einstellung_tempo(), d.tempo())


    def _nav_aktion(self, name: str, b: dict):
        e = self.current_editor()
        if e is None:
            return
        if name == "kommentar_weg":
            e.kommentar_loeschen(int(b["wert"]))
        elif name == "aenderung_an":
            e.aenderung_annehmen(b, True)
        elif name == "aenderung_ab":
            e.aenderung_annehmen(b, False)
        elif name == "note_weg":
            e.note_loeschen(b["art"], b["id"])
        elif name == "note_bearbeiten":
            self.befehle.note_bearbeiten(b["art"], b["id"])
        self.navigation.aktualisieren()


    def zeige_navigation(self, tab: str):
        self.navigation.show()
        self.navigation.zeige_tab(tab)


    def autor_angaben(self) -> tuple[str, str]:
        name = self.settings.get("benutzer/name", "") or "Unbekannt"
        init = self.settings.get("benutzer/initialen", "") or "".join(w[0] for w in name.split()[:2]).upper()
        return name, init


    def toggle_navigation(self):
        if self.navigation.isVisible():
            self.navigation.hide()
        else:
            self.navigation.show()
            self.navigation.zeige_tab(self.navigation.zuletzt)


    def toggle_lesemodus(self):
        self.lesemodus = not self.lesemodus
        for w in (self.band, self.sidebar):
            w.setVisible(not self.lesemodus and (w is self.band or self.settings.get_bool("ui/seitenleiste", True)))
        for t in self._doc_tabs():
            t.editor.setReadOnly(self.lesemodus)
        self.lbl_msg.setText("Lesemodus — Tastenkürzel Strg+Umschalt+L oder Schreibhilfe ▸ Lesemodus beendet ihn."
                             if self.lesemodus else "")
        sb = self.statusBar()
        if hasattr(sb, "lesen_ende"):
            sb.lesen_ende.setVisible(self.lesemodus)
        if not hasattr(self, "_lese_ende"):
            from vcl.qt.widgets.bausteine.symbole.bauteile.lese_ende_knopf import LeseEndeKnopf
            self._lese_ende = LeseEndeKnopf(self, self.toggle_lesemodus)
        self._lese_ende.zeigen(self.lesemodus)
        self.ansicht_anzeigen()


    def set_theme(self, wahl: str):
        from vcl.qt.widgets.bausteine.farben.thema.thema import apply_theme
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        from vcl.qt.widgets.bausteine.farben.thema import thema
        self.settings.set("theme", wahl)
        thema.WEICH = self.settings.get_bool("ui/weich", False)
        QApplication.setOverrideCursor(Qt.WaitCursor)               # das Umstellen dauert einen Moment: Sanduhr statt scheinbarem Stillstand
        try:
            apply_theme(QApplication.instance(), wahl)
            symbole.leeren()
            symbole.alle_neu()                                        # Schienen, Schwebeknopf und Datei-Ansicht: Symbole in der neuen Farbe
            self.neu_bauen_band()
        finally:
            QApplication.restoreOverrideCursor()
        self.thema_anzeigen()


    def thema_ist_dunkel(self) -> bool:
        return QApplication.instance().palette().window().color().lightness() < 128


    def thema_wechseln(self):
        """Schneller Zugang zu Hell und Dunkel (Strg+Umschalt+D, Statusleiste, Ansicht-Menü): wechselt zum jeweils anderen."""
        self.set_theme("light" if self.thema_ist_dunkel() else "dark")


    def thema_anzeigen(self) -> None:
        sb = self.statusBar()
        if hasattr(sb, "thema_zeigen"):
            sb.thema_zeigen(self.thema_ist_dunkel())


    def _bereiche_bauen(self):
        self.sidebar.setze_bereiche()
        self.ki_schnell_zeigen()


    def _chat_knopf_pruefen(self, neu=None) -> None:
        """Der schwebende KI-Chat-Knopf ist weg, solange der Chat in der Seitenleiste offen ist – und solange derselbe Chat über das Chat-Symbol der
        Leiste rechts erreichbar ist (sonst stünde er doppelt da). Ohne diese Leiste bleibt er der Weg zum Chat."""
        offen = self.sidebar.isVisible() and self.sidebar.stapel.currentIndex() == 1
        in_leiste = getattr(self, "_rechts", {}).get("Chat")
        erreichbar = in_leiste is not None and not in_leiste.isHidden() and not in_leiste.parentWidget().isHidden()
        for t in (*self._doc_tabs(), *([neu] if neu is not None else ())):     # ``neu``: ein Reiter, der gerade erst angelegt wird
            k = getattr(t, "_chat_knopf", None)
            if k is not None:
                k.setVisible(not offen and not erreichbar)


    def ki_schnell_zeigen(self) -> None:
        """Die Schnellen KI-Aktionen mit Zugriff „Schnellzugriff“ in der Schnellzugriffsleiste zeigen."""
        if hasattr(self.band, "ki_schnell"):
            self.band.ki_schnell([a for a in self.ki.konfig.assistenten("aktion") if a.get("zugriff") == "schnell"], self.ki.assistent)


    # ==== Seite ==================================================================================
    def _page_change(self, fn):
        t = self.current_tab()
        if not t:
            return
        p = t.editor.abschnitt_seite(); fn(p); t.editor.page_settings_changed(p)


    def set_margins(self, top, bottom, left, right):
        def f(p):
            p.margin_top_mm, p.margin_bottom_mm, p.margin_left_mm, p.margin_right_mm = top, bottom, left, right
        self._page_change(f)


    def set_orientation(self, landscape: bool):
        self._page_change(lambda p: p.set_orientation(landscape))


    def set_paper(self, name: str):
        self._page_change(lambda p: p.set_paper(name))


    def page_setup(self):
        t = self.current_tab()
        if not t:
            return
        d = PageSetupDialog(t.editor.abschnitt_seite(), self)
        if d.exec():
            t.editor.page_settings_changed(d.result_page())
