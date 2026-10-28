"""Das Dokument als Bild schreiben: jede Seite als eigene Datei oder alle Seiten untereinander als ein langes Bild.

Die Seiten zeichnet ``editor.pagination.seiten_bilder`` (dieselbe Darstellung wie Druck und PDF). Seite für Seite: Bei hoher
Auflösung belegt ein Seitenbild Dutzende MB, alle auf einmal im Speicher zu halten, kann den Arbeitsspeicher füllen.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter

from lunivo_writer.core.farben import Farbe

FORMATE = {"JPG": ("jpg", "JPG"), "PNG": ("png", "PNG"), "BMP": ("bmp", "BMP"), "TIF": ("tif", "TIFF")}
QUALITAET = [("Normal", 96), ("Standard", 150), ("Hoch", 200), ("Sehr hoch", 300)]
LANG_MAX_PX = 30000              # längste Seite eines langen Bildes; darüber wird es kleiner gerechnet (sonst schreiben JPG/BMP nicht)
LUECKE_PX = 12                   # Abstand zwischen den Seiten im langen Bild (bei 96 dpi)


@dataclass
class BildWahl:
    lang: bool = False           # False: jede Seite eine Datei · True: ein langes Bild
    wasserzeichen: str = ""
    dpi: int = 150
    format: str = "PNG"
    ordner: str = ""


def _frei(pfad: str) -> str:
    """Ein Dateiname, den es noch nicht gibt (nichts Vorhandenes wird überschrieben): „Brief (2).png“."""
    if not os.path.exists(pfad):
        return pfad
    stamm, endung = os.path.splitext(pfad)
    n = 2
    while os.path.exists(f"{stamm} ({n}){endung}"):
        n += 1
    return f"{stamm} ({n}){endung}"


def wasserzeichen(img: QImage, text: str) -> None:
    """Den Text schräg und blass über das ganze Bild legen."""
    if not text.strip():
        return
    p = QPainter(img)
    p.setRenderHint(QPainter.Antialiasing); p.setRenderHint(QPainter.TextAntialiasing)
    f = QFont(); f.setPixelSize(max(12, int(min(img.width(), img.height()) / 9))); f.setBold(True)
    p.setFont(f)
    farbe = QColor(Farbe.GRAU); farbe.setAlpha(70)
    p.setPen(farbe)
    p.translate(img.width() / 2, img.height() / 2)
    p.rotate(-35)
    breite = max(img.width(), img.height()) * 1.5
    p.drawText(QRectF(-breite / 2, -f.pixelSize(), breite, f.pixelSize() * 2), Qt.AlignCenter, text.strip())
    p.end()


def _speichern(img: QImage, pfad: str, fmt: str) -> None:
    endung, qt_fmt = FORMATE[fmt]
    if fmt == "JPG" and img.hasAlphaChannel():
        img = img.convertToFormat(QImage.Format_RGB32)
    if not img.save(pfad, qt_fmt, 92 if fmt == "JPG" else -1):
        raise OSError(f"„{os.path.basename(pfad)}“ konnte nicht geschrieben werden.")


def bilder_schreiben(doc, page, noten, name: str, wahl: BildWahl) -> list[str]:
    """Schreibt die Bilder nach ``wahl.ordner``. → die geschriebenen Dateien."""
    from lunivo_writer.editor.pagination import seiten_bilder, seitenzahl
    endung = FORMATE[wahl.format][0]
    stamm = os.path.join(wahl.ordner, os.path.splitext(os.path.basename(name))[0] or "Dokument")
    faktor = wahl.dpi / 96
    if not wahl.lang:
        bilder = seiten_bilder(doc, page, noten, faktor)
        erstes = next(bilder, None)
        if erstes is None:
            return []
        zweites = next(bilder, None)
        mehrere = zweites is not None
        geschrieben = []
        for i, img, _ps in (b for teil in ((erstes, zweites), bilder) for b in teil if b is not None):
            wasserzeichen(img, wahl.wasserzeichen)
            pfad = _frei(f"{stamm}-{i}.{endung}" if mehrere else f"{stamm}.{endung}")
            _speichern(img, pfad, wahl.format)
            geschrieben.append(pfad)
        return geschrieben
    # Langes Bild: zuerst die Höhe abschätzen, damit es nicht zu groß für das Bildformat wird
    from lunivo_writer.models.page import mm_to_px
    n = max(1, seitenzahl(doc, page, noten))
    hoehe = n * (mm_to_px(page.height_mm) + LUECKE_PX) * faktor
    if hoehe > LANG_MAX_PX:
        faktor *= LANG_MAX_PX / hoehe
    seiten = [img for _i, img, _ps in seiten_bilder(doc, page, noten, faktor)]
    if not seiten:
        return []
    luecke = int(LUECKE_PX * faktor)
    breite = max(s.width() for s in seiten)
    gesamt = QImage(breite, sum(s.height() for s in seiten) + luecke * (len(seiten) - 1), QImage.Format_RGB32)
    gesamt.fill(QColor(Farbe.GRAU_HELL))
    p = QPainter(gesamt)
    y = 0
    for s in seiten:
        wasserzeichen(s, wahl.wasserzeichen)                       # auf jede Seite einzeln, nicht einmal quer über das lange Bild
        p.drawImage((breite - s.width()) // 2, y, s)
        y += s.height() + luecke
    p.end()
    del seiten
    pfad = _frei(f"{stamm}.{endung}")
    _speichern(gesamt, pfad, wahl.format)
    return [pfad]
