"""Die gemeinsame Dateiliste aller Bild-Fenster (Einfügen, Bild ändern, Füllung, Wasserzeichen). Der Chat hat seine eigene (PNG, JPEG, WebP)."""
from __future__ import annotations

BILD_ENDUNGEN = ("png", "jpg", "jpeg", "jfif", "jpe", "gif", "bmp", "dib", "tif", "tiff", "webp", "svg", "svgz", "emf", "emz", "wmf", "wmz")
BILD_MUSTER = " ".join(f"*.{e}" for e in BILD_ENDUNGEN)
BILD_FILTER = f"Bilder ({BILD_MUSTER});;Alle Dateien (*)"
