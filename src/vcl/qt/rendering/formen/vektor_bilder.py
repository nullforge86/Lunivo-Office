"""Vektorbilder aus Textprogrammen auf Qt legen: EMF und WMF (Windows-Metafiles). Ausgewertet und gerastert wird vom Kern über
``writer`` → ``framework``; Qt ist hier nur der Behälter (``QImage``) für das fertige Bild und die Fläche, auf die es gelegt wird."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QImage, QPainter

from vcl.qt.rendering.formen import bilddaten as BD
from vcl.qt.rendering.formen.anzeige import _ausgerichtet
from writer.funktionen.objekte import ist_metafile_emf, ist_metafile_wmf, metafile_rgba


def _qimage(erg) -> QImage | None:
    """``(breite, hoehe, RGBA)`` des Kerns als ``QImage``."""
    if erg is None:
        return None
    b, h, roh = erg
    return QImage(bytes(roh), b, h, b * 4, QImage.Format_RGBA8888).copy()


def bild_lesen(blob: bytes) -> QImage:
    """Ein eingebettetes Bild lesen: Pixelformate direkt, EMF/WMF über den Interpreter des Kerns (auch gepackt als EMZ/WMZ). Leeres QImage, wenn es sich nicht lesen lässt."""
    if blob[:2] == b"\x1f\x8b":
        try:
            blob = BD.entpacken(blob)
        except BD.BildFehler:
            return QImage()
    from vcl.qt.rendering.formen import bild_aus_daten
    if ist_metafile_emf(blob) or ist_metafile_wmf(blob):        # Metafile: zuerst als Vektor; leer gezeichnet → eingebettetes Bitmap (Rückfall)
        img = _qimage(metafile_rgba(blob)) or QImage()
        if not img.isNull() and not _leer(img):
            BD.merken(img, blob)
            return img
        roh = bild_aus_daten(blob)
        if not roh.isNull():
            return roh
        if not img.isNull():
            BD.merken(img, blob)
        return img
    return bild_aus_daten(blob)


def _leer(img: QImage) -> bool:
    """Ist das Bild ganz durchsichtig? (zur Probe auf 16 × 16 verkleinert)"""
    klein = img.scaled(16, 16, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
    return all(klein.pixelColor(x, y).alpha() == 0 for x in range(16) for y in range(16))


def emf_bild(blob: bytes, hoehe_px: int = 0, breite_px: int = 0) -> QImage | None:
    """Das EMF gezeichnet in ein Bild (Größe: ``breite_px``/``hoehe_px`` oder aus dem Rahmen, doppelt so fein wie 96 dpi, höchstens ``MAX_SEITE_PX``); ``None``, wenn unlesbar."""
    return _qimage(metafile_rgba(blob, breite_px, hoehe_px)) if ist_metafile_emf(blob) else None


def wmf_bild(blob: bytes, breite_px: int = 0, hoehe_px: int = 0) -> QImage | None:
    return _qimage(metafile_rgba(blob, breite_px, hoehe_px)) if ist_metafile_wmf(blob) else None


def _auf_zeichner(blob: bytes, p: QPainter, ziel: QRectF) -> bool:
    """Das Metafile in der Auflösung des Zeichners rastern lassen und passgenau in ``ziel`` legen. ``False``, wenn es nicht lesbar ist."""
    faktor, x, y, b, h = _ausgerichtet(p, ziel.x(), ziel.y(), max(1.0, ziel.width()), max(1.0, ziel.height()), 4.0)
    img = _qimage(metafile_rgba(blob, max(1, round(b * faktor)), max(1, round(h * faktor))))
    if img is None:
        return False
    p.drawImage(QRectF(x, y, b, h), img)
    return True


def emf_zeichnen(blob: bytes, p: QPainter, ziel: QRectF) -> bool:
    """Das EMF in ``ziel`` legen (der Kern zeichnet in der Auflösung des Zeichners). ``False``, wenn es kein lesbares EMF ist."""
    return ist_metafile_emf(blob) and _auf_zeichner(blob, p, ziel)


def wmf_zeichnen(blob: bytes, p: QPainter, ziel: QRectF) -> bool:
    return ist_metafile_wmf(blob) and _auf_zeichner(blob, p, ziel)
