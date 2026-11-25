"""Fluss layout: aus ``vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QLabel
from vcl.qt.widgets.bausteine.abstaende.raster_hilfen import Anordnung
from vcl.qt.widgets.bausteine.abstaende.plan_raster import PlanRaster
from vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter_hilfen import _natuerlich


class FlussLayout(PlanRaster):
    """Elemente in gleich breiten Gitterspalten, die umbrechen: so viele Spalten, wie in die Breite passen, der Rest in den nächsten
    Gitterzeilen — Ankreuzfelder, Optionen und Knöpfe stehen dadurch in sauberen Spalten untereinander. Eine Beschriftung und das Feld dahinter
    bleiben eine Einheit (Beschriftungs- und Feldspalte). ``zentriert``: die Spalten stehen mittig statt links."""

    def __init__(self, abstand: int = 6, zentriert: bool = False):
        super().__init__()
        self._abstand = abstand
        self._zentriert = zentriert

    def _neu_aufnehmen(self, it) -> None:
        self.invalidate()

    def _einheiten(self) -> list[list]:
        """Beschriftung + nächstes Feld sind eine Einheit, alles andere steht für sich (ausgeblendete Elemente zählen nicht)."""
        items = [i for i in self.elemente() if not i.isEmpty()]
        out, i = [], 0
        while i < len(items):
            it = items[i]
            if isinstance(it.widget(), QLabel) and i + 1 < len(items) and not isinstance(items[i + 1].widget(), QLabel):
                out.append([it, items[i + 1]]); i += 2
            else:
                out.append([it]); i += 1
        return out

    def _masse(self, einheiten: list) -> tuple[int, int, int]:
        """→ (Breite der Beschriftungsspalte, Breite der Feldspalte, Breite einer Einheit)."""
        nat = lambda i: max(_natuerlich(i), i.minimumSize().width())
        lb = max((nat(e[0]) for e in einheiten if len(e) == 2), default=0)
        fb = max((nat(e[1]) for e in einheiten if len(e) == 2), default=0)
        for e in einheiten:
            if len(e) == 1:
                fb = max(fb, nat(e[0]) - (lb + self._abstand if lb else 0))
        return lb, fb, lb + (self._abstand if lb else 0) + fb

    def spalten(self, breite: int) -> int:
        einheiten = self._einheiten()
        if not einheiten:
            return 1
        b = self._masse(einheiten)[2]
        return max(1, min(len(einheiten), (breite + self._abstand) // max(1, b + self._abstand)))

    def _anordnung(self, breite: int) -> Anordnung:
        einheiten = self._einheiten()
        a = self._abstand
        an = Anordnung(waagerecht=a, senkrecht=a)
        if not einheiten:
            return an
        lb, fb, _ub = self._masse(einheiten)
        n = self.spalten(breite)
        je = 2 if lb else 1                                                  # Gitterspalten je Einheit
        start = 0
        hoehen: dict[int, int] = {}
        for k, e in enumerate(einheiten):
            zl, sp = divmod(k, n)
            c = start + sp * je
            if len(e) == 2:
                an.zellen.append((e[0], zl, c, 1, 1, Qt.AlignVCenter | Qt.AlignLeft))
                an.zellen.append((e[1], zl, c + 1, 1, 1, Qt.AlignVCenter))
            else:
                an.zellen.append((e[0], zl, c, 1, je, Qt.AlignVCenter))
            hoehen[zl] = max([hoehen.get(zl, 0)] + [i.sizeHint().height() for i in e])
        for sp in range(n):
            c = start + sp * je
            if lb:
                an.spalten[c] = lb
            an.spalten[c + je - 1] = fb
            an.spalten_dehnung[c + je - 1] = 0 if self._zentriert else 1
        an.hoehe = sum(hoehen.values()) + a * (len(hoehen) - 1)
        return an

    def setGeometry(self, r) -> None:
        """``zentriert``: das ganze Gitter (nicht jedes Element) steht mittig in der verfügbaren Breite."""
        if self._zentriert and self._einheiten():
            m = self.contentsMargins()
            innen = max(1, r.width() - m.left() - m.right())
            n, ub = self.spalten(innen), self._masse(self._einheiten())[2]
            b = min(r.width(), n * ub + (n - 1) * self._abstand + m.left() + m.right())
            r = r.adjusted((r.width() - b) // 2, 0, 0, 0); r.setWidth(b)
        super().setGeometry(r)

    def sizeHint(self) -> QSize:
        return self.minimumSize()

    def minimumSize(self) -> QSize:
        m = self.contentsMargins()
        einheiten = self._einheiten()
        b = self._masse(einheiten)[2] if einheiten else 0
        h = max((i.sizeHint().height() for e in einheiten for i in e), default=0)
        return QSize(b + m.left() + m.right(), h + m.top() + m.bottom())
