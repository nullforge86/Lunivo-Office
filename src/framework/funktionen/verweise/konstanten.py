"""Auswahlwerte der Verweise-Fenster (Quellentypen, Zitierweisen, Inhaltsverzeichnis, Füllzeichen, Beschriftungen, Verweistypen), aus dem Programmkern
als einfache Werte."""
from __future__ import annotations

from core.funktionen.verweise.beschriftungen import beschriftung
from core.funktionen.verweise.querverweise import querverweis
from core.funktionen.verweise.quellen.literatur import TYPEN, ZITIERWEISEN
from core.funktionen.verweise.verzeichnisse.verzeichnis import TOC_FUELL, TOC_VORGABE
from core.editor.dokument.zusatz import BESCHRIFTUNGEN
from core.editor.text import zahlformat
from core.funktionen.absatz.tabfuell import FUELL

QUELLENTYPEN: tuple[str, ...] = tuple(TYPEN)
ZITIERWEISEN_NAMEN: tuple[str, ...] = tuple(ZITIERWEISEN)
INHALTSVERZEICHNIS_FUELL: tuple[str, ...] = tuple(TOC_FUELL)
INHALTSVERZEICHNIS_VORGABE: dict = dict(TOC_VORGABE)
FUELLZEICHEN: dict = dict(FUELL)
BESCHRIFTUNGS_BEZEICHNUNGEN: tuple[str, ...] = tuple(BESCHRIFTUNGEN)
VERWEISTYPEN: tuple[str, ...] = tuple(querverweis.VERWEISTYPEN)
NUMMERIERUNGSFORMATE: tuple[tuple[str, str], ...] = tuple((k, t) for k, t in zahlformat.TYPEN if k in beschriftung.SEQ_FORMAT)


def verweisen_auf(art: str) -> list[tuple[str, str]]:
    """Die Möglichkeiten „Verweisen auf“ zu einem Verweistyp als (Schlüssel, Text)."""
    return list(querverweis.verweisen_auf(art))
