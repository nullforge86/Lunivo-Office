"""Synchronisierung zwischen aktivem Dokument, Ribbon und Statusleiste."""
from __future__ import annotations

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

    def _sync_later(self):
        self._sync_timer.start()

    def _sync_format(self):
        e = self.current_editor()
        self.band.aktualisieren(e is not None)
        self.band.kontext("tabelle", bool(e) and not e.isReadOnly() and e.textCursor().currentTable() is not None)
        text_art = self._sync_kontexte(e)
        self._zeichen_masse(e)
        self._tabelle_masse(e)
        f = self.band.felder
        if e is None or not f:
            return
        cf = e.textCursor().charFormat()
        fam = cf.fontFamilies()[0] if cf.fontFamilies() else e.document().defaultFont().family()
        font_feld = f.get("font")
        if font_feld is not None:
            _feld_setzen(font_feld, "setCurrentFont", QFont(fam))
        size = cf.fontPointSize() or e.document().defaultFont().pointSizeF() or 11
        groesse_feld = f.get("groesse")
        if groesse_feld is not None:
            _feld_setzen(groesse_feld, "setEditText", f"{size:g}")
        self._sync_seitenmasse(f)
        if "tt_font" in f and text_art:                              # Schrift und Größe des markierten WordArt/Textfelds
            from lunivo_writer.editor.objekte import frei_objekt as FO
            d = FO.ziel(e)[1]
            _feld_setzen(f["tt_font"], "setCurrentFont", QFont(d.get("schrift", "Liberation Sans")))
            if not f["tt_groesse"].hasFocus():
                _feld_setzen(f["tt_groesse"], "setEditText", f"{float(d.get('pt', 36 if text_art == 'wordart' else 11)):g}")
        if e.textCursor().currentTable() is not None and "tab_font" in f:       # Schrift und Größe der Tabellentools
            _feld_setzen(f["tab_font"], "setCurrentFont", QFont(fam))
            if not f["tab_groesse"].hasFocus():
                _feld_setzen(f["tab_groesse"], "setEditText", f"{size:g}")
        st = e.current_style()
        stil_feld = f.get("stil")
        if stil_feld is not None:
            _feld_setzen(stil_feld, "setCurrentText", "Fließtext" if st == "Standard" else st)

    def _sync_kontexte(self, e):
        """Schaltet die Kontext-Reiter nach dem gewählten Objekt. → Art des Textobjekts (WordArt, Textfeld) oder None."""
        bf = e.bild_format() if e else None
        from lunivo_writer.editor.objekte import formen
        art = (formen.objekt(bf) or {}).get("art") if bf is not None else None
        from lunivo_writer.editor.objekte import frei_objekt as FO
        frei_art = FO.art_gewaehlt(e) if e else None                  # WordArt, Textfeld, Form, Diagramm oder SmartArt als freies Objekt gewählt
        text_art = frei_art if frei_art in FO.TEXT_ARTEN else None
        if frei_art:
            art, bf = frei_art, True
        frei_bild = bool(e) and getattr(e, "_frei_sel", None) is not None and frei_art in (None, "piktogramm")   # Bild, Bildschirmfoto, Piktogramm
        self.band.kontext("bild", frei_bild or (bf is not None and art not in ("form", "gruppe", "smartart", "wordart", "textfeld", "diagramm", "piktogramm", "zeichenbereich")))
        self.band.kontext("form", art in ("form", "gruppe"))
        self.band.kontext("smartart", art == "smartart")
        self.band.kontext("zeichen", bool(e) and getattr(e, "_frei_sel", None) is not None)
        self.band.kontext("text", text_art is not None)             # Texttools: nur WordArt und Textfeld (die Vorlage zeigt dazu auch Zeichentools)
        self.band.kontext("diagramm", frei_art == "diagramm")       # Diagrammtools (der Reiter selbst kommt aus der Reiter-Definition)
        frei_wahl = frei_art or ("bild" if frei_bild else None)
        if frei_wahl != getattr(self, "_frei_art_alt", None):         # neu gewählt: WordArt öffnet Texttools, SmartArt/Diagramm/Bild ihre Tools, sonst Zeichentools
            self._frei_art_alt = frei_wahl
            if frei_wahl:
                ziel_reiter = {"wordart": "text", "smartart": "smartart", "diagramm": "diagramm", "piktogramm": "bild", "bild": "bild"}.get(frei_wahl, "zeichen")
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
        if zw is None or zw[0] is not doc or zw[1] != doc.revision():
            txt = doc.toPlainText()
            zw = e._zaehler_zw = (doc, doc.revision(), len(txt.split()), len(txt))
        self.statusleiste.zaehler(zw[2], zw[3])
