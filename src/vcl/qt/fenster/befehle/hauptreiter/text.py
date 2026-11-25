"""Kompatible Fassade für Zeichen-, Absatz- und Formatvorlagenbefehle."""
from __future__ import annotations

from vcl.qt.fenster.befehle.hauptreiter.text_zeichen import TextZeichenBefehle
from vcl.qt.fenster.befehle.hauptreiter.text_absatz import TextAbsatzBefehle
from vcl.qt.fenster.befehle.hauptreiter.text_vorlagen import TextVorlagenBefehle
from vcl.qt.fenster.befehle.hauptreiter.text_absatz import ZEILENABSTAENDE  # noqa: F401


class TextBefehle(TextZeichenBefehle, TextAbsatzBefehle, TextVorlagenBefehle):
    """Befehle des Bandes: Zeichen und Absatz; öffentliche Fassade."""
