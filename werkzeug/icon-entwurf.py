#!/usr/bin/env python3
"""Icon-Entwurf prüfen:  python3 werkzeug/icon-entwurf.py [Zielordner]

Schreibt aus assets/icons/entwurf/entwurf.json je Symbol eine SVG-Datei (Ordner svg/), rendert mit Qt (wie in der
Anwendung, aber 1× statt 2×, also strenger) eine Kontaktübersicht in hell und dunkel (Entwurf links, heutiges Symbol rechts,
je 16/20/24 px und 48 px Vergrößerung) und meldet die Ähnlichkeit der Symbole bei 16 px. Kein HTML."""
import itertools
import json
import os
import sys

WURZEL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(WURZEL, "src"))
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QByteArray, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QFont, QImage, QPainter  # noqa: E402
from PySide6.QtSvg import QSvgRenderer  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from lunivo_writer.ui.widgets import icons  # noqa: E402

GRUPPEN = [  # Verwechslungsgefahr: innerhalb einer Gruppe müssen die Symbole auch bei 16 px unterscheidbar sein
    ("Ausrichtung", ["links", "mitte", "rechts", "block", "einzug"]),
    ("Seitenaufbau", ["kopfz", "fussz", "spalte2", "spalte3"]),
    ("Datei", ["neu", "oeffnen", "speichern", "pdf", "drucken"]),
    ("Zwischenablage", ["schere", "kopie", "kleben"]),
    ("Tabelle", ["tabelle", "tabellezeile"]),
    ("Zeichen/Zahl", ["zahl", "ebenen", "raender", "assistent"]),
    ("Liste/Verlauf", ["punkte", "zurueck", "vor", "naechstes"]),
]


def svg(pfad: str, farbe: str, strich: float = icons.STRICH) -> bytes:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{farbe}" stroke-width="{strich}" '
            f'stroke-linecap="round" stroke-linejoin="round"><path d="{pfad}"/></svg>').encode()


def bild(pfad: str, px: int, farbe: str) -> QImage:
    img = QImage(px, px, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(svg(pfad, farbe))).render(p, QRectF(0, 0, px, px))
    p.end()
    return img


def alpha16(pfad: str) -> list[int]:
    img = bild(pfad, 16, "#000000")
    return [(img.pixelColor(x, y).alpha() > 90) for y in range(16) for x in range(16)]


def ueberdeckung(a: list[int], b: list[int]) -> float:
    """Anteil gemeinsamer Pixel an allen belegten Pixeln (1 = identisch)."""
    u = sum(1 for x, y in zip(a, b) if x or y)
    return sum(1 for x, y in zip(a, b) if x and y) / u if u else 0.0


def svg_schreiben(entwurf: dict, ordner: str) -> None:
    os.makedirs(ordner, exist_ok=True)
    for n, d in entwurf.items():
        with open(os.path.join(ordner, f"{n}.svg"), "wb") as fh:
            fh.write(svg(d, "currentColor").replace(b'stroke-width="1.5"', b'stroke-width="1.5"') + b"\n")


def uebersicht(entwurf: dict, ziel: str, dunkel: bool) -> None:
    alt = icons.pfade_original()
    hg, fg = ("#1f2328", "#f4f6f8") if dunkel else ("#ffffff", "#1f2328")
    zeile_h, name_b, block_b = 58, 104, 214
    namen = [n for _, g in GRUPPEN for n in g] + [n for n in entwurf if all(n not in g for _, g in GRUPPEN)]
    img = QImage(name_b + 2 * block_b + 10, 30 + len(namen) * zeile_h, QImage.Format_ARGB32)
    img.fill(QColor(hg))
    p = QPainter(img)
    p.setFont(QFont("DejaVu Sans", 8, QFont.Bold))
    p.setPen(QColor(fg))
    p.drawText(name_b, 4, block_b, 20, Qt.AlignLeft, "ENTWURF  16 / 20 / 24 / 48")
    p.drawText(name_b + block_b, 4, block_b, 20, Qt.AlignLeft, "HEUTE (zum Vergleich)")
    p.setFont(QFont("DejaVu Sans", 8))
    for i, n in enumerate(namen):
        y = 30 + i * zeile_h
        p.drawText(6, y, name_b - 8, zeile_h, Qt.AlignVCenter | Qt.TextWordWrap, n)
        for b, quelle in enumerate((entwurf.get(n), alt.get(n))):
            if quelle is None:
                p.drawText(name_b + b * block_b, y, block_b, zeile_h, Qt.AlignVCenter, "(kein Gegenstück)")
                continue
            x = name_b + b * block_b
            for k, px in enumerate((16, 20, 24)):
                p.drawImage(x + k * 36, y + 17, bild(quelle, px, fg))
            p.drawImage(x + 112, y + 4, bild(quelle, 48, fg))
        p.setPen(QColor(128, 128, 128, 70))
        p.drawLine(0, y + zeile_h - 1, img.width(), y + zeile_h - 1)
        p.setPen(QColor(fg))
    p.end()
    img.save(ziel)


def aehnlichkeit(entwurf: dict) -> list[str]:
    zeilen = []
    for titel, g in GRUPPEN:
        paare = [(round(ueberdeckung(alpha16(entwurf[a]), alpha16(entwurf[b])), 2), a, b) for a, b in itertools.combinations(g, 2)]
        paare_alt = {(a, b): ueberdeckung(alpha16(icons.pfade_original()[a]), alpha16(icons.pfade_original()[b]))
                     for a, b in itertools.combinations(g, 2) if a in icons.pfade_original() and b in icons.pfade_original()}
        w, a, b = max(paare)
        alt = paare_alt.get((a, b))
        zeilen.append(f"| {titel} | {a} ↔ {b} | {w:.2f} | {'—' if alt is None else f'{alt:.2f}'} | {'prüfen' if w > 0.6 else 'ok'} |")
    return zeilen


if __name__ == "__main__":
    app = QApplication([])
    ziel = sys.argv[1] if len(sys.argv) > 1 else os.path.join(WURZEL, "assets", "icons", "entwurf")
    with open(os.path.join(WURZEL, "assets", "icons", "entwurf", "entwurf.json"), encoding="utf-8") as fh:
        entwurf = json.load(fh)
    svg_schreiben(entwurf, os.path.join(ziel, "svg"))
    for dunkel in (False, True):
        uebersicht(entwurf, os.path.join(ziel, "kontaktuebersicht-dunkel.png" if dunkel else "kontaktuebersicht-hell.png"), dunkel)
    print(len(entwurf), "Symbole ->", ziel)
    print("| Gruppe | ähnlichstes Paar (Entwurf) | Überdeckung Entwurf | Überdeckung heute | Urteil |\n|---|---|---|---|---|")
    print("\n".join(aehnlichkeit(entwurf)))
