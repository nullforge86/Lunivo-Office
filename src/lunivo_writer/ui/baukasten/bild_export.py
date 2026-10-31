"""„Als Bild exportieren“: die Bildlayoutkarten und Einstellungen in der rechten Spalte des Datei-Menüs.

Oben zwei Karten — **Jede Seite** (eine Datei je Seite) und **Langes Bild** (alle Seiten untereinander) —, darunter Wasserzeichen,
Qualität, Format und Zielordner, rechts unten **Exportieren**. Die Bildchen auf den Karten zeichnet ``QPainter``; geschrieben wird
in ``services/bild_export.py``.
"""
from __future__ import annotations

import os
from typing import Callable

from PySide6.QtCore import QPointF, QRectF, QSize, QStandardPaths, Qt, QUrl
from PySide6.QtGui import QColor, QDesktopServices, QPainter, QPainterPath, QPalette, QPen
from PySide6.QtWidgets import (QAbstractButton, QButtonGroup, QComboBox, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QLayout, QPushButton, QVBoxLayout, QWidget)

from lunivo_writer.core.farben import Farbe
from lunivo_writer.services.bild_export import FORMATE, QUALITAET, BildWahl

STIL = ("QPushButton#beHaupt { background: " + Farbe.AKZENT + "; color: white; border: none; border-radius: 4px; padding: 8px 28px; }"
        "QPushButton#beHaupt:hover { background: " + Farbe.AKZENT_DUNKEL + "; }"
        "QLabel#beText { font-size: 11pt; }")


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


