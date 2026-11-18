"""Bearbeiten des Dokumentmodells ohne Qt.

Maßgeblich ist die ``Bearbeitungssitzung`` (kurz ``Sitzung``) über ``core.document.Dokument``: Text, Formate, Listen, Tabellen, Objekte, Abschnitte, Zusatzdaten,
Schreibmarke und Auswahl, Schritte mit Rückgängig/Wiederholen und Beobachter. ``SitzungsAenderung`` ist die Änderungsmeldung an die Beobachter.
"""
from .bearbeitungssitzung import Bearbeitungssitzung
from .verlauf import Aenderung as SitzungsAenderung, BearbeitungsFehler

Sitzung = Bearbeitungssitzung

__all__ = ["Bearbeitungssitzung", "BearbeitungsFehler", "Sitzung", "SitzungsAenderung"]
