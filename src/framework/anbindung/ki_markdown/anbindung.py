"""Anbindung an ``core.text.ki_markdown``: reine Daten und Rechenfunktionen des Kerns, Ergebnisse als feste Kopie."""
from __future__ import annotations

from collections.abc import Sequence

import core.text as _k
from framework.anbindung import fest


def hat_struktur(text: str) -> bool:
    """Wahr, wenn der Text Überschriften, Listen, Tabellen oder Hervorhebungen enthält. Sonst bleibt er einfacher Text (auch ohne Markdown-Deutung)."""
    return fest(_k.hat_struktur(text))


def markdown_bloecke(text: str) -> Sequence:
    """Einfaches Markdown (Überschriften, Aufzählungen, Nummerierungen, Fett, Kursiv, Code) als Absatzliste:"""
    return fest(_k.markdown_bloecke(text))


def normalisieren(text: str) -> str:
    """Einheitliche Vorbereitung: einzelne Zeilenumbrüche werden harte Umbrüche (außer vor Listen, Tabellen, Überschriften, Codeblöcken);"""
    return fest(_k.normalisieren(text))
