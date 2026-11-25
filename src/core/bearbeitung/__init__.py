"""Bearbeiten des Dokumentmodells ohne Qt.

Maßgeblich ist die ``Bearbeitungssitzung`` (kurz ``Sitzung``) über ``core.document.Dokument``: Text, Formate, Listen, Tabellen, Objekte, Abschnitte, Zusatzdaten,
Schreibmarke und Auswahl, Schritte mit Rückgängig/Wiederholen und Beobachter. ``SitzungsAenderung`` ist die Änderungsmeldung an die Beobachter.
"""
from core.bearbeitung.bearbeitungssitzung import Bearbeitungssitzung
from core.bearbeitung.verlauf import Aenderung as SitzungsAenderung, BearbeitungsFehler

Sitzung = Bearbeitungssitzung

__all__ = ["Kontext", "Bearbeitungssitzung", "BearbeitungsFehler", "Sitzung", "SitzungsAenderung", "WORDART_VORLAGEN"]


def __getattr__(name: str):
    if name == "Kontext":                                 # erst beim ersten Zugriff laden (keine zusätzlichen Importzyklen)
        from core.bearbeitung.kontext import Kontext
        return Kontext
    if name == "WORDART_VORLAGEN":
        from core.bearbeitung.einfuegen_hilfen import WORDART_VORLAGEN
        return WORDART_VORLAGEN
    raise AttributeError(f"Das Paket {__name__!r} hat keinen Namen {name!r}")
