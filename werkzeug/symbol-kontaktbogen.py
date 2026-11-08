#!/usr/bin/env python3
"""Kontaktbogen für Symbolentwürfe: zeichnet jedes Symbol aus ``assets/icons/entwurf/`` neben das aktuelle Symbol gleichen Namens.

    .venv/bin/python werkzeug/symbol-kontaktbogen.py [--ziel docs/symbolsystem]

Je Symbol: groß (72 px) und in 16, 20, 24 px — ohne Hochskalierung, also so grob wie auf einem normalen Bildschirm; links der Entwurf, rechts das
bisherige Symbol. Es entstehen PNG-Bilder in hell und dunkel (Qt-Zeichnung, kein HTML).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(WURZEL, "src"))

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter, QPen
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

THEMEN = {"hell": dict(grund="#ffffff", tinte="#1f2328", leise="#6b7280", linie="#d8dce1"),
          "dunkel": dict(grund="#202124", tinte="#f4f6f8", leise="#9aa0a6", linie="#3c4043")}
ZELLE_B, ZELLE_H, RAND = 190, 190, 16


def svg_neu(pfad_d: str, farbe: str, strich: float) -> bytes:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{farbe}" stroke-width="{strich}" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="{pfad_d}"/></svg>').encode()


def zeichne(p: QPainter, svg: bytes, x: float, y: float, px: int) -> None:
    QSvgRenderer(QByteArray(svg)).render(p, QRectF(x, y, px, px))


def bogen(daten: dict, thema: dict, alt_pfade: dict, alt_strich: float) -> QImage:
    spalten = 6
    zeilen = 0
    for namen in daten["gruppen"].values():
        zeilen += 1 + (len(namen) + spalten - 1) // spalten
    bild = QImage(RAND * 2 + spalten * ZELLE_B, RAND * 2 + zeilen * ZELLE_H - (zeilen - len(daten["gruppen"])) * 0 + 0, QImage.Format_ARGB32)
    # Höhe: Titelzeilen sind niedriger; wir rechnen genau nach
    hoehe = RAND * 2
    for namen in daten["gruppen"].values():
        hoehe += 34 + ((len(namen) + spalten - 1) // spalten) * ZELLE_H
    bild = QImage(RAND * 2 + spalten * ZELLE_B, hoehe, QImage.Format_ARGB32)
    bild.fill(QColor(thema["grund"]))
    p = QPainter(bild)
    p.setRenderHint(QPainter.Antialiasing)
    schrift = QFont("Sans", 9)
    titel = QFont("Sans", 11, QFont.Bold)
    y = RAND
    for gruppe, namen in daten["gruppen"].items():
        p.setFont(titel); p.setPen(QColor(thema["tinte"]))
        p.drawText(RAND, y + 20, gruppe)
        y += 34
        for i, n in enumerate(namen):
            x0 = RAND + (i % spalten) * ZELLE_B
            y0 = y + (i // spalten) * ZELLE_H
            p.setPen(QPen(QColor(thema["linie"]), 1)); p.drawRect(x0, y0, ZELLE_B - 6, ZELLE_H - 6)
            p.setFont(schrift); p.setPen(QColor(thema["tinte"])); p.drawText(x0 + 8, y0 + 16, n)
            neu = svg_neu(daten["pfade"][n], thema["tinte"], daten["strich"])
            alt_d = alt_pfade.get(n)
            alt = svg_neu(alt_d, thema["tinte"], alt_strich) if alt_d and not alt_d.startswith("#e#") else None
            zeichne(p, neu, x0 + 10, y0 + 26, 72)
            if alt:
                zeichne(p, alt, x0 + 98, y0 + 26, 72)
            for k, px in enumerate((16, 20, 24)):
                gx = x0 + 10 + (0 if k == 0 else 16 + 8 if k == 1 else 16 + 8 + 20 + 8)
                gx = x0 + 10 + [0, 24, 52][k]
                zeichne(p, neu, gx, y0 + 112, px)
                if alt:
                    zeichne(p, alt, gx + 88, y0 + 112, px)
            p.setPen(QColor(thema["leise"]))
            p.drawText(x0 + 10, y0 + 160, "Entwurf")
            p.drawText(x0 + 98, y0 + 160, "bisher" if alt else "—")
        y += ((len(namen) + spalten - 1) // spalten) * ZELLE_H
    p.end()
    return bild


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ziel", default=os.path.join(WURZEL, "docs", "symbolsystem"))
    ap.add_argument("--bisher", help="symbole.json aus der Zeit vor dem Einbau (Gegenstück rechts); ohne Angabe gilt die aktuelle Wiedergabe")
    a = ap.parse_args()
    app = QApplication([])
    from lunivo_writer.ui.widgets import icons
    daten = json.load(open(os.path.join(WURZEL, "assets", "icons", "entwurf", "entwurf.json"), encoding="utf-8"))
    if a.bisher:
        vorher = json.load(open(a.bisher, encoding="utf-8"))
        alt = {n: vorher.get(n) or icons.katalog().get(n) for n in daten["pfade"]}
    else:
        alt = {n: icons._symbolpfad(n) for n in daten["pfade"]}
    os.makedirs(a.ziel, exist_ok=True)
    for name, thema in THEMEN.items():
        ziel = os.path.join(a.ziel, f"kontaktbogen-{name}.png")
        bogen(daten, thema, alt, 1.05 if a.bisher else icons.STRICH).save(ziel)
        print(ziel)


if __name__ == "__main__":
    main()
