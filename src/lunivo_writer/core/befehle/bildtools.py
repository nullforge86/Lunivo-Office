"""Befehle: Kontext-Reiter „Bildtools“ für frei positionierte Bilder (Datei, Bildschirmfoto, Piktogramm): Zuschneiden, Größe, Farbe.

Die Fachlogik steht in ``editor/bildzuschnitt.py`` (Zuschneiden, nicht zerstörend) und ``editor/bildwerkzeuge.py``; hier nur die Befehle.
Ein Baustein von ``Befehle`` (siehe ``core/commands.py``). Ohne gewähltes freies Bild zeigen alle Befehle einen Hinweis in der Statuszeile."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt

from lunivo_writer.ui.baukasten import weitere_farben

HINWEIS = "Bitte zuerst ein Bild auswählen."


class BildToolsBefehle:
    def _bz(self):
        """Das gewählte freie Bild (``bildlayout``-Ziel) oder None (dann Hinweis in der Statuszeile)."""
        from lunivo_writer.editor import bildwerkzeuge as BW
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
        from lunivo_writer.editor import bildzuschnitt as BZ
        z = self._bz()
        if z is not None and not BZ.form(self.ed, z, str(name or "")):
            self.w.lbl_msg.setText("Diese Form gibt es nicht oder sie lässt sich nicht zum Zuschneiden nutzen.")

    def bildZuschneidenSkala(self, k=None, verhaeltnis="1:1"):
        """Nach Skala zuschneiden: Seitenverhältnis wie ``"16:9"``, ``"4:3"``, ``"1:1"`` (mittiger Ausschnitt)."""
        from lunivo_writer.editor import bildzuschnitt as BZ
        z = self._bz()
        if z is not None and not BZ.skala_text(self.ed, z, verhaeltnis):
            self.w.lbl_msg.setText("Das Seitenverhältnis ist ungültig (Beispiel: 16:9).")

    def bildZuschneidenZuruecksetzen(self, k=None):
        """Form und Größe zurücksetzen: Maske und Zuschnitt entfernen, das ganze Bild im ursprünglichen Seitenverhältnis."""
        from lunivo_writer.editor import bildzuschnitt as BZ
        z = self._bz()
        if z is not None:
            BZ.zuruecksetzen(self.ed, z)
            self.ed.__dict__["_frei_zuschnitt"] = False

    def menue_bildZuschneiden(self):
        """Klappe „Zuschneiden“: Zuschneiden, Nach Form zuschneiden (Katalog, ohne Linien), Nach Skala zuschneiden, Form und Größe zurücksetzen.
        Die Daten für die Galerie liefern ``bildzuschnitt.formen_kategorien()`` und ``bildzuschnitt.VERHAELTNISSE``."""
        from PySide6.QtCore import QRectF, QSize
        from PySide6.QtGui import QColor, QPen
        from lunivo_writer.core.farben import Farbe
        from lunivo_writer.editor import bildzuschnitt as BZ
        from lunivo_writer.editor import formen_katalog as K
        from lunivo_writer.ui.baukasten.raster_auswahl import RasterAuswahl
        m = RasterAuswahl(self.w, titel="Nach Form zuschneiden", spalten=10, groesse=QSize(24, 24))
        formen_namen: dict[str, str] = {}
        for kat, namen in BZ.formen_kategorien():
            m.abschnitt(kat)
            for name in namen:
                def zeichne(p, r, name=name):
                    p.setPen(QPen(QColor(Farbe.AKZENT), 1.3)); p.setBrush(Qt.NoBrush)
                    p.drawPath(K.pfad(name, QRectF(r).adjusted(3, 3, -3, -3)))
                m.kachel(name, name, zeichne).setCheckable(False)
                formen_namen[name] = name
        m.gewaehlt.connect(lambda n: self.bildZuschneidenForm(None, n))
        m.fuss("Zuschneiden", self.bildZuschneidenModus)
        for text, b, h in BZ.VERHAELTNISSE[:6]:
            m.fuss(f"Nach Skala zuschneiden: {text}", lambda t=text: self.bildZuschneidenSkala(None, t))
        m.fuss("Form und Größe zurücksetzen", self.bildZuschneidenZuruecksetzen)
        return m

    # ==== Größe, Seitenverhältnis ====================================================================================================
    def bildGroesseZuruecksetzen(self, k=None):
        """Größe zurücksetzen: Originalgröße des sichtbaren Ausschnitts in Bildpunkten."""
        from lunivo_writer.editor import bildlayout as BL
        z = self._bz()
        if z is not None:
            BL.frei_original_groesse(self.ed, z)

    def bildSeitenverhaeltnis(self, k=None):
        """Seitenverhältnis sperren ein/aus (auch Ziehen an den Kanten hält es dann)."""
        from lunivo_writer.editor import bildwerkzeuge as BW
        z = self._bz()
        if z is not None:
            BW.sperre_umschalten(self.ed, z)
            self.w.band.aktualisieren()

    def an_bildSeitenverhaeltnis(self):
        from lunivo_writer.editor import bildwerkzeuge as BW
        return bool(self.ed and BW.sperre(BW.frei_bild(self.ed)))

    # ==== Farbe, Inhalt =============================================================================================================
    def bildTransparent(self, k=None, toleranz=12):
        """Transparente Farbe: eine Farbe des Bildes wählen (Farbfenster), alle gleichen Bildpunkte werden durchsichtig."""
        from lunivo_writer.editor import bildwerkzeuge as BW
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
        from lunivo_writer.ui.baukasten.bild_zoom import BildZoomFenster
        BildZoomFenster(self.w, z[3]).exec()
        return True

    def bildHelligkeit(self, k=None, schritt=10):
        """Heller (+10) oder dunkler (-10): Helligkeit des Bildes um ``schritt`` Prozent ändern (-100 bis 100). Nicht zerstörend: der Wert steht als
        ``hell`` in der Angabe des Bildes (``editor/bildwerkzeuge.py``); „Bild zurücksetzen“ und „Farbe ▸ Original“ nehmen ihn zurück."""
        from lunivo_writer.editor import bildwerkzeuge as BW
        z = self._bz()
        return z is not None and BW.korrektur_schritt(self.ed, z, hell=int(schritt))

    def bildKontrast(self, k=None, schritt=10):
        """Kontrast erhöhen (+10) oder verringern (-10) um ``schritt`` Prozent (Angabe ``kontrast``, nicht zerstörend)."""
        from lunivo_writer.editor import bildwerkzeuge as BW
        z = self._bz()
        return z is not None and BW.korrektur_schritt(self.ed, z, kontrast=int(schritt))

    def bildAendern(self, k=None, pfad=None):
        """Bild ändern: eine andere Bilddatei an die Stelle des Bildes setzen (Größe, Lage und Rahmen bleiben)."""
        from lunivo_writer.editor import bildwerkzeuge as BW
        z = self._bz()
        if z is None:
            return
        if not pfad:
            from lunivo_writer.ui.baukasten.speichern_fenster import Dateifenster
            pfad, _ = Dateifenster.getOpenFileName(self.w, "Bild ändern", self.w.settings.get("last_dir", os.path.expanduser("~")),
                                                   "Bilder (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;Alle Dateien (*)")
        if pfad and not BW.aus_datei(self.ed, z, pfad):
            self.w.lbl_msg.setText("Die Datei ist kein lesbares Bild.")

    def bildKomprimieren(self, k=None):
        """Bilder komprimieren: weggeschnittene Bereiche löschen und auf 144 dpi (Anzeigegröße) verkleinern."""
        from lunivo_writer.editor import bildwerkzeuge as BW
        z = self._bz()
        if z is None:
            return
        r = BW.komprimieren(self.ed, z)
        self.w.lbl_msg.setText("Das Bild ist schon klein genug." if r is None else f"Bild komprimiert: {r[0] // 1000} auf {r[1] // 1000} tausend Bildpunkte.")

    def bildZuruecksetzen(self, k=None):
        """Bild zurücksetzen: Zuschnitt, Farbe, Rahmen, Füllung, Effekte und Drehung zurück (Lage und Alternativtext bleiben)."""
        from lunivo_writer.editor import bildwerkzeuge as BW
        z = self._bz()
        if z is not None:
            BW.zuruecksetzen(self.ed, z)
