"""SmartArt: Abfragen und Befehle auf den Daten eines SmartArt. Die Fachlogik (Knotenbaum, Katalog) liegt im Kern. Die Daten gehen als schreibgeschützte
Abbilder hinein und als eigene, tief eingefrorene Kopien heraus; nichts davon verweist auf Objekte des Kerns."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from types import MappingProxyType

from core.objekte.smartart import smartart_daten as modell
from framework.schnittstellen.smartart import SmartArtKatalog, SmartArtLayout
from system.daten.unveraenderlich import Daten, auftauen, einfrieren

FORMAT_SCHLUESSEL: tuple[str, ...] = modell.FORMAT_SCHLUESSEL


def katalog() -> SmartArtKatalog:
    """Layouts, Farbschemata, Mustertexte, Hierarchien und Formenstile."""
    return SmartArtKatalog(
        layouts=tuple(modell.LAYOUTS),
        galerie=tuple(SmartArtLayout(e["schluessel"], e["name"], e["beschreibung"], e["muster"]) for e in modell.LAYOUT_KATALOG),
        farben=MappingProxyType({n: tuple(f) for n, f in modell.FARBEN.items()}),
        muster=MappingProxyType(dict(modell.MUSTER)),
        anzeigenamen=MappingProxyType(dict(modell.ANZEIGENAMEN)),
        beschreibungen=MappingProxyType(dict(modell.BESCHREIBUNGEN)),
        hierarchien=tuple(modell.HIERARCHIEN),
        hierarchie_layouts=tuple(modell.HIERARCHIE_LAYOUTS),
        stile=tuple(modell.STILE),
        standard_layout=modell.STANDARD_LAYOUT,
        aufzaehlungspunkt=modell.BULLET)


def einfuegen_daten(daten: Mapping | str | None) -> Daten:
    """Die Daten, mit denen ein SmartArt eingefügt wird (``daten`` = Daten oder der Schlüssel eines Katalogeintrags)."""
    return einfrieren(modell.einfuegen_daten(auftauen(daten) if isinstance(daten, Mapping) else daten))


def knoten_von(daten: Mapping) -> tuple[Daten, ...]:
    return einfrieren(modell.knoten_von(auftauen(daten)))


def text_aus_knoten(knoten: Sequence[Mapping]) -> str:
    return modell.text_aus_knoten(auftauen(knoten))


def knotentext(knoten: Mapping) -> str:
    """Text eines Knotens mit seinen Aufzählungspunkten."""
    return modell._knotentext(auftauen(knoten))


def knoten_index(knoten: Sequence[Mapping], ident: str | None) -> int | None:
    return modell._index(auftauen(knoten), ident)


def knoten_gewaehlt(daten: Mapping | None) -> str | None:
    return modell.knoten_gewaehlt(auftauen(daten) if daten is not None else None)


def knoten_waehlbar(daten: Mapping | None, ident: str | None) -> bool:
    return modell.knoten_waehlbar(auftauen(daten) if daten is not None else None, ident)


def knoten_text(daten: Mapping | None, ident: str | None) -> str | None:
    return modell.knoten_text(auftauen(daten) if daten is not None else None, ident)


def text_gegen_knoten(daten: Mapping | None, neu: Mapping) -> Daten:
    """Ein neuer ``text`` ohne Knoten ersetzt die Knoten nur, wenn er vom Text der vorhandenen abweicht; → die angepassten neuen Angaben."""
    angaben = auftauen(neu)
    modell.text_gegen_knoten(auftauen(daten) if daten is not None else None, angaben)
    return einfrieren(angaben)


def format_mischen(fmt: Mapping, angaben: Mapping) -> Daten:
    return einfrieren(modell._format_mischen(auftauen(fmt), auftauen(angaben)))


def format_lesen(daten: Mapping | None) -> Daten | None:
    erg = modell.format_lesen(auftauen(daten) if daten is not None else None)
    return einfrieren(erg) if erg is not None else None


def kann(daten: Mapping | None, was: str, richtung: str = "") -> bool:
    return modell.kann(auftauen(daten) if daten is not None else None, was, richtung)


def form_einfuegen(knoten: Sequence[Mapping], ident: str | None, wie: str) -> tuple[tuple[Daten, ...], str] | None:
    erg = modell.form_einfuegen(auftauen(knoten), ident, wie)
    return None if erg is None else (einfrieren(erg[0]), erg[1])


def level(knoten: Sequence[Mapping], ident: str | None, richtung: str) -> tuple[Daten, ...] | None:
    erg = modell.level(auftauen(knoten), ident, richtung)
    return None if erg is None else einfrieren(erg)


def verschieben(knoten: Sequence[Mapping], ident: str | None, richtung: str) -> tuple[Daten, ...] | None:
    erg = modell.verschieben(auftauen(knoten), ident, richtung)
    return None if erg is None else einfrieren(erg)


def aufzaehlung(knoten: Sequence[Mapping], ident: str | None) -> tuple[Daten, ...] | None:
    erg = modell.aufzaehlung(auftauen(knoten), ident)
    return None if erg is None else einfrieren(erg)
