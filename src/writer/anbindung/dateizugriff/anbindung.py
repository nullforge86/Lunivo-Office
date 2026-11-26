"""Dateizugriff für die Oberfläche: Stand und Sperren von Dateien, Sicherungsordner und der PDF-Export – alles über das Framework."""
from __future__ import annotations

import framework.dokumentverwaltung.dateizugriff as _fw
from framework.befehle import datei as _datei


def stand(path: str) -> tuple[int, int] | None:
    """(Änderungszeit in ns, Größe) der Datei oder None — zum Erkennen fremder Änderungen."""
    return _fw.stand(path)


def fremd_geoeffnet(path: str) -> str | None:
    """Beschreibung des Programms, das die Datei laut Sperrdatei offen hat, sonst None."""
    return _fw.fremd_geoeffnet(path)


def sicherungs_ordner() -> str:
    return _fw.sicherungs_ordner()


def pdf_wahl(**felder):
    """Eine Exportwahl für die PDF-Ausgabe mit den angegebenen Feldern (alle übrigen mit ihren Vorgaben)."""
    return _datei.pdf_wahl(**felder)


def pdf_wahl_mit(wahl, **felder):
    """Die Exportwahl mit geänderten Feldern (die Angabe selbst ist unveränderlich)."""
    return _datei.pdf_wahl_mit(wahl, **felder)


def pdf_druckrechte() -> list[tuple[str, str]]:
    """(Beschriftung, Wert) der Druckrechte einer geschützten PDF."""
    return list(_datei.pdf_druckrechte())


def pdf_kennwort_fehler(wahl, bestaetigt_rechte: str, bestaetigt_oeffnen: str) -> str:
    """Was an den Kennwörtern der Wahl nicht stimmt (leer: alles in Ordnung)."""
    return _datei.pdf_kennwort_fehler(wahl, bestaetigt_rechte, bestaetigt_oeffnen)


def pdf_schreiben(kennung: int, pfad: str, wahl, titel: str, autor: str, aktuelle_seite: int) -> int:
    """Das Dokument ``kennung`` nach der Wahl als PDF nach ``pfad`` schreiben; → Zahl der Seiten."""
    return _datei.pdf_schreiben(kennung, pfad, wahl, titel, autor, aktuelle_seite)
