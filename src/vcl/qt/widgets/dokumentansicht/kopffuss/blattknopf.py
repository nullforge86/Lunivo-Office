"""Ein Knopf, der auf dem Blatt liegt und eine Klappe öffnet – gebaut aus seiner Beschreibung (``writer.funktionen.kopffuss``) und dem Knopf-Baustein.

Das helle Aussehen auf dem Papier setzt der Halter des Knopfes mit ``papierleiste``; hier stehen nur Inhalt und Verhalten."""
from __future__ import annotations

from PySide6.QtWidgets import QToolButton

from vcl.qt.widgets.bausteine.farben import KOPFFUSS_PILLE_TEXT
from vcl.qt.widgets.bausteine.interaktion.knopf import werkzeugknopf


def blattknopf(beschreibung) -> QToolButton:
    """``beschreibung``: ein ``BlattKnopf`` (Text, Symbol, Hinweis). Ein Klick öffnet sofort die Klappe, die der Aufrufer anhängt."""
    k = werkzeugknopf("band_menue", beschreibung.text, symbol=beschreibung.symbol, symbolfarbe=KOPFFUSS_PILLE_TEXT,
                      name=beschreibung.text or beschreibung.hinweis, tooltip=beschreibung.hinweis)
    k.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
    return k
