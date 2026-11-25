"""Richtungsregeln der Architektur – eine einzige Quelle für den Importwächter und die Architekturtests.

    Qt-Oberfläche  →  Farmwork  →  Programmkern (core, editor, dienste, ki, korrektur, modelle, plattform)

    oberflaeche   darf Qt, sich selbst und ``farmwork`` importieren, nie den Programmkern
    farmwork      darf sich selbst und den Programmkern importieren, nie ``oberflaeche``; Qt nur in ``farmwork.qt``
    core          darf core, modelle und plattform importieren, kein Qt, nie ``oberflaeche``/``farmwork``
    editor, dienste, ki, korrektur   dürfen den Programmkern importieren, nie ``oberflaeche``/``farmwork``
    modelle       darf modelle, core und plattform importieren
    plattform     darf nur sich selbst importieren, kein Qt

Keine Direktverbindungen, keine Rückfallwege, keine alternativen Schnittstellen, keine Ausnahmen. Dieses Modul importiert nur die Standardbibliothek."""
from __future__ import annotations

PAKET = "lunivo_writer"
OBERFLAECHE = "oberflaeche"
FARMWORK = "farmwork"
PROGRAMMKERN = frozenset({"core", "editor", "dienste", "ki", "korrektur", "modelle", "plattform"})
SCHICHTEN = (OBERFLAECHE, FARMWORK, *sorted(PROGRAMMKERN))
QT_PAKETE = ("PySide6", "PyQt5", "PyQt6", "PyQt", "shiboken6", "shiboken")
QT_FARMWORK = PAKET + "." + FARMWORK + ".qt"          # die einzige Stelle im Farmwork, die Qt kennt

ERLAUBTE_ZIELE = {
    OBERFLAECHE: frozenset({OBERFLAECHE, FARMWORK}),
    FARMWORK: frozenset({FARMWORK}) | PROGRAMMKERN,
    "core": frozenset({"core", "modelle", "plattform"}),
    "modelle": frozenset({"modelle", "core", "plattform"}),
    "plattform": frozenset({"plattform"}),
    "editor": PROGRAMMKERN,
    "dienste": PROGRAMMKERN,
    "ki": PROGRAMMKERN,
    "korrektur": PROGRAMMKERN,
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
    return schicht_von(importeur) == OBERFLAECHE or importeur == QT_FARMWORK or importeur.startswith(QT_FARMWORK + ".")


def verstoss(importeur: str, ziel: str) -> str | None:
    """Beschreibung des Verstoßes, wenn ``importeur`` ``ziel`` nicht importieren darf, sonst ``None``."""
    von = schicht_von(importeur)
    if von not in ERLAUBTE_ZIELE:
        return None
    if ist_qt(ziel):
        return None if qt_erlaubt(importeur) else f"Qt ({ziel}) ist nur in oberflaeche und farmwork.qt erlaubt, nicht in {von}"
    nach = schicht_von(ziel)
    if nach is None:
        return None
    if nach not in ERLAUBTE_ZIELE[von]:
        return f"{von} darf {nach} nicht importieren ({ziel})"
    return None
