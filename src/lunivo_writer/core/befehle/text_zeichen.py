"""TextZeichenBefehle: fachlich abgegrenzte Bandbefehle."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt  # noqa: F401
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor, QTextListFormat  # noqa: F401
from PySide6.QtWidgets import QMenu, QMessageBox  # noqa: F401
from lunivo_writer.editor.linie import Linie  # noqa: F401
from lunivo_writer.ui.baukasten import FarbPalette, RahmenMenue, RasterAuswahl  # noqa: F401
from lunivo_writer.core.farben import Farbe  # noqa: F401
from lunivo_writer.ui.baukasten.basis import farben as BF  # noqa: F401


class TextZeichenBefehle:
    """Teilbereich der Textbefehle; wird von TextBefehle zusammengesetzt."""

    def stilAnwenden(self, name):
        self.w.stil_anwenden(name)

    def stilVorschau(self, name, ed):
        """Stilvorschau (Überfahren der Galerie): „Fließtext“ gilt als „Standard“."""
        ed.apply_style("Standard" if name == "Fließtext" else name)

    def schriftGroesser(self, k=None):
        if self.ed: self.ed.grow_font(1)

    def schriftKleiner(self, k=None):
        if self.ed: self.ed.grow_font(-1)


    groesser = schriftGroesser

    kleiner = schriftKleiner

    def schlicht(self, k=None):
        if self.ed: self.ed.clear_formatting()

    def fett(self, k=None):
        if self.ed: self.ed.toggle_bold(not self.an_fett())

    def an_fett(self): return self._fmt().fontWeight() >= 600

    def kursiv(self, k=None):
        if self.ed: self.ed.toggle_italic(not self.an_kursiv())

    def an_kursiv(self): return self._fmt().fontItalic()

    def unter(self, k=None):
        if self.ed: self.ed.toggle_underline(not self.an_unter())

    def an_unter(self): return self._fmt().underlineStyle() != QTextCharFormat.NoUnderline


    # Linien im Menü am Knopf „Unterstrichen“ — dieselben acht wie in der Vorlage, als Bild
    UNTER_MENUE = ("einfach", "doppelt", "dick", "gepunktet", "gestrichelt", "strichpunkt", "strichpunktpunkt", "wellig")

    def menue_unterstrichKlappe(self):
        """Wie in der Vorlage: die Linienarten als Bild, „Mehr Unterstreichungen …“ (Fenster Schriftart) und „Unterstreichungsfarbe“ mit der
        gemeinsamen Farbpalette."""
        from lunivo_writer.editor.textfx import unter_zeichnen
        from lunivo_writer.ui.baukasten.basis.linien import linien_menue_zeile
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        from lunivo_writer.ui.baukasten.formatierung.text_format import unter_format
        m = MenueListe()
        for art in self.UNTER_MENUE:
            linien_menue_zeile(m, "", art, 1.0, lambda a=art: self.ed and self.ed._merge(unter_format(a)),
                               maler=lambda p, x0, y, x1, farbe, a=art: unter_zeichnen(p, x0, y, x1, a, farbe))
        m.trenner()
        m.eintrag("Mehr Unterstreichungen …", self.schriftartMehr)                  # das Fenster „Schriftart“ mit allen Arten und der Farbe der Linie
        pal = FarbPalette(m, keine_text="Automatisch", weitere_text="Weitere Unterstreichungsfarben …", titel="Unterstreichungsfarbe", pipette=False)
        pal.setTitle("Unterstreichungsfarbe")
        pal.gewaehlt.connect(lambda c: self.ed and self._unterfarbe(c))
        m.addMenu(pal)
        return m

    def _unterfarbe(self, farbe) -> None:
        """Farbe der Unterstreichung; ist der Text noch nicht unterstrichen, wird er es einfach (wie in der Vorlage)."""
        from lunivo_writer.ui.baukasten.formatierung.text_format import unter_format
        f = QTextCharFormat() if self.an_unter() else unter_format("einfach")
        f.setUnderlineColor(farbe if farbe is not None else QColor())
        self.ed._merge(f)


    # Knopf „Durchgestrichen“ mit Klappe wie in der Vorlage: Durchgestrichen oder Betonungszeichen; der Knopf führt das zuletzt Gewählte aus
    _DURCH = (("durch", "Durchgestrichen", "durchgestrichen"), ("betonung", "Betonungszeichen", "betonung"))

    def durchJetzt(self, k=None):
        self.betonung() if getattr(self, "_durch_art", "durch") == "betonung" else self.durch()

    def an_durchJetzt(self):
        return self.an_betonung() if getattr(self, "_durch_art", "durch") == "betonung" else self.an_durch()

    def symbolname_durchJetzt(self) -> str:
        return next(s for a, _t, s in self._DURCH if a == getattr(self, "_durch_art", "durch"))

    def menue_durchKlappe(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe()
        for art, text, symbol in self._DURCH:
            m.eintrag(text, lambda a=art: self._durch_waehlen(a), symbol=icons.icon(symbol, 16))
        return m

    def _durch_waehlen(self, art: str) -> None:
        self._durch_art = art
        self.durchJetzt()
        self.w.band.aktualisieren()

    def betonung(self, k=None):
        """Betonungszeichen (Punkt über jedem Buchstaben) an- oder ausschalten; andere Zeichen wählt das Fenster „Schriftart“."""
        from lunivo_writer.editor.zusatz import P_BETONUNG
        if self.ed:
            f = QTextCharFormat(); f.setProperty(P_BETONUNG, "" if self.an_betonung() else "punkt")
            self.ed._merge(f)

    def an_betonung(self):
        from lunivo_writer.editor.zusatz import P_BETONUNG
        f = self._fmt()
        return bool(f.hasProperty(P_BETONUNG) and f.stringProperty(P_BETONUNG))

    def menue_einstellungenKlappe(self):
        """Knopf „Einstellungen“ wie in der Vorlage: die Fenster des Reiters Start."""
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons
        m = MenueListe()
        m.eintrag("Schriftart …", self.schriftartMehr, symbol=icons.icon("schriftFenster", 16), kuerzel="Strg+D")
        m.eintrag("Absatz …", self.einzugGenau, symbol=icons.icon("absatzFenster", 16))
        m.eintrag("Formatvorlagen und Formatierung …", self.formatvorlagenBereich, symbol=icons.icon("pinsel", 16))
        return m

    def formatvorlagenBereich(self, k=None):
        """„Formatvorlagen und Formatierung“: die Liste aller Formatvorlagen in der rechten Seitenleiste (wie der Bereich der Vorlage)."""
        if not self.ed:
            return
        from lunivo_writer.ui.baukasten.controls.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.vorlagen.formatvorlagen_bereich import FormatvorlagenBereich
        ausfuehren(FormatvorlagenBereich(self.w, self.w.current_editor, self.w.stil_anwenden, self.neueFormatvorlage))

    def objekteWaehlen(self, k=None):
        """Springt zum nächsten Bild im Text und markiert es (dann erscheinen die Bildtools)."""
        e = self.ed
        if not e:
            return
        doc = e.document()
        start = e.textCursor().selectionEnd()
        for runde in (0, 1):
            b = doc.findBlock(start) if runde == 0 else doc.firstBlock()
            while b.isValid():
                it = b.begin()
                while not it.atEnd():
                    fr = it.fragment()
                    if fr.isValid() and fr.charFormat().isImageFormat() and (runde == 1 or fr.position() >= start):
                        c = QTextCursor(doc); c.setPosition(fr.position()); c.setPosition(fr.position() + 1, QTextCursor.KeepAnchor)
                        e.setTextCursor(c); e.setFocus()
                        return
                    it += 1
                b = b.next()
        self.w.statusBar().showMessage("Im Dokument gibt es keine Bilder.", 4000)

    def zeichenumriss(self, k=None):
        if self.ed:
            self.ed.set_outline(not self.an_zeichenumriss())

    def an_zeichenumriss(self): return self._fmt().textOutline().style() != Qt.NoPen


    # Zeichenschattierung (Start ▸ „A“ im Kasten): graue Fläche hinter dem Text, ein/aus; Hervorheben bleibt die bunte Markierung
    SCHATTIERUNG = BF.VORGABE_SCHATTIERUNG

    def zeichenschattierung(self, k=None):
        if self.ed: self.ed.set_highlight(None if self.an_zeichenschattierung() else QColor(self.SCHATTIERUNG))

    def an_zeichenschattierung(self):
        f = self._fmt()
        return f.background().style() != Qt.NoBrush and f.background().color().name() == self.SCHATTIERUNG

    def texteffekte(self, k=None):
        """„Texteffekte formatieren“ in der rechten Seitenleiste: die Änderungen wirken sofort an der Markierung, solange der Bereich offen ist."""
        if not self.ed:
            return
        self.w.texteffekte_seitenleiste()

    def _effekt_setzen(self, **teile) -> None:
        """Einen Teil der Texteffekte der Markierung ersetzen (Wert ``None`` nimmt ihn weg); die übrigen Effekte bleiben."""
        if not self.ed:
            return
        from lunivo_writer.editor import texteffekt
        w = texteffekt.aus_format(self._fmt())
        for k, v in teile.items():
            if v is None:
                w.pop(k, None)
            else:
                w[k] = v
        self.ed._merge(texteffekt.zu_format(w))

    def menue_texteffekteKlappe(self):
        """Menü am Knopf „Texteffekte“ wie in der Vorlage: WordArt, Schatten, Spiegelung, Leuchteffekt (je mit Bildchen zum Anklicken), 3D-Drehung und
        Transformieren (nur für Formen und Textfelder, hier ausgegraut), „Weitere Texteffekte …“ öffnet die Seitenleiste."""
        from lunivo_writer.editor import texteffekt, textfx
        from lunivo_writer.ui.baukasten.dropdown.voreinstellung_menue import VoreinstellungMenue
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()

        def untermenue(titel: str, keine: tuple | None) -> VoreinstellungMenue:
            u = VoreinstellungMenue(m, keine=keine); u.setTitle(titel); m.addMenu(u)
            return u
        wa = untermenue("WordArt", None)
        vor = textfx.wordart_vorgaben()
        wa.abschnitt("Formatvorlage", [(str(i), textfx.wordart_icon(w, (56, 44)), n) for i, (n, w) in enumerate(vor)], 6)
        wa.gewaehlt.connect(lambda k: self.ed and self.ed._merge(texteffekt.zu_format({**texteffekt.EFFEKT, **vor[int(k)][1]})))
        sc = untermenue("Schatten", ("Kein Schatten", textfx.voreinstellung_icon({})))
        sv = textfx.schatten_vorgaben()
        for abschnitt in ("Außen", "Innen", "Perspektive"):
            sc.abschnitt(abschnitt, [(str(i), textfx.voreinstellung_icon({"schatten": s}), n) for i, (a, n, s) in enumerate(sv) if a == abschnitt], 3)
        sc.gewaehlt.connect(lambda k: self._effekt_setzen(schatten=sv[int(k)][2] if k else None))
        sp = untermenue("Spiegelung(&R)", ("Keine Spiegelung", textfx.voreinstellung_icon({})))
        rv = textfx.reflektion_vorgaben()
        sp.abschnitt("Spiegelungsvarianten", [(str(i), textfx.voreinstellung_icon({"reflektion": r}), n) for i, (n, r) in enumerate(rv)], 3)
        sp.gewaehlt.connect(lambda k: self._effekt_setzen(reflektion=rv[int(k)][1] if k else None))
        le = untermenue("Leuchteffekt(&G)", ("Kein Leuchteffekt", textfx.voreinstellung_icon({})))
        lv = textfx.leuchten_vorgaben()
        le.abschnitt("Leuchtvarianten", [(str(i), textfx.voreinstellung_icon({"leuchten": g}), n) for i, (n, g) in enumerate(lv)], 6)
        le.gewaehlt.connect(lambda k: self._effekt_setzen(leuchten=lv[int(k)][1] if k else None))
        for titel in ("3D-Drehung", "Transformieren"): # wie in der Vorlage: nur für Formen und Textfelder, sonst ausgegraut
            a = m.untermenue(titel, aktiv=False)
        m.addSeparator()
        m.eintrag("Weitere Texteffekte(&O) …", self.texteffekte)
        return m

    def texteffekteFenster(self, k=None):
        """Dasselbe als eigenes Fenster (mit „OK“), wie es das Schriftart-Fenster und die Formatvorlage benutzen."""
        if not self.ed:
            return
        from lunivo_writer.editor import texteffekt
        from lunivo_writer.ui.baukasten.formatierung.texteffekt_dialog import TexteffektDialog
        d = TexteffektDialog(self.w, texteffekt.aus_format(self._fmt()))
        if d.exec():
            self.ed._merge(texteffekt.zu_format(d.werte()))

    def effekt(self, k=None):
        if not self.ed:
            return
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Kapitälchen", lambda: self.ed.set_capitalization(QFont.SmallCaps))
        m.eintrag("Großbuchstaben (Anzeige)", lambda: self.ed.set_capitalization(QFont.AllUppercase))
        m.eintrag("Normal", lambda: self.ed.set_capitalization(QFont.MixedCase))
        m.addSeparator()
        m.eintrag("Texteffekte …", self.texteffekte)
        m.addSeparator()
        for t, px in (("Zeichenabstand: eng", -1.0), ("Zeichenabstand: normal", 0.0), ("Zeichenabstand: weit", 2.0),
                      ("Zeichenabstand: sehr weit", 4.0)):
            m.eintrag(t, lambda px=px: self.ed.set_letter_spacing(px))
        self._popup(m)

    def durch(self, k=None):
        if self.ed: self.ed.toggle_strike(not self.an_durch())

    def an_durch(self): return self._fmt().fontStrikeOut()

    def hoch(self, k=None):
        if self.ed: self.ed.set_script(None if self.an_hoch() else "sup")

    def an_hoch(self): return self._fmt().verticalAlignment() == QTextCharFormat.AlignSuperScript

    def tief(self, k=None):
        if self.ed: self.ed.set_script(None if self.an_tief() else "sub")

    def an_tief(self): return self._fmt().verticalAlignment() == QTextCharFormat.AlignSubScript


    # Menü „Groß-/Kleinschreibung“: vier Einträge; der Knopf zeigt das Symbol des zuletzt gewählten und führt ihn beim Klicken wieder aus
    _AA = (("umwandeln", "Groß-/Kleinschreibung umwandeln …", "schreibweise", "schreibweiseFenster"),
           ("umschlossen", "Eingeschlossene Zeichen …", "umschlossen", "umschlosseneZeichen"),
           ("umriss", "Zeichenumriss", "umriss", "zeichenumriss"),
           ("phonetisch", "Phonetisches Leitzeichen …", "phonetisch", "phonetischesLeitzeichen"))

    def schreibweise(self, k=None):
        wahl = getattr(self, "_aa", "umwandeln")
        getattr(self, next(b for a, _t, _s, b in self._AA if a == wahl))()

    def symbolname_schreibweise(self) -> str:
        wahl = getattr(self, "_aa", "umwandeln")
        return next(s for a, _t, s, _b in self._AA if a == wahl)

    def _aa_waehlen(self, wahl: str) -> None:
        self._aa = wahl
        self.w.band.aktualisieren()
        self.schreibweise()

    def menue_schreibweiseKlappe(self):
        from lunivo_writer.ui.widgets import icons
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for wahl, text, symbol, _b in self._AA:
            m.eintrag(text, lambda w=wahl: self._aa_waehlen(w), symbol=icons.icon(symbol, 16))
        return m

    def schreibweiseFenster(self, k=None):
        """Das Fenster „Groß-/Kleinschreibung“ (Zusatzfenster in der Seitenleiste)."""
        if not self.ed:
            return
        from lunivo_writer.ui.baukasten.controls.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.formatierung.schreibweise_dialog import SchreibweiseDialog
        d = SchreibweiseDialog(self.w, getattr(self, "_schreibweise", "satz"))
        if ausfuehren(d):
            self._schreibweise = d.art()
            self.ed.change_case(self._schreibweise)

    def zeichenSkalierung(self, k=None, prozent=100):
        """Zeichenskalierung: Breite der Zeichen des gewählten Texts in Prozent (wie „Skalieren“ im Fenster Schriftart)."""
        if self.ed:
            f = QTextCharFormat(); f.setFontStretch(int(prozent)); self.ed._merge(f)

    def zeichenSkalierungJetzt(self):
        """Aktuelle Zeichenskalierung in Prozent am Cursor (für den Haken im Menü Zeichen-Layout)."""
        if not self.ed:
            return 100
        cf = self.ed.currentCharFormat()
        return int(cf.fontStretch() or 100)

    def umschlosseneZeichen(self, k=None):
        """Das Fenster „Eingeschlossene Zeichen“: der gewählte Text bekommt Kreis, Quadrat, Dreieck oder Raute."""
        if not self.ed:
            return
        from lunivo_writer.editor import zeichenzusatz as Z
        from lunivo_writer.editor.zusatz import P_UMSCHLOSSEN
        from lunivo_writer.ui.baukasten.controls.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.formatierung.umschlossen_dialog import UmschlosseneZeichenDialog
        c = self.ed.textCursor()
        d = UmschlosseneZeichenDialog(self.w, c.selectedText().replace("\u2029", " "))
        if not ausfuehren(d):
            return
        w = d.werte()
        if not w["text"]:
            return
        f = QTextCharFormat(c.charFormat()); f.setProperty(P_UMSCHLOSSEN, Z.umschlossen_text(w["form"], w["vorlage"]))
        c.beginEditBlock(); c.insertText(w["text"], f); c.endEditBlock()

    def phonetischesLeitzeichen(self, k=None):
        """Das Fenster „Phonetisches Leitzeichen“: Leittext über dem gewählten Text."""
        if not self.ed:
            return
        from lunivo_writer.editor import zeichenzusatz as Z
        from lunivo_writer.editor.zusatz import P_RUBY
        from lunivo_writer.ui.baukasten.controls.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.formatierung.ruby_dialog import RubyDialog
        c = self.ed.textCursor()
        text = c.selectedText().replace("\u2029", " ")
        if not text:
            self.w.statusBar().showMessage("Phonetisches Leitzeichen: erst den Text markieren.", 4000)
            return
        d = RubyDialog(self.w, [(ch, "") for ch in text], self.ed.currentCharFormat().font().family())
        if not ausfuehren(d):
            return
        basis_format = c.charFormat()
        c.beginEditBlock()
        c.removeSelectedText()
        for basis, ruby, wie in d.zeilen():
            f = QTextCharFormat(basis_format); f.setProperty(P_RUBY, Z.ruby_text(ruby, wie["ausrichtung"], wie["abstand"], wie["groesse"]))
            c.insertText(basis, f)
        c.endEditBlock()

    def _farbmenue(self, setzen, ohne_text, vorschau=None, **opt):
        """Die gemeinsame Farbpalette; ``setzen`` bekommt eine QColor oder None („keine“)."""
        m = FarbPalette(self.w, keine_text=ohne_text, **opt)
        m.gewaehlt.connect(lambda c: self.ed and setzen(c))
        if vorschau is not None:                              # Live-Vorschau beim Überfahren der Farben
            m.ueberfahren.connect(lambda c: self.w.vorschau.zeigen(lambda e: vorschau(c)))
            m.verlassen.connect(self.w.vorschau.ende)
            m.aboutToHide.connect(self.w.vorschau.ende)
        return m

    def schriftfarbeJetzt(self, k=None):
        if self.ed: self.ed.set_text_color(QColor(getattr(self, "_schriftfarbe", Farbe.ROT)))

    def menue_schriftfarbeKlappe(self):
        def setze(c):
            self._schriftfarbe = c.name() if c else Farbe.SCHWARZ
            self.ed.set_text_color(c)
        return self._farbmenue(setze, "Automatisch", lambda c: self.ed.set_text_color(c))

    def hervorhebenJetzt(self, k=None):
        if self.ed: self.ed.set_highlight(QColor(getattr(self, "_marker", BF.VORGABE_MARKER)))

    def menue_hervorhebenKlappe(self):
        def setze(c):
            self._marker = c.name() if c else BF.VORGABE_MARKER
            self.ed.set_highlight(c)
        return self._farbmenue(setze, "Keine Hervorhebung", lambda c: self.ed.set_highlight(c))


    # ---- Absatz ---------------------------------------------------------------------------------------
