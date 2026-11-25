"""Richtungsregeln der Architektur – eine einzige Quelle für den Importwächter und die Architekturtests.

    Qt-Oberfläche  →  Farmwork (Qt-frei)  →  Kern und Infrastruktur (Qt-frei)

    oberflaeche    darf Qt, sich selbst und ``farmwork`` importieren, nie ``core`` oder ``infrastruktur``
    farmwork       darf sich selbst, ``core`` und ``infrastruktur`` importieren, kein Qt, nie ``oberflaeche``
    core           darf nur ``core`` importieren, kein Qt
    infrastruktur  darf nur ``infrastruktur`` importieren, kein Qt

Bis zur vollständigen Umstellung gibt es die alten Ordner ``editor``, ``dienste``, ``ki`` und ``korrektur`` (Programmteile, die noch nicht nach ``kern``
gewandert sind). Sie dürfen ``core``, ``infrastruktur`` und sich gegenseitig importieren, nie ``farmwork`` oder ``oberflaeche``; das Farmwork darf sie
vorübergehend importieren. Jeder Verstoß steht auf der Übergangsliste, die nur kleiner werden darf.

Keine Direktverbindungen, keine Rückfallwege, keine alternativen Schnittstellen, keine Ausnahmen. Dieses Modul importiert nur die Standardbibliothek."""
from __future__ import annotations

PAKET = "lunivo_writer"
OBERFLAECHE = "oberflaeche"
FARMWORK = "farmwork"
ALTE_ORDNER = frozenset({"editor", "dienste", "ki", "korrektur"})
SCHICHTEN = (OBERFLAECHE, FARMWORK, "core", "infrastruktur", *sorted(ALTE_ORDNER))
QT_PAKETE = ("PySide6", "PyQt5", "PyQt6", "PyQt", "shiboken6", "shiboken")

ERLAUBTE_ZIELE = {
    OBERFLAECHE: frozenset({OBERFLAECHE, FARMWORK}),
    FARMWORK: frozenset({FARMWORK, "core", "infrastruktur"}) | ALTE_ORDNER,
    "core": frozenset({"core"}),
    "infrastruktur": frozenset({"infrastruktur"}),
    **{alt: frozenset({"core", "infrastruktur"}) | ALTE_ORDNER for alt in ALTE_ORDNER},
}


def schicht_von(modul: str) -> str | None:
    """Schicht eines Moduls ``lunivo_writer.<schicht>…``; ``None`` für Module der Paketwurzel und für Fremdmodule."""
    teile = modul.split(".")
    if len(teile) < 2 or teile[0] != PAKET:
        return None
    return teile[1] if teile[1] in SCHICHTEN else None


def ist_qt(modul: str) -> bool:
    return modul.split(".")[0] in QT_PAKETE


def qt_erlaubt(importeur: str) -> bool:
    """Qt gibt es ausschließlich in der Oberfläche."""
    return schicht_von(importeur) == OBERFLAECHE


def verstoss(importeur: str, ziel: str) -> str | None:
    """Beschreibung des Verstoßes, wenn ``importeur`` ``ziel`` nicht importieren darf, sonst ``None``."""
    von = schicht_von(importeur)
    if von not in ERLAUBTE_ZIELE:
        return None
    if ist_qt(ziel):
        return None if qt_erlaubt(importeur) else f"Qt ({ziel}) ist nur in oberflaeche erlaubt, nicht in {von}"
    nach = schicht_von(ziel)
    if nach is None:
        return None
    if nach not in ERLAUBTE_ZIELE[von]:
        return f"{von} darf {nach} nicht importieren ({ziel})"
    return None
