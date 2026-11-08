"""Befehle: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen."""
from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QTextBlockFormat, QBrush, QColor, QCursor, QTextFrameFormat, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QMenu
from lunivo_writer.ui.baukasten.dokument.eingabe_fenster import EingabeFenster
from lunivo_writer.ui.baukasten import FarbPalette, weitere_farben
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis import farben as BF
from lunivo_writer.core.befehle.hilfen import FreiMenue, _farbfeld


class KontextBefehle:
    """Befehle des Bandes: Kontext-Reiter: Tabelle, Bild, Formen, Zeichnen. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``)."""


    # ---- Bild, Tabelle, Schrift, Seite: der Rest der Werkzeug-Reiter ----------------------------------------------
    def _bild_frei(self):
        """(Editor, Ziel) des gewählten frei positionierten Bildes (Datei, Bildschirmfoto, Piktogramm …) oder (Editor, None)."""
        from lunivo_writer.editor import bildlayout as BL
        e = self.ed
        z = BL.ziel(e) if e else None
        return e, (z if z is not None and z[0] == "frei" else None)


    def bildFarbe(self, k=None):
        e, z = self._bild_frei()
        if z is None:
            e, f = self._bild()
            if f is None:
                return
        from lunivo_writer.editor import bildlayout as BL
        from lunivo_writer.editor import einfuegen as E
        modi = ["Original", "Graustufen", "Schwarzweiß", "Sepia", "Heller", "Dunkler"]
        n, ok = EingabeFenster.getItem(self.w, "Bildfarbe", "Darstellung:", modi, 0, False)
        if ok:
            if n == "Original":
                if z is not None:
                    from lunivo_writer.editor import bildwerkzeuge as BW
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
        from lunivo_writer.editor import bildlayout as BL
        from lunivo_writer.editor import einfuegen as E
        from lunivo_writer.ui.dialogs.dokument_dialoge import BildZuschneidenDialog
        d = BildZuschneidenDialog(self.w)
        if d.exec():
            l, o, r, u = d.werte()
            if z is not None:                                            # freies Bild: nicht zerstörend als Anteil (editor/bildzuschnitt.py)
                from lunivo_writer.editor import bildzuschnitt as BZ
                q = BZ._quelle(e, z[2])
                if q is not None:
                    BZ.setzen(e, z, (l / q.width(), o / q.height(), r / q.width(), u / q.height()))
            else:
                E.bild_ersetzen(e, lambda img: E.zuschneiden(img, l, o, r, u))


    def objektDrehen(self, k=None):
        e, f = self._bild()
        if f is None:
            return
        from lunivo_writer.editor import einfuegen as E
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


    # ==== Tabellentools (Kontext) ===================================================================================================
    def _tab(self):
        e = self.ed
        if not e:
            return None, None, None
        c = e.textCursor()
        t = None if e.isReadOnly() else c.currentTable()               # im Nur-Lesen-Modus gibt es keine Tabelle zum Ändern
        return (e, c, t) if t else (e, c, None)


    def tabelleZeileOben(self, k=None):
        e, c, t = self._tab()
        if t: t.insertRows(t.cellAt(c).row(), 1)


    def tabelleZeileUnten(self, k=None):
        e, c, t = self._tab()
        if t: t.insertRows(t.cellAt(c).row() + 1, 1)


    def tabelleSpalteLinks(self, k=None):
        e, c, t = self._tab()
        if t: t.insertColumns(t.cellAt(c).column(), 1)


    def tabelleSpalteRechts(self, k=None):
        e, c, t = self._tab()
        if t: t.insertColumns(t.cellAt(c).column() + 1, 1)


    def tabelleZeileLoeschen(self, k=None):
        e, c, t = self._tab()
        if t and t.rows() > 1: t.removeRows(t.cellAt(c).row(), 1)
        elif t: self.tabelleLoeschen()


    def tabelleSpalteLoeschen(self, k=None):
        e, c, t = self._tab()
        if t and t.columns() > 1: t.removeColumns(t.cellAt(c).column(), 1)
        elif t: self.tabelleLoeschen()


    def tabelleLoeschen(self, k=None):
        e, c, t = self._tab()
        if t:
            first = t.firstCursorPosition().position() - 1
            last = t.lastCursorPosition().position() + 1
            cc = QTextCursor(e.document())
            cc.setPosition(max(0, first)); cc.setPosition(min(last, e.document().characterCount() - 1), QTextCursor.KeepAnchor)
            cc.removeSelectedText()


    _ZELLEN_LOESCHEN = {"Zellen nach links verschieben": "links", "Zellen nach oben verschieben": "oben",
                        "Ganze Zeile löschen": "zeile", "Ganze Spalte löschen": "spalte"}

    def tabelleZellenLoeschen(self, k=None):
        """Löschen ▸ Zellen löschen …: Auswahl, wie die Lücke geschlossen wird (Logik: ``editor/tabelleneigenschaften.zellen_loeschen``)."""
        e, c, t = self._tab()
        if not t:
            return
        n, ok = EingabeFenster.getItem(self.w, "Zellen löschen", "Löschen:", list(self._ZELLEN_LOESCHEN), 0, False)
        if not ok:
            return
        art = self._ZELLEN_LOESCHEN[n]
        if art == "zeile":
            return self.tabelleZeileLoeschen()
        if art == "spalte":
            return self.tabelleSpalteLoeschen()
        from lunivo_writer.editor.tabelleneigenschaften import zellen_loeschen
        meldung = zellen_loeschen(t, e.textCursor(), art)
        if meldung:
            self.w.lbl_msg.setText(meldung)
        else:
            e.document().setModified(True)


    def tabelleVerbinden(self, k=None):
        e, c, t = self._tab()
        if t and c.hasSelection(): t.mergeCells(c)


    def tabelleTeilen(self, k=None):
        e, c, t = self._tab()
        if not t: return
        from lunivo_writer.editor.tabelleneigenschaften import zelle_teilen
        text, ok = EingabeFenster.getText(self.w, "Zellen teilen", "Spalten,Zeilen:", text="2,1")
        if not ok: return
        try:
            sp, ze = (int(x) for x in text.replace(";", ",").split(","))
            if not (1 <= sp <= 20 and 1 <= ze <= 20): raise ValueError
        except ValueError:
            self.w.lbl_msg.setText("Ungültige Eingabe: bitte „Spalten,Zeilen“ angeben, zum Beispiel 2,1.")
            return
        if zelle_teilen(t, e.textCursor(), sp, ze): e.document().setModified(True)


    def tabelleRahmen(self, k=None):
        e, c, t = self._tab()
        if t:
            f = t.format(); f.setBorder(0 if f.border() > 0 else 1); f.setBorderBrush(QColor(BF.VORGABE_TABELLENRAND)); f.setBorderStyle(QTextFrameFormat.BorderStyle_Solid); t.setFormat(f)


    def an_tabelleRahmen(self):
        e, c, t = self._tab()
        return bool(t) and t.format().border() > 0


    _RAHMENSTIL = {"gepunktet": QTextFrameFormat.BorderStyle_Dotted, "fein_gestrichelt": QTextFrameFormat.BorderStyle_Dashed,
                   "gestrichelt": QTextFrameFormat.BorderStyle_Dashed, "strichpunkt": QTextFrameFormat.BorderStyle_Dashed,
                   "strichpunktpunkt": QTextFrameFormat.BorderStyle_Dashed, "doppelt": QTextFrameFormat.BorderStyle_Double}

    def tabelleRahmenSchattierung(self, k=None):
        """Rechtsklick ▸ Rahmen und Schattierung: der Baustein-Dialog (ohne Reiter Seitenrand), vorbelegt aus Tabelle und Zelle."""
        e, c, t = self._tab()
        if not t:
            return
        from lunivo_writer.editor.linie import Linie
        from lunivo_writer.ui.baukasten.formatierung.rahmen_schattierung import RahmenSchattierungDialog
        from lunivo_writer.ui.baukasten.controls.fenster_stapel import ausfuehren
        f = t.format()
        linie = Linie(f.borderBrush().color().name(), round(f.border() * 0.75, 2), "einfach", "tblr") if f.border() > 0 else None
        bg = t.cellAt(c).format().background()
        fuell = bg.color().name() if bg.style() != Qt.NoBrush else None
        d = RahmenSchattierungDialog(self.w, rahmen=linie, fuell=fuell, mit_seitenrand=False, innen_h=False, fuer=["Tabelle"])
        if ausfuehren(d):
            self._tabelle_rahmen_schattierung_anwenden(t, c, d.rahmen(), d.schattierung()[0])


    def _tabelle_rahmen_schattierung_anwenden(self, t, c, linie, fuell) -> None:
        """Rahmen der Tabelle (Linie oder None = ohne) und Füllfarbe der markierten Zellen bzw. der Zelle der Schreibmarke.
        Nicht abgebildet: einzelne Kanten (Qt kennt nur einen Tabellenrahmen), Linienart über Voll/Punkt/Strich/Doppelt hinaus, Füllmuster."""
        c.beginEditBlock()
        f = t.format()
        if linie is None:
            f.setBorder(0)
        else:
            f.setBorder(max(1, round(linie.breite_pt / 0.75)))
            f.setBorderBrush(QColor(linie.farbe))
            f.setBorderStyle(self._RAHMENSTIL.get(linie.art, QTextFrameFormat.BorderStyle_Solid))
        t.setFormat(f)
        if c.hasSelection():
            r0, rn, s0, sn = c.selectedTableCells()
            zellen = [t.cellAt(r, s) for r in range(r0, r0 + rn) for s in range(s0, s0 + sn)]
        else:
            zellen = [t.cellAt(c)]
        for cell in zellen:
            cf = cell.format()
            cf.setBackground(QBrush(QColor(fuell))) if fuell else cf.clearBackground()
            cell.setFormat(cf)
        c.endEditBlock()


    def tabelleBeschriftung(self, k=None, oben: bool = False):
        """„Beschriftung …“ für die Tabelle der Schreibmarke: dasselbe Fenster wie Verweise ▸ Beschriftung (``BeschriftungDialog``),
        Bezeichnung „Tabelle“ vorbelegt, Lage über/unter der Tabelle wählbar (``oben`` stellt „Über“ voreingestellt ein)."""
        import json
        e, c, t = self._tab()
        if not t:
            return
        from lunivo_writer.editor import verweise
        from lunivo_writer.ui.dialogs.verweise_fenster import BeschriftungDialog
        try:
            eigene = [str(x) for x in json.loads(self.w.settings.get("verweise/beschriftungen", "[]") or "[]")]
        except (ValueError, TypeError):
            eigene = []
        d = BeschriftungDialog(self.w, eigene, lambda label, zahl: verweise.naechste_nummer(e, label, zahl), objekt=True, label="Tabelle")
        d.pos.setCurrentIndex(1 if oben else 0)
        ok = d.exec()
        if d.eigene != eigene:
            self.w.settings.set("verweise/beschriftungen", json.dumps(d.eigene, ensure_ascii=False))
        if ok:
            r = d.ergebnis()
            verweise.beschriftung_einfuegen(e, r["label"], "", r["oben"], nach=r["nach"], ohne_bezeichnung=r["ohne"], zahl=r["zahl"])


    def menue_tabelleSchattierung(self):
        def setze(col):
            e, c, t = self._tab()
            if t:
                cell = t.cellAt(c)
                f = cell.format()
                f.setBackground(QBrush(col)) if col else f.clearBackground()
                cell.setFormat(f)
        return self._farbmenue(setze, "Keine Schattierung")


    # Tabellenformatvorlagen und Formatoptionen
    def menue_tabelleVorlagen(self):
        from lunivo_writer.editor import tabellenstil as TS
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for n, (kopf, _s, streifen, _r) in TS.VORLAGEN.items():
            m.eintrag(n, lambda n=n: self._tabelle_vorlage(n), symbol=_farbfeld(kopf or streifen or Farbe.WEISS))
        return m


    def _tabelle_vorlage(self, name):
        """Vorlage auf die Tabelle der Schreibmarke anwenden; Kopfzeile/Streifen/Erste Spalte stehen je Tabelle (editor/tabelleneigenschaften.py)."""
        from lunivo_writer.editor import tabellenstil as TS
        from lunivo_writer.editor import tabelleneigenschaften as TE
        e, c, t = self._tab()
        if t:
            o = TE.optionen_lesen(t)
            if not o["gesetzt"]:                                  # noch nie gestaltet: wie bisher Kopfzeile und Streifen an
                o.update(kopf=True, streifen=True, spalte=False)
            e.textCursor().beginEditBlock()
            TE.optionen_setzen(t, kopf=o["kopf"], streifen=o["streifen"], spalte=o["spalte"], vorlage=name)
            TS.anwenden(t, name, o["kopf"], o["streifen"], o["spalte"])
            e.textCursor().endEditBlock()
            e.document().setModified(True)


    def _tabellen_option(self, key):
        """Option (kopf/streifen/spalte) der Tabelle der Schreibmarke umschalten; ist eine Vorlage gesetzt, wird sie neu angewendet."""
        from lunivo_writer.editor import tabelleneigenschaften as TE
        e, c, t = self._tab()
        if not t:
            return
        o = TE.optionen_lesen(t)
        e.textCursor().beginEditBlock()
        TE.optionen_setzen(t, **{key: not o[key]})
        if o["vorlage"]:
            self._tabelle_vorlage(o["vorlage"])
        e.textCursor().endEditBlock()
        e.document().setModified(True)


    def tabelleKopfzeile(self, k=None): self._tabellen_option("kopf")

    def tabelleStreifen(self, k=None): self._tabellen_option("streifen")

    def tabelleErsteSpalte(self, k=None): self._tabellen_option("spalte")

    def _an_tabellen_option(self, key):
        from lunivo_writer.editor import tabelleneigenschaften as TE
        e, c, t = self._tab()
        return bool(t) and TE.optionen_lesen(t)[key]

    def an_tabelleKopfzeile(self): return self._an_tabellen_option("kopf")

    def an_tabelleStreifen(self): return self._an_tabellen_option("streifen")

    def an_tabelleErsteSpalte(self): return self._an_tabellen_option("spalte")


    def _zelle_ausrichten(self, wo):
        e, c, t = self._tab()
        if t:
            cell = t.cellAt(c)
            f = cell.format().toTableCellFormat()
            f.setVerticalAlignment(wo)
            cell.setFormat(f)


    def zelleOben(self, k=None): self._zelle_ausrichten(QTextCharFormat.AlignTop)

    def zelleMitte(self, k=None): self._zelle_ausrichten(QTextCharFormat.AlignMiddle)

    def zelleUnten(self, k=None): self._zelle_ausrichten(QTextCharFormat.AlignBottom)


    def _zelle_waagrecht(self, wo):
        e, c, t = self._tab()
        if t:
            z = c if c.hasSelection() else t.cellAt(c).firstCursorPosition()
            if not c.hasSelection():
                z.setPosition(t.cellAt(c).lastCursorPosition().position(), QTextCursor.KeepAnchor)
            bf = z.blockFormat(); bf.setAlignment(wo); z.mergeBlockFormat(bf)

    def zelleLinks(self, k=None): self._zelle_waagrecht(Qt.AlignLeft)

    def zelleZentriert(self, k=None): self._zelle_waagrecht(Qt.AlignHCenter)

    def zelleRechts(self, k=None): self._zelle_waagrecht(Qt.AlignRight)


    def tabelleTabelleTeilen(self, k=None):
        """Tabelle oberhalb der Zeile der Schreibmarke teilen: die Zeilen ab hier kommen in eine neue Tabelle darunter."""
        e, c, t = self._tab()
        if not t:
            return
        r = t.cellAt(c).row()
        if r < 1:
            self.w.lbl_msg.setText("Die Schreibmarke muss unterhalb der ersten Zeile stehen, damit die Tabelle geteilt werden kann.")
            return
        zeilen = []
        for zr in range(r, t.rows()):
            zeilen.append([QTextCursor(t.cellAt(zr, sp).firstCursorPosition()) for sp in range(t.columns())])
        frag = []
        for zeile in zeilen:
            reihe = []
            for z in zeile:
                z.movePosition(QTextCursor.EndOfBlock, QTextCursor.KeepAnchor)
                reihe.append(z.selection())
            frag.append(reihe)
        fmt = t.format()
        c.beginEditBlock()
        t.removeRows(r, t.rows() - r)
        ende = QTextCursor(t.lastCursorPosition())
        ende.movePosition(QTextCursor.NextBlock)
        ende.insertBlock()
        neu = ende.insertTable(len(frag), len(frag[0]), fmt)
        for zr, reihe in enumerate(frag):
            for sp, f in enumerate(reihe):
                neu.cellAt(zr, sp).firstCursorPosition().insertFragment(f)
        c.endEditBlock()
        e.document().setModified(True)


    def tabelleEigenschaften(self, k=None):
        e, c, t = self._tab()
        if not t:
            return
        from lunivo_writer.editor import tabelleneigenschaften as TE
        from lunivo_writer.ui.baukasten.controls.fenster_stapel import ausfuehren
        from lunivo_writer.ui.dialogs.dokument_dialoge import TabellenEigenschaftenDialog
        d = TabellenEigenschaftenDialog(self.w, werte=TE.lesen(t, c))
        if ausfuehren(d):
            TE.anwenden(t, c, d.werte())
            fm = t.format()
            fm.setHeaderRowCount(1 if d.kopf.isChecked() else 0)
            t.setFormat(fm)
            e.document().setModified(True)


    def _tabellen_aktionsmenue(self, name: str):
        """Menü „Einfügen“ bzw. „Löschen“ aus der gemeinsamen Definition (``core/tabellenaktionen.py``): Band, Mini-Leiste und Kontextmenü."""
        from lunivo_writer.core.tabellenaktionen import GRUPPEN
        from lunivo_writer.ui.widgets import icons
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for a in GRUPPEN[name]:
            m.eintrag(a.name, lambda bf=a.befehl: self.tun(bf), symbol=icons.icon(a.symbol, 16) if icons.hat(a.symbol) else None)
        return m


    def menue_tabelleEinfuegenAktionen(self):
        return self._tabellen_aktionsmenue("Einfügen")


    def menue_tabelleLoeschenAktionen(self):
        return self._tabellen_aktionsmenue("Löschen")


    def menue_tabelleAutoAnpassen(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("An Inhalt anpassen", self._tabelle_inhalt)
        m.eintrag("An Fenster anpassen", self._tabelle_fenster)
        m.eintrag("Spalten gleichmäßig verteilen", self._tabelle_gleich)
        m.eintrag("Zeilen gleichmäßig verteilen", self._tabelle_zeilen_gleich)
        m.eintrag("Feste Spaltenbreite", self._tabelle_fest)
        m.eintrag("Spaltenbreite festlegen …", self.tabelleBreite)
        return m


    def _tabelle_fenster(self):
        from PySide6.QtGui import QTextLength
        e, c, t = self._tab()
        if t:
            f = t.format(); f.setWidth(QTextLength(QTextLength.PercentageLength, 100))
            f.setColumnWidthConstraints([QTextLength(QTextLength.PercentageLength, 100 / t.columns())] * t.columns())
            t.setFormat(f)


    def _tabelle_inhalt(self):
        from lunivo_writer.editor import tabelleneigenschaften as TE
        e, c, t = self._tab()
        if t:
            TE.an_inhalt_anpassen(t, c)
            e.document().setModified(True)


    def absatzFormatZuruecksetzen(self, k=None):
        """Absatzformat (Blockformat) der Absätze an der Schreibmarke/Auswahl auf Standard; Zeichenformat bleibt. Ein Rückgängig-Schritt."""
        e = self.ed
        if not e:
            return
        c = e.textCursor()
        c.beginEditBlock()
        a, b = sorted((c.anchor(), c.position()))
        x = QTextCursor(e.document()); x.setPosition(a)
        blk = x.block()
        while blk.isValid() and blk.position() <= b:
            QTextCursor(blk).setBlockFormat(QTextBlockFormat())
            blk = blk.next()
        c.endEditBlock()
        e.document().setModified(True)


    def _tabelle_aendern(self, funktion):
        from lunivo_writer.editor import tabelleneigenschaften as TE
        e, c, t = self._tab()
        if t:
            c.beginEditBlock()
            getattr(TE, funktion)(t)
            c.endEditBlock()
            e.document().setModified(True)


    def _tabelle_gleich(self):
        self._tabelle_aendern("spalten_gleich")


    def _tabelle_zeilen_gleich(self):
        self._tabelle_aendern("zeilen_gleich")


    def _tabelle_fest(self):
        self._tabelle_aendern("spalten_festschreiben")


    def tabelleBreite(self, k=None):
        """Breite der Spalte der Schreibmarke in cm festlegen (Eingabe; gesetzt über ``tabelleMasse``)."""
        e, c, t = self._tab()
        if not t:
            return
        txt, ok = EingabeFenster.getText(self.w, "Spaltenbreite", "Breite in cm:", "3,0")
        try:
            cm = float(txt.replace(",", "."))
        except ValueError:
            return
        if ok and cm > 0:
            self.tabelleMasse(breite_mm=cm * 10)


    def tabelleMasse(self, breite_mm=None, hoehe_mm=None):
        """Band-Zahlenfelder der Tabellentools: Spaltenbreite der Schreibmarke und/oder Mindesthöhe ihrer Zeile in mm setzen (ein Rückgängig-Schritt)."""
        from lunivo_writer.editor import tabelleneigenschaften as TE
        from lunivo_writer.models.page import mm_to_px
        e, c, t = self._tab()
        if not t:
            return
        if breite_mm is not None and breite_mm > 0:
            w = TE.lesen(t, c)
            w.update(spalte=float(breite_mm), spalte_fest=True)
            TE.anwenden(t, c, w)
        if hoehe_mm is not None and hoehe_mm > 0:
            c.beginEditBlock()
            TE.zeilenhoehe_setzen(t, t.cellAt(c).row(), mm_to_px(float(hoehe_mm)), e.fontMetrics().lineSpacing())
            c.endEditBlock()
        e.document().setModified(True)


    def tabelleMasseLesen(self):
        """(Breite der Spalte, Höhe der Zeile) der Schreibmarke in mm für die Zahlenfelder des Bandes; ``None`` außerhalb einer Tabelle.
        Ohne gesetztes Maß wird die tatsächliche Größe aus dem Layout genommen."""
        from lunivo_writer.editor import tabelleneigenschaften as TE
        from lunivo_writer.models.page import px_to_mm
        e, c, t = self._tab()
        if not t:
            return None
        z = t.cellAt(c)
        w = TE.lesen(t, c)
        lay = e.document().documentLayout()
        if w["spalte_fest"] and w["spalte"] > 0:
            breite = w["spalte"]
        else:
            f = t.format()
            halb = f.cellPadding() + f.cellSpacing() / 2
            x0 = lay.blockBoundingRect(z.firstCursorPosition().block()).left() - halb
            n = z.column() + z.columnSpan()
            x1 = (lay.blockBoundingRect(t.cellAt(z.row(), n).firstCursorPosition().block()).left() - halb if n < t.columns()
                  else lay.frameBoundingRect(t).right() - f.border())
            breite = px_to_mm(max(0.0, x1 - x0))
        px = TE.zeilenhoehe_lesen(t, z.row())
        if px <= 0:
            px = e.fontMetrics().lineSpacing() + 2 * t.format().cellPadding()
        return breite, px_to_mm(px)


    _GITTER_FARBE = "#c8c8c8"

    def an_tabelleGitternetz(self):
        e, c, t = self._tab()
        if not t:
            return False
        f = t.cellAt(0, 0).format().toTableCellFormat()
        return f.topBorder() > 0 and f.topBorderStyle() == QTextFrameFormat.BorderStyle_Dashed and f.topBorderBrush().color().name() == self._GITTER_FARBE


    def tabelleGitternetz(self, k=None):
        """Gitternetzlinien umschalten: hellgraue gestrichelte Zellränder; wirkt nur bei Tabellen ohne Rahmen."""
        e, c, t = self._tab()
        if not t:
            return
        if t.format().border() > 0:
            self.w.lbl_msg.setText("Das Gitternetz wird nur bei Tabellen ohne Rahmen angezeigt.")
            return
        an = not self.an_tabelleGitternetz()
        c.beginEditBlock()
        for r in range(t.rows()):
            for sp in range(t.columns()):
                cell = t.cellAt(r, sp)
                if cell.row() != r or cell.column() != sp:
                    continue
                f = cell.format().toTableCellFormat()
                for seite in ("Top", "Bottom", "Left", "Right"):
                    getattr(f, f"set{seite}Border")(1 if an else 0)
                    getattr(f, f"set{seite}BorderStyle")(QTextFrameFormat.BorderStyle_Dashed)
                    getattr(f, f"set{seite}BorderBrush")(QColor(self._GITTER_FARBE))
                cell.setFormat(f)
        c.endEditBlock()
        e.document().setModified(True)


    def menue_tabelleTextrichtung(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Waagrecht (links nach rechts)", lambda: self._tabelle_richtung(Qt.LeftToRight))
        m.eintrag("Rechts nach links", lambda: self._tabelle_richtung(Qt.RightToLeft))
        return m


    def tabelleTextrichtung(self, k=None):
        """Auswahl der Textrichtung der Zelle (waagrecht / rechts nach links); Qt zeichnet nur diese beiden."""
        e, c, t = self._tab()
        if not t:
            return
        namen = ["Waagrecht (links nach rechts)", "Rechts nach links"]
        n, ok = EingabeFenster.getItem(self.w, "Textrichtung", "Richtung:", namen, 0, False)
        if ok:
            self._tabelle_richtung(Qt.LeftToRight if n == namen[0] else Qt.RightToLeft)


    def _tabelle_richtung(self, richtung):
        """Textrichtung der Zelle der Schreibmarke bzw. aller markierten Zellen setzen (Blockformat setLayoutDirection)."""
        e, c, t = self._tab()
        if not t:
            return
        if c.hasSelection():
            a, b = t.cellAt(c.selectionStart()), t.cellAt(c.selectionEnd())
            r0, r1 = sorted((a.row(), b.row())); c0, c1 = sorted((a.column(), b.column()))
            zellen = [t.cellAt(r, s) for r in range(r0, r1 + 1) for s in range(c0, c1 + 1)]
        else:
            zellen = [t.cellAt(c)]
        c.beginEditBlock()
        for cell in zellen:
            z = cell.firstCursorPosition()
            z.setPosition(cell.lastCursorPosition().position(), QTextCursor.KeepAnchor)
            bf = z.blockFormat(); bf.setLayoutDirection(richtung)
            z.mergeBlockFormat(bf)
        c.endEditBlock()
        e.document().setModified(True)


    # ==== Bildtools (Kontext) =========================================================================================================
    def _bild(self):
        e = self.ed
        if not e:
            return None, None
        f = e.bild_format()
        return (e, f) if f is not None else (e, None)


    # ---- Form- und WordArt-Tools --------------------------------------------------------------------------------------------
    FARBEN = (Farbe.AKZENT_DUNKEL, "#6bbf59", "#f4a259", "#e5645f", "#ffd43b", "#ced4da", "#495057", Farbe.WEISS, Farbe.SCHWARZ)


    def _form_farbe(self, feld: str, titel: str):
        c = weitere_farben(self.w, Farbe.AKZENT_DUNKEL, titel)
        if c is not None:
            self._form_aendern(**{feld: c.name()})


    def _form_aendern(self, **kw):
        from lunivo_writer.editor import formen
        if not (self.ed and formen.aendern(self.ed, **kw)):
            self.w.lbl_msg.setText("Bitte zuerst eine Form auswählen (Schreibmarke vor der Form oder Form markieren).")


    def menue_formFuellung(self):
        m = FarbPalette(self.w, keine_text="Keine Füllung", start=Farbe.AKZENT_DUNKEL, titel="Füllfarbe")
        m.gewaehlt.connect(lambda c: self._form_aendern(fuell=c.name() if c is not None else ""))
        return m


    def menue_formKontur(self):
        m = FarbPalette(self.w, keine_text=None, start=Farbe.AKZENT_DUNKEL, titel="Linienfarbe")
        m.gewaehlt.connect(lambda c: self._form_aendern(linie=c.name()))
        m.addSeparator()
        st = m.untermenue("Linienstärke")
        for w in (0.5, 1.0, 2.0, 3.0, 5.0, 8.0):
            st.eintrag(f"{w:g} pt".replace(".", ","), lambda w=w: self._form_aendern(strich=w))
        return m


    def menue_formVorlagen(self):
        from lunivo_writer.editor import formen
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for n, fu, li, _st in formen.VORLAGEN:
            m.eintrag(n, lambda n=n: self._form_vorlage(n), symbol=_farbfeld(fu or Farbe.WEISS))
        return m


    def _form_vorlage(self, name):
        from lunivo_writer.editor import formen
        if not (self.ed and formen.vorlage(self.ed, name)):
            self.w.lbl_msg.setText("Bitte zuerst eine Form auswählen.")


    def formText(self, k=None):
        from lunivo_writer.editor import formen
        frei = formen.frei_daten(self.ed) if self.ed else None            # als freies Objekt gewählte Form
        if frei is not None:
            akt = frei.get("text", "")
        else:
            e, f = self._bild()
            if f is None:
                return
            o = formen.objekt(f) or {}
            akt = o.get("daten", {}).get("text", "")
        t, ok = EingabeFenster.getText(self.w, "Text in der Form", "Text:", text=akt)
        if ok:
            self._form_aendern(text=t)


    # ---- Zeichentools (Kontext-Reiter für frei positionierte Bilder und Formen) --------------------------------------------------
    def _zeichen(self):
        """(Editor, Ziel) des markierten Bildes oder (Editor, None)."""
        from lunivo_writer.editor import bildlayout as BL
        e = self.ed
        return (e, BL.ziel(e)) if e else (None, None)


    def _zeichen_edit(self):
        return self.ed


    def menue_zeichenFormstile(self):
        return FreiMenue.formstile(self)


    def menue_zeichenFuellung(self):
        return FreiMenue.fuell(self)


    def menue_zeichenGliederung(self):
        return FreiMenue.kontur(self)


    def menue_zeichenAusrichten(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for schl, text in (("links", "Links ausrichten"), ("mitte", "Waagerecht zentrieren"), ("rechts", "Rechts ausrichten"),
                           ("oben", "Oben ausrichten"), ("mittig", "Senkrecht zentrieren"), ("unten", "Unten ausrichten")):
            m.eintrag(text, lambda s=schl: self.zeichenAusrichten(None, s))
        return m


    def menue_zeichenDrehen(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Um 90° nach rechts drehen", lambda: self.zeichenDrehen(None, 90))
        m.eintrag("Um 90° nach links drehen", lambda: self.zeichenDrehen(None, -90))
        m.eintrag("Drehung zurücksetzen", lambda: self.zeichenDrehen(None, 0))
        return m


    def menue_zeichenEbene(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        m.eintrag("Vor den Text", lambda: self.zeichenEbene(None, "vor"))
        m.eintrag("Hinter den Text", lambda: self.zeichenEbene(None, "hinter"))
        return m


    def wortExtras(self, k=None):
        """Wort-Extras: Absätze aufräumen (Markierung, sonst das ganze Dokument)."""
        if self.ed:
            self._popup(self.menue_wortExtrasKlappe())


    def menue_wortExtrasKlappe(self):
        """Das Menü „Wort-Extras“ wie in der Vorlage, mit dem Untermenü „Löschen“; jeder Eintrag ist ein Schritt für Rückgängig."""
        from lunivo_writer.editor import wortextras as W
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        from lunivo_writer.ui.widgets import icons

        def fuellen(m, zeilen):
            for z in zeilen:
                if z == "-":
                    m.trenner()
                elif isinstance(z[2], list):
                    fuellen(m.untermenue(z[0], icons.icon(z[1], 16)), z[2])
                else:
                    m.eintrag(z[0], lambda t=z[0], f=z[2]: self.ed and self._wort_extra(t, f), symbol=icons.icon(z[1], 16))
        m = MenueListe()
        fuellen(m, W.MENUE)
        return m


    def _wort_extra(self, text, f):
        n = f(self.ed)
        self.w.statusBar().showMessage(f"{text}: {n} Stelle(n) geändert." if n else f"{text}: nichts zu ändern.", 5000)


    def zeichenEffekte(self, k=None):
        e, z = self._zeichen()
        if z is not None:
            e._frei_effekte()


    def zeichenFormatUebertragen(self, k=None):
        from lunivo_writer.editor import bildlayout as BL
        e, z = self._zeichen()
        merk = BL.format_merken(z)
        if merk is None:
            self.w.statusBar().showMessage("Format übertragen: erst ein freies Bild oder eine Form markieren.", 4000)
            return
        e._frei_format_merk = merk
        self.w.statusBar().showMessage("Jetzt das Bild anklicken, das dieses Format bekommen soll.", 6000)


    def zeichenAusrichten(self, k=None, wie="links"):
        from lunivo_writer.editor import bildlayout as BL
        e, z = self._zeichen()
        BL.ausrichten(e, z, wie)


    def zeichenDrehen(self, k=None, grad=90):
        from lunivo_writer.editor import bildlayout as BL
        e, z = self._zeichen()
        if z is not None and z[0] == "frei":
            BL.frei_aendern(e, z, dreh=0.0) if grad == 0 else BL.drehen(e, z, float(grad))


    def zeichenEbene(self, k=None, wo="vor"):
        from lunivo_writer.editor import bildlayout as BL
        e, z = self._zeichen()
        BL.ebene(e, z, wo == "vor")


    def zeichenVorn(self, k=None): self.zeichenEbene(None, "vor")

    def zeichenHinten(self, k=None): self.zeichenEbene(None, "hinter")


    def zeichenUmbruch(self, k=None):
        e, z = self._zeichen()
        if z is not None:
            e._frei_layout_popup(QCursor.pos())


    def zeichenLayout(self, k=None):
        e, z = self._zeichen()
        if z is not None:
            e.bild_layout_dialog()


    def zeichenMasse(self, breite_mm=None, hoehe_mm=None):
        from lunivo_writer.editor import bildlayout as BL
        e, z = self._zeichen()
        BL.masse_setzen(e, z, breite_mm, hoehe_mm)


    def gruppieren(self, k=None):
        from lunivo_writer.editor import formen
        if self.ed:
            r = formen.gruppieren(self.ed)
            self.w.lbl_msg.setText(r or "Formen gruppiert.")


    def gruppeAufheben(self, k=None):
        from lunivo_writer.editor import formen
        if self.ed:
            r = formen.gruppe_aufheben(self.ed)
            self.w.lbl_msg.setText(r or "Gruppierung aufgehoben.")


    def bildGroesse(self, k=None):
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor import bildlayout as BL
            from lunivo_writer.ui.dialogs.dokument_dialoge import BildGroesseDialog
            d = BildGroesseDialog(z[2]["b"], z[2]["h"], self.w)
            if d.exec():
                BL.frei_aendern(e, z, b=float(d.breite_px()), h=float(d.hoehe_px()))
            return
        e, f = self._bild()
        if f is None:
            return
        from lunivo_writer.ui.dialogs.dokument_dialoge import BildGroesseDialog
        d = BildGroesseDialog(f.width(), f.height(), self.w)
        if d.exec():
            e.bild_setzen(width=d.breite_px(), height=d.hoehe_px())


    def bildBreite(self, k=None):
        e, z = self._bild_frei()
        if z is not None:                                                # auf Inhaltsbreite, Seitenverhältnis bleibt
            from lunivo_writer.editor import bildlayout as BL
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
        from lunivo_writer.editor import umbruch as U
        aktuell = U.schwebend(e.document(), e._bild_cursor().selectionStart()) or "zeile"
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for modus, text in (("zeile", "Mit Text in Zeile"), ("links", "Links, Text umfließt"), ("rechts", "Rechts, Text umfließt"),
                             ("oben_unten", "Oben und unten (eigene Zeile)")):
            m.eintrag(text, lambda modus=modus: U.umbruch_setzen(e, modus), haken=modus == aktuell)
        self._popup(m)


    def bildOriginal(self, k=None):
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor import bildlayout as BL
            BL.frei_original_groesse(e, z)
            return
        e, f = self._bild()
        if f is not None:
            img = e.document().resource(2, QUrl(f.name()))
            if img is not None and not img.isNull():
                e.bild_setzen(width=img.width(), height=img.height())


    def bildAltText(self, k=None):
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor import bildlayout as BL
            t, ok = EingabeFenster.getText(self.w, "Alternativtext", "Beschreibung des Bildes:", text=z[2].get("alt", ""))
            if ok:
                BL.frei_aendern(e, z, alt=t)
            return
        e, f = self._bild()
        if f is None:
            return
        akt = f.property(0x100000 + 0x101 + 1) if f.hasProperty(0x100000 + 0x101 + 1) else ""
        t, ok = EingabeFenster.getText(self.w, "Alternativtext", "Beschreibung des Bildes:", text=akt or "")
        if ok:
            e.bild_setzen(alt=t)


    def bildEntfernen(self, k=None):
        e, z = self._bild_frei()
        if z is not None:
            from lunivo_writer.editor import bildlayout as BL
            BL.frei_entfernen(e)
            return
        e, f = self._bild()
        if f is not None:
            e.textCursor().removeSelectedText()


    def exportierenRtf(self, k=None): self.w.export_as(".rtf")

