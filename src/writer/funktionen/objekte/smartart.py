"""SmartArt: die Steuerung der Oberfläche. Reicht Abfragen und Befehle an das Framework weiter und gibt der Oberfläche eigene, veränderbare Kopien der
eingefrorenen Ergebnisse; die Oberfläche kennt den Kern nicht."""
from __future__ import annotations

from collections.abc import Mapping, Sequence

from framework.befehle.objekte import smartart as befehle
from framework.schnittstellen.smartart import SmartArtKatalog, SmartArtLayout
from system.daten.unveraenderlich import auftauen


def format_schluessel() -> tuple[str, ...]:
    return befehle.FORMAT_SCHLUESSEL


def katalog() -> SmartArtKatalog:
    return befehle.katalog()


def einfuegen_daten(daten: Mapping | str | SmartArtLayout | None) -> dict:
    if isinstance(daten, SmartArtLayout):
        daten = daten.schluessel
    return auftauen(befehle.einfuegen_daten(daten))


def knoten_von(daten: Mapping) -> list[dict]:
    return auftauen(befehle.knoten_von(daten))


def text_aus_knoten(knoten: Sequence[Mapping]) -> str:
    return befehle.text_aus_knoten(knoten)


def knotentext(knoten: Mapping) -> str:
    return befehle.knotentext(knoten)


def knoten_index(knoten: Sequence[Mapping], ident: str | None) -> int | None:
    return befehle.knoten_index(knoten, ident)


def knoten_gewaehlt(daten: Mapping | None) -> str | None:
    return befehle.knoten_gewaehlt(daten)


def knoten_waehlbar(daten: Mapping | None, ident: str | None) -> bool:
    return befehle.knoten_waehlbar(daten, ident)


def knoten_text(daten: Mapping | None, ident: str | None) -> str | None:
    return befehle.knoten_text(daten, ident)


def text_gegen_knoten(daten: Mapping | None, neu: Mapping) -> dict:
    return auftauen(befehle.text_gegen_knoten(daten, neu))


def format_mischen(fmt: Mapping, angaben: Mapping) -> dict:
    return auftauen(befehle.format_mischen(fmt, angaben))


def format_lesen(daten: Mapping | None) -> dict | None:
    erg = befehle.format_lesen(daten)
    return auftauen(erg) if erg is not None else None


def kann(daten: Mapping | None, was: str, richtung: str = "") -> bool:
    return befehle.kann(daten, was, richtung)


def form_einfuegen(knoten: Sequence[Mapping], ident: str | None, wie: str) -> tuple[list[dict], str] | None:
    erg = befehle.form_einfuegen(knoten, ident, wie)
    return None if erg is None else (auftauen(erg[0]), erg[1])


def level(knoten: Sequence[Mapping], ident: str | None, richtung: str) -> list[dict] | None:
    erg = befehle.level(knoten, ident, richtung)
    return None if erg is None else auftauen(erg)


def verschieben(knoten: Sequence[Mapping], ident: str | None, richtung: str) -> list[dict] | None:
    erg = befehle.verschieben(knoten, ident, richtung)
    return None if erg is None else auftauen(erg)


def aufzaehlung(knoten: Sequence[Mapping], ident: str | None) -> list[dict] | None:
    erg = befehle.aufzaehlung(knoten, ident)
    return None if erg is None else auftauen(erg)
