"""Felder einfügen (Einfügen ▸ Schnellbausteine ▸ Felder …): der Text ist das Feldergebnis, die Feldanweisung steht in ``P_FELD`` und geht als
echtes Feld ins DOCX (Word rechnet es dort neu). Keine Oberfläche.

    feld_einfuegen(ed, "NUMPAGES", "3")
"""
from __future__ import annotations

import os

from PySide6.QtCore import QDateTime, QLocale

from lunivo_writer.editor.zusatz import P_FELD

# Feldname → (Beschreibung, Feldanweisung)
FELDER = {
    "Datum": ("Das heutige Datum", 'DATE \\@ "dd.MM.yyyy"'),
    "Uhrzeit": ("Die Uhrzeit beim Einfügen", 'TIME \\@ "HH:mm"'),
    "Seitenanzahl": ("Die Zahl der Seiten im Dokument", "NUMPAGES"),
    "Wörter": ("Die Zahl der Wörter im Dokument", "NUMWORDS"),
    "Autor": ("Der Name aus den Optionen (Benutzername)", "AUTHOR"),
    "Dateiname": ("Der Name der Datei", "FILENAME"),
}


def ergebnis(name: str, kontext: dict) -> str:
    """Das Feldergebnis jetzt. ``kontext``: ``seiten``, ``woerter``, ``autor``, ``pfad``."""
    jetzt = QDateTime.currentDateTime()
    de = QLocale(QLocale.German, QLocale.Germany)
    if name == "Datum":
        return de.toString(jetzt.date(), "dd.MM.yyyy")
    if name == "Uhrzeit":
        return de.toString(jetzt.time(), "HH:mm")
    if name == "Seitenanzahl":
        return str(kontext.get("seiten", 1))
    if name == "Wörter":
        return str(kontext.get("woerter", 0))
    if name == "Autor":
        return kontext.get("autor") or "Unbekannt"
    if name == "Dateiname":
        return os.path.basename(kontext.get("pfad") or "") or "Unbenannt"
    return ""


def feld_einfuegen(ed, anweisung: str, text: str) -> None:
    c = ed.textCursor()
    f = c.charFormat()
    f.setProperty(P_FELD, anweisung)
    c.insertText(text, f)
    f.clearProperty(P_FELD)
    c.setCharFormat(f)                                      # danach geschriebener Text gehört nicht mehr zum Feld
    ed.setTextCursor(c)
    ed.document().setModified(True)
