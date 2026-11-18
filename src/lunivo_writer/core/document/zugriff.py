"""Zugriff auf Dokumentelemente anhand ihrer Pfade."""

from __future__ import annotations

from .model import Document, Frame, Paragraph, Table
from .position import Pfad


def behaelter(dok: Document, pfad: Pfad) -> list:
    """Die Blockliste, in der der Absatz mit dem Pfad ``pfad + (index,)`` steht."""
    liste = dok.sections[pfad[0]].content
    i = 1
    while i < len(pfad):
        b = liste[pfad[i]]
        if isinstance(b, Table):
            liste = b.table_rows[pfad[i + 1]].cells[pfad[i + 2]].content
            i += 3
        elif isinstance(b, Frame):
            liste = b.content
            i += 1
        else:
            raise ValueError(f"Pfad {pfad}: kein Behälter bei {i}")
    return liste


def absatz_bei(dok: Document, pfad: Pfad) -> Paragraph:
    b = behaelter(dok, pfad[:-1])[pfad[-1]]
    if not isinstance(b, Paragraph):
        raise ValueError(f"Pfad {pfad} ist kein Absatz")
    return b
