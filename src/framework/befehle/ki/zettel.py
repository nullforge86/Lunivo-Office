"""Der Zettel für die KI (was sie über den Schreibenden wissen soll): seine Grenze. Die Oberfläche erhält einen unveränderlichen Wert."""
from __future__ import annotations

from framework.ki.dienst import ki_konfiguration as konfiguration

ZETTEL_GRENZE: int = konfiguration.ZETTEL_GRENZE          # höchstens so viele Zeichen
