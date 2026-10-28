"""Befehle: Seriendruck (Reiter „Mailings“ nach der WPS-Vorlage)."""
from __future__ import annotations

import os


class SerienBefehle:
    """Befehle des Kontext-Reiters „Mailings“. Ein Baustein von ``Befehle`` (siehe ``core/commands.py``).

    Die Datenquelle gehört zum Dokumentfenster (``tab.serie``, nicht gespeichert): pfad, spalten, saetze, aktiv (je Satz ein Haken),
    zuordnung {Feld im Text: Spalte}, nr (Datensatz der Vorschau, ab 0), hervorheben."""

    # ---- Zustand -----------------------------------------------------------------------------------------------
    def _serie(self) -> dict | None:
        t = self.w.current_tab()
        if t is None:
            return None
        if not hasattr(t, "serie"):
            t.serie = {"pfad": "", "spalten": [], "saetze": [], "aktiv": [], "zuordnung": {}, "nr": 0, "hervorheben": True}
        return t.serie

    def _hat_quelle(self) -> bool:
        s = self._serie()
        return bool(s and s["saetze"])

    def _gewaehlte(self) -> list[dict]:
        """Die angehakten Sätze, mit den Namen der Felder im Text."""
        from lunivo_writer.editor import sendungen as S
        s = self._serie()
        return [S.zugeordnet(x, s["zuordnung"]) for x, an in zip(s["saetze"], s["aktiv"]) if an] if s else []

    kann_serienEmpfaenger = kann_serienZuordnen = kann_serienVorschau = kann_serienHervorheben = _hat_quelle
    kann_serienErster = kann_serienVorheriger = kann_serienNaechsterSatz = kann_serienLetzter = _hat_quelle
    kann_serienNeuesDokument = kann_serienEinzeln = kann_serienDrucker = _hat_quelle

    def an_serienVorschau(self) -> bool:
        from lunivo_writer.ui.document import serien_vorschau
        t = self.w.current_tab()
        return bool(t) and serien_vorschau.aktiv(t)

    def an_serienHervorheben(self) -> bool:
        s = self._serie()
        return bool(s and s["hervorheben"])

    # ---- Reiter ------------------------------------------------------------------------------------------------
    def serienReiter(self, k=None):
        """Verweise ▸ Seriendruck: den Reiter „Mailings“ zeigen und dorthin wechseln."""
        band = self.w.band
        band.kontext("serien", True)
        i = band.kontext_index.get("serien")
        if i is not None:
            band.reiter.setCurrentIndex(i)
        self._datensatz_anzeigen()

    def serienSchliessen(self, k=None):
        from lunivo_writer.ui.document import serien_vorschau
        t = self.w.current_tab()
        if t is not None:
            serien_vorschau.beenden(t)
        self.w.band.kontext("serien", False)

    # ---- Datenquelle -------------------------------------------------------------------------------------------
    def serienQuelle(self, k=None):
        """Datenquelle öffnen: eine Empfängerliste als Text (CSV mit ; , oder Tabulator; erste Zeile = Spaltennamen)."""
        from lunivo_writer.editor import sendungen as S
        from lunivo_writer.ui.baukasten.speichern_fenster import datei_waehlen
        s = self._serie()
        if s is None:
            return
        pfade = datei_waehlen(self.w, "Datenquelle öffnen", os.path.dirname(s["pfad"]) or "",
                              "Empfängerlisten (*.csv *.tsv *.txt);;Alle Dateien (*)")
        if not pfade:
            return
        tab = S.quelle_lesen(pfade[0])
        if not tab:
            self.w.statusBar().showMessage("Die Datei braucht eine Kopfzeile und mindestens einen Empfänger.", 6000)
            return
        self._quelle_setzen(pfade[0], *tab)

    def _quelle_setzen(self, pfad: str, spalten: list[str], saetze: list[dict]) -> None:
        s = self._serie()
        s.update(pfad=pfad, spalten=spalten, saetze=saetze, aktiv=[True] * len(saetze), nr=0)
        self.w.statusBar().showMessage(f"Datenquelle „{os.path.basename(pfad)}“: {len(saetze)} Empfänger.", 5000)
        self._vorschau_auffrischen()

    def serienQuelleSchliessen(self, k=None):
        from lunivo_writer.ui.document import serien_vorschau
        s = self._serie()
        if s is None:
            return
        s.update(pfad="", spalten=[], saetze=[], aktiv=[], zuordnung={}, nr=0)
        t = self.w.current_tab()
        serien_vorschau.beenden(t)
        self._datensatz_anzeigen()

    def menue_serienQuelleKlappe(self):
        from PySide6.QtWidgets import QMenu
        m = QMenu(self.w)
        m.addAction("Datenquelle &öffnen…", lambda: (self.serienQuelle(), self.w.band.aktualisieren()))
        zu = m.addAction("Datenquelle &schließen", lambda: (self.serienQuelleSchliessen(), self.w.band.aktualisieren()))
        m.aboutToShow.connect(lambda: zu.setEnabled(self._hat_quelle()))
        return m

    def serienEmpfaenger(self, k=None):
        from lunivo_writer.ui.dialogs.serien_fenster import EmpfaengerDialog
        s = self._serie()
        if not self._hat_quelle():
            return
        d = EmpfaengerDialog(self.w, s["spalten"], s["saetze"], s["aktiv"])
        if d.exec():
            s["aktiv"] = d.ergebnis()
            s["nr"] = 0
            self._vorschau_auffrischen()

    # ---- Felder -------------------------------------------------------------------------------------------------
    def serienFeld(self, k=None):
        from lunivo_writer.editor import sendungen as S
        from lunivo_writer.ui.dialogs.serien_fenster import FeldDialog
        e = self.ed
        if not e:
            return
        s = self._serie()
        d = FeldDialog(self.w, s["spalten"] if s else [])
        d.einfuegen.connect(lambda name: S.feld_einfuegen(e, name))
        d.exec()
        self._vorschau_auffrischen()

    def serienNaechster(self, k=None):
        from lunivo_writer.editor import sendungen as S
        if self.ed:
            S.naechster_einfuegen(self.ed)
            self._vorschau_auffrischen()

    def serienHervorheben(self, k=None):
        """Seriendruckfelder hervorheben: der farbige Hintergrund der Felder an oder aus (nur Anzeige, ändert den Text nicht)."""
        from lunivo_writer.editor import sendungen as S
        s = self._serie()
        if not s or not self.ed:
            return
        s["hervorheben"] = not s["hervorheben"]
        S.felder_hervorheben(self.ed.document(), s["hervorheben"])

    def serienZuordnen(self, k=None):
        from lunivo_writer.editor import sendungen as S
        from lunivo_writer.ui.dialogs.serien_fenster import ZuordnenDialog
        s = self._serie()
        if not self._hat_quelle() or not self.ed:
            return
        felder = [f for f in S.felder_im_text(self.ed.document()) if f != S.NAECHSTER]
        d = ZuordnenDialog(self.w, felder, s["spalten"], s["zuordnung"])
        if d.exec():
            s["zuordnung"] = d.ergebnis()
            self._vorschau_auffrischen()

    # ---- Vorschau ------------------------------------------------------------------------------------------------
    def _briefe(self) -> list[list[dict]]:
        from lunivo_writer.editor import sendungen as S
        return S.gruppen(self.ed.document(), self._gewaehlte()) if self.ed else []

    def _vorschau_auffrischen(self) -> None:
        from lunivo_writer.editor import sendungen as S
        from lunivo_writer.ui.document import serien_vorschau
        t = self.w.current_tab()
        if t is not None and serien_vorschau.aktiv(t):
            briefe = self._briefe()
            s = self._serie()
            if not briefe:
                serien_vorschau.beenden(t)
            else:
                s["nr"] = max(0, min(s["nr"], len(briefe) - 1))
                serien_vorschau.zeigen(t, S.brief_fuer(t.editor.document(), briefe[s["nr"]]))
        self._datensatz_anzeigen()

    def serienVorschau(self, k=None):
        """Seriendruck-Vorschau an/aus: zeigt den Brief des gewählten Datensatzes; die Vorlage bleibt unverändert."""
        from lunivo_writer.ui.document import serien_vorschau
        t = self.w.current_tab()
        if t is None:
            return
        if serien_vorschau.aktiv(t):
            serien_vorschau.beenden(t)
            self._datensatz_anzeigen()
            return
        if not self._briefe():
            self.w.statusBar().showMessage("Keine Empfänger: Datenquelle öffnen und Empfänger anhaken.", 5000)
            return
        serien_vorschau.zeigen(t, t.editor.document().clone())
        self._vorschau_auffrischen()

    def _gehe_satz(self, wohin) -> None:
        from lunivo_writer.ui.document import serien_vorschau
        s = self._serie()
        n = len(self._briefe())
        if not s or not n:
            return
        s["nr"] = max(0, min(n - 1, wohin(s["nr"], n)))
        t = self.w.current_tab()
        if not serien_vorschau.aktiv(t):
            self.serienVorschau()
        else:
            self._vorschau_auffrischen()

    def serienErster(self, k=None): self._gehe_satz(lambda _i, _n: 0)
    def serienVorheriger(self, k=None): self._gehe_satz(lambda i, _n: i - 1)
    def serienNaechsterSatz(self, k=None): self._gehe_satz(lambda i, _n: i + 1)
    def serienLetzter(self, k=None): self._gehe_satz(lambda _i, n: n - 1)

    def feld_datensatz(self):
        """Das Feld zwischen „Vorheriger“ und „Nächster Datensatz“: Nummer des gezeigten Datensatzes (Eingabe springt dorthin)."""
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIntValidator
        from PySide6.QtWidgets import QLineEdit
        f = QLineEdit(); f.setFixedWidth(80); f.setMinimumHeight(36); f.setAlignment(Qt.AlignCenter)
        f.setAccessibleName("Datensatz"); f.setToolTip("Datensatz"); f.setValidator(QIntValidator(1, 999999, f))
        f.returnPressed.connect(lambda: f.text() and self._gehe_satz(lambda _i, _n: int(f.text()) - 1))
        return f

    def _datensatz_anzeigen(self) -> None:
        from lunivo_writer.ui.document import serien_vorschau
        f = getattr(self.w.band, "felder", {}).get("datensatz")
        if f is None:
            return
        s = self._serie()
        t = self.w.current_tab()
        an = bool(s and s["saetze"]) and t is not None and serien_vorschau.aktiv(t)
        f.setEnabled(an)
        f.setText(str(s["nr"] + 1) if an else "")

    # ---- Fertigstellen -------------------------------------------------------------------------------------------
    def serienNeuesDokument(self, k=None):
        """In neuem Dokument zusammenführen: alle Briefe hintereinander, je Brief eine neue Seite."""
        from lunivo_writer.editor import sendungen as S
        e = self.ed
        if not e or not self._hat_quelle():
            return None
        saetze = self._gewaehlte()
        quelle, seite, titel = e.document(), e.page.copy(), self.w.current_tab().title
        t = self._neues_blatt(titel + " — Seriendruck")
        n = S.serienbrief_erzeugen(quelle, saetze, t.editor.document())
        t.editor.page_settings_changed(seite)
        self.w.statusBar().showMessage(f"{n} Briefe in einem neuen Dokument (die Vorlage bleibt unverändert).", 6000)
        return t

    def serienEinzeln(self, k=None):
        """In anderem neuen Dokument zusammenführen: jeder Brief als eigene DOCX-Datei in einem Ordner."""
        from lunivo_writer.editor import sendungen as S
        from lunivo_writer.services import file_service
        from lunivo_writer.ui.baukasten.speichern_fenster import ordner_waehlen
        e = self.ed
        if not e or not self._hat_quelle():
            return
        ordner = ordner_waehlen(self.w, "Ordner für die einzelnen Briefe", os.path.dirname(self._serie()["pfad"]) or os.path.expanduser("~"))
        if not ordner:
            return
        briefe = S.gruppen(e.document(), self._gewaehlte())
        name = os.path.splitext(self.w.current_tab().title)[0] or "Brief"
        for i, gruppe in enumerate(briefe, 1):
            d = S.brief_fuer(e.document(), gruppe)
            file_service.save(os.path.join(ordner, f"{name} {i:03d}.docx"), d, e.page, dict(self.w.current_tab().meta), sicherung=False)
        self.w.statusBar().showMessage(f"{len(briefe)} Briefe gespeichert in „{ordner}“.", 6000)

    def serienDrucker(self, k=None):
        """An Drucker zusammenführen: die Briefe in ein neues Dokument und gleich das Druckfenster."""
        if self.serienNeuesDokument() is not None:
            self.drucken()
