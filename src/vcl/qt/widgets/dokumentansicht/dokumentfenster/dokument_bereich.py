"""Ein geöffnetes Dokument: Zeichenfläche auf grauem Arbeitsgrund, Pfad, Meta, Wiederherstellungs-Kennung.

Der Tab besitzt das Dokument (``core.document.Dokument``) und über den ``KernEditor`` dessen Bearbeitungssitzung; die Zeichenfläche zeigt es.
"""
from __future__ import annotations

import os

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QScrollArea

from framework.dokumentverwaltung.dokumentpflege import wiederherstellung
from core.dokument.abschnitte.seite import PageSettings
from writer.werte import mm_zu_px as mm_to_px
from vcl.qt.widgets.dokumentansicht.bearbeitung.kern_editor import KernEditor


class DocumentTab(QScrollArea):
    layout_geaendert = Signal(str)

    def __init__(self, kennung: int, path: str | None = None, title: str | None = None):
        super().__init__()
        self.setWidgetResizable(True)
        self.setFrameShape(QScrollArea.NoFrame)
        self.setBackgroundRole(self.backgroundRole().Dark)
        self.kennung = kennung
        self.editor = KernEditor(kennung)
        from vcl.qt.widgets.dokumentansicht.ansicht.lineal_h import LinealH
        from vcl.qt.widgets.dokumentansicht.ansicht.lineal_v import LinealV
        # Die Lineale stehen fest am Rand des Fensters (im Rand des Viewports) und folgen dem Blatt beim Rollen
        self.lineal_h = LinealH(self); self.lineal_v = LinealV(self)
        self.lineal_h.hide(); self.lineal_v.hide()
        self._lineale = (False, False)
        self.lineal_h.randGeaendert.connect(self._rand)
        self.lineal_v.randGeaendert.connect(self._rand)
        self.lineal_h.einzugGeaendert.connect(lambda l, r, f: self.editor.set_indents(l, r, f))
        for leiste in (self.horizontalScrollBar(), self.verticalScrollBar()):
            leiste.valueChanged.connect(self._lineale_neu_zeichnen)
        self.setWidget(self.editor.ansicht)
        self.layout_art = "blatt"
        self.path = path
        self.title = title or (os.path.basename(path) if path else "Unbenannt")
        self.meta: dict = self.editor.meta
        self.token = wiederherstellung.new_token()
        self.untitled = path is None
        self.editor.ansicht.setFocus()

    def set_layout(self, art: str) -> None:
        """blatt/kern (Drucklayout) | web (Weblayout, eine endlose Seite) | doppelt (zwei Seiten nebeneinander)."""
        self.layout_art = art
        self.editor.ansicht.set_seitenansicht({"web": "web", "doppelt": "doppelt"}.get(art, "einzeln"))
        self._lineale_anordnen()
        self.layout_geaendert.emit(art)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._lineale_anordnen()
        if self.layout_art == "web":
            self.editor.ansicht.set_seitenansicht("web")                   # die Seite folgt der Breite des Fensters

    def _rand(self, seite: str, mm: float) -> None:
        pg = self.editor.abschnitt_seite()
        setattr(pg, {"links": "margin_left_mm", "rechts": "margin_right_mm", "oben": "margin_top_mm",
                     "unten": "margin_bottom_mm"}[seite], mm)
        self.editor.page_settings_changed(pg)

    def zeige_lineale(self, waagerecht: bool, senkrecht: bool) -> None:
        self._lineale = (waagerecht, senkrecht)
        self._lineale_anordnen()

    def _lineale_anordnen(self) -> None:
        """Lineale in den Rand des Viewports legen; nur im Drucklayout."""
        from vcl.qt.widgets.dokumentansicht.ansicht.lineal_hilfen import HOEHE
        h, v = self._lineale if self.layout_art in ("blatt", "kern") else (False, False)
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
        frei = self.viewport().width() - 24
        self.editor.set_zoom(frei / mm_to_px(self.page.width_mm))

    def zoom_seite(self) -> None:
        """Eine Seite: die ganze Seite ist sichtbar."""
        b = (self.viewport().width() - 24) / mm_to_px(self.page.width_mm)
        h = (self.viewport().height() - 24) / mm_to_px(self.page.height_mm)
        self.editor.set_zoom(min(b, h))

    @property
    def page(self) -> PageSettings:
        return self.editor.page

    def modell_fuer_speichern(self):
        """Das Dokument des Tabs."""
        return self.editor.sitzung.dokument

    def is_modified(self) -> bool:
        return self.editor.document().isModified()

    def set_path(self, path: str) -> None:
        self.path = path
        self.untitled = False
        self.title = os.path.basename(path)
