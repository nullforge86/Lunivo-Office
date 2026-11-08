"""Zwei-Seiten-Ansicht: die Seiten des Dokuments nebeneinander, so wie sie gedruckt werden (nur zum Ansehen)."""
from __future__ import annotations

from lunivo_writer.core.farben import Farbe
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QWidget

from lunivo_writer.models.page import mm_to_px
from lunivo_writer.editor.seite.pagination import seiten_bilder
from lunivo_writer.ui.baukasten.controls.formular_gitter import tabellen_gitter
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_SEITENBILDER, RAND_SEITENBILDER


class SeitenAnsicht(QWidget):
    def __init__(self, editor, breite: int):
        super().__init__()
        self.setBackgroundRole(self.backgroundRole().Dark)
        self.setAutoFillBackground(True)
        lay = tabellen_gitter(self, rand=RAND_SEITENBILDER, waagerecht=ABSTAND_SEITENBILDER, senkrecht=ABSTAND_SEITENBILDER)       # Seitenbilder: zwei je Zeile, rechts/links angelehnt
        pg = editor.page
        faktor = max(0.25, min(1.2, (breite - 16 * 4) / 2 / mm_to_px(pg.width_mm)))
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.seiten = 0
            for n, bild, _ps in seiten_bilder(editor.document(), pg, editor.noten, faktor):
                self.seiten = n
                lab = QLabel()
                lab.setPixmap(QPixmap.fromImage(bild))
                lab.setFixedSize(bild.size())
                lab.setStyleSheet(f"border: 1px solid {Farbe.GRAU};")
                lay.addWidget(lab, (n - 1) // 2, (n - 1) % 2, Qt.AlignTop | (Qt.AlignRight if n % 2 else Qt.AlignLeft))
        finally:
            QApplication.restoreOverrideCursor()
        lay.setRowStretch(lay.rowCount(), 1)
        lay.setColumnStretch(0, 1); lay.setColumnStretch(1, 1)
