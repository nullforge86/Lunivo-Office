#!/usr/bin/env python3
"""Repräsentative Icon-Auswahl prüfen (Auftrag Phase 8–10):  python3 werkzeug/icon-auswahl.py

Liest assets/icons/entwurf/auswahl.json, schreibt je Variante eine SVG nach assets/icons/entwurf/svg-auswahl/, rendert eine
Kontaktübersicht (hell links, dunkel rechts; 16/20/24 px; Funktionsnamen) mit Qt nach assets/icons/entwurf/kontaktuebersicht-auswahl.png
und schreibt die technische Prüfung nach docs/entwicklung/icon-auswahl-technik.md. Kein HTML."""
import json
import os
import sys
import xml.etree.ElementTree as ET

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtCore import QByteArray, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

STRICH = 1.5
HELL = ("#ffffff", "#1f2328")
DUNKEL = ("#1f2328", "#f4f6f8")


def svg(pfad, farbe):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="{farbe}" '
            f'stroke-width="{STRICH}" stroke-linecap="round" stroke-linejoin="round"><path d="{pfad}"/></svg>')


def bild(pfad, px, farbe):
    img = QImage(px, px, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(svg(pfad, farbe).encode())).render(p, QRectF(0, 0, px, px))
    p.end()
    return img


def lum(h):
    c = QColor(h)
    f = lambda v: v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c.redF()) + 0.7152 * f(c.greenF()) + 0.0722 * f(c.blueF())


def kontrast(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def main():
    auswahl = json.load(open(os.path.join(W, "assets", "icons", "entwurf", "auswahl.json"), encoding="utf-8"))
    zeilen = [(a["funktion"], v, a["varianten"][v], v == a["empfohlen"]) for a in auswahl for v in a["varianten"]]
    ordner = os.path.join(W, "assets", "icons", "entwurf", "svg-auswahl")
    os.makedirs(ordner, exist_ok=True)
    technik = ["| Symbol | XML gültig | viewBox 0 0 24 24 | QSvgRenderer gültig | Zeichnung innerhalb 1…23 | Tinte 16 px | Ergebnis |", "|---|---|---|---|---|---|---|"]
    for a in auswahl:
        for v, d in a["varianten"].items():
            datei = f"{a['name']}-{v}.svg"
            txt = svg(d, "currentColor") + "\n"
            open(os.path.join(ordner, datei), "w", encoding="utf-8").write(txt)
            try:
                wurzel = ET.fromstring(txt)
                xml = "ja"
                vb = "ja" if wurzel.get("viewBox") == "0 0 24 24" else "NEIN"
            except ET.ParseError:
                xml, vb = "NEIN", "NEIN"
            r = QSvgRenderer(QByteArray(svg(d, "#000000").encode()))
            test = QSvgRenderer(QByteArray(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-50 -50 124 124"><path id="p" d="{d}"/></svg>'.encode()))
            b = test.boundsOnElement("p")
            innen = b.left() >= 0.9 and b.top() >= 0.9 and b.right() <= 23.1 and b.bottom() <= 23.1
            m = bild(d, 16, "#000000")
            tinte = sum(1 for y in range(16) for x in range(16) if m.pixelColor(x, y).alpha() > 90) / 256
            ok = xml == "ja" and vb == "ja" and r.isValid() and innen and 0.04 <= tinte <= 0.55
            technik.append(f"| {a['funktion']} {v} (`{datei}`) | {xml} | {vb} | {'ja' if r.isValid() else 'NEIN'} | {'ja' if innen else 'NEIN'} ({b.left():.1f}…{b.right():.1f} / {b.top():.1f}…{b.bottom():.1f}) | {tinte * 100:.0f} % | {'OK' if ok else 'PRÜFEN'} |")
    zh, name_b, blk = 54, 150, 200
    img = QImage(name_b + 2 * blk, 36 + len(zeilen) * zh, QImage.Format_ARGB32)
    img.fill(QColor(HELL[0]))
    p = QPainter(img)
    p.fillRect(name_b + blk, 0, blk, img.height(), QColor(DUNKEL[0]))
    p.fillRect(0, 0, name_b, img.height(), QColor(HELL[0]))
    p.setFont(QFont("DejaVu Sans", 8, QFont.Bold))
    p.setPen(QColor(HELL[1]))
    p.drawText(6, 4, name_b, 26, Qt.AlignVCenter, "Funktion / Variante")
    p.drawText(name_b + 6, 4, blk, 26, Qt.AlignVCenter, "HELL  16 · 20 · 24 · 48")
    p.setPen(QColor(DUNKEL[1]))
    p.drawText(name_b + blk + 6, 4, blk, 26, Qt.AlignVCenter, "DUNKEL  16 · 20 · 24 · 48")
    p.setFont(QFont("DejaVu Sans", 8))
    for i, (f, v, d, emp) in enumerate(zeilen):
        y = 36 + i * zh
        p.setPen(QColor(HELL[1]))
        p.drawText(6, y, name_b - 8, zh, Qt.AlignVCenter | Qt.TextWordWrap, f"{f}\nVariante {v}{'  ★ empfohlen' if emp else ''}")
        for bl, (hg, fg) in enumerate((HELL, DUNKEL)):
            x0 = name_b + bl * blk
            for k, px in enumerate((16, 20, 24)):
                p.drawImage(x0 + 8 + k * 34, y + (zh - px) // 2, bild(d, px, fg))
            p.drawImage(x0 + 8 + 3 * 34 + 8, y + 3, bild(d, 48, fg))
        p.setPen(QColor(128, 128, 128, 80))
        p.drawLine(0, y + zh - 1, img.width(), y + zh - 1)
    p.end()
    img.save(os.path.join(W, "assets", "icons", "entwurf", "kontaktuebersicht-auswahl.png"))
    kopf = ["# Icon-Auswahl: technische Prüfung (Phase 10.1)", "",
            f"Erzeugt mit `werkzeug/icon-auswahl.py`. Strich {STRICH} px, Rendering mit `QSvgRenderer` (1× – strenger als die 2×-Darstellung im Programm).", "",
            "## Kontrast (WCAG-Formel, Nicht-Text-Kontrast Mindestwert 3:1)",
            f"- hell: {HELL[1]} auf {HELL[0]} = {kontrast(*HELL):.1f}:1", f"- dunkel: {DUNKEL[1]} auf {DUNKEL[0]} = {kontrast(*DUNKEL):.1f}:1",
            "- deaktiviert: Palettenfarbe des Programms (Disabled); hier nicht gemessen (**NICHT PRÜFBAR** ohne laufende Oberfläche)", ""]
    open(os.path.join(W, "docs", "entwicklung", "icon-auswahl-technik.md"), "w", encoding="utf-8").write("\n".join(kopf + technik) + "\n")
    print(len(zeilen), "Varianten;", sum(1 for t in technik if t.endswith("PRÜFEN |")), "zu prüfen")


if __name__ == "__main__":
    QApplication([])
    main()
