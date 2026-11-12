"""Ein geöffnetes Dokument: Editor auf grauem Arbeitsgrund, Pfad, Meta, Wiederherstellungs-Kennung."""
from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QScrollArea, QWidget

from lunivo_writer.dienste.datei_dienst import Loaded
from lunivo_writer.oberflaeche.dokument.bearbeitung.dokument_editor import DocumentEditor
from lunivo_writer.modelle.seite import PageSettings
from lunivo_writer.dienste import wiederherstellung
from lunivo_writer.oberflaeche.baukasten.basis.mass import RAND_DOKUMENTFLAECHE


class DocumentTab(QScrollArea):
    layout_geaendert = Signal(str)

    def __init__(self, loaded: Loaded | None = None, path: str | None = None, title: str | None = None):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setBackgroundRole(self.backgroundRole().Dark)
        holder = QWidget()
        holder.setBackgroundRole(holder.backgroundRole().Dark)
        holder.setAutoFillBackground(True)
        lay = QHBoxLayout(holder)
        lay.setContentsMargins(*RAND_DOKUMENTFLAECHE)
        self.editor = DocumentEditor()
        from lunivo_writer.oberflaeche.dokument.ansicht.lineal import LinealH, LinealV
        # Die Lineale stehen fest am Rand des Fensters (im Rand des Viewports) und folgen dem Blatt beim Rollen
        self.lineal_h = LinealH(self); self.lineal_v = LinealV(self)
        self.lineal_h.hide(); self.lineal_v.hide()
        self._lineale = (False, False)
        self.lineal_h.randGeaendert.connect(self._rand)
        self.lineal_v.randGeaendert.connect(self._rand)
        self.lineal_h.einzugGeaendert.connect(lambda l, r, f: self.editor.set_indents(l, r, f))
        for leiste in (self.horizontalScrollBar(), self.verticalScrollBar()):
            leiste.valueChanged.connect(self._lineale_neu_zeichnen)
        lay.addStretch(1)
        lay.addWidget(self.editor, 0, Qt.AlignTop)
        lay.addStretch(1)
        self.setWidget(holder)
        self._holder = holder
        self.layout_art = "blatt"
        self.path = path
        self.title = title or (os.path.basename(path) if path else "Unbenannt")
        self.meta: dict = {}
        self.token = wiederherstellung.new_token()
        self.untitled = path is None
        if loaded is not None:
            self.editor.set_document_and_page(loaded.doc, loaded.page)
            self.meta = loaded.meta
        self.editor.document().setDefaultFont(self.editor.document().defaultFont())
        self.editor.zusatz_binden(self.meta)
        from lunivo_writer.oberflaeche.dokument.ansicht.modell_ansicht import KERN_ANSICHT
        if KERN_ANSICHT:
            self.set_layout("kern")

    def set_layout(self, art: str) -> None:
        """blatt (Drucklayout) | web (Weblayout) | doppelt (Zwei Seiten, nur Ansicht) | kern (Drucklayout aus dem Dokumentenkern, bearbeitbar über die Sitzung)."""
        from lunivo_writer.oberflaeche.dokument.ansicht.seiten_ansicht import SeitenAnsicht
        if self.layout_art in ("doppelt", "kern") and art != self.layout_art:
            alt = self.takeWidget()
            if alt is not self._holder and alt is not None:
                alt.deleteLater()
            self.setWidget(self._holder)
            self._holder.show()
        self.layout_art = art
        self._lineale_anordnen()
        self.editor.set_web(art == "web")
        if art == "web":
            self.editor.set_web_breite(self.viewport().width() - 24 - 22)
        if art == "doppelt":
            ansicht = SeitenAnsicht(self.editor, self.viewport().width())
            self.takeWidget()
            self._holder.hide()
            self.setWidget(ansicht)
        if art == "kern":
            from lunivo_writer.oberflaeche.dokument.ansicht.modell_ansicht import ModellAnsicht
            ansicht = ModellAnsicht(lambda: self.editor.modell_spiegel().sitzung())
            ansicht.setReadOnly(self.editor.isReadOnly())
            ansicht.set_zoom(self.editor.zoom)
            self.editor.zoomChanged.connect(ansicht.set_zoom)
            self.takeWidget()
            self._holder.hide()
            self.setWidget(ansicht)
            ansicht.setFocus()
        self.layout_geaendert.emit(art)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._lineale_anordnen()
        if self.layout_art == "web":
            self.editor.set_web_breite(self.viewport().width() - 24 - 22)

    def _rand(self, seite: str, mm: float) -> None:
        pg = self.editor.page.copy()
        setattr(pg, {"links": "margin_left_mm", "rechts": "margin_right_mm", "oben": "margin_top_mm",
                     "unten": "margin_bottom_mm"}[seite], mm)
        self.editor.page_settings_changed(pg)

    def zeige_lineale(self, waagerecht: bool, senkrecht: bool) -> None:
        self._lineale = (waagerecht, senkrecht)
        self._lineale_anordnen()

    def _lineale_anordnen(self) -> None:
        """Lineale in den Rand des Viewports legen; nur im Drucklayout (Weblayout und Zwei Seiten haben keine Blattkanten)."""
        from lunivo_writer.oberflaeche.dokument.ansicht.lineal import HOEHE
        h, v = self._lineale if self.layout_art == "blatt" else (False, False)
        self.setViewportMargins(HOEHE if v else 0, HOEHE if h else 0, 0, 0)
        self.lineal_h.setVisible(h); self.lineal_v.setVisible(v)
        vp = self.viewport().geometry()
        self.lineal_h.setGeometry(vp.left(), 0, vp.width(), HOEHE)
        self.lineal_v.setGeometry(0, vp.top(), HOEHE, vp.height())
        self.lineal_h.update(); self.lineal_v.update()

    def _lineale_neu_zeichnen(self, *_) -> None:
        if self.lineal_h.isVisible():
            self.lineal_h.update()
        if self.lineal_v.isVisible():
            self.lineal_v.update()

    def zoom_breite(self) -> None:
        """Seitenbreite: die Seite füllt die Breite des Fensters."""
        from lunivo_writer.modelle.seite import mm_to_px
        frei = self.viewport().width() - 24
        self.editor.set_zoom(frei / mm_to_px(self.page.width_mm))

    def zoom_seite(self) -> None:
        """Eine Seite: die ganze Seite ist sichtbar."""
        from lunivo_writer.modelle.seite import mm_to_px
        b = (self.viewport().width() - 24) / mm_to_px(self.page.width_mm)
        h = (self.viewport().height() - 24) / mm_to_px(self.page.height_mm)
        self.editor.set_zoom(min(b, h))

    @property
    def page(self) -> PageSettings:
        return self.editor.page

    def is_modified(self) -> bool:
        return self.editor.document().isModified()

    def set_path(self, path: str) -> None:
        self.path = path
        self.untitled = False
        self.title = os.path.basename(path)
