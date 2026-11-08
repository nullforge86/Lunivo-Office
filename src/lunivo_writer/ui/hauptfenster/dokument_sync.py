"""Synchronisierung zwischen aktivem Dokument, Ribbon und Statusleiste."""
from __future__ import annotations

from PySide6.QtGui import QFont


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
        bf = e.bild_format() if e else None
        from lunivo_writer.editor import formen
        art = (formen.objekt(bf) or {}).get("art") if bf is not None else None
        from lunivo_writer.editor import frei_objekt as FO
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
        self._zeichen_masse(e)
        self._tabelle_masse(e)
        f = self.band.felder
        if e is None or not f:
            return
        cf = e.textCursor().charFormat()
        fam = cf.fontFamilies()[0] if cf.fontFamilies() else e.document().defaultFont().family()
        f["font"].blockSignals(True); f["font"].setCurrentFont(QFont(fam)); f["font"].blockSignals(False)
        size = cf.fontPointSize() or e.document().defaultFont().pointSizeF() or 11
        f["groesse"].blockSignals(True); f["groesse"].setEditText(f"{size:g}"); f["groesse"].blockSignals(False)
        t = self.current_tab()
        if t is not None and "rand_oben" in f:                       # Maßfelder im Reiter Seitenlayout
            p = t.page
            for schl, wert in (("oben", p.margin_top_mm), ("unten", p.margin_bottom_mm), ("links", p.margin_left_mm), ("rechts", p.margin_right_mm)):
                sp = f["rand_" + schl]
                if not sp.hasFocus():
                    sp.blockSignals(True); sp.setValue(wert); sp.blockSignals(False)
        if "tt_font" in f and text_art:                              # Schrift und Größe des markierten WordArt/Textfelds
            d = FO.ziel(e)[1]
            f["tt_font"].blockSignals(True); f["tt_font"].setCurrentFont(QFont(d.get("schrift", "Liberation Sans"))); f["tt_font"].blockSignals(False)
            if not f["tt_groesse"].hasFocus():
                f["tt_groesse"].blockSignals(True); f["tt_groesse"].setEditText(f"{float(d.get('pt', 36 if text_art == 'wordart' else 11)):g}"); f["tt_groesse"].blockSignals(False)
        if "tab_font" in f and e.textCursor().currentTable() is not None:       # Schrift und Größe der Tabellentools
            f["tab_font"].blockSignals(True); f["tab_font"].setCurrentFont(QFont(fam)); f["tab_font"].blockSignals(False)
            if not f["tab_groesse"].hasFocus():
                f["tab_groesse"].blockSignals(True); f["tab_groesse"].setEditText(f"{size:g}"); f["tab_groesse"].blockSignals(False)
        st = e.current_style()
        f["stil"].blockSignals(True); f["stil"].setCurrentText("Fließtext" if st == "Standard" else st); f["stil"].blockSignals(False)

    def _sync_status(self):
        e = self.current_editor()
        if e is None:
            self.statusleiste.seite(None, None); self.statusleiste.zaehler(0, 0)
            return
        txt = e.document().toPlainText()
        self.statusleiste.seite(e.current_page(), e.page_count)
        self.statusleiste.zaehler(len(txt.split()), len(txt))
