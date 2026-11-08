"""KartenRaster: ein Raster mit gemeinsamem Maßsystem für Karten, Schalter und Knöpfe.

Maßsystem
---------
* Das Raster besteht aus gleich großen Zellen. Die Spaltenzahl folgt der verfügbaren Breite (``min_breite`` je Zelle), die Zeileneinheit ist für alle Zeilen gleich.
* Jedes Element belegt eine **Rasterspanne** ``Spalten × Zeilen`` (``1×1``, ``2×1``, ``2×2``, ``3×1`` …). Seine Außenmaße ergeben sich nur daraus:
  Breite = Spalten · Zellenbreite + (Spalten − 1) · Abstand, Höhe entsprechend. Elemente mit gleicher Spanne sind also gleich groß; es gibt keine Pixelwerte je Element.
* Die Spannen sind **zentral** festgelegt (``SPANNEN``). Ein Element bekommt seine Spanne über einen Namen (``addWidget(w, "breit")``), über die Eigenschaft ``raster_spanne``
  (Name oder ``"2x1"``) oder die Vorgabe ``SPANNE_STANDARD``.
* Wird die Breite kleiner, ändert sich die Spaltenzahl und die Elemente ordnen sich neu. Passt eine Spanne nicht mehr (mehr Spalten als vorhanden), wird sie auf die vorhandene Spaltenzahl
  gekürzt: das Element belegt dann eine ganze Zeile. Nichts wird abgeschnitten, überlagert oder aus dem sichtbaren Bereich geschoben.
* Die Zeileneinheit wächst gemeinsam für alle Elemente so weit, dass der Inhalt jedes Elements in seine Spanne passt.

    raster = KartenRaster(min_breite=132, abstand=6)
    raster.addWidget(karte)                  # 1×1
    raster.addWidget(grosse_karte, "gross")  # 2×2
"""
from __future__ import annotations

import math

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtWidgets import QGridLayout, QLayout, QLayoutItem, QWidget
from lunivo_writer.ui.baukasten.formular_gitter import tabellen_gitter
from lunivo_writer.ui.baukasten.mass import RAND_KEIN

SPANNE_STANDARD: tuple[int, int] = (1, 1)
SPANNEN: dict[str, tuple[int, int]] = {          # die einzige Stelle, an der Rasterspannen festgelegt werden
    "karte": (1, 1),
    "breit": (2, 1),
    "gross": (2, 2),
    "band": (3, 1),
}
ZEILE_MIN = 36                                    # kleinste Zeileneinheit in Pixeln (die Einheit wächst mit dem Inhalt)


def spanne_von(name_oder_text: object) -> tuple[int, int]:
    """Spanne aus einem Namen der zentralen Tabelle (``"breit"``), aus ``"2x1"`` oder aus einem Paar."""
    if isinstance(name_oder_text, (tuple, list)) and len(name_oder_text) == 2:
        return max(1, int(name_oder_text[0])), max(1, int(name_oder_text[1]))
    t = str(name_oder_text or "").strip().lower()
    if t in SPANNEN:
        return SPANNEN[t]
    if "x" in t:
        try:
            c, r = t.split("x", 1)
            return max(1, int(c)), max(1, int(r))
        except ValueError:
            pass
    return SPANNE_STANDARD


