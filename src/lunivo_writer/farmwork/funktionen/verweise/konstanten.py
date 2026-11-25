"""Auswahlwerte der Verweise-Fenster (Quellentypen, Zitierweisen, Inhaltsverzeichnis, Füllzeichen, Beschriftungen, Verweistypen), aus dem Programmkern
als einfache Werte."""
from __future__ import annotations

from lunivo_writer.editor.dokument import verweise
from lunivo_writer.editor.dokument.literatur import TYPEN, ZITIERWEISEN
from lunivo_writer.editor.dokument.verzeichnis import TOC_FUELL, TOC_VORGABE
from lunivo_writer.editor.dokument.zusatz import BESCHRIFTUNGEN
from lunivo_writer.editor.text import zahlformat
from lunivo_writer.editor.text.tabfuell import FUELL

QUELLENTYPEN: tuple[str, ...] = tuple(TYPEN)
ZITIERWEISEN_NAMEN: tuple[str, ...] = tuple(ZITIERWEISEN)
INHALTSVERZEICHNIS_FUELL: tuple[str, ...] = tuple(TOC_FUELL)
INHALTSVERZEICHNIS_VORGABE: dict = dict(TOC_VORGABE)
FUELLZEICHEN: dict = dict(FUELL)
BESCHRIFTUNGS_BEZEICHNUNGEN: tuple[str, ...] = tuple(BESCHRIFTUNGEN)
VERWEISTYPEN: tuple[str, ...] = tuple(verweise.VERWEISTYPEN)
NUMMERIERUNGSFORMATE: tuple[tuple[str, str], ...] = tuple((k, t) for k, t in zahlformat.TYPEN if k in verweise.SEQ_FORMAT)


def verweisen_auf(art: str) -> list[tuple[str, str]]:
    """Die Möglichkeiten „Verweisen auf“ zu einem Verweistyp als (Schlüssel, Text)."""
    return list(verweise.verweisen_auf(art))
