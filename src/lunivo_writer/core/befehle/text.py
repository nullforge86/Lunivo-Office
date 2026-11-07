"""Kompatible Fassade für Zeichen-, Absatz- und Formatvorlagenbefehle."""
from __future__ import annotations

from lunivo_writer.core.befehle.text_zeichen import TextZeichenBefehle
from lunivo_writer.core.befehle.text_absatz import TextAbsatzBefehle
from lunivo_writer.core.befehle.text_vorlagen import TextVorlagenBefehle


class TextBefehle(TextZeichenBefehle, TextAbsatzBefehle, TextVorlagenBefehle):
    """Befehle des Bandes: Zeichen und Absatz; öffentliche Fassade."""
