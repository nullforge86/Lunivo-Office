"""Seitenumbruch ohne Qt: legt ein ``core.document.Document`` mit einer ``TextLayoutEngine`` auf Seiten (Abschnitte, Spalten, Absätze, Tabellen, Bilder)."""
from lunivo_writer.core.layout.seitenumbruch import AbsatzOrt, Ergebnis, Platz, Seite, hoehe_von_bloecken, umbrechen

__all__ = ["AbsatzOrt", "Ergebnis", "Platz", "Seite", "hoehe_von_bloecken", "umbrechen"]
