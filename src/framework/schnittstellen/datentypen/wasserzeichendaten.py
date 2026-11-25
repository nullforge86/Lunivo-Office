"""Unveränderliche Angabe eines Wasserzeichens für die Oberfläche."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Wasserzeichenangabe:
    """Ein Wasserzeichen: Text oder Bild (Bild als Text kodiert); weitere Angaben als Schlüssel-Wert-Paare."""
    text: str = ""
    bild: str = ""
    weitere: tuple[tuple[str, str | int | float | bool], ...] = ()
