"""Anbindung der Oberfläche an ``framework.serienbriefe.formate``: Funktionen mit derselben Signatur, Werte als unveränderliche Kopie."""
from __future__ import annotations

import framework.serienbriefe as _fw


def etiketten_boegen() -> tuple[str, ...]:
    return _fw.etiketten_boegen()


def umschlag_formate() -> tuple[str, ...]:
    return _fw.umschlag_formate()
