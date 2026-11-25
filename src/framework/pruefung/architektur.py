"""Richtungsregeln der Architektur – eine einzige Quelle für den Importwächter und die Architekturtests.

    vcl/qt  →  writer  →  framework  →  core, filter, system

    vcl.qt       darf Qt, sich selbst, ``vcl``, ``writer`` und ``framework`` importieren, nie ``core``, ``filter`` oder ``system``
    vcl          (Qt-freie Darstellungsverträge und Zeichnen) darf nur sich selbst importieren, kein Qt
    writer       Steuerung der Oberfläche: darf sich selbst, ``framework`` und ``system`` importieren, kein Qt, nie ``core``
    framework    darf sich selbst, ``core``, ``system`` und die Übergangsordner importieren, kein Qt, nie ``vcl`` oder ``writer``
    core         darf nur ``core`` importieren, kein Qt
    system       darf nur ``system`` importieren, kein Qt

Bis zur vollständigen Umstellung gibt es Übergangsordner (``core.editor``, ``core.korrektur``, ``filter``, ``framework.ki`` und ``framework.dokumentverwaltung``
mit ``ausgabe``, ``dateizugriff``, ``dokumentpflege``, ``integrationen``; früher ``editor``, ``korrektur``, ``dienste``, ``ki``). Sie dürfen ``core``, ``system`` und sich
gegenseitig importieren, nie ``framework`` (außerhalb der Übergangsordner), ``writer`` oder ``vcl``; das Framework darf sie vorübergehend importieren.
Jeder Verstoß steht auf der Übergangsliste, die nur kleiner werden darf.

Keine Direktverbindungen, keine Rückfallwege, keine alternativen Schnittstellen, keine Ausnahmen. Dieses Modul importiert nur die Standardbibliothek."""
from __future__ import annotations

from framework.pruefung.uebergang import ALT_MODULE_KERN

OBERFLAECHE = "vcl.qt"
VCL = "vcl"
WRITER = "writer"
FARMWORK = "framework"
KERN = "core"
SYSTEM = "system"
ALT = "uebergang"
WURZELN = frozenset({"core", "framework", "vcl", "writer", "filter", "system"})
UEBERGANGSORDNER = (
    "filter", "framework.ki",
    "framework.dokumentverwaltung.ausgabe", "framework.dokumentverwaltung.dateizugriff",
    "framework.dokumentverwaltung.dokumentpflege", "framework.dokumentverwaltung.integrationen",
)
SCHICHT_PRAEFIXE = ((OBERFLAECHE, OBERFLAECHE), (VCL, VCL), (WRITER, WRITER), (FARMWORK, FARMWORK), (KERN, KERN), (SYSTEM, SYSTEM))
QT_PAKETE = ("PySide6", "PyQt5", "PyQt6", "PyQt", "shiboken6", "shiboken")

ERLAUBTE_ZIELE = {
    OBERFLAECHE: frozenset({OBERFLAECHE, VCL, WRITER, FARMWORK}),
    VCL: frozenset({VCL}),
    WRITER: frozenset({WRITER, FARMWORK, SYSTEM}),
    FARMWORK: frozenset({FARMWORK, KERN, SYSTEM, ALT}),
    KERN: frozenset({KERN}),
    SYSTEM: frozenset({SYSTEM}),
    ALT: frozenset({KERN, SYSTEM, ALT}),
}


def _beginnt(modul: str, vorsatz: str) -> bool:
    return modul == vorsatz or modul.startswith(vorsatz + ".")


def schicht_von(modul: str) -> str | None:
    """Schicht eines Moduls (``vcl.qt``, ``vcl``, ``writer``, ``framework``, ``core``, ``system`` oder ``uebergang``); ``None`` für Fremdmodule."""
    if modul.split(".")[0] not in WURZELN:
        return None
    if any(_beginnt(modul, o) for o in (*UEBERGANGSORDNER, *ALT_MODULE_KERN)):          # auch Namen in einem Modul (Modul.Name) zählen zum Modul
        return ALT
    for vorsatz, schicht in SCHICHT_PRAEFIXE:
        if _beginnt(modul, vorsatz):
            return schicht
    return None


def ist_qt(modul: str) -> bool:
    return modul.split(".")[0] in QT_PAKETE


def qt_erlaubt(importeur: str) -> bool:
    """Qt gibt es ausschließlich unter ``vcl/qt``."""
    return schicht_von(importeur) == OBERFLAECHE


def verstoss(importeur: str, ziel: str) -> str | None:
    """Beschreibung des Verstoßes, wenn ``importeur`` ``ziel`` nicht importieren darf, sonst ``None``."""
    von = schicht_von(importeur)
    if von not in ERLAUBTE_ZIELE:
        return None
    if ist_qt(ziel):
        return None if qt_erlaubt(importeur) else f"Qt ({ziel}) ist nur in vcl.qt erlaubt, nicht in {von}"
    nach = schicht_von(ziel)
    if nach is None:
        return None
    if nach not in ERLAUBTE_ZIELE[von]:
        return f"{von} darf {nach} nicht importieren ({ziel})"
    return None
