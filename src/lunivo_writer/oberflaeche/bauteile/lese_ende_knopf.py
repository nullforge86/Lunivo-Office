"""Großer Knopf „Lesemodus beenden“, der im Lesemodus oben mittig über dem Fenster schwebt (Band und Seitenleiste sind dann ausgeblendet)."""
from __future__ import annotations

from PySide6.QtCore import QEvent, QObject, Qt
from PySide6.QtWidgets import QPushButton
from lunivo_writer.kern.farben import Farbe
from lunivo_writer.oberflaeche.baukasten.basis.mass import GROESSE_LESEENDEKNOPF, PADDING_LESEENDEKNOPF, RADIUS_KARTE, SCHRIFT_LESEENDEKNOPF


class LeseEndeKnopf(QPushButton):
    OBEN = 14

    def __init__(self, fenster, aktion):
        super().__init__("Lesemodus beenden", fenster)
        self.fenster = fenster
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(*GROESSE_LESEENDEKNOPF)
        self.setToolTip("Zurück zum Bearbeiten (Strg+Umschalt+L)"); self.setAccessibleName("Lesemodus beenden")
        self.setStyleSheet("QPushButton { background: palette(highlight); color: palette(highlighted-text); border: 2px solid palette(window-text); "
                           "border-radius: " f"{RADIUS_KARTE}" "px; padding: " f"{PADDING_LESEENDEKNOPF}" "; font-size: " f"{SCHRIFT_LESEENDEKNOPF}" "pt; font-weight: bold; }"
                           "QPushButton:hover { background: palette(link); color: %s; }" % Farbe.SCHWARZ)
        self.clicked.connect(lambda: aktion())
        fenster.installEventFilter(self)
        self.hide()

    def zeigen(self, sichtbar: bool) -> None:
        self.setVisible(sichtbar)
        if sichtbar:
            self.platzieren()

    def platzieren(self) -> None:
        self.adjustSize()
        self.move((self.fenster.width() - self.width()) // 2, self.OBEN)
        self.raise_()

    def eventFilter(self, obj: QObject, e: QEvent) -> bool:
        if self.isVisible() and e.type() == QEvent.Resize:
            self.platzieren()
        return False
