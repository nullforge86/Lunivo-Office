"""Die Textsatz-Maschine der Anwendung: eine Stelle, die sagt, welche ``TextLayoutEngine`` Schriftmaße und Umbruch liefert."""
from __future__ import annotations

import os

from lunivo_writer.core.textlayout import TextLayoutEngine

_engine: TextLayoutEngine | None = None


def standard_engine() -> TextLayoutEngine:
    """Die Engine für Maße außerhalb des Seitenlaufs: Qt-Umsetzung; mit ``LUNIVO_TEXTSATZ=hb`` die Qt-freie (HarfBuzz/FreeType). Die Maße beider stimmen auf 0,5 % überein
    (``tests/architektur/test_textsatz_hb.py``), der Seitenlauf selbst setzt weiter mit Qt."""
    global _engine
    if _engine is None:
        if os.environ.get("LUNIVO_TEXTSATZ", "").lower() == "hb":
            from lunivo_writer.core.textlayout.hb_engine import HarfBuzzEngine
            _engine = HarfBuzzEngine()
        else:
            from lunivo_writer.adapter.qt.textlayout import QtTextLayoutEngine
            _engine = QtTextLayoutEngine()
    return _engine


def engine_setzen(engine: TextLayoutEngine | None) -> None:
    """Andere Engine einsetzen (Tests, Qt-freie Umsetzung); ``None`` = Standard."""
    global _engine
    _engine = engine
