"""Angepasste reiter: aus ``vcl.qt.widgets.bausteine.interaktion.felder.formular_gitter`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QSize
from PySide6.QtWidgets import QTabWidget, QSizePolicy, QWidget
from vcl.qt.widgets.bausteine.abstaende.mass import ABSTAND_UNTER_REITER


class AngepassteReiter(QTabWidget):
    """Reiter, deren Höhe dem gewählten Reiter folgt (ein ``QTabWidget`` richtet sich sonst nach dem höchsten und lässt kürzeren Reitern leeren Platz)."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        from vcl.qt.widgets.bausteine.interaktion.felder.flache_reiter_leiste import HAUPT, FlacheReiterLeiste
        self.setTabBar(FlacheReiterLeiste(HAUPT))          # EINE Reiterleiste für alle Fenster: flach, die Beschriftung bricht um, nichts wird abgeschnitten
        self.currentChanged.connect(self._aktuelle_seite)
        self.setUsesScrollButtons(False)

    def _aktuelle_seite(self, _i: int = 0) -> None:
        """Nur die gewählte Seite bestimmt die Höhe: die anderen zählen für das Layout nicht mit (sonst bleibt unter kürzeren Reitern leerer Platz)."""
        for k in range(self.count()):
            w = self.widget(k)
            sp = w.sizePolicy()
            sp.setVerticalPolicy(QSizePolicy.Preferred if k == self.currentIndex() else QSizePolicy.Ignored)
            w.setSizePolicy(sp)
        self.updateGeometry()
        e = self.parentWidget()
        while e is not None:                                      # die Layouts darüber merken sich sonst die Höhe des vorigen Reiters
            if e.layout() is not None:
                e.layout().invalidate()
            e = e.parentWidget()

    def tabInserted(self, index: int) -> None:
        super().tabInserted(index)
        self._aktuelle_seite()
        self.tabBar().setTabToolTip(index, self.tabText(index))

    def _mass(self, minimum: bool) -> QSize:
        w = self.currentWidget()
        if w is None:
            return super().minimumSizeHint() if minimum else super().sizeHint()
        ws = w.minimumSizeHint() if minimum else w.sizeHint()
        h = max(ws.height(), w.minimumHeight())                                       # ein Reiter mit fester Höhe (zum Beispiel Kachelraster) gilt mit dieser
        if w.maximumHeight() < 16777215:
            h = min(h, w.maximumHeight())
        ws = QSize(ws.width(), h)
        tb = self.tabBar().sizeHint()
        return QSize(ws.width() + 6, ws.height() + tb.height() + 8 + ABSTAND_UNTER_REITER)               # die Leiste kürzt ihre Namen, sie bestimmt die Breite nicht

    def hasHeightForWidth(self) -> bool:
        w = self.currentWidget()
        return w is not None and w.hasHeightForWidth()

    def heightForWidth(self, breite: int) -> int:
        """Die Höhe der gewählten Seite bei dieser Breite (Seiten aus ``FormularGitter`` brechen um): so bleibt unter kürzeren Reitern kein leerer Platz."""
        w = self.currentWidget()
        tb = self.tabBar().sizeHint()
        return w.heightForWidth(max(1, breite - 6)) + tb.height() + 8 + ABSTAND_UNTER_REITER

    def sizeHint(self) -> QSize:
        return self._mass(False)

    def minimumSizeHint(self) -> QSize:
        return self._mass(True)
