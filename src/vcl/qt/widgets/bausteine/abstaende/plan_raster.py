"""Plan raster: aus ``vcl.qt.widgets.bausteine.abstaende.raster`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QGridLayout, QLayout, QLayoutItem, QSizePolicy, QSpacerItem, QWidget
from vcl.qt.widgets.bausteine.abstaende.raster_hilfen import Anordnung, RasterLayout


_MAX = 16777215                                                     # QWIDGETSIZE_MAX


class PlanRaster(RasterLayout):
    """``QGridLayout``, dessen Zellen der Breite folgen. Unterklassen liefern ``_anordnung(breite)``; ``setGeometry`` legt die Elemente in die Zellen
    dieser Breite und lässt das Gitter sie anordnen. Höhe für eine Breite kommt aus derselben Anordnung (``hoehe``), unabhängig davon, für welche
    Breite die Zellen gerade belegt sind. Eine dehnbare Zeile unter allem nimmt überzählige Höhe auf (sie zählt nicht als Element)."""

    dehnt_nicht = True                                       # das Layout verlangt selbst keinen überzähligen Platz

    def __init__(self, eltern: QWidget | None = None):
        self._rest: QSpacerItem | None = None
        super().__init__(eltern) if eltern is not None else super().__init__()
        self.setSpacing(0)

    # ---- von Unterklassen -------------------------------------------------------------------------------
    def _anordnung(self, breite: int) -> Anordnung:
        raise NotImplementedError

    def _vergessen(self, it: QLayoutItem) -> None:
        """Unterklassen streichen ein entnommenes Element aus ihrer eigenen Beschreibung."""

    # ---- Elemente (ohne die Restzeile) -------------------------------------------------------------------
    def _innen(self, i: int) -> int:
        """Index im Gitter für den Elementindex ``i`` (die Restzeile wird übersprungen); -1, wenn es ihn nicht gibt."""
        k = -1
        for j in range(QGridLayout.count(self)):
            if QGridLayout.itemAt(self, j) is self._rest:
                continue
            k += 1
            if k == i:
                return j
        return -1

    def count(self) -> int:
        return QGridLayout.count(self) - (1 if self._rest is not None else 0)

    def itemAt(self, i: int):
        j = self._innen(i) if i >= 0 else -1
        return QGridLayout.itemAt(self, j) if j >= 0 else None

    def takeAt(self, i: int):                                                          # Qt entnimmt Elemente (gelöschtes Widget, removeWidget)
        j = self._innen(i) if i >= 0 else -1
        if j < 0:
            return None
        it = QGridLayout.takeAt(self, j)
        if it is not None:
            self._vergessen(it)
        return it

    def elemente(self) -> list:
        return [self.itemAt(i) for i in range(self.count())]

    def addItem(self, it: QLayoutItem, *gitter) -> None:                               # type: ignore[override]
        """Ein Element kommt sofort ins Gitter (vorläufige Zelle); seine Zelle bei der tatsächlichen Breite bekommt es beim nächsten Legen."""
        if gitter:
            QGridLayout.addItem(self, it, *gitter)
        else:
            self.zelle_setzen(it, 0, 0)
        self._neu_aufnehmen(it)

    def _neu_aufnehmen(self, it: QLayoutItem) -> None:
        """Unterklassen merken sich das neue Element (Spanne, Einheit …)."""

    def element_widget(self, w: QWidget) -> QLayoutItem:
        """``w`` aufnehmen, ohne ``_neu_aufnehmen`` (für Unterklassen mit eigener Beschreibung)."""
        self.addChildWidget(w)
        from PySide6.QtWidgets import QWidgetItem
        it = QWidgetItem(w)
        QGridLayout.addItem(self, it, 0, 0)
        return it

    def element_layout(self, l: QLayout) -> QLayoutItem:
        QGridLayout.addLayout(self, l, 0, 0)
        return l

    # ---- Legen ----------------------------------------------------------------------------------------
    @staticmethod
    def _schluessel(it: QLayoutItem):
        return it.widget() or it.layout() or it.spacerItem() or it

    def _uebernehmen(self, a: Anordnung) -> None:
        soll = {self._schluessel(it): (r, c, rs, cs, al) for it, r, c, rs, cs, al in a.zellen}
        aendern = False
        for j in range(QGridLayout.count(self)):
            it = QGridLayout.itemAt(self, j)
            if it is self._rest:
                continue
            r, c, rs, cs, al = soll.get(self._schluessel(it), (0, 0, 1, 1, None))
            if tuple(self.getItemPosition(j)) != (r, c, rs, cs) or (al is not None and it.alignment() != al):
                aendern = True
                break
        zeilen = max([r + rs for _it, r, _c, rs, _cs, _al in a.zellen] + [max(a.zeilen, default=-1) + 1, 0])
        rest_falsch = self._rest is None or aendern or self.getItemPosition(self._innen_rest())[0] != zeilen
        if aendern or rest_falsch:
            for it, *_alt in self.leeren():
                if it is self._rest:
                    continue
                r, c, rs, cs, al = soll.get(self._schluessel(it), (0, 0, 1, 1, None))
                self.zelle_setzen(it, r, c, rs, cs, al)
            self._rest = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
            QGridLayout.addItem(self, self._rest, zeilen, 0)
        zd = dict(a.zeilen_dehnung); zd[zeilen] = 1
        zm = dict(a.zeilen); zm[zeilen] = 0
        self._rastermass(a.spalten, zm, a.spalten_dehnung, zd)
        if self.horizontalSpacing() != a.waagerecht:
            self.setHorizontalSpacing(a.waagerecht)
        if self.verticalSpacing() != a.senkrecht:
            self.setVerticalSpacing(a.senkrecht)

    def _innen_rest(self) -> int:
        return next((j for j in range(QGridLayout.count(self)) if QGridLayout.itemAt(self, j) is self._rest), -1)

    def setGeometry(self, r) -> None:
        m = self.contentsMargins()
        self._uebernehmen(self._anordnung(max(1, r.width() - m.left() - m.right())))
        super().setGeometry(r)

    # ---- Maße aus der Anordnung (nicht aus der gerade belegten Zelle) -----------------------------------------
    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, breite: int) -> int:
        m = self.contentsMargins()
        return self._anordnung(max(1, breite - m.left() - m.right())).hoehe + m.top() + m.bottom()

    def minimumHeightForWidth(self, breite: int) -> int:
        return self.heightForWidth(breite)

    def maximumSize(self) -> QSize:
        return QSize(_MAX, _MAX)

    def expandingDirections(self):
        return Qt.Orientation(0) if self.dehnt_nicht else super().expandingDirections()
