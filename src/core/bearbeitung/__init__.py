"""Bearbeiten des Dokumentmodells ohne Qt.

Maßgeblich ist die ``Bearbeitungssitzung`` (kurz ``Sitzung``) über ``core.document.Dokument``: Text, Formate, Listen, Tabellen, Objekte, Abschnitte, Zusatzdaten,
Schreibmarke und Auswahl, Schritte mit Rückgängig/Wiederholen und Beobachter. ``SitzungsAenderung`` ist die Änderungsmeldung an die Beobachter.
"""
from core.bearbeitung.bearbeitungssitzung import Bearbeitungssitzung
from core.bearbeitung.verlauf import Aenderung as SitzungsAenderung, BearbeitungsFehler

Sitzung = Bearbeitungssitzung

__all__ = ["Bearbeitungssitzung", "BearbeitungsFehler", "Sitzung", "SitzungsAenderung"]
