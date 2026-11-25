"""Darstellung — wie eine Seite ihre Widgets für das Designsystem kennzeichnet, ohne selbst zu gestalten.

``rolle(widget, "hinweis")`` setzt die Eigenschaft ``rolle`` (und weitere wie ``status=...``); das Aussehen steht allein in ``dashboard_regeln.py``.
``farbflaeche`` ist die einzige zugelassene Ausnahme: eine vom Menschen gewählte Farbe (z. B. der Papierton der Lesehilfe) kann kein festes Stylesheet
sein, deshalb setzt dieses Modul sie — und kein anderes."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget



def eigenschaft(widget: QWidget, **werte) -> QWidget:
    for name, wert in werte.items():
        widget.setProperty(name, wert)
    stil = widget.style()
    stil.unpolish(widget); stil.polish(widget)                 # eine spätere Änderung gilt auch für ein schon angezeigtes Widget
    return widget


def rolle(widget: QWidget, name: str, **werte) -> QWidget:
    return eigenschaft(widget, rolle=name, **werte)


def farbflaeche(widget: QWidget, hintergrund: str, schrift: str) -> QWidget:
    """Hintergrund und Schrift aus Benutzerdaten (Ausnahme, siehe oben)."""
    widget.setStyleSheet(f"background: {hintergrund}; color: {schrift};")
    return widget


def grundschrift(wurzel: QWidget) -> QWidget:
    """Kennzeichnet die Wurzel einer Dashboard-Seite (Eigenschaft ``dashboard``): alle Bedienelemente darunter erhalten die Grundschrift
    ``mass.SCHRIFT_DASHBOARD_TEXT``. Die Regel steht in ``dashboard_regeln.py``; hier wird nur gekennzeichnet."""
    wurzel.setProperty("dashboard", True)
    return wurzel


def zahlfeld_ohne_pfeilknoepfe(feld: QWidget) -> QWidget:
    """Zahlfeld mit schmalem Innenrand und ohne gezeichnete Auf-/Ab-Knöpfe (Stil der Höhenfelder im Band) — der eine Ort dieses Stils."""
    feld.setStyleSheet("QDoubleSpinBox { padding: 0px 3px; } QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 0px; border: none; }")
    return feld


def schriftfarbe(widget: QWidget, farbe: str) -> QWidget:
    """Schriftfarbe, die erst zur Laufzeit feststeht (Name aus Daten, z. B. der Titel einer Panel-Beschreibung) — zweite zugelassene Ausnahme neben ``farbflaeche``."""
    widget.setStyleSheet(f"color: {farbe};")
    return widget
