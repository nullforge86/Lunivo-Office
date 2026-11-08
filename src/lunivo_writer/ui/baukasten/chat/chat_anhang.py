"""Bild-Anhang im KI-Chat: ``AnhangChip`` (über dem Textfeld) und (Vorschau ``miniatur`` steht in ``chat_blase``).

Nur Darstellung: Rahmen und Farben kommen aus dem Thema (Karten-Arten ``anhang`` und ``miniatur``), Maße aus ``mass.py``. Der Chip kennt die Datei nur als Pfad
und meldet das Entfernen über ``entfernt``; geprüft und gesendet wird im Dienst."""
from __future__ import annotations

import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout

from lunivo_writer.ui.baukasten.basis.beschriftung import text_label
from lunivo_writer.ui.baukasten.chat.chat_blase import SymbolKnopf, miniatur
from lunivo_writer.ui.baukasten.basis.karte import als_karte
from lunivo_writer.ui.baukasten.basis.mass import ABSTAND_MITTEL, CHAT_ANHANG_MINIATUR, CHAT_ANHANG_ZEICHEN
from lunivo_writer.ui.baukasten.basis.texte import hinweis_label


def groesse_text(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    return f"{n / 1024:.0f} KB" if n < 1024 * 1024 else f"{n / 1024 / 1024:.1f} MB"


def name_gekuerzt(pfad: str, zeichen: int = CHAT_ANHANG_ZEICHEN) -> str:
    """Dateiname, in der Mitte gekürzt, die Endung bleibt sichtbar."""
    n = os.path.basename(pfad)
    if len(n) <= zeichen:
        return n
    stamm, endung = os.path.splitext(n)
    rest = max(3, zeichen - len(endung) - 1)
    return stamm[:rest] + "…" + endung


class AnhangChip(QFrame):
    """Zeile „Vorschau, Dateiname (gekürzt), Größe, ×“. ``entfernt`` kommt beim Klick auf ×."""
    entfernt = Signal()

    def __init__(self, pfad: str, groesse: int):
        super().__init__()
        als_karte(self, "anhang"); self.pfad = pfad
        h = QHBoxLayout(self); h.setContentsMargins(ABSTAND_MITTEL, 0, 0, 0); h.setSpacing(ABSTAND_MITTEL)
        h.addWidget(miniatur(pfad, CHAT_ANHANG_MINIATUR))
        self.name = text_label(name_gekuerzt(pfad)); self.name.setToolTip(pfad)
        h.addWidget(self.name, 1)
        h.addWidget(hinweis_label(groesse_text(groesse), umbruch=False, klein=True))
        self.weg = SymbolKnopf("x", "Anhang entfernen", self.entfernt.emit)
        h.addWidget(self.weg)
