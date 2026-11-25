"""Lineal v: aus ``vcl.qt.widgets.dokumentansicht.ansicht.lineal`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from writer.werte import px_je_mm
from vcl.qt.widgets.dokumentansicht.ansicht.lineal_hilfen import HOEHE, _Lineal


class LinealV(_Lineal):
    randGeaendert = Signal(str, float)            # "oben"|"unten"

    def _blatt(self) -> int:
        """Nummer des Blattes, in dem die Schreibmarke steht — das Lineal richtet sich nach diesem Blatt."""
        e = self.e
        schritt = e.blatt_oben(1) - e.blatt_oben(0)
        if schritt <= 0:
            return 0
        return max(0, int((e.cursorRect().center().y() - e.blatt_oben(0)) // schritt))

    def _o(self) -> float:
        """y des oberen Blattrandes des aktuellen Blattes im Lineal."""
        return self._versatz().y() + self.e.blatt_oben(self._blatt())

    def paintEvent(self, ev):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        c = self.farben()
        pg = self.e.page
        o = self._o()
        t = o + self.px(pg.margin_top_mm)
        if self._zieh == "oben" and self._wert is not None:
            t = o + self.px(self._wert)
        unten = o + self.px(pg.height_mm - pg.margin_bottom_mm)
        if self._zieh == "unten" and self._wert is not None:
            unten = o + self.px(pg.height_mm - self._wert)
        p.fillRect(self.rect(), c["aussen"])
        p.fillRect(QRectF(0, o, HOEHE, self.px(pg.height_mm)), c["grund"])
        p.fillRect(QRectF(0, t, HOEHE, unten - t), c["text"])
        rand = QColor(c["schrift"]); rand.setAlpha(60)
        p.setPen(QPen(rand, 1)); p.drawLine(HOEHE - 1, 0, HOEHE - 1, self.height())
        self._schrift(p)
        zahl, ticks = QColor(c["schrift"]), QColor(c["schrift"])
        zahl.setAlpha(225); ticks.setAlpha(170)
        feiner = px_je_mm() * self.e.zoom >= 2.4
        k0, k1 = -int(pg.margin_top_mm), int(pg.height_mm - pg.margin_top_mm)
        for k in range(k0, k1 + 1):                                        # k = Millimeter von der oberen Textkante
            y = t + self.px(k)
            if y < -12 or y > self.height() + 12:
                continue
            if k % 10 == 0:
                p.setPen(QPen(ticks, 1)); p.drawLine(QPointF(HOEHE - 8, y), QPointF(HOEHE - 2, y))
                if k:
                    p.setPen(zahl)
                    p.drawText(QRectF(0, y - 7, HOEHE - 9, 14), Qt.AlignRight | Qt.AlignVCenter, str(abs(k) // 10))
            elif k % 5 == 0:
                p.setPen(QPen(ticks, 1)); p.drawLine(QPointF(HOEHE - 6, y), QPointF(HOEHE - 2, y))
            elif feiner:
                p.setPen(QPen(ticks, 1)); p.drawLine(QPointF(HOEHE - 4, y), QPointF(HOEHE - 2, y))
        p.end()

    def _treffer(self, y):
        pg = self.e.page
        o = self._o()
        if abs(y - o - self.px(pg.margin_top_mm)) <= 3:
            return "oben"
        if abs(y - o - self.px(pg.height_mm - pg.margin_bottom_mm)) <= 3:
            return "unten"
        return None

    def mouseMoveEvent(self, ev):
        if self._zieh:
            pg = self.e.page
            mm = (ev.position().y() - self._o()) / (px_je_mm() * self.e.zoom)
            if self._zieh == "oben":
                self._wert = max(0.0, min(mm, pg.height_mm - pg.margin_bottom_mm - 40))
            else:
                self._wert = max(0.0, min(pg.height_mm - mm, pg.height_mm - pg.margin_top_mm - 40))
            self.update()
            return
        self.setCursor(Qt.SizeVerCursor if self._treffer(ev.position().y()) else Qt.ArrowCursor)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            self._zieh = self._treffer(ev.position().y())
            self._wert = None

    def mouseReleaseEvent(self, ev):
        n, w = self._zieh, self._wert
        self._zieh = self._wert = None
        if n and w is not None:
            self.randGeaendert.emit(n, round(w, 1))
        self.update()
