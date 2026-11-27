"""Lineal h: aus ``vcl.qt.widgets.dokumentansicht.ansicht.lineal`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QPolygonF
from writer.werte import px_zu_mm as px_to_mm, px_je_mm
from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import ABDUNKELUNG
from vcl.qt.widgets.bausteine.abstaende import LINEAL_MARKE_RAND, LINEAL_MARKE_SPITZE
from vcl.qt.widgets.dokumentansicht.ansicht.lineal_hilfen import HOEHE, _Lineal
from vcl.qt.widgets.dokumentansicht.ansicht.lineal_tabs import LinealTabs


FANG = 6            # so nahe (Bildpunkte) muss die Maus an einer Marke sein


AKZENT = QColor(Farbe.AKZENT_DUNKEL)


class LinealH(LinealTabs, _Lineal):
    randGeaendert = Signal(str, float)             # "links"|"rechts", neuer Rand in mm
    einzugGeaendert = Signal(float, float, float)  # links, rechts, erste Zeile (mm)
    tabsGeaendert = Signal(list)                   # Tabstopps des Absatzes: [(mm ab der linken Textkante, Ausrichtung, Füllzeichen), …]

    def _einzuege(self):
        from writer.anbindung.formatwerte import einzuege
        links, rechts, erste = einzuege(self.e.absatzformat())
        return px_to_mm(links), px_to_mm(rechts), px_to_mm(erste)

    def _x0(self) -> float:
        """x des linken Blattrandes im Lineal."""
        return self._versatz().x() + self.e.ansicht.blatt(0).left()

    def _marken(self):
        """Name → x-Position (Bildpunkte) der ziehbaren Marken."""
        pg = self.e.page
        l, r, f = self._einzuege()
        if self._zieh and self._wert is not None:
            n, w = self._zieh, self._wert
            if n == "links": pg = pg.copy(); pg.margin_left_mm = w
            if n == "rechts": pg = pg.copy(); pg.margin_right_mm = w
            if n == "einzug_links": l = w
            if n == "einzug_rechts": r = w
            if n == "einzug_erste": f = w
        x = self._x0()
        a, b = x + self.px(pg.margin_left_mm), x + self.px(pg.width_mm - pg.margin_right_mm)
        return {"links": a, "rechts": b, "einzug_erste": a + self.px(l + f), "einzug_links": a + self.px(l),
                "einzug_rechts": b - self.px(r), "blatt_links": x, "blatt_rechts": x + self.px(pg.width_mm), "pg": pg}

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = self.farben()
        m = self._marken()
        pg = m["pg"]
        self.koerper_zeichnen(p, QRectF(m["blatt_links"], 0, m["blatt_rechts"] - m["blatt_links"], HOEHE),          # nur über die Breite des Blatts
                              QRectF(m["links"], 0, m["rechts"] - m["links"], HOEHE), c)
        self._schrift(p)
        zahl, ticks = self.stifte(c)
        z = self.e.zoom
        feiner = px_je_mm() * z >= 2.4                                       # jeder Millimeter nur, wenn er sich noch trennen lässt
        k0, k1 = -int(pg.margin_left_mm), int(pg.width_mm - pg.margin_left_mm)
        for k in range(k0, k1 + 1):                                        # k = Millimeter von der linken Textkante
            x = m["links"] + self.px(k)
            if k % 10 == 0:
                p.setPen(QPen(ticks, 1)); p.drawLine(QPointF(x, HOEHE - 8), QPointF(x, HOEHE - 2))
                if k:
                    p.setPen(zahl)
                    p.drawText(QRectF(x - 14, 2, 28, 13), Qt.AlignCenter, str(abs(k) // 10))
            elif k % 5 == 0:
                p.setPen(QPen(ticks, 1)); p.drawLine(QPointF(x, HOEHE - 6), QPointF(x, HOEHE - 2))
            elif feiner:
                p.setPen(QPen(ticks, 1)); p.drawLine(QPointF(x, HOEHE - 4), QPointF(x, HOEHE - 2))
        # Marken: erste Zeile (Dreieck nach unten, oben), linker und rechter Einzug (Dreiecke nach oben, unten)
        p.setPen(QPen(QColor(*ABDUNKELUNG), 1)); p.setBrush(AKZENT)
        x = m["einzug_erste"]
        p.drawPolygon(QPolygonF([QPointF(x - 5, 1.5), QPointF(x + 5, 1.5), QPointF(x, 8.5)]))
        for n in ("einzug_links", "einzug_rechts"):
            x = m[n]
            p.drawPolygon(QPolygonF([QPointF(x - 5, HOEHE - 1.5), QPointF(x + 5, HOEHE - 1.5), QPointF(x, HOEHE - 8.5)]))
        self.tabs_zeichnen(p, m, c)
        p.end()

    def _treffer(self, x, y):
        """Die Marke unter der Maus. Die Dreiecke greifen nur in ihrer eigenen Höhe (oben die erste Zeile, unten die Einzüge); das Band
        dazwischen gehört den Seitenrändern – sonst verdecken die Dreiecke, die ohne Einzug genau auf dem Rand sitzen, die Randgrenze."""
        m = self._marken()
        dreieck = LINEAL_MARKE_RAND + LINEAL_MARKE_SPITZE
        if y <= dreieck and abs(x - m["einzug_erste"]) <= FANG:
            return "einzug_erste"
        if y >= HOEHE - dreieck:
            for n in ("einzug_links", "einzug_rechts"):
                if abs(x - m[n]) <= FANG:
                    return n
        mitte = dreieck < y < HOEHE - dreieck
        for n in ("links", "rechts"):
            if abs(x - m[n]) <= (FANG if mitte else 2.5):
                return n
        return None

    def mouseMoveEvent(self, ev):
        if self._tab_zieh is not None:
            self.tab_ziehen(ev.position().x(), ev.position().y(), self._marken())
            return
        self.setToolTip(self.tab_hinweis(ev.position().x(), ev.position().y()))
        if self._zieh:
            self._wert = self._mm(ev.position().x(), self._zieh)
            self.hilfslinie.zeigen(self._marken()[self._zieh])       # die Stelle der gezogenen Marke quer über das Dokument
            self.update()
            return
        self.setCursor(Qt.SizeHorCursor if self._treffer(ev.position().x(), ev.position().y()) else Qt.ArrowCursor)

    def _mm(self, x, name):
        pg = self.e.page
        mm = (x - self._x0()) / (px_je_mm() * self.e.zoom)
        l0 = pg.margin_left_mm
        r0 = pg.width_mm - pg.margin_right_mm
        if name == "links":
            return max(0.0, min(mm, r0 - 30))
        if name == "rechts":
            return max(0.0, min(pg.width_mm - mm, pg.width_mm - l0 - 30))
        if name == "einzug_links":
            return max(0.0, mm - l0)
        if name == "einzug_rechts":
            return max(0.0, r0 - mm)
        l, _r, _f = self._einzuege()
        return mm - l0 - l                  # erste Zeile relativ zum linken Einzug

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._zieh = self._treffer(ev.position().x(), ev.position().y())
            self._wert = None
            if self._zieh:
                self.hilfslinie.zeigen(self._marken()[self._zieh])
            else:                                              # keine Rand- oder Einzugsmarke: Wahlfeld, vorhandener oder neuer Tabstopp
                self.tab_druecken(ev.position().x(), ev.position().y(), self._marken())

    def mouseReleaseEvent(self, ev):
        if self._tab_zieh is not None:
            self.tabsGeaendert.emit(self.tab_loslassen())
            return
        n, w = self._zieh, self._wert
        self._zieh = self._wert = None
        self.hilfslinie.weg()
        if n and w is not None:
            if n in ("links", "rechts"):
                self.randGeaendert.emit(n, round(w, 1))
            else:
                l, r, f = self._einzuege()
                if n == "einzug_links": l = w
                if n == "einzug_rechts": r = w
                if n == "einzug_erste": f = w
                self.einzugGeaendert.emit(round(l, 1), round(r, 1), round(f, 1))
        self.update()
