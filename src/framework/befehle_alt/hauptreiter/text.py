"""Kompatible Fassade für Zeichen-, Absatz- und Formatvorlagenbefehle."""
from __future__ import annotations

from framework.befehle_alt.hauptreiter.text_zeichen import TextZeichenBefehle
from framework.befehle_alt.hauptreiter.text_absatz import TextAbsatzBefehle
from framework.befehle_alt.hauptreiter.text_vorlagen import TextVorlagenBefehle
from framework.befehle_alt.hauptreiter.text_absatz import ZEILENABSTAENDE  # noqa: F401


class TextBefehle(TextZeichenBefehle, TextAbsatzBefehle, TextVorlagenBefehle):
    """Befehle des Bandes: Zeichen und Absatz; öffentliche Fassade."""
