"""PDF exportieren nach der Wahl im Fenster „PDF-Datei exportieren“: Seitenbereich, Exportoptionen, Berechtigungen und Kennwörter.

Gezeichnet wird die PDF wie bisher in ``editor/pagination.export_pdf`` (dieselbe Darstellung wie Druck und Vorschau). Dieser Dienst übersetzt
die Wahl in dessen Angaben, schneidet für „Markierung“ das Dokument zu und verschlüsselt die fertige Datei mit pypdf (AES-256).
Das Fenster dazu liegt in ``ui/baukasten/pdf_export.py``; es kennt nur ``PdfWahl``.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

from PySide6.QtGui import QTextCursor, QTextDocument

BEREICHE = ("alles", "aktuell", "markierung", "seiten")
DRUCK = [("Freier Druck", "frei"), ("Nur niedrige Auflösung", "niedrig"), ("Kein Druck", "kein")]


@dataclass
class PdfWahl:
    pfad: str = ""
    bereich: str = "alles"            # alles · aktuell · markierung · seiten
    von: int = 1
    bis: int = 1
    # Exportoptionen
    eigenschaften: bool = True        # Zusammenfassungsinformationen (Titel, Autor)
    kommentare: bool = True           # Kommentare als PDF-Notizen
    hyperlinks: bool = True
    notenlinks: bool = True           # Fußnotenzeichen springen zur Fußnote
    textmarken: bool = False          # Textmarken als Lesezeichen
    ueberschriften: bool = True       # Überschriften als Lesezeichen
    andere: bool = False              # Titel, Untertitel, Zitat als Lesezeichen
    eigene: bool = False              # eigene Formatvorlagen als Lesezeichen
    # Berechtigungen
    verschluesseln: bool = False
    kennwort_rechte: str = ""         # schützt die Berechtigungen
    kennwort_oeffnen: str = ""        # ohne dieses Kennwort öffnet sich die Datei nicht
    aendern: bool = True
    kopieren: bool = True
    kommentieren: bool = True
    druck: str = "frei"               # frei · niedrig · kein
    schliessen: bool = False          # Fenster nach dem Export schließen


def seiten(wahl: PdfWahl, aktuelle: int) -> tuple[int, int | None]:
    """(erste, letzte) Seite für ``export_pdf``; ``None`` = bis zum Ende."""
    if wahl.bereich == "aktuell":
        return aktuelle, aktuelle
    if wahl.bereich == "seiten":
        von, bis = sorted((max(1, wahl.von), max(1, wahl.bis)))
        return von, bis
    return 1, None


def lesezeichen(wahl: PdfWahl) -> dict | None:
    was = {"ueberschriften": wahl.ueberschriften, "textmarken": wahl.textmarken, "andere": wahl.andere, "eigene": wahl.eigene}
    return was if any(was.values()) else None


def nur_markierung(qdoc: QTextDocument, anfang: int, ende: int) -> QTextDocument:
    """Eine Kopie des Dokuments, in der nur der markierte Teil steht (Bilder und Formate bleiben, das Original bleibt unberührt)."""
    d = qdoc.clone()
    c = QTextCursor(d)
    c.setPosition(ende); c.movePosition(QTextCursor.End, QTextCursor.KeepAnchor); c.removeSelectedText()
    c.setPosition(0); c.setPosition(anfang, QTextCursor.KeepAnchor); c.removeSelectedText()
    return d


def berechtigungen(wahl: PdfWahl) -> int:
    """Die Rechte als PDF-Bits (ISO 32000, Tabelle 22)."""
    from pypdf.constants import UserAccessPermissions as U
    rechte = U.all()
    if not wahl.aendern:
        rechte &= ~(U.MODIFY | U.ASSEMBLE_DOC | U.FILL_FORM_FIELDS)
    if not wahl.kopieren:
        rechte &= ~(U.EXTRACT | U.EXTRACT_TEXT_AND_GRAPHICS)
    if not wahl.kommentieren:
        rechte &= ~U.ADD_OR_MODIFY
    if wahl.druck == "niedrig":
        rechte &= ~U.PRINT_TO_REPRESENTATION
    elif wahl.druck == "kein":
        rechte &= ~(U.PRINT | U.PRINT_TO_REPRESENTATION)
    return rechte


def kennwort_fehler(wahl: PdfWahl, bestaetigt_rechte: str, bestaetigt_oeffnen: str) -> str:
    """Leer, wenn die Kennwörter passen; sonst der Hinweis für das Fenster."""
    if not wahl.verschluesseln:
        return ""
    if wahl.kennwort_rechte != bestaetigt_rechte:
        return "Das Kennwort für die Berechtigungen und seine Bestätigung stimmen nicht überein."
    if wahl.kennwort_oeffnen != bestaetigt_oeffnen:
        return "Das Kennwort zum Öffnen und seine Bestätigung stimmen nicht überein."
    if not wahl.kennwort_rechte and not wahl.kennwort_oeffnen:
        return "Zum Verschlüsseln mindestens ein Kennwort eingeben."
    return ""


def verschluesseln(pfad: str, wahl: PdfWahl) -> None:
    """Die fertige PDF an Ort und Stelle verschlüsseln. Ohne Kennwort für die Berechtigungen gilt das Kennwort zum Öffnen auch dafür."""
    if not wahl.verschluesseln:
        return
    from pypdf import PdfReader, PdfWriter
    from pypdf.errors import DependencyError
    w = PdfWriter(clone_from=PdfReader(pfad))
    try:
        w.encrypt(wahl.kennwort_oeffnen, wahl.kennwort_rechte or None, permissions_flag=berechtigungen(wahl), algorithm="AES-256")
    except DependencyError:                       # ohne das Paket „cryptography“ geht nur das ältere RC4
        w = PdfWriter(clone_from=PdfReader(pfad))
        w.encrypt(wahl.kennwort_oeffnen, wahl.kennwort_rechte or None, permissions_flag=berechtigungen(wahl), algorithm="RC4-128")
    puffer = io.BytesIO()
    w.write(puffer)
    with open(pfad, "wb") as f:
        f.write(puffer.getvalue())
