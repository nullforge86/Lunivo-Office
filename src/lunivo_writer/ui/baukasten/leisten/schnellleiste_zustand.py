"""Zustand der Schnellleiste neben dem gewählten SmartArt-Knoten: ob ⊖ fehlt und welche Knöpfe grau sind. Reine Funktionen, zeichnen nichts."""
from __future__ import annotations

_KANN = {"sa_form": ("kann_smartartFormEinfuegen",), "sa_bullet": ("kann_smartartAufzaehlung",),
         "sa_level": ("kann_smartartLevelErhoehen", "kann_smartartLevelReduzieren"),
         "sa_layout": ("kann_smartartKnotenWaehlen",), "sa_stil": ("kann_smartartKnotenWaehlen",)}


def ohne_minus(leiste, knoten) -> bool:
    """Bei gewähltem SmartArt-Knoten (Knopfsatz mit ``sa_form`` und ein Knotenrechteck) steht kein ⊖ (wie in der Vorlage)."""
    return knoten is not None and "sa_form" in tuple(leiste or ())


def knopf_aktiv(b, name: str) -> bool:
    """Ob der Knopf bedienbar ist (sonst grau). Unbekannte Knöpfe und fehlende Befehle gelten als aktiv; ``sa_level`` genügt eine Richtung."""
    namen = _KANN.get(name)
    if b is None or not namen:
        return True
    return any(bool(getattr(b, n)()) for n in namen if hasattr(b, n))
