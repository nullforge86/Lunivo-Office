"""Anbindung der Oberfläche an ``core.text.ki_markdown`` über ``framework.anbindung.ki_markdown``: Ergebnisse als eigene Kopie der Oberfläche."""
from __future__ import annotations

from collections.abc import Sequence

import framework.anbindung.ki_markdown as _fw
from writer.werte import eigene_kopie


def hat_struktur(text: str) -> bool:
    """Wahr, wenn der Text Überschriften, Listen, Tabellen oder Hervorhebungen enthält. Sonst bleibt er einfacher Text (auch ohne Markdown-Deutung)."""
    return eigene_kopie(_fw.hat_struktur(text))


def markdown_bloecke(text: str) -> Sequence:
    """Einfaches Markdown (Überschriften, Aufzählungen, Nummerierungen, Fett, Kursiv, Code) als Absatzliste:"""
    return eigene_kopie(_fw.markdown_bloecke(text))


def normalisieren(text: str) -> str:
    """Einheitliche Vorbereitung: einzelne Zeilenumbrüche werden harte Umbrüche (außer vor Listen, Tabellen, Überschriften, Codeblöcken);"""
    return eigene_kopie(_fw.normalisieren(text))