class BildExportAnsicht(QWidget):
    """Bildexport als Seite in der zweiten Spalte des Datei-Menüs."""

    def __init__(self, parent, startordner: str, dpi: int, exportieren: Callable[[BildWahl], list[str]], zurueck: Callable[[], None]):
        super().__init__(parent)
        self.setStyleSheet(STIL)
        self._exportieren_cb = exportieren
        self._zurueck = zurueck
        v = QVBoxLayout(self); v.setContentsMargins(30, 20, 30, 16); v.setSpacing(8)
        titel = QLabel("Als Bild exportieren"); titel.setObjectName("bsTitel"); v.addWidget(titel)
        intro = QLabel("Wähle das Bildlayout, die Qualität und den Speicherort. Jede Seite kann einzeln oder als langes Bild gespeichert werden.")
        intro.setWordWrap(True); intro.setObjectName("bsHinweis"); v.addWidget(intro)

        karten = QHBoxLayout(); karten.setSpacing(24)
        self.k_seite = _Karte("Jede Seite", False)
        self.k_lang = _Karte("Langes Bild", True)
        gruppe = QButtonGroup(self); gruppe.setExclusive(True)
        for k in (self.k_seite, self.k_lang):
            gruppe.addButton(k); karten.addWidget(k)
        karten.addStretch(1)
        self.k_seite.setChecked(True)
        v.addWidget(_abschnitt("1. Bildlayout", "Wähle eine Bilddatei pro Seite oder ein langes Bild mit allen Seiten untereinander.", karten))

        g = QGridLayout(); g.setHorizontalSpacing(14); g.setVerticalSpacing(14)
        self.wasser = QLineEdit(); self.wasser.setPlaceholderText("Zum Beispiel: Vertraulich")
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
        waehlen = self.ordner.addAction(icons.icon("ellipsis", 18), QLineEdit.TrailingPosition)
        waehlen.setToolTip("Ordner wählen …")
        waehlen.triggered.connect(self._ordner_waehlen)
        self.k_export = QPushButton("Exportieren"); self.k_export.setObjectName("beHaupt"); self.k_export.setDefault(True)
        self.k_export.setCursor(Qt.PointingHandCursor); self.k_export.setMinimumWidth(120)
        self.k_export.clicked.connect(self._exportieren)
        self.wasser.setToolTip("Optionaler, blasser Schriftzug auf jeder exportierten Seite.")
        self.qualitaet.setToolTip("Höhere Auflösung ergibt schärfere, aber größere Bilddateien.")
        self.format.setToolTip("Wähle PNG, JPG, BMP oder TIF.")
        for zeile, (text, feld) in enumerate((("&Wasserzeichen", self.wasser), ("&Qualität", self.qualitaet),
                                              ("&Format", self.format), ("Speichern &in", self.ordner))):
            l = QLabel(text); l.setBuddy(feld)
            g.addWidget(l, zeile, 0)
            g.addWidget(feld, zeile, 1, Qt.AlignLeft if feld in (self.qualitaet, self.format) else Qt.Alignment())
        for feld in (self.wasser, self.qualitaet, self.format, self.ordner, self.k_export):
            feld.setMinimumHeight(36)                                 # Felder in der Höhe des Vorbilds, nicht schmal
        g.setColumnStretch(1, 1)
        v.addWidget(_abschnitt("2. Ausgabe festlegen", "Lege Wasserzeichen, Bildqualität, Dateiformat und Zielordner fest.", g))
        self.k_export.setText("Bilder exportieren")
        self.ordner.setAccessibleName("Ordner für die exportierten Bilder")
        self.wasser.setAccessibleName("Wasserzeichen, optional")
        self.qualitaet.setAccessibleName("Bildqualität")
        self.format.setAccessibleName("Bildformat")
        self._wahl: BildWahl | None = None
        self._dateien: list[str] = []

        self.meldung = QLabel(); self.meldung.setWordWrap(True); self.meldung.setObjectName("bsHinweis"); self.meldung.hide()
        v.addWidget(self.meldung)
        aktionen = QHBoxLayout(); aktionen.addStretch(1)
        self._datei_oeffnen = QPushButton("Bild öffnen"); self._datei_oeffnen.setEnabled(False)
        self._ordner_oeffnen = QPushButton("Ordner öffnen"); self._ordner_oeffnen.setEnabled(False)
        self._datei_oeffnen.hide(); self._ordner_oeffnen.hide()
        self._datei_oeffnen.clicked.connect(self._erstes_bild_oeffnen)
        self._ordner_oeffnen.clicked.connect(self._zielordner_oeffnen)
        aktionen.addWidget(self._datei_oeffnen); aktionen.addWidget(self._ordner_oeffnen)
        v.addLayout(aktionen)
        v.addStretch(1)
        fuss = QHBoxLayout(); fuss.setContentsMargins(0, 8, 0, 0)
        self.zurueck_knopf = QPushButton("Zurück zum Dokument"); self.zurueck_knopf.clicked.connect(self._zurueck)
        self.k_export.setMinimumHeight(38); self.k_export.setMinimumWidth(160)
        fuss.addStretch(1); fuss.addWidget(self.zurueck_knopf); fuss.addWidget(self.k_export)
        v.addLayout(fuss)

    def _ordner_waehlen(self) -> None:
        from lunivo_writer.ui.baukasten.speichern_fenster import ordner_waehlen
        neu = ordner_waehlen(self, "Ordner für die Bilder", self.ordner.text() or _bilder_ordner())
        if neu:
            self.ordner.setText(neu)

    def _exportieren(self) -> None:
        ordner = os.path.expanduser(self.ordner.text().strip())
        if not os.path.isdir(ordner):
            self.meldung.setText(f"Der gewählte Ordner „{ordner}“ ist nicht vorhanden.")
            self.meldung.show(); self.ordner.setFocus()
            return
        self._wahl = BildWahl(lang=self.k_lang.isChecked(), wasserzeichen=self.wasser.text(), dpi=int(self.qualitaet.currentData()),
                              format=self.format.currentText(), ordner=ordner)
        self._dateien = []
        self._datei_oeffnen.setEnabled(False); self._datei_oeffnen.hide()
        self._ordner_oeffnen.setEnabled(False); self._ordner_oeffnen.hide()
        self.meldung.setStyleSheet("")
        self.k_export.setEnabled(False); self.meldung.setText("Bilder werden erstellt …"); self.meldung.show()
        from PySide6.QtWidgets import QApplication
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            dateien = self._exportieren_cb(self._wahl)
        except OSError as e:
            self.meldung.setText(f"Export nicht möglich: {e}")
            self.meldung.setStyleSheet("color: #e88b8b;")
            self.ordner.setFocus()
            return
        finally:
            QApplication.restoreOverrideCursor()
            self.k_export.setEnabled(True)
        self._dateien = dateien
        if not dateien:
            self.meldung.setText("Es wurden keine Seiten zum Exportieren gefunden.")
            return
        self.meldung.setStyleSheet("")
        self.meldung.setText(f"{len(dateien)} Bild{'er' if len(dateien) != 1 else ''} gespeichert.")
        self.meldung.show()
        self._datei_oeffnen.setEnabled(True)
        self._ordner_oeffnen.setEnabled(True)
        self._datei_oeffnen.show(); self._ordner_oeffnen.show()

    def _erstes_bild_oeffnen(self) -> None:
        if self._dateien:
            QDesktopServices.openUrl(QUrl.fromLocalFile(self._dateien[0]))

    def _zielordner_oeffnen(self) -> None:
        if self._dateien:
            QDesktopServices.openUrl(QUrl.fromLocalFile(os.path.dirname(self._dateien[0])))


def _abschnitt(titel: str, hilfe: str, layout: QLayout) -> QWidget:
    w = QWidget(); v = QVBoxLayout(w); v.setContentsMargins(0, 6, 0, 6); v.setSpacing(5)
    t = QLabel(titel); t.setStyleSheet("font-weight: 600; font-size: 11pt;")
    h = QLabel(hilfe); h.setObjectName("bsHinweis"); h.setWordWrap(True)
    v.addWidget(t); v.addWidget(h); v.addLayout(layout)
    return w


def _bilder_ordner() -> str:
    return QStandardPaths.writableLocation(QStandardPaths.PicturesLocation) or os.path.expanduser("~")
