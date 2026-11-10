"""Aktives Dokument und Reiter des Hauptfensters: Zugriff, Titel, Umschalten, Verdrahtung neuer Reiter."""
from __future__ import annotations

from PySide6.QtGui import QIcon

from lunivo_writer.ui.document.bearbeitung.document_editor import DocumentEditor
from lunivo_writer.ui.document.dokumentfenster.document_area import DocumentTab
from lunivo_writer.ui.widgets import icons
from lunivo_writer.ui.baukasten.basis.mass import ICON_TAB_GEAENDERT


class ReiterZustandMixin:
    """Baustein von ``MainWindow`` (siehe ``lunivo_writer/ui/main_window.py``)."""

    # ==== Hilfen ====================================================================
    def current_tab(self) -> DocumentTab | None:
        w = self.tabs.currentWidget()
        return w if isinstance(w, DocumentTab) else None

    def current_editor(self) -> DocumentEditor | None:
        t = self.current_tab()
        return t.editor if t else None

    def _ed(self, fn):
        self.vorschau.ende()
        e = self.current_editor()
        if e is not None:
            fn(e)

    def _doc_tabs(self) -> list[DocumentTab]:
        return [self.tabs.widget(i) for i in range(self.tabs.count())
                if isinstance(self.tabs.widget(i), DocumentTab)]

    def _tab_title(self, tab: DocumentTab) -> str:
        return tab.title

    def _update_tab_titles(self):
        for i in range(self.tabs.count()):
            w = self.tabs.widget(i)
            if isinstance(w, DocumentTab):
                self.tabs.setTabText(i, self._tab_title(w))
                self.tabs.setTabIcon(i, icons.icon("circle", ICON_TAB_GEAENDERT) if w.is_modified() else QIcon())
                self.tabs.setTabToolTip(i, w.path or "Noch nicht gespeichert")
        self._update_window_title()

    def _update_window_title(self):
        t = self.current_tab()
        self.setWindowTitle(f"{self._tab_title(t)} — Lunivo Writer" if t else "Lunivo Writer")

    def _tab_changed(self, _i):
        t = self.current_tab()
        self._refresh_ui()
        self.ki.kontext_pruefen()
        if t:
            t.editor.setFocus()
            t.editor._recount()

    def _refresh_ui(self):
        has = self.current_tab() is not None
        self.docs.stack.setCurrentWidget(self.current_tab() if has else self.leer)
        self.band.aktualisieren(has)
        for a in (self.a_undo, self.a_redo):
            a.setEnabled(has)
        self._update_window_title()
        self._sync_format()
        self._sync_status()
        self._zoom_anzeigen()
        self.assistant.attach(self.current_editor())

    def _connect_tab(self, tab: DocumentTab):
        e = tab.editor
        e.zoomChanged.connect(lambda f, ed=e: ed is self.current_editor() and self._zoom_anzeigen(f))
        e.formatChanged.connect(self._sync_later)
        e.freiAuswahlGeaendert.connect(self._sync_later)
        e.leseschutzGeaendert.connect(self._sync_later)
        from lunivo_writer.ui.widgets.schweb_knopf import SchwebKnopf
        tab._chat_knopf = SchwebKnopf(tab, "chat", "KI-Chat", lambda: self.chat_oeffnen(""))
        self.sidebar.bereich_geaendert.connect(lambda *_: self._chat_knopf_pruefen())
        e.formatChanged.connect(self._effekt_sync)
        e.pageInfoChanged.connect(lambda *_: self._sync_status())
        e.document().modificationChanged.connect(lambda _m: self._update_tab_titles())
        e.document().contentsChanged.connect(self._sync_status)
        e.document().contentsChanged.connect(self.assistant.dokument_geaendert)
        for sig in (e.selectionChanged, e.document().contentsChanged):       # KI-Chat: Markierung/leeres Dokument (nur der aktuelle Editor zählt)
            sig.connect(lambda ed=e: ed is self.current_editor() and self.ki.kontext_pruefen())
        e.document().contentsChanged.connect(self.navigation.spaeter)
        e.document().contentsChanged.connect(lambda ed=e: ed is self.current_editor() and self.ki.dauer_geaendert("absatz"))        # fortlaufende KI-Assistenten
        e.selectionChanged.connect(lambda ed=e: ed is self.current_editor() and self.ki.dauer_geaendert("markierung"))
        e.opt = lambda name, std=True: self.settings.get_bool(name, std)
        e.opt_text = lambda name, std="": self.settings.get(name, std)
        e.autor = self.autor_angaben
        e.mini_hook = self.mini_zeigen
        e.zusatzGeaendert.connect(self.navigation.spaeter)
        e.noteAngeklickt.connect(lambda art, nid: self.noten_feld.oeffnen(art, nid))
        e.set_marken(self.settings.get_bool("ui/marken", False))
        self.formatzeichen_anwenden(e)
        self.lineale_anwenden(tab)
        self._lesehilfe_auf(e)
        felder = self.band.felder
        if felder and e is not None:
            pass

    def _verbinde_felder(self):
        f = self.band.felder
        if not f:
            return
        f["font"].activated.connect(lambda _: self._ed(lambda e: (e.set_font_family(f["font"].currentFont().family()), e.setFocus())))
        f["groesse"].activated.connect(self._size_chosen)
        f["groesse"].lineEdit().editingFinished.connect(self._size_chosen)
        f["stil"].activated.connect(lambda _: self.stil_anwenden(f["stil"].currentText()))

    def stil_anwenden(self, name: str):
        name = "Standard" if name == "Fließtext" else name
        self._ed(lambda e: e.apply_style(name))

    def _size_chosen(self, *_):
        try:
            pt = float(self.band.felder["groesse"].currentText().replace(",", "."))
        except ValueError:
            return
        self._ed(lambda e: (e.set_font_size(pt), e.setFocus()))
