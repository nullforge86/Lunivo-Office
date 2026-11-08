"""Verzeichnis der Dateiformate: was Lunivo öffnen und speichern kann, was dabei unterstützt wird und was nicht.

Ein Format ist ein Eintrag hier plus je ein Leser und Schreiber, die dieselben Rückgaben haben wie die vorhandenen
(``lesen(pfad) → (QTextDocument, PageSettings, meta, IOReport)``, ``schreiben(pfad, doc, page, meta) → IOReport``).
Der zentrale Ablauf (``file_service``) fragt dieses Verzeichnis und kennt die Formate nicht einzeln beim Namen; für ein neues Format
kommt ein Eintrag hinzu, und ``file_service`` ruft den eingetragenen Leser/Schreiber auf.

``nicht_unterstuetzt`` ist die ehrliche Liste dessen, was beim Lesen oder Schreiben verloren geht oder nur angenähert wird; dieselben Dinge
meldet der ``IOReport`` im Einzelfall. Die Liste steht auch im Handbuch und in ``docs/formate.md``.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FormatInfo:
    endung: str
    name: str
    lesen: bool
    schreiben: bool
    unterstuetzt: tuple[str, ...]
    nicht_unterstuetzt: tuple[str, ...] = ()
    hinweise: tuple[str, ...] = ()
    paket: bool = False                       # ZIP-Paket: unterliegt den Importgrenzen für Pakete (services/import_grenzen.py)


FORMATE: dict[str, FormatInfo] = {f.endung: f for f in (
    FormatInfo(".docx", "Word-Dokument", True, True,
               ("Formatvorlagen mit Vererbung", "Zeichen- und Absatzformat", "Listen", "Tabellen mit verbundenen Zellen", "Bilder im Text und schwebend",
                "Kopf- und Fußzeilen", "Abschnitte", "Kommentare", "Fuß- und Endnoten", "Felder", "Lesezeichen und Verweise"),
               ("Verschachtelte Tabellen", "Formeln (OMML)", "Zeichnungen und SmartArt außer den eigenen Formen", "Makros"),
               ("Kennwortgeschützte Dateien werden mit Kennwort geöffnet und geschrieben.",), True),
    FormatInfo(".dotx", "Word-Vorlage", True, False, ("wie DOCX",), ("Speichern als Vorlage",), ("Wird als Dokument geöffnet.",), True),
    FormatInfo(".docm", "Word-Dokument mit Makros", True, False, ("wie DOCX",), ("Makros",), ("Makros werden nicht ausgeführt und nicht gespeichert.",), True),
    FormatInfo(".odt", "OpenDocument-Text", True, True, ("Absätze, Zeichenformat, Listen, Tabellen, Bilder, Seitenformat",),
               ("Änderungsverfolgung", "Formeln", "Formulare"), (), True),
    FormatInfo(".fodt", "Flaches OpenDocument", True, False, ("wie ODT",), ("Speichern",), (), False),
    FormatInfo(".rtf", "Rich Text", True, True, ("Absätze, Zeichenformat, Listen, Tabellen, Bilder, Kopf- und Fußzeile",),
               ("Fußnoten", "Kommentare", "Zeichnungen"), (), False),
    FormatInfo(".txt", "Textdatei", True, True, ("Reiner Text (UTF-8, Windows-1252 beim Lesen)",),
               ("Formatierung", "Tabellen", "Bilder", "Kopf- und Fußzeilen"), ("Beim Speichern geht die Formatierung verloren; der Bericht sagt es.",), False),
    FormatInfo(".pdf", "PDF", False, True, ("Ausgabe mit Seitenlayout, Lesezeichen, Verweisen",), ("Öffnen", "Bearbeiten nach dem Export"),
               ("Nur Ausgabe (Export), kein Bearbeitungsformat.",), False),
)}


def finde(endung: str) -> FormatInfo | None:
    return FORMATE.get((endung or "").lower())


def lesbar() -> list[str]:
    return [e for e, f in FORMATE.items() if f.lesen]


def speicherbar() -> list[str]:
    return [e for e, f in FORMATE.items() if f.schreiben]


def als_markdown() -> str:
    """Tabelle für Handbuch und Dokumentation (Markdown, kein HTML)."""
    z = ["| Format | Öffnen | Speichern | Unterstützt | Nicht unterstützt |", "|---|---|---|---|---|"]
    for f in FORMATE.values():
        z.append(f"| {f.name} (`{f.endung}`) | {'ja' if f.lesen else 'nein'} | {'ja' if f.schreiben else 'nein'} | {'; '.join(f.unterstuetzt)} | "
                 f"{'; '.join(f.nicht_unterstuetzt) or '–'} |")
    return "\n".join(z) + "\n"
