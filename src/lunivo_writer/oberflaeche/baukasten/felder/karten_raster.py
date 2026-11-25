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

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QGridLayout, QLayout, QLayoutItem, QWidget
from lunivo_writer.oberflaeche.baukasten.basis.raster import Anordnung, PlanRaster, RasterLinie
from lunivo_writer.oberflaeche.baukasten.felder.formular_gitter import tabellen_gitter
from lunivo_writer.oberflaeche.baukasten.basis.mass import RAND_KEIN

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


def _platzieren(spannen: list[tuple[int, int]], n: int) -> list[tuple[int, int, int, int]]:
    """Platzierung im Raster mit ``n`` Spalten → je Element (Zeile, Spalte, Spalten, Zeilen): der Reihe nach an die erste freie Stelle ab dem
    Zeiger (kein Umsortieren), die Spanne auf die vorhandene Spaltenzahl gekürzt."""
    belegt: set[tuple[int, int]] = set()
    stellen, zeiger = [], 0
    for c, r in spannen:
        c = min(c, n)
        while True:
            zl, sp = divmod(zeiger, n)
            if sp + c <= n and all((zl + dz, sp + dc) not in belegt for dz in range(r) for dc in range(c)):
                break
            zeiger += 1
        belegt.update((zl + dz, sp + dc) for dz in range(r) for dc in range(c))
        stellen.append((zl, sp, c, r))
        zeiger += c
    return stellen


def _zeilenhoehen(stellen: list[tuple[int, int, int, int]], noetig: list[int], a: int, gleich: bool, zmin: int = ZEILE_MIN) -> list[int]:
    """Höhe jeder Rasterzeile; ``noetig[i]`` = Höhe, die Element i für seinen Inhalt braucht. ``gleich``: eine gemeinsame Zeileneinheit, so
    hoch, dass jedes Element in seine Spanne passt. Sonst: jede Zeile so hoch wie ihr höchstes Element; Spannen über mehrere Zeilen bekommen
    den Fehlbetrag in der letzten Zeile."""
    zeilen = max((zl + r for zl, _sp, _c, r in stellen), default=0)
    if gleich:
        einheit = max([zmin] + [math.ceil((h - (r - 1) * a) / r) for (_zl, _sp, _c, r), h in zip(stellen, noetig)])
        return [einheit] * zeilen
    hoehen = [zmin] * zeilen
    for (zl, _sp, _c, r), h in zip(stellen, noetig):
        if r == 1:
            hoehen[zl] = max(hoehen[zl], h)
    for (zl, _sp, _c, r), h in zip(stellen, noetig):
        fehlt = h - (sum(hoehen[zl:zl + r]) + (r - 1) * a)
        if r > 1 and fehlt > 0:
            hoehen[zl + r - 1] += fehlt
    return hoehen


