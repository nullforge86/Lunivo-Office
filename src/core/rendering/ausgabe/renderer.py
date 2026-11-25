"""Der Dokument-Renderer: zeichnet Seiten des Layout-Ergebnisses über das Dokumentmodell auf ein ``RenderTarget``. Seitenaufbau in ``seitenrenderer.py``, Text in
``textrenderer.py``, Tabellen in ``tabellenrenderer.py``, Objekte in ``objektrenderer.py``, Auswahl und Schreibmarke in ``auswahlrenderer.py``. Ohne Qt."""
from __future__ import annotations

from core.dokument.dokument import Dokument
from core.layout.ergebnis import Ergebnis
from core.textsatz.engine import FontSpec
from core.rendering.ausgabe.backend import RenderTarget
from core.rendering.seite.seitenrenderer import SeitenRenderer


class DokumentRenderer(SeitenRenderer):
    def zeichne_seiten(self, b: RenderTarget, dok: Dokument, erg: Ergebnis, indizes, zeilennummern_schrift: FontSpec | None = None) -> None:
        """Mehrere Seiten nacheinander auf dasselbe Ziel (der Ursprung liegt für jede Seite an ihrer linken oberen Ecke; das Ziel richtet das der Aufrufer ein)."""
        for i in indizes:
            self.zeichne_seite(b, dok, erg, i, zeilennummern_schrift)
