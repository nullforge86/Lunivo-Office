"""Darstellung — wie eine Seite ihre Widgets für das Designsystem kennzeichnet, ohne selbst zu gestalten.

``rolle(widget, "hinweis")`` setzt die Eigenschaft ``rolle`` (und weitere wie ``status=...``); das Aussehen steht allein in ``dashboard_regeln.py``.
``farbflaeche`` ist die einzige zugelassene Ausnahme: eine vom Menschen gewählte Farbe (z. B. der Papierton der Lesehilfe) kann kein festes Stylesheet
sein, deshalb setzt dieses Modul sie — und kein anderes."""
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe
from vcl.qt.widgets.bausteine.farben.farben import AUSWAHL_OBJEKTTEXT
from vcl.qt.widgets.bausteine.abstaende.mass import RADIUS_FELD, RADIUS_STUFE



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


def farbknopf(knopf: QWidget, farbe: str) -> QWidget:
    """Knopf, der eine vom Menschen gewählte Farbe zeigt (Farbfeld der Eigenen Farben) — Rand und Rundung aus ``mass``."""
    knopf.setStyleSheet(f"QPushButton {{ background: {farbe}; border: 1px solid palette(mid); border-radius: {RADIUS_FELD}px; }}")
    return knopf


def stufe_mit_farbe(label: QWidget, farbe: str) -> QWidget:
    """Runde Stufe (Initialen eines Autors) auf einer Farbe aus Daten, weiße fette Schrift."""
    label.setStyleSheet(f"background: {farbe}; color: {Farbe.WEISS}; font-weight: bold; border-radius: {RADIUS_STUFE}px;")
    return label


def knoten_eingabe(feld: QWidget) -> QWidget:
    """Eingabefeld über einem SmartArt-Knoten: Papiergrund, Symbolschrift, Rand in der Auswahlfarbe."""
    feld.setStyleSheet(f"QLineEdit {{ background: {Farbe.PAPIER}; color: {Farbe.SYMBOL}; border: 1px solid palette(highlight); }}")
    return feld


def objekttext_eingabe(feld: QWidget, grund: str, farbe: str) -> QWidget:
    """Schreibfeld direkt im Objekt (WordArt, Textfeld): Grund und Schrift aus dem Objekt, ohne Rand, Auswahl in der Objekttext-Farbe."""
    feld.setStyleSheet(f"QTextEdit {{ background: {grund}; color: {farbe}; border: none; selection-background-color: {AUSWAHL_OBJEKTTEXT}; }}")
    return feld
