"""Layout ohne Qt: Absatzzeilen, Objektpositionen und Seitenumbruch des Dokumentenmodells.

Maßgeblich ist ``LayoutEngine`` (``seitenlayout.py``) über dem Modell aus ``core.document.Dokument``; ``LayoutErgebnis`` ist deren Ergebnis, die
Schreibmarken- und Auswahlgeometrie steht in ``schreibmarke.py``. ``umbrechen`` und die gleichnamigen Klassen darunter arbeiten auf dem
bisherigen Modell und entfallen, sobald ihre Aufrufstellen umgestellt sind (``AbsatzOrt``, ``Ergebnis``, ``Platz`` und ``Seite`` heißen bis dahin
für das alte Ergebnis so).
"""
from .ergebnis import Ergebnis as LayoutErgebnis
from .objekte import objekt_rechteck
from .engine import LayoutEngine
from .seitenumbruch import AbsatzOrt, Ergebnis, Platz, Seite, hoehe_von_bloecken, umbrechen
from ..textlayout.paragraph import Absatzsatz, SatzZeile

__all__ = ["AbsatzOrt", "Absatzsatz", "Ergebnis", "LayoutEngine", "LayoutErgebnis", "Platz", "SatzZeile", "Seite", "hoehe_von_bloecken",
           "objekt_rechteck", "umbrechen"]
