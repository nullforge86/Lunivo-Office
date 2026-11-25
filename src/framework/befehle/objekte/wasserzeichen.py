"""Wasserzeichen: Auswahllisten und Standardwerte des Einfügen-Fensters. Gezeichnet wird vom Kern; die Oberfläche erhält unveränderliche Werte."""
from __future__ import annotations

from core.objekte.textfelder.modell import wasserzeichen_daten as modell
from framework.schnittstellen.datentypen.wasserzeichendaten import Wasserzeichenangabe

VORGABEN: tuple[str, ...] = tuple(modell.VORGABEN)
GROESSEN: tuple[int, ...] = tuple(modell.GROESSEN)
ZOOMS: tuple[int, ...] = tuple(modell.ZOOMS)
HORIZONTAL: tuple[tuple[str, str], ...] = tuple(modell.HORIZONTAL)
VERTIKAL: tuple[tuple[str, str], ...] = tuple(modell.VERTIKAL)
FORMATE: tuple[tuple[int, str], ...] = tuple(modell.FORMATE)
STANDARD_FARBE: str = modell.STANDARD_FARBE


def da(w: Wasserzeichenangabe | None) -> bool:
    """Ob das Wasserzeichen etwas zeigt (Text oder Bild)."""
    return modell.da(None if w is None else {**dict(w.weitere), "text": w.text, "bild": w.bild})
