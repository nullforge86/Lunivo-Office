"""Die Klappen an den Knöpfen auf dem Blatt (Kopf- und Fußzeile): füllt ein Menü aus den Einträgen von ``writer`` (``blattklappen``) und
meldet die Wahl an den Bearbeiter. Jede Klappe wird beim Öffnen neu gefüllt, damit Haken und Startwert zum Dokument passen."""
from __future__ import annotations

from PySide6.QtWidgets import QLabel, QSpinBox, QWidget, QWidgetAction

from writer.funktionen.kopffuss import blattklappen as K, blatttexte as T
from vcl.qt.widgets.bausteine.abstaende import KOPFFUSS_NUMMER_MAX
from vcl.qt.widgets.bausteine.zustaende.geruest import reihe
from vcl.qt.widgets.menues.dropdown import MenueListe


def neu_aufbauen(m: MenueListe, bearbeiter) -> None:
    """„Seitenzahl neu aufbauen“: Startwert der Seitennummerierung und „Nummerierung fortsetzen“."""
    m.clear()
    zeile = QWidget()
    h = reihe("popup", zeile)
    h.addWidget(QLabel(T.NUMMERIERUNG + ":"))
    feld = QSpinBox()
    feld.setRange(1, KOPFFUSS_NUMMER_MAX)
    feld.setValue(bearbeiter.erste_nummer())
    feld.setAccessibleName(T.NUMMERIERUNG)
    feld.editingFinished.connect(lambda: bearbeiter.start_setzen(feld.value()))
    h.addWidget(feld)
    h.addStretch(1)
    aktion = QWidgetAction(m)
    aktion.setDefaultWidget(zeile)
    m.addAction(aktion)
    m.eintrag(T.NUMMERIERUNG_FORTSETZEN, lambda: bearbeiter.start_setzen(0), aktiv=bearbeiter.nummerierung_beginnt_neu())


def zahlenformat(m: MenueListe, bearbeiter) -> None:
    """„Seitenzahlenformat“: die Zahlenarten, die geltende mit Haken."""
    m.clear()
    aktuell = bearbeiter.seitenzahlenformat()
    for schluessel, text in K.FORMATE:
        m.eintrag(text, lambda s=schluessel: bearbeiter.seitenzahlenformat_setzen(s), haken=schluessel == aktuell)


def loeschen(m: MenueListe, bearbeiter) -> None:
    """„Seitenzahl löschen“: wo die Seitenzahl entfernt wird."""
    m.clear()
    for art, text in K.LOESCHEN:
        m.eintrag(text, lambda a=art: bearbeiter.seitenzahl_loeschen(a))


def absatz(m: MenueListe, aktionen: dict) -> None:
    """Die Klappe des Absatz-Symbols; ``aktionen``: Schlüssel des Eintrags → Aufruf."""
    m.clear()
    for schluessel, text in K.ABSATZ:
        m.eintrag(text, aktionen[schluessel])


FUELLER = {"neu": neu_aufbauen, "format": zahlenformat, "loeschen": loeschen}       # Schlüssel des Knopfes → seine Klappe
