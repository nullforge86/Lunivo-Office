"""Ausgang des Frameworks: Prüfung aller Objekte, die an die Oberfläche gehen (Befehlsergebnisse, Ereignisdaten).

Stammt der Typ eines Objekts – oder eines darin enthaltenen Objekts – aus ``lunivo_writer.kern``, gibt es sofort einen Fehler. So verlässt kein
Kern-Objekt (Dokument, Absatz, Lauf, Format) das Framework."""
from __future__ import annotations

import dataclasses

KERN_PRAEFIX = "lunivo_writer.core"


class KernObjektAmAusgang(TypeError):
    """Ein Objekt aus ``lunivo_writer.kern`` sollte an die Oberfläche gehen."""


def pruefe(objekt, pfad: str = "Ausgabe"):
    """Gibt ``objekt`` unverändert zurück oder wirft ``KernObjektAmAusgang``. Prüft Behälter und Datenklassen rekursiv."""
    typ = type(objekt)
    if (typ.__module__ or "").startswith(KERN_PRAEFIX):
        raise KernObjektAmAusgang(f"{pfad}: Objekt vom Typ {typ.__module__}.{typ.__qualname__} aus dem Kern darf nicht an die Oberfläche")
    if dataclasses.is_dataclass(objekt) and not isinstance(objekt, type):
        for feld in dataclasses.fields(objekt):
            pruefe(getattr(objekt, feld.name), f"{pfad}.{feld.name}")
    elif isinstance(objekt, dict):
        for schluessel, wert in objekt.items():
            pruefe(schluessel, f"{pfad}[Schlüssel]")
            pruefe(wert, f"{pfad}[{schluessel!r}]")
    elif isinstance(objekt, (list, tuple, set, frozenset)):
        for i, element in enumerate(objekt):
            pruefe(element, f"{pfad}[{i}]")
    return objekt
