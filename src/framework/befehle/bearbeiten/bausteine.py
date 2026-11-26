"""Textbausteine (AutoText) am Dokument: die Markierung als Baustein merken und einen Baustein an der Schreibmarke einfügen – anhand der Kennung."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from framework.anbindung import Daten, fest
from framework.sitzungen import sitzung as _steuerung


def bausteine_eigene() -> Sequence[Mapping[str, Daten]]:
    """Die eigenen Textbausteine (unveränderliche Kopien)."""
    from framework.dokumentverwaltung.dokumentpflege import laden
    return fest(laden())


def bausteine_standard() -> Sequence[Mapping[str, Daten]]:
    """Die mitgelieferten Textbausteine (unveränderliche Kopien)."""
    from framework.dokumentverwaltung.dokumentpflege import standard
    return fest(standard())


def baustein_fuer_kuerzel(kuerzel: str) -> Mapping[str, Daten] | None:
    from framework.dokumentverwaltung.dokumentpflege import finde_kuerzel
    return fest(finde_kuerzel(kuerzel))


def baustein_merken(kennung: int, name: str, kuerzel: str = "") -> None:
    """Die Auswahl des Dokuments als eigenen Baustein ``name`` speichern."""
    from framework.dokumentverwaltung.dokumentpflege import hinzufuegen
    hinzufuegen(name, _steuerung._sitzungen[kennung].sitzung.ausschnitt(), kuerzel)


def baustein_entfernen(name: str) -> None:
    from framework.dokumentverwaltung.dokumentpflege import entfernen
    entfernen(name)


def baustein_einfuegen(kennung: int, baustein: Mapping[str, Daten]) -> bool:
    """Fügt den Baustein mit seiner Formatierung an der Schreibmarke ein; ein Eintrag ohne Blockdaten kommt als einfacher Text.
    ``False``, wenn der Kern ablehnt."""
    from core.bearbeitung import BearbeitungsFehler
    from framework.dokumentverwaltung.dokumentpflege import bloecke_von
    s = _steuerung._sitzungen[kennung].sitzung
    bloecke = bloecke_von(baustein)
    try:
        if bloecke is None:
            s.text_einfuegen(baustein.get("text", ""))
        else:
            s.ausschnitt_einfuegen(bloecke)
    except BearbeitungsFehler:
        return False
    return True
