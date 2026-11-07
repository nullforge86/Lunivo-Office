"""TextAbsatzBefehle: fachlich abgegrenzte Bandbefehle."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt  # noqa: F401
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor, QTextListFormat  # noqa: F401
from PySide6.QtWidgets import QMenu, QMessageBox  # noqa: F401
from lunivo_writer.editor.linie import Linie  # noqa: F401
from lunivo_writer.ui.baukasten import FarbPalette, RahmenMenue, RasterAuswahl  # noqa: F401
from lunivo_writer.core.farben import Farbe  # noqa: F401
from lunivo_writer.ui.baukasten import farben as BF  # noqa: F401

ZEILENABSTAENDE = (1.0, 1.5, 2.0, 2.5, 3.0)


class TextAbsatzBefehle:
    """Teilbereich der Textbefehle; wird von TextBefehle zusammengesetzt."""

    def punkte(self, k=None):
        if self.ed: self.ed.toggle_list("bullet")

    def an_punkte(self):
        l = self.ed.textCursor().currentList() if self.ed else None
        return bool(l) and l.format().style() in (QTextListFormat.ListDisc, QTextListFormat.ListCircle, QTextListFormat.ListSquare)

    def zahlen(self, k=None):
        if self.ed: self.ed.toggle_list("number")

    def an_zahlen(self):
        l = self.ed.textCursor().currentList() if self.ed else None
        return bool(l) and l.format().style() == QTextListFormat.ListDecimal

    def _listenraster(self, art: str, titel: str) -> RasterAuswahl:
        """Auswahl der Aufzählungs- bzw. Nummerierungsarten: dieselben Kacheln und Listen wie im Fenster „Nummerierung und Aufzählungszeichen“."""
        from lunivo_writer.ui.baukasten.liste_dialog import aufzaehlungen, kachel_bild, nummerierungen
        arten = aufzaehlungen() if art == "bullet" else nummerierungen()
        aktuell = self.ed.liste_spec() if self.ed else None
        r = RasterAuswahl(self.w, titel=titel, spalten=4, groesse=QSize(96, 68))
        r.kachel("keine", "Keine", kachel_bild(None, QSize(96, 68)), aktuell=aktuell is None)
        for i, spec in enumerate(arten):
            r.kachel(str(i), "", kachel_bild(spec, QSize(96, 68)), aktuell=aktuell == spec)
        r.gewaehlt.connect(lambda k: self._liste_setzen(None if k == "keine" else arten[int(k)]))
        r.fuss("Weitere Aufzählungszeichen …" if art == "bullet" else "Weitere Nummerierungen …",
               lambda: self.listeDialog("aufzaehlung" if art == "bullet" else "nummerierung"))
        return r

    def _liste_setzen(self, spec) -> None:
        if self.ed:
            self.ed.set_liste(spec)

    def listeDialog(self, seite: str = "aufzaehlung"):
        """Fenster „Nummerierung und Aufzählungszeichen“ (Baukasten); das Ergebnis gilt für den Absatz an der Schreibmarke."""
        if not self.ed:
            return
        from lunivo_writer.ui.baukasten.liste_dialog import ListenDialog
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        d = ListenDialog(self.w, self.ed.liste_spec(), seite=seite)
        if ausfuehren(d):
            self.ed.set_liste(d.ergebnis())

    def menue_aufzaehlungKlappe(self):
        return self._listenraster("bullet", "Aufzählungszeichen")

    def menue_nummerierungKlappe(self):
        return self._listenraster("number", "Nummerierung")

    def einzugMehr(self, k=None):
        if self.ed: self.ed.change_indent(10)

    def einzugWeniger(self, k=None):
        if self.ed: self.ed.change_indent(-10)

    def einzugGenau(self, k=None):
        self.w.paragraph_dialog()

    def ebeneHoeher(self, k=None):
        if self.ed: self.ed.list_level(1)

    def ebeneTiefer(self, k=None):
        if self.ed: self.ed.list_level(-1)

    def links(self, k=None):
        if self.ed: self.ed.set_alignment(Qt.AlignLeft)

    def an_links(self): return bool(self.ed) and bool(self.ed.alignment() & Qt.AlignLeft)

    def mitte(self, k=None):
        if self.ed: self.ed.set_alignment(Qt.AlignHCenter)

    def an_mitte(self): return bool(self.ed) and bool(self.ed.alignment() & Qt.AlignHCenter)

    def rechts(self, k=None):
        if self.ed: self.ed.set_alignment(Qt.AlignRight)

    def an_rechts(self): return bool(self.ed) and bool(self.ed.alignment() & Qt.AlignRight)

    def block(self, k=None):
        if self.ed: self.ed.set_alignment(Qt.AlignJustify)

    def an_block(self): return bool(self.ed) and bool(self.ed.alignment() & Qt.AlignJustify)

    def menue_zeilenabstandKlappe(self):
        from lunivo_writer.ui.baukasten.dropdown.menue_liste import MenueListe
        m = MenueListe()
        for f in ZEILENABSTAENDE:                                   # wie in der Vorlage; alles andere im Fenster Absatz (dort auch „Tabstopps …“)
            m.eintrag(f"{f:g}".replace(".", ","), lambda f=f: self.ed and self.ed.set_line_spacing(f))
        m.eintrag("Mehr …", self.w.paragraph_dialog)
        return m

    def steuerzeichenZeigen(self, k=None):
        self.w.a_marks.toggle() if hasattr(self.w, "a_marks") else None

    def an_steuerzeichenZeigen(self): return self.w.marks_on


    # ==== Start: weitere Absatz-/Zeichenbefehle ==================================================================

    def verteilt(self, k=None):
        if self.ed: self.ed.set_alignment(Qt.AlignJustify)

    def formatUebertragen(self, k=None):
        e = self.ed
        if not e:
            return
        if getattr(self, "_pinsel", None) is None:
            self._pinsel = QTextCharFormat(e.textCursor().charFormat())
            self.w.lbl_msg.setText("Format aufgenommen — jetzt Text markieren, um es zu übertragen.")
        else:
            c = e.textCursor()
            if c.hasSelection():
                c.mergeCharFormat(self._pinsel)
            self._pinsel = None
            self.w.lbl_msg.setText("Format übertragen.")

    def an_formatUebertragen(self): return getattr(self, "_pinsel", None) is not None

    def sortieren(self, k=None):
        """Sortiert die markierten Absätze (ohne Markierung das ganze Dokument); „Text sortieren“ fragt Schlüssel, Typ und Richtung,
        „Option …“ Feldtrenner, Groß-/Kleinschreibung und Sortiersprache."""
        e = self.ed
        if not e:
            return
        from lunivo_writer.editor import schreibweise as S
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        from lunivo_writer.ui.baukasten.sortieren_dialog import SortierenDialog
        c = e.textCursor()
        doc = e.document()
        bloecke = S.absaetze(doc, c.selectionStart(), c.selectionEnd()) if c.hasSelection() else S.absaetze(doc)
        if len(bloecke) < 2:
            self.w.statusBar().showMessage("Zum Sortieren braucht es mindestens zwei Absätze außerhalb von Tabellen.", 5000)
            return
        texte = [b.text() for b in bloecke]
        d = SortierenDialog(self.w, texte)
        if not ausfuehren(d):
            return
        S.umstellen(doc, bloecke, S.reihenfolge(texte, **d.werte()))

    def menue_absatzSchattierung(self):
        def setze(c):
            self.ed.set_absatzschatten(c.name() if c else None)
        return self._farbmenue(setze, "Keine Schattierung", pipette=False)


    _rahmen_stil = Linie(Farbe.SCHWARZ, 0.75, "einfach")          # Linie, die ein neuer Rahmen aus dem Menü bekommt

    def menue_absatzRahmen(self):
        m = RahmenMenue(self.w, innen="h", mehr=self.absatzRahmen)
        m.gewaehlt.connect(lambda _s, k: self._rahmen_seite(k))
        return m

    def _rahmen_seite(self, schluessel: str) -> None:
        """Eintrag des Rahmen-Menüs: einzelne Seiten ein-/ausschalten, alle, außen oder keine."""
        if not self.ed:
            return
        aktuell = self.ed.absatzrahmen()
        seiten = set(aktuell.seiten) if aktuell else set()
        if schluessel == "kein":
            seiten = set()
        elif schluessel == "alle":
            seiten = set("tblrh")
        elif schluessel == "aussen":
            seiten = set("tblr")
        else:
            k = {"unten": "b", "oben": "t", "links": "l", "rechts": "r", "innen_h": "h"}[schluessel]
            seiten ^= {k}
        basis = aktuell or self._rahmen_stil
        self.ed.set_absatzrahmen(basis.mit_seiten("".join(seiten)).text() if seiten else None)

    def absatzRahmen(self, k=None, seite: str = "rahmen"):
        """Fenster „Rahmen und Schattierung“ (Reiter Rahmen · Seitenrand · Schattierung); ``seite`` wählt den Reiter."""
        if not self.ed:
            return
        from lunivo_writer.ui.baukasten.rahmen_schattierung import RahmenSchattierungDialog
        from lunivo_writer.ui.baukasten.fenster_stapel import ausfuehren
        fuell, muster = self.ed.absatzschatten()
        alt_rand = self.ed.page.border
        d = RahmenSchattierungDialog(self.w, rahmen=self.ed.absatzrahmen(), fuell=fuell, muster=muster, seitenrand=alt_rand,
                                     fuer=["Absatz"], seite=seite)
        if not ausfuehren(d):
            return
        linie = d.rahmen()
        if linie is not None:
            self._rahmen_stil = linie.mit_seiten("tblr")
        self.ed.set_absatzrahmen(linie.text() if linie is not None else None)
        self.ed.set_absatzschatten(*d.schattierung())
        if d.seitenrand() != alt_rand:
            self._seite_aendern(border=d.seitenrand())
