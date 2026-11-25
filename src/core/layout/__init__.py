"""Layout ohne Qt: Absatzzeilen, Objektpositionen und Seitenumbruch des Dokumentenmodells.

Maßgeblich ist ``LayoutEngine`` (``seitenlayout.py``) über dem Modell aus ``core.document.Dokument``; ``LayoutErgebnis`` ist deren Ergebnis (``AbsatzOrt``,
``Platz`` und ``Seite`` stehen in ``ergebnis.py``), die Schreibmarken- und Auswahlgeometrie in ``schreibmarke.py``. Es gibt keinen zweiten Seitenumbruch.
"""
from core.layout.ergebnis import AbsatzOrt, Ergebnis, Platz, Seite
from core.layout.ergebnis import Ergebnis as LayoutErgebnis
from core.layout.objekte import objekt_rechteck
from core.layout.engine import LayoutEngine
from core.textsatz.paragraph import Absatzsatz, SatzZeile

__all__ = ["AbsatzOrt", "Absatzsatz", "Ergebnis", "LayoutEngine", "LayoutErgebnis", "Platz", "SatzZeile", "Seite", "objekt_rechteck"]
