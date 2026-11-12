"""Befehle: Kontext-Reiter „Bildtools“ für frei positionierte Bilder (Datei, Bildschirmfoto, Piktogramm): Zuschneiden, Größe, Farbe.

Die Fachlogik steht in ``editor/objekte/bildzuschnitt.py`` (Zuschneiden, nicht zerstörend) und ``editor/objekte/bildwerkzeuge.py``; hier nur die Befehle.
Auch die Bildbefehle des Kontext-Reiters (Bild im Text und frei: Farbe, Zuschneiden, Drehen, Größe, Anordnen) stehen hier.
Ein Baustein von ``Befehle`` (siehe ``kern/befehlsliste.py``). Ohne gewähltes freies Bild zeigen alle Befehle einen Hinweis in der Statuszeile."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt, QUrl
from lunivo_writer.oberflaeche.baukasten.dokument.eingabe_fenster import EingabeFenster
from lunivo_writer.oberflaeche.baukasten import weitere_farben

HINWEIS = "Bitte zuerst ein Bild auswählen."


class BildToolsBefehle:
    def _bz(self):
        """Das gewählte freie Bild (``bildlayout``-Ziel) oder None (dann Hinweis in der Statuszeile)."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = BW.frei_bild(self.ed) if self.ed else None
        if z is None:
            self.w.lbl_msg.setText(HINWEIS)
        return z

    # ==== Zuschneiden ================================================================================================================
    def bildZuschneidenModus(self, k=None):
        """Zuschneiden ein/aus: schwarze Eckwinkel und Kantenstriche; Ziehen schneidet ab (der Zuschnitt wird als Anteil gespeichert)."""
        if self._bz() is None:
            return
        e = self.ed
        e.__dict__["_frei_zuschnitt"] = not e.__dict__.get("_frei_zuschnitt", False)
        e.viewport().update()
        self.w.band.aktualisieren()

    def an_bildZuschneidenModus(self): return bool(self.ed and self.ed.__dict__.get("_frei_zuschnitt"))

    def bildZuschneidenForm(self, k=None, name=None):
        """Nach Form zuschneiden: ``name`` ist eine Form des Formenkatalogs (zum Beispiel „Ellipse“, „Herz“)."""
        from lunivo_writer.editor.objekte import bildzuschnitt as BZ
        z = self._bz()
        if z is not None and not BZ.form(self.ed, z, str(name or "")):
            self.w.lbl_msg.setText("Diese Form gibt es nicht oder sie lässt sich nicht zum Zuschneiden nutzen.")

    def bildZuschneidenSkala(self, k=None, verhaeltnis="1:1"):
        """Nach Skala zuschneiden: Seitenverhältnis wie ``"16:9"``, ``"4:3"``, ``"1:1"`` (mittiger Ausschnitt)."""
        from lunivo_writer.editor.objekte import bildzuschnitt as BZ
        z = self._bz()
        if z is not None and str(verhaeltnis).strip().lower() == "frei":
            self.bildZuschneidenModus()                               # „Frei“: Zuschneiden ohne festes Seitenverhältnis
        elif z is not None and not BZ.skala_text(self.ed, z, verhaeltnis):
            self.w.lbl_msg.setText("Das Seitenverhältnis ist ungültig (Beispiel: 16:9).")

    def bildDrehen(self, k=None, richtung="rechts"):
        """Das Bild um 90° drehen: ``richtung`` ist ``"rechts"`` oder ``"links"`` (nutzt ``zeichenDrehen``)."""
        self.zeichenDrehen(None, -90 if str(richtung) == "links" else 90)

    def bildZuschneidenZuruecksetzen(self, k=None):
        """Form und Größe zurücksetzen: Maske und Zuschnitt entfernen, das ganze Bild im ursprünglichen Seitenverhältnis."""
        from lunivo_writer.editor.objekte import bildzuschnitt as BZ
        z = self._bz()
        if z is not None:
            BZ.zuruecksetzen(self.ed, z)
            self.ed.__dict__["_frei_zuschnitt"] = False

    # ==== Größe, Seitenverhältnis ====================================================================================================
    def bildGroesseZuruecksetzen(self, k=None):
        """Größe zurücksetzen: Originalgröße des sichtbaren Ausschnitts in Bildpunkten."""
        from lunivo_writer.editor.objekte import bildlayout as BL
        z = self._bz()
        if z is not None:
            BL.frei_original_groesse(self.ed, z)

    def bildSeitenverhaeltnis(self, k=None):
        """Seitenverhältnis sperren ein/aus (auch Ziehen an den Kanten hält es dann)."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = self._bz()
        if z is not None:
            BW.sperre_umschalten(self.ed, z)
            self.w.band.aktualisieren()

    def an_bildSeitenverhaeltnis(self):
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        return bool(self.ed and BW.sperre(BW.frei_bild(self.ed)))

    # ==== Farbe, Inhalt =============================================================================================================
    def bildTransparent(self, k=None, toleranz=12):
        """Transparente Farbe: eine Farbe des Bildes wählen (Farbfenster), alle gleichen Bildpunkte werden durchsichtig."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = self._bz()
        if z is None:
            return
        c = weitere_farben(self.w, None, "Transparente Farbe")
        if c is not None:
            BW.transparent(self.ed, z, c, int(toleranz))

    def bildVergroessern(self, k=None):
        """Lupe der Schnellleiste: das Bild in seiner Auflösung in der Seitenleiste zeigen, Zoom per Regler oder Mausrad (nur ansehen)."""
        z = self._bz()
        if z is None or z[3] is None:
            return False
        from lunivo_writer.oberflaeche.baukasten.medien.bild_zoom import BildZoomFenster
        BildZoomFenster(self.w, z[3]).exec()
        return True

    def bildHelligkeit(self, k=None, schritt=10):
        """Heller (+10) oder dunkler (-10): Helligkeit des Bildes um ``schritt`` Prozent ändern (-100 bis 100). Nicht zerstörend: der Wert steht als
        ``hell`` in der Angabe des Bildes (``editor/objekte/bildwerkzeuge.py``); „Bild zurücksetzen“ und „Farbe ▸ Original“ nehmen ihn zurück."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = self._bz()
        return z is not None and BW.korrektur_schritt(self.ed, z, hell=int(schritt))

    def bildKontrast(self, k=None, schritt=10):
        """Kontrast erhöhen (+10) oder verringern (-10) um ``schritt`` Prozent (Angabe ``kontrast``, nicht zerstörend)."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = self._bz()
        return z is not None and BW.korrektur_schritt(self.ed, z, kontrast=int(schritt))

    def bildAendern(self, k=None, pfad=None):
        """Bild ändern: eine andere Bilddatei an die Stelle des Bildes setzen (Größe, Lage und Rahmen bleiben)."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = self._bz()
        if z is None:
            return
        if not pfad:
            from lunivo_writer.oberflaeche.baukasten.dokument.speichern_fenster import Dateifenster
            from lunivo_writer.oberflaeche.baukasten.medien.bildformate import BILD_FILTER
            pfad, _ = Dateifenster.getOpenFileName(self.w, "Bild ändern", self.w.settings.get("last_dir", os.path.expanduser("~")),
                                                   BILD_FILTER)
        if not pfad:
            return
        from lunivo_writer.editor.objekte.bilddaten import BildFehler
        try:
            if not BW.aus_datei(self.ed, z, pfad):
                self.w.lbl_msg.setText("Die Datei ist kein lesbares Bild.")
        except BildFehler as fehler:
            self.w.lbl_msg.setText(str(fehler))

    def bildKomprimieren(self, k=None):
        """Bilder komprimieren: weggeschnittene Bereiche löschen und auf 144 dpi (Anzeigegröße) verkleinern."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = self._bz()
        if z is None:
            return
        r = BW.komprimieren(self.ed, z)
        self.w.lbl_msg.setText("Das Bild ist schon klein genug." if r is None else f"Bild komprimiert: {r[0] // 1000} auf {r[1] // 1000} tausend Bildpunkte.")

    def bildZuruecksetzen(self, k=None):
        """Bild zurücksetzen: Zuschnitt, Farbe, Rahmen, Füllung, Effekte und Drehung zurück (Lage und Alternativtext bleiben)."""
        from lunivo_writer.editor.objekte import bildwerkzeuge as BW
        z = self._bz()
        if z is not None:
            BW.zuruecksetzen(self.ed, z)

    # ---- Bild im Text und frei: Farbe, Zuschneiden, Drehen, Größe, Anordnen (aus dem Kontext-Reiter) ---------------------------------------------------
    # ---- Bild, Tabelle, Schrift, Seite: der Rest der Werkzeug-Reiter ----------------------------------------------
    def _bild_frei(self):
        """(Editor, Ziel) des gewählten frei positionierten Bildes (Datei, Bildschirmfoto, Piktogramm …) oder (Editor, None)."""
        from lunivo_writer.editor.objekte import bildlayout as BL
        e = self.ed
        z = BL.ziel(e) if e else None
        return e, (z if z is not None and z[0] == "frei" else None)

    def bildFarbe(self, k=None):
        e, z = self._bild_frei()
        if z is None:
            e, f = self._bild()
            if f is None:
                return
        from lunivo_writer.editor.objekte import bildlayout as BL
        from lunivo_writer.editor.dokument import einfuegen as E
        modi = ["Original", "Graustufen", "Schwarzweiß", "Sepia", "Heller", "Dunkler"]
        n, ok = EingabeFenster.getItem(self.w, "Bildfarbe", "Darstellung:", modi, 0, False)
        if ok:
            if n == "Original":
                if z is not None:
                    from lunivo_writer.editor.objekte import bildwerkzeuge as BW
                    BW.korrektur_setzen(e, z, 0, 0)                               # Helligkeit/Kontrast zurück (nicht zerstörend)
                    z = BL.ziel(e)
                    BL.frei_original(e, z)
                else:
                    E.bild_original(e)
            elif z is not None and n in ("Heller", "Dunkler"):                    # derselbe Weg wie die Knöpfe „Heller/Dunkler“ der Bildtools
                self.bildHelligkeit(None, 10 if n == "Heller" else -10)
            elif z is not None:
                BL.frei_bild_ersetzen(e, z, lambda img, n=n: E.farbe_anwenden(img, n))
            else:
                E.bild_ersetzen(e, lambda img, n=n: E.farbe_anwenden(img, n))

    def bildZuschneiden(self, k=None):
        e, z = self._bild_frei()
        if z is None:
            e, f = self._bild()
            if f is None:
                return
        from lunivo_writer.editor.objekte import bildlayout as BL
        from lunivo_writer.editor.dokument import einfuegen as E
        from lunivo_writer.oberflaeche.dialoge.dokument_dialoge import BildZuschneidenDialog
        d = BildZuschneidenDialog(self.w)
        if d.exec():
            l, o, r, u = d.werte()
            if z is not None:                                            # freies Bild: nicht zerstörend als Anteil (editor/objekte/bildzuschnitt.py)
                from lunivo_writer.editor.objekte import bildzuschnitt as BZ
                q = BZ._quelle(e, z[2])
                if q is not None:
                    BZ.setzen(e, z, (l / q.width(), o / q.height(), r / q.width(), u / q.height()))
            else:
                E.bild_ersetzen(e, lambda img: E.zuschneiden(img, l, o, r, u))

    def objektDrehen(self, k=None):
        e, f = self._bild()
        if f is None:
            return
        from lunivo_writer.editor.dokument import einfuegen as E
        namen = {"90° nach rechts": "rechts", "90° nach links": "links", "Horizontal spiegeln": "horizontal", "Vertikal spiegeln": "vertikal"}
        n, ok = EingabeFenster.getItem(self.w, "Drehen", "Bild:", list(namen), 0, False)
        if ok:
            E.bild_ersetzen(e, lambda img: E.drehen(img, namen[n]))

    def objektAusrichten(self, k=None):
        e, f = self._bild()
        if f is None:
            return
        namen = {"Links": Qt.AlignLeft, "Zentriert": Qt.AlignHCenter, "Rechts": Qt.AlignRight}
        n, ok = EingabeFenster.getItem(self.w, "Ausrichten", "Bild im Text:", list(namen), 0, False)
        if ok:
            e.set_alignment(namen[n])

    # ==== Bildtools (Kontext) =========================================================================================================
    def _bild(self):
        e = self.ed
        if not e:
            return None, None
        f = e.bild_format()
        return (e, f) if f is not None else (e, None)

    def bildGroesse(self, k=None):
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor.objekte import bildlayout as BL
            from lunivo_writer.oberflaeche.dialoge.dokument_dialoge import BildGroesseDialog
            d = BildGroesseDialog(z[2]["b"], z[2]["h"], self.w)
            if d.exec():
                BL.frei_aendern(e, z, b=float(d.breite_px()), h=float(d.hoehe_px()))
            return
        e, f = self._bild()
        if f is None:
            return
        from lunivo_writer.oberflaeche.dialoge.dokument_dialoge import BildGroesseDialog
        d = BildGroesseDialog(f.width(), f.height(), self.w)
        if d.exec():
            e.bild_setzen(width=d.breite_px(), height=d.hoehe_px())

    def bildBreite(self, k=None):
        e, z = self._bild_frei()
        if z is not None:                                                # auf Inhaltsbreite, Seitenverhältnis bleibt
            from lunivo_writer.editor.objekte import bildlayout as BL
            b = e.page.content_width_px
            BL.frei_aendern(e, z, b=b, h=b * z[2]["h"] / max(1.0, z[2]["b"]))
            return
        e, f = self._bild()
        if f is not None and f.width():
            r = f.height() / f.width()
            b = e.page.content_width_px
            e.bild_setzen(width=b, height=b * r)

    def anordnen(self, k=None):
        """Textumbruch / Position: Bild mit Text in der Zeile oder links/rechts vom Text umflossen."""
        e, f = self._bild()
        if f is None:
            self.w.statusBar().showMessage("Erst ein Bild anklicken.", 4000)
            return
        from lunivo_writer.editor.seite import umbruch as U
        aktuell = U.schwebend(e.document(), e._bild_cursor().selectionStart()) or "zeile"
        from lunivo_writer.oberflaeche.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for modus, text in (("zeile", "Mit Text in Zeile"), ("links", "Links, Text umfließt"), ("rechts", "Rechts, Text umfließt"),
                             ("oben_unten", "Oben und unten (eigene Zeile)")):
            m.eintrag(text, lambda modus=modus: U.umbruch_setzen(e, modus), haken=modus == aktuell)
        self._popup(m)

    def bildOriginal(self, k=None):
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor.objekte import bildlayout as BL
            BL.frei_original_groesse(e, z)
            return
        e, f = self._bild()
        if f is not None:
            img = e.document().resource(2, QUrl(f.name()))
            if img is not None and not img.isNull():
                e.bild_setzen(width=img.width(), height=img.height())

    def bildAltText(self, k=None):
        """Alternativtext und „Als dekorativ markieren“ in der Seitenleiste (``BildAlternativtextPanel``); Änderungen gelten sofort."""
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor.objekte import bildlayout as BL
            werte = {"alt": z[2].get("alt", ""), "dekor": bool(z[2].get("dekor"))}

            def anwenden(w: dict) -> None:
                aktuell = BL.ziel(e)                                 # die Angabe kann sich seit dem Öffnen geändert haben
                if aktuell is not None and aktuell[0] == "frei":
                    BL.frei_aendern(e, aktuell, alt=w["alt"], dekor=bool(w["dekor"]))
        else:
            e, f = self._bild()
            if f is None:
                return
            from lunivo_writer.editor.dokument.zusatz import P_DEKORATIV
            alt = f.property(0x100000 + 0x101 + 1) if f.hasProperty(0x100000 + 0x101 + 1) else ""
            werte = {"alt": alt or "", "dekor": bool(f.hasProperty(P_DEKORATIV) and f.property(P_DEKORATIV))}

            def anwenden(w: dict) -> None:
                e.bild_setzen(alt=w["alt"], dekor=bool(w["dekor"]))
        self.w._seitenleiste_oeffnen()
        self.w.sidebar.zeige_bildalternativtext(werte, anwenden)

    def bildEntfernen(self, k=None):
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor.objekte import bildlayout as BL
            BL.frei_entfernen(e)
            return
        e, f = self._bild()
        if f is not None:
            e.textCursor().removeSelectedText()
