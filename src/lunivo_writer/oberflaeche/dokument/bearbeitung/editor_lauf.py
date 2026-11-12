"""Der Seitenlauf im Editor (siehe ``editor/layout/seitenlauf.py`` und ``dokumentation/architektur/layout-schicht.md``).

Ist der Lauf eingeschaltet, setzt er das Dokument in Blattkoordinaten mit dem Zoom; der Editor zeigt es ohne die Umrechnung zwischen
Textfluss und Blatt, die er für die Qt-Anordnung braucht. Cursor, Klick, Ziehen, Markierung und Eingabe bleiben beim ``QTextEdit``.

Einschalten ``lauf_einschalten()``, ausschalten ``lauf_ausschalten()``. Ein Dokument behält seinen Lauf, bis es geschlossen wird: eine
eigene Layout-Klasse lässt sich aus Python nicht wieder gegen die Standard-Anordnung tauschen. Deshalb schaltet der Editor ihn erst von selbst
ein, wenn der Lauf alles kann, was im Dokument stehen darf (``unterstuetzt``)."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPen

from lunivo_writer.adapter.qt.geometrie import rect_to_qt
from lunivo_writer.editor.layout.seitenlauf import LAUF_STANDARD  # noqa: F401  (``dokument_editor`` liest den Schalter hier)

from lunivo_writer.kern.farben import Farbe
from lunivo_writer.modelle.seite import mm_to_px, umbruchraster


class LaufBaustein:
    """Baustein von ``DocumentEditor``: Seitenlauf einsetzen und seine Blattmaße für die Anzeige liefern."""

    _lauf = None

    def setDocument(self, doc) -> None:
        """Ein anderes Dokument: der Seitenlauf gehört dem Dokument (es löscht ihn mit sich), das neue bekommt seinen eigenen."""
        self._lauf = None
        super().setDocument(doc)

    def lauf_aktiv(self) -> bool:
        return self._lauf is not None

    def lauf_einschalten(self) -> bool:
        """Den Seitenlauf einsetzen (nur Blattmodus und nur, wenn er das Dokument kennt). → True, wenn er jetzt läuft."""
        from lunivo_writer.editor.layout.seitenlauf import Seitenlauf, unterstuetzt
        from lunivo_writer.oberflaeche.dokument.bearbeitung.editor_gemeinsam import BLATT_ABSTAND_PX
        if not unterstuetzt(self.document()):
            return False
        if self._lauf is None:
            self._lauf = Seitenlauf(self.document(), self.page, self.zoom, rand_oben=max(10.0, BLATT_ABSTAND_PX * self.zoom))
            self.document().setDocumentLayout(self._lauf)
            self._lauf.documentSizeChanged.connect(self._passe_hoehe_an)
        self._lauf_auffrischen()
        return True

    def lauf_ausschalten(self) -> None:
        """Für den Editor ohne Lauf weiterarbeiten: nur im Anzeigemodell; die Layout-Klasse bleibt am Dokument (siehe Modulkopf)."""
        self._lauf = None

    def _lauf_auffrischen(self, voll: bool = True) -> None:
        """Nach einer Änderung von Seite oder Zoom neu setzen (``voll``), nach einer Eingabe nur die Anzeigemaße anpassen: gesetzt hat
        der Lauf schon selbst, und zwar nur ab dem geänderten Absatz."""
        lauf = self._lauf
        if lauf is None:
            return
        web = float(self._web_breite) if self.web else None
        if not voll and lauf.basis is self.page and lauf.endlos == web and abs(lauf.zoom - self.zoom) <= 1e-9:
            pass
        else:
            lauf.basis = self.page
            lauf.endlos_setzen(web, neu_setzen=False)
            if abs(lauf.zoom - self.zoom) > 1e-9:
                lauf.zoom_setzen(self.zoom, neu_setzen=False)
            lauf.voll_setzen()
        if self.web:                                           # Weblayout: ein endloser Fluss in der Breite des Fensters
            self._qplan = None
            self.viewport().update()
            return
        self._qbreite = lauf._breite / max(self.zoom, 1e-9)
        self._qplan = [b.seite for b in lauf.blaetter]
        self.setFixedWidth(int(lauf._breite) + getattr(self, "_blasen_extra", 0))
        self._passe_hoehe_an()
        self.viewport().update()

    # ---- Maße der Blätter in der Form, die der Editor kennt (``_blatt`` in ``editor_spalten.py``) -----------------------------
    def _lauf_blatt(self, k: int) -> dict:
        bl = self._lauf.blaetter[max(0, min(k, len(self._lauf.blaetter) - 1))]
        z = self.zoom
        pg = bl.seite
        return {"x": bl.x, "W": bl.breite, "H": bl.hoehe, "ml": bl.text_links, "mt": bl.text_oben,
                "mb": mm_to_px(pg.margin_bottom_mm) * z, "leer": bl.leer, "cw": pg.content_width_px * z, "ch": umbruchraster(pg.content_height_px * z), "pg": pg}

    def _lauf_oben(self) -> list[float]:
        return [b.oben for b in self._lauf.blaetter]

    def _lauf_blatt_bei_y(self, y: float) -> int:
        return self._lauf.blatt_bei_y(y)

    def _lauf_rechteck(self, k: int) -> QRectF:
        return rect_to_qt(self._lauf.blaetter[max(0, min(k, len(self._lauf.blaetter) - 1))].rechteck)

    def _lauf_frei_index(self) -> dict:
        return self._lauf.frei_index()

    # ---- Zierat auf dem Blatt: Spaltenlinien und Zeilennummern -----------------------------------------------------------------
    def _lauf_spaltenlinien(self, p, farbe: QColor) -> None:
        """Die Trennlinie zwischen den Spalten, auf jedem Blatt nach dessen eigener Einrichtung und Spaltenaufteilung."""
        lauf = self._lauf
        p.setPen(QPen(farbe, 1))
        for bl in lauf.blaetter:
            sp = lauf.plan.bereiche[bl.bereich].spalten
            if not bl.seite.spalten_linie or len(sp) < 2:
                continue
            for a, b in zip(sp, sp[1:]):
                x = int(bl.text_links + (a.x + a.breite + b.x) / 2 * self.zoom)
                p.drawLine(x, int(bl.oben + bl.text_oben), x, int(bl.oben + bl.text_oben + bl.text_hoehe))

    def _lauf_zeilennummern(self, p) -> None:
        """Zeilennummern links vom Text jedes Blattes; „jede Seite neu“ beginnt auf jedem Blatt bei 1."""
        lauf = self._lauf
        f = p.font(); f.setPixelSize(max(7, int(9 * self.zoom))); p.setFont(f)
        p.setPen(QColor(Farbe.GRAU))
        for k, y, h, nr in lauf.zeilennummern(self.page.zeilennummern_neu):
            rechts = lauf.blaetter[k].text_links - 8 * self.zoom
            p.drawText(QRectF(rechts - 44 * self.zoom, y, 44 * self.zoom, h), Qt.AlignRight | Qt.AlignVCenter, str(nr))
