from __future__ import annotations
from PySide6.QtGui import QColor

from vcl.qt.widgets.bausteine.farben.grundfarben import Farbe


def _monochrom(basis: str) -> list[str]:
    """Sechs Töne einer Farbe, vom dunklen zum hellen."""
    c = QColor(basis)
    return [c.darker(f).name() for f in (170, 130)] + [c.name()] + [c.lighter(f).name() for f in (130, 165, 205)]


# Farbschemen (Diagrammstile ▸ Farben): Gruppe → [(Name, sechs Farben)]
FARBSCHEMEN = [
    ("Farbig", [(name, list(farben)) for name, farben in Farbe.DIAGRAMM_FARBIG]),
    ("Monochrom", [(f"Monochrom {i + 1}", _monochrom(c)) for i, c in enumerate(Farbe.DIAGRAMM_MONOCHROM)]),
]


def farbschemen_gruppen() -> list[tuple[str, list[tuple[str, list[str]]]]]:
    """Die Gruppen „Farbig“ und „Monochrom“ mit ihren Farbzeilen (Kopie von ``FARBSCHEMEN``)."""
    return [(g, [(n, list(f)) for n, f in z]) for g, z in FARBSCHEMEN]


def farbschemen_flach() -> list[tuple[str, list[str]]]:
    """Alle Farbzeilen hintereinander (Nummer = Argument von ``diagrammFarben``)."""
    return [(n, list(f)) for _g, z in FARBSCHEMEN for n, f in z]
