"""Vektorbilder aus Textprogrammen lesen: EMF und WMF (Windows-Metafiles) sowie SVG. Ausgewertet und gezeichnet wird vom Qt-freien Kern (``core/rendering/metafile.py``, ``svg.py``);
Qt ist hier nur noch der Behälter (``QImage``) für das fertig gerasterte Bild und die Fläche, auf die es gelegt wird. Gebraucht vom Qt-Backend (``adapter/qt``) und von
``editor/objekte/bilddaten.py``."""
from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QImage

from lunivo_writer.core.geometry import Rect
from lunivo_writer.core.rendering import metafile as MF
from lunivo_writer.core.rendering.metafile import MAX_SEITE_PX, ist_emf, ist_wmf, masse_px  # noqa: F401  (Namen der bisherigen Schnittstelle)
from lunivo_writer.editor.objekte import bilddaten as BD


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
    from lunivo_writer.editor.objekte.freie_bilder import bild_aus_daten
    if ist_emf(blob) or ist_wmf(blob):                        # Metafile: zuerst als Vektor; leer gezeichnet → eingebettetes Bitmap (Rückfall)
        img = _qimage(MF.metafile_rgba(blob)) or QImage()
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
    return _qimage(MF.metafile_rgba(blob, breite_px, hoehe_px)) if ist_emf(blob) else None


def wmf_bild(blob: bytes, breite_px: int = 0, hoehe_px: int = 0) -> QImage | None:
    return _qimage(MF.metafile_rgba(blob, breite_px, hoehe_px)) if ist_wmf(blob) else None


def _auf_zeichner(blob: bytes, p, ziel: QRectF, zeichne) -> bool:
    from lunivo_writer.oberflaeche.zeichnen.anzeige import kern_malen
    gelungen = [False]

    def los(z) -> None:
        gelungen[0] = zeichne(blob, z, Rect(ziel.x(), ziel.y(), ziel.width(), ziel.height()))
    kern_malen(p, ziel, los, rand=0.0)
    return gelungen[0]


def emf_zeichnen(blob: bytes, p, ziel: QRectF) -> bool:
    """Das EMF als Vektorzeichnung in ``ziel`` legen (der Kern zeichnet in der Auflösung des Zeichners). ``False``, wenn es kein lesbares EMF ist."""
    return ist_emf(blob) and MF._emf_kopf(blob) is not None and _auf_zeichner(blob, p, ziel, MF.emf_zeichnen)


def wmf_zeichnen(blob: bytes, p, ziel: QRectF) -> bool:
    return ist_wmf(blob) and MF._wmf_kopf(blob) is not None and _auf_zeichner(blob, p, ziel, MF.wmf_zeichnen)
