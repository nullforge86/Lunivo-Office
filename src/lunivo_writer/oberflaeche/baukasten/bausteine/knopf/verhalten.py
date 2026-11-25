"""Verhalten des Knopfes: Aktion beim Klick, ob er aktiv ist, Tastenkürzel und ob er der Standardknopf ist – getrennt von Form und Inhalt."""
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QAbstractButton, QPushButton


def verbinden(knopf: QAbstractButton, aktion: Callable[[], object] | None = None, aktiv: bool = True, kuerzel: str = "",
              standard: bool = False, umschaltbar: bool = False, an: bool = False, hand: bool = False) -> QAbstractButton:
    """Verbindet die Aktion mit dem Klick (ohne den ``checked``-Wert des Signals), setzt Aktivierung, Kürzel, Umschalten und den Handzeiger."""
    if aktion is not None:
        knopf.clicked.connect(lambda _checked=False: aktion())
    knopf.setEnabled(aktiv)
    if umschaltbar:
        knopf.setCheckable(True)
        knopf.setChecked(an)
    if hand:
        knopf.setCursor(Qt.PointingHandCursor)
    if kuerzel:
        knopf.setShortcut(QKeySequence(kuerzel))
    if standard and isinstance(knopf, QPushButton):
        knopf.setDefault(True)
    return knopf
