"""Auswahlwerte der Verweise-Fenster (Quellentypen, Zitierweisen, Inhaltsverzeichnis, Füllzeichen, Beschriftungen, Verweistypen), aus dem Programmkern
als einfache Werte."""
from __future__ import annotations

from core.verzeichnisse.abbildungsverzeichnis import beschriftung
from core.referenzen.querverweise import querverweis
from core.referenzen.literaturverzeichnis.literatur import TYPEN, ZITIERWEISEN
from core.verzeichnisse.inhaltsverzeichnis.verzeichnis import TOC_FUELL, TOC_VORGABE
from core.dokument.zusatz import BESCHRIFTUNGEN
from core.text import zahlformat
from core.formatierung.absatz.tabfuell import FUELL

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
