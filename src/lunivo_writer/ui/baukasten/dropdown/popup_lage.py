"""Popup-Lage: das eine Öffnungsverhalten für alle aufklappenden Fenster (Menüs, Klapplisten, Popup-Fenster).

Die Basisklasse ``PopupVerhalten`` (geerbt von ``MenueListe`` und damit von allen Menüs, Galerien und Paletten, sowie von den Popup-Widgets) rückt jedes aufklappende Fenster nach den Regeln in ``popup_klemmen`` in den Bereich seines Ankers (Seitenleiste oder Programmfenster) und in den Bildschirm, jeweils mit Randabstand.
Einzelne Stellen müssen nichts tun. Passt ein Popup nicht ins Programmfenster (kleiner Dialog), gilt der Bildschirm als Grenze.
Unter Wayland kann die Plattform das Verschieben von Popups ignorieren.
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget

from lunivo_writer.ui.baukasten.basis.mass import DROPDOWN_BREITE_MIN, POPUP_RAND


GRENZE = "popupGrenze"      # Eigenschaft eines Widgets: „Popups, die von hier aus aufklappen, bleiben innerhalb von mir“ (z. B. die Seitenleiste)


def popup_bereich(anker: QWidget | None, schirm_geometrie: QRect) -> QRect:
    """Der Bereich, in dem ein von ``anker`` aufklappendes Fenster liegen darf: nächste Grenze oberhalb des Ankers (Eigenschaft
    ``popupGrenze``, sonst das Programmfenster) ∩ Bildschirm, innen verkleinert um ``POPUP_RAND``."""
    grenze = anker
    while grenze is not None and not grenze.property(GRENZE):
        grenze = grenze.parentWidget()
    if grenze is None and anker is not None:
        grenze = anker.window()
    bereich = schirm_geometrie
    if grenze is not None and grenze.isVisible():
        fr = QRect(grenze.mapToGlobal(QPoint(0, 0)), grenze.size())
        if fr.intersects(schirm_geometrie):
            bereich = fr.intersected(schirm_geometrie)
    return bereich.adjusted(POPUP_RAND, POPUP_RAND, -POPUP_RAND, -POPUP_RAND)


def popup_klemmen(pop: QWidget, anker: QWidget | None = None) -> bool:
    """Die Öffnungsregeln für jedes aufklappende Fenster. True, wenn es verschoben wurde.
    1. Es liegt ganz im Bereich des Ankers (Seitenleiste oder Fenster) und hat ``POPUP_RAND`` Abstand zu dessen Rand.
    2. Es ist nie breiter als dieser Bereich; passt es dort nicht hinein, gilt der Bildschirm (mit Abstand) als Bereich.
    3. Senkrecht gilt immer der Bildschirm (mit Abstand)."""
    mitte = pop.frameGeometry().center()
    schirm = QGuiApplication.screenAt(mitte) or pop.screen() or QGuiApplication.primaryScreen()
    bs = (schirm.availableGeometry() if schirm else QRect(0, 0, 100000, 100000)).adjusted(POPUP_RAND, POPUP_RAND, -POPUP_RAND, -POPUP_RAND)
    if anker is None:
        anker = pop.parentWidget() or QApplication.activeWindow()
    bereich = popup_bereich(anker, bs.adjusted(-POPUP_RAND, -POPUP_RAND, POPUP_RAND, POPUP_RAND))
    g = pop.frameGeometry()
    if g.width() > bs.width():
        pop.setMaximumWidth(bs.width()); g = pop.frameGeometry()
    region = bereich if g.width() <= bereich.width() else bs
    x = max(region.left(), min(g.left(), region.right() - g.width() + 1))
    y = max(bs.top(), min(g.top(), bs.bottom() - g.height() + 1))
    if (x, y) == (g.left(), g.top()):
        return False
    pop.move(pop.x() + x - g.left(), pop.y() + y - g.top())
    return True


class PopupVerhalten:
    """Basis aller aufklappenden Fenster (Menüs, Galerien, Popup-Widgets): Wer von ihr erbt, öffnet sich nach denselben Regeln.
    Reihenfolge der Basisklassen: ``class MeinMenue(PopupVerhalten, QMenu)``. Die Regeln selbst stehen in ``popup_klemmen``,
    die Maße in ``mass.py`` (``POPUP_RAND``, ``DROPDOWN_BREITE_MIN``)."""

    def showEvent(self, ev) -> None:
        self.setMinimumWidth(max(self.minimumWidth(), DROPDOWN_BREITE_MIN))        # alle gleich breit, nie schmaler als die Mindestbreite
        super().showEvent(ev)
        popup_klemmen(self)
        QTimer.singleShot(0, lambda o=self: popup_klemmen(o) if o.isVisible() else None)     # nach dem endgültigen Platzieren durch Qt noch einmal
