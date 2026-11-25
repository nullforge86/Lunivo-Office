"""Startwächter der Schichtensperre: ein ``sys.meta_path``-Finder, der bei jedem erstmaligen Import prüft, ob der importierende Modulname die
Richtungstabelle (``sperre.regeln``) einhält.

Qt ist nur in ``lunivo_writer.oberflaeche`` erlaubt, die übrigen Schichten dürfen nur in die erlaubten Richtungen importieren. Ein Verstoß bricht mit
einer eindeutigen Fehlermeldung ab. Module auf ``sperre.uebergang.NOCH_NICHT_UMGESTELLT`` sind vorübergehend ausgenommen; die Liste wird nur kleiner
und ist im letzten Umbau-Schritt leer."""
from __future__ import annotations

import sys

from lunivo_writer.farmwork.pruefung import architektur as regeln, uebergang

_EIGENE = "lunivo_writer.farmwork.pruefung"


class SchichtenVerstoss(ImportError):
    """Ein Import verletzt die Richtungsregeln der Schichten."""


def _importeur() -> str | None:
    """Modulname des Codes, der gerade importiert (erster Aufrufer außerhalb des Importsystems und dieses Wächters)."""
    rahmen = sys._getframe(2)
    while rahmen is not None:
        name = rahmen.f_globals.get("__name__", "")
        if not (name.startswith("importlib") or name == regeln.PAKET or name.startswith(_EIGENE)):
            return name
        rahmen = rahmen.f_back
    return None


class Schichtenwaechter:
    """Meta-Pfad-Finder, der nie Module lädt, sondern nur prüft und ``None`` zurückgibt."""

    def find_spec(self, fullname, path=None, target=None):
        if not (fullname.startswith(regeln.PAKET + ".") or regeln.ist_qt(fullname)):
            return None
        importeur = _importeur()
        if not importeur or not importeur.startswith(regeln.PAKET):
            return None                                                        # Fremdcode (Tests, Werkzeuge, Hauptprogramm) ist frei
        grund = regeln.verstoss(importeur, fullname)
        if grund and importeur not in uebergang.NOCH_NICHT_UMGESTELLT:
            raise SchichtenVerstoss(
                f"Schichtensperre: {importeur} importiert {fullname}. {grund}. "
                "Verbindungen zwischen Oberfläche und Kern laufen nur über lunivo_writer.farmwork "
                "(siehe CLAUDE.md, Abschnitt „Schichten und Richtungsregeln“)."
            )
        return None


def einhaengen() -> None:
    if not any(isinstance(f, Schichtenwaechter) for f in sys.meta_path):
        sys.meta_path.insert(0, Schichtenwaechter())
