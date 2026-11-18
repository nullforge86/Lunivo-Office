"""Die Textsatz-Maschine der Anwendung: eine Stelle, die sagt, welche ``TextLayoutEngine`` Schriftmaße und Umbruch liefert."""
from __future__ import annotations

from lunivo_writer.core.textlayout import TextLayoutEngine

_engine: TextLayoutEngine | None = None


def standard_engine() -> TextLayoutEngine:
    """Die Qt-freie HarfBuzz/FreeType-Engine für Kernlayout und Modellrendering."""
    global _engine
    if _engine is None:
        from lunivo_writer.core.textlayout.hb_engine import HarfBuzzEngine
        _engine = HarfBuzzEngine()
    return _engine


def engine_setzen(engine: TextLayoutEngine | None) -> None:
    """Andere Engine einsetzen (Tests, Qt-freie Umsetzung); ``None`` = Standard."""
    global _engine
    _engine = engine
