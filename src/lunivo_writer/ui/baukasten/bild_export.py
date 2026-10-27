"""„Als Bild exportieren“: das Fenster nach Kays Vorbild (WPS-Bildschirmfoto „Export Image“) und die Meldung danach.

Oben zwei Karten — **Jede Seite** (eine Datei je Seite) und **Langes Bild** (alle Seiten untereinander) —, darunter Wasserzeichen,
Qualität, Format und Zielordner, rechts unten **Exportieren**. Die Bildchen auf den Karten zeichnet ``QPainter``; geschrieben wird
in ``services/bild_export.py``.
"""
from __future__ import annotations

import os

from PySide6.QtCore import QPointF, QRectF, QSize, QStandardPaths, Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import (QAbstractButton, QButtonGroup, QComboBox, QDialog, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QPushButton, QVBoxLayout)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.services.bild_export import FORMATE, QUALITAET, BildWahl

STIL = ("QPushButton#beHaupt { background: " + Farbe.AKZENT + "; color: white; border: none; border-radius: 4px; padding: 8px 28px; }"
        "QPushButton#beHaupt:hover { background: " + Farbe.AKZENT_DUNKEL + "; }"
        "QLabel#beText { font-size: 11pt; }")
PUNKTE = "M5 12h.01 M12 12h.01 M19 12h.01"


