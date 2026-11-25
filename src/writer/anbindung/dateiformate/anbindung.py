"""Anbindung der Oberfläche an ``framework.dokumentverwaltung.dateizugriff.dateiformate``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.dokumentverwaltung.dateizugriff as _fw
from writer.werte import unveraenderlich


def open_filter():
    return unveraenderlich(_fw.OPEN_FILTER)


def pdf_filter():
    return unveraenderlich(_fw.PDF_FILTER)


def save_filters():
    return unveraenderlich(_fw.SAVE_FILTERS)


def ext(path: str) -> str:
    return _fw.ext(path)
