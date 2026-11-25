"""Ueberlauf leiste: aus ``vcl.qt.widgets.bausteine.interaktion.felder.flache_reiter_leiste`` herausgelöst."""
from __future__ import annotations
from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QTabBar
from vcl.qt.widgets.bausteine.abstaende.mass import BREITE_KNOPF_KLEIN, HOEHE_BANDREITER_KNOPF
from vcl.qt.widgets.bausteine.interaktion.felder.flache_reiter_leiste_hilfen import ReiterUeberlauf


_MEHR = BREITE_KNOPF_KLEIN     # Breite des Knopfes „•••“ (Überlaufmenü der ``UeberlaufLeiste``)


class UeberlaufLeiste(ReiterUeberlauf, QTabBar):
    """Gewöhnliche Reiterleiste (Band, Dokumente, Register) nach derselben Regel wie ``FlacheReiterLeiste``: keine Rollpfeile, kein angeschnittener Reiter.

    Zu wenig Platz: so viele Reiter wie ganz passen (der aktive immer), der Rest steht hinter dem Knopf „•••“. ``setTabVisible``/``isTabVisible`` behalten ihren Sinn
    (gewollte Sichtbarkeit, z. B. Kontext-Reiter); ``gezeigt(i)`` sagt, ob der Reiter wirklich in der Leiste steht. ``platz`` (optional) liefert die verfügbare Breite,
    wenn die Leiste nicht den ganzen Platz bekommt (Standard: ihre eigene Breite).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._will: list[bool] = []
        self._im_verteilen = False
        self.platz = None
        self.setUsesScrollButtons(False); self.setElideMode(Qt.ElideNone); self.setExpanding(False)       # Reiter in natürlicher Breite: die Summe stimmt mit der Rechnung überein
        self._mehr_einrichten()
        self.currentChanged.connect(lambda _i: self.neu_verteilen())
        self.tabMoved.connect(self._verschoben)

    # ---- gewollte Sichtbarkeit -------------------------------------------------------------------------------------------------
    def setTabVisible(self, index: int, sichtbar: bool) -> None:
        if 0 <= index < len(self._will):
            self._will[index] = sichtbar
        self.neu_verteilen()

    def isTabVisible(self, index: int) -> bool:
        return self._will[index] if 0 <= index < len(self._will) else QTabBar.isTabVisible(self, index)

    def gezeigt(self, index: int) -> bool:
        return QTabBar.isTabVisible(self, index)

    def tabInserted(self, index: int) -> None:
        self._will.insert(index, True)
        super().tabInserted(index)

    def tabRemoved(self, index: int) -> None:
        if 0 <= index < len(self._will):
            self._will.pop(index)
        super().tabRemoved(index)
        self.neu_verteilen()

    def _verschoben(self, von: int, nach: int) -> None:
        if 0 <= von < len(self._will) and 0 <= nach < len(self._will):
            self._will.insert(nach, self._will.pop(von))

    # ---- Überlauf --------------------------------------------------------------------------------------------------------------
    def _verfuegbar(self) -> int:
        return int(self.platz()) if self.platz else self.width()

    def _versteckte(self) -> list[int]:
        return [i for i in range(min(self.count(), len(self._will))) if self._will[i] and not QTabBar.isTabVisible(self, i)]      # Qt fragt die Größe, bevor ``tabInserted`` den Reiter eingetragen hat

    def _sichtbare_waehlen(self, wollen: list[int], gesamt: int) -> set[int]:
        """Welche Reiter bei der verfügbaren Breite sichtbar bleiben (der aktive immer)."""
        breite = {i: self.tabSizeHint(i).width() for i in wollen}
        if sum(breite.values()) <= gesamt:
            return set(wollen)
        frei, summe, zeige_l = gesamt - _MEHR, 0, []
        for i in wollen:
            if summe + breite[i] > frei:
                break
            zeige_l.append(i); summe += breite[i]
        aktiv = self.currentIndex()
        if aktiv in breite and aktiv not in zeige_l:
            while zeige_l and summe + breite[aktiv] > frei:
                summe -= breite[zeige_l.pop()]
            zeige_l.append(aktiv)
        return set(zeige_l)

    def _sichtbarkeit_setzen(self, zeige: set[int]) -> None:
        if any(QTabBar.isTabVisible(self, i) != (i in zeige) for i in range(self.count())):
            for i in range(self.count()):
                QTabBar.setTabVisible(self, i, i in zeige)
            self.setUsesScrollButtons(True); self.setUsesScrollButtons(False)       # setzt den alten Rollversatz von Qt zurück (sonst steht der erste Reiter angeschnitten)

    def _mehr_knopf_setzen(self) -> None:
        mehr = bool(self._versteckte())
        self._mehr.setVisible(mehr)
        if mehr:
            letzte = max((self.tabRect(i).right() for i in range(self.count()) if QTabBar.isTabVisible(self, i)), default=0)
            self._mehr.setGeometry(min(letzte + 1, max(0, self.width() - _MEHR)), 0, _MEHR, max(HOEHE_BANDREITER_KNOPF, self.height()))
            self._mehr.raise_()

    def neu_verteilen(self) -> None:
        if self._im_verteilen or len(self._will) != self.count():
            return
        gesamt = self._verfuegbar()
        wollen = [i for i in range(self.count()) if self._will[i]]
        if gesamt < 2 * _MEHR or not wollen:
            return
        self._im_verteilen = True
        try:
            self._sichtbarkeit_setzen(self._sichtbare_waehlen(wollen, gesamt))
            self._mehr_knopf_setzen()
        finally:
            self._im_verteilen = False
        self.updateGeometry()

    def sizeHint(self) -> QSize:
        sh = super().sizeHint()
        return QSize(sh.width() + (_MEHR if self._versteckte() else 0), sh.height())

    def minimumSizeHint(self) -> QSize:
        return QSize(2 * _MEHR, super().sizeHint().height())

    def resizeEvent(self, e) -> None:
        super().resizeEvent(e)
        self.neu_verteilen()

    def tabLayoutChange(self) -> None:
        super().tabLayoutChange()
        if not self._im_verteilen:
            self.neu_verteilen()
