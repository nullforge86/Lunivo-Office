"""Druckfunktionen des Hauptfensters.

Dieser Baustein wird von DateienBaustein eingebunden, damit die bisherigen
Methodennamen und Aufrufstellen unverändert bleiben.
"""
from __future__ import annotations

from PySide6.QtCore import QTimer
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import QMessageBox


class DateienDruckenBaustein:
    def druck_start(self) -> dict:
        """Letzte Wahl im Druckfenster; Hintergrund, Grafik und Leerseiten teilen sich die Schalter mit den Optionen."""
        g, gb = self.settings.get, self.settings.get_bool
        start = {"hintergrund": gb("drucken/hintergrund", True), "zeichnungen": gb("drucken/zeichnungen", True), "leere": gb("drucken/leere", True),
                 "drucker": g("drucken/dlg_drucker", ""), "kopien": 1, "sortieren": gb("drucken/dlg_sortieren", True),
                 "platzhalter": gb("drucken/dlg_platzhalter", False), "steuerelemente": gb("drucken/dlg_steuerelemente", True),
                 "kommentare": g("drucken/dlg_kommentare", "keine"), "schwarz": gb("drucken/dlg_schwarz", False),
                 "vorschau": gb("drucken/dlg_vorschau", True), "beidseitig": g("drucken/dlg_beidseitig", "aus")}
        return start


    def druck_merken(self, e: dict) -> None:
        for k in ("hintergrund", "zeichnungen", "leere"):
            self.settings.set(f"drucken/{k}", e[k])
        for k in ("drucker", "sortieren", "platzhalter", "steuerelemente", "kommentare", "schwarz", "vorschau", "beidseitig"):
            self.settings.set(f"drucken/dlg_{k}", e[k])


    def druck_vorschau(self, t):
        from lunivo_writer.editor.seite.druck import optionen_aus, vorschau_bild

        def bilder(nummern, ein):
            opt = optionen_aus(self.druckoptionen(), ein, t.editor.noten)
            return vorschau_bild(t.editor.document(), t.page, opt, t.editor.noten, nummern)
        return bilder


    def _druck_args(self, t) -> dict:
        from lunivo_writer.editor.seite.pagination import seitenzahl
        start = self.druck_start()
        if self.settings.get("drucken/vorgabe", "Alle Seiten") == "Aktuelle Seite":
            start.update(bereich="seiten", seiten_text=str(t.editor.current_page()))
        ps = t.page
        return dict(seiten=seitenzahl(t.editor.document(), ps, t.editor.noten), papier_mm=(ps.width_mm, ps.height_mm), quer=bool(ps.landscape),
                    start=start, auswahl=t.editor.textCursor().hasSelection(), vorschau=self.druck_vorschau(t))


    def druck_ansicht(self, t, parent=None):
        """Das Druckfenster ohne Knopfzeile (Menü ▸ Drucken, zweite Spalte)."""
        from lunivo_writer.ui.baukasten.dokument.druck_dialog import DruckAnsicht
        a = DruckAnsicht(parent=parent, **self._druck_args(t))
        a.eigenschaften.connect(lambda name: self._drucker_eigenschaften(a, name))
        return a


    def print_dialog(self):
        """Drucken (Strg+P, Schnellzugriff, Druckvorschau): die Seite „Drucken“ im Menü, kein eigenes Fenster."""
        if self.current_tab():
            self.backstage_oeffnen("drucken")


    def druckfenster(self):
        """Dasselbe als eigenes Fenster (für Aufrufer ohne Menü)."""
        t = self.current_tab()
        if not t:
            return
        from lunivo_writer.ui.baukasten.dokument.druck_dialog import DruckDialog
        dlg = DruckDialog(self, hilfe=self.druck_hilfe, **self._druck_args(t))
        dlg.ansicht.eigenschaften.connect(lambda name: self._drucker_eigenschaften(dlg.ansicht, name))
        if not dlg.exec():
            return
        self.drucke_nach_wahl(t, dlg.ergebnis())


    def druck_hilfe(self):
        QMessageBox.information(self, "Drucken", "Oben wählen Sie Drucker, Seiten, Kopien und Papier; darunter sehen Sie das Blatt, wie es gedruckt wird. "
                                "Auf „Lunivo-Office“ stehen die Inhalte des Dokuments.")


    def drucke_nach_wahl(self, t, e: dict) -> None:
        """Druckt das Blatt `t` nach der Wahl `e` (Druckfenster oder Menü ▸ Drucken)."""
        from PySide6.QtPrintSupport import QPrinterInfo
        from lunivo_writer.editor.seite.druck import drucken
        self.druck_merken(e)
        info = QPrinterInfo.printerInfo(e["drucker"]) if e["drucker"] else QPrinterInfo()
        pr = QPrinter(info, QPrinter.HighResolution if self.settings.get_bool("drucken/hoch", True) else QPrinter.ScreenResolution) \
            if not info.isNull() else self._neuer_drucker()
        if not e["drucker"]:                                           # kein Drucker eingerichtet: das Fenster des Systems übernimmt
            if not QPrintDialog(pr, self).exec():
                return
        self._vor_dem_drucken(t)
        n = drucken(pr, t.editor.document(), t.page, self.druckoptionen(), e, t.editor.noten)
        self.statusBar().showMessage(f"An den Drucker gesendet ({n} Blatt)." if n else "Keine Seiten zum Drucken.", 4000)


    def _drucker_eigenschaften(self, dlg, name: str) -> None:
        from PySide6.QtPrintSupport import QPrinterInfo
        pr = QPrinter(QPrinterInfo.printerInfo(name))
        sys_dlg = QPrintDialog(pr, self)
        sys_dlg.setOption(QPrintDialog.PrintPageRange, False)
        if sys_dlg.exec():
            dlg.drucker_setzen(pr.copyCount(), {QPrinter.DuplexLongSide: "lang", QPrinter.DuplexShortSide: "kurz"}.get(pr.duplex(), "aus"))


    def print_preview(self):
        t = self.current_tab()
        if not t:
            return
        from lunivo_writer.editor.seite.druck import Zwischenseiten, optionen_aus
        from lunivo_writer.ui.baukasten.dokument.druckvorschau import DruckVorschau
        opt = optionen_aus(self.druckoptionen(), self.druck_start(), t.editor.noten)
        dlg = DruckVorschau(self, Zwischenseiten(t.editor.document(), t.page, opt, t.editor.noten))
        dlg.drucken.connect(lambda: QTimer.singleShot(0, self.print_dialog))
        dlg.showMaximized()
        dlg.exec()


    def ausgabe_ppi(self) -> int:
        """Standard-Ausgabeziel: Auflösung für „Als Bild exportieren“."""
        try:
            return int(str(self.settings.get("ausgabe/ppi", "150")).split()[0])
        except (ValueError, IndexError):
            return 150


    def druckoptionen(self) -> dict:
        return {"umgekehrt": self.settings.get_bool("drucken/umgekehrt", False),
                "duplex": self.settings.get("drucken/duplex", "alle"),
                "hintergrund": self.settings.get_bool("drucken/hintergrund", True),
                "leere": self.settings.get_bool("drucken/leere", True),
                "hervorhebungen": self.settings.get_bool("drucken/hervorhebungen", True),
                "textmarken": self.settings.get_bool("drucken/textmarken", False),
                "textgrenzen": self.settings.get_bool("drucken/textgrenzen", False),
                "zuschnitt": self.settings.get_bool("drucken/zuschnitt", False),
                "silbenfarben": self._silben_fuer_druck(),
                "versteckt": self.settings.get_bool("drucken/versteckt", False),
                "felder_code": self.settings.get_bool("drucken/felder_code", False),
                "zeichnungen": self.settings.get_bool("drucken/zeichnungen", True),
                "balken": self.settings.get("aenderungen/balken", "links"),
                "notenlinks": self.settings.get_bool("pdf/notenlinks", True),
                "blasen": self._blasen_fuer_druck(),
                "nur_formular": self.settings.get_bool("drucken/nur_formular", False)}


    def _blasen_fuer_druck(self):
        from lunivo_writer.editor.objekte import sprechblasen as SB
        e = self.current_editor()
        k = SB.konfig_lesen(self.settings)
        if e is None or not self.settings.get_bool("sprechblasen/drucken", False) or not SB.aktiv(k):
            return None
        if not e.kommentare and not (k["verwenden"] == "Immer" and e.aenderungen()):
            return None
        return {"konfig": k, "kommentare": dict(e.kommentare)}


    def _silben_fuer_druck(self):
        from lunivo_writer.editor.text import silbenfarben as S
        k = S.konfig_lesen(self.settings)
        return dict(k, nur_absatz=False) if k["an"] and k["drucken"] else None


    def _neuer_drucker(self):
        return QPrinter(QPrinter.HighResolution if self.settings.get_bool("drucken/hoch", True) else QPrinter.ScreenResolution)


    def _vor_dem_drucken(self, tab):
        """„Felder vor dem Drucken aktualisieren“: Verzeichnisse neu rechnen."""
        if self.settings.get_bool("drucken/felder", True):
            from lunivo_writer.editor.dokument.verzeichnis import verzeichnis_aktualisieren
            verzeichnis_aktualisieren(tab.editor)
