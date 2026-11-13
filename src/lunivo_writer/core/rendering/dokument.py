"""Zusammenspiel von Dokumentmodell, Seitenlayout und Renderbackend für eine Dokumentseite."""
from __future__ import annotations

from typing import Callable

from lunivo_writer.core.document.model import Document, PageLayout
from lunivo_writer.core.layout.seitenumbruch import Ergebnis
from lunivo_writer.core.rendering.backend import RenderTarget
from lunivo_writer.core.rendering.seite import zeichne_seite, zeichne_zeilennummern
from lunivo_writer.core.rendering.seitenschmuck import zeichne_seitenschmuck
from lunivo_writer.core.textlayout.engine import FontSpec, TextLayoutEngine

SeitenErweiterung = Callable[[RenderTarget, PageLayout | None, int], None]


def zeichne_dokumentseite(backend: RenderTarget, dokument: Document, layout: Ergebnis, index: int, engine: TextLayoutEngine,
                         zeilennummern_schrift: FontSpec | None = None, vor_inhalt: SeitenErweiterung | None = None,
                         nach_inhalt: SeitenErweiterung | None = None) -> None:
    """Zeichnet eine berechnete Seite samt Seitenschmuck und optionalen Adapter-Erweiterungen.

    Der Ursprung des Backends muss an der linken oberen Ecke der Seite liegen. ``vor_inhalt`` ist
    für Kopf-/Fußzeilen und Objekte hinter dem Text, ``nach_inhalt`` für Vordergrundobjekte.
    Adapter können dort Qt-spezifische Daten auf dasselbe Backend abbilden; Seiteninhalt und
    Seitenschmuck bleiben in der Rendering-Schicht.
    """
    seite = layout.seiten[index]
    einrichtung = seite.einrichtung
    if einrichtung is not None:
        zeichne_seitenschmuck(backend, engine, einrichtung, True, rahmen="hinten")
    if vor_inhalt is not None:
        vor_inhalt(backend, einrichtung, index)

    zeichne_seite(backend, layout, index, engine, hintergrund=False, dok=dokument)
    if zeilennummern_schrift is not None:
        zeichne_zeilennummern(backend, layout, index, zeilennummern_schrift)

    if nach_inhalt is not None:
        nach_inhalt(backend, einrichtung, index)
    if einrichtung is not None:
        zeichne_seitenschmuck(backend, engine, einrichtung, False, rahmen="vorn", wasserzeichen=False)
