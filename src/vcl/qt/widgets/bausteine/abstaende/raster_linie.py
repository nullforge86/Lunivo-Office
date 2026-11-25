"""Raster linie: aus ``vcl.qt.widgets.bausteine.abstaende.raster`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QBoxLayout, QGridLayout, QLayout, QLayoutItem, QSizePolicy, QSpacerItem, QWidget
from vcl.qt.widgets.bausteine.abstaende.raster_hilfen import RasterLayout


_KEINE = Qt.AlignmentFlag(0)


def _ausrichtung(a) -> Qt.AlignmentFlag:
    """Ausrichtung als ``Qt.AlignmentFlag`` (auch aus ``0`` oder einer Zahl)."""
    return a if isinstance(a, Qt.AlignmentFlag) else Qt.AlignmentFlag(int(a or 0))


class RasterLinie(RasterLayout):
    """Elemente der Reihe nach in einer Gitterspalte (``senkrecht``) oder Gitterzeile. Reihenfolge = Zellenfolge; Dehnung je Element = Dehnung
    seiner Zeile/Spalte; ``addStretch``/``addSpacing`` sind Platzhalterzellen. Wird ein Element entfernt, bleibt seine Zelle leer — ein leeres
    Gitterfeld hat keine Größe und keinen Abstand, die Anordnung ändert sich also nicht."""

    def __init__(self, senkrecht: bool = True, eltern: QWidget | None = None):
        self._senkrecht, self._umgekehrt = senkrecht, False
        self._soll: dict[int, int] = {}                                           # gewünschte Dehnung je Zelle (wirkt nur, solange die Zelle belegt und sichtbar ist)
        super().__init__(eltern) if eltern is not None else super().__init__()

    # ---- Lage im Gitter --------------------------------------------------------------------------------
    def senkrecht(self) -> bool:
        return self._senkrecht

    def _lage(self, k: int) -> tuple[int, int]:
        return (k, 0) if self._senkrecht else (0, k)

    def _stelle(self, i: int) -> int:
        r, c, _rs, _cs = self.getItemPosition(i)
        return r if self._senkrecht else c

    def _naechste(self) -> int:
        if self.count() == 0:                                                     # leer: alte Dehnungen gelten nicht mehr
            self._soll.clear()
            for k in range(max(self.rowCount(), self.columnCount()) + 1):
                if self.rowStretch(k): self.setRowStretch(k, 0)
                if self.columnStretch(k): self.setColumnStretch(k, 0)
        return max((self._stelle(i) for i in range(self.count())), default=-1) + 1

    def _dehnung_setzen(self, k: int, d: int) -> None:
        self._soll[k] = max(0, int(d))
        (self.setRowStretch if self._senkrecht else self.setColumnStretch)(k, self._soll[k])

    def _dehnung_lesen(self, k: int) -> int:
        return self._soll.get(k, 0)

    def _dehnungen_abgleichen(self) -> None:
        """Wie bei einer Reihe von Elementen: ein ausgeblendetes oder entferntes Element gibt seinen Anteil am freien Platz ab. Eine Gitterzeile
        behält ihre Dehnung sonst auch leer und nähme den Platz weg. Platzhalter (``addStretch``) behalten ihre Dehnung."""
        belegt = set()
        for i in range(self.count()):
            it = self.itemAt(i)
            if it is not None and (it.spacerItem() is not None or not it.isEmpty()):
                belegt.add(self._stelle(i))
        lesen, setzen = (self.rowStretch, self.setRowStretch) if self._senkrecht else (self.columnStretch, self.setColumnStretch)
        for k in range(self.rowCount() if self._senkrecht else self.columnCount()):
            soll = self._soll.get(k, 0) if k in belegt else 0
            if lesen(k) != soll:
                setzen(k, soll)

    def setGeometry(self, r) -> None:
        self._dehnungen_abgleichen()
        super().setGeometry(r)

    def _platz(self, i: int | None) -> int | None:
        """Index für ein Einfügen; ``None`` = hinten anhängen ohne Umordnen."""
        n = self.count()
        if i is None or i < 0 or i >= n:
            return None if not self._umgekehrt else n
        return i

    def _neu_ordnen(self, i: int) -> None:
        """Das zuletzt angehängte Element an die Stelle ``i`` rücken und alle Zellen der Reihe nach neu belegen."""
        dehn = [self._dehnung_lesen(self._stelle(k)) for k in range(self.count())]
        alt = self.leeren()
        neu, nd = alt.pop(), dehn.pop()
        alt.insert(i, neu); dehn.insert(i, nd)
        self._belegen([it for it, *_ in alt], dehn)

    def _belegen(self, items: list, dehn: list) -> None:
        self._soll.clear()
        for k in range(max(self.rowCount(), self.columnCount()) + 1):
            self.setRowStretch(k, 0); self.setColumnStretch(k, 0)
        n = len(items)
        for k, (it, d) in enumerate(zip(items, dehn)):
            pos = n - 1 - k if self._umgekehrt else k
            self.zelle_setzen(it, *self._lage(pos))
            self._dehnung_setzen(pos, d)

    def _anhaengen(self, setzen, i: int | None, dehnung: int) -> None:
        stelle = self._platz(i)
        k = self._naechste()
        setzen(*self._lage(k))
        self._dehnung_setzen(k, dehnung)
        if stelle is not None:
            self._neu_ordnen(stelle)

    # ---- Aufbau (gewohnte Befehle) -----------------------------------------------------------------------
    def addWidget(self, w: QWidget, dehnung: int = 0, ausrichtung=_KEINE, **kw) -> None:       # type: ignore[override]
        self.insertWidget(-1, w, kw.get("stretch", dehnung), kw.get("alignment", ausrichtung))

    def insertWidget(self, i: int, w: QWidget, dehnung: int = 0, ausrichtung=_KEINE, **kw) -> None:
        a = _ausrichtung(kw.get("alignment", ausrichtung))
        self._anhaengen(lambda r, c: QGridLayout.addWidget(self, w, r, c, 1, 1, a), i, kw.get("stretch", dehnung))

    def addLayout(self, l: QLayout, dehnung: int = 0, **kw) -> None:                            # type: ignore[override]
        self.insertLayout(-1, l, kw.get("stretch", dehnung))

    def insertLayout(self, i: int, l: QLayout, dehnung: int = 0, **kw) -> None:
        self._anhaengen(lambda r, c: QGridLayout.addLayout(self, l, r, c), i, kw.get("stretch", dehnung))

    def addItem(self, it: QLayoutItem, *gitter) -> None:                                         # type: ignore[override]
        if gitter:                                                                                # Gitterform (Zeile, Spalte …): unverändert
            QGridLayout.addItem(self, it, *gitter)
            return
        self.insertItem(-1, it)

    def insertItem(self, i: int, it: QLayoutItem) -> None:
        self._anhaengen(lambda r, c: QGridLayout.addItem(self, it, r, c), i, 0)

    def addSpacerItem(self, s: QSpacerItem) -> None:
        self.insertItem(-1, s)

    def insertSpacerItem(self, i: int, s: QSpacerItem) -> None:
        self.insertItem(i, s)

    def _abstandhalter(self, groesse: int, dehnbar: bool) -> QSpacerItem:
        pol = QSizePolicy.Expanding if dehnbar else QSizePolicy.Fixed
        if self._senkrecht:
            return QSpacerItem(0, groesse, QSizePolicy.Minimum, pol)
        return QSpacerItem(groesse, 0, pol, QSizePolicy.Minimum)

    def addStretch(self, dehnung: int = 0) -> None:
        self.insertStretch(-1, dehnung)

    def insertStretch(self, i: int, dehnung: int = 0) -> None:
        s = self._abstandhalter(0, True)
        self._anhaengen(lambda r, c: QGridLayout.addItem(self, s, r, c), i, dehnung)

    def addSpacing(self, groesse: int) -> None:
        self.insertSpacing(-1, groesse)

    def insertSpacing(self, i: int, groesse: int) -> None:
        s = self._abstandhalter(groesse, False)
        self._anhaengen(lambda r, c: QGridLayout.addItem(self, s, r, c), i, 0)

    def addStrut(self, groesse: int) -> None:
        """Mindestmaß quer zur Richtung (wie bei ``QBoxLayout``)."""
        (self.setColumnMinimumWidth if self._senkrecht else self.setRowMinimumHeight)(0, groesse)

    def setStretch(self, i: int, dehnung: int) -> None:
        if 0 <= i < self.count():
            self._dehnung_setzen(self._stelle(i), dehnung)

    def stretch(self, i: int) -> int:
        return self._dehnung_lesen(self._stelle(i)) if 0 <= i < self.count() else 0

    def setStretchFactor(self, ziel, dehnung: int) -> bool:                                       # Widget oder Layout
        for i in range(self.count()):
            it = self.itemAt(i)
            if it is not None and (it.widget() is ziel or it.layout() is ziel):
                self.setStretch(i, dehnung)
                return True
        return False

    def spacing(self) -> int:
        return self.verticalSpacing() if self._senkrecht else self.horizontalSpacing()

    # ---- Richtung ------------------------------------------------------------------------------------------
    def direction(self):
        if self._senkrecht:
            return QBoxLayout.BottomToTop if self._umgekehrt else QBoxLayout.TopToBottom
        return QBoxLayout.RightToLeft if self._umgekehrt else QBoxLayout.LeftToRight

    def senkrecht_stellen(self) -> None:
        """Die Elemente untereinander statt nebeneinander (gleiche Reihenfolge, gleiche Dehnungen)."""
        self.setDirection(QBoxLayout.TopToBottom)

    def waagerecht_stellen(self) -> None:
        self.setDirection(QBoxLayout.LeftToRight)

    def setDirection(self, richtung) -> None:
        senkrecht = richtung in (QBoxLayout.TopToBottom, QBoxLayout.BottomToTop)
        umgekehrt = richtung in (QBoxLayout.BottomToTop, QBoxLayout.RightToLeft)
        if (senkrecht, umgekehrt) == (self._senkrecht, self._umgekehrt):
            return
        dehn = [self._dehnung_lesen(self._stelle(k)) for k in range(self.count())]
        alt = sorted(self.leeren(), key=lambda t: (t[1] if self._senkrecht else t[2]) * (-1 if self._umgekehrt else 1))
        wechsel = senkrecht != self._senkrecht
        self._senkrecht, self._umgekehrt = senkrecht, umgekehrt
        items = []
        for it, *_ in alt:
            s = it.spacerItem()
            if s is not None and wechsel:                                                         # Platzhalter drehen mit
                sp, g = s.sizePolicy(), s.sizeHint()
                s.changeSize(g.height(), g.width(), sp.verticalPolicy(), sp.horizontalPolicy())
            items.append(it)
        self._belegen(items, dehn)
