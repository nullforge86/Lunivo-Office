"""Befehle: Seite, Abschnitte, Spalten."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from lunivo_writer.ui.baukasten.eingabe_fenster import EingabeFenster
from lunivo_writer.models.page import HeaderFooter
from PySide6.QtWidgets import QMenu
from lunivo_writer.core.farben import Farbe


class SeiteBefehle:
    """Befehle des Bandes: Seite, Abschnitte, Spalten. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""



    # ---- Seitenlayout --------------------------------------------------------------------------------------------------
    def seitenraenderRahmen(self, k=None, *_):
        self.w.page_setup()


    # ==== Seitenlayout =========================================================================================
    RAND = {"normal": (25, 25, 32, 32), "schmal": (13, 13, 13, 13), "moderat": (25, 25, 19, 19), "breit": (25, 25, 51, 51)}

    PAPIER = {"a4": (210, 297), "a3": (297, 420), "a5": (148, 210), "b5": (176, 250), "letter": (216, 279),
              "legal": (216, 356), "dinlang": (220, 110), "c5": (229, 162), "c6": (162, 114)}


    def w_setzeRandVorgabe(self, k, art):
        o, u, l, r = self.RAND[art]
        self.w.set_margins(o, u, l, r)


    def w_randVorgabeJetzt(self):
        t = self.w.current_tab()
        if not t:
            return ""
        p = t.editor.abschnitt_seite()
        ist = tuple(round(x) for x in (p.margin_top_mm, p.margin_bottom_mm, p.margin_left_mm, p.margin_right_mm))
        for art, v in self.RAND.items():
            if ist == v:
                return art
        return ""


    def seitenraender(self, k=None, *_): self.w.page_setup()


    # ---- Spalten (Seitenansicht, Druck, PDF; die Bearbeitungsansicht bleibt einspaltig) ----------------------------------------------
    def spaltenSetzen(self, k=None, n=1):
        self.w._page_change(lambda p: setattr(p, "spalten", int(n)))
        self.w.statusBar().showMessage("Eine Spalte." if int(n) == 1 else f"{int(n)} Spalten.", 4000)


    def w_spaltenJetzt(self):
        t = self.w.current_tab()
        return t.editor.abschnitt_seite().spalten if t else 1


    def spalten(self, k=None):
        self.w.page_setup()


    def spaltenumbruch(self, k=None):
        """Der Text danach beginnt in der nächsten Spalte (bei einer Spalte: auf der nächsten Seite)."""
        if self.ed:
            self.ed.insert_column_break()

    seitenraenderRahmen = seitenraender


    def w_setzePapier(self, k, art):
        b, h = self.PAPIER[art]
        self.w._page_change(lambda p: (setattr(p, "width_mm", min(b, h) if not p.landscape else max(b, h)),
                                       setattr(p, "height_mm", max(b, h) if not p.landscape else min(b, h))))


    def w_papierJetzt(self):
        t = self.w.current_tab()
        if not t:
            return ""
        a, b = sorted((round(t.editor.abschnitt_seite().width_mm), round(t.editor.abschnitt_seite().height_mm)))
        for art, (x, y) in self.PAPIER.items():
            if (a, b) == tuple(sorted((x, y))):
                return art
        return ""


    def w_querJetzt(self):
        t = self.w.current_tab()
        return bool(t) and t.editor.abschnitt_seite().landscape


    def w_setzeQuer(self, k=None, quer=True):
        """Hochformat (False) oder Querformat (True) für den Abschnitt am Zeiger."""
        if self.w.current_tab():
            self.w.set_orientation(bool(quer))


    def querformat(self, k=None):
        t = self.w.current_tab()
        if t:
            self.w.set_orientation(not t.editor.abschnitt_seite().landscape)


    def w_setzeThema(self, k, wahl):
        self.w.set_theme(wahl)


    def w_themaJetzt(self):
        return self.w.settings.get("theme", "system")


    # ---- Klappmenüs wie in der Vorlage: Ränder, Ausrichtung, Größe, Spalten, Textrichtung, Zeilennummern, Ausrichten ----------------
    RAND_NAMEN = {"normal": "Normal", "schmal": "Schmal", "moderat": "Moderat", "breit": "Breit"}
    PAPIER_NAMEN = {"a4": "A4", "a3": "A3", "a5": "A5", "b5": "B5", "letter": "Letter", "legal": "Legal", "dinlang": "Umschlag DIN lang",
                    "c5": "Umschlag C5", "c6": "Umschlag C6"}


    @staticmethod
    def _haken_auffrischen(m, jetzt) -> None:
        """Vor dem Aufklappen die aktuelle Kachel markieren (die Menüs werden nur einmal gebaut)."""
        m.aboutToShow.connect(lambda: [k.setChecked(s == jetzt()) for s, k in m.knoepfe.items()])


    def menue_raenderKlappe(self):
        from PySide6.QtCore import QSize
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, zeilenkachel
        from lunivo_writer.ui.baukasten.seiten_bildchen import raender_zeichner
        m = RasterAuswahl(self.w, spalten=1, groesse=QSize(320, 70))
        for art, (o, u, l, r) in self.RAND.items():
            m.kachel(art, self.RAND_NAMEN[art], zeilenkachel(raender_zeichner(o, u, l, r), self.RAND_NAMEN[art],
                                                            [f"Oben: {o} mm", f"Unten: {u} mm", f"Links: {l} mm", f"Rechts: {r} mm"], 2))
        m.trenner()
        m.fuss("Benutzerdefinierte Seitenränder …", self.w.page_setup)
        m.gewaehlt.connect(lambda art: self.w_setzeRandVorgabe(None, art))
        self._haken_auffrischen(m, self.w_randVorgabeJetzt)
        return m


    def menue_ausrichtungKlappe(self):
        from PySide6.QtCore import QSize
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, zeilenkachel
        from lunivo_writer.ui.baukasten.seiten_bildchen import format_zeichner
        m = RasterAuswahl(self.w, spalten=1, groesse=QSize(170, 40))
        m.kachel("hoch", "Hochformat", zeilenkachel(format_zeichner(False), "Hochformat", bild_breite=34))
        m.kachel("quer", "Querformat", zeilenkachel(format_zeichner(True), "Querformat", bild_breite=34))
        m.gewaehlt.connect(lambda art: self.w_setzeQuer(None, art == "quer"))
        self._haken_auffrischen(m, lambda: "quer" if self.w_querJetzt() else "hoch")
        return m


    def menue_groesseKlappe(self):
        from PySide6.QtCore import QSize
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, zeilenkachel
        from lunivo_writer.ui.baukasten.seiten_bildchen import papier_zeichner
        m = RasterAuswahl(self.w, spalten=1, groesse=QSize(240, 48), hoehe_max=620)
        for art, (b, h) in self.PAPIER.items():
            m.kachel(art, self.PAPIER_NAMEN[art], zeilenkachel(papier_zeichner(), self.PAPIER_NAMEN[art], [f"{b} mm × {h} mm"], bild_breite=34))
        m.trenner()
        m.fuss("Weitere Papierformate …", self.w.page_setup)
        m.gewaehlt.connect(lambda art: self.w_setzePapier(None, art))
        self._haken_auffrischen(m, self.w_papierJetzt)
        return m


    def menue_spaltenKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe()
        eintraege = [m.eintrag(t, lambda n=n: self.spaltenSetzen(None, n), symbol=icons.icon(f"spalte{n}", 18), haken=False)
                     for n, t in ((1, "Eins"), (2, "Zwei"), (3, "Drei"))]
        m.eintrag("Mehr Spalten …", self.spalten, symbol=icons.icon("spalten", 18))
        m.aboutToShow.connect(lambda: [a.setChecked(i + 1 == self.w_spaltenJetzt()) for i, a in enumerate(eintraege)])
        return m


    TEXTRICHTUNGEN = [("waagerecht", "Horizontal"), ("senkrecht_rl", "Vertikal von rechts nach links"),
                      ("senkrecht_lr", "Vertikal von links nach rechts"), ("dreh90", "Gesamten Text um 90 Grad drehen"),
                      ("dreh270", "Gesamten Text um 270 Grad drehen"), ("asiatisch270", "Asiatische Zeichen um 270 Grad drehen")]


    def menue_textrichtungKlappe(self):
        """Textrichtung wie in der Vorlage. Lunivo setzt Text nur waagerecht; die senkrechten Richtungen bleiben grau."""
        from PySide6.QtCore import QSize
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, zeilenkachel
        from lunivo_writer.ui.baukasten.seiten_bildchen import textrichtung_zeichner
        m = RasterAuswahl(self.w, spalten=1, groesse=QSize(330, 44))
        for art, text in self.TEXTRICHTUNGEN:
            m.kachel(art, text, zeilenkachel(textrichtung_zeichner(art), text, bild_breite=40), aktiv=art == "waagerecht")
        m.trenner()
        m.fuss("Textrichtung ändern …", lambda: None).setEnabled(False)
        m.gewaehlt.connect(lambda art: self.textrichtungLinks())
        self._haken_auffrischen(m, lambda: "" if self.an_textrichtung() else "waagerecht")
        return m


    def menue_zeilennummernKlappe(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        keine = m.eintrag("Keine", lambda: self.zeilennummernArt(None, None), haken=False)
        fort = m.eintrag("Fortlaufend", lambda: self.zeilennummernArt(None, ""), haken=False)
        seite = m.eintrag("Jede Seite neu beginnen", lambda: self.zeilennummernArt(None, "seite"), haken=False)
        m.eintrag("Jeden Abschnitt neu beginnen", aktiv=False)
        m.trenner()
        unter = m.eintrag("Für aktuellen Absatz unterdrücken", self.zeilennummernUnterdruecken, haken=False)
        m.eintrag("Zeilennummern für leere Zeilen verstecken", aktiv=False)
        m.trenner()
        m.eintrag("Zeilennummerierungs-Einstellungen …", aktiv=False)

        def auffrischen():
            pg = self.ed.page if self.ed else None
            an = bool(pg and pg.zeilennummern)
            keine.setChecked(not an); fort.setChecked(an and not pg.zeilennummern_neu); seite.setChecked(an and pg.zeilennummern_neu == "seite")
            unter.setEnabled(an); unter.setChecked(bool(self.ed) and self._ohne_zeilennr())
        m.aboutToShow.connect(auffrischen)
        return m


    def zeilennummernArt(self, k=None, art=""):
        """``art``: None = keine, "" = fortlaufend, "seite" = jede Seite neu."""
        if not self.ed:
            return
        pg = self.ed.page
        pg.zeilennummern_neu = art or ""
        self.ed.set_zeilennummern(art is not None)
        self.ed.document().setModified(True)


    def _ohne_zeilennr(self) -> bool:
        from lunivo_writer.editor import absatzopt
        return absatzopt.lesen(self.ed.textCursor().blockFormat())["ohne_zeilennr"]


    def zeilennummernUnterdruecken(self, k=None):
        """Der Absatz an der Schreibmarke (oder die markierten) bekommt keine Zeilennummern — oder wieder welche."""
        if not self.ed:
            return
        from lunivo_writer.editor import absatzopt
        neu = not self._ohne_zeilennr()
        self.ed._block_merge(lambda bf: absatzopt.setzen(bf, {**absatzopt.lesen(bf), "ohne_zeilennr": neu}))
        self.ed.viewport().update()


    def menue_ausrichtenKlappe(self):
        """Ausrichten wie in der Vorlage: die Form oder das freie Bild am Blatt ausrichten; was eine Mehrfachauswahl braucht, bleibt grau."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe()
        objekt = [m.eintrag(t, lambda w=w: self.zeichenAusrichten(None, w), symbol=icons.icon(sym, 18))
                  for w, t, sym in (("links", "Linksbündig", "kanteLinks"), ("mitte", "Zentriert ausrichten", "mitte"),
                                    ("rechts", "Rechtsbündig", "kanteRechts"), ("oben", "Oben ausrichten", "kanteOben"),
                                    ("mittig", "Mittig ausrichten", "mitte"), ("unten", "Untenbündig ausrichten", "kanteUnten"))]
        m.trenner()
        for t in ("Horizontal verteilen", "Vertikal verteilen"):
            m.eintrag(t, aktiv=False, tip="Braucht mehrere markierte Objekte.")
        m.trenner()
        for t in ("Gleiche Höhe", "Gleiche Breite", "Gleiche Größe"):
            m.eintrag(t, aktiv=False, tip="Braucht mehrere markierte Objekte.")
        m.trenner()
        m.eintrag("Relativ zur Seite", haken=True, aktiv=False, tip="Lunivo richtet am Blatt aus.")
        m.trenner()
        netz = m.eintrag("Gitternetzlinien", self.netzlinien, symbol=icons.icon("netz", 18), haken=False)
        m.eintrag("Raster …", aktiv=False)

        def auffrischen():
            from lunivo_writer.editor import bildlayout as BL
            z = BL.ziel(self.ed) if self.ed else None
            for a in objekt:
                a.setEnabled(z is not None and z[0] == "frei")
            netz.setChecked(self.an_netzlinien())
        m.aboutToShow.connect(auffrischen)
        return m


    # ---- Seitenhintergrund -------------------------------------------------------------------
    def _seite_aendern(self, **felder):
        e = self.ed
        if not e:
            return
        pg = e.abschnitt_seite()
        for k, v in felder.items():
            setattr(pg, k, v)
        e.page_settings_changed(pg)


    def menue_seitenfarbe(self):
        m = self._farbmenue(lambda c: self._seite_aendern(color=c.name() if c else ""), "Keine Farbe")
        return m


    def menue_seitenfarbeKlappe(self):
        """Seitenfarbe wie in der Vorlage: Palette, darunter Hintergrundbild und anderer Hintergrund (in Lunivo noch grau) und das
        Untermenü Wasserzeichen (dieselbe Galerie wie Einfügen ▸ Wasserzeichen)."""
        m = self.menue_seitenfarbe()
        m.addSeparator()
        m.addAction("Hintergrundbild …").setEnabled(False)
        anders = m.addMenu("Anderer Hintergrund"); anders.setEnabled(False)
        m.addSeparator()
        w = self.menue_wasserzeichenKlappe(); w.setTitle("Wasserzeichen")
        from lunivo_writer.ui.widgets import icons
        w.setIcon(icons.icon("wasserzeichen", 18))
        m.addMenu(w)
        return m


    def seitenfarbe(self, k=None):
        m = self.menue_seitenfarbe()
        self._popup(m)


    def wasserzeichen(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.ui.dialogs.wasserzeichen_fenster import WasserzeichenDialog
        e = self.ed
        d = WasserzeichenDialog(self.w, e.abschnitt_seite().watermark or e.page.watermark, e.abschnitt_seite(),
                                str(self.w.settings.get("last_dir", "") or ""))
        if d.exec():
            self._wasserzeichen_setzen(d.ergebnis(), d.bereich())


    def _wasserzeichen_setzen(self, w: dict | None, bereich: str = "dokument") -> None:
        """Wasserzeichen für das ganze Dokument oder nur den Abschnitt mit der Schreibmarke („Übernehmen für“)."""
        e = self.ed
        if not e:
            return
        from lunivo_writer.editor import abschnitte as AB
        doc = e.document()
        nr = e.abschnitt_nr()
        alt = e.page.watermark
        w = {k: v for k, v in (w or {}).items() if k != "abschnitt"} or None
        for i, (_n, _t, ps) in enumerate(AB.umbrueche(doc), start=1):
            eigen = (ps.watermark or {}).get("abschnitt")
            if bereich == "abschnitt" and i == nr:
                ps.watermark = dict(w or {}, abschnitt=True)
            elif bereich == "abschnitt" and nr == 0 and not eigen:
                ps.watermark = dict(alt or {}, abschnitt=True)          # die anderen Abschnitte behalten, was sie bisher zeigten
            elif bereich == "dokument":
                ps.watermark = None
            else:
                continue
            AB.setzen(doc, i, ps)
        if bereich == "dokument" or nr == 0:
            pg = e.page.copy(); pg.watermark = w
            e.apply_page(pg)
        e.document().setModified(True)
        e.viewport().update()


    def seitenrahmen(self, k=None):
        if not self.ed:
            return
        self.absatzRahmen(seite="seitenrand")                       # dasselbe Fenster, Reiter Seitenrand


    def netzlinien(self, k=None):
        if self.ed:
            self.ed.set_gitter(not self.ed.gitter)


    def an_netzlinien(self): return bool(self.ed and self.ed.gitter)


    # ---- Seitenlayout: Absatz, Zeilennummern, Textrichtung, Designs ---------------------------------------
    ABSATZABSTAND = [("Standard (0 / 0 pt)", 0, 0), ("Kompakt (0 / 4 pt)", 0, 4), ("Locker (0 / 10 pt)", 0, 10),
                     ("Luftig (6 / 12 pt)", 6, 12), ("Vor und nach 12 pt", 12, 12)]


    def absatzabstand(self, k=None):
        if not self.ed:
            return
        m = QMenu()
        for text, vor, nach in self.ABSATZABSTAND:
            m.addAction(text, lambda _=False, v=vor, n=nach: self._abstand_setzen(v, n))
        self._popup(m)


    def _abstand_setzen(self, vor, nach):
        e = self.ed
        if not e.textCursor().hasSelection():
            c = e.textCursor(); c.select(QTextCursor.Document); e.setTextCursor(c)       # ohne Markierung: ganzes Dokument
            e.set_paragraph_spacing(vor, nach)
            c.clearSelection(); e.setTextCursor(c)
        else:
            e.set_paragraph_spacing(vor, nach)


    def zeilennummern(self, k=None):
        if self.ed:
            self.ed.set_zeilennummern(not self.ed.page.zeilennummern)
            self.ed.document().setModified(True)


    def an_zeilennummern(self): return bool(self.ed and self.ed.page.zeilennummern)


    def silbentrennung(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.editor.pagination import _trenner
        pg = self.ed.page
        sprache = self.w.settings.get("silben/sprache", "de_DE")
        if _trenner(sprache) is None:
            self.w.statusBar().showMessage("Silbentrennung braucht das Paket „pyphen“ (pip install pyphen).", 6000)
            return
        pg.silbentrennung = not pg.silbentrennung
        pg.silben_sprache = sprache
        self.ed.page_settings_changed(pg)
        self.w.statusBar().showMessage(
            "Silbentrennung an — in Seitenansicht, Druck und PDF; die Bearbeitungsansicht zeigt keine Trennstriche."
            if pg.silbentrennung else "Silbentrennung aus.", 6000)


    def an_silbentrennung(self): return bool(self.ed and self.ed.page.silbentrennung)


    def textrichtung(self, k=None):
        if self.ed:
            self.ed.toggle_rtl()


    def textrichtungLinks(self, k=None):
        if self.ed and self.an_textrichtung():
            self.ed.toggle_rtl()


    def textrichtungRechts(self, k=None):
        if self.ed and not self.an_textrichtung():
            self.ed.toggle_rtl()


    def zeilenumbruch(self, k=None):
        """Zeilenumbruch ohne neuen Absatz (Umschalt+Enter)."""
        if self.ed:
            c = self.ed.textCursor()
            c.insertText("\u2028")
            self.ed.setTextCursor(c)


    textflussumbruch = zeilenumbruch                       # WPS: „Textflussumbruch“ (Umschalt+Enter) ist bei Lunivo der Zeilenumbruch


    def an_textrichtung(self):
        return bool(self.ed and self.ed.textCursor().blockFormat().layoutDirection() == Qt.RightToLeft)


    # Designs, Farben, Schriftarten, Effekte: Galerien wie in der Vorlage; die Werte stehen in editor/designs.py
    def menue_designsKlappe(self):
        from PySide6.QtCore import QSize
        from lunivo_writer.editor import designs as D
        from lunivo_writer.ui.baukasten.design_bildchen import design_zeichner
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, spalten=4, groesse=QSize(72, 50), hoehe_max=620)
        for name, (schema, paar) in D.DESIGNS.items():
            m.kachel(name, name, design_zeichner(D.FARBSCHEMEN[schema], D.SCHRIFTPAARE[paar][0]))
        m.gewaehlt.connect(lambda n: self.designSetzen(None, n))
        return m


    def designSetzen(self, k=None, name="Lunivo"):
        """Design: Schrift der Überschriften und des Textes, Farbe der Überschriften — für das ganze Dokument (ein Schritt)."""
        from lunivo_writer.editor import designs as D
        if self.ed and name in D.DESIGNS:
            d = D.design(name)
            self.ed.apply_design(d["text"], d["kopf"], d["farbe"])


    def menue_farbenKlappe(self):
        from PySide6.QtCore import QSize
        from lunivo_writer.editor import designs as D
        from lunivo_writer.ui.baukasten.design_bildchen import farbreihe_zeichner
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, titel="Farbschemen", spalten=1, groesse=QSize(310, 24), hoehe_max=620)
        for name, farben in D.FARBSCHEMEN.items():
            m.kachel(name, name, farbreihe_zeichner(farben, name))
        m.trenner()
        m.fuss("Benutzerdefinierte Farbe …", self._farbe_eigen)
        m.gewaehlt.connect(lambda n: self.farbschemaSetzen(None, n))
        return m


    def farbschemaSetzen(self, k=None, name="Lunivo"):
        from lunivo_writer.editor import designs as D
        if self.ed and name in D.FARBSCHEMEN:
            self.ed.apply_design(None, None, D.ueberschrift_farbe(name))


    def _farbe_eigen(self):
        from lunivo_writer.ui.baukasten.farbpalette import weitere_farben
        if self.ed and (c := weitere_farben(self.w, titel="Farbe der Überschriften")) is not None:
            self.ed.apply_design(None, None, c.name())


    def menue_schriftartenKlappe(self):
        from PySide6.QtCore import QSize
        from lunivo_writer.editor import designs as D
        from lunivo_writer.ui.baukasten.design_bildchen import schriftpaar_zeichner
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, spalten=1, groesse=QSize(290, 70), hoehe_max=640)
        for name, (kopf, text) in D.SCHRIFTPAARE.items():
            m.kachel(name, f"{name}: Überschriften {kopf}, Text {text}", schriftpaar_zeichner(name, kopf, text))
        m.gewaehlt.connect(lambda n: self.schriftpaarSetzen(None, n))
        return m


    def schriftpaarSetzen(self, k=None, name="Lunivo"):
        from lunivo_writer.editor import designs as D
        if self.ed and name in D.SCHRIFTPAARE:
            kopf, text = D.SCHRIFTPAARE[name]
            self.ed.apply_design(text, kopf, None)


    def menue_effekteKlappe(self):
        from PySide6.QtCore import QSize
        from lunivo_writer.editor import designs as D
        from lunivo_writer.ui.baukasten.design_bildchen import effekt_zeichner
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, spalten=4, groesse=QSize(112, 60), beschriftet=True, hoehe_max=640)
        for name, fx in D.EFFEKTE.items():
            m.kachel(name, name, effekt_zeichner(fx))
        m.gewaehlt.connect(lambda n: self.effektSetzen(None, n))
        return m


    def effektSetzen(self, k=None, name="Schlicht"):
        """Effekt an die markierte Form bzw. das markierte freie Bild; ist nichts markiert, an alle im Dokument."""
        from lunivo_writer.editor import bildlayout as BL
        from lunivo_writer.editor import designs as D
        if not self.ed or name not in D.EFFEKTE:
            return
        z = BL.ziel(self.ed)
        if z is not None and z[0] == "frei":
            BL.format_setzen(self.ed, z, fx=dict(D.EFFEKTE[name]))
        elif not BL.fx_alle(self.ed, D.EFFEKTE[name]):
            self.w.statusBar().showMessage("Effekte gelten für Formen und frei liegende Bilder — im Dokument gibt es keine.", 5000)


    def designs(self, k=None): self._popup(self.menue_designsKlappe())

    def farbschema(self, k=None): self._popup(self.menue_farbenKlappe())

    def designSchriften(self, k=None): self._popup(self.menue_schriftartenKlappe())

    def designEffekte(self, k=None): self._popup(self.menue_effekteKlappe())


    # ---- Abschnitte ------------------------------------------------------------------------------------------------------
    ABSCHNITT_ART = {"NextPage": "naechste", "Continuous": "fortlaufend", "EvenPage": "gerade", "OddPage": "ungerade"}


    def abschnittsumbruch(self, k=None, art="NextPage"):
        if not self.ed:
            return
        nr = self.ed.abschnitt_einfuegen(self.ABSCHNITT_ART.get(art, "naechste"))
        self.w.statusBar().showMessage(f"Abschnitt {nr + 1} beginnt hier (Einrichtung wie der vorige; Orientierung, Größe, Ränder gelten für den Abschnitt der Schreibmarke).", 7000)


    def abschnittLoeschen(self, k=None):
        if self.ed:
            ok = self.ed.abschnitt_entfernen()
            self.w.statusBar().showMessage("Abschnittsumbruch entfernt — die beiden Abschnitte sind einer (mit der Einrichtung des früheren)."
                                           if ok else "Das Dokument hat nur einen Abschnitt.", 6000)


    def abschnittVorher(self, k=None):
        if self.ed:
            self.ed.abschnitt_gehe(self.ed.abschnitt_nr() - 1)


    def abschnittNaechster(self, k=None):
        if self.ed:
            self.ed.abschnitt_gehe(self.ed.abschnitt_nr() + 1)


    def abschnittNavigation(self, k=None):
        self.geheZu(k, "Abschnitt")


    def abschnittEinstellungen(self, k=None):
        t = self.w.current_tab()
        if not t:
            return
        from lunivo_writer.editor import abschnitte as AB
        from lunivo_writer.ui.dialogs.dokument_dialoge import PageSetupDialog
        e = t.editor
        nr = e.abschnitt_nr()
        d = PageSetupDialog(e.abschnitt_seite(), self.w)
        d.setWindowTitle(f"Abschnitt {nr + 1} einrichten")
        if d.exec():
            e.page_settings_changed(d.result_page())
        if nr > 0:
            namen = list(AB.TYPEN.values())
            ab = AB.umbrueche(e.document())[nr - 1]
            gewaehlt, ok = EingabeFenster.getItem(self.w, f"Abschnitt {nr + 1}", "Der Abschnitt beginnt:", namen,
                                                list(AB.TYPEN).index(ab[1]), False)
            if ok:
                typ = list(AB.TYPEN)[namen.index(gewaehlt)]
                AB.setzen(e.document(), nr, AB.einrichtung(e.document(), e.page, nr), typ)
                e.document().setModified(True)
                e._recount()


    def _kopf_link(self, was: str, an: bool | None = None):
        t = self.w.current_tab()
        if not t or t.editor.abschnitt_nr() == 0:
            return None
        pg = t.editor.abschnitt_seite()
        feld = "kopf_verknuepft" if was == "kopf" else "fuss_verknuepft"
        if an is None:
            return getattr(pg, feld)
        setattr(pg, feld, an)
        t.editor.page_settings_changed(pg)
        return an


    def kopfVerknuepfen(self, k=None):
        if self._kopf_link("kopf") is None:
            self.w.statusBar().showMessage("Der erste Abschnitt hat keinen Vorgänger.", 4000)
        else:
            self._kopf_link("kopf", not self._kopf_link("kopf"))


    def fussVerknuepfen(self, k=None):
        if self._kopf_link("fuss") is None:
            self.w.statusBar().showMessage("Der erste Abschnitt hat keinen Vorgänger.", 4000)
        else:
            self._kopf_link("fuss", not self._kopf_link("fuss"))


    def an_kopfVerknuepfen(self): return bool(self._kopf_link("kopf"))

    def an_fussVerknuepfen(self): return bool(self._kopf_link("fuss"))


    def schriftartMehr(self, k=None):
        if not self.ed:
            return
        """Fenster „Schriftart“ (Baukasten): Schrift, Schnitt, Größe, Farbe, Unterstreichung, Effekte, Zeichenabstand."""
        from lunivo_writer.ui.baukasten.schriftart_dialog import SchriftartDialog
        from lunivo_writer.ui.baukasten.text_format import aus_format, zu_format
        d0 = self.ed.document().defaultFont()
        w = aus_format(self._fmt(), d0.family(), d0.pointSizeF())
        w["versteckt"] = self.ed.ist_versteckt()
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        d = SchriftartDialog(self.w, w)
        if ausfuehren(d):
            neu = d.werte()
            if neu.pop("als_standard", False):                  # „Standard …“: Schrift und Größe für neue Dokumente merken
                if neu["schrift"]:
                    self.w.settings.set("standard/schrift", neu["schrift"])
                if neu["groesse"]:
                    self.w.settings.set("standard/groesse", neu["groesse"])
                self.w.statusBar().showMessage("Die Schrift gilt jetzt als Standard für neue Dokumente.", 5000)
            self.ed._merge(zu_format(neu))
            if "effekt" in neu:
                from lunivo_writer.editor import texteffekt
                self.ed._merge(texteffekt.zu_format(neu["effekt"]))
            if neu["versteckt"] != w["versteckt"]:
                self.ed.set_versteckt(neu["versteckt"])


    def papierformatFenster(self, k=None): self.w.page_setup()

    def fusszeileBearbeiten(self, k=None): self.w.edit_header_footer(False)


    def ersteSeiteAnders(self, k=None):
        t = self.w.current_tab()
        if not t:
            return
        pg = t.editor.abschnitt_seite()
        pg.diff_first = not pg.diff_first
        if pg.diff_first and pg.first_header.is_empty() and pg.first_footer.is_empty():
            pg.first_header = HeaderFooter(); pg.first_footer = HeaderFooter()
        t.editor.page_settings_changed(pg)


    def an_ersteSeiteAnders(self):
        t = self.w.current_tab()
        return bool(t and t.editor.abschnitt_seite().diff_first)


    def tabelleEigenschaften(self, k=None):
        t = self.ed.textCursor().currentTable() if self.ed else None
        if t is None:
            return
        from PySide6.QtGui import QTextLength
        from lunivo_writer.ui.dialogs.dokument_dialoge import TabellenEigenschaftenDialog
        fm = t.format()
        d = TabellenEigenschaftenDialog(
            self.w, int(fm.width().rawValue()) if fm.width().type() == QTextLength.PercentageLength else 100,
            1 if fm.alignment() & Qt.AlignHCenter else 2 if fm.alignment() & Qt.AlignRight else 0,
            fm.border(), fm.cellPadding(), fm.headerRowCount() > 0)
        if d.exec():
            fm.setWidth(QTextLength(QTextLength.PercentageLength, d.breite.value()))
            fm.setAlignment([Qt.AlignLeft, Qt.AlignHCenter, Qt.AlignRight][d.ausr.currentIndex()])
            fm.setBorder(d.rand.value()); fm.setCellPadding(d.pad.value()); fm.setHeaderRowCount(1 if d.kopf.isChecked() else 0)
            t.setFormat(fm)
            self.ed.document().setModified(True)


    def tabelleSortieren(self, k=None):
        c = self.ed.textCursor() if self.ed else None
        t = c.currentTable() if c else None
        if t is None:
            return
        cell = t.cellAt(c)
        namen = [f"Spalte {i + 1}" for i in range(t.columns())]
        n, ok = EingabeFenster.getItem(self.w, "Tabelle sortieren", "Nach welcher Spalte?", namen, cell.column(), False)
        if not ok:
            return
        auf, ok = EingabeFenster.getItem(self.w, "Tabelle sortieren", "Reihenfolge:", ["Aufsteigend", "Absteigend"], 0, False)
        if not ok:
            return
        spalte = namen.index(n)
        start = t.format().headerRowCount()
        zeilen = []
        for r in range(start, t.rows()):
            zeilen.append([t.cellAt(r, k_).firstCursorPosition().block().text() for k_ in range(t.columns())])

        def schluessel(z):
            v = z[spalte].strip().replace(",", ".")
            try:
                return (0, float(v), "")
            except ValueError:
                return (1, 0.0, v.casefold())
        zeilen.sort(key=schluessel, reverse=(auf == "Absteigend"))
        c.beginEditBlock()
        for i, z in enumerate(zeilen):
            for k_, text in enumerate(z):
                cc = t.cellAt(start + i, k_).firstCursorPosition()
                fmt = cc.charFormat()
                cc.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                cc.insertText(text, fmt)
        c.endEditBlock()
        self.ed.document().setModified(True)
