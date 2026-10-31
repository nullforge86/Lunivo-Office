"""Lokale, vollständige Dateityp-Symbole aus der zentralen Iconsammlung."""
from __future__ import annotations

import os

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QIcon, QImage, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from lunivo_writer.core import paths


_DATEITYP = {
    ".doc": "docx", ".docx": "docx", ".docm": "docx",
    ".pdf": "pdf",
    ".odt": "rtf", ".rtf": "rtf", ".epub": "rtf",
    ".txt": "txt", ".md": "code",
    ".xls": "xlsx", ".xlsx": "xlsx", ".ods": "spreadsheet", ".csv": "csv",
    ".ppt": "pptx", ".pptx": "pptx", ".odp": "presentation",
    ".png": "photo", ".jpg": "photo", ".jpeg": "photo", ".gif": "photo",
    ".bmp": "photo", ".webp": "photo", ".svg": "photo",
    ".mp3": "audio", ".wav": "audio", ".mp4": "video", ".mov": "video",
    ".zip": "zip", ".7z": "archive", ".rar": "archive", ".tar": "archive",
    ".py": "code", ".js": "code", ".xml": "xml", ".json": "code",
}


def icon_namen(name: str) -> list[str]:
    """Liefert den passenden lokalen Dateityp und den generischen Rückfall."""
    ext = os.path.splitext(os.path.basename(name))[1].lower()
    if name.startswith(".") and name.count(".") == 1:
        ext = name.lower()
    symbol = _DATEITYP.get(ext, "genericfile")
    return [symbol, "genericfile"]


def datei_symbol(name: str) -> QIcon:
    """Rendert ein vollständiges farbiges Dateiblatt aus einem gebündelten SVG."""
    ordner = os.path.join(paths.ASSETS, "icons", "filetypes")
    for symbol in icon_namen(name):
        pfad = os.path.join(ordner, f"{symbol}.svg")
        try:
            with open(pfad, "rb") as fh:
                renderer = QSvgRenderer(QByteArray(fh.read()))
        except OSError:
            continue
        if not renderer.isValid():
            continue
        ratio = 2
        px = 48
        bild = QImage(px * ratio, px * ratio, QImage.Format_ARGB32_Premultiplied)
        bild.fill(Qt.transparent)
        p = QPainter(bild)
        p.setRenderHint(QPainter.Antialiasing)
        renderer.render(p, QRectF(0, 0, px * ratio, px * ratio))
        p.end()
        bild.setDevicePixelRatio(ratio)
        icon = QIcon()
        icon.addPixmap(QPixmap.fromImage(bild))
        return icon
    return QIcon()