class KartenRaster(PlanRaster):
    """Karten im gemeinsamen Raster: ein ``QGridLayout`` mit so vielen gleich breiten Spalten, wie die Breite zulässt; jede Karte belegt ihre
    Spanne als Zellenbereich (``Zeile, Spalte, Zeilen, Spalten``). Ändert sich die Breite, werden die Zellen neu verteilt."""

    def __init__(self, parent: QWidget | None = None, min_breite: int = 132, abstand: int = 6, spalten_fest: int = 0, gleiche_hoehe: bool = True,
                 spanne_nach_inhalt: bool = False, zeile_min: int = ZEILE_MIN, hoechstens_anzahl: bool = False):
        """``spanne_nach_inhalt``: jedes Element belegt so viele Spalten, wie sein Inhalt braucht (Chips, Schlagwörter) — feine Spalten
        (``min_breite`` klein), alle Kanten auf denselben Spaltenlinien."""
        self._spannen: dict = {}
        self._nach_inhalt = spanne_nach_inhalt
        self._hoechstens = hoechstens_anzahl                                            # nie mehr Spalten als Elemente: wenige Karten nutzen die ganze Breite
        self._zmin = zeile_min                                                          # kleinste Zeilenhöhe (die Zeile wächst mit dem Inhalt)
        super().__init__(parent)
        self._min_b, self._abstand, self._fest = min_breite, abstand, spalten_fest      # spalten_fest > 0: immer diese Spaltenzahl (1 = untereinander)
        self._gleich = gleiche_hoehe                                                    # False: jede Rasterzeile so hoch wie ihr höchstes Element (Zeilen mit natürlicher Höhe)
        self.setContentsMargins(*RAND_KEIN)

    # ---- Aufbau -----------------------------------------------------------------------------------------
    def addWidget(self, w: QWidget, spanne: object = None) -> None:                    # type: ignore[override]
        self.element_widget(w)
        self._spannen[w] = spanne_von(spanne if spanne is not None else w.property("raster_spanne"))
        self.invalidate()

    def _neu_aufnehmen(self, it: QLayoutItem) -> None:
        w = it.widget()
        self._spannen.setdefault(self._schluessel(it), spanne_von(w.property("raster_spanne") if w is not None else None))
        self.invalidate()

    def _vergessen(self, it: QLayoutItem) -> None:
        self._spannen.pop(self._schluessel(it), None)

    def setSpanne(self, w: QWidget, spanne: object) -> None:
        if w in self._spannen:
            self._spannen[w] = spanne_von(spanne)
        self.invalidate()

    # ---- Maße -------------------------------------------------------------------------------------------
    def spalten(self, breite: int) -> int:
        if self._fest:
            return self._fest
        a = self._abstand
        n = max(1, (max(breite, 1) + a) // (self._min_b + a))
        return max(1, min(n, len(self._sichtbar()))) if self._hoechstens else n

    def _sichtbar(self) -> list[QLayoutItem]:
        return [i for i in self.elemente() if i.widget() is None or not i.widget().isHidden()]

    def _anordnung(self, breite: int) -> Anordnung:
        """Zellen bei der Breite ``breite``: Spaltenzahl aus der Breite, Platzierung der Reihe nach, Zeilenhöhen aus dem Inhalt."""
        items = self._sichtbar()
        n, a = self.spalten(breite), self._abstand
        zb = max(1, (breite - a * (n - 1)) // n)                                       # Zellenbreite
        stellen = _platzieren([self._spanne(it, n, zb, a) for it in items], n)

        def noetig(it, c):
            bw = c * zb + (c - 1) * a
            hfw = it.heightForWidth(bw) if it.hasHeightForWidth() else it.sizeHint().height()
            return max(hfw, it.minimumSize().height())
        hoehen = _zeilenhoehen(stellen, [noetig(it, c) for it, (_zl, _sp, c, _r) in zip(items, stellen)], a, self._gleich, self._zmin)
        an = Anordnung(waagerecht=a, senkrecht=a, hoehe=(sum(hoehen) + (len(hoehen) - 1) * a if hoehen else 0))
        an.zellen = [(it, zl, sp, r, c, None) for it, (zl, sp, c, r) in zip(items, stellen)]
        an.spalten = {k: zb for k in range(n)}
        an.spalten_dehnung = {k: 1 for k in range(n)}
        an.zeilen = dict(enumerate(hoehen))
        return an

    def setGeometry(self, r) -> None:
        """Das Gitter bekommt genau die Breite der gleich breiten Zellen (der Rundungsrest bleibt rechts frei): gleiche Spanne = gleiche Größe."""
        m = self.contentsMargins()
        innen = max(1, r.width() - m.left() - m.right())
        n, a = self.spalten(innen), self._abstand
        zb = max(1, (innen - a * (n - 1)) // n)
        r = type(r)(r); r.setWidth(min(r.width(), n * zb + (n - 1) * a + m.left() + m.right()))
        super().setGeometry(r)

    def _spanne(self, it: QLayoutItem, n: int, zb: int, a: int) -> tuple[int, int]:
        """Spanne eines Elements; mit ``spanne_nach_inhalt`` aus seiner natürlichen Breite bei der aktuellen Zellenbreite."""
        if not self._nach_inhalt:
            return self._spannen.get(self._schluessel(it), SPANNE_STANDARD)
        nat = max(it.sizeHint().width(), it.minimumSize().width())
        return min(n, max(1, math.ceil((nat + a) / (zb + a)))), 1

    def sizeHint(self) -> QSize:
        m = self.contentsMargins()
        return QSize(self._min_b + m.left() + m.right(), self.heightForWidth(self._min_b + m.left() + m.right()) if self.count() else 0)

    def minimumSize(self) -> QSize:
        m = self.contentsMargins()
        return QSize(60 + m.left() + m.right(), m.top() + m.bottom())


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


def _ist_kurz(it, max_breite: int) -> bool:
    """Ein sichtbares kurzes Ankreuzfeld, Optionsfeld oder ein kurzer Knopf, der ins Raster darf."""
    w = it.widget() if it is not None else None
    return (w is not None and not w.isHidden() and any(c.__name__ in _KURZ for c in type(w).__mro__)
            and (w.natuerliche_breite() if hasattr(w, "natuerliche_breite") else w.sizeHint().width()) <= max_breite
            and not w.property("raster_nein"))


def _alle_layouts(fenster: QWidget) -> list[QLayout]:
    """Jedes Layout des Fensters genau einmal, auch die verschachtelten."""
    offen = [x.layout() for x in [fenster] + fenster.findChildren(QWidget) if x.layout() is not None]
    gesehen: set[int] = set()
    aus = []
    while offen:
        l = offen.pop()
        if id(l) in gesehen:
            continue
        gesehen.add(id(l))
        aus.append(l)
        offen.extend(l.itemAt(i).layout() for i in range(l.count()) if l.itemAt(i) is not None and l.itemAt(i).layout() is not None)
    return aus


def _gruppe_ins_raster(l: QLayout, von: int, bis: int) -> None:
    """Die Elemente ``von`` bis ``bis`` (ausschließlich) des Layouts in ein ``KartenRaster`` an derselben Stelle legen."""
    ws = [l.itemAt(k).widget() for k in range(von, bis)]
    r = KartenRaster(min_breite=max(max(w.sizeHint().width() for w in ws), 90), abstand=6)
    for w in ws:
        l.removeWidget(w)
    for w in ws:
        r.addWidget(w)
    l.insertLayout(von, r)


def _gruppen_buendeln(l: QLayout, max_breite: int) -> int:
    """Jede Folge von mindestens zwei kurzen Elementen im Layout bündeln. → Zahl der Gruppen."""
    n = i = 0
    while i < l.count():
        j = i
        while j < l.count() and _ist_kurz(l.itemAt(j), max_breite):
            j += 1
        if j - i >= 2:
            _gruppe_ins_raster(l, i, j)
            n += 1
            i += 1
        else:
            i = max(j, i + 1)
    return n


def kurze_gruppen_ins_raster(fenster: QWidget, max_breite: int = 150) -> int:
    """Zentrale Automatik für jedes Fenster der Seitenleiste: aufeinanderfolgende kurze Ankreuzfelder, Optionsfelder und Knöpfe in einer senkrechten Rasterlinie
    (``RasterSpalte``) kommen in ein ``KartenRaster`` (alle ``1×1``) und stehen so nebeneinander, statt einzeln untereinander. Gibt die Zahl der Gruppen zurück."""
    n = 0
    for l in _alle_layouts(fenster):
        if isinstance(l, RasterLinie) and l.senkrecht() and not l.property("raster_nein"):
            n += _gruppen_buendeln(l, max_breite)
    return n