"""TextZeichenBefehle: fachlich abgegrenzte Bandbefehle."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt  # noqa: F401
from PySide6.QtGui import QColor  # noqa: F401
from PySide6.QtWidgets import QMenu, QMessageBox  # noqa: F401
from core.layout.drucklayout.formatwerte import schrift as schrift_von
from vcl.qt.rendering.formen import Linie  # noqa: F401
from vcl.qt.widgets.bausteine import FarbPalette, RahmenMenue, RasterAuswahl  # noqa: F401
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe  # noqa: F401
from vcl.qt.widgets.bausteine.farben import farben as BF  # noqa: F401


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

    def _zeichen_dict(self) -> dict:
        """Das wirksame Zeichenformat an der Schreibmarke als Wörterbuch (Modellnamen); in Kopf-/Fußzeile aus deren Feld."""
        if not self.ed:
            return {}
        return self.ed.zeichenformat()

    def an_fett(self):
        return schrift_von(self._zeichen_dict()).weight >= 600

    def kursiv(self, k=None):
        if self.ed: self.ed.toggle_italic(not self.an_kursiv())

    def an_kursiv(self): return bool(self._zeichen_dict().get("kursiv"))

    def unter(self, k=None):
        if self.ed: self.ed.toggle_underline(not self.an_unter())

    def an_unter(self): return bool(self._zeichen_dict().get("unterstrichen") or self._zeichen_dict().get("unter_stil"))


    # Linien im Menü am Knopf „Unterstrichen“ — dieselben acht wie in der Vorlage, als Bild
    UNTER_MENUE = ("einfach", "doppelt", "dick", "gepunktet", "gestrichelt", "strichpunkt", "strichpunktpunkt", "wellig")

    def menue_unterstrichKlappe(self):
        """Wie in der Vorlage: die Linienarten als Bild, „Mehr Unterstreichungen …“ (Fenster Schriftart) und „Unterstreichungsfarbe“ mit der
        gemeinsamen Farbpalette."""
        from vcl.qt.rendering.wordart import unter_zeichnen
        from vcl.qt.widgets.bausteine.rahmen.linien import linien_menue_zeile
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for art in self.UNTER_MENUE:
            linien_menue_zeile(m, "", art, 1.0, lambda a=art: self.ed and self.ed._zf({"unterstrichen": True, "unter_art": None if a == "einfach" else a}),
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
        aenderung = {} if self.an_unter() else {"unterstrichen": True}
        aenderung["unter_farbe"] = farbe.name() if farbe is not None and farbe.isValid() else None
        self.ed._zf(aenderung)


    # Knopf „Durchgestrichen“ mit Klappe wie in der Vorlage: Durchgestrichen oder Betonungszeichen; der Knopf führt das zuletzt Gewählte aus
    _DURCH = (("durch", "Durchgestrichen", "durchgestrichen"), ("betonung", "Betonungszeichen", "betonung"))

    def durchJetzt(self, k=None):
        self.betonung() if getattr(self, "_durch_art", "durch") == "betonung" else self.durch()

    def an_durchJetzt(self):
        return self.an_betonung() if getattr(self, "_durch_art", "durch") == "betonung" else self.an_durch()

    def symbolname_durchJetzt(self) -> str:
        return next(s for a, _t, s in self._DURCH if a == getattr(self, "_durch_art", "durch"))

    def menue_durchKlappe(self):
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        m = MenueListe()
        for art, text, symbol in self._DURCH:
            m.eintrag(text, lambda a=art: self._durch_waehlen(a), symbol=symbole.icon(symbol, 16))
        return m

    def _durch_waehlen(self, art: str) -> None:
        self._durch_art = art
        self.durchJetzt()
        self.w.band.aktualisieren()

    def betonung(self, k=None):
        """Betonungszeichen (Punkt über jedem Buchstaben) an- oder ausschalten; andere Zeichen wählt das Fenster „Schriftart“."""
        if self.ed:
            self.ed._zf({"betonung": None if self.an_betonung() else "punkt"})

    def an_betonung(self):
        return bool(self._zeichen_dict().get("betonung"))

    def menue_einstellungenKlappe(self):
        """Knopf „Einstellungen“ wie in der Vorlage: die Fenster des Reiters Start."""
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        m = MenueListe()
        m.eintrag("Schriftart …", self.schriftartMehr, symbol=symbole.icon("schriftFenster", 16), kuerzel="Strg+D")
        m.eintrag("Absatz …", self.einzugGenau, symbol=symbole.icon("absatzFenster", 16))
        m.eintrag("Formatvorlagen und Formatierung …", self.formatvorlagenBereich, symbol=symbole.icon("pinsel", 16))
        return m

    def formatvorlagenBereich(self, k=None):
        """„Formatvorlagen und Formatierung“: die Liste aller Formatvorlagen in der rechten Seitenleiste (wie der Bereich der Vorlage)."""
        if not self.ed:
            return
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
        from vcl.qt.widgets.seitenleisten.vorlagen.formatvorlagen_bereich import FormatvorlagenBereich
        ausfuehren(FormatvorlagenBereich(self.w, self.w.current_editor, self.w.stil_anwenden, self.neueFormatvorlage))

    def objekteWaehlen(self, k=None):
        """Springt zum nächsten Bild im Text und markiert es (dann erscheinen die Bildtools)."""
        e = self.ed
        if not e:
            return
        if e.naechstes_objekt_waehlen():
            return
        self.w.statusBar().showMessage("Im Dokument gibt es keine Bilder.", 4000)

    def zeichenumriss(self, k=None):
        if self.ed:
            self.ed.set_outline(not self.an_zeichenumriss())

    def an_zeichenumriss(self):
        e = self._zeichen_dict().get("effekt")
        return bool(e.get("kontur")) if isinstance(e, dict) else bool(e) and "kontur" in str(e)


    # Zeichenschattierung (Start ▸ „A“ im Kasten): graue Fläche hinter dem Text, ein/aus; Hervorheben bleibt die bunte Markierung
    SCHATTIERUNG = BF.VORGABE_SCHATTIERUNG

    def zeichenschattierung(self, k=None):
        if self.ed: self.ed.set_highlight(None if self.an_zeichenschattierung() else QColor(self.SCHATTIERUNG))

    def an_zeichenschattierung(self):
        return str(self._zeichen_dict().get("marker") or "")[:7].lower() == self.SCHATTIERUNG.lower()

    def texteffekte(self, k=None):
        """„Texteffekte formatieren“ in der rechten Seitenleiste: die Änderungen wirken sofort an der Markierung, solange der Bereich offen ist."""
        if not self.ed:
            return
        self.w.texteffekte_seitenleiste()

    def _effekt_setzen(self, **teile) -> None:
        """Einen Teil der Texteffekte der Markierung ersetzen (Wert ``None`` nimmt ihn weg); die übrigen Effekte bleiben."""
        if not self.ed:
            return
        from vcl.qt.rendering import wordart as texteffekt
        w = texteffekt.aus_zeichen(self._zeichen_dict())
        for k, v in teile.items():
            if v is None:
                w.pop(k, None)
            else:
                w[k] = v
        self.ed._zf(texteffekt.zu_zeichen(w))

    def menue_texteffekteKlappe(self):
        """Menü am Knopf „Texteffekte“ wie in der Vorlage: WordArt, Schatten, Spiegelung, Leuchteffekt (je mit Bildchen zum Anklicken), 3D-Drehung und
        Transformieren (nur für Formen und Textfelder, hier ausgegraut), „Weitere Texteffekte …“ öffnet die Seitenleiste."""
        from vcl.qt.rendering import wordart as texteffekt
        from vcl.qt.rendering import wordart as textfx
        from vcl.qt.rendering import wordart as textfx_vorgaben
        from vcl.qt.widgets.menues.dropdown.voreinstellung_menue import VoreinstellungMenue
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()

        def untermenue(titel: str, keine: tuple | None) -> VoreinstellungMenue:
            u = VoreinstellungMenue(m, keine=keine); u.setTitle(titel); m.addMenu(u)
            return u
        wa = untermenue("WordArt", None)
        vor = textfx.wordart_vorgaben()
        wa.abschnitt("Formatvorlage", [(str(i), textfx_vorgaben.wordart_icon(w, (56, 44)), n) for i, (n, w) in enumerate(vor)], 6)
        wa.gewaehlt.connect(lambda k: self.ed and self.ed._zf(texteffekt.zu_zeichen({**texteffekt.EFFEKT, **vor[int(k)][1]})))
        sc = untermenue("Schatten", ("Kein Schatten", textfx_vorgaben.voreinstellung_icon({})))
        sv = textfx.schatten_vorgaben()
        for abschnitt in ("Außen", "Innen", "Perspektive"):
            sc.abschnitt(abschnitt, [(str(i), textfx_vorgaben.voreinstellung_icon({"schatten": s}), n) for i, (a, n, s) in enumerate(sv) if a == abschnitt], 3)
        sc.gewaehlt.connect(lambda k: self._effekt_setzen(schatten=sv[int(k)][2] if k else None))
        sp = untermenue("Spiegelung(&R)", ("Keine Spiegelung", textfx_vorgaben.voreinstellung_icon({})))
        rv = textfx.reflektion_vorgaben()
        sp.abschnitt("Spiegelungsvarianten", [(str(i), textfx_vorgaben.voreinstellung_icon({"reflektion": r}), n) for i, (n, r) in enumerate(rv)], 3)
        sp.gewaehlt.connect(lambda k: self._effekt_setzen(reflektion=rv[int(k)][1] if k else None))
        le = untermenue("Leuchteffekt(&G)", ("Kein Leuchteffekt", textfx_vorgaben.voreinstellung_icon({})))
        lv = textfx.leuchten_vorgaben()
        le.abschnitt("Leuchtvarianten", [(str(i), textfx_vorgaben.voreinstellung_icon({"leuchten": g}), n) for i, (n, g) in enumerate(lv)], 6)
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
        from vcl.qt.rendering import wordart as texteffekt
        from vcl.qt.widgets.dialoge.formatierung.texteffekt_dialog import TexteffektDialog
        d = TexteffektDialog(self.w, texteffekt.aus_zeichen(self._zeichen_dict()))
        if d.exec():
            self.ed._zf(texteffekt.zu_zeichen(d.werte()))

    def effekt(self, k=None):
        if not self.ed:
            return
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Kapitälchen", lambda: self.ed.set_capitalization("kapitaelchen"))
        m.eintrag("Großbuchstaben (Anzeige)", lambda: self.ed.set_capitalization("gross"))
        m.eintrag("Normal", lambda: self.ed.set_capitalization("normal"))
        m.addSeparator()
        m.eintrag("Texteffekte …", self.texteffekte)
        m.addSeparator()
        for t, px in (("Zeichenabstand: eng", -1.0), ("Zeichenabstand: normal", 0.0), ("Zeichenabstand: weit", 2.0),
                      ("Zeichenabstand: sehr weit", 4.0)):
            m.eintrag(t, lambda px=px: self.ed.set_letter_spacing(px))
        self._popup(m)

    def durch(self, k=None):
        if self.ed: self.ed.toggle_strike(not self.an_durch())

    def an_durch(self): return bool(self._zeichen_dict().get("durchgestrichen"))

    def hoch(self, k=None):
        if self.ed: self.ed.set_script(None if self.an_hoch() else "sup")

    def an_hoch(self): return self._zeichen_dict().get("hoch_tief") == "hoch"

    def tief(self, k=None):
        if self.ed: self.ed.set_script(None if self.an_tief() else "sub")

    def an_tief(self): return self._zeichen_dict().get("hoch_tief") == "tief"


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
        from vcl.qt.widgets.bausteine.symbole.bauteile import symbole
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for wahl, text, symbol, _b in self._AA:
            m.eintrag(text, lambda w=wahl: self._aa_waehlen(w), symbol=symbole.icon(symbol, 16))
        return m

    def schreibweiseFenster(self, k=None):
        """Das Fenster „Groß-/Kleinschreibung“ (Zusatzfenster in der Seitenleiste)."""
        if not self.ed:
            return
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
        from vcl.qt.widgets.dialoge.formatierung.schreibweise_dialog import SchreibweiseDialog
        d = SchreibweiseDialog(self.w, getattr(self, "_schreibweise", "satz"))
        if ausfuehren(d):
            self._schreibweise = d.art()
            self.ed.change_case(self._schreibweise)

    def zeichenSkalierung(self, k=None, prozent=100):
        """Zeichenskalierung: Breite der Zeichen des gewählten Texts in Prozent (wie „Skalieren“ im Fenster Schriftart)."""
        if self.ed:
            self.ed._zf({"skalierung": float(prozent) if int(prozent) not in (0, 100) else None})

    def zeichenSkalierungJetzt(self):
        """Aktuelle Zeichenskalierung in Prozent am Cursor (für den Haken im Menü Zeichen-Layout)."""
        if not self.ed:
            return 100
        return int(self._zeichen_dict().get("skalierung") or 100)

    def umschlosseneZeichen(self, k=None):
        """Das Fenster „Eingeschlossene Zeichen“: der gewählte Text bekommt Kreis, Quadrat, Dreieck oder Raute."""
        if not self.ed:
            return
        from writer.anbindung import zeichenzusatz as Z
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
        from vcl.qt.widgets.dialoge.formatierung.umschlossen_dialog import UmschlosseneZeichenDialog
        c = self.ed.textCursor()
        d = UmschlosseneZeichenDialog(self.w, c.selectedText().replace("\u2029", " "))
        if not ausfuehren(d):
            return
        w = d.werte()
        if not w["text"]:
            return
        zeichen = {"umschlossen": Z.umschlossen_text(w["form"], w["vorlage"])}
        self.ed.ansicht._aendern(lambda s: s.text_einfuegen(w["text"], format=zeichen))                # ersetzt die Auswahl, ein Schritt

    def phonetischesLeitzeichen(self, k=None):
        """Das Fenster „Phonetisches Leitzeichen“: Leittext über dem gewählten Text."""
        if not self.ed:
            return
        from writer.anbindung import zeichenzusatz as Z
        from vcl.qt.widgets.bausteine.zustaende.geruest.fenster_stapel import ausfuehren
        from vcl.qt.widgets.dialoge.formatierung.ruby_dialog import RubyDialog
        c = self.ed.textCursor()
        text = c.selectedText().replace("\u2029", " ")
        if not text:
            self.w.statusBar().showMessage("Phonetisches Leitzeichen: erst den Text markieren.", 4000)
            return
        d = RubyDialog(self.w, [(ch, "") for ch in text], schrift_von(self._zeichen_dict()).family)
        if not ausfuehren(d):
            return
        teile = d.zeilen()

        def schreiben(s):
            with s.gruppe("Phonetisches Leitzeichen"):
                if not s.auswahl.leer:
                    s.loeschen()
                for basis, ruby, wie in teile:
                    s.text_einfuegen(basis, format={"ruby": Z.ruby_text(ruby, wie["ausrichtung"], wie["abstand"], wie["groesse"])})
        self.ed.ansicht._aendern(schreiben)

    def _farbmenue(self, setzen, ohne_text, vorschau=None, **opt):
        """Die gemeinsame Farbpalette; ``setzen`` bekommt eine QColor oder None („keine“)."""
        m = FarbPalette(self.w, keine_text=ohne_text, **opt)
        def gewaehlt(c):
            self.w.vorschau.ende()                            # erst die Vorschau zurücknehmen; sonst nähme ihr Ende beim Schließen die gewählte Farbe mit
            if self.ed:
                setzen(c)
        m.gewaehlt.connect(gewaehlt)
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
