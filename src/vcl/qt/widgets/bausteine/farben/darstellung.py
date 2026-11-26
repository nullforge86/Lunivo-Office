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


def papierfeld(feld: QWidget) -> QWidget:
    """Textfeld, das auf dem weißen Blatt liegt (Kopf- und Fußzeile bearbeiten): Papier, schwarze Schrift, kein Rahmen – unabhängig vom Thema,
    weil das Blatt selbst nicht dem Thema folgt."""
    from vcl.qt.widgets.bausteine.farben.farben import KOPFFUSS_AUSWAHL, KOPFFUSS_AUSWAHL_TEXT, KOPFFUSS_PAPIER, KOPFFUSS_TEXT
    feld.setStyleSheet(f"QPlainTextEdit {{ background: {KOPFFUSS_PAPIER}; color: {KOPFFUSS_TEXT}; border: none; border-radius: 0px; padding: 0px;"
                       f" selection-background-color: {KOPFFUSS_AUSWAHL}; selection-color: {KOPFFUSS_AUSWAHL_TEXT}; }}")
    return feld


def papierleiste(leiste: QWidget) -> QWidget:
    """Leiste mit Knöpfen, die auf dem weißen Blatt liegt (Seitenzahl-Knöpfe der Kopf- und Fußzeile): helle Knöpfe mit dunkler Schrift, unabhängig vom Thema."""
    from vcl.qt.widgets.bausteine.farben.farben import KOPFFUSS_KNOPF_GRUND, KOPFFUSS_KNOPF_GRUND_UEBER, KOPFFUSS_PILLE_RAND, KOPFFUSS_PILLE_TEXT
    from vcl.qt.widgets.bausteine.abstaende.mass import PADDING_BLATTPILLE, RADIUS_BLATTPILLE
    leiste.setStyleSheet(f"QToolButton {{ background: {KOPFFUSS_KNOPF_GRUND}; color: {KOPFFUSS_PILLE_TEXT}; border: 1px solid {KOPFFUSS_PILLE_RAND};"
                         f" border-radius: {RADIUS_BLATTPILLE}px; padding: {PADDING_BLATTPILLE}; }}"
                         f" QToolButton:hover {{ background: {KOPFFUSS_KNOPF_GRUND_UEBER}; }} QToolButton::menu-indicator {{ image: none; width: 0px; }}")
    return leiste


def papierpanel(menue: QWidget, inhalt: QWidget, hauptknopf: QWidget) -> QWidget:
    """Aufklappfeld, das zu den Knöpfen auf dem weißen Blatt gehört (Seitenzahl einfügen): weißer Grund, dunkle Schrift, helle Kacheln, die gewählte
    hellblau, der Hauptknopf (OK) blau – unabhängig vom Thema, wie die Leiste, aus der es aufklappt."""
    from vcl.qt.widgets.bausteine.farben.farben import (KOPFFUSS_AUSWAHL, KOPFFUSS_AUSWAHL_TEXT, KOPFFUSS_KACHEL_GEWAEHLT, KOPFFUSS_KACHEL_GRUND,
                                                        KOPFFUSS_KNOPF_RAND, KOPFFUSS_KNOPF_TEXT, KOPFFUSS_OPTION_RAND, KOPFFUSS_PAPIER)
    from vcl.qt.widgets.bausteine.abstaende.mass import (PADDING_KOPFFUSS_ABSATZKNOPF, PADDING_KOPFFUSS_PANELKNOPF, PADDING_KOPFFUSS_PANELTASTE,
                                                         RADIUS_FELD, RADIUS_KLEIN)
    inhalt.setObjectName("kfPanel")
    hauptknopf.setObjectName("kfPanelOk")
    menue.setStyleSheet(f"QMenu {{ background: {KOPFFUSS_PAPIER}; border: 1px solid {KOPFFUSS_KNOPF_RAND}; }}")
    inhalt.setStyleSheet(
        f"QWidget#kfPanel {{ background: {KOPFFUSS_PAPIER}; color: {KOPFFUSS_KNOPF_TEXT}; }}"
        f" #kfPanel QLabel, #kfPanel QRadioButton {{ color: {KOPFFUSS_KNOPF_TEXT}; background: transparent; }}"
        f" #kfPanel QComboBox {{ background: {KOPFFUSS_PAPIER}; color: {KOPFFUSS_KNOPF_TEXT}; border: 1px solid {KOPFFUSS_KNOPF_RAND};"
        f" border-radius: {RADIUS_KLEIN}px; padding: {PADDING_KOPFFUSS_ABSATZKNOPF}; }}"
        f" #kfPanel QComboBox QAbstractItemView {{ background: {KOPFFUSS_PAPIER}; color: {KOPFFUSS_KNOPF_TEXT};"
        f" selection-background-color: {KOPFFUSS_KACHEL_GEWAEHLT}; selection-color: {KOPFFUSS_KNOPF_TEXT}; }}"
        f" #kfPanel QToolButton {{ background: {KOPFFUSS_KACHEL_GRUND}; color: {KOPFFUSS_KNOPF_TEXT}; border: 1px solid transparent;"
        f" padding: {PADDING_KOPFFUSS_PANELKNOPF}; }}"
        f" #kfPanel QToolButton:checked {{ background: {KOPFFUSS_KACHEL_GEWAEHLT}; }}"
        f" #kfPanel QToolButton:hover {{ border: 1px solid {KOPFFUSS_KNOPF_RAND}; }}"
        f" #kfPanel QRadioButton::indicator {{ width: {RADIUS_FELD + RADIUS_FELD}px; height: {RADIUS_FELD + RADIUS_FELD}px;"
        f" border: 1px solid {KOPFFUSS_OPTION_RAND}; border-radius: {RADIUS_FELD + 1}px; background: {KOPFFUSS_PAPIER}; }}"
        f" #kfPanel QRadioButton::indicator:checked {{ background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, stop:0 {KOPFFUSS_AUSWAHL},"
        f" stop:0.5 {KOPFFUSS_AUSWAHL}, stop:0.6 {KOPFFUSS_PAPIER}, stop:1 {KOPFFUSS_PAPIER}); border-color: {KOPFFUSS_AUSWAHL}; }}"
        f" #kfPanel QToolButton#kfPanelOk {{ background: {KOPFFUSS_AUSWAHL}; color: {KOPFFUSS_AUSWAHL_TEXT}; border: none;"
        f" border-radius: {RADIUS_KLEIN}px; padding: {PADDING_KOPFFUSS_PANELTASTE}; }}")
    return menue


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


def knoten_zeilen_eingabe(feld: QWidget) -> QWidget:
    """Mehrzeiliges Eingabefeld über den Aufzählungspunkten eines SmartArt-Knotens: wie ``knoten_eingabe``."""
    feld.setStyleSheet(f"QPlainTextEdit {{ background: {Farbe.PAPIER}; color: {Farbe.SYMBOL}; border: 1px solid palette(highlight); }}")
    return feld


def objekttext_eingabe(feld: QWidget, grund: str, farbe: str) -> QWidget:
    """Schreibfeld direkt im Objekt (WordArt, Textfeld): Grund und Schrift aus dem Objekt, ohne Rand, Auswahl in der Objekttext-Farbe."""
    feld.setStyleSheet(f"QTextEdit {{ background: {grund}; color: {farbe}; border: none; selection-background-color: {AUSWAHL_OBJEKTTEXT}; }}")
    return feld
