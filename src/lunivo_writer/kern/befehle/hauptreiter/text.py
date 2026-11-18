"""Kompatible Fassade für Zeichen-, Absatz- und Formatvorlagenbefehle."""
from __future__ import annotations

from lunivo_writer.kern.befehle.hauptreiter.text_zeichen import TextZeichenBefehle
from lunivo_writer.kern.befehle.hauptreiter.text_absatz import TextAbsatzBefehle
from lunivo_writer.kern.befehle.hauptreiter.text_vorlagen import TextVorlagenBefehle
from lunivo_writer.kern.befehle.hauptreiter.text_absatz import ZEILENABSTAENDE  # noqa: F401


class TextBefehle(TextZeichenBefehle, TextAbsatzBefehle, TextVorlagenBefehle):
    """Befehle des Bandes: Zeichen und Absatz; öffentliche Fassade."""
