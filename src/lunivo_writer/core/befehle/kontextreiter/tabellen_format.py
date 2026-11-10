"""Befehle: Kontext-Reiter „Tabellentools“, Gestaltung: Rahmen, Schattierung, Vorlagen, Optionen, Zellausrichtung, Maße, Gitternetz, Textrichtung.

Ein Baustein von ``KontextBefehle`` (``core/befehle/kontextreiter/kontext.py``); nutzt ``_tab`` aus ``TabellenBefehle`` (``tabellen.py``)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QTextFrameFormat, QTextCharFormat, QTextCursor
from lunivo_writer.ui.baukasten.dokument.eingabe_fenster import EingabeFenster
from lunivo_writer.core.farben import Farbe
from lunivo_writer.ui.baukasten.basis import farben as BF
from lunivo_writer.core.befehle.hilfen import _farbfeld


class TabellenFormatBefehle:
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
        from lunivo_writer.editor.objekte.linie import Linie
        from lunivo_writer.ui.baukasten.formatierung.rahmen_schattierung import RahmenSchattierungDialog
        from lunivo_writer.ui.baukasten.geruest.fenster_stapel import ausfuehren
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
        from lunivo_writer.editor.dokument import verweise
        from lunivo_writer.ui.dialogs.verweise.verweise_fenster import BeschriftungDialog
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
        from lunivo_writer.editor.tabelle import tabellenstil as TS
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for n, (kopf, _s, streifen, _r) in TS.VORLAGEN.items():
            m.eintrag(n, lambda n=n: self._tabelle_vorlage(n), symbol=_farbfeld(kopf or streifen or Farbe.WEISS))
        return m

    def _tabelle_vorlage(self, name):
        """Vorlage auf die Tabelle der Schreibmarke anwenden; Kopfzeile/Streifen/Erste Spalte stehen je Tabelle (editor/tabelle/tabelleneigenschaften.py)."""
        from lunivo_writer.editor.tabelle import tabellenstil as TS
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
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
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
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
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
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
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
        e, c, t = self._tab()
        if t:
            TE.an_inhalt_anpassen(t, c)
            e.document().setModified(True)

    def _tabelle_aendern(self, funktion):
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
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
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
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
        from lunivo_writer.editor.tabelle import tabelleneigenschaften as TE
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
