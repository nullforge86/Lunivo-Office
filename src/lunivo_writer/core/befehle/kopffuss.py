"""Befehle: Kontext-Reiter „Kopf- und Fußzeile“ (Bearbeiten direkt auf der Seite, siehe ``ui/document/kopffuss_bearbeiter.py``)."""
from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QVBoxLayout

from lunivo_writer.ui.baukasten.menue_liste import MenueListe

AUSRICHTUNGEN = (("Links", "left"), ("Zentriert", "center"), ("Rechts", "right"), ("Außen", "aussen"), ("Innen", "innen"))


class KopfFussBefehle:
    """Befehle des Bandes: Kopf- und Fußzeile. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""

    def _kf(self):
        """Der Bearbeiter des aktuellen Editors, nur wenn er gerade bearbeitet."""
        e = self.ed
        b = e.kopffuss() if e is not None else None
        return b if b is not None and b.aktiv else None


    def _kf_start(self, zone: str):
        t = self.w.current_tab()
        if t:
            self.w.kopffuss_starten(t.editor, zone == "kopf")


    # ---- Klappen ----------------------------------------------------------------------------------------------------
    def menue_kfGruppeKlappe(self):
        m = MenueListe()
        m.eintrag("Kopfzeile bearbeiten", lambda: self._kf_start("kopf"))
        m.eintrag("Fußzeile bearbeiten", lambda: self._kf_start("fuss"))
        m.eintrag("Zwischen Kopf- und Fußzeile wechseln", self.kfWechseln, aktiv=self._kf() is not None)
        return m


    def _hf_klappe(self, zone: str):
        b = self._kf()
        m = MenueListe()
        feld = "header" if zone == "kopf" else "footer"
        name = "Kopfzeile" if zone == "kopf" else "Fußzeile"
        m.eintrag(name + " bearbeiten", lambda: self._kf_start(zone))
        m.trenner()
        for text, ausr in AUSRICHTUNGEN:
            m.eintrag(text, lambda a=ausr: self._kf_ausrichten(zone, a))
        m.trenner()
        m.eintrag(name + " entfernen", lambda: self._kf_leeren((feld,)))
        return m


    def menue_kopfzeileKlappe(self): return self._hf_klappe("kopf")

    def menue_fusszeileKlappe(self): return self._hf_klappe("fuss")


    def menue_kopfLinieKlappe(self):
        m = MenueListe()
        m.eintrag("Kopfzeile entfernen", lambda: self._kf_leeren(("header",)))
        m.eintrag("Fußzeile entfernen", lambda: self._kf_leeren(("footer",)))
        m.eintrag("Kopf- und Fußzeile entfernen", lambda: self._kf_leeren(("header", "footer", "first_header", "first_footer", "even_header", "even_footer")))
        return m


    def menue_kfEinstellungenKlappe(self):
        m = MenueListe()
        m.eintrag("Optionen für Kopf- und Fußzeile …", self.kfOptionen)
        m.eintrag("Seite einrichten …", self.papierformatFenster)
        m.trenner()
        m.eintrag("Kopf- und Fußzeile schließen", self.kopfFussSchliessen)
        return m


    def _kf_ausrichten(self, zone: str, ausr: str):
        b = self._kf()
        if b is None:
            self._kf_start(zone)
            b = self._kf()
        if b is not None:
            if b.zone != zone:
                b.starte(zone, b.blatt)
            b.ausrichtung_setzen(ausr)


    def _kf_leeren(self, felder: tuple):
        from lunivo_writer.models.page import HeaderFooter
        e = self.ed
        if e is None:
            return
        b = self._kf()
        if b is not None:
            b.speichern()
        pg = e.abschnitt_seite()
        for f in felder:
            setattr(pg, f, HeaderFooter("", getattr(pg, f).align))
        e.page_settings_changed(pg)
        if b is not None:
            b._laden()


    # ---- Knöpfe -----------------------------------------------------------------------------------------------------
    def kopfFussSchliessen(self, k=None):
        b = self._kf()
        if b is not None:
            b.beende()


    def kfWechseln(self, k=None):
        b = self._kf()
        if b is not None:
            b.wechseln()


    def kfVorige(self, k=None):
        b = self._kf()
        if b is not None and not b.abschnitt_springen(-1):
            self.w.statusBar().showMessage("Es gibt keine vorige Kopfzeile.", 4000)


    def kfNaechste(self, k=None):
        b = self._kf()
        if b is not None and not b.abschnitt_springen(1):
            self.w.statusBar().showMessage("Es gibt keine nächste Kopfzeile.", 4000)


    def kfVerknuepfen(self, k=None):
        b = self._kf()
        if b is None:
            return
        (self.kopfVerknuepfen if b.zone == "kopf" else self.fussVerknuepfen)()
        b._laden()


    def kann_kfVerknuepfen(self):
        """Grau auf der ersten Seite/im ersten Abschnitt: dort gibt es keinen Vorgänger."""
        b = self._kf()
        return b is not None and self.ed.abschnitt_nr() > 0


    def an_kfVerknuepfen(self):
        b = self._kf()
        return bool(b is not None and self._kopf_link("kopf" if b.zone == "kopf" else "fuss"))


    def kfTabstopp(self, k=None):
        b = self._kf()
        if b is not None:
            b.tabstopp_einfuegen()


    def kfOptionen(self, k=None):
        """Seitenleistenfenster: Erste Seite anders; Gerade und ungerade Seiten unterschiedlich."""
        from lunivo_writer.ui.baukasten.dialog_rahmen import fussleiste
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.zusatz_panel import PanelFaehig
        from PySide6.QtWidgets import QDialog
        t = self.w.current_tab()
        if not t:
            return
        pg = t.editor.abschnitt_seite()

        class Fenster(PanelFaehig, QDialog):
            pass
        d = Fenster(self.w)
        d.setWindowTitle("Optionen für Kopf- und Fußzeile")
        v = QVBoxLayout(d)
        erste = QCheckBox("Erste Seite anders"); erste.setChecked(pg.diff_first)
        gu = QCheckBox("Gerade und ungerade Seiten sind unterschiedlich"); gu.setChecked(pg.diff_even)
        v.addWidget(erste); v.addWidget(gu); v.addStretch(1)
        fussleiste(d, v)
        if ausfuehren(d):
            if erste.isChecked() != pg.diff_first:
                self.ersteSeiteAnders()
            if gu.isChecked() != pg.diff_even:
                self.geradeUngerade()
            b = self._kf()
            if b is not None:
                b._laden()


    # ---- Felder: Abstand des Kopf-/Fußbereichs ---------------------------------------------------------------------
    # Lunivo zeichnet Kopf und Fuß fest 8 mm vom Blattrand (editor_anzeige.py / pagination.py); das gilt, solange kein Abstand gesetzt ist.
    WIRKSAMER_ABSTAND_MM = 8.0

    def _kf_abstand(self, attr: str, name: str, symbol: str):
        from PySide6.QtCore import QLocale, QSize
        from PySide6.QtWidgets import QHBoxLayout, QLabel, QToolButton, QWidget
        from lunivo_writer.ui.widgets import icons
        from lunivo_writer.ui.baukasten.schiebe_feld import SchrittFeld
        class _Zeile(QWidget):
            neu_laden = None

            def showEvent(self, ev):                       # beim Einblenden den aktuellen Wert des Abschnitts holen
                if self.neu_laden:
                    self.neu_laden()
                super().showEvent(ev)
        host = _Zeile(); h = QHBoxLayout(host); h.setContentsMargins(0, 0, 0, 0); h.setSpacing(3)
        bild = QLabel(); bild.setPixmap(icons.icon(symbol, 16).pixmap(QSize(16, 16))); h.addWidget(bild)
        h.addWidget(QLabel(name + ":"))
        f = SchrittFeld(0.0, 100.0, " mm", 0.5, 1)
        f.feld.setLocale(QLocale(QLocale.German, QLocale.Germany)); f.feld.setButtonSymbols(f.feld.ButtonSymbols.UpDownArrows); f.feld.setMinimumWidth(72)   # „NoButtons“ lässt im Thema kein Textfeld übrig
        f.feld.setStyleSheet("QDoubleSpinBox { padding: 0px 3px; } QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0px; border: none; }")
        f.feld.setAccessibleName(name); f.setToolTip(name)
        for k in f.findChildren(QToolButton):
            k.setFixedSize(22, 22)
        f.feld.setFixedHeight(22)
        h.addWidget(f)

        def laden():
            e = self.ed
            if e is not None:
                wert = float(getattr(e.abschnitt_seite(), attr) or 0.0)
                f.feld.blockSignals(True); f.setValue(wert if wert > 0 else self.WIRKSAMER_ABSTAND_MM); f.feld.blockSignals(False)

        def setzen(wert):
            e = self.ed
            if e is not None:
                pg = e.abschnitt_seite(); setattr(pg, attr, float(wert)); e.page_settings_changed(pg)
        laden(); host.neu_laden = laden
        f.valueChanged.connect(setzen)
        host.feld = f
        return host


    def feld_kopfHoehe(self): return self._kf_abstand("kopf_abstand_mm", "Kopfzeilenhöhe", "kopfz")

    def feld_fussHoehe(self): return self._kf_abstand("fuss_abstand_mm", "Fußzeilenhöhe", "fussz")
