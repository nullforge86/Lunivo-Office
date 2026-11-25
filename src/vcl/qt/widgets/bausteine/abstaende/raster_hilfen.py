"""Raster hilfen: aus ``vcl.qt.widgets.bausteine.abstaende.raster`` herausgelöst."""
from __future__ import annotations
from dataclasses import dataclass, field
from PySide6.QtWidgets import QGridLayout, QLayoutItem


class RasterLayout(QGridLayout):
    """Gemeinsame Basis aller Layouts der Oberfläche (für ``isinstance``-Prüfungen und gemeinsame Hilfen)."""

    def leeren(self) -> list:
        """Alle Elemente aus den Zellen nehmen (nicht löschen) → [(Element, Zeile, Spalte, Zeilen, Spalten)] in der bisherigen Reihenfolge."""
        n = QGridLayout.count(self)
        stellen = [self.getItemPosition(k) for k in range(n)]
        genommen = [QGridLayout.takeAt(self, k) for k in range(n - 1, -1, -1)][::-1]
        return [(it, *pos) for it, pos in zip(genommen, stellen)]

    def zelle_setzen(self, it: QLayoutItem, r: int, c: int, rs: int = 1, cs: int = 1, ausrichtung=None) -> None:
        """Ein (genommenes) Element in eine Zelle legen; ein verschachteltes Layout bekommt dabei wieder dieses Layout als Eltern."""
        a = it.alignment() if ausrichtung is None else ausrichtung
        lay = it.layout()
        if lay is not None:
            QGridLayout.addLayout(self, lay, r, c, rs, cs, a)
        else:
            QGridLayout.addItem(self, it, r, c, rs, cs, a)

    def _rastermass(self, spalten: dict[int, int] | None, zeilen: dict[int, int] | None, sdehn: dict[int, int] | None,
                    zdehn: dict[int, int] | None) -> None:
        """Spaltenbreiten, Zeilenhöhen und Dehnungen übernehmen; nur, was sich ändert (jedes Setzen löst sonst einen neuen Layoutlauf aus)."""
        for werte, lesen, setzen, anzahl in ((spalten, self.columnMinimumWidth, self.setColumnMinimumWidth, self.columnCount()),
                                             (zeilen, self.rowMinimumHeight, self.setRowMinimumHeight, self.rowCount()),
                                             (sdehn, self.columnStretch, self.setColumnStretch, self.columnCount()),
                                             (zdehn, self.rowStretch, self.setRowStretch, self.rowCount())):
            if werte is None:
                continue
            for k in range(max(anzahl, max(werte, default=-1) + 1)):
                soll = werte.get(k, 0)
                if lesen(k) != soll:
                    setzen(k, soll)


# ---- responsives Gitter --------------------------------------------------------------------------------------------
@dataclass
class Anordnung:
    """Was ein ``PlanRaster`` bei einer Breite ins Gitter legt. ``zellen``: (Element, Zeile, Spalte, Zeilen, Spalten, Ausrichtung oder None).
    ``spalten``/``zeilen``: Mindestbreite/-höhe je Spalte/Zeile; ``spalten_dehnung``/``zeilen_dehnung``: Dehnung. ``hoehe``: benötigte Höhe."""
    zellen: list = field(default_factory=list)
    spalten: dict = field(default_factory=dict)
    zeilen: dict = field(default_factory=dict)
    spalten_dehnung: dict = field(default_factory=dict)
    zeilen_dehnung: dict = field(default_factory=dict)
    waagerecht: int = 0
    senkrecht: int = 0
    hoehe: int = 0
