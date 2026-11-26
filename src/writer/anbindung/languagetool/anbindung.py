"""LanguageTool für die Oberfläche: reicht an die Anbindung des Frameworks weiter. Fehler des Dienstes kommen als ``Sprachpruefungsfehler`` an."""
from __future__ import annotations

import framework.dokumentverwaltung.integrationen as _fw


class Sprachpruefungsfehler(Exception):
    """LanguageTool ist nicht erreichbar oder antwortet nicht — der Text ist für Anwender gedacht."""


def ordner() -> str:
    return _fw.ordner()


def jar_finden() -> str | None:
    return _fw.jar_finden()


def verfuegbar(port: int | None = None) -> bool:
    return _fw.verfuegbar(port)


def pruefe(text: str, sprache: str = "de-DE", port: int | None = None) -> list[dict]:
    try:
        return [dict(f) for f in _fw.pruefe(text, sprache, port)]
    except _fw.LanguageToolFehler as e:
        raise Sprachpruefungsfehler(str(e)) from e
