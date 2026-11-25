"""Dokumentschutz (Überprüfen ▸ Bearbeitung einschränken): Arten und Prüfung, ob ein Befehl bei einem Schutz erlaubt ist.

Der Schutz gilt nur für die Sitzung und gehört zum Dokumentfenster der Oberfläche (``None``, ``lesen``, ``aenderungen`` oder ``kommentare``); er
wird den Befehlen als Wert übergeben."""
from __future__ import annotations

SCHUTZ_HINWEIS = "Das Dokument ist geschützt (Überprüfen ▸ Bearbeitung einschränken)."


def ist_geschuetzt(schutz: str | None, *arten: str) -> bool:
    """Steht ein Dokumentschutz einer dieser Arten?"""
    return schutz is not None and schutz in arten
