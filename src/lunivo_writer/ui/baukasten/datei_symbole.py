"""Einheitliche Lucide-Symbole für Dateien, ohne Abhängigkeit vom Desktop-Theme."""
from __future__ import annotations

import os

from PySide6.QtGui import QIcon

from lunivo_writer.ui.widgets import icons


def icon_namen(name: str) -> list[str]:
    """Liefert den Lucide-Namen für die Dateiendung und einen stabilen Rückfall."""
    ext = os.path.splitext(os.path.basename(name))[1].lower()
    if name.startswith(".") and name.count(".") == 1:
        ext = name.lower()
    if ext == ".pdf":
        return ["file-text", "file"]
    if ext in {".doc", ".docx", ".odt", ".rtf", ".txt", ".md"}:
        return ["file-text", "file"]
    if ext in {".xls", ".xlsx", ".ods", ".csv"}:
        return ["table", "file"]
    if ext in {".ppt", ".pptx", ".odp"}:
        return ["presentation", "file"]
    if ext in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg"}:
        return ["image", "file"]
    return ["file"]


def datei_symbol(name: str) -> QIcon:
    """Dateisymbol aus Lucide; gleichbleibend auf allen Desktop-Umgebungen."""
    return icons.icon(icon_namen(name)[0], 24)
