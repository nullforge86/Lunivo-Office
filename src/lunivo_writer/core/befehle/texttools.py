"""Befehle: Kontext-Reiter „Texttools“ (und die Galerien von „Zeichentools“) für die freien Objekte WordArt und Textfeld.

Alle ``tt…``-Befehle ändern die Angaben des markierten freien Objekts über ``editor/frei_objekt`` (``ziel``, ``aendern``); die Form
(Füllung, Kontur, Effekte, Formstile) nutzt dieselben Wege und Menüs wie der Reiter Zeichentools (``FreiMenue``, ``_frei_wirken``).
Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""
from __future__ import annotations

from PySide6.QtCore import QRectF, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPixmap
from PySide6.QtWidgets import QMenu

from lunivo_writer.core.befehle.text import ZEILENABSTAENDE
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten import FarbPalette

STRICHE = (0.5, 1.0, 2.0, 3.0, 5.0, 8.0)
WA_STILKACHELN = (0, 1, 2)                    # die drei Kacheln im Band: Schwarz, Blau, Orange (wie in der Vorlage)
FORMSTIL_KACHELN = ("z00", "z01", "z02")      # Abc mit schwarzem, blauem, orangem Rand


class TextToolsBefehle:
    TEXTRICHTUNGEN = [("waagerecht", "Horizontal"), ("senkrecht_rl", "Vertikal von rechts nach links"),
                      ("senkrecht_lr", "Vertikal von links nach rechts"), ("dreh90", "Gesamten Text um 90 Grad drehen"),
                      ("dreh270", "Gesamten Text um 270 Grad drehen"), ("asiatisch270", "Asiatische Zeichen um 270 Grad drehen")]

    # ==== Erkennung ===================================================================================================================
    def tt_art(self) -> str | None:
        """Welches freie Textobjekt ist markiert? ``wordart`` | ``textfeld`` | None."""
        from lunivo_writer.editor import frei_objekt as FO
        art = FO.art_gewaehlt(self.ed) if self.ed else None
        return art if art in FO.TEXT_ARTEN else None


    def _wa(self) -> dict:
        from lunivo_writer.editor import frei_objekt as FO
        z = FO.ziel(self.ed) if self.ed else None
        return z[1] if z and z[0] in FO.TEXT_ARTEN else {}


    def _wa_set(self, **kw) -> bool:
        """Angaben des markierten WordArt/Textfelds ändern; ohne Auswahl ein Hinweis in der Statuszeile."""
        from lunivo_writer.editor import frei_objekt as FO
        art = self.tt_art()
        if not (art and FO.aendern(self.ed, art, **kw)):
            self.w.lbl_msg.setText("Bitte zuerst ein WordArt oder Textfeld markieren.")
            return False
        self.w.band.aktualisieren()
        return True


    # ==== WordArt: Schrift =============================================================================================================
    def ttSchriftart(self, name):
        self._wa_set(schrift=str(name))


    def ttGroesse(self, pt):
        try:
            pt = float(str(pt).replace(",", "."))
        except ValueError:
            return
        if 1 <= pt <= 400:
            self._wa_set(pt=pt)


    def _tt_pt(self, delta):
        pt = float(self._wa().get("pt", 36 if self.tt_art() == "wordart" else 11))
        self._wa_set(pt=max(1.0, min(400.0, pt + delta)))


    def ttGroesser(self, k=None): self._tt_pt(2)

    def ttKleiner(self, k=None): self._tt_pt(-2)


    def ttSchlicht(self, k=None):
        """Formatierung löschen: Schrift, Auszeichnungen, Hervorhebung, Effekte, Liste und Absatzwerte zurück auf die Vorgabe der Vorlage."""
        self._wa_set(schrift=None, pt=None, fett=None, kursiv=None, unter=None, durch=None, hoch=None, tief=None, hervor=None, effekt=None,
                     liste=None, einzug=None, richtung=None, zeilenabstand=None, ausr=None, fuell=None, kontur=None, kontur_breite=None)


    def _tt_umschalten(self, schl, standard=False):
        self._wa_set(**{schl: not bool(self._wa().get(schl, standard))})


    def ttFett(self, k=None): self._tt_umschalten("fett", self.tt_art() == "wordart")

    def an_ttFett(self): return bool(self._wa().get("fett", self.tt_art() == "wordart"))

    def ttKursiv(self, k=None): self._tt_umschalten("kursiv")

    def an_ttKursiv(self): return bool(self._wa().get("kursiv", False))

    def ttUnter(self, k=None): self._wa_set(unter=None if self._wa().get("unter") else "einfach")

    def an_ttUnter(self): return bool(self._wa().get("unter"))

    def ttDurch(self, k=None): self._tt_umschalten("durch")

    def an_ttDurch(self): return bool(self._wa().get("durch"))


    def ttHoch(self, k=None):
        self._wa_set(hoch=not self._wa().get("hoch", False), tief=None)

    def an_ttHoch(self): return bool(self._wa().get("hoch"))


    def ttTief(self, k=None):
        self._wa_set(tief=not self._wa().get("tief", False), hoch=None)

    def an_ttTief(self): return bool(self._wa().get("tief"))


    def menue_ttUnter(self):
        """Wie bei Start: die Linienarten als Bild, „Mehr Unterstreichungen …“ und die Unterstreichungsfarbe; wirkt auf das Objekt."""
        from lunivo_writer.editor.textfx import unter_zeichnen
        from lunivo_writer.ui.baukasten.linien import linien_menue_zeile
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        for art in self.UNTER_MENUE:
            linien_menue_zeile(m, "", art, 1.0, lambda a=art: self._wa_set(unter=a),
                               maler=lambda p, x0, y, x1, farbe, a=art: unter_zeichnen(p, x0, y, x1, a, farbe))
        m.trenner()
        m.eintrag("Mehr Unterstreichungen …", self._tt_unter_dialog)
        pal = FarbPalette(m, keine_text="Automatisch", weitere_text="Weitere Unterstreichungsfarben …", titel="Unterstreichungsfarbe", pipette=False)
        pal.setTitle("Unterstreichungsfarbe")
        pal.gewaehlt.connect(lambda c: self._wa_set(unter=self._wa().get("unter") or "einfach", unterfarbe=c.name() if c is not None else None))
        m.addMenu(pal)
        return m


    def _tt_unter_dialog(self) -> None:
        """Das Fenster „Schriftart“ mit der Unterstreichung des Objekts; übernommen werden Art und Farbe der Linie."""
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.schriftart_dialog import SchriftartDialog
        from lunivo_writer.ui.baukasten.text_format import ZEICHEN
        d0 = self._wa()
        u = d0.get("unter")
        w = dict(ZEICHEN, unter=u if isinstance(u, str) else ("einfach" if u else ""), unterfarbe=d0.get("unterfarbe") or "")
        d = SchriftartDialog(self.w, w)
        if ausfuehren(d):
            neu = d.werte()
            self._wa_set(unter=neu.get("unter") or None, unterfarbe=(neu.get("unterfarbe") or None) if neu.get("unter") else None)


    def menue_ttDurch(self):
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Durchgestrichen", self.ttDurch)
        m.eintrag("Nicht durchgestrichen", lambda: self._wa_set(durch=None))
        return m


    def ttHervorJetzt(self, k=None):
        self._wa_set(hervor=getattr(self, "_marker", "#ffec99"))


    def menue_ttHervor(self):
        def setze(c):
            if c is not None:
                self._marker = c.name()
            self._wa_set(hervor=c.name() if c is not None else None)
        m = FarbPalette(self.w, keine_text="Keine Hervorhebung", titel="Hervorhebung")
        m.gewaehlt.connect(setze)
        return m


    def ttSchriftfarbeJetzt(self, k=None):
        self._wa_set(fuell=getattr(self, "_schriftfarbe", Farbe.ROT))


    def menue_ttSchriftfarbe(self):
        def setze(c):
            if c is not None:
                self._schriftfarbe = c.name()
            self._wa_set(fuell=c.name() if c is not None else None)
        m = FarbPalette(self.w, keine_text="Automatisch", titel="Schriftfarbe")
        m.gewaehlt.connect(setze)
        return m


    # ==== WordArt: Absatz ==============================================================================================================
    def _tt_liste_setzen(self, spec) -> None:
        """Aufzählung/Nummerierung des Objekts: dieselben Angaben wie im Start-Reiter (``editor/listen``), ``None`` = keine Liste."""
        self._wa_set(liste=spec or None)


    def _tt_liste_ist(self, aufzaehlung: bool) -> bool:
        from lunivo_writer.editor import listen as L, mehrstufig as M
        spec = self._wa().get("liste")
        if not isinstance(spec, dict):
            return False
        if "ebenen" in spec:
            return M.ist_aufzaehlung(spec) == aufzaehlung
        return L.STILE.get(spec.get("stil"), ("", None))[1] == aufzaehlung


    def ttPunkte(self, k=None):
        from lunivo_writer.editor import listen as L
        self._tt_liste_setzen(None if self._tt_liste_ist(True) else L.liste("disc"))

    def an_ttPunkte(self): return self._tt_liste_ist(True)

    def ttZahlen(self, k=None):
        from lunivo_writer.editor import listen as L
        self._tt_liste_setzen(None if self._tt_liste_ist(False) else L.liste("dezimal", "", "."))

    def an_ttZahlen(self): return self._tt_liste_ist(False)


    def _tt_listenraster(self, art: str, titel: str):
        """Dieselbe Auswahl wie bei Start (alle Aufzählungszeichen und Nummerierungen), gilt für den Text im Objekt."""
        from lunivo_writer.ui.baukasten.liste_dialog import aufzaehlungen, kachel_bild, nummerierungen
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        arten = aufzaehlungen() if art == "bullet" else nummerierungen()
        r = RasterAuswahl(self.w, titel=titel, spalten=4, groesse=QSize(96, 68))
        r.kachel("keine", "Keine", kachel_bild(None, QSize(96, 68)))
        for i, spec in enumerate(arten):
            r.kachel(str(i), "", kachel_bild(spec, QSize(96, 68)))
        r.gewaehlt.connect(lambda k: self._tt_liste_setzen(None if k == "keine" else arten[int(k)]))
        r.fuss("Weitere Aufzählungszeichen …" if art == "bullet" else "Weitere Nummerierungen …",
               lambda: self._tt_listendialog("aufzaehlung" if art == "bullet" else "nummerierung"))
        return r


    def _tt_listendialog(self, seite: str) -> None:
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.liste_dialog import ListenDialog
        d = ListenDialog(self.w, self._wa().get("liste") if isinstance(self._wa().get("liste"), dict) else None, seite=seite)
        if ausfuehren(d):
            self._tt_liste_setzen(d.ergebnis())


    def menue_ttPunkte(self): return self._tt_listenraster("bullet", "Aufzählungszeichen")

    def menue_ttZahlen(self): return self._tt_listenraster("number", "Nummerierung")


    def ttEinzugMehr(self, k=None): self._wa_set(einzug=min(8, int(self._wa().get("einzug", 0)) + 1))

    def ttEinzugWeniger(self, k=None): self._wa_set(einzug=max(0, int(self._wa().get("einzug", 0)) - 1) or None)


    def ttSortieren(self, k=None):
        """Zeilen des WordArt-Textes sortieren (A–Z, beim nächsten Mal Z–A)."""
        zeilen = str(self._wa().get("text", "")).split("\n")
        auf = sorted(zeilen, key=str.casefold)
        self._wa_set(text="\n".join(auf if zeilen != auf else auf[::-1]))


    def menue_ttTextrichtung(self):
        """Textrichtung wie in WPS (dieselben sechs Einträge mit Bildchen wie bei Start), wirkt auf den Text im Objekt."""
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl, zeilenkachel
        from lunivo_writer.ui.baukasten.seiten_bildchen import textrichtung_zeichner
        m = RasterAuswahl(self.w, spalten=1, groesse=QSize(330, 44))
        for art, text in self.TEXTRICHTUNGEN:
            m.kachel(art, text, zeilenkachel(textrichtung_zeichner(art), text, bild_breite=40))
        m.gewaehlt.connect(lambda art: self._wa_set(richtung=None if art == "waagerecht" else art))
        return m


    def _tt_ausr(self, wie): self._wa_set(ausr=wie)

    def ttLinks(self, k=None): self._tt_ausr("links")

    def ttMitte(self, k=None): self._tt_ausr("mitte")

    def ttRechts(self, k=None): self._tt_ausr("rechts")

    def ttBlock(self, k=None): self._tt_ausr("block")

    def ttVerteilt(self, k=None): self._tt_ausr("verteilt")

    def an_ttLinks(self): return self._wa().get("ausr", "links") == "links"

    def an_ttMitte(self): return self._wa().get("ausr") == "mitte"

    def an_ttRechts(self): return self._wa().get("ausr") == "rechts"

    def an_ttBlock(self): return self._wa().get("ausr") == "block"

    def an_ttVerteilt(self): return self._wa().get("ausr") == "verteilt"


    def menue_ttZeilenabstand(self):
        m = QMenu()
        for f in ZEILENABSTAENDE:
            m.addAction(f"{f:g}".replace(".", ","), lambda _=False, f=f: self._wa_set(zeilenabstand=f if f != 1.0 else None))
        return m


    # ==== WordArt: Stile, Füllung, Kontur, Effekte =====================================================================================
    def ttStil(self, nr: int):
        """WordArt-Formatvorlage (0–14) auf das markierte WordArt anwenden; die Textfüllung, Kontur und Effekte setzen sich neu."""
        self._wa_set(vorlage=int(nr), fuell=None, kontur=None, kontur_breite=None, effekt=None)


    def galerie_ttWordartStile(self):
        from lunivo_writer.editor import einfuegen as E
        kacheln = [(E.WORDART_VORLAGEN[i][0], self._wa_kachel(i), lambda i=i: self.ttStil(i)) for i in WA_STILKACHELN]
        return {"kacheln": kacheln, "menue": self.menue_ttStile(), "name": "WordArt-Stile"}


    @staticmethod
    def _wa_kachel(i: int) -> QPixmap:
        from lunivo_writer.editor import einfuegen as E
        pm = QPixmap(QSize(40, 40)); pm.fill(QColor("#f3f4f6"))              # heller Kachelgrund: auch das schwarze „A“ ist im dunklen Thema zu sehen
        img = E.wordart_bild("A", vorlage=i, pt=80).scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
        p.drawImage((40 - img.width()) // 2, (40 - img.height()) // 2, img)
        p.end()
        return pm


    def menue_ttStile(self):
        """Alle 15 Stile als „A“ auf hellem Grund (wie das Menü neben Einfügen ▸ WordArt), wirkt auf das markierte WordArt."""
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, titel="Formatvorlage", spalten=5, groesse=QSize(40, 40))
        for i, (name, *_r) in enumerate(E.WORDART_VORLAGEN):
            pm = QPixmap(QSize(40, 40)); pm.fill(QColor("#f3f4f6"))
            p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
            img = E.wordart_bild("A", vorlage=i, pt=80).scaled(34, 34, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            p.drawImage((40 - img.width()) // 2, (40 - img.height()) // 2, img); p.end()
            m.kachel(str(i), name, pm).setCheckable(False)
        m.gewaehlt.connect(lambda schl: self.ttStil(int(schl)))
        return m


    def menue_ttTextfuellung(self):
        m = FarbPalette(self.w, keine_text="Keine Füllung", titel="Textfüllung")
        m.gewaehlt.connect(lambda c: self._wa_set(fuell=c.name() if c is not None else ""))
        return m


    def menue_ttTextkontur(self):
        m = FarbPalette(self.w, keine_text="Keine Kontur", titel="Textkontur")
        m.gewaehlt.connect(lambda c: self._wa_set(kontur=c.name() if c is not None else "", **({} if c is None else {"kontur_breite": self._wa().get("kontur_breite") or 1.5})))
        m.addSeparator()
        st = m.addMenu("Linienstärke")
        for w in STRICHE:
            st.addAction(f"{w:g} pt".replace(".", ","), lambda _=False, w=w: self._wa_set(kontur_breite=w, kontur=self._wa().get("kontur") or Farbe.SCHWARZ))
        return m


    def menue_ttTexteffekte(self):
        return self._effekt_menue(lambda **t: self._wa_effekt(**t), "effekt")


    def _wa_effekt(self, **teile):
        alt = dict(self._wa().get("effekt") or {})
        for k, v in teile.items():
            if v is None:
                alt.pop(k, None)
            else:
                alt[k] = v
        self._wa_set(effekt=alt or None)


    def _effekt_menue(self, setzen, _schl):
        """Schatten, Spiegelung und Leuchteffekt mit Bildchen (wie bei Start ▸ Texteffekte); ``setzen(**teil)`` schreibt den Teil."""
        from lunivo_writer.editor import textfx
        from lunivo_writer.ui.baukasten.voreinstellung_menue import VoreinstellungMenue
        m = QMenu()

        def untermenue(titel, keine):
            u = VoreinstellungMenue(m, keine=keine); u.setTitle(titel); m.addMenu(u)
            return u
        sc = untermenue("Schatten", ("Kein Schatten", textfx.voreinstellung_icon({})))
        sv = textfx.schatten_vorgaben()
        for abschnitt in ("Außen", "Innen", "Perspektive"):
            sc.abschnitt(abschnitt, [(str(i), textfx.voreinstellung_icon({"schatten": s}), n) for i, (a, n, s) in enumerate(sv) if a == abschnitt], 3)
        sc.gewaehlt.connect(lambda k: setzen(schatten=sv[int(k)][2] if k else None))
        sp = untermenue("Spiegelung", ("Keine Spiegelung", textfx.voreinstellung_icon({})))
        rv = textfx.reflektion_vorgaben()
        sp.abschnitt("Spiegelungsvarianten", [(str(i), textfx.voreinstellung_icon({"reflektion": r}), n) for i, (n, r) in enumerate(rv)], 3)
        sp.gewaehlt.connect(lambda k: setzen(reflektion=rv[int(k)][1] if k else None))
        le = untermenue("Leuchteffekt", ("Kein Leuchteffekt", textfx.voreinstellung_icon({})))
        lv = textfx.leuchten_vorgaben()
        le.abschnitt("Leuchtvarianten", [(str(i), textfx.voreinstellung_icon({"leuchten": g}), n) for i, (n, g) in enumerate(lv)], 6)
        le.gewaehlt.connect(lambda k: setzen(leuchten=lv[int(k)][1] if k else None))
        return m


    # ---- Form (Kasten hinter dem Text): dieselben Menüs und Wege wie im Reiter Zeichentools (Baukasten, ``_frei_wirken``) -------------------
    def ttFormstil(self, schl: str):
        from lunivo_writer.ui.baukasten.objekt_menues import formstil_werte
        w = formstil_werte(schl)
        if self.ed:
            self.ed._frei_wirken(fuell=w["fuell"], rand=w["rand"])


    def galerie_ttFormstile(self):
        """Die drei Kacheln „Abc“ im Band (schwarzer, blauer, oranger Rand) und das Menü mit allen 42 Formstilen."""
        from lunivo_writer.ui.baukasten.objekt_menues import formstil_zeichner
        kacheln = []
        for k in FORMSTIL_KACHELN:
            pm = QPixmap(QSize(52, 36)); pm.fill(QColor("#ffffff"))
            p = QPainter(pm); formstil_zeichner(k)(p, QRectF(0, 0, 52, 36)); p.end()
            kacheln.append(("Formstil", pm, lambda k=k: self.ttFormstil(k)))
        from lunivo_writer.core.befehle.hilfen import FreiMenue
        return {"kacheln": kacheln, "menue": FreiMenue.formstile(self), "name": "Formstile"}


    def menue_ttFormFuellung(self):
        from lunivo_writer.core.befehle.hilfen import FreiMenue
        return FreiMenue.fuell(self)


    def menue_ttFormKontur(self):
        from lunivo_writer.core.befehle.hilfen import FreiMenue
        return FreiMenue.kontur(self)


    def ttFormEffekte(self, k=None):
        """Weitere Formeffekte: die Seitenleiste „Formatierung“ auf dem Reiter Effekte (Schatten, Reflektion, Leuchten, Weiche Kanten)."""
        if self.ed:
            self.ed._frei_effekte()


    def menue_ttFormEffekte(self):
        """Schatten, Spiegelung und Leuchteffekt der Form (wie die Voreinstellungen der Seitenleiste), darunter „Weitere Effekte …“."""
        from lunivo_writer.editor import bildlayout as BL

        def setze(**teile):
            z = BL.ziel(self.ed) if self.ed else None
            if z is None or z[0] != "frei":
                self.w.lbl_msg.setText("Bitte zuerst ein WordArt oder Textfeld markieren.")
                return
            fx = dict(z[2].get("fx") or {})
            for schl, v in teile.items():
                if v is None:
                    fx.pop(schl, None)
                else:
                    fx[schl] = dict(v)
            BL.format_setzen(self.ed, z, fx=fx)
        m = self._effekt_menue(setze, "fx")
        m.addSeparator()
        m.addAction("Weitere Effekte …", self.ttFormEffekte)
        return m


    # ==== Format übertragen, Verknüpfung, Navigation ==================================================================================
    def ttFormatUebertragen(self, k=None):
        """Format des markierten WordArt/Textfelds (Schrift, Auszeichnungen, Farben, Effekte, Form) aufnehmen; beim nächsten markierten Objekt
        denselben Knopf noch einmal drücken, dann wird es übertragen."""
        from lunivo_writer.editor import bildlayout as BL
        d = self._wa()
        schluessel = ("schrift", "pt", "fett", "kursiv", "unter", "durch", "hoch", "tief", "hervor", "fuell", "farbe", "kontur", "kontur_breite",
                      "effekt", "vorlage", "ausr", "liste", "einzug", "richtung", "zeilenabstand")
        if getattr(self, "_tt_pinsel", None) is None:
            if not d:
                self.w.lbl_msg.setText("Bitte zuerst ein WordArt oder Textfeld markieren.")
                return
            self._tt_pinsel = ({s: d.get(s) for s in schluessel}, BL.format_merken(BL.ziel(self.ed)))
            self.w.lbl_msg.setText("Format aufgenommen — jetzt ein anderes WordArt oder Textfeld markieren und den Knopf noch einmal drücken.")
            return
        text, form = self._tt_pinsel
        self._tt_pinsel = None
        if self._wa_set(**text):
            if form:
                BL.format_uebertragen(self.ed, BL.ziel(self.ed), form)
            self.w.lbl_msg.setText("Format übertragen.")


    def an_ttFormatUebertragen(self): return getattr(self, "_tt_pinsel", None) is not None


    # ---- Verknüpfung erstellen: Textfelder verketten (Text läuft von A nach B), wie in WPS ---------------------------------------------
    def _tt_felder(self):
        """Die Textfelder, mit denen das markierte verknüpft werden kann (Schlüssel, Anzeigename): nicht es selbst, keins mit Vorgänger."""
        from lunivo_writer.editor import frei_objekt as FO
        e = self.ed
        jetzt = getattr(e, "_frei_sel", None)
        out = []
        for key, a in FO._textfelder(e):
            d = a.get("daten") or {}
            if key != jetzt and not d.get("von"):
                t = str(d.get("gezeigt", d.get("text", ""))).strip().replace("\n", " ")
                out.append((key, f"Textfeld: {t[:24] or '(leer)'}"))
        return out


    def menue_ttVerknuepfung(self):
        """Das markierte Textfeld mit einem anderen verknüpfen (der Text läuft weiter) oder die Verknüpfung lösen."""
        from lunivo_writer.editor import frei_objekt as FO
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()

        def fuellen():
            m.clear()
            ist = self.tt_art() == "textfeld"
            felder = self._tt_felder() if ist and not (FO.ist_verknuepft(self.ed, self.ed._frei_sel) and
                                                        dict(FO._textfelder(self.ed))[self.ed._frei_sel]["daten"].get("weiter")) else []
            for key, name in felder:
                m.eintrag("Verknüpfen mit " + name, lambda k=key: self.ttVerknuepfen(None, k))
            if not felder:
                m.eintrag("Kein Textfeld zum Verknüpfen", None, aktiv=False)
            m.trenner()
            m.eintrag("Verknüpfung aufheben", self.ttVerknuepfungLoesen, aktiv=ist and FO.ist_verknuepft(self.ed, self.ed._frei_sel))
        m.aboutToShow.connect(fuellen)
        fuellen()
        return m


    def ttVerknuepfen(self, k=None, ziel=None):
        """Das markierte Textfeld mit ``ziel`` verknüpfen: was nicht mehr hineinpasst, läuft dort weiter."""
        from lunivo_writer.editor import frei_objekt as FO
        if self.tt_art() != "textfeld" or ziel is None or not FO.verknuepfen(self.ed, self.ed._frei_sel, ziel):
            self.w.lbl_msg.setText("Verknüpfen geht nur von einem markierten Textfeld zu einem freien Textfeld ohne Vorgänger.")
            return
        self.w._sync_format()


    def ttVerknuepfungLoesen(self, k=None):
        from lunivo_writer.editor import frei_objekt as FO
        if self.tt_art() != "textfeld" or not FO.loesen(self.ed, self.ed._frei_sel):
            self.w.lbl_msg.setText("Bitte zuerst ein verknüpftes Textfeld markieren.")
            return
        self.w._sync_format()


    def menue_ttEinstellungen(self):
        """Einstellungen wie in WPS: die Fenster zum markierten Objekt (Seitenleiste „Formatierung“, Layout, Text)."""
        from lunivo_writer.ui.baukasten.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Formatierung: Füllung und Linie …", lambda: self.ed and self.ed._frei_linien_fenster())
        m.eintrag("Formatierung: Effekte …", self.ttFormEffekte)
        m.eintrag("Layout …", lambda: self.ed and self.ed.bild_layout_dialog())
        m.eintrag("Text bearbeiten …", self.ttTextBearbeiten)
        return m


    def ttTextBearbeiten(self, k=None):
        art = self.tt_art()
        if art == "textfeld":
            self.textfeldBearbeiten()
        elif art == "wordart":
            self.wordartBearbeiten()
        else:
            self.w.lbl_msg.setText("Bitte zuerst ein WordArt oder Textfeld markieren.")


    # ==== Navigation zwischen Textobjekten (WordArt und Textfelder) ======================================================================
    def _tt_gehe(self, richtung: int) -> None:
        """Das vorige/nächste WordArt oder Textfeld des Dokuments markieren (am Ende springt es an den Anfang)."""
        from lunivo_writer.editor import frei_objekt as FO
        e = self.ed
        if not e:
            return
        schluessel = [key for key, a, *_r in e._frei_liste() if a.get("art") in FO.TEXT_ARTEN]
        if not schluessel:
            self.w.lbl_msg.setText("Im Dokument gibt es kein WordArt und kein Textfeld.")
            return
        jetzt = getattr(e, "_frei_sel", None)
        i = schluessel.index(jetzt) + richtung if jetzt in schluessel else (0 if richtung > 0 else -1)
        e._frei_sel = schluessel[i % len(schluessel)]
        e.viewport().update()
        self.w._sync_format()


    def ttVoriges(self, k=None): self._tt_gehe(-1)

    def ttNaechstes(self, k=None): self._tt_gehe(1)
