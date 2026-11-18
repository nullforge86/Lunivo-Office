"""Das Dokument als Bild schreiben: jede Seite als eigene Datei oder alle Seiten untereinander als ein langes Bild.

Die Seiten setzt und zeichnet der Qt-freie Kern (dieselbe Darstellung wie Druck und PDF); Qt rastert sie nur. Seite für Seite: Bei hoher
Auflösung belegt ein Seitenbild Dutzende MB, alle auf einmal im Speicher zu halten, kann den Arbeitsspeicher füllen.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QImage, QPainter

from lunivo_writer.kern.farben import Farbe

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


def bilder_schreiben(dokument, name: str, wahl: BildWahl) -> list[str]:
    """Schreibt die Bilder nach ``wahl.ordner``. → die geschriebenen Dateien.

    ``dokument`` ist das maßgebliche ``Dokument``; gesetzt und gezeichnet wird es von derselben Layout-Engine und demselben Renderer wie die
    Zeichenfläche, der Druck und das PDF (``dienste.drucken.Ausgabe``)."""
    from lunivo_writer.dienste.drucken import Ausgabe
    endung = FORMATE[wahl.format][0]
    stamm = os.path.join(wahl.ordner, os.path.splitext(os.path.basename(name))[0] or "Dokument")
    faktor = wahl.dpi / 96
    ausgabe = Ausgabe(dokument)
    if ausgabe.anzahl() == 0:
        return []
    if not wahl.lang:
        return _seitenbilder_schreiben(ausgabe, stamm, endung, faktor, wahl)
    return _langes_bild_schreiben(ausgabe, stamm, endung, faktor, wahl)


def _seitenbilder_schreiben(ausgabe, stamm: str, endung: str, faktor: float, wahl: BildWahl) -> list[str]:
    """Jede Seite eine Datei, Seite für Seite gerastert (nie alle Seitenbilder gleichzeitig im Speicher)."""
    mehrere = ausgabe.anzahl() > 1
    geschrieben = []
    for n in range(1, ausgabe.anzahl() + 1):
        img = ausgabe.bild(n, faktor)
        wasserzeichen(img, wahl.wasserzeichen)
        pfad = _frei(f"{stamm}-{n}.{endung}" if mehrere else f"{stamm}.{endung}")
        _speichern(img, pfad, wahl.format)
        geschrieben.append(pfad)
    return geschrieben


def _langes_bild_schreiben(ausgabe, stamm: str, endung: str, faktor: float, wahl: BildWahl) -> list[str]:
    """Alle Seiten untereinander in einem Bild; zuerst die Höhe abschätzen, damit es nicht zu groß für das Bildformat wird."""
    seiten = range(1, ausgabe.anzahl() + 1)
    luecke = int(LUECKE_PX * faktor)
    hoehe = sum(ausgabe.groesse_px(n, faktor)[1] for n in seiten) + luecke * (ausgabe.anzahl() - 1)
    if hoehe > LANG_MAX_PX:
        faktor *= LANG_MAX_PX / hoehe
        luecke = int(LUECKE_PX * faktor)
    groessen = [ausgabe.groesse_px(n, faktor) for n in seiten]
    breite = max(w for w, _h in groessen)
    gesamt = QImage(breite, sum(h for _w, h in groessen) + luecke * (len(groessen) - 1), QImage.Format_RGB32)
    gesamt.fill(QColor(Farbe.GRAU_HELL))
    p = QPainter(gesamt)
    y = 0
    for n in seiten:
        bild = ausgabe.bild(n, faktor)
        wasserzeichen(bild, wahl.wasserzeichen)                    # auf jede Seite einzeln, nicht einmal quer über das lange Bild
        p.drawImage((breite - bild.width()) // 2, y, bild)
        y += bild.height() + luecke
    p.end()
    pfad = _frei(f"{stamm}.{endung}")
    _speichern(gesamt, pfad, wahl.format)
    return [pfad]
