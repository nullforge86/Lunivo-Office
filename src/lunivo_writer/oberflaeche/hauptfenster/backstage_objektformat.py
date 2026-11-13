"""Objektformatierung in der Backstage-Seitenleiste."""
from __future__ import annotations


class BackstageObjektformatBaustein:
    """Formatierungsseitenleisten für Bilder, SmartArt, Diagramme und weitere Objekte."""

    def _seitenleiste_oeffnen(self) -> None:
        """Gemeinsam für alle Bereiche „Formatierung“: die Seitenleiste einblenden, falls sie zu ist."""
        if self.sidebar.isHidden():
            self.toggle_sidebar()


    def objektformat_seitenleiste(self, reiter: int = 0, fuellung: str | None = None) -> None:
        """Den Bereich „Formatierung“ für das markierte Bild in der Seitenleiste öffnen (Füllung und Linie, Effekte); Änderungen gelten sofort."""
        from PySide6.QtGui import QImage
        from lunivo_writer.oberflaeche.baukasten.medien.bildformate import BILD_FILTER
        from lunivo_writer.editor.objekte.bilddaten import bild_aus_datei
        from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster
        from lunivo_writer.editor.objekte import bildlayout as BL
        e = self.current_editor()
        z = BL.ziel(e) if e is not None else None
        w = BL.format_lesen(e, z) if z is not None else None
        if w is None:
            return
        self._seitenleiste_oeffnen()

        def anwenden(neu: dict):
            ed = self.current_editor()
            if ed is not None:
                BL.format_aus_panel(ed, BL.ziel(ed), neu)

        def bild():
            ed = self.current_editor()
            pfad, _ = Dateifenster.getOpenFileName(self, "Bild als Füllung", "", BILD_FILTER)
            if ed is not None and pfad:
                BL.fuellbild_setzen(ed, BL.ziel(ed), bild_aus_datei(pfad, still=True))
        self.sidebar.zeige_objektformat(w, anwenden, reiter, bild)
        self._objekt_text_verbinden()
        if fuellung:
            self.sidebar.objekt_panel.fuellung_waehlen(fuellung)


    def formatierung_seitenleiste(self, reiter: int = 0) -> None:
        """Zahnrad am Diagramm und „Formatieren“ im Rechtsklick-Menü: die Seitenleiste „Formatierung“ passend zum gewählten Objekt."""
        from lunivo_writer.editor.objekte import frei_objekt as FO
        art = FO.art_gewaehlt(self.current_editor()) if self.current_editor() is not None else None
        if art == "diagramm":
            self.diagrammformat_seitenleiste()
        elif art == "smartart" and hasattr(self, "smartartformat_seitenleiste"):
            self.smartartformat_seitenleiste()
        else:
            self.objektformat_seitenleiste(reiter)


    def _smartart_werte(self, e) -> dict | None:
        from lunivo_writer.editor.objekte import smartart as SA
        return SA.format_lesen(e)

    def smartartformat_seitenleiste(self) -> None:
        """Seitenleiste „Formatierung“ für SmartArt (Rechtsklick): die Seitenleiste „Formatierung“ für den gewählten Knoten (ohne Auswahl: alle Knoten); Änderungen gelten sofort."""
        from PySide6.QtGui import QImage
        from lunivo_writer.oberflaeche.baukasten.medien.bildformate import BILD_FILTER
        from lunivo_writer.editor.objekte.bilddaten import bild_aus_datei
        from lunivo_writer.editor.diagramme import diagramm_format as F
        from lunivo_writer.editor.objekte import smartart as SA
        from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster
        w = self._smartart_werte(self.current_editor())
        if w is None:
            self.statusBar().showMessage("Bitte zuerst ein SmartArt auswählen.", 4000)
            return
        self._seitenleiste_oeffnen()

        def anwenden(angaben: dict):
            ed = self.current_editor()
            if ed is not None:
                SA.format_setzen(ed, **dict(angaben))
                self.band.aktualisieren()

        def bild():
            pfad, _ = Dateifenster.getOpenFileName(self, "Bild als Füllung", "", BILD_FILTER)
            b64 = F.bild_kodieren(bild_aus_datei(pfad, still=True)) if pfad else ""
            if b64 and self.current_editor() is not None:
                SA.format_setzen(self.current_editor(), fuell={"art": "bild", "bild_b64": b64})
                self.smartartformat_folgen()
        self.sidebar.zeige_smartartformat(w, anwenden, bild)

    def smartartformat_folgen(self) -> None:
        """Wählt der Benutzer einen anderen Knoten, zeigt der offene Bereich dessen Format."""
        self._format_folgen("smartart", self._smartart_werte)

    def _diagramm_werte(self, e) -> dict | None:
        """Die Werte für die Seitenleiste „Formatierung“ des gewählten Diagrammteils (None ohne markiertes Diagramm)."""
        from lunivo_writer.editor.diagramme import diagramm as D
        from lunivo_writer.editor.diagramme import diagramm_teile as T
        from lunivo_writer.editor.objekte import frei_objekt as FO
        from lunivo_writer.modelle.seite import px_to_mm
        z = FO.ziel(e) if e is not None else None
        d = FO.daten_lesen(e, "diagramm") if e is not None else None
        if d is None or z is None:
            return None
        teil = T.teil_gewaehlt(e) or "diagrammbereich"
        art = D._art(d)
        reihe = teil.startswith("reihe_")
        return {"teil": teil, "teile": self.befehle.diagrammTeile(), "name": T.teil_name(e) or "Diagrammbereich", "format": T.diagramm_teil_format_lesen(e, teil),
                "linienreihe": reihe and D.hat_linien(art), "saeulen": reihe and art.startswith(("saeule", "balken")),
                "wertachse": (art.startswith("punkte") or (teil == "achse_horizontal") == art.startswith("balken")) if teil.startswith("achse_") else True,
                "objekt": {"legende_pos": d.get("legende_pos", "unten"), "breite_mm": px_to_mm(float(z[3]["b"])), "hoehe_mm": px_to_mm(float(z[3]["h"])),
                           "dreh": float(z[3].get("dreh", 0.0) or 0.0)},
                "alt_titel": d.get("alt_titel") or "", "alt_beschreibung": d.get("alt_beschreibung") or "", "alt_dekorativ": bool(z[3].get("dekor"))}


    def diagrammformat_seitenleiste(self) -> None:
        """„Formatieren“ in den Diagrammtools: die Seitenleiste „Formatierung“ für den gewählten Diagrammteil öffnen; Änderungen gelten sofort."""
        from PySide6.QtGui import QImage
        from lunivo_writer.oberflaeche.baukasten.medien.bildformate import BILD_FILTER
        from lunivo_writer.editor.objekte.bilddaten import bild_aus_datei
        from lunivo_writer.editor.diagramme import diagramm_format as F
        from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster
        w = self._diagramm_werte(self.current_editor())
        if w is None:
            self.statusBar().showMessage("Bitte zuerst ein Diagramm auswählen.", 4000)
            return
        self._seitenleiste_oeffnen()

        def anwenden(angaben: dict):
            from lunivo_writer.editor.objekte import bildlayout as BL
            from lunivo_writer.editor.objekte import frei_objekt as FO
            from lunivo_writer.modelle.seite import mm_to_px
            angaben = dict(angaben)
            ed = self.current_editor()
            obj, gr, dreh = angaben.pop("objekt", None), angaben.pop("groesse", None), angaben.pop("dreh", None)
            if ed is not None and obj:
                self.befehle._dg_set(**obj)
            if ed is not None and gr:
                FO.aendern(ed, "diagramm", breite=mm_to_px(gr["breite_mm"]), hoehe=mm_to_px(gr["hoehe_mm"]))
            if ed is not None and dreh is not None:
                BL.frei_aendern(ed, BL.ziel(ed), dreh=float(dreh) % 360.0)
            if angaben:
                self.befehle.diagrammTeilFormat(None, angaben)

        def alt(titel: str, beschreibung: str):
            self.befehle.diagrammAltText(None, titel, beschreibung)

        def dekor(an: bool):
            from lunivo_writer.editor.objekte import bildlayout as BL
            ed = self.current_editor()
            if ed is not None and BL.ziel(ed) is not None:
                BL.frei_aendern(ed, BL.ziel(ed), dekor=bool(an))

        def bild():
            pfad, _ = Dateifenster.getOpenFileName(self, "Bild als Füllung", "", BILD_FILTER)
            b64 = F.bild_kodieren(bild_aus_datei(pfad, still=True)) if pfad else ""
            if b64:
                self.befehle.diagrammTeilFormat(None, {"fuell": {"art": "bild", "bild_b64": b64}})
                self.diagrammformat_folgen()
        def teil(schluessel: str):
            self.befehle.diagrammTeilWaehlen(None, schluessel)
            self.diagrammformat_folgen()
        self.sidebar.zeige_diagrammformat(w, anwenden, alt, bild, teil, dekor)


    def _format_folgen(self, schluessel: str, lesen) -> None:
        """Gemeinsam für alle Bereiche „Formatierung“: ist er offen, zeigt er die Werte des neu gewählten Objekts (``lesen(editor)`` -> Werte oder None)."""
        e = self.current_editor()
        if e is not None and self.sidebar.format_sichtbar(schluessel):
            w = lesen(e)
            if w is not None:
                self.sidebar.aktualisiere_format(schluessel, w)

    def diagrammformat_folgen(self) -> None:
        """Wählt der Benutzer einen anderen Diagrammteil, zeigt der offene Bereich dessen Format."""
        self._format_folgen("diagramm", self._diagramm_werte)


    def _objekt_text_verbinden(self) -> None:
        """Die Textoptionen der Seitenleiste wirken auf den Text im gewählten WordArt oder Textfeld (``editor/objekte/frei_objekt.py``)."""
        from lunivo_writer.editor.objekte import frei_objekt as FO
        panel = self.sidebar.objekt_panel
        if panel is None:
            return
        if getattr(panel, "_objekt_text_verbunden", False):
            panel.text_geaendert.disconnect()
        panel._objekt_text_verbunden = True
        panel.text_geaendert.connect(lambda w: FO.text_werte_anwenden(self.current_editor(), w) if self.current_editor() is not None else None)
        e = self.current_editor()
        w = FO.text_werte_lesen(e) if e is not None else None
        if w is not None:
            panel.setze_text(w)


    def _zeichen_masse(self, e) -> None:
        """Höhe und Breite im Reiter Zeichentools (``bild_…``) und Bildtools (``bt_…``) mit dem markierten Bild abgleichen."""
        f = self.band.felder
        if e is None or getattr(e, "_frei_sel", None) is None:
            return
        from lunivo_writer.editor.objekte import bildlayout as BL
        m = None
        for vor in ("bild_", "bt_", "sa_"):
            if vor + "breite" not in f:
                continue
            m = m or BL.masse_lesen(e, BL.ziel(e))
            if m is None:
                return
            km = self.befehle.smartartKnotenMasse() if vor == "sa_" else None            # SmartArt-Knoten gewählt: dessen Maße, nur ablesbar
            mv = km or m
            for schl, wert in ((vor + "breite", mv[0]), (vor + "hoehe", mv[1])):
                sp = f[schl]
                if vor == "sa_" and hasattr(sp, "setReadOnly"):
                    sp.setReadOnly(km is not None)
                if not sp.hasFocus() and abs(sp.value() - wert) > 0.05:
                    sp.blockSignals(True); sp.setValue(wert); sp.blockSignals(False)
            f[vor + "verhaeltnis"][0] = mv[0] / max(0.1, mv[1])


    def _tabelle_masse(self, e) -> None:
        """Zahlenfelder Höhe/Breite im Reiter Tabellentools (``tab_…``) mit der Zeile und Spalte der Schreibmarke abgleichen."""
        f = self.band.felder
        if e is None or e.textCursor().currentTable() is None or not dict.__contains__(f, "tab_breite"):
            return
        m = self.befehle.tabelleMasseLesen()
        if m is None:
            return
        for schl, wert in (("tab_breite", m[0]), ("tab_hoehe", m[1])):
            sp = f[schl]
            if not sp.hasFocus() and abs(sp.value() - wert) > 0.05:
                sp.blockSignals(True); sp.setValue(wert); sp.blockSignals(False)


    OBJEKT_FORMATE = ("objekt", "smartart", "diagramm")

    def objektformat_folgen(self) -> None:
        """Wechsler der Seitenleiste „Formatierung“ bei neuer Auswahl: Ist ein Format-Bereich (Objekt, SmartArt, Diagramm) offen, zeigt der zur
        Art des neu gewählten Objekts passende Bereich dessen Werte. Ohne Objekt (Text) bleibt der Bereich, wie er ist."""
        e, sb = self.current_editor(), self.sidebar
        offen = [k for k in self.OBJEKT_FORMATE if sb.format_sichtbar(k)]
        if e is None or not offen:
            return
        from lunivo_writer.editor.objekte import bildlayout as BL
        from lunivo_writer.editor.objekte import frei_objekt as FO
        if getattr(e, "_frei_sel", None) is None:
            return
        art = FO.art_gewaehlt(e)
        ziel = art if art in ("diagramm", "smartart") else "objekt"
        if ziel not in offen:
            self.formatierung_seitenleiste()                         # anderer Bereich offen: der passende ersetzt ihn
        elif ziel == "diagramm":
            self.diagrammformat_folgen()
        elif ziel == "smartart":
            self.smartartformat_folgen()
        else:
            self._format_folgen("objekt", lambda ed: BL.format_lesen(ed, BL.ziel(ed)))


