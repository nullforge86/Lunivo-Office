"""Frei positionierte Bilder im Editor: die Schaltflächen neben dem gewählten Objekt und ihre Menüs — Layoutoptionen, Formstile, Füllung, Kontur,
Absatz-Symbol, Lupe/Zuschneiden, Diagramm- und SmartArt-Knöpfe. Lage und Aussehen der Knöpfe stehen in ``freie_bilder_zeichnen.py``, der Klick
darauf in ``freie_bilder_interaktion.py``; die Menüs selbst sind Bausteine unter ``ui/baukasten/dropdown/objektmenues/``. Zusammengesetzt wird in
``freie_bilder_bedienung.py`` (``FreieBilderMixin``).
"""
from __future__ import annotations

from PySide6.QtGui import QColor, QTextCursor

from lunivo_writer.core.farben import Farbe
from lunivo_writer.editor.dokument.zusatz import B_BILDANKER


class FreieBilderKnoepfeMixin:
    def _frei_knopf(self, name: str, pos) -> None:
        if name == "anker":
            self._frei_anker_menue(pos)
        elif name == "minus":
            self._frei_knoepfe_offen = not getattr(self, "_frei_knoepfe_offen", True)
            self.viewport().update()
        elif name == "layout":
            self._frei_layout_popup(pos)
        elif name == "zahnrad":
            self._frei_formatierung()
        elif name in ("lupe", "zuschnitt", "dg_element", "dg_stile", "dg_filter") or name.startswith("sa_"):
            self._frei_befehl_knopf(name, pos)
        elif name == "formstile":
            self._frei_formstile(pos)
        elif name == "fuell":
            self._frei_fuell(pos)
        elif name == "kontur":
            self._frei_kontur(pos)

    def _frei_befehl_knopf(self, name: str, pos) -> None:
        """Bild: Vergrößern (Ansicht mit Zoom) und Zuschneiden; Diagramm: Elemente, Stile, Einstellungen (Datenfenster) — jeweils der Befehl des Bandes."""
        b = getattr(self.window(), "befehle", None)
        if b is None:
            return
        if name == "lupe":
            b.bildVergroessern()
        elif name == "zuschnitt":
            from lunivo_writer.ui.baukasten.dropdown.objektmenues.bild_diagramm_menues import zuschneiden_menue
            if not b.an_bildZuschneidenModus():                    # Klick schaltet den Zuschneiden-Modus ein und öffnet die Klappe
                b.bildZuschneidenModus()
            m = zuschneiden_menue(b)
            m.popup(pos); self._frei_menue = m
        elif name == "sa_bullet":
            b.smartartAufzaehlung(); self.viewport().update()
        else:
            from lunivo_writer.ui.baukasten.dropdown.objektmenues import diagramm_popups as DP
            from lunivo_writer.ui.baukasten.dropdown.objektmenues import smartart_menues as SM
            bau = {"dg_element": DP.elemente_popup, "dg_stile": DP.stile_popup, "dg_filter": DP.filter_popup, "sa_form": SM.form_menue,
                   "sa_layout": lambda bb: SM.hierarchie_menue(bb, True), "sa_level": SM.level_menue, "sa_stil": SM.stile_menue}[name]
            m = bau(b)
            m.popup(pos); self._frei_menue = m

    def _frei_anker_menue(self, pos) -> None:
        """Menü des Absatz-Symbols links vom Rahmen: Absatzformat zurücksetzen, Symbol ausblenden."""
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe(self)
        m.eintrag("Absatzformat zurücksetzen", self._frei_absatz_zuruecksetzen)
        m.eintrag("Symbol vom Absatz-Layout ausblenden", self._frei_anker_ausblenden)
        m.popup(pos); self._frei_menue = m

    def _frei_anker_ausblenden(self) -> None:
        self._frei_anker_zeigen = False
        self.viewport().update()

    def _frei_absatz_zuruecksetzen(self) -> None:
        """Der Absatz, an dem das Objekt hängt, bekommt Ausrichtung, Einzüge und Abstände zurück (das Objekt bleibt)."""
        sel = self._frei_sel
        if sel is None or sel[0] != "t":
            return
        b = self.document().findBlockByNumber(sel[1])
        if not b.isValid():
            return
        from PySide6.QtGui import QTextBlockFormat
        alt = b.blockFormat(); neu = QTextBlockFormat()
        if alt.hasProperty(B_BILDANKER):
            neu.setProperty(B_BILDANKER, alt.stringProperty(B_BILDANKER))
        QTextCursor(b).setBlockFormat(neu)
        self.document().setModified(True); self._frei_rev = None; self.viewport().update()

    def _frei_wirken(self, **teile) -> None:
        from lunivo_writer.editor.objekte import bildlayout as BL
        BL.format_setzen(self, BL.ziel(self), **teile)

    def _frei_formstile(self, pos) -> None:
        m = self.frei_formstile_menue(self)
        m.popup(pos); self._frei_menue = m

    def frei_formstile_menue(self, parent=None, ed=None):
        E = ed or (lambda: self)                               # der Editor, auf den die Wahl wirkt (zur Wahlzeit, nicht zur Bauzeit)
        from lunivo_writer.ui.baukasten.dropdown.objektmenues.objekt_menues import formstil_werte, formstile
        m = formstile(parent)
        def waehlen(k: str) -> None:
            ed = E()
            from lunivo_writer.editor.objekte import frei_objekt as FO
            if FO.art_gewaehlt(ed) == "form" and hasattr(ed.window(), "befehle"):        # Form: Füllung, Verlauf, Linie und Effekt des Rasters (formStilRaster)
                ed.window().befehle.formStilRaster(None, int(k[1]), int(k[2]))
            else:                                                                           # Bild, Textfeld, WordArt: Füllung und Rand
                w = formstil_werte(k)
                ed._frei_wirken(fuell=w["fuell"], rand=w["rand"])
            m.close()
        m.gewaehlt.connect(waehlen)
        m.fuss("Weitere Effekte(O)…", lambda: E()._frei_effekte())
        return m

    def _frei_formatierung(self, reiter: int = 0) -> None:
        """Zahnrad am Diagramm und Rechtsklick „Formatieren“: die Seitenleiste „Formatierung“ für das gewählte Objekt (Diagramm, SmartArt, Form, Bild …)."""
        fenster = self.window()
        if hasattr(fenster, "formatierung_seitenleiste"):
            fenster.formatierung_seitenleiste(reiter)

    def _frei_effekte(self) -> None:
        """„Weitere Effekte …“: die Seitenleiste „Formatierung“ mit den Effekten."""
        fenster = self.window()
        if hasattr(fenster, "objektformat_seitenleiste"):
            fenster.objektformat_seitenleiste(1)

    def _frei_fuell(self, pos) -> None:
        m = self.frei_fuell_menue(self)
        m.popup(pos); self._frei_menue = m

    def frei_fuell_menue(self, parent=None, ed=None):
        E = ed or (lambda: self)                               # der Editor, auf den die Wahl wirkt (zur Wahlzeit, nicht zur Bauzeit)
        from lunivo_writer.ui.baukasten.dokument.speichern_fenster import Dateifenster
        from PySide6.QtGui import QImage
        from lunivo_writer.editor.objekte import bildlayout as BL
        from lunivo_writer.ui.baukasten.dropdown.objektmenues.objekt_menues import FuellMenue
        m = FuellMenue(parent)
        m.gewaehlt.connect(lambda c: E()._frei_wirken(fuell=None if c is None else {"art": "farbe", "farbe": c.name(QColor.HexArgb)}))
        m.verlauf_gewaehlt.connect(lambda c: E()._frei_wirken(fuell={"art": "verlauf", "farbe": c.name(QColor.HexArgb)}))
        m.graduell_gewaehlt.connect(lambda d, h: E()._frei_wirken(fuell={"art": "graduell", "dunkel": d, "hell": h, "farbe": d}))
        m.muster_gewaehlt.connect(lambda k: E()._frei_wirken(fuell={"art": "muster", "key": k, "farbe": Farbe.TINTE, "grund": Farbe.WEISS}))
        m.textur_gewaehlt.connect(lambda k: E()._frei_wirken(fuell={"art": "textur", "key": k}))

        def bild():
            pfad, _ = Dateifenster.getOpenFileName(E().window(), "Bild als Füllung", "", "Bilder (*.png *.jpg *.jpeg *.bmp *.gif)")
            if pfad:
                BL.fuellbild_setzen(E(), BL.ziel(E()), QImage(pfad))
        m.bild_gewaehlt.connect(bild)
        m.weitere_fuellung.connect(lambda art: E()._frei_fuell_fenster(art))
        return m

    def _frei_fuell_fenster(self, art: str) -> None:
        """„Fülleffekte“, „Weitere Farbverläufe/Texturen/Muster“: die Seitenleiste „Formatierung“ auf „Füllung und Linie“ mit dieser Füllungsart."""
        fenster = self.window()
        if hasattr(fenster, "objektformat_seitenleiste"):
            fenster.objektformat_seitenleiste(0, art)

    def _frei_kontur(self, pos) -> None:
        m = self.frei_kontur_menue(self)
        m.popup(pos); self._frei_menue = m

    def frei_kontur_menue(self, parent=None, ed=None):
        E = ed or (lambda: self)                               # der Editor, auf den die Wahl wirkt (zur Wahlzeit, nicht zur Bauzeit)
        from lunivo_writer.ui.baukasten.dropdown.objektmenues.objekt_menues import KonturMenue
        m = KonturMenue(parent)
        m.gewaehlt.connect(lambda c: E()._frei_wirken(rand=None) if c is None else E()._frei_wirken(rand_teil={"farbe": c.name(QColor.HexArgb)}))
        m.breite_gewaehlt.connect(lambda pt: E()._frei_wirken(rand_teil={"b": pt * 96 / 72}))
        m.strich_gewaehlt.connect(lambda a: E()._frei_wirken(rand_teil={"art": a}))
        m.weitere_linien.connect(lambda: E()._frei_linien_fenster())
        return m

    def _frei_linien_fenster(self) -> None:
        """„Weitere Linien …“: die Seitenleiste „Formatierung“ auf dem Reiter „Füllung und Linie“ (Farbe, Breite, Strichart)."""
        fenster = self.window()
        if hasattr(fenster, "objektformat_seitenleiste"):
            fenster.objektformat_seitenleiste(0)

    # ---- Layout: Popup neben dem Bild und das Fenster ---------------------------------------------------------------------------
    def bild_layout_popup(self, global_pos) -> None:
        self._frei_layout_popup(global_pos)

    def _frei_layout_popup(self, global_pos) -> None:
        from lunivo_writer.editor.objekte import bildlayout as BL
        from lunivo_writer.ui.baukasten.dropdown.objektmenues.layout_optionen_objekt import LayoutOptionenObjekt
        z = BL.ziel(self)
        if z is None:
            return
        w = BL.lesen(self, z)
        p = LayoutOptionenObjekt(self, w["umbruch"], w.get("verschieben_wahl", "mit_text" if w.get("mit_text") else "fest") == "mit_text")
        p.verschieben_wahl = w.get("verschieben_wahl")               # None (SmartArt): beide Radios leer – die Oberfläche greift das auf
        p.gewaehlt.connect(lambda art: BL.anwenden(self, BL.ziel(self), {"umbruch": art}) if BL.ziel(self) else None)
        p.verschieben.connect(lambda an: BL.anwenden(self, BL.ziel(self), {"mit_text": bool(an)}) if BL.ziel(self) else None)
        p.mehr.connect(self.bild_layout_dialog)
        p.zeigen_bei(global_pos)
        self._frei_popup = p

    def bild_layout_dialog(self) -> None:
        """Das Fenster „Layout“ für das markierte Bild (frei oder im Text)."""
        from lunivo_writer.editor.objekte import bildlayout as BL
        from lunivo_writer.ui.baukasten.dokument.layout_dialog_objekt import layout_dialog_fuer
        z = BL.ziel(self)
        if z is None:
            return
        d = layout_dialog_fuer(z[2].get("art") if z[0] == "frei" else None)(self.window(), BL.lesen(self, z))
        if d.exec():
            z = BL.ziel(self)
            if z is not None:
                BL.anwenden(self, z, d.werte())
