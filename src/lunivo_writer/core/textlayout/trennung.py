"""Silbentrennung für den Zeilenumbruch, ohne Qt: Trennstellen langer Wörter aus den pyphen-Mustern. Die Stellen sind Zeichenstellen im Text des Absatzes;
der Text selbst bleibt unverändert (der Umbruch zeichnet den Trennstrich am Zeilenende, siehe ``zeilenumbruch``)."""
from __future__ import annotations

import re
from typing import Callable

_WORT = re.compile(r"[^\W\d_]{6,}", re.UNICODE)
_WOERTERBUECHER: dict = {}


def _woerterbuch(sprache: str):
    """pyphen-Wörterbuch (zwischengespeichert); ``None``, wenn pyphen oder die Sprache fehlt."""
    if sprache not in _WOERTERBUECHER:
        try:
            import pyphen
            wahl = sprache if sprache in pyphen.LANGUAGES else next((k for k in pyphen.LANGUAGES if k.split("_")[0] == sprache.replace("-", "_").split("_")[0]), None)
            _WOERTERBUECHER[sprache] = pyphen.Pyphen(lang=wahl, left=2, right=3) if wahl else None
        except ImportError:
            _WOERTERBUECHER[sprache] = None
    return _WOERTERBUECHER[sprache]


def trenner_fuer(sprache: str) -> Callable[[str], list[int]] | None:
    """Funktion ``text → Trennstellen`` (Zeichenstellen, vor denen eine Zeile enden darf) für die Sprache; ``None``, wenn es keine Muster gibt."""
    w = _woerterbuch(sprache or "de_DE")
    if w is None:
        return None

    def stellen(text: str) -> list[int]:
        aus: list[int] = []
        for m in _WORT.finditer(text):
            wort = m.group()
            if wort.isupper() or "\u00ad" in wort:
                continue
            aus.extend(m.start() + i for i in w.positions(wort))
        return aus
    return stellen
