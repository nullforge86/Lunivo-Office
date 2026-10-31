"""Protokoll: eine Logdatei im Zwischenspeicher-Ordner, damit Fehler beim Laden, Speichern und Prüfen nicht still verschwinden.

Module holen sich ``logging.getLogger("lunivo.<bereich>")``; ``einrichten()`` wird einmal beim Programmstart aufgerufen.
Ohne Aufruf (z. B. in Tests) schreibt nichts in eine Datei.
"""
from __future__ import annotations

import logging
import logging.handlers
import os
import sys

from lunivo_writer.plattform import pfade

NAME = "lunivo"
DATEI = "lunivo.log"
_MAX_BYTES = 512 * 1024
_SICHERUNGEN = 2


def logdatei() -> str:
    d = os.path.join(pfade.cache_dir(), "logs")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, DATEI)


def einrichten(stufe: int = logging.INFO) -> str | None:
    """Logdatei einrichten und nicht abgefangene Fehler protokollieren; liefert den Pfad (oder None, wenn nicht schreibbar)."""
    log = logging.getLogger(NAME)
    log.setLevel(stufe)
    bestehend = next((h for h in log.handlers if isinstance(h, logging.handlers.RotatingFileHandler)), None)
    if bestehend is not None:
        return bestehend.baseFilename
    try:
        pfad = logdatei()
        h = logging.handlers.RotatingFileHandler(pfad, maxBytes=_MAX_BYTES, backupCount=_SICHERUNGEN, encoding="utf-8")
    except OSError:
        return None
    h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    log.addHandler(h)
    _alt = sys.excepthook

    def _haken(art, wert, spur):
        log.critical("Nicht abgefangener Fehler", exc_info=(art, wert, spur))
        _alt(art, wert, spur)

    sys.excepthook = _haken
    return pfad
