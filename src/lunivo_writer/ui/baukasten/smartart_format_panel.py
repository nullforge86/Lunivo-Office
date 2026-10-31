"""„Formatierung“ für SmartArt in der rechten Seitenleiste: Füllung und Linie, Effekte, Textoptionen — für den gewählten Knoten, ohne Auswahl für alle.

Das Panel ist das des Diagramms (``DiagrammFormatPanel``, gebaut aus ``ObjektFormatPanel``) ohne Teilliste, ohne „Optionen“ und ohne „Größe und Eigenschaften“.
Werte und Meldungen sind dieselben wie beim Diagrammteil (Format wie ``teil_format`` in ``editor/diagramm_format.py``): ``setze({"format": {…}})``,
``geaendert({"fuell": …, "linie": …, …})`` bzw. ``geaendert({"text": {…}})``. Zeichnen: ``editor/smartart.py``.
"""
from __future__ import annotations

from lunivo_writer.ui.baukasten.diagramm_format_panel import DiagrammFormatPanel


class SmartArtFormatPanel(DiagrammFormatPanel):
    def __init__(self, parent=None, werte: dict | None = None):
        super().__init__(parent, werte)
        self._nur_format()

    def _nur_format(self) -> None:
        self.teil_wahl.hide()
        kopf = self.layout().itemAt(0)
        for i in range(kopf.count() if kopf is not None and kopf.layout() is not None else 0):
            w = kopf.layout().itemAt(i).widget()
            if w is not None:
                w.hide()
        for i in (2, 3):
            self.reiter.setTabVisible(i, False)

    def _teil_einrichten(self, werte: dict) -> None:
        super()._teil_einrichten(werte)
        if hasattr(self, "reiter") and self.reiter.count() > 3:
            self._nur_format()
            self.optionen.setTabText(0, "Formoptionen"); self.optionen.setTabEnabled(0, True); self.optionen.setTabEnabled(1, True)
