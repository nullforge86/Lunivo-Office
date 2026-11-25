"""Markup-Filter (Überprüfen ▸ Markup anzeigen): welche Kommentare und nachverfolgten Änderungen gezeigt werden – Kommentare, Einfügungen und
Löschungen, ausgewählte Bearbeiter (``None`` = alle), ein Tag (``None`` = alle)."""
from __future__ import annotations

STANDARD: dict = {"kommentare": True, "einfuegungen": True, "formatierung": True, "bearbeiter": None, "zeit": None}


def ist_sichtbar(aenderung: dict, filter_: dict) -> bool:
    """Gehört die Änderung (``{"autor", "datum", …}``) zum gewählten Markup?"""
    if not filter_["einfuegungen"]:
        return False
    if filter_["bearbeiter"] is not None and aenderung["autor"] not in filter_["bearbeiter"]:
        return False
    return filter_["zeit"] is None or aenderung["datum"][:10] == filter_["zeit"]


def ist_gefiltert(filter_: dict) -> bool:
    """Zeigt das Markup nur einen Teil der Änderungen?"""
    return bool(filter_) and (filter_["bearbeiter"] is not None or filter_["zeit"] is not None or not filter_["einfuegungen"])
