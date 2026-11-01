#!/usr/bin/env python3
"""Schreibt jedes Funktionssymbol aus assets/icons/symbole.json als eigenständige SVG-Datei nach assets/icons/svg/ und prüft sie.

Quelle der Wahrheit bleibt symbole.json (so lädt das Programm); die SVG-Dateien sind eine erzeugte Referenz (nicht von Hand ändern).
Prüfung je Datei: gültiges XML, viewBox 0 0 24 24, mit QSvgRenderer renderbar, Zeichnung innerhalb 0,9…23,1. Kein HTML."""
import json
import os
import sys
import xml.etree.ElementTree as ET

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

STRICH = 1.5


def main() -> int:
    sym = json.load(open(os.path.join(W, "assets", "icons", "symbole.json"), encoding="utf-8"))
    ziel = os.path.join(W, "assets", "icons", "svg")
    os.makedirs(ziel, exist_ok=True)
    for f in os.listdir(ziel):
        if f.endswith(".svg"):
            os.remove(os.path.join(ziel, f))
    fehler = []
    for n, d in sorted(sym.items()):
        txt = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
               f'stroke-width="{STRICH}" stroke-linecap="round" stroke-linejoin="round"><path d="{d}"/></svg>\n')
        try:
            ET.fromstring(txt)
        except ET.ParseError as e:
            fehler.append(f"{n}: XML {e}")
            continue
        r = QSvgRenderer(QByteArray(txt.replace("currentColor", "#000").encode()))
        probe = QSvgRenderer(QByteArray(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -50 124 124"><path id="p" d="{d}"/></svg>'.encode()))
        b = probe.boundsOnElement("p")
        if not r.isValid():
            fehler.append(f"{n}: nicht renderbar")
        elif not (b.left() >= 0.9 and b.top() >= 0.9 and b.right() <= 23.1 and b.bottom() <= 23.1):
            fehler.append(f"{n}: Zeichnung außerhalb 0,9…23,1 ({b.left():.1f},{b.top():.1f},{b.right():.1f},{b.bottom():.1f})")
        open(os.path.join(ziel, f"{n}.svg"), "w", encoding="utf-8").write(txt)
    print(len(sym), "SVG geschrieben;", len(fehler), "Befunde")
    for f in fehler:
        print(" ", f)
    return 0


if __name__ == "__main__":
    QApplication([])
    sys.exit(main())
