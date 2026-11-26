"""Kopf- und Fußzeile auf dem Blatt bearbeiten: Qt-freie Beschreibung der Knöpfe, Klappen und Texte und die Übersetzung des Zeilenformats.

Tür des Pakets: Aufrufer außerhalb importieren ``blattknoepfe``, ``blattklappen``, ``blatttexte`` und ``blattformat`` von hier."""
from writer.funktionen.kopffuss import klappen as blattklappen
from writer.funktionen.kopffuss import leiste as blattknoepfe
from writer.funktionen.kopffuss import texte as blatttexte
from writer.funktionen.kopffuss import zeilenformat as blattformat

__all__ = ["blattformat", "blattklappen", "blattknoepfe", "blatttexte"]
