"""Synchronisierung zwischen aktivem Dokument, Ribbon und Statusleiste."""
from __future__ import annotations
from writer.funktionen import bearbeiten as _bearbeiten

from PySide6.QtGui import QFont


def _feld_setzen(feld, setter: str, wert) -> None:
    """Setzt den Wert eines Feldes, ohne dessen Signale auszulösen."""
    feld.blockSignals(True); getattr(feld, setter)(wert); feld.blockSignals(False)


class DokumentSyncMixin:
    """Hält UI-Felder und Statusanzeige mit dem aktiven Dokument synchron."""

    def _regler_bewegt(self, v: int):
        e = self.current_editor()
        if e and abs(e.zoom * 100 - v) > 0.5:
            e.set_zoom(v / 100)

    def _zoom_anzeigen(self, f: float | None = None):
        e = self.current_editor()
        f = f if f is not None else (e.zoom if e else 1.0)
        self.statusleiste.zoom_zeigen(f)

    def _ansicht_gewaehlt(self, art: str):
        """Ansichtswahl der Statusleiste: Befehl ausführen und anzeigen, was danach gilt (auch wenn sich nichts ändern ließ)."""
        self.befehle.ansichtWaehlen(art=art)
        self.ansicht_anzeigen()

    def ansicht_anzeigen(self):
        """Dokumentansicht, Vollbild und Augenschutz an den Knöpfen der Statusleiste zeigen."""
        self.statusleiste.ansicht_zeigen(self.befehle.ansichtJetzt(), self.isFullScreen(), self.befehle.an_augenschutz())

    def _sync_later(self):
        self._sync_timer.start()

    def _sync_format(self):
        self.ansicht_anzeigen()
        e = self.current_editor()
        self.band.aktualisieren(e is not None)
        self.band.kontext("tabelle", bool(e) and not e.isReadOnly() and e.textCursor().currentTable() is not None)
        text_art = self._sync_kontexte(e)
        self._zeichen_masse(e)
        self._tabelle_masse(e)
        f = self.band.felder
        if e is None or not f:
            return
        from writer.anbindung.formatwerte import schrift as schrift_von
        z = e.zeichenformat()
        fam = schrift_von(z).family if z.get("schrift") else e.document().defaultFont().family()
        font_feld = f.get("font")
        if font_feld is not None:
            _feld_setzen(font_feld, "setCurrentFont", QFont(fam))
        size = z.get("groesse_pt") or e.document().defaultFont().pointSizeF() or 11
        groesse_feld = f.get("groesse")
        if groesse_feld is not None:
            _feld_setzen(groesse_feld, "setEditText", f"{size:g}")
        self._sync_seitenmasse(f)
        if "tt_font" in f and text_art:                              # Schrift und Größe des markierten WordArt/Textfelds
            d = _bearbeiten.dok_objekt(e.kennung, e.ansicht.gewaehltes_objekt).daten
            _feld_setzen(f["tt_font"], "setCurrentFont", QFont(d.get("schrift", "Liberation Sans")))
            if not f["tt_groesse"].hasFocus():
                _feld_setzen(f["tt_groesse"], "setEditText", f"{float(d.get('pt', 36 if text_art == 'wordart' else 11)):g}")
        st = e.current_style()
        stil_feld = f.get("stil")
        if stil_feld is not None:
            _feld_setzen(stil_feld, "setCurrentText", "Fließtext" if st == "Standard" else st)

    def _sync_kontexte(self, e):
        """Schaltet die Kontext-Reiter nach dem gewählten Objekt. → Art des Textobjekts (WordArt, Textfeld) oder None."""
        art = e.objekt_art() if e else None                          # Art des gewählten frei positionierten Objekts
        text_art = art if art in ("wordart", "textfeld") else None
        frei_bild = art in ("bild", "piktogramm")
        self.band.kontext("bild", frei_bild)
        self.band.kontext("smartart", art == "smartart")
        self.band.kontext("zeichen", art is not None and not frei_bild)
        self.band.kontext("text", text_art is not None)             # Texttools: nur WordArt und Textfeld
        self.band.kontext("diagramm", art == "diagramm")
        if art != getattr(self, "_frei_art_alt", None):               # neu gewählt: das passende Werkzeug öffnen
            self._frei_art_alt = art
            if art:
                ziel_reiter = {"wordart": "text", "smartart": "smartart", "diagramm": "diagramm", "piktogramm": "bild", "bild": "bild"}.get(art, "zeichen")
                self.band.kontext(ziel_reiter, True, aktivieren=True)
        return text_art

    def _sync_seitenmasse(self, f: dict) -> None:
        """Maßfelder im Reiter Seitenlayout."""
        t = self.current_tab()
        if t is None or not dict.__contains__(f, "rand_oben"):
            return
        p = t.page
        for schl, wert in (("oben", p.margin_top_mm), ("unten", p.margin_bottom_mm), ("links", p.margin_left_mm), ("rechts", p.margin_right_mm)):
            sp = f["rand_" + schl]
            if not sp.hasFocus():
                _feld_setzen(sp, "setValue", wert)

    def _sync_status(self):
        e = self.current_editor()
        if e is None:
            self.statusleiste.seite(None, None); self.statusleiste.zaehler(0, 0)
            return
        self.statusleiste.seite(e.current_page(), e.page_count)
        doc = e.document()
        zw = getattr(e, "_zaehler_zw", None)             # Wörter zählen kopiert das ganze Dokument: je Revision einmal, nicht bei jeder Bewegung der Schreibmarke
        if zw is None or zw[0] != doc.revision():
            txt = doc.toPlainText()
            zw = e._zaehler_zw = (doc.revision(), len(txt.split()), len(txt))
        self.statusleiste.zaehler(zw[1], zw[2])
