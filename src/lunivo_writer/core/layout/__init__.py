"""Layout ohne Qt: Absatzzeilen, Objektpositionen und Seitenumbruch des Dokumentenmodells.

Maßgeblich ist ``LayoutEngine`` (``seitenlayout.py``) über dem Modell aus ``core.document.Dokument``; ``LayoutErgebnis`` ist deren Ergebnis (``AbsatzOrt``,
``Platz`` und ``Seite`` stehen in ``ergebnis.py``), die Schreibmarken- und Auswahlgeometrie in ``schreibmarke.py``. Es gibt keinen zweiten Seitenumbruch.
"""
from .ergebnis import AbsatzOrt, Ergebnis, Platz, Seite
from .ergebnis import Ergebnis as LayoutErgebnis
from .objekte import objekt_rechteck
from .engine import LayoutEngine
from ..textlayout.paragraph import Absatzsatz, SatzZeile

__all__ = ["AbsatzOrt", "Absatzsatz", "Ergebnis", "LayoutEngine", "LayoutErgebnis", "Platz", "SatzZeile", "Seite", "objekt_rechteck"]
