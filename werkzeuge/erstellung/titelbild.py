"""Zeichnet die Titelbilder für die README mit QPainter.

Aufruf (nimmt die Anwendung neu auf und setzt das Bild zusammen): .venv/bin/python werkzeuge/erstellung/titelbild.py
Ausgabe: ressourcen/bilder/titelbild.png
Nur Qt-Zeichnen, kein HTML.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (QBrush, QColor, QFont, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath,
                           QPen, QPixmap, QRadialGradient)

WURZEL = Path(__file__).resolve().parents[2]
BILDER = WURZEL / "ressourcen" / "bilder"
LOGO = WURZEL / "ressourcen" / "symbole" / "varianten" / "icon-SVG" / "Logo-Bunte.png"
BREITE, HOEHE = 1600, 1200

def _fenster(p: QPainter, bild: QPixmap, ziel: QRectF, thema: dict) -> None:
    """Screenshot mit runden Ecken, Schatten und Rahmen."""
    for i, grad in enumerate((26, 16, 8)):
        schatten = QPainterPath()
        schatten.addRoundedRect(ziel.adjusted(-grad / 3, grad / 2 - 6, grad / 3, grad / 2 + 6), 14, 14)
        p.fillPath(schatten, QColor(0, 0, 0, int(thema["schatten"] / (i + 2.5))))
    pfad = QPainterPath()
    pfad.addRoundedRect(ziel, 12, 12)
    p.save()
    p.setClipPath(pfad)
    p.drawPixmap(ziel, bild, QRectF(bild.rect()))
    p.restore()
    p.setPen(QPen(QColor(thema["rahmen"]), 1.5))
    p.setBrush(Qt.NoBrush)
    p.drawPath(pfad)


def aufnehmen() -> None:
    """Startet Lunivo (ohne Bildschirm) und nimmt das Hauptfenster hell und dunkel auf."""
    sys.path.insert(0, str(WURZEL / "werkzeuge" / "erstellung"))
    import bildschirmfotos as B
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance()
    for thema, name in (("light", "titel-hell.png"), ("dark", "titel-dunkel.png")):
        w = B.fenster(app, thema)
        B.reiter(w, "Start")
        w.sidebar.setVisible(True)
        B.warte(1500)
        B.foto(w, name)
        B.schliessen(w)


def zeichne() -> Path:
    """Ein Titelbild: Zwei Fenster wie in der Vorlage: hell hinten, dunkel vorn, ohne Logo."""
    t = {"oben": "#1a2a3a", "unten": "#0b121b", "glanz": "#2a7f9c", "titel": "#ffffff", "untertitel": "#8fdcea",
         "schatten": 170, "rahmen": "#3a4a60"}
    bild = QImage(BREITE, HOEHE, QImage.Format_ARGB32)
    bild.fill(Qt.transparent)
    p = QPainter(bild)
    p.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
    pfad = QPainterPath()
    pfad.addRoundedRect(QRectF(0, 0, BREITE, HOEHE), 44, 44)
    p.setClipPath(pfad)
    verlauf = QLinearGradient(0, 0, 0, HOEHE)
    verlauf.setColorAt(0, QColor(t["oben"]))
    verlauf.setColorAt(1, QColor(t["unten"]))
    p.fillRect(bild.rect(), verlauf)
    glanz = QRadialGradient(QPointF(BREITE / 2, 480), 760)
    farbe = QColor(t["glanz"])
    farbe.setAlpha(90)
    glanz.setColorAt(0, farbe)
    farbe.setAlpha(0)
    glanz.setColorAt(1, farbe)
    p.fillRect(bild.rect(), glanz)
    _fenster(p, QPixmap(str(BILDER / "titel-hell.png")), QRectF(50, 100, 940, 564), t)
    _fenster(p, QPixmap(str(BILDER / "titel-dunkel.png")), QRectF(610, 420, 940, 564), t)
    p.setClipping(False)
    p.setPen(QColor(t["titel"]))
    schrift = QFont("Inter", 1)
    schrift.setPixelSize(104)
    schrift.setWeight(QFont.Weight.Bold)
    p.setFont(schrift)
    p.drawText(QRectF(0, 1002, BREITE, 120), Qt.AlignHCenter | Qt.AlignVCenter, "Lunivo Writer")
    p.setPen(QColor(t["untertitel"]))
    schrift.setPixelSize(42)
    schrift.setWeight(QFont.Weight.Normal)
    p.setFont(schrift)
    p.drawText(QRectF(0, 1112, BREITE, 56), Qt.AlignHCenter | Qt.AlignVCenter,
               "Schreib, wie du denkst. Lunivo achtet auf den Rest.")
    p.end()
    ziel = BILDER / "titelbild.png"
    bild.save(str(ziel))
    return ziel


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    aufnehmen()
    print(zeichne())
