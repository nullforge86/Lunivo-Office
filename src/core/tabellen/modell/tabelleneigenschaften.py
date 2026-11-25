"""Vorgabewerte des Fensters „Tabelleneigenschaften“ (Maße in Millimetern). Keine Oberfläche, kein Dokumentzugriff: Lesen und Setzen der Eigenschaften
leistet die zentrale Bearbeitung (``core/editing/tabellenbearbeitung.py``, ``KernEditor.tabellenformat`` und ``zellformat``)."""
from __future__ import annotations

VORGABE = {"breite_art": "prozent", "breite": 100.0, "ausr": "links", "innen": 1.0, "abstand": 0.0, "rahmen": 1.0,
           "spalte": 0.0, "spalte_fest": False, "senkrecht": "oben"}