class KartenRaster(QLayout):
    def __init__(self, parent: QWidget | None = None, min_breite: int = 132, abstand: int = 6, spalten_fest: int = 0, gleiche_hoehe: bool = True):
        self._items: list[QLayoutItem] = []
        self._spannen: dict[int, tuple[int, int]] = {}
        super().__init__(parent)
        self._min_b, self._abstand, self._fest = min_breite, abstand, spalten_fest      # spalten_fest > 0: immer diese Spaltenzahl (1 = untereinander)
        self._gleich = gleiche_hoehe                                                    # False: jede Rasterzeile so hoch wie ihr höchstes Element (Zeilen mit natürlicher Höhe)
        self.setContentsMargins(*RAND_KEIN)

    # ---- QLayout ----------------------------------------------------------------------------------------
    def addWidget(self, w: QWidget, spanne: object = None) -> None:                    # type: ignore[override]
        super().addWidget(w)
        it = self._items[-1]
        self._spannen[id(it)] = spanne_von(spanne if spanne is not None else w.property("raster_spanne"))

    def addItem(self, item: QLayoutItem) -> None:
        self._items.append(item)
        self.invalidate()

    def setSpanne(self, w: QWidget, spanne: object) -> None:
        for it in self._items:
            if it.widget() is w:
                self._spannen[id(it)] = spanne_von(spanne)
        self.invalidate()

    def count(self) -> int:
        return len(self._items)

    def itemAt(self, i: int):
        return self._items[i] if 0 <= i < len(self._items) else None

    def takeAt(self, i: int):
        if 0 <= i < len(self._items):
            it = self._items.pop(i)
            self._spannen.pop(id(it), None)
            return it
        return None

    def hasHeightForWidth(self) -> bool:
        return True

    def expandingDirections(self):
        return Qt.Orientation(0)

    # ---- Maße -------------------------------------------------------------------------------------------
    def spalten(self, breite: int) -> int:
        if self._fest:
            return self._fest
        a = self._abstand
        return max(1, (max(breite, 1) + a) // (self._min_b + a))

    def _sichtbar(self) -> list[QLayoutItem]:
        return [i for i in self._items if i.widget() is None or not i.widget().isHidden()]

    def _plan(self, breite: int):
        """Plätze (Item, x, y, b, h) und Gesamthöhe bei der Breite ``breite``."""
        items = self._sichtbar()
        n, a = self.spalten(breite), self._abstand
        zb = max(1, (breite - a * (n - 1)) // n)                                       # Zellenbreite
        # 1. Platzierung im Raster: der Reihe nach, erste freie Stelle ab dem Zeiger (kein Umsortieren), Spanne auf die vorhandene Spaltenzahl gekürzt
        belegt: set[tuple[int, int]] = set()
        stellen, zeiger = [], 0
        for it in items:
            c, r = self._spannen.get(id(it), SPANNE_STANDARD)
            c = min(c, n)
            while True:
                zl, sp = divmod(zeiger, n)
                if sp + c <= n and all((zl + dz, sp + dc) not in belegt for dz in range(r) for dc in range(c)):
                    break
                zeiger += 1
            for dz in range(r):
                for dc in range(c):
                    belegt.add((zl + dz, sp + dc))
            stellen.append((it, zl, sp, c, r))
            zeiger += c
        # 2. Zeilenhöhen. gleiche_hoehe: eine gemeinsame Zeileneinheit, so hoch, dass jedes Element mit seinem Inhalt in seine Spanne passt.
        #    sonst: jede Rasterzeile so hoch wie ihr höchstes Element (Spannen über mehrere Zeilen bekommen den Fehlbetrag in der letzten Zeile)
        def noetig(it, c):
            bw = c * zb + (c - 1) * a
            hfw = it.heightForWidth(bw) if it.hasHeightForWidth() else it.sizeHint().height()
            return max(hfw, it.minimumSize().height())
        zeilen = max((zl + r for _it, zl, _sp, _c, r in stellen), default=0)
        if self._gleich:
            einheit = ZEILE_MIN
            for it, zl, sp, c, r in stellen:
                einheit = max(einheit, math.ceil((noetig(it, c) - (r - 1) * a) / r))
            hoehen = [einheit] * zeilen
        else:
            hoehen = [ZEILE_MIN] * zeilen
            for it, zl, sp, c, r in stellen:
                if r == 1:
                    hoehen[zl] = max(hoehen[zl], noetig(it, c))
            for it, zl, sp, c, r in stellen:
                if r > 1:
                    fehlt = noetig(it, c) - (sum(hoehen[zl:zl + r]) + (r - 1) * a)
                    if fehlt > 0:
                        hoehen[zl + r - 1] += fehlt
        ys = [sum(hoehen[:k]) + k * a for k in range(zeilen)]
        plaetze = []
        for it, zl, sp, c, r in stellen:
            plaetze.append((it, sp * (zb + a), ys[zl], c * zb + (c - 1) * a, sum(hoehen[zl:zl + r]) + (r - 1) * a))
        return plaetze, (sum(hoehen) + (zeilen - 1) * a if zeilen else 0)

    def heightForWidth(self, breite: int) -> int:
        m = self.contentsMargins()
        return self._plan(breite - m.left() - m.right())[1] + m.top() + m.bottom()

    def sizeHint(self) -> QSize:
        m = self.contentsMargins()
        return QSize(self._min_b + m.left() + m.right(), self.heightForWidth(self._min_b) if self._items else 0)

    def minimumSize(self) -> QSize:
        m = self.contentsMargins()
        return QSize(60 + m.left() + m.right(), m.top() + m.bottom())

    def setGeometry(self, r: QRect) -> None:
        super().setGeometry(r)
        m = self.contentsMargins()
        innen = r.adjusted(m.left(), m.top(), -m.right(), -m.bottom())
        for it, x, y, b, h in self._plan(innen.width())[0]:
            it.setGeometry(QRect(innen.x() + x, innen.y() + y, b, h))


def kacheln_legen(gitter: QGridLayout, kacheln, spalten: int) -> None:
    """Kacheln der Reihe nach in ``spalten`` Spalten ins Gitter setzen (zeilenweise, links oben beginnend)."""
    spalten = max(1, spalten)
    for n, k in enumerate(kacheln):
        gitter.addWidget(k, n // spalten, n % spalten)


def kachel_gitter(kacheln=(), spalten: int = 3, *, eltern: QWidget | None = None, rand: tuple | None = RAND_KEIN, abstand: int | None = None,
                  waagerecht: int | None = None, senkrecht: int | None = None, oben_links: bool = False, rest_dehnt: bool = False) -> QGridLayout:
    """Kachelraster fester Kachelgröße (Farben, Formen, Seitenbildchen …): die Rasterlogik für alle Stellen, an denen das Gitter der Zweck ist.
    ``rest_dehnt``: überzählige Breite fällt in eine zusätzliche Spalte, die Kacheln bleiben links. Kacheln gleicher Größe, die sich der Breite anpassen
    sollen, gehören in ``KartenRaster``."""
    g = tabellen_gitter(eltern, rand=rand, abstand=abstand, waagerecht=waagerecht, senkrecht=senkrecht, oben_links=oben_links)
    kacheln_legen(g, kacheln, spalten)
    if rest_dehnt:
        g.setColumnStretch(max(1, spalten), 1)
    return g


_KURZ = ("QCheckBox", "QRadioButton", "QPushButton", "QToolButton")


def kurze_gruppen_ins_raster(fenster: QWidget, max_breite: int = 150) -> int:
    """Zentrale Automatik für jedes Fenster der Seitenleiste: aufeinanderfolgende kurze Ankreuzfelder, Optionsfelder und Knöpfe in einem senkrechten Layout
    (``QVBoxLayout``) kommen in ein ``KartenRaster`` (alle ``1×1``) und stehen so nebeneinander, statt einzeln untereinander. Gibt die Zahl der Gruppen zurück."""
    from PySide6.QtWidgets import QBoxLayout, QVBoxLayout

    def kurz(it) -> bool:
        w = it.widget() if it is not None else None
        return (w is not None and not w.isHidden() and any(c.__name__ in _KURZ for c in type(w).__mro__)
                and (w.natuerliche_breite() if hasattr(w, "natuerliche_breite") else w.sizeHint().width()) <= max_breite
                and not w.property("raster_nein"))

    n = 0
    layouts = [x.layout() for x in [fenster] + fenster.findChildren(QWidget) if x.layout() is not None]
    gesehen: set[int] = set()
    while layouts:
        l = layouts.pop()
        if id(l) in gesehen:
            continue
        gesehen.add(id(l))
        for i in range(l.count()):
            sub = l.itemAt(i).layout() if l.itemAt(i) is not None else None
            if sub is not None:
                layouts.append(sub)
        if not isinstance(l, QVBoxLayout) or l.direction() != QBoxLayout.TopToBottom or l.property("raster_nein"):
            continue
        i = 0
        while i < l.count():
            if not kurz(l.itemAt(i)):
                i += 1
                continue
            j = i
            while j < l.count() and kurz(l.itemAt(j)):
                j += 1
            if j - i >= 2:
                ws = [l.itemAt(k).widget() for k in range(i, j)]
                breit = max(w.sizeHint().width() for w in ws)
                r = KartenRaster(min_breite=max(breit, 90), abstand=6)
                for w in ws:
                    l.removeWidget(w)
                for w in ws:
                    r.addWidget(w)
                l.insertLayout(i, r)
                n += 1
                i += 1
            else:
                i = j
    return n
