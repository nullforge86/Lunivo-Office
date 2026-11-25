"""Raster — die EINE Layoutgrundlage der selbst gebauten Oberfläche: jedes Fenster, jede Seitenleiste, jeder Dialog ordnet seine Elemente mit ``QGridLayout``.

Es gibt genau drei Bausteine, alle abgeleitet von ``RasterLayout`` (selbst ein ``QGridLayout``):

* ``RasterLinie`` (``RasterSpalte`` / ``RasterZeile``) — Elemente der Reihe nach untereinander (Zellen ``(i, 0)``) oder nebeneinander (Zellen ``(0, i)``).
  Für den Aufbau gibt es die gewohnten Befehle (``addWidget(w, dehnung, ausrichtung)``, ``addLayout``, ``addStretch``, ``addSpacing``, ``insertWidget`` …);
  die Anordnung selbst übernimmt das Gitter: Dehnung = Zeilen-/Spaltendehnung, Abstand = Zellenabstand, Ausrichtung = Zellenausrichtung.
  Erzeugt werden sie nur über ``geruest/rollen.py`` (``spalte(rolle)`` / ``reihe(rolle)``), damit Ränder und Abstände aus der Rollentabelle kommen.
* ``PlanRaster`` — ein Gitter, dessen Zeilen und Spalten bei jeder Breite neu bestimmt werden (responsiv): ``KartenRaster``, ``FlussLayout``,
  ``FormularGitter``, die Knopfzeile der Dialoge. Eine Unterklasse beschreibt nur, welche Zelle jedes Element bei dieser Breite bekommt
  (``_anordnung(breite) -> Anordnung``); Zellen setzen, Spalten-/Zeilenmaße übernehmen und die Elemente legen tut das ``QGridLayout``.
* ``tabellen_gitter`` (``felder/formular_gitter.py``) — ein Gitter mit festen Spalten (Kacheln, Zwei-Listen-Gerüst), ebenfalls ein ``RasterLayout``.

Rasterregeln (Ränder, waagerechte/senkrechte Abstände) stehen ausschließlich in ``geruest/rollen.py`` (``ROLLEN``) bzw. ``mass.py``; hier wird keine
eigene Zahl festgelegt. Kein Baustein setzt Positionen selbst mit ``setGeometry`` einzelner Elemente.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QBoxLayout, QGridLayout, QLayout, QLayoutItem, QSizePolicy, QSpacerItem, QWidget

_MAX = 16777215                                                     # QWIDGETSIZE_MAX
_KEINE = Qt.AlignmentFlag(0)


def _ausrichtung(a) -> Qt.AlignmentFlag:
    """Ausrichtung als ``Qt.AlignmentFlag`` (auch aus ``0`` oder einer Zahl)."""
    return a if isinstance(a, Qt.AlignmentFlag) else Qt.AlignmentFlag(int(a or 0))


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


class RasterSpalte(RasterLinie):
    """Elemente untereinander."""

    def __init__(self, eltern: QWidget | None = None):
        super().__init__(True, eltern)


class RasterZeile(RasterLinie):
    """Elemente nebeneinander."""

    def __init__(self, eltern: QWidget | None = None):
        super().__init__(False, eltern)


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


def kanten_anordnung(plaetze: list, breite: int, hoehe: int) -> Anordnung:
    """Gitter aus Rechtecken (Element, x, y, b, h): jede Kante eines Elements wird eine Gitterlinie, jedes Element belegt die Zellen zwischen
    seinen Kanten. Spalten und Zeilen bekommen genau die Breite/Höhe zwischen zwei Linien (Abstand 0); die letzte Zeile nimmt überzählige Höhe."""
    xs = sorted({0, max(1, breite)} | {x for _it, x, _y, _b, _h in plaetze} | {x + b for _it, x, _y, b, _h in plaetze})
    ys = sorted({0, max(0, hoehe)} | {y for _it, _x, y, _b, _h in plaetze} | {y + h for _it, _x, y, _b, h in plaetze})
    xi, yi = {x: k for k, x in enumerate(xs)}, {y: k for k, y in enumerate(ys)}
    a = Anordnung(hoehe=hoehe)
    for it, x, y, b, h in plaetze:
        c0, r0 = xi[x], yi[y]
        a.zellen.append((it, r0, c0, max(1, yi[y + h] - r0), max(1, xi[x + b] - c0), None))
    a.spalten = {k: xs[k + 1] - xs[k] for k in range(len(xs) - 1)}
    a.zeilen = {k: ys[k + 1] - ys[k] for k in range(len(ys) - 1)}
    return a


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
