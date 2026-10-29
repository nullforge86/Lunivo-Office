"""Einheitliche Lucide-Symbole für Dateien, ohne Abhängigkeit vom Desktop-Theme."""
from __future__ import annotations

import os

from PySide6.QtGui import QIcon

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
    """Dateisymbol aus Lucide; gleichbleibend auf allen Desktop-Umgebungen."""
    return icons.icon(icon_namen(name)[0], 24)