class _Karte(QAbstractButton):
    """Eine wählbare Karte mit Bildchen und Beschriftung; gewählt mit blauem Rand und Haken in der Ecke."""

    def __init__(self, text: str, lang: bool):
        super().__init__()
        self.setText(text)
        self.lang = lang
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(260, 200)
        self.setAccessibleName(text)

    def sizeHint(self) -> QSize:
        return QSize(260, 200)

    def paintEvent(self, _e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        pal = self.palette()
        dunkel = pal.color(QPalette.Window).lightness() < 128
        grund = pal.color(QPalette.Base).darker(104 if not dunkel else 90)
        akzent = QColor(Farbe.AKZENT_DUNKEL if dunkel else Farbe.AKZENT)
        rahmen = akzent if self.isChecked() else pal.color(QPalette.Mid).lighter(125)
        r = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        p.fillRect(r, grund)
        p.setPen(QPen(rahmen, 2 if self.isChecked() else 1))
        p.drawRect(r)
        self._bildchen(p, dunkel)
        p.setPen(pal.color(QPalette.Text) if self.isChecked() else pal.color(QPalette.PlaceholderText))
        p.drawText(QRectF(0, r.bottom() - 34, r.width(), 24), Qt.AlignCenter, self.text())
        if self.isChecked():                                           # Haken in der Ecke rechts unten
            ecke = QPainterPath()
            ecke.moveTo(r.right(), r.bottom() - 36); ecke.lineTo(r.right(), r.bottom()); ecke.lineTo(r.right() - 36, r.bottom())
            ecke.closeSubpath()
            p.fillPath(ecke, akzent)
            p.setPen(QPen(QColor(Farbe.WEISS), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            p.drawPolyline([QPointF(r.right() - 17, r.bottom() - 9), QPointF(r.right() - 12, r.bottom() - 5),
                            QPointF(r.right() - 5, r.bottom() - 13)])

    def _bildchen(self, p: QPainter, dunkel: bool) -> None:
        blatt = QColor(Farbe.WEISS) if not dunkel else QColor("#3a3f45")
        linie = QColor(Farbe.GRAU_HELL)
        block = QColor(Farbe.AKZENT).lighter(170) if not dunkel else QColor(Farbe.AKZENT_DUNKEL).darker(130)
        p.setPen(QPen(QColor(Farbe.GRAU_HELL), 1))

        def seite(x: float, y: float, b: float, h: float, zeilen: int) -> None:
            p.setBrush(blatt)
            p.drawRoundedRect(QRectF(x, y, b, h), 3, 3)
            p.fillRect(QRectF(x + 7, y + 8, b * 0.18, b * 0.16), block)
            p.save(); p.setPen(QPen(linie, 1.4))
            p.drawLine(QPointF(x + 7 + b * 0.26, y + 12), QPointF(x + b - 8, y + 12))
            for k in range(zeilen):
                yy = y + 22 + k * ((h - 30) / max(1, zeilen))
                p.drawLine(QPointF(x + 7, yy), QPointF(x + b - 8, yy))
            p.restore()

        if not self.lang:
            for i, (x, y) in enumerate(((80, 28), (134, 28), (80, 92), (134, 92))):
                seite(x, y, 46, 56, 3)
        else:
            x, y, b, h = 88, 24, 82, 128
            p.setBrush(blatt)
            p.drawRoundedRect(QRectF(x, y, b, h), 3, 3)
            p.fillRect(QRectF(x + 10, y + 10, 20, 18), block)
            p.save(); p.setPen(QPen(linie, 1.4))
            for yy in (14, 22):
                p.drawLine(QPointF(x + 36, y + yy), QPointF(x + b - 10, y + yy))
            for yy in (38, 46, 62, 70, 78, 96, 104, 112):
                links = x + 30 if yy > 86 else x + 10                  # neben dem kleinen Bild unten links
                p.drawLine(QPointF(links, y + yy), QPointF(x + (b - 30 if 54 < yy < 86 else b - 10), y + yy))
            p.restore()
            p.fillRect(QRectF(x + b - 26, y + 54, 16, 24), QColor(Farbe.ORANGE).lighter(175) if not dunkel else QColor("#6b5442"))
            p.fillRect(QRectF(x + 10, y + 90, 14, 14), linie)


class BildExportFenster(QDialog):
    def __init__(self, parent, startordner: str = "", dpi: int = 150):
        super().__init__(parent)
        self.setWindowTitle("Als Bild exportieren")
        self.setStyleSheet(STIL)
        v = QVBoxLayout(self)
        v.setContentsMargins(36, 28, 36, 28)
        v.setSpacing(18)
        karten = QHBoxLayout(); karten.setSpacing(36)
        self.k_seite = _Karte("Jede Seite", False)
        self.k_lang = _Karte("Langes Bild", True)
        gruppe = QButtonGroup(self); gruppe.setExclusive(True)
        for k in (self.k_seite, self.k_lang):
            gruppe.addButton(k); karten.addWidget(k)
        karten.addStretch(1)
        self.k_seite.setChecked(True)
        v.addLayout(karten)

        g = QGridLayout(); g.setHorizontalSpacing(14); g.setVerticalSpacing(14)
        self.wasser = QLineEdit(); self.wasser.setPlaceholderText("Vertraulich, Nicht kopieren, Original, Muster …")
        self.wasser.setMinimumWidth(390)
        self.qualitaet = QComboBox()
        for name, wert in QUALITAET:
            self.qualitaet.addItem(f"{name} ({wert} dpi)", wert)
        if dpi not in [d for _n, d in QUALITAET]:                  # die Auflösung aus den Optionen steht dann zuoberst
            self.qualitaet.insertItem(0, f"Wie in den Optionen ({dpi} dpi)", dpi)
        self.qualitaet.setCurrentIndex(self.qualitaet.findData(dpi))
        self.format = QComboBox()
        for name in FORMATE:
            self.format.addItem(name)
        self.format.setCurrentText("PNG")
        for c in (self.qualitaet, self.format):
            c.setFixedWidth(220)
        self.ordner = QLineEdit(startordner or _bilder_ordner())
        from lunivo_writer.ui.widgets import icons
        waehlen = self.ordner.addAction(icons.icon_aus_pfad(PUNKTE, 18), QLineEdit.TrailingPosition)
        waehlen.setToolTip("Ordner wählen …")
        waehlen.triggered.connect(self._ordner_waehlen)
        self.k_export = QPushButton("Exportieren"); self.k_export.setObjectName("beHaupt"); self.k_export.setDefault(True)
        self.k_export.setCursor(Qt.PointingHandCursor); self.k_export.setMinimumWidth(120)
        self.k_export.clicked.connect(self._exportieren)
        for zeile, (text, feld) in enumerate((("&Wasserzeichen", self.wasser), ("&Qualität", self.qualitaet),
                                              ("&Format", self.format), ("Speichern &in", self.ordner))):
            l = QLabel(text); l.setBuddy(feld)
            g.addWidget(l, zeile, 0)
            g.addWidget(feld, zeile, 1, Qt.AlignLeft if feld in (self.qualitaet, self.format) else Qt.Alignment())
        for feld in (self.wasser, self.qualitaet, self.format, self.ordner, self.k_export):
            feld.setMinimumHeight(36)                                 # Felder in der Höhe des Vorbilds, nicht schmal
        g.addWidget(self.k_export, 3, 2)
        g.setColumnStretch(1, 1)
        g.setColumnMinimumWidth(2, 140)
        v.addLayout(g)
        self._wahl: BildWahl | None = None

    def _ordner_waehlen(self) -> None:
        from lunivo_writer.ui.baukasten.speichern_fenster import ordner_waehlen
        neu = ordner_waehlen(self, "Ordner für die Bilder", self.ordner.text() or _bilder_ordner())
        if neu:
            self.ordner.setText(neu)

    def _exportieren(self) -> None:
        ordner = os.path.expanduser(self.ordner.text().strip())
        if not os.path.isdir(ordner):
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, self.windowTitle(), f"Den Ordner „{ordner}“ gibt es nicht.")
            return
        self._wahl = BildWahl(lang=self.k_lang.isChecked(), wasserzeichen=self.wasser.text(), dpi=int(self.qualitaet.currentData()),
                              format=self.format.currentText(), ordner=ordner)
        self.accept()

    def wahl(self) -> BildWahl | None:
        return self._wahl


class ErfolgFenster(QDialog):
    """Nach dem Export: Datei öffnen oder Ordner zeigen."""

    def __init__(self, parent, dateien: list[str]):
        super().__init__(parent)
        self.setWindowTitle("Export erfolgreich")
        self.setStyleSheet(STIL)
        self.dateien = dateien
        v = QVBoxLayout(self); v.setContentsMargins(24, 20, 24, 20); v.setSpacing(14)
        kopf = QHBoxLayout()
        haken = QLabel(); haken.setFixedSize(28, 28); haken.setPixmap(_haken(28))
        titel = QLabel("Export erfolgreich"); titel.setObjectName("beText")
        kopf.addWidget(haken); kopf.addWidget(titel); kopf.addStretch(1)
        v.addLayout(kopf)
        n = len(dateien)
        text = QLabel(f"{n} Bild{'er' if n != 1 else ''} gespeichert. Öffnen Sie die Datei oder den Ordner, um es anzusehen."
                      if n == 1 else f"{n} Bilder gespeichert. Öffnen Sie die erste Datei oder den Ordner, um sie anzusehen.")
        text.setWordWrap(True)
        v.addWidget(text)
        v.addSpacing(16)
        knoepfe = QHBoxLayout(); knoepfe.addStretch(1)
        oeffnen = QPushButton("Ö&ffnen"); oeffnen.setObjectName("beHaupt"); oeffnen.setDefault(True)
        ordner = QPushButton("&Ordner öffnen")
        oeffnen.clicked.connect(lambda: (QDesktopServices.openUrl(QUrl.fromLocalFile(dateien[0])), self.accept()))
        ordner.clicked.connect(lambda: (QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(dateien[0]))), self.accept()))
        for k in (oeffnen, ordner):
            k.setMinimumWidth(130); k.setCursor(Qt.PointingHandCursor); knoepfe.addWidget(k)
        v.addLayout(knoepfe)
        self.setMinimumWidth(480)


def _haken(px: int):
    from PySide6.QtGui import QPixmap
    pm = QPixmap(px * 2, px * 2); pm.setDevicePixelRatio(2); pm.fill(Qt.transparent)
    p = QPainter(pm); p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen); p.setBrush(QColor(Farbe.GRUEN)); p.drawEllipse(QRectF(0, 0, px, px))
    p.setPen(QPen(QColor(Farbe.WEISS), 2.6, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    p.drawPolyline([QPointF(px * 0.28, px * 0.52), QPointF(px * 0.44, px * 0.68), QPointF(px * 0.74, px * 0.36)])
    p.end()
    return pm


def _bilder_ordner() -> str:
    return QStandardPaths.writableLocation(QStandardPaths.PicturesLocation) or os.path.expanduser("~")


def bild_export_fragen(parent, startordner: str, dpi: int) -> BildWahl | None:
    f = BildExportFenster(parent, startordner, dpi)
    return f.wahl() if f.exec() == QDialog.Accepted else None


def erfolg_zeigen(parent, dateien: list[str]) -> None:
    if dateien:
        ErfolgFenster(parent, dateien).exec()
