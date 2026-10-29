"""Einheitliche Lucide-Symbole für Dateien, ohne Abhängigkeit vom Desktop-Theme."""
from __future__ import annotations

import os

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QFont, QIcon, QPainter, QPixmap

from lunivo_writer.ui.widgets import icons


def icon_namen(name: str) -> list[str]:
    """Liefert ein formatspezifisches Lucide-Symbol und einen stabilen Rückfall."""
    ext = os.path.splitext(os.path.basename(name))[1].lower()
    if name.startswith(".") and name.count(".") == 1:
        ext = name.lower()
    symbol = {
        # Textdokumente und Austauschformate
        ".doc": "file-text", ".docx": "file-text", ".odt": "file-type",
        ".rtf": "file-pen-line", ".txt": "file-text", ".md": "file-code",
        ".pdf": "file-type",
        # Tabellen und Präsentationen
        ".xls": "file-spreadsheet", ".xlsx": "file-chart-column",
        ".ods": "table", ".csv": "table",
        ".ppt": "presentation", ".pptx": "file-chart-column-increasing",
        ".odp": "presentation",
        # Medien, Code und Archive
        ".png": "file-image", ".jpg": "file-image", ".jpeg": "file-image",
        ".gif": "file-image", ".bmp": "file-image", ".webp": "file-image",
        ".svg": "file-code", ".mp3": "file-music", ".wav": "file-music",
        ".mp4": "file-video-camera", ".mov": "file-video-camera",
        ".zip": "file-archive", ".7z": "file-archive", ".rar": "file-archive",
        ".py": "file-code", ".js": "file-code", ".html": "file-code",
        ".json": "file-braces", ".xml": "file-code",
    }.get(ext, "file")
    return [symbol, "file"]


def datei_symbol(name: str) -> QIcon:
    """Lucide-Dateisymbol mit kleiner, formatbezogener Kennzeichnung."""
    ext = os.path.splitext(os.path.basename(name))[1].lower()
    if name.startswith(".") and name.count(".") == 1:
        ext = name.lower()
    symbol = icon_namen(name)[0]
    kennung = {
        ".doc": ("DOC", "#2b579a"), ".docx": ("DOCX", "#2b579a"),
        ".odt": ("ODT", "#4b8b3b"), ".rtf": ("RTF", "#687b91"),
        ".txt": ("TXT", "#687b91"), ".md": ("MD", "#687b91"),
        ".pdf": ("PDF", "#d73535"),
        ".xls": ("XLS", "#217346"), ".xlsx": ("XLSX", "#217346"),
        ".ods": ("ODS", "#4b8b3b"), ".csv": ("CSV", "#217346"),
        ".ppt": ("PPT", "#c43e1c"), ".pptx": ("PPTX", "#c43e1c"),
        ".odp": ("ODP", "#c43e1c"),
        ".png": ("PNG", "#8b5cf6"), ".jpg": ("JPG", "#8b5cf6"),
        ".jpeg": ("JPG", "#8b5cf6"), ".gif": ("GIF", "#8b5cf6"),
        ".bmp": ("BMP", "#8b5cf6"), ".webp": ("WEBP", "#8b5cf6"),
        ".svg": ("SVG", "#8b5cf6"),
        ".zip": ("ZIP", "#8a6d3b"), ".7z": ("7Z", "#8a6d3b"),
        ".rar": ("RAR", "#8a6d3b"),
    }.get(ext, (ext.lstrip(".").upper()[:4] or "DATEI", "#687b91"))

    # Das Grundpiktogramm kommt weiter aus Lucide; die Marke trägt nur die
    # Dateiendung und macht ansonsten gleiche Dateitypen schnell erkennbar.
    dpr = 2
    bild = QPixmap(64, 64)
    bild.fill(Qt.transparent)
    bild.setDevicePixelRatio(dpr)
    p = QPainter(bild)
    p.setRenderHint(QPainter.Antialiasing)
    p.drawPixmap(QRectF(0, 0, 32, 32), icons.icon(symbol, 32).pixmap(32, 32), QRectF(0, 0, 32, 32))
    text, farbe = kennung
    schrift = QFont()
    schrift.setBold(True)
    schrift.setPointSizeF(6.5 if len(text) > 3 else 7.0)
    p.setFont(schrift)
    marke = QRectF(2, 20, 28, 11)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(farbe))
    p.drawRoundedRect(marke, 2, 2)
    p.setPen(Qt.white)
    p.drawText(marke, Qt.AlignCenter, text)
    p.end()
    return QIcon(bild)
