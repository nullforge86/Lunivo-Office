"""Flache reiter leiste hilfen: aus ``vcl.qt.widgets.bausteine.interaktion.felder.flache_reiter_leiste`` herausgelöst."""
from __future__ import annotations
from vcl.qt.widgets.bausteine.interaktion.knopf.knopf import werkzeugknopf
from PySide6.QtCore import QPoint, Qt


MEHR_TEXT = "•••"                 # Beschriftung des Überlaufknopfs aller Reiterleisten (an einer Stelle)


MEHR_TIPP = "Weitere Reiter"      # Tooltip und Name des Überlaufknopfs


class ReiterUeberlauf:
    """Basis der Reiterleisten mit Knopf „•••“ (Band, Dokumente, Register: ``UeberlaufLeiste``) und Menü der Reiter, die nicht mehr in die Leiste passen.
    Reihenfolge: ``class X(ReiterUeberlauf, QTabBar)``. Die Leiste liefert ``_versteckte()`` (Indizes der ausgelagerten Reiter) und setzt den Knopf selbst.
    Die flachen Leisten der Fenster nutzen stattdessen ``ReiterDropdown``."""

    def _mehr_einrichten(self) -> None:
        self._mehr = werkzeugknopf("standard", flach=False, eltern=self)
        self._mehr.setText(MEHR_TEXT); self._mehr.setAutoRaise(True); self._mehr.setCursor(Qt.PointingHandCursor)
        self._mehr.setToolTip(MEHR_TIPP); self._mehr.setAccessibleName(MEHR_TIPP)
        self._mehr.clicked.connect(self._mehr_menue); self._mehr.hide()

    def _mehr_menue(self) -> None:
        from vcl.qt.widgets.menues.dropdown.menue_liste import MenueListe
        m = MenueListe(self)
        for i in self._versteckte():
            m.eintrag(self.tabText(i), lambda i=i: self.setCurrentIndex(i), aktiv=self.isTabEnabled(i))
        m.exec(self.mapToGlobal(QPoint(max(0, self._mehr.x() + self._mehr.width() - m.sizeHint().width()), self.height())))
