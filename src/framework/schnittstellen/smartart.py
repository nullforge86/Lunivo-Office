"""SmartArt: unveränderliche Katalogdaten, die das Framework der Oberfläche übergibt."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class SmartArtLayout:
    """Ein Eintrag der Layout-Galerie."""
    schluessel: str
    name: str
    beschreibung: str
    muster: str


@dataclass(frozen=True)
class SmartArtKatalog:
    """Layouts, Farbschemata, Mustertexte und Formenstile des SmartArt."""
    layouts: tuple[str, ...]
    galerie: tuple[SmartArtLayout, ...]
    farben: Mapping[str, tuple[str, str, str]]
    muster: Mapping[str, str]
    anzeigenamen: Mapping[str, str]
    beschreibungen: Mapping[str, str]
    hierarchien: tuple[tuple[str, str], ...]
    hierarchie_layouts: tuple[str, ...]
    stile: tuple[str, ...]
    standard_layout: str
    aufzaehlungspunkt: str
