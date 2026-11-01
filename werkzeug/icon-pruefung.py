#!/usr/bin/env python3
"""Prüfung des gesamten Icon-Systems:  python3 werkzeug/icon-pruefung.py

Rendert alle Funktionssymbole (assets/icons/symbole.json) mit Qt bei 16/20/24 px in hell und dunkel nach
assets/icons/uebersicht/ und schreibt docs/entwicklung/icon-qualitaet.md (Kennzahlen je Symbol, ähnlichste Paare).
Maße: Tinte = Anteil belegter Pixel bei 16 px (zu wenig = verschwindet, zu viel = Klumpen); Überdeckung = gemeinsame
Pixel zweier Symbole bei 16 px. Kein HTML."""
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


def bild(pfad: str, px: int, farbe: str) -> QImage:
    img = QImage(px, px, QImage.Format_ARGB32_Premultiplied)
    img.fill(Qt.transparent)
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing)
    QSvgRenderer(QByteArray(icons._svg(pfad, farbe))).render(p, QRectF(0, 0, px, px))
    p.end()
    return img


def maske(pfad: str) -> tuple:
    img = bild(pfad, 16, "#000000")
    return tuple(img.pixelColor(x, y).alpha() > 90 for y in range(16) for x in range(16))


def uebersicht(namen: list, ziel: str, dunkel: bool) -> None:
    al = icons.pfade_original()
    hg, fg = ("#1f2328", "#f4f6f8") if dunkel else ("#ffffff", "#1f2328")
    sp, w, h = 8, 150, 40
    img = QImage(sp * w, -(-len(namen) // sp) * h, QImage.Format_ARGB32)
    img.fill(QColor(hg))
    p = QPainter(img)
    p.setFont(QFont("DejaVu Sans", 7))
    p.setPen(QColor(fg))
    for i, n in enumerate(namen):
        x, y = (i % sp) * w + 4, (i // sp) * h + 4
        for k, px in enumerate((16, 20, 24)):
            p.drawImage(x + k * 28, y + (24 - px) // 2, bild(al[n], px, fg))
        p.drawText(x + 88, y, w - 92, 32, Qt.AlignVCenter | Qt.TextWordWrap, n)
    p.end()
    img.save(ziel)


def main() -> None:
    al = icons.pfade_original()
    namen = sorted(al, key=str.lower)
    ordner = os.path.join(WURZEL, "assets", "icons", "uebersicht")
    os.makedirs(ordner, exist_ok=True)
    uebersicht(namen, os.path.join(ordner, "alle-hell.png"), False)
    uebersicht(namen, os.path.join(ordner, "alle-dunkel.png"), True)
    m = {n: maske(al[n]) for n in namen}
    zeilen, paare = [], []
    for n in namen:
        best = (0.0, "")
        for o in namen:
            if o == n:
                continue
            u = sum(1 for a, b in zip(m[n], m[o]) if a or b)
            ue = sum(1 for a, b in zip(m[n], m[o]) if a and b) / u if u else 0.0
            if ue > best[0]:
                best = (ue, o)
        tinte = sum(m[n]) / 256
        urteil = []
        if tinte < 0.04:
            urteil.append("zu hell")
        if tinte > 0.55:
            urteil.append("zu dicht")
        if al[n] == al[best[1]]:
            urteil.append("gleiche Zeichnung (gewollt?)")
        elif best[0] >= 0.85:
            urteil.append("fast gleich wie " + best[1])
        zeilen.append(f"| {n} | {tinte * 100:.0f} % | {best[1]} | {best[0]:.2f} | {', '.join(urteil) or 'ok'} |")
        if best[0] >= 0.85 and n < best[1]:
            paare.append((best[0], n, best[1]))
    kopf = ["# Icon-Qualität: Kennzahlen aller Funktionssymbole", "",
            f"Erzeugt von `werkzeug/icon-pruefung.py`. {len(namen)} Symbole. Übersichten: `assets/icons/uebersicht/alle-hell.png`, `alle-dunkel.png` (16/20/24 px).",
            "Maße sind Hilfen, kein Ersatz für Nutzertests (`icon-testbogen.md`). Tinte = belegte Pixel bei 16 px; Überdeckung = Pixelgleichheit mit dem ähnlichsten anderen Symbol.", "",
            f"Paare mit Überdeckung ≥ 0,85: {len(paare)}", ""]
    kopf += [f"- {a} ↔ {b} ({w:.2f})" for w, a, b in sorted(paare, reverse=True)]
    kopf += ["", "| Symbol | Tinte 16 px | ähnlichstes | Überdeckung | Urteil |", "|---|---|---|---|---|"]
    with open(os.path.join(WURZEL, "docs", "entwicklung", "icon-qualitaet.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(kopf + zeilen) + "\n")
    print(len(namen), "Symbole;", len(paare), "Paare >= 0,85")
    for w, a, b in sorted(paare, reverse=True):
        print(f"{w:.2f} {a} <-> {b}")


if __name__ == "__main__":
    QApplication([])
    main()
