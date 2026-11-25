"""Formatvorlagen anwenden (Start ▸ Formatvorlagen, Tastenkürzel, Gliederungsebene): Die Vorlage kommt aus dem Katalog ins Dokument und wird
auf die Auswahl angewandt – über den Änderungsrahmen."""
from __future__ import annotations

from core.formatierung.absatz import tabs_als_text as _als_text, tabs_aus_text as _aus_text
from collections.abc import Mapping
from types import MappingProxyType

from core.formatvorlagen import vorlage_abgleichen, vorlage_anwenden, werte_aus_auswahl
from framework.befehle import ausfuehren, lesen


def formatvorlage_anwenden(kennung: int, name: str) -> bool:
    """→ ``False``, wenn es die Vorlage nicht gibt oder das Dokument schreibgeschützt ist."""
    return bool(ausfuehren(kennung, lambda s: vorlage_anwenden(s, name)))


def formatvorlage_abgleichen(kennung: int, name: str) -> bool:
    """Nach dem Ändern einer Vorlage im Katalog übernimmt das Dokument die neue Definition. → ``True``, wenn sich etwas geändert hat."""
    return bool(ausfuehren(kennung, lambda s: vorlage_abgleichen(s, name)))


Tabstopp = tuple[float, str, str]              # Millimeter, Ausrichtung, Füllzeichen


def tabs_als_text(stopps: tuple[Tabstopp, ...]) -> str:
    """Tabstopps in der Textform des Katalogs (``30.0:rechts:punkt;80.0:mitte:``)."""
    return _als_text(stopps)


def tabs_aus_text(text: str | None) -> tuple[Tabstopp, ...]:
    return tuple(_aus_text(text))


Katalogwert = str | float | int | bool


def formatvorlage_aus_auswahl(kennung: int) -> Mapping[str, Katalogwert]:
    """Die Felder einer Katalogvorlage aus dem Absatz an der Schreibmarke (Vorgabe für „Neue Formatvorlage“; ohne Liste). Leer ohne Dokument."""
    werte = lesen(kennung, werte_aus_auswahl)
    return MappingProxyType(dict(werte or {}))
