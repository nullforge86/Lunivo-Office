"""TextVorlagenBefehle: fachlich abgegrenzte Bandbefehle."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt  # noqa: F401
from PySide6.QtGui import QColor, QFont, QTextCharFormat, QTextCursor, QTextListFormat  # noqa: F401
from PySide6.QtWidgets import QMenu, QMessageBox  # noqa: F401
from lunivo_writer.editor.objekte.linie import Linie  # noqa: F401
from lunivo_writer.ui.baukasten import FarbPalette, RahmenMenue, RasterAuswahl  # noqa: F401
from lunivo_writer.core.farben import Farbe  # noqa: F401
from lunivo_writer.ui.baukasten.basis import farben as BF  # noqa: F401


class TextVorlagenBefehle:
    """Teilbereich der Textbefehle; wird von TextBefehle zusammengesetzt."""

    def _stile_fertig(self) -> None:
        """Nach jeder Änderung an den Vorlagen: Galerie neu füllen, Tastenkombinationen der Vorlagen in allen Dokumenten neu setzen."""
        getattr(self.w.band, "stile_aktualisieren", lambda: None)()
        for t in self.w._doc_tabs():
            t.editor.stil_tasten()

    def _taste_belegt(self, taste: str, eigene: str | None = None) -> str | None:
        """Name dessen, was die Tastenkombination schon hat (Befehl im Fenster oder andere Vorlage), sonst None."""
        from PySide6.QtGui import QAction, QKeySequence
        from lunivo_writer.editor.text import stile
        seq = QKeySequence(taste)
        for a in self.w.findChildren(QAction):
            if any(s == seq for s in a.shortcuts()):
                return a.text().replace("&", "").replace(" …", "").strip() or taste
        for n in stile.namen():
            if n != eigene and stile.definition(n).get("taste") == taste:
                return f"Formatvorlage „{n}“"
        return None

    def neueFormatvorlage(self, k=None):
        """Fenster „Neue Formatvorlage“ (Baukasten); die Werte kommen vom Absatz an der Schreibmarke."""
        from lunivo_writer.editor.text import stile
        from lunivo_writer.ui.baukasten.formatierung.formatvorlage_dialog import FormatvorlageDialog
        from lunivo_writer.ui.baukasten.geruest.fenster_stapel import ausfuehren
        d = FormatvorlageDialog(self.w, start=(self.ed.stil_aus_auswahl() if self.ed else None), belegt=self._taste_belegt,
                                standard_tab_mm=self.ed.standard_tab_mm() if self.ed else None)
        if not ausfuehren(d):
            return
        erg = d.ergebnis()
        std = erg.pop("tab_standard", None)
        if self.ed and std:
            self.ed.set_standard_tab_mm(std)
        merken = erg.pop("zur_vorlage", True)                 # „Zur Vorlage hinzufügen“: auch für künftige Dokumente speichern
        grund = stile.anlegen(erg.pop("name"), basis=erg.pop("basis"), folge=erg.pop("folge"), **erg)
        if grund:
            QMessageBox.warning(self.w, "Neue Formatvorlage", grund)
            return
        if merken:
            self.w.settings.set("stile/eigene", stile.als_json_neu())
        self._stile_fertig()

    def formatvorlageAendern(self, name: str):
        """Rechtsklick auf eine Vorlage in der Galerie ▸ Ändern …: dasselbe Fenster, der Name steht fest."""
        from lunivo_writer.editor.text import stile
        from lunivo_writer.ui.baukasten.formatierung.formatvorlage_dialog import FormatvorlageDialog
        from lunivo_writer.ui.baukasten.geruest.fenster_stapel import ausfuehren
        d = FormatvorlageDialog(self.w, aendern=name, belegt=self._taste_belegt, standard_tab_mm=self.ed.standard_tab_mm() if self.ed else None)
        if not ausfuehren(d):
            return
        erg = d.ergebnis()
        std = erg.pop("tab_standard", None)
        if self.ed and std:
            self.ed.set_standard_tab_mm(std)
        erg.pop("zur_vorlage", None)
        erg.pop("name"); basis, folge = erg.pop("basis"), erg.pop("folge")
        if stile.ist_eigen(name):
            stile.loeschen(name)
            stile.anlegen(name, basis=basis, folge=folge, **erg)
        else:
            stile.aendern(name, **erg)
        self.w.settings.set("stile/aenderungen", stile.als_json())
        self.w.settings.set("stile/eigene", stile.als_json_neu())
        for t in self.w._doc_tabs():
            t.editor.stil_neu_anwenden(name)
        self._stile_fertig()

    def formatvorlageLoeschen(self, name: str):
        from lunivo_writer.editor.text import stile
        if not stile.ist_eigen(name):
            return
        if QMessageBox.question(self.w, "Formatvorlage löschen", f"„{name}“ löschen? Absätze behalten ihr Aussehen, gelten aber wieder als „Standard“.") != QMessageBox.Yes:
            return
        for t in self.w._doc_tabs():
            t.editor.stil_entfernen(name)
        stile.loeschen(name)
        self.w.settings.set("stile/eigene", stile.als_json_neu())
        self._stile_fertig()


    vorlageNeu = neueFormatvorlage                                  # Menüleiste ▸ Start ▸ Stile ▸ Neue Formatvorlage …
