"""Text aus einer Datei einfügen: ordnet die Bedienung den Framework-Befehlen zu."""
from __future__ import annotations

from framework.befehle import bearbeiten as _befehle


def fremdtext_laden(pfad: str) -> tuple[int, tuple[str, ...]]:
    """Eine Datei zum Einfügen laden; → (Nummer, Hinweise über Nicht-Übernommenes). Meldet ``Dateifehler``, wenn sie sich nicht lesen lässt."""
    from framework.schnittstellen import Dateifehler as _Dateifehler
    from writer.werte import Dateifehler
    try:
        return _befehle.fremdtext_datei_laden(pfad)
    except _Dateifehler as e:
        raise Dateifehler(str(e)) from e


def fremdtext_verwerfen(nummer: int) -> None:
    _befehle.fremdtext_datei_verwerfen(nummer)


def fremdtext_einfuegen(kennung: int, nummer: int) -> bool:
    """Den Haupttext der geladenen Datei an der Schreibmarke einfügen; ``False``, wenn der Kern ablehnt."""
    return _befehle.fremdtext_datei_einfuegen(kennung, nummer)
