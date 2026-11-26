"""Kopf- und Fußzeile eines Abschnitts als Text setzen und die Seitenzahl einfügen: ordnet die Bedienung den Framework-Befehlen zu."""
from __future__ import annotations

from framework.befehle import kopffuss as _befehle


def kopffuss_zeile_setzen(kennung: int, abschnitt: int, zeile: str, text: str, ausrichtung: str) -> bool:
    """Die Zeile (``header``, ``footer``, ``first_header`` oder ``first_footer``) des Abschnitts durch Text mit Ausrichtung ersetzen."""
    return _befehle.zeile_setzen(kennung, abschnitt, zeile, text, ausrichtung)


def seitenzahl_einfuegen(kennung: int, abschnitt: int) -> bool:
    """Die Seitenzahl in die Fußzeile des Abschnitts setzen (leere Fußzeile: mittig; sonst angehängt)."""
    return _befehle.seitenzahl_einfuegen(kennung, abschnitt)
