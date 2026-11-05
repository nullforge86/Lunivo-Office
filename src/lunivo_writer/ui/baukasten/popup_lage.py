"""Popup-Lage: das eine Öffnungsverhalten für alle aufklappenden Fenster (Menüs, Klapplisten, Popup-Fenster).

Ein Filter an der Anwendung greift bei jedem Fenster vom Typ ``Qt.Popup`` (``QMenu``, die Liste eines ``Auswahlfeld``, eigene
Popup-Widgets) und rückt es so, dass es nie über den Rand des Programmfensters und nie über den Rand des Bildschirms ragt.
Einzelne Stellen müssen nichts tun. Passt ein Popup nicht ins Programmfenster (kleiner Dialog), gilt der Bildschirm als Grenze.
Unter Wayland kann die Plattform das Verschieben von Popups ignorieren.
"""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, Qt, QTimer
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication, QWidget


def popup_klemmen(pop: QWidget, anker: QWidget | None = None) -> bool:
    """Schiebt ``pop`` in den erlaubten Bereich (Fenster des Ankers ∩ Bildschirm). True, wenn es verschoben wurde."""
    mitte = pop.frameGeometry().center()
    schirm = QGuiApplication.screenAt(mitte) or pop.screen() or QGuiApplication.primaryScreen()
    bs = schirm.availableGeometry() if schirm else QRect(0, 0, 100000, 100000)
    if anker is None and pop.parentWidget() is not None:
        anker = pop.parentWidget().window()                         # das Fenster, zu dem das Popup gehört
    fenster = anker if anker is not None else QApplication.activeWindow()
    if fenster is not None and fenster is not pop and fenster.isVisible():
        fr = QRect(fenster.mapToGlobal(QPoint(0, 0)), fenster.size())
        grenze = fr.intersected(bs) if fr.intersects(bs) else bs
    else:
        grenze = bs
    g = pop.frameGeometry()
    if g.width() > bs.width():
        pop.setMaximumWidth(bs.width()); g = pop.frameGeometry()
    region = grenze if g.width() <= grenze.width() else bs          # breiter als das Fenster: der Bildschirm ist die Grenze
    x = max(region.left(), min(g.left(), region.right() - g.width() + 1))
    y = max(bs.top(), min(g.top(), bs.bottom() - g.height() + 1))
    if (x, y) == (g.left(), g.top()):
        return False
    pop.move(pop.x() + x - g.left(), pop.y() + y - g.top())
    return True


class PopupWaechter(QObject):
    """Wird einmal an der Anwendung eingehängt (``einhaengen``) und klemmt jedes aufklappende Fenster beim Öffnen."""

    @staticmethod
    def einhaengen(app: QApplication) -> "PopupWaechter":
        w = PopupWaechter(app)
        app.installEventFilter(w)
        app._popup_waechter = w
        return w

    def eventFilter(self, obj, ev) -> bool:
        if ev.type() == QEvent.Type.Show and isinstance(obj, QWidget) and obj.isWindow() and obj.windowType() == Qt.WindowType.Popup:
            popup_klemmen(obj)
            QTimer.singleShot(0, lambda o=obj: popup_klemmen(o) if o.isVisible() else None)       # nach dem endgültigen Platzieren durch Qt noch einmal
        return False
