"""Der Zettel für die KI: die Steuerung der Oberfläche. Reicht die Abfrage an das Framework weiter."""
from __future__ import annotations

from framework.befehle.ki import zettel as befehle


def zettel_grenze() -> int:
    """Wie viele Zeichen der Zettel für die KI höchstens hat."""
    return int(befehle.ZETTEL_GRENZE)
